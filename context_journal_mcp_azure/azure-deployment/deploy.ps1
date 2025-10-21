# Azure Deployment Script for Context Journal MCP Server (PowerShell)
# This script creates all necessary Azure resources and deploys the MCP server

# ============================================================================
# Configuration Variables - CUSTOMIZE THESE
# ============================================================================

$RESOURCE_GROUP = "mcp-context-journal-rg"
$LOCATION = "eastus"
$COSMOS_ACCOUNT_NAME = "context-journal-db"
$DATABASE_NAME = "context_db"
$CONTAINER_NAME = "entries"
$ACR_NAME = "contextjournalacr"
$CONTAINER_APP_NAME = "context-journal-mcp"
$CONTAINER_APP_ENV = "mcp-environment"
$IMAGE_NAME = "context-journal-mcp"
$IMAGE_TAG = "latest"

# ============================================================================
# Helper Functions
# ============================================================================

function Write-Info {
    param($Message)
    Write-Host "[INFO] $Message" -ForegroundColor Blue
}

function Write-Success {
    param($Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor Green
}

function Write-Warning {
    param($Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

function Write-ErrorMsg {
    param($Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

# ============================================================================
# Step 1: Verify Azure CLI
# ============================================================================

Write-Info "Verifying Azure CLI installation..."

if (!(Get-Command az -ErrorAction SilentlyContinue)) {
    Write-ErrorMsg "Azure CLI is not installed. Please install from: https://docs.microsoft.com/cli/azure/install-azure-cli"
    exit 1
}

$azVersion = az version --query '"azure-cli"' -o tsv
Write-Success "Azure CLI found: $azVersion"

# ============================================================================
# Step 2: Login to Azure
# ============================================================================

Write-Info "Checking Azure login status..."

$accountInfo = az account show 2>$null
if (!$accountInfo) {
    Write-Warning "Not logged in to Azure. Initiating login..."
    az login
} else {
    Write-Success "Already logged in to Azure"
    $subscription = az account show --query name -o tsv
    Write-Info "Current subscription: $subscription"
}

# ============================================================================
# Step 3: Create Resource Group
# ============================================================================

Write-Info "Creating resource group: $RESOURCE_GROUP in $LOCATION..."

$rgExists = az group show --name $RESOURCE_GROUP 2>$null
if ($rgExists) {
    Write-Warning "Resource group already exists"
} else {
    az group create `
        --name $RESOURCE_GROUP `
        --location $LOCATION `
        --output none
    Write-Success "Resource group created"
}

# ============================================================================
# Step 4: Create Azure Cosmos DB Account
# ============================================================================

Write-Info "Creating Cosmos DB account: $COSMOS_ACCOUNT_NAME (this may take several minutes)..."

$cosmosExists = az cosmosdb show --name $COSMOS_ACCOUNT_NAME --resource-group $RESOURCE_GROUP 2>$null
if ($cosmosExists) {
    Write-Warning "Cosmos DB account already exists"
} else {
    az cosmosdb create `
        --name $COSMOS_ACCOUNT_NAME `
        --resource-group $RESOURCE_GROUP `
        --locations regionName=$LOCATION failoverPriority=0 isZoneRedundant=False `
        --default-consistency-level Session `
        --enable-automatic-failover false `
        --output none
    Write-Success "Cosmos DB account created"
}

# ============================================================================
# Step 5: Create Database
# ============================================================================

Write-Info "Creating database: $DATABASE_NAME..."

$dbExists = az cosmosdb sql database show `
    --account-name $COSMOS_ACCOUNT_NAME `
    --resource-group $RESOURCE_GROUP `
    --name $DATABASE_NAME 2>$null

if ($dbExists) {
    Write-Warning "Database already exists"
} else {
    az cosmosdb sql database create `
        --account-name $COSMOS_ACCOUNT_NAME `
        --resource-group $RESOURCE_GROUP `
        --name $DATABASE_NAME `
        --output none
    Write-Success "Database created"
}

# ============================================================================
# Step 6: Create Container
# ============================================================================

Write-Info "Creating container: $CONTAINER_NAME..."

$containerExists = az cosmosdb sql container show `
    --account-name $COSMOS_ACCOUNT_NAME `
    --database-name $DATABASE_NAME `
    --resource-group $RESOURCE_GROUP `
    --name $CONTAINER_NAME 2>$null

if ($containerExists) {
    Write-Warning "Container already exists"
} else {
    az cosmosdb sql container create `
        --account-name $COSMOS_ACCOUNT_NAME `
        --database-name $DATABASE_NAME `
        --resource-group $RESOURCE_GROUP `
        --name $CONTAINER_NAME `
        --partition-key-path "/id" `
        --throughput 400 `
        --output none
    Write-Success "Container created"
}

# ============================================================================
# Step 7: Get Cosmos DB Connection Information
# ============================================================================

Write-Info "Retrieving Cosmos DB connection information..."

$COSMOS_ENDPOINT = az cosmosdb show `
    --name $COSMOS_ACCOUNT_NAME `
    --resource-group $RESOURCE_GROUP `
    --query documentEndpoint `
    -o tsv

$COSMOS_KEY = az cosmosdb keys list `
    --name $COSMOS_ACCOUNT_NAME `
    --resource-group $RESOURCE_GROUP `
    --query primaryMasterKey `
    -o tsv

Write-Success "Cosmos DB endpoint: $COSMOS_ENDPOINT"
Write-Info "Connection string retrieved (not displayed for security)"

# ============================================================================
# Step 8: Create Azure Container Registry
# ============================================================================

Write-Info "Creating Azure Container Registry: $ACR_NAME..."

$acrExists = az acr show --name $ACR_NAME --resource-group $RESOURCE_GROUP 2>$null
if ($acrExists) {
    Write-Warning "Container registry already exists"
} else {
    az acr create `
        --name $ACR_NAME `
        --resource-group $RESOURCE_GROUP `
        --sku Basic `
        --admin-enabled true `
        --output none
    Write-Success "Container registry created"
}

# ============================================================================
# Step 9: Build and Push Docker Image
# ============================================================================

Write-Info "Building and pushing Docker image to ACR..."

az acr build `
    --registry $ACR_NAME `
    --image "${IMAGE_NAME}:${IMAGE_TAG}" `
    --file Dockerfile `
    . `
    --output none

Write-Success "Docker image built and pushed: ${IMAGE_NAME}:${IMAGE_TAG}"

# ============================================================================
# Step 10: Create Container Apps Environment
# ============================================================================

Write-Info "Creating Container Apps environment: $CONTAINER_APP_ENV..."

$envExists = az containerapp env show `
    --name $CONTAINER_APP_ENV `
    --resource-group $RESOURCE_GROUP 2>$null

if ($envExists) {
    Write-Warning "Container Apps environment already exists"
} else {
    az containerapp env create `
        --name $CONTAINER_APP_ENV `
        --resource-group $RESOURCE_GROUP `
        --location $LOCATION `
        --output none
    Write-Success "Container Apps environment created"
}

# ============================================================================
# Step 11: Deploy Container App
# ============================================================================

Write-Info "Deploying Container App: $CONTAINER_APP_NAME..."

$ACR_LOGIN_SERVER = az acr show --name $ACR_NAME --resource-group $RESOURCE_GROUP --query loginServer -o tsv
$ACR_USERNAME = az acr credential show --name $ACR_NAME --query username -o tsv
$ACR_PASSWORD = az acr credential show --name $ACR_NAME --query passwords[0].value -o tsv

$appExists = az containerapp show `
    --name $CONTAINER_APP_NAME `
    --resource-group $RESOURCE_GROUP 2>$null

if ($appExists) {
    Write-Warning "Container App already exists - updating..."
    
    az containerapp update `
        --name $CONTAINER_APP_NAME `
        --resource-group $RESOURCE_GROUP `
        --image "${ACR_LOGIN_SERVER}/${IMAGE_NAME}:${IMAGE_TAG}" `
        --set-env-vars COSMOS_ENDPOINT="$COSMOS_ENDPOINT" `
        --secrets cosmos-key="$COSMOS_KEY" acr-password="$ACR_PASSWORD" `
        --output none
    
    Write-Success "Container App updated"
} else {
    az containerapp create `
        --name $CONTAINER_APP_NAME `
        --resource-group $RESOURCE_GROUP `
        --environment $CONTAINER_APP_ENV `
        --image "${ACR_LOGIN_SERVER}/${IMAGE_NAME}:${IMAGE_TAG}" `
        --registry-server "$ACR_LOGIN_SERVER" `
        --registry-username "$ACR_USERNAME" `
        --registry-password "$ACR_PASSWORD" `
        --target-port 8000 `
        --ingress external `
        --min-replicas 1 `
        --max-replicas 3 `
        --cpu 0.5 `
        --memory 1Gi `
        --env-vars COSMOS_ENDPOINT="$COSMOS_ENDPOINT" COSMOS_KEY=secretref:cosmos-key `
        --secrets cosmos-key="$COSMOS_KEY" `
        --output none
    
    Write-Success "Container App created"
}

# ============================================================================
# Step 12: Get Container App URL
# ============================================================================

Write-Info "Retrieving Container App URL..."

$APP_URL = az containerapp show `
    --name $CONTAINER_APP_NAME `
    --resource-group $RESOURCE_GROUP `
    --query properties.configuration.ingress.fqdn `
    -o tsv

# ============================================================================
# Deployment Complete
# ============================================================================

Write-Host ""
Write-Success "========================================="
Write-Success "Deployment Complete!"
Write-Success "========================================="
Write-Host ""
Write-Info "Resource Group: $RESOURCE_GROUP"
Write-Info "Cosmos DB Account: $COSMOS_ACCOUNT_NAME"
Write-Info "Cosmos DB Endpoint: $COSMOS_ENDPOINT"
Write-Info "Container Registry: $ACR_NAME"
Write-Info "Container App: $CONTAINER_APP_NAME"
Write-Info "App URL: https://$APP_URL"
Write-Host ""
Write-Info "Next steps:"
Write-Host "  1. Test the deployment with:"
Write-Host "     Invoke-WebRequest https://$APP_URL/health"
Write-Host ""
Write-Host "  2. Configure Claude Desktop to use the HTTP endpoint:"
Write-Host "     {`"mcpServers`": {`"context-journal`": {`"url`": `"https://$APP_URL`"}}}"
Write-Host ""
Write-Host "  3. View logs:"
Write-Host "     az containerapp logs show --name $CONTAINER_APP_NAME --resource-group $RESOURCE_GROUP --follow"
Write-Host ""
Write-Warning "IMPORTANT: Your Cosmos DB key is stored as a secret. To rotate:"
Write-Host "  az cosmosdb keys regenerate --name $COSMOS_ACCOUNT_NAME --resource-group $RESOURCE_GROUP --key-kind primary"
Write-Host ""
