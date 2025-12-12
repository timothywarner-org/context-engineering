#!/bin/bash

# Azure Deployment Script for Context Journal MCP Server
# This script creates all necessary Azure resources and deploys the MCP server

set -e  # Exit on error

# ============================================================================
# Configuration Variables - CUSTOMIZE THESE
# ============================================================================

RESOURCE_GROUP="mcp-context-journal-rg"
LOCATION="eastus"
COSMOS_ACCOUNT_NAME="context-journal-db"
DATABASE_NAME="context_db"
CONTAINER_NAME="entries"
ACR_NAME="contextjournalacr"
CONTAINER_APP_NAME="context-journal-mcp"
CONTAINER_APP_ENV="mcp-environment"
IMAGE_NAME="context-journal-mcp"
IMAGE_TAG="latest"

# ============================================================================
# Colors for output
# ============================================================================

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ============================================================================
# Helper Functions
# ============================================================================

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# ============================================================================
# Step 1: Verify Azure CLI
# ============================================================================

log_info "Verifying Azure CLI installation..."

if ! command -v az &> /dev/null; then
    log_error "Azure CLI is not installed. Please install from: https://docs.microsoft.com/cli/azure/install-azure-cli"
    exit 1
fi

log_success "Azure CLI found: $(az version --query '"azure-cli"' -o tsv)"

# ============================================================================
# Step 2: Login to Azure
# ============================================================================

log_info "Checking Azure login status..."

if ! az account show &> /dev/null; then
    log_warning "Not logged in to Azure. Initiating login..."
    az login
else
    log_success "Already logged in to Azure"
    SUBSCRIPTION=$(az account show --query name -o tsv)
    log_info "Current subscription: $SUBSCRIPTION"
fi

# ============================================================================
# Step 3: Create Resource Group
# ============================================================================

log_info "Creating resource group: $RESOURCE_GROUP in $LOCATION..."

if az group show --name $RESOURCE_GROUP &> /dev/null; then
    log_warning "Resource group already exists"
else
    az group create \
        --name $RESOURCE_GROUP \
        --location $LOCATION \
        --output none
    log_success "Resource group created"
fi

# ============================================================================
# Step 4: Create Azure Cosmos DB Account
# ============================================================================

log_info "Creating Cosmos DB account: $COSMOS_ACCOUNT_NAME (this may take several minutes)..."

if az cosmosdb show --name $COSMOS_ACCOUNT_NAME --resource-group $RESOURCE_GROUP &> /dev/null; then
    log_warning "Cosmos DB account already exists"
else
    az cosmosdb create \
        --name $COSMOS_ACCOUNT_NAME \
        --resource-group $RESOURCE_GROUP \
        --locations regionName=$LOCATION failoverPriority=0 isZoneRedundant=False \
        --default-consistency-level Session \
        --enable-automatic-failover false \
        --output none
    log_success "Cosmos DB account created"
fi

# ============================================================================
# Step 5: Create Database
# ============================================================================

log_info "Creating database: $DATABASE_NAME..."

if az cosmosdb sql database show \
    --account-name $COSMOS_ACCOUNT_NAME \
    --resource-group $RESOURCE_GROUP \
    --name $DATABASE_NAME &> /dev/null; then
    log_warning "Database already exists"
else
    az cosmosdb sql database create \
        --account-name $COSMOS_ACCOUNT_NAME \
        --resource-group $RESOURCE_GROUP \
        --name $DATABASE_NAME \
        --output none
    log_success "Database created"
fi

# ============================================================================
# Step 6: Create Container
# ============================================================================

log_info "Creating container: $CONTAINER_NAME..."

if az cosmosdb sql container show \
    --account-name $COSMOS_ACCOUNT_NAME \
    --database-name $DATABASE_NAME \
    --resource-group $RESOURCE_GROUP \
    --name $CONTAINER_NAME &> /dev/null; then
    log_warning "Container already exists"
else
    az cosmosdb sql container create \
        --account-name $COSMOS_ACCOUNT_NAME \
        --database-name $DATABASE_NAME \
        --resource-group $RESOURCE_GROUP \
        --name $CONTAINER_NAME \
        --partition-key-path "/id" \
        --throughput 400 \
        --output none
    log_success "Container created"
fi

# ============================================================================
# Step 7: Get Cosmos DB Connection Information
# ============================================================================

log_info "Retrieving Cosmos DB connection information..."

COSMOS_ENDPOINT=$(az cosmosdb show \
    --name $COSMOS_ACCOUNT_NAME \
    --resource-group $RESOURCE_GROUP \
    --query documentEndpoint \
    -o tsv)

COSMOS_KEY=$(az cosmosdb keys list \
    --name $COSMOS_ACCOUNT_NAME \
    --resource-group $RESOURCE_GROUP \
    --query primaryMasterKey \
    -o tsv)

log_success "Cosmos DB endpoint: $COSMOS_ENDPOINT"
log_info "Connection string retrieved (not displayed for security)"

# ============================================================================
# Step 8: Create Azure Container Registry
# ============================================================================

log_info "Creating Azure Container Registry: $ACR_NAME..."

if az acr show --name $ACR_NAME --resource-group $RESOURCE_GROUP &> /dev/null; then
    log_warning "Container registry already exists"
else
    az acr create \
        --name $ACR_NAME \
        --resource-group $RESOURCE_GROUP \
        --sku Basic \
        --admin-enabled true \
        --output none
    log_success "Container registry created"
fi

# ============================================================================
# Step 9: Build and Push Docker Image
# ============================================================================

log_info "Building and pushing Docker image to ACR..."

az acr build \
    --registry $ACR_NAME \
    --image $IMAGE_NAME:$IMAGE_TAG \
    --file Dockerfile \
    . \
    --output none

log_success "Docker image built and pushed: $IMAGE_NAME:$IMAGE_TAG"

# ============================================================================
# Step 10: Create Container Apps Environment
# ============================================================================

log_info "Creating Container Apps environment: $CONTAINER_APP_ENV..."

if az containerapp env show \
    --name $CONTAINER_APP_ENV \
    --resource-group $RESOURCE_GROUP &> /dev/null; then
    log_warning "Container Apps environment already exists"
else
    az containerapp env create \
        --name $CONTAINER_APP_ENV \
        --resource-group $RESOURCE_GROUP \
        --location $LOCATION \
        --output none
    log_success "Container Apps environment created"
fi

# ============================================================================
# Step 11: Deploy Container App
# ============================================================================

log_info "Deploying Container App: $CONTAINER_APP_NAME..."

ACR_LOGIN_SERVER=$(az acr show --name $ACR_NAME --resource-group $RESOURCE_GROUP --query loginServer -o tsv)
ACR_USERNAME=$(az acr credential show --name $ACR_NAME --query username -o tsv)
ACR_PASSWORD=$(az acr credential show --name $ACR_NAME --query passwords[0].value -o tsv)

if az containerapp show \
    --name $CONTAINER_APP_NAME \
    --resource-group $RESOURCE_GROUP &> /dev/null; then
    log_warning "Container App already exists - updating..."
    
    az containerapp update \
        --name $CONTAINER_APP_NAME \
        --resource-group $RESOURCE_GROUP \
        --image "$ACR_LOGIN_SERVER/$IMAGE_NAME:$IMAGE_TAG" \
        --set-env-vars \
            COSMOS_ENDPOINT="$COSMOS_ENDPOINT" \
        --secrets \
            cosmos-key="$COSMOS_KEY" \
            acr-password="$ACR_PASSWORD" \
        --output none
    
    log_success "Container App updated"
else
    az containerapp create \
        --name $CONTAINER_APP_NAME \
        --resource-group $RESOURCE_GROUP \
        --environment $CONTAINER_APP_ENV \
        --image "$ACR_LOGIN_SERVER/$IMAGE_NAME:$IMAGE_TAG" \
        --registry-server "$ACR_LOGIN_SERVER" \
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
            COSMOS_KEY=secretref:cosmos-key \
        --output none
    
    log_success "Container App created"
fi

# ============================================================================
# Step 12: Get Container App URL
# ============================================================================

log_info "Retrieving Container App URL..."

APP_URL=$(az containerapp show \
    --name $CONTAINER_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --query properties.configuration.ingress.fqdn \
    -o tsv)

# ============================================================================
# Deployment Complete
# ============================================================================

echo ""
log_success "========================================="
log_success "Deployment Complete!"
log_success "========================================="
echo ""
log_info "Resource Group: $RESOURCE_GROUP"
log_info "Cosmos DB Account: $COSMOS_ACCOUNT_NAME"
log_info "Cosmos DB Endpoint: $COSMOS_ENDPOINT"
log_info "Container Registry: $ACR_NAME"
log_info "Container App: $CONTAINER_APP_NAME"
log_info "App URL: https://$APP_URL"
echo ""
log_info "Next steps:"
echo "  1. Test the deployment with:"
echo "     curl https://$APP_URL/health"
echo ""
echo "  2. Configure Claude Desktop to use the HTTP endpoint:"
echo "     {\"mcpServers\": {\"context-journal\": {\"url\": \"https://$APP_URL\"}}}"
echo ""
echo "  3. View logs:"
echo "     az containerapp logs show --name $CONTAINER_APP_NAME --resource-group $RESOURCE_GROUP --follow"
echo ""
log_warning "IMPORTANT: Your Cosmos DB key is stored as a secret. To rotate:"
echo "  az cosmosdb keys regenerate --name $COSMOS_ACCOUNT_NAME --resource-group $RESOURCE_GROUP --key-kind primary"
echo ""
