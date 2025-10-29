# CoreText MCP - Azure Quick Start

> **TL;DR**: Deploy to Azure in 5 minutes

## Prerequisites Check

```bash
# Check you have everything
az --version      # Need 2.50+
docker --version  # Any recent version
az login          # Must be logged in
```

## One-Command Deployment

```bash
cd coretext-mcp/azure
./deploy.sh
```

That's it. The script handles everything.

## What Gets Created

| Resource | Type | Cost |
|----------|------|------|
| Cosmos DB | Free Tier | $0 |
| Container App | Consumption | ~$1-5/mo |
| Key Vault | Standard | ~$0.03/mo |
| ACR | Basic | ~$5/mo |
| Logs | 30-day | ~$2-5/mo |
| **TOTAL** | | **~$8-15/mo** |

## Test Deployment

```bash
# Get your app URL (output from deploy.sh)
APP_URL="https://coretext-app-xyz.eastus.azurecontainerapps.io"

# Test health
curl $APP_URL/health
```

Expected:
```json
{
  "status": "healthy",
  "timestamp": "2025-10-29T...",
  "memoryCount": 3,
  "enrichmentConfigured": true
}
```

## Update Your Code

```bash
# 1. Make changes to src/index.js
# 2. Rebuild and push
docker build -t YOUR_ACR.azurecr.io/coretext-mcp:latest .
docker push YOUR_ACR.azurecr.io/coretext-mcp:latest

# 3. Update Container App
az containerapp update \
  -n YOUR_APP_NAME \
  -g context-engineering-rg \
  --image YOUR_ACR.azurecr.io/coretext-mcp:latest
```

## View Logs

```bash
az containerapp logs show \
  -n YOUR_APP_NAME \
  -g context-engineering-rg \
  --follow
```

## Common Issues

**"Cosmos DB free tier already exists"**
- You can only have ONE free tier per subscription
- Solution: Remove `enableFreeTier: true` from main.bicep (costs ~$25/mo)

**"Managed identity not found"**
```bash
az identity create \
  --name context-msi \
  --resource-group context-engineering-rg
```

**"Resource group not found"**
```bash
az group create \
  --name context-engineering-rg \
  --location eastus
```

## Clean Up

```bash
# Delete everything
az group delete \
  --name context-engineering-rg \
  --yes
```

## Need More Help?

- Full docs: [README.md](README.md)
- Azure Portal: https://portal.azure.com
- MCP Docs: https://modelcontextprotocol.io/docs

---

**Pro Tip**: The deployment script auto-detects your DeepSeek API key from `../.env`. Just press Enter when prompted to use it.
