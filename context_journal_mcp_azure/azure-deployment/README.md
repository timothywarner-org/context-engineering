# Azure Deployment Guide - Context Journal MCP Server

## 🎯 Overview

This package contains everything needed to deploy the Context Journal MCP Server to Azure Container Apps with Cosmos DB backend.

## 📦 Package Contents

```
azure-deployment/
├── context_journal_mcp_azure.py   # Azure-ready MCP server with Cosmos DB
├── Dockerfile                      # Container image definition
├── requirements-azure.txt          # Python dependencies with Azure SDKs
├── deploy.sh                       # Bash deployment script (macOS/Linux)
├── deploy.ps1                      # PowerShell deployment script (Windows)
├── .env.example                    # Environment variables template
└── README.md                       # This file
```

## 🚀 Quick Start

### **Prerequisites**

1. **Azure Account** with active subscription
   - Create free account: https://azure.microsoft.com/free/

2. **Azure CLI** installed and configured
   - Install: https://docs.microsoft.com/cli/azure/install-azure-cli
   - Test: `az --version`

3. **Docker** (optional - for local testing)
   - Install: https://docs.docker.com/get-docker/

### **One-Command Deployment**

**macOS/Linux:**
```bash
./deploy.sh
```

**Windows:**
```powershell
.\deploy.ps1
```

The script will:
- ✅ Create Azure Resource Group
- ✅ Provision Cosmos DB account, database, and container
- ✅ Create Azure Container Registry
- ✅ Build and push Docker image
- ✅ Deploy to Azure Container Apps
- ✅ Configure all connections and secrets

**Total deployment time:** ~10-15 minutes

---

## 📋 Manual Deployment Steps

If you prefer manual deployment or want to understand each step:

### **Step 1: Login to Azure**

```bash
az login
az account set --subscription "Your Subscription Name"
```

### **Step 2: Create Resource Group**

```bash
RESOURCE_GROUP="mcp-context-journal-rg"
LOCATION="eastus"

az group create \
  --name $RESOURCE_GROUP \
  --location $LOCATION
```

### **Step 3: Create Cosmos DB**

```bash
COSMOS_ACCOUNT_NAME="context-journal-db-$(date +%s)"

# Create account (takes 5-10 minutes)
az cosmosdb create \
  --name $COSMOS_ACCOUNT_NAME \
  --resource-group $RESOURCE_GROUP \
  --locations regionName=$LOCATION failoverPriority=0 \
  --default-consistency-level Session

# Create database
az cosmosdb sql database create \
  --account-name $COSMOS_ACCOUNT_NAME \
  --resource-group $RESOURCE_GROUP \
  --name context_db

# Create container
az cosmosdb sql container create \
  --account-name $COSMOS_ACCOUNT_NAME \
  --database-name context_db \
  --resource-group $RESOURCE_GROUP \
  --name entries \
  --partition-key-path "/id" \
  --throughput 400
```

### **Step 4: Get Connection Information**

```bash
# Get endpoint
COSMOS_ENDPOINT=$(az cosmosdb show \
  --name $COSMOS_ACCOUNT_NAME \
  --resource-group $RESOURCE_GROUP \
  --query documentEndpoint -o tsv)

# Get primary key
COSMOS_KEY=$(az cosmosdb keys list \
  --name $COSMOS_ACCOUNT_NAME \
  --resource-group $RESOURCE_GROUP \
  --query primaryMasterKey -o tsv)

echo "COSMOS_ENDPOINT=$COSMOS_ENDPOINT"
echo "COSMOS_KEY=$COSMOS_KEY"
```

### **Step 5: Create Container Registry**

```bash
ACR_NAME="contextjournalacr$(date +%s)"

az acr create \
  --name $ACR_NAME \
  --resource-group $RESOURCE_GROUP \
  --sku Basic \
  --admin-enabled true
```

### **Step 6: Build and Push Image**

```bash
# Build and push to ACR
az acr build \
  --registry $ACR_NAME \
  --image context-journal-mcp:latest \
  --file Dockerfile \
  .

# Or build locally and push
docker build -t context-journal-mcp:latest .
az acr login --name $ACR_NAME
docker tag context-journal-mcp:latest $ACR_NAME.azurecr.io/context-journal-mcp:latest
docker push $ACR_NAME.azurecr.io/context-journal-mcp:latest
```

### **Step 7: Create Container Apps Environment**

```bash
az containerapp env create \
  --name mcp-environment \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION
```

### **Step 8: Deploy Container App**

```bash
# Get ACR credentials
ACR_SERVER=$(az acr show --name $ACR_NAME --query loginServer -o tsv)
ACR_USERNAME=$(az acr credential show --name $ACR_NAME --query username -o tsv)
ACR_PASSWORD=$(az acr credential show --name $ACR_NAME --query passwords[0].value -o tsv)

# Deploy app
az containerapp create \
  --name context-journal-mcp \
  --resource-group $RESOURCE_GROUP \
  --environment mcp-environment \
  --image "$ACR_SERVER/context-journal-mcp:latest" \
  --registry-server "$ACR_SERVER" \
  --registry-username "$ACR_USERNAME" \
  --registry-password "$ACR_PASSWORD" \
  --target-port 8000 \
  --ingress external \
  --min-replicas 1 \
  --max-replicas 3 \
  --cpu 0.5 \
  --memory 1Gi \
  --env-vars \
    COSMOS_ENDPOINT="$COSMOS_ENDPOINT" \
  --secrets \
    cosmos-key="$COSMOS_KEY" \
  --env-vars \
    COSMOS_KEY=secretref:cosmos-key
```

### **Step 9: Get App URL**

```bash
APP_URL=$(az containerapp show \
  --name context-journal-mcp \
  --resource-group $RESOURCE_GROUP \
  --query properties.configuration.ingress.fqdn -o tsv)

echo "App URL: https://$APP_URL"
```

---

## 🔧 Configuration

### **Environment Variables**

Create `.env` file from template:

```bash
cp .env.example .env
```

Edit with your values:

```env
# Azure Cosmos DB Configuration
COSMOS_ENDPOINT=https://your-account.documents.azure.com:443/
COSMOS_KEY=your-primary-key-here
DATABASE_NAME=context_db
CONTAINER_NAME=entries

# Azure Container Registry
ACR_NAME=your-acr-name
IMAGE_NAME=context-journal-mcp
IMAGE_TAG=latest

# Container App Configuration
RESOURCE_GROUP=mcp-context-journal-rg
LOCATION=eastus
CONTAINER_APP_NAME=context-journal-mcp
```

### **Using Managed Identity (Recommended for Production)**

Instead of using Cosmos DB keys, use managed identity:

```bash
# Enable managed identity on Container App
az containerapp identity assign \
  --name context-journal-mcp \
  --resource-group $RESOURCE_GROUP \
  --system-assigned

# Get principal ID
PRINCIPAL_ID=$(az containerapp identity show \
  --name context-journal-mcp \
  --resource-group $RESOURCE_GROUP \
  --query principalId -o tsv)

# Grant Cosmos DB permissions
az cosmosdb sql role assignment create \
  --account-name $COSMOS_ACCOUNT_NAME \
  --resource-group $RESOURCE_GROUP \
  --role-definition-name "Cosmos DB Built-in Data Contributor" \
  --principal-id $PRINCIPAL_ID \
  --scope "/dbs/context_db"

# Remove COSMOS_KEY environment variable
az containerapp update \
  --name context-journal-mcp \
  --resource-group $RESOURCE_GROUP \
  --remove-env-vars COSMOS_KEY
```

---

## 🧪 Testing

### **Test Local Docker Build**

```bash
# Build image
docker build -t context-journal-mcp:test .

# Run locally (requires .env file)
docker run --env-file .env -p 8000:8000 context-journal-mcp:test
```

### **Test Azure Deployment**

```bash
# Get app URL
APP_URL=$(az containerapp show \
  --name context-journal-mcp \
  --resource-group $RESOURCE_GROUP \
  --query properties.configuration.ingress.fqdn -o tsv)

# Test health endpoint (if you add one)
curl https://$APP_URL/health

# View logs
az containerapp logs show \
  --name context-journal-mcp \
  --resource-group $RESOURCE_GROUP \
  --follow
```

### **Test from Claude Desktop**

Update Claude Desktop config to use HTTP endpoint:

```json
{
  "mcpServers": {
    "context-journal": {
      "url": "https://your-app-url.azurecontainerapps.io"
    }
  }
}
```

---

## 📊 Monitoring & Management

### **View Logs**

```bash
# Real-time logs
az containerapp logs show \
  --name context-journal-mcp \
  --resource-group $RESOURCE_GROUP \
  --follow

# Historical logs
az containerapp logs show \
  --name context-journal-mcp \
  --resource-group $RESOURCE_GROUP \
  --tail 100
```

### **View Metrics**

```bash
# Container App metrics
az monitor metrics list \
  --resource $CONTAINER_APP_ID \
  --metric "Requests"
```

### **Scale Application**

```bash
# Manual scale
az containerapp update \
  --name context-journal-mcp \
  --resource-group $RESOURCE_GROUP \
  --min-replicas 2 \
  --max-replicas 5

# Auto-scale based on HTTP requests
az containerapp update \
  --name context-journal-mcp \
  --resource-group $RESOURCE_GROUP \
  --scale-rule-name http-scaling \
  --scale-rule-type http \
  --scale-rule-http-concurrency 10
```

### **Update Application**

```bash
# Rebuild and deploy new version
az acr build \
  --registry $ACR_NAME \
  --image context-journal-mcp:v2 \
  --file Dockerfile \
  .

# Update container app
az containerapp update \
  --name context-journal-mcp \
  --resource-group $RESOURCE_GROUP \
  --image "$ACR_SERVER/context-journal-mcp:v2"
```

---

## 💰 Cost Optimization

### **Estimated Monthly Costs**

Based on minimal usage (development/testing):

| Service | Configuration | Est. Cost/Month |
|---------|--------------|-----------------|
| **Cosmos DB** | 400 RU/s, 1GB storage | ~$24 |
| **Container Apps** | 0.5 vCPU, 1GB RAM, 1 replica | ~$15 |
| **Container Registry** | Basic tier, <1GB storage | ~$5 |
| **Total** | | **~$44/month** |

### **Cost Reduction Tips**

1. **Use serverless Cosmos DB** for development:
   ```bash
   az cosmosdb create \
     --name $COSMOS_ACCOUNT_NAME \
     --resource-group $RESOURCE_GROUP \
     --capabilities EnableServerless
   ```

2. **Scale down during non-business hours:**
   ```bash
   # Stop (scale to 0)
   az containerapp update \
     --name context-journal-mcp \
     --resource-group $RESOURCE_GROUP \
     --min-replicas 0
   ```

3. **Use consumption-based Container Apps:**
   ```bash
   # Already using consumption plan if --min-replicas can be 0
   ```

---

## 🔒 Security Best Practices

### **1. Use Managed Identity**

See "Using Managed Identity" section above - eliminates key management.

### **2. Enable Private Endpoints**

```bash
# Create VNet
az network vnet create \
  --name mcp-vnet \
  --resource-group $RESOURCE_GROUP \
  --address-prefix 10.0.0.0/16

# Create private endpoint for Cosmos DB
az network private-endpoint create \
  --name cosmos-pe \
  --resource-group $RESOURCE_GROUP \
  --vnet-name mcp-vnet \
  --subnet default \
  --private-connection-resource-id $(az cosmosdb show --name $COSMOS_ACCOUNT_NAME --resource-group $RESOURCE_GROUP --query id -o tsv) \
  --group-id Sql
```

### **3. Rotate Keys Regularly**

```bash
# Rotate Cosmos DB key
az cosmosdb keys regenerate \
  --name $COSMOS_ACCOUNT_NAME \
  --resource-group $RESOURCE_GROUP \
  --key-kind primary

# Update Container App secret
az containerapp secret set \
  --name context-journal-mcp \
  --resource-group $RESOURCE_GROUP \
  --secrets cosmos-key="$NEW_KEY"
```

### **4. Enable Azure AD Authentication**

```bash
# Coming in future versions - integrate with Azure AD for user auth
```

---

## 🐛 Troubleshooting

### **Problem: Deployment Script Fails**

**Check Azure CLI version:**
```bash
az version
# Update if needed: https://docs.microsoft.com/cli/azure/update-azure-cli
```

**Check subscription:**
```bash
az account show
az account list --output table
```

### **Problem: Container App Won't Start**

**Check logs:**
```bash
az containerapp logs show \
  --name context-journal-mcp \
  --resource-group $RESOURCE_GROUP \
  --follow
```

**Common issues:**
- Missing environment variables
- Incorrect Cosmos DB connection string
- Image failed to pull from ACR

### **Problem: Can't Connect to Cosmos DB**

**Verify firewall rules:**
```bash
az cosmosdb firewall-rules list \
  --account-name $COSMOS_ACCOUNT_NAME \
  --resource-group $RESOURCE_GROUP
```

**Add Container App IP:**
```bash
# Get Container App outbound IP
az containerapp show \
  --name context-journal-mcp \
  --resource-group $RESOURCE_GROUP \
  --query properties.outboundIpAddresses

# Add to Cosmos DB firewall
az cosmosdb update \
  --name $COSMOS_ACCOUNT_NAME \
  --resource-group $RESOURCE_GROUP \
  --ip-range-filter "your-container-app-ip"
```

### **Problem: 429 (Too Many Requests) from Cosmos DB**

**Increase throughput:**
```bash
az cosmosdb sql container throughput update \
  --account-name $COSMOS_ACCOUNT_NAME \
  --database-name context_db \
  --name entries \
  --resource-group $RESOURCE_GROUP \
  --throughput 1000
```

---

## 🧹 Cleanup

### **Delete Everything**

```bash
az group delete \
  --name $RESOURCE_GROUP \
  --yes \
  --no-wait
```

### **Delete Individual Resources**

```bash
# Delete Container App
az containerapp delete \
  --name context-journal-mcp \
  --resource-group $RESOURCE_GROUP

# Delete Cosmos DB
az cosmosdb delete \
  --name $COSMOS_ACCOUNT_NAME \
  --resource-group $RESOURCE_GROUP

# Delete Container Registry
az acr delete \
  --name $ACR_NAME \
  --resource-group $RESOURCE_GROUP
```

---

## 📚 Additional Resources

- **Azure Container Apps:** https://docs.microsoft.com/azure/container-apps/
- **Azure Cosmos DB:** https://docs.microsoft.com/azure/cosmos-db/
- **MCP Protocol:** https://modelcontextprotocol.io
- **FastMCP SDK:** https://github.com/modelcontextprotocol/python-sdk

---

## 🎓 Course Integration

### **For Instructors**

**Segment 4 Demo Flow:**

1. **Show local version** (JSON file)
2. **Run deployment script** (while explaining each step)
3. **Wait for deployment** (use this time to explain architecture)
4. **Test deployed version** (show it works)
5. **Compare code** (highlight minimal changes)
6. **Discuss scaling** (show Azure Portal metrics)

**Timing:** 35-45 minutes including Q&A

**Pre-demo checklist:**
- [ ] Azure CLI installed and logged in
- [ ] Subscription has available quota
- [ ] Deployment script tested beforehand
- [ ] Backup plan if deployment fails

---

**Ready to deploy? Run `./deploy.sh` (macOS/Linux) or `.\deploy.ps1` (Windows)**
