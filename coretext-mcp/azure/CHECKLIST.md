# Azure Deployment Checklist

Use this checklist before and during deployment.

## Pre-Deployment

### Azure Account Setup

- [ ] Azure subscription active
- [ ] Subscription ID confirmed: `92fd53f2-c38e-461a-9f50-e1ef3382c54c`
- [ ] Billing alert configured (optional but recommended)

### Resource Prerequisites

- [ ] Resource group exists: `context-engineering-rg`
  ```bash
  az group show --name context-engineering-rg
  ```

- [ ] Managed Identity exists: `context-msi`
  ```bash
  az identity show --name context-msi --resource-group context-engineering-rg
  ```

- [ ] Location confirmed: `eastus`

### Local Machine Setup

- [ ] Azure CLI installed (version 2.50+)
  ```bash
  az --version
  ```

- [ ] Docker installed and running
  ```bash
  docker --version
  docker ps  # Should not error
  ```

- [ ] Git Bash or Bash shell available

- [ ] Logged into Azure
  ```bash
  az login
  az account show  # Verify correct subscription
  ```

### API Keys

- [ ] DeepSeek API key ready (or plan to skip)
  - Get from: https://platform.deepseek.com/
  - Can skip - server works in fallback mode

### Cosmos DB Consideration

- [ ] Check if you already have a Cosmos DB Free Tier account
  ```bash
  az cosmosdb list --query "[?properties.enableFreeTier].{name:name,rg:resourceGroup}"
  ```

  **If you already have one:**
  - Option 1: Use existing account (modify Bicep)
  - Option 2: Remove `enableFreeTier: true` from main.bicep (costs ~$25/mo)

## During Deployment

### Script Execution

- [ ] Navigate to azure directory
  ```bash
  cd context-engineering-2/coretext-mcp/azure
  ```

- [ ] Make script executable
  ```bash
  chmod +x deploy.sh
  ```

- [ ] Run deployment
  ```bash
  ./deploy.sh
  ```

### Watch for Prompts

- [ ] Script verifies Azure CLI ✓
- [ ] Script verifies Docker ✓
- [ ] Script verifies Azure login ✓
- [ ] Script checks resource group ✓
- [ ] Script checks managed identity ✓
- [ ] Script creates/finds ACR ✓
- [ ] Script builds Docker image ✓
- [ ] Script pushes to ACR ✓
- [ ] Script prompts for DeepSeek API key (enter or skip)
- [ ] Bicep deployment starts (may take 5-10 minutes)

### Common Errors During Deployment

If you see: **"Resource group not found"**
```bash
az group create --name context-engineering-rg --location eastus
```

If you see: **"Managed identity not found"**
```bash
az identity create --name context-msi --resource-group context-engineering-rg
```

If you see: **"Free tier Cosmos DB already exists"**
- Edit `main.bicep` and remove `enableFreeTier: true` line
- Or update connection string to use existing free tier account

If you see: **"Docker daemon not running"**
- Start Docker Desktop
- Wait for it to fully initialize

## Post-Deployment

### Verify Deployment

- [ ] Note Container App URL from output
- [ ] Test health endpoint
  ```bash
  curl https://YOUR-APP-URL.eastus.azurecontainerapps.io/health
  ```

  Expected response:
  ```json
  {
    "status": "healthy",
    "timestamp": "2025-10-29T...",
    "memoryCount": 3,
    "enrichmentConfigured": true
  }
  ```

- [ ] Check deployment in Azure Portal
  - Navigate to: https://portal.azure.com
  - Find resource group: `context-engineering-rg`
  - Verify resources exist:
    - Container App
    - Cosmos DB account
    - Key Vault
    - Container Registry
    - Log Analytics workspace

### Test Functionality

- [ ] View logs
  ```bash
  az containerapp logs show \
    -n $(az containerapp list -g context-engineering-rg --query '[0].name' -o tsv) \
    -g context-engineering-rg \
    --tail 50
  ```

- [ ] Test with MCP Inspector (optional)
  ```bash
  npx @modelcontextprotocol/inspector https://YOUR-APP-URL
  ```

- [ ] Check Cosmos DB has data
  ```bash
  # Should show "coretext" database
  az cosmosdb sql database list \
    -g context-engineering-rg \
    -a $(az cosmosdb list -g context-engineering-rg --query '[0].name' -o tsv)
  ```

### Document Deployment Info

- [ ] Save Container App URL
- [ ] Save Cosmos DB account name
- [ ] Save Key Vault name
- [ ] Save Container Registry name

### Set Up Monitoring (Optional)

- [ ] Configure Application Insights
- [ ] Set up cost alerts
- [ ] Create uptime monitor

## Cost Management

### Verify Cost Configuration

- [ ] Container App scales to zero (check min replicas = 0)
  ```bash
  az containerapp show \
    -n $(az containerapp list -g context-engineering-rg --query '[0].name' -o tsv) \
    -g context-engineering-rg \
    --query "properties.template.scale"
  ```

- [ ] Cosmos DB using Free Tier
  ```bash
  az cosmosdb show \
    -n $(az cosmosdb list -g context-engineering-rg --query '[0].name' -o tsv) \
    -g context-engineering-rg \
    --query "properties.enableFreeTier"
  ```

- [ ] Log Analytics retention set to 30 days

### Set Cost Alert (Recommended)

```bash
# Create budget alert for $20/month
az consumption budget create \
  --resource-group context-engineering-rg \
  --budget-name coretext-budget \
  --amount 20 \
  --time-grain Monthly \
  --start-date $(date -u +%Y-%m-01) \
  --end-date $(date -u -d "+1 year" +%Y-%m-01)
```

## Maintenance Checklist

### Monthly Review

- [ ] Check actual costs vs. expected (~$8-15/mo)
- [ ] Review logs for errors
- [ ] Check Cosmos DB RU consumption
- [ ] Verify backups are working
- [ ] Update container image if needed

### When Updating Code

- [ ] Make changes to `src/index.js`
- [ ] Test locally with `npm run inspector`
- [ ] Rebuild Docker image
- [ ] Push to ACR
- [ ] Update Container App
- [ ] Verify health endpoint
- [ ] Check logs for errors

## Cleanup Checklist

### When Done with Deployment

**Option 1: Delete Everything**
```bash
az group delete --name context-engineering-rg --yes
```

**Option 2: Delete Specific Resources**
```bash
# Container App only
az containerapp delete -n YOUR_APP_NAME -g context-engineering-rg --yes

# Cosmos DB only (careful - deletes data!)
az cosmosdb delete -n YOUR_COSMOS_NAME -g context-engineering-rg --yes

# Container Registry only
az acr delete -n YOUR_ACR_NAME --yes
```

## Troubleshooting Reference

### Get Help

- [ ] Check deployment logs
  ```bash
  az deployment group show \
    --name YOUR_DEPLOYMENT_NAME \
    --resource-group context-engineering-rg
  ```

- [ ] Check Container App logs
  ```bash
  az containerapp logs show \
    -n YOUR_APP_NAME \
    -g context-engineering-rg \
    --follow
  ```

- [ ] Review Azure Portal for error messages
  - Portal: https://portal.azure.com
  - Navigate to Activity Log in resource group

### Common Issues

| Issue | Quick Fix |
|-------|-----------|
| Health check fails | Check logs, verify port 3000 exposed |
| Secrets not loading | Verify managed identity has Key Vault access |
| Out of memory | Increase memory in main.bicep (0.5Gi → 1Gi) |
| Slow cold starts | Set minReplicas to 1 (disables scale-to-zero) |
| High costs | Check Container App isn't stuck with replicas running |

## Success Criteria

Deployment is successful when:

- [ ] Health endpoint returns 200 OK
- [ ] Container App shows "Running" status in portal
- [ ] Logs show "🚀 CoreText MCP Server listening on port 3000"
- [ ] Cosmos DB shows "memories" container exists
- [ ] Key Vault shows 2 secrets (deepseek-api-key, cosmos-connection-string)
- [ ] Monthly cost estimate is ~$8-15

---

**Checklist Version**: 1.0.0
**Last Updated**: 2025-10-29

**Print this checklist** before deployment for easy tracking!
