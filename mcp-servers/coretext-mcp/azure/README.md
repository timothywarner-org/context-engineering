# CoreText MCP - Azure Deployment Guide

> **MVP Edition**: Cost-optimized deployment for production testing (~$3-10/month)
>
> **Includes**: Manual deployment script + GitHub Actions CI/CD

## Architecture Overview

This deployment uses Azure's most cost-effective services:

```
┌─────────────────────────────────────────────────────────────┐
│                     Azure Container Apps                    │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  CoreText MCP Server (Node.js)                      │   │
│  │  - Scales to zero when idle (cost savings!)         │   │
│  │  - Min: 0 replicas, Max: 3 replicas                 │   │
│  │  - CPU: 0.25 cores, Memory: 0.5Gi                   │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ Uses Managed Identity
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      Azure Key Vault                        │
│  - DeepSeek API Key (encrypted)                             │
│  - Cosmos DB Connection String (encrypted)                  │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                  Cosmos DB (FREE TIER)                      │
│  - 1000 RU/s shared across all resources                   │
│  - 25GB storage included                                    │
│  - Serverless billing (pay-per-request)                    │
│  - Database: "coretext"                                     │
│  - Container: "memories"                                    │
└─────────────────────────────────────────────────────────────┘
```

## Cost Breakdown (Monthly Estimates)

| Service | Configuration | Estimated Cost |
|---------|--------------|----------------|
| **Cosmos DB** | Free Tier (1000 RU/s, 25GB) | **$0.00** |
| **Container Apps** | Consumption plan, scales to zero | **$1-5** |
| **Key Vault** | Standard tier, ~1000 operations | **$0.03** |
| **Log Analytics** | 30-day retention, ~1GB ingestion | **$2-5** |
| **Container Registry** | Basic tier, ~1GB storage | **$5** |
| **Managed Identity** | User-assigned identity | **$0.00** |
| **Total** | | **~$8-15/month** |

**Cost Optimization Features:**

- Container Apps scale to **zero replicas** when idle
- Cosmos DB Free Tier provides 1000 RU/s (good for MVP)
- Log retention limited to 30 days
- Minimal CPU/memory allocation

## Prerequisites

### Local Machine Requirements

1. **Azure CLI** (version 2.50+)

   ```bash
   az --version
   # Install: https://aka.ms/azure-cli
   ```

2. **Docker** (for building container images)

   ```bash
   docker --version
   # Install: https://docs.docker.com/get-docker/
   ```

3. **Git Bash** (Windows) or Bash shell (Linux/Mac)

### Azure Requirements

1. **Active Azure Subscription**
   - Subscription ID: `92fd53f2-c38e-461a-9f50-e1ef3382c54c`

2. **Resource Group** (must exist before deployment)

   ```bash
   az group create \
     --name context-engineering-rg \
     --location eastus
   ```

3. **Managed Identity** (must exist before deployment)

   ```bash
   az identity create \
     --name context-msi \
     --resource-group context-engineering-rg
   ```

4. **DeepSeek API Key** (optional - server works without it)
   - Get one from: <https://platform.deepseek.com/>

## Deployment Options

You have two deployment methods:

1. **Manual Script** (`deploy.sh`) - For initial setup and testing
2. **GitHub Actions** (CI/CD) - For automated deployments on every commit

---

## Option 1: Manual Deployment (Recommended for First Time)

### Automated Deployment Script

```bash
# Navigate to the azure directory
cd coretext-mcp/azure

# Make script executable (if not already)
chmod +x deploy.sh

# Run the deployment
./deploy.sh
```

The script will:

1. ✅ Verify Azure CLI and Docker installation
2. ✅ Check Azure login status
3. ✅ Verify resource group and managed identity exist
4. ✅ Create Azure Container Registry (if needed)
5. ✅ Build and push Docker image
6. ✅ Prompt for DeepSeek API key
7. ✅ Deploy infrastructure with Bicep
8. ✅ Display deployment outputs and next steps

**Expected output:**

```
[INFO] Starting CoreText MCP Azure Deployment
[SUCCESS] Azure CLI found: 2.55.0
[SUCCESS] Docker found: 24.0.7
[SUCCESS] Logged into Azure
...
[SUCCESS] ===================================================
[SUCCESS] CoreText MCP Deployment Complete!
[SUCCESS] ===================================================

Container App URL: https://coretext-app-abc123.eastus.azurecontainerapps.io
Cosmos DB Account: coretext-cosmos-abc123
Key Vault: coretext-kv-abc123

Health Check: https://coretext-app-abc123.eastus.azurecontainerapps.io/health
```

**What the script does:**

1. ✅ Creates Azure Container Registry (if needed)
2. ✅ Builds and pushes Docker image
3. ✅ Deploys infrastructure with Bicep
4. ✅ Configures secrets in Key Vault
5. ✅ Sets up managed identity permissions

---

## Option 2: GitHub Actions (CI/CD)

**For automated deployments on every commit to `main` branch.**

### Setup GitHub Actions

See detailed setup guide: **[.github/GITHUB_ACTIONS_SETUP.md](../../.github/GITHUB_ACTIONS_SETUP.md)**

**Quick summary:**

1. **Deploy manually first** (using deploy.sh above)
2. **Create Azure Service Principal**:

   ```bash
   az ad sp create-for-rbac \
     --name "github-actions-coretext-mcp" \
     --role contributor \
     --scopes /subscriptions/92fd53f2-c38e-461a-9f50-e1ef3382c54c/resourceGroups/context-engineering-rg \
     --sdk-auth
   ```

3. **Add GitHub Secrets**:
   - `AZURE_CREDENTIALS` - JSON output from above
   - `ACR_NAME` - Your ACR name (e.g., coretextacr123456)
   - `CONTAINER_APP_NAME` - Your app name (e.g., coretext-app-abc123)
4. **Push to main** - Deployment happens automatically!

**What GitHub Actions does:**

1. ✅ Triggers on push to `main` (when coretext-mcp/ changes)
2. ✅ Builds Docker image with caching
3. ✅ Pushes to ACR
4. ✅ Updates Container App
5. ✅ Performs health check
6. ✅ Creates deployment record in GitHub

**Workflow file**: `.github/workflows/deploy-coretext-mcp.yml`

---

## Option 3: Fully Manual Deployment

If you prefer complete manual control:

#### Step 1: Login to Azure

```bash
az login
az account set --subscription 92fd53f2-c38e-461a-9f50-e1ef3382c54c
```

#### Step 2: Create Container Registry

```bash
# Generate unique name (no hyphens, lowercase only)
ACR_NAME="coretextacr$(date +%s | tail -c 6)"

az acr create \
  --resource-group context-engineering-rg \
  --name $ACR_NAME \
  --sku Basic \
  --location eastus \
  --admin-enabled false

# Login to ACR
az acr login --name $ACR_NAME
```

#### Step 3: Build and Push Docker Image

```bash
# Navigate to coretext-mcp root
cd ..

# Build image
docker build -t ${ACR_NAME}.azurecr.io/coretext-mcp:latest .

# Push to ACR
docker push ${ACR_NAME}.azurecr.io/coretext-mcp:latest
```

#### Step 4: Deploy with Bicep

```bash
cd azure

# Create parameters file
cat > params.json <<EOF
{
  "\$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentParameters.json#",
  "contentVersion": "1.0.0.0",
  "parameters": {
    "location": { "value": "eastus" },
    "managedIdentityName": { "value": "context-msi" },
    "containerImage": { "value": "${ACR_NAME}.azurecr.io/coretext-mcp:latest" },
    "deepseekApiKey": { "value": "YOUR_DEEPSEEK_API_KEY_HERE" }
  }
}
EOF

# Deploy
az deployment group create \
  --name coretext-deployment-$(date +%Y%m%d-%H%M%S) \
  --resource-group context-engineering-rg \
  --template-file main.bicep \
  --parameters @params.json
```

## Post-Deployment Testing

### Health Check

```bash
# Get Container App URL
APP_URL=$(az containerapp list \
  --resource-group context-engineering-rg \
  --query "[0].properties.configuration.ingress.fqdn" \
  -o tsv)

# Test health endpoint
curl https://${APP_URL}/health

# Expected response:
# {
#   "status": "healthy",
#   "timestamp": "2025-10-29T...",
#   "memoryCount": 3,
#   "enrichmentConfigured": true,
#   "uptime": 123.45
# }
```

### View Logs

```bash
# Stream live logs
az containerapp logs show \
  -n $(az containerapp list -g context-engineering-rg --query '[0].name' -o tsv) \
  -g context-engineering-rg \
  --follow

# View last 100 lines
az containerapp logs show \
  -n $(az containerapp list -g context-engineering-rg --query '[0].name' -o tsv) \
  -g context-engineering-rg \
  --tail 100
```

### Test MCP Server

The Container App exposes the MCP server via HTTPS. You can connect to it using:

**MCP Inspector (local testing):**

```bash
# Forward the remote server locally
npx @modelcontextprotocol/inspector https://${APP_URL}
```

**Claude Desktop (production):**

Edit `%APPDATA%\Claude\claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "coretext-azure": {
      "url": "https://your-app-url.eastus.azurecontainerapps.io",
      "transport": "sse"
    }
  }
}
```

## Updating the Deployment

### Update Application Code

```bash
# Rebuild and push image
cd coretext-mcp
docker build -t ${ACR_NAME}.azurecr.io/coretext-mcp:latest .
docker push ${ACR_NAME}.azurecr.io/coretext-mcp:latest

# Update Container App (triggers restart)
az containerapp update \
  -n $(az containerapp list -g context-engineering-rg --query '[0].name' -o tsv) \
  -g context-engineering-rg \
  --image ${ACR_NAME}.azurecr.io/coretext-mcp:latest
```

### Update Secrets (e.g., API Key)

```bash
# Get Key Vault name
KV_NAME=$(az keyvault list \
  --resource-group context-engineering-rg \
  --query "[0].name" -o tsv)

# Update DeepSeek API key
az keyvault secret set \
  --vault-name $KV_NAME \
  --name deepseek-api-key \
  --value "new-api-key-here"

# Restart Container App to pick up new secret
az containerapp revision restart \
  -n $(az containerapp list -g context-engineering-rg --query '[0].name' -o tsv) \
  -g context-engineering-rg
```

### Update Infrastructure

```bash
# Modify main.bicep as needed, then redeploy
cd azure
az deployment group create \
  --name coretext-update-$(date +%Y%m%d-%H%M%S) \
  --resource-group context-engineering-rg \
  --template-file main.bicep \
  --parameters @params.json
```

## Monitoring and Troubleshooting

### View Metrics

```bash
# Container App metrics (requests, CPU, memory)
az monitor metrics list \
  --resource $(az containerapp show -n $(az containerapp list -g context-engineering-rg --query '[0].name' -o tsv) -g context-engineering-rg --query id -o tsv) \
  --metric "Requests"

# Cosmos DB metrics (RU consumption)
az monitor metrics list \
  --resource $(az cosmosdb show -n $(az cosmosdb list -g context-engineering-rg --query "[0].name" -o tsv) -g context-engineering-rg --query id -o tsv) \
  --metric "TotalRequestUnits"
```

### Common Issues

**Issue: Container App won't start**

```bash
# Check logs for errors
az containerapp logs show \
  -n $(az containerapp list -g context-engineering-rg --query '[0].name' -o tsv) \
  -g context-engineering-rg \
  --tail 50

# Check revision status
az containerapp revision list \
  -n $(az containerapp list -g context-engineering-rg --query '[0].name' -o tsv) \
  -g context-engineering-rg
```

**Issue: Health check failing**

```bash
# Test health endpoint directly
curl -v https://${APP_URL}/health

# If 404, ensure server has health endpoint in src/index.js
```

**Issue: Cosmos DB free tier already used**

```bash
# Check if you already have a free tier account
az cosmosdb list --query "[?properties.enableFreeTier].{name:name,rg:resourceGroup}"

# Solution: Either:
# 1. Use existing free tier account (update main.bicep)
# 2. Remove enableFreeTier: true from main.bicep (will cost ~$25/month for 400 RU/s)
```

**Issue: Managed Identity permission errors**

```bash
# Verify managed identity has Key Vault access
az role assignment list \
  --assignee $(az identity show -n context-msi -g context-engineering-rg --query principalId -o tsv) \
  --scope $(az keyvault show -n $KV_NAME -g context-engineering-rg --query id -o tsv)

# Re-assign role if needed
az role assignment create \
  --role "Key Vault Secrets User" \
  --assignee $(az identity show -n context-msi -g context-engineering-rg --query principalId -o tsv) \
  --scope $(az keyvault show -n $KV_NAME -g context-engineering-rg --query id -o tsv)
```

## Scaling Configuration

### Increase Resources (if needed)

Edit `main.bicep` and update:

```bicep
resources: {
  cpu: json('0.5')     // Increase from 0.25
  memory: '1Gi'        // Increase from 0.5Gi
}

scale: {
  minReplicas: 1       // Keep at least 1 running (no scale-to-zero)
  maxReplicas: 5       // Increase max replicas
}
```

Redeploy after changes.

### Enable Always-On (Disable Scale-to-Zero)

```bash
# Set minReplicas to 1 (will increase cost but improve response time)
az containerapp update \
  -n $(az containerapp list -g context-engineering-rg --query '[0].name' -o tsv) \
  -g context-engineering-rg \
  --min-replicas 1
```

## Cleanup / Teardown

### Delete Entire Deployment

```bash
# Delete resource group (removes ALL resources)
az group delete \
  --name context-engineering-rg \
  --yes \
  --no-wait
```

### Delete Individual Resources

```bash
# Delete Container App only
az containerapp delete \
  -n $(az containerapp list -g context-engineering-rg --query '[0].name' -o tsv) \
  -g context-engineering-rg \
  --yes

# Delete Cosmos DB only
az cosmosdb delete \
  -n $(az cosmosdb list -g context-engineering-rg --query "[0].name" -o tsv) \
  -g context-engineering-rg \
  --yes

# Delete Container Registry only
az acr delete \
  -n $ACR_NAME \
  -g context-engineering-rg \
  --yes
```

## File Structure

```
coretext-mcp/
├── azure/
│   ├── main.bicep           # Infrastructure as Code (Bicep)
│   ├── parameters.json      # Deployment parameters template
│   ├── deploy.sh            # Automated deployment script
│   └── README.md            # This file
├── Dockerfile               # Container image definition
├── .dockerignore            # Files to exclude from image
├── src/
│   └── index.js             # MCP server implementation
└── package.json             # Node.js dependencies
```

## Security Best Practices

1. **Never commit secrets to Git**
   - Use Key Vault for all secrets
   - Use Managed Identity for authentication

2. **Enable soft-delete on Key Vault**
   - Already enabled in Bicep (7-day retention)
   - Recover deleted secrets within retention period

3. **Use RBAC instead of access policies**
   - Bicep template uses `enableRbacAuthorization: true`

4. **Run container as non-root user**
   - Dockerfile uses `USER nodejs` (UID 1001)

5. **Enable network isolation (future enhancement)**
   - Add VNET integration to Container App
   - Use Private Endpoints for Cosmos DB

## Next Steps

1. **Enable CI/CD**
   - Set up GitHub Actions for automated deployments
   - Trigger on push to `main` branch

2. **Add Monitoring**
   - Configure Application Insights for distributed tracing
   - Set up alerts for errors and high latency

3. **Implement Backup**
   - Enable Cosmos DB backup (point-in-time restore)
   - Schedule: continuous backup (7-30 days)

4. **Add Custom Domain**
   - Configure custom domain for Container App
   - Add TLS certificate via Key Vault

5. **Scale to Production**
   - Increase RU/s for Cosmos DB
   - Enable multi-region replication
   - Add CDN for static assets

## Support

**Deployment Issues:**

- Check the deployment logs: `az deployment group show`
- Review troubleshooting section above

**Azure Support:**

- <https://portal.azure.com> -> Help + Support
- Or file ticket via Azure CLI: `az support tickets create`

**MCP Protocol Issues:**

- MCP Specification: <https://spec.modelcontextprotocol.io/>
- MCP Inspector: <https://github.com/modelcontextprotocol/inspector>

---

**Deployment Version:** 1.0.0
**Last Updated:** 2025-10-29
**Tested On:** Azure CLI 2.55.0, Docker 24.0.7
