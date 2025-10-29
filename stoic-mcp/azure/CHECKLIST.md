# Stoic MCP - Deployment Checklist

Use this checklist to ensure successful deployment and troubleshooting.

## Pre-Deployment Checklist

### ✅ Local Environment
- [ ] **Azure CLI installed**: Run `az --version` (minimum 2.50.0)
- [ ] **Docker installed**: Run `docker --version` (minimum 20.10)
- [ ] **Git repository cloned**: `git clone` and `cd context-engineering-2`
- [ ] **DeepSeek API key available**: Get from https://platform.deepseek.com/

### ✅ Azure Account Setup
- [ ] **Azure subscription active**: Run `az account show`
- [ ] **Logged into Azure**: Run `az login`
- [ ] **Correct subscription selected**: Run `az account set --subscription "YOUR_SUB_ID"`
- [ ] **Contributor access**: Verify you can create resources

### ✅ Azure Resources (One-Time)
- [ ] **Resource group exists**: `context-engineering-rg` (or create with `az group create`)
- [ ] **Managed identity exists**: `context-msi` (or create with `az identity create`)
- [ ] **Location set**: Default is `eastus` (can customize in deploy.sh)

### ✅ Cosmos DB Free Tier
- [ ] **Check existing free tier**: You can only have ONE Cosmos DB free tier per subscription
  ```bash
  az cosmosdb list --query "[?properties.enableFreeTier].name" -o table
  ```
- [ ] **If free tier exists**: Either use different subscription or modify `main.bicep` to remove `enableFreeTier: true`

### ✅ Environment Variables
- [ ] **DeepSeek API key**: Either in `../../.env` or ready to enter during deployment
- [ ] **Export custom variables** (optional):
  ```bash
  export SUBSCRIPTION_ID="your-sub-id"
  export RESOURCE_GROUP="your-rg"
  export LOCATION="eastus"
  export MANAGED_IDENTITY="your-msi"
  ```

## Deployment Checklist

### ✅ Run Deployment Script
- [ ] **Navigate to deployment directory**: `cd stoic-mcp/azure`
- [ ] **Make script executable**: `chmod +x deploy.sh`
- [ ] **Run deployment**: `./deploy.sh`

### ✅ Monitor Deployment Progress
- [ ] **Pre-flight checks pass**: Azure CLI, Docker, Azure login
- [ ] **Resource group verified**: Script confirms RG exists
- [ ] **Managed identity verified**: Script confirms MSI exists
- [ ] **ACR created/found**: Azure Container Registry ready
- [ ] **Docker build succeeds**: Multi-stage TypeScript build completes
- [ ] **Image pushed to ACR**: Docker push completes without errors
- [ ] **DeepSeek API key entered**: Key stored in Key Vault
- [ ] **Bicep deployment succeeds**: Infrastructure created
- [ ] **Deployment outputs displayed**: URLs and resource names shown

### ✅ Expected Output
```
==================================================
Stoic MCP Deployment Complete!
==================================================

Container App URL: https://stoic-app-XXXXX.azurecontainerapps.io
Cosmos DB Account: stoic-cosmos-XXXXX
Cosmos DB Database: stoic
Key Vault: stoic-kv-XXXXX

Health Check: https://stoic-app-XXXXX.azurecontainerapps.io/health
==================================================
```

## Post-Deployment Checklist

### ✅ Verify Container App
- [ ] **Health check responds**:
  ```bash
  curl https://YOUR_APP_URL/health
  # Expected: {"status":"healthy","timestamp":"...","service":"stoic-mcp"}
  ```
- [ ] **Container logs show startup**:
  ```bash
  az containerapp logs show -n stoic-app-XXXXX -g context-engineering-rg --tail 20
  # Expected: "Stoic MCP Server running on port 3000"
  ```
- [ ] **Container is running**:
  ```bash
  az containerapp show -n stoic-app-XXXXX -g context-engineering-rg --query "properties.runningStatus" -o tsv
  # Expected: "Running"
  ```

### ✅ Verify Cosmos DB
- [ ] **Database exists**:
  ```bash
  az cosmosdb sql database show -g context-engineering-rg -a stoic-cosmos-XXXXX -n stoic
  ```
- [ ] **Quotes container exists**:
  ```bash
  az cosmosdb sql container show -g context-engineering-rg -a stoic-cosmos-XXXXX -d stoic -n quotes
  ```
- [ ] **Metadata container exists**:
  ```bash
  az cosmosdb sql container show -g context-engineering-rg -a stoic-cosmos-XXXXX -d stoic -n metadata
  ```

### ✅ Verify Key Vault
- [ ] **Key Vault exists**:
  ```bash
  az keyvault show --name stoic-kv-XXXXX -g context-engineering-rg
  ```
- [ ] **DeepSeek secret stored**:
  ```bash
  az keyvault secret list --vault-name stoic-kv-XXXXX --query "[?name=='deepseek-api-key'].name" -o tsv
  # Expected: deepseek-api-key
  ```
- [ ] **Cosmos connection secret stored**:
  ```bash
  az keyvault secret list --vault-name stoic-kv-XXXXX --query "[?name=='cosmos-connection-string'].name" -o tsv
  # Expected: cosmos-connection-string
  ```

### ✅ Verify Access & Security
- [ ] **Managed identity has Key Vault access**:
  ```bash
  az role assignment list --assignee YOUR_MSI_PRINCIPAL_ID --scope /subscriptions/YOUR_SUB/resourceGroups/context-engineering-rg/providers/Microsoft.KeyVault/vaults/stoic-kv-XXXXX
  # Expected: Key Vault Secrets User role
  ```
- [ ] **Container App uses managed identity**:
  ```bash
  az containerapp show -n stoic-app-XXXXX -g context-engineering-rg --query "identity.type" -o tsv
  # Expected: UserAssigned
  ```

### ✅ Test MCP Functionality
- [ ] **Open MCP Inspector**: Navigate to https://inspector.modelcontextprotocol.io/
- [ ] **Connect to server**: Enter your Container App URL
- [ ] **View available tools**: Should see 11 tools (get_random_quote, search_quotes, etc.)
- [ ] **Test a tool**: Try "get_random_quote" - should return a Stoic quote
- [ ] **Test AI explanation**: Try "explain_quote" - should use DeepSeek API

## Troubleshooting Checklist

### ❌ Deployment Fails

#### "Azure CLI not found"
- [ ] Install Azure CLI: https://aka.ms/azure-cli
- [ ] Verify: `az --version`

#### "Docker not found"
- [ ] Install Docker: https://docs.docker.com/get-docker/
- [ ] Verify: `docker --version`
- [ ] Start Docker daemon: `docker ps`

#### "Not logged into Azure"
- [ ] Run: `az login`
- [ ] Verify: `az account show`

#### "Resource group not found"
- [ ] Create resource group:
  ```bash
  az group create --name context-engineering-rg --location eastus
  ```

#### "Managed identity not found"
- [ ] Create managed identity:
  ```bash
  az identity create --name context-msi --resource-group context-engineering-rg
  ```

#### "Cosmos DB free tier already in use"
- [ ] Check existing free tier:
  ```bash
  az cosmosdb list --query "[?properties.enableFreeTier].name" -o table
  ```
- [ ] Option 1: Use different subscription
- [ ] Option 2: Edit `main.bicep` line 75, change `enableFreeTier: true` to `enableFreeTier: false`
  - **Warning**: This will cost ~$25/month for provisioned throughput

#### "ACR login failed"
- [ ] Login manually:
  ```bash
  az acr login --name YOUR_ACR_NAME
  ```
- [ ] Re-run deployment: `./deploy.sh`

#### "Docker build failed"
- [ ] Check you're in correct directory: `cd stoic-mcp/azure`
- [ ] Verify `../local/Dockerfile` exists
- [ ] Check `../local/src/` has TypeScript source files
- [ ] Check `../local/tsconfig.json` exists
- [ ] Try manual build:
  ```bash
  cd ../local
  docker build -t test-build .
  ```

#### "Bicep deployment failed"
- [ ] Check error message in script output
- [ ] View deployment details:
  ```bash
  az deployment group show --name YOUR_DEPLOYMENT_NAME --resource-group context-engineering-rg
  ```
- [ ] Common issues:
  - Free tier conflict (see Cosmos DB section above)
  - Missing throughput configuration (check main.bicep line 103)
  - Invalid container image reference

### ❌ Container Not Starting

#### Container App shows "Provisioning"
- [ ] Wait 3-5 minutes for initial startup
- [ ] Check logs:
  ```bash
  az containerapp logs show -n stoic-app-XXXXX -g context-engineering-rg --tail 50
  ```

#### Health check returns 503
- [ ] Check container status:
  ```bash
  az containerapp revision list -n stoic-app-XXXXX -g context-engineering-rg -o table
  ```
- [ ] Check for errors in logs
- [ ] Verify image exists in ACR:
  ```bash
  az acr repository show -n YOUR_ACR --repository stoic-mcp
  ```

#### "Cannot connect to Cosmos DB"
- [ ] Verify connection string in Key Vault:
  ```bash
  az keyvault secret show --vault-name stoic-kv-XXXXX --name cosmos-connection-string
  ```
- [ ] Check Cosmos DB firewall (should allow Azure services):
  ```bash
  az cosmosdb show --name stoic-cosmos-XXXXX --resource-group context-engineering-rg --query "ipRules"
  ```

#### "Key Vault access denied"
- [ ] Verify role assignment exists:
  ```bash
  az role assignment list --assignee YOUR_MSI_PRINCIPAL_ID --all
  ```
- [ ] Re-assign if missing:
  ```bash
  az role assignment create \
    --role "Key Vault Secrets User" \
    --assignee YOUR_MSI_PRINCIPAL_ID \
    --scope /subscriptions/YOUR_SUB/resourceGroups/context-engineering-rg/providers/Microsoft.KeyVault/vaults/stoic-kv-XXXXX
  ```

### ❌ MCP Tools Not Working

#### "DeepSeek API error"
- [ ] Verify API key in Key Vault:
  ```bash
  az keyvault secret show --vault-name stoic-kv-XXXXX --name deepseek-api-key --query "value" -o tsv
  ```
- [ ] Test API key manually:
  ```bash
  curl https://api.deepseek.com/v1/chat/completions \
    -H "Authorization: Bearer YOUR_KEY" \
    -H "Content-Type: application/json" \
    -d '{"model":"deepseek-chat","messages":[{"role":"user","content":"test"}]}'
  ```
- [ ] Update key in Key Vault if invalid:
  ```bash
  az keyvault secret set --vault-name stoic-kv-XXXXX --name deepseek-api-key --value "new-key"
  az containerapp revision restart -n stoic-app-XXXXX -g context-engineering-rg
  ```

#### "No quotes returned"
- [ ] Database starts empty - populate with quotes:
  - Use MCP Inspector to add quotes via `add_quote` tool
  - Or bulk import from `quotes.json`
- [ ] Verify containers exist:
  ```bash
  az cosmosdb sql container show -g context-engineering-rg -a stoic-cosmos-XXXXX -d stoic -n quotes
  ```

## Update Checklist

### ✅ Update Container Image
- [ ] Make code changes in `stoic-mcp/local/src/`
- [ ] Navigate to `stoic-mcp/local`
- [ ] Rebuild image:
  ```bash
  docker build -t YOUR_ACR.azurecr.io/stoic-mcp:latest .
  ```
- [ ] Push to ACR:
  ```bash
  az acr login --name YOUR_ACR
  docker push YOUR_ACR.azurecr.io/stoic-mcp:latest
  ```
- [ ] Update Container App:
  ```bash
  az containerapp update -n stoic-app-XXXXX -g context-engineering-rg --image YOUR_ACR.azurecr.io/stoic-mcp:latest
  ```
- [ ] Verify new version running:
  ```bash
  curl https://YOUR_APP_URL/health
  ```

### ✅ Update Environment Variables
- [ ] Update in Azure:
  ```bash
  az containerapp update -n stoic-app-XXXXX -g context-engineering-rg --set-env-vars "NEW_VAR=value"
  ```
- [ ] Restart if needed:
  ```bash
  az containerapp revision restart -n stoic-app-XXXXX -g context-engineering-rg
  ```

### ✅ Update Secrets
- [ ] Update in Key Vault:
  ```bash
  az keyvault secret set --vault-name stoic-kv-XXXXX --name deepseek-api-key --value "new-key"
  ```
- [ ] Restart Container App:
  ```bash
  az containerapp revision restart -n stoic-app-XXXXX -g context-engineering-rg
  ```

## Cleanup Checklist

### ✅ Remove Deployment
- [ ] Delete deployment (keeps resources):
  ```bash
  az deployment group delete --name YOUR_DEPLOYMENT_NAME --resource-group context-engineering-rg
  ```
- [ ] Delete all resources:
  ```bash
  az group delete --name context-engineering-rg --yes --no-wait
  ```
- [ ] Delete ACR (if no longer needed):
  ```bash
  az acr delete --name YOUR_ACR --yes
  ```

## Cost Monitoring Checklist

### ✅ Monitor Costs
- [ ] View cost analysis in Azure Portal
- [ ] Set budget alerts:
  ```bash
  az consumption budget create --budget-name stoic-budget --amount 20 --time-grain Monthly --resource-group context-engineering-rg
  ```
- [ ] Review resource usage:
  - Container App: Check replica count and CPU/memory usage
  - Cosmos DB: Monitor RU/s consumption (free tier = 1000 RU/s)
  - Log Analytics: Review data ingestion (minimize logs if high)

### ✅ Optimize Costs
- [ ] **Scale to zero enabled**: Check `main.bicep` line 345 (`minReplicas: 0`)
- [ ] **Free tier active**: Check Cosmos DB has free tier enabled
- [ ] **Minimal resources**: Container App uses 0.25 CPU, 0.5Gi RAM
- [ ] **Log retention**: Set to 30 days (line 62 in main.bicep)

---

**Total Checklist Items**: 80+
**Estimated Time**: 15-20 minutes
**Difficulty**: Intermediate
