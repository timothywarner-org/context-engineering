# CoreText MCP - Azure Container Apps Deployment Guide

## Overview

This guide walks through deploying CoreText MCP to Azure Container Apps - a simple, production-ready deployment without CI/CD complexity.

## Prerequisites

1. **Azure CLI** installed and logged in
   ```bash
   az login
   ```

2. **Azure Subscription** with these resources:
   - Subscription ID: `92fd53f2-c38e-461a-9f50-e1ef3382c54c`
   - Resource Group: `context-engineering-rg`
   - Region: `eastus`
   - Managed Identity: `context-msi`

3. **(Optional) Deepseek API Key** for AI enrichment
   ```bash
   export DEEPSEEK_API_KEY="your-api-key-here"
   ```

## Quick Deployment

### Option 1: Automated Script (Recommended)

```bash
cd coretext-mcp/azure-deployment
chmod +x deploy.sh
./deploy.sh
```

That's it! The script will:
1. Create Azure Container Registry (if needed)
2. Build and push Docker image
3. Create Container Apps Environment (if needed)
4. Deploy the container app
5. Output the public URL

### Option 2: Manual Deployment

If you prefer step-by-step control:

#### 1. Create Azure Container Registry

```bash
az acr create \
  --resource-group context-engineering-rg \
  --name coretextmcr \
  --sku Basic \
  --admin-enabled true
```

#### 2. Build and Push Image

```bash
cd coretext-mcp
az acr build \
  --registry coretextmcr \
  --image coretext-mcp:latest \
  --file azure-deployment/Dockerfile \
  .
```

#### 3. Create Container Apps Environment

```bash
az containerapp env create \
  --name coretext-env \
  --resource-group context-engineering-rg \
  --location eastus
```

#### 4. Get ACR Credentials

```bash
ACR_USERNAME=$(az acr credential show --name coretextmcr --query username -o tsv)
ACR_PASSWORD=$(az acr credential show --name coretextmcr --query passwords[0].value -o tsv)
ACR_LOGIN_SERVER=$(az acr show --name coretextmcr --query loginServer -o tsv)
```

#### 5. Deploy Container App

```bash
az containerapp create \
  --name coretext-mcp \
  --resource-group context-engineering-rg \
  --environment coretext-env \
  --image "$ACR_LOGIN_SERVER/coretext-mcp:latest" \
  --registry-server $ACR_LOGIN_SERVER \
  --registry-username $ACR_USERNAME \
  --registry-password $ACR_PASSWORD \
  --target-port 3001 \
  --ingress external \
  --min-replicas 1 \
  --max-replicas 3 \
  --cpu 0.5 \
  --memory 1.0Gi \
  --env-vars NODE_ENV=production DEEPSEEK_API_KEY="$DEEPSEEK_API_KEY"
```

## Architecture

```
┌─────────────────────────────────────────────┐
│   Azure Container Apps                      │
│                                             │
│   ┌───────────────────────────────────┐    │
│   │  CoreText MCP Container           │    │
│   │                                   │    │
│   │  - Node.js 20 Alpine              │    │
│   │  - MCP Server (stdio transport)   │    │
│   │  - Health Endpoint (port 3001)    │    │
│   │  - JSON Storage (/app/data)       │    │
│   └───────────────────────────────────┘    │
│                                             │
│   External Ingress (HTTPS)                 │
└─────────────────────────────────────────────┘
          │
          ▼
    Claude Desktop / MCP Clients
```

## Configuration

### Environment Variables

The deployment uses these environment variables:

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `NODE_ENV` | No | `production` | Node environment |
| `DEEPSEEK_API_KEY` | No | - | API key for AI enrichment |
| `HEALTH_PORT` | No | `3001` | Health endpoint port |

### Resource Limits

| Resource | Value | Notes |
|----------|-------|-------|
| CPU | 0.5 cores | Sufficient for demo workload |
| Memory | 1.0 GB | Plenty for JSON storage |
| Min Replicas | 1 | Always running |
| Max Replicas | 3 | Auto-scales under load |

### Container Apps Pricing

Estimated cost with 1 replica running 24/7:
- **Consumption tier**: ~$30-40/month
- **Pay only for what you use**
- **Scales to zero option available** (set min-replicas=0)

## Post-Deployment

### 1. Verify Health

```bash
# Get the URL
APP_URL=$(az containerapp show \
  --name coretext-mcp \
  --resource-group context-engineering-rg \
  --query properties.configuration.ingress.fqdn -o tsv)

# Test health endpoint
curl https://$APP_URL/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2025-10-30T...",
  "memoryCount": 3,
  "enrichmentConfigured": true,
  "uptime": 123.45
}
```

### 2. View Logs

```bash
# Stream live logs
az containerapp logs show \
  --name coretext-mcp \
  --resource-group context-engineering-rg \
  --follow

# View recent logs
az containerapp logs show \
  --name coretext-mcp \
  --resource-group context-engineering-rg \
  --tail 100
```

### 3. Configure Claude Desktop

**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
**Mac/Linux**: `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "coretext-azure": {
      "url": "https://YOUR-APP-URL.eastus.azurecontainerapps.io",
      "transport": "sse"
    }
  }
}
```

Replace `YOUR-APP-URL` with the actual FQDN from deployment.

## Management Commands

### Update Deployment

```bash
# Rebuild and deploy new version
cd coretext-mcp/azure-deployment
./deploy.sh
```

### Scale Manually

```bash
# Scale to 2 replicas
az containerapp update \
  --name coretext-mcp \
  --resource-group context-engineering-rg \
  --min-replicas 2 \
  --max-replicas 5
```

### Restart Container

```bash
az containerapp revision restart \
  --name coretext-mcp \
  --resource-group context-engineering-rg
```

### Delete Deployment

```bash
# Delete container app only
az containerapp delete \
  --name coretext-mcp \
  --resource-group context-engineering-rg \
  --yes

# Delete everything (app + environment + registry)
az containerapp delete --name coretext-mcp --resource-group context-engineering-rg --yes
az containerapp env delete --name coretext-env --resource-group context-engineering-rg --yes
az acr delete --name coretextmcr --resource-group context-engineering-rg --yes
```

## Troubleshooting

### Container Won't Start

**Check logs:**
```bash
az containerapp logs show \
  --name coretext-mcp \
  --resource-group context-engineering-rg \
  --tail 100
```

**Common issues:**
- Missing environment variables
- Port conflicts (ensure HEALTH_PORT=3001)
- Image build failures

### Health Check Failing

**Verify endpoint locally first:**
```bash
# Test in local Docker
docker build -t coretext-mcp -f azure-deployment/Dockerfile .
docker run -p 3001:3001 coretext-mcp
curl http://localhost:3001/health
```

**Check Container Apps health probe:**
```bash
az containerapp show \
  --name coretext-mcp \
  --resource-group context-engineering-rg \
  --query properties.template.containers[0].probes
```

### Cannot Connect from Claude

**Verify ingress is external:**
```bash
az containerapp show \
  --name coretext-mcp \
  --resource-group context-engineering-rg \
  --query properties.configuration.ingress.external
```

Should return `true`.

**Check firewall rules:**
- Container Apps uses Azure-managed networking
- No NSG rules needed for external ingress
- HTTPS is automatic (managed certificates)

## Local Testing

Before deploying to Azure, test the Docker image locally:

```bash
cd coretext-mcp

# Build image
docker build -t coretext-mcp -f azure-deployment/Dockerfile .

# Run container
docker run -p 3001:3001 \
  -e DEEPSEEK_API_KEY="your-key" \
  coretext-mcp

# Test in another terminal
curl http://localhost:3001/health
```

## Monitoring

### Azure Portal

1. Navigate to **Resource Group** → `context-engineering-rg`
2. Click on **Container App** → `coretext-mcp`
3. View:
   - **Metrics**: CPU, Memory, HTTP requests
   - **Log stream**: Real-time logs
   - **Revisions**: Deployment history
   - **Replica count**: Current scale

### Azure Monitor (Optional)

Enable Application Insights for advanced monitoring:

```bash
# Create App Insights
az monitor app-insights component create \
  --app coretext-insights \
  --location eastus \
  --resource-group context-engineering-rg

# Link to Container App
INSTRUMENTATION_KEY=$(az monitor app-insights component show \
  --app coretext-insights \
  --resource-group context-engineering-rg \
  --query instrumentationKey -o tsv)

az containerapp update \
  --name coretext-mcp \
  --resource-group context-engineering-rg \
  --set-env-vars APPLICATIONINSIGHTS_CONNECTION_STRING="InstrumentationKey=$INSTRUMENTATION_KEY"
```

## Migration to Cosmos DB (Future)

When JSON storage becomes insufficient, migrate to Cosmos DB:

1. **Create Cosmos DB account**
2. **Update storage.js** to use `@azure/cosmos` SDK
3. **Add connection string** to environment variables
4. **Redeploy** using same process

The container image supports both JSON and Cosmos DB - just change environment variables.

## Cost Optimization

### Option 1: Scale to Zero

For non-production workloads:
```bash
az containerapp update \
  --name coretext-mcp \
  --resource-group context-engineering-rg \
  --min-replicas 0
```

Container will start automatically on first request (cold start ~5 seconds).

### Option 2: Dev/Test Pricing

Use smaller SKUs for development:
```bash
az containerapp update \
  --name coretext-mcp \
  --resource-group context-engineering-rg \
  --cpu 0.25 \
  --memory 0.5Gi
```

### Option 3: Scheduled Scaling

Scale down during off-hours using Azure Automation or Logic Apps.

## Security

### Best Practices Implemented

✅ **Non-root user** - Container runs as `node` user
✅ **Minimal base image** - Alpine Linux (small attack surface)
✅ **Health checks** - Automatic restart on failure
✅ **Managed identity** - Can be integrated for Azure service access
✅ **HTTPS only** - Automatic with Container Apps
✅ **No hardcoded secrets** - Environment variables only

### Additional Security (Optional)

1. **Integrate with Key Vault:**
   ```bash
   az containerapp secret set \
     --name coretext-mcp \
     --resource-group context-engineering-rg \
     --secrets "deepseek-key=<value>"
   ```

2. **Enable managed identity:**
   ```bash
   az containerapp identity assign \
     --name coretext-mcp \
     --resource-group context-engineering-rg \
     --user-assigned context-msi
   ```

## Support

For issues:
1. Check logs: `az containerapp logs show ...`
2. Verify health: `curl https://YOUR-URL/health`
3. Review this guide's troubleshooting section
4. Check Azure status: https://status.azure.com

## Next Steps

1. ✅ Deploy to Azure (you are here)
2. Test with Claude Desktop
3. Monitor logs and metrics
4. Consider Cosmos DB migration for production scale
5. Set up Application Insights for advanced monitoring
