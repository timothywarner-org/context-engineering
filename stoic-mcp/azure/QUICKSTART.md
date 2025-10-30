# Stoic MCP - Azure Quick Start (5 Minutes)

Get the Stoic MCP server deployed to Azure in under 5 minutes.

## Prerequisites Checklist

- [ ] Azure CLI installed (`az --version`)
- [ ] Docker installed (`docker --version`)
- [ ] Logged into Azure (`az login`)
- [ ] DeepSeek API key (get from <https://platform.deepseek.com/>)

## One-Time Setup (First Deployment Only)

```bash
# Set subscription
az account set --subscription "YOUR_SUBSCRIPTION_ID"

# Create resource group
az group create \
  --name context-engineering-rg \
  --location eastus

# Create managed identity
az identity create \
  --name context-msi \
  --resource-group context-engineering-rg
```

## Deploy

```bash
# Navigate to deployment directory
cd stoic-mcp/azure

# Run deployment script
./deploy.sh
```

That's it! The script will:

1. Verify prerequisites
2. Create/find Azure Container Registry
3. Build Docker image
4. Deploy infrastructure (Cosmos DB, Container App, Key Vault)
5. Display your app URL

## Verify

```bash
# Check health endpoint (copy URL from script output)
curl https://YOUR_APP_URL/health

# Expected: {"status":"healthy","timestamp":"...","service":"stoic-mcp"}
```

## What You Get

- **Stoic MCP Server**: Running in Azure Container Apps
- **Cosmos DB**: Two containers (quotes, metadata) on free tier
- **Key Vault**: Secure storage for DeepSeek API key
- **Container Registry**: Stores your Docker image
- **Cost**: ~$8-15/month for MVP workload

## Troubleshooting

### Script fails at "az acr login"

```bash
# Login manually
az acr login --name YOUR_ACR_NAME
# Re-run script
./deploy.sh
```

### "Resource group not found"

```bash
# Create it first
az group create --name context-engineering-rg --location eastus
# Re-run script
./deploy.sh
```

### Health check returns 503

Wait 2-3 minutes for container to start, then retry:

```bash
curl https://YOUR_APP_URL/health
```

## Next Steps

1. **Test with MCP Inspector**: Connect to your Container App URL
2. **View Logs**: `az containerapp logs show -n YOUR_APP_NAME -g context-engineering-rg --follow`
3. **Populate Quotes**: Use MCP tools to add quotes or bulk import
4. **Set Up CI/CD**: Configure GitHub Actions for automated deployment

## Full Documentation

See [README.md](./README.md) for complete deployment guide.

---

**Time to Deploy**: 5-10 minutes
**Difficulty**: Easy
**Cost**: $8-15/month
