#!/bin/bash
# ============================================================
# CoreText MCP - Azure Deployment Script
# ============================================================
# This script deploys the CoreText MCP server to Azure
# Requirements:
#   - Azure CLI installed (az --version)
#   - Docker installed (docker --version)
#   - Logged into Azure (az login)
#   - Logged into ACR (az acr login)
# ============================================================

set -e  # Exit on error
set -u  # Exit on undefined variable

# ============================================================
# Configuration (from azure-details.md)
# ============================================================

SUBSCRIPTION_ID="${SUBSCRIPTION_ID:-92fd53f2-c38e-461a-9f50-e1ef3382c54c}"
RESOURCE_GROUP="${RESOURCE_GROUP:-context-engineering-rg}"
LOCATION="${LOCATION:-eastus}"
MANAGED_IDENTITY="${MANAGED_IDENTITY:-context-msi}"

# Deployment-specific
DEPLOYMENT_NAME="coretext-mcp-$(date +%Y%m%d-%H%M%S)"
ACR_NAME=""  # Will be set or created
IMAGE_NAME="coretext-mcp"
IMAGE_TAG="${IMAGE_TAG:-latest}"

# ============================================================
# Colors for output
# ============================================================

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ============================================================
# Helper Functions
# ============================================================

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

# ============================================================
# Pre-flight Checks
# ============================================================

log_info "Starting CoreText MCP Azure Deployment"
echo ""

# Check Azure CLI
if ! command -v az &> /dev/null; then
    log_error "Azure CLI not found. Install from: https://aka.ms/azure-cli"
    exit 1
fi
log_success "Azure CLI found: $(az version --query '"azure-cli"' -o tsv)"

# Check Docker
if ! command -v docker &> /dev/null; then
    log_error "Docker not found. Install from: https://docs.docker.com/get-docker/"
    exit 1
fi
log_success "Docker found: $(docker --version | cut -d' ' -f3 | tr -d ',')"

# Check Azure login
if ! az account show &> /dev/null; then
    log_error "Not logged into Azure. Run: az login"
    exit 1
fi
log_success "Logged into Azure"

# Set subscription
log_info "Setting subscription to: $SUBSCRIPTION_ID"
az account set --subscription "$SUBSCRIPTION_ID"
log_success "Subscription set"

echo ""

# ============================================================
# Step 1: Verify Resource Group and Managed Identity
# ============================================================

log_info "Verifying resource group: $RESOURCE_GROUP"
if az group show --name "$RESOURCE_GROUP" &> /dev/null; then
    log_success "Resource group exists"
else
    log_error "Resource group '$RESOURCE_GROUP' not found"
    log_info "Create it with: az group create --name $RESOURCE_GROUP --location $LOCATION"
    exit 1
fi

log_info "Verifying managed identity: $MANAGED_IDENTITY"
if az identity show --name "$MANAGED_IDENTITY" --resource-group "$RESOURCE_GROUP" &> /dev/null; then
    log_success "Managed identity exists"
else
    log_error "Managed identity '$MANAGED_IDENTITY' not found"
    log_info "Create it with: az identity create --name $MANAGED_IDENTITY --resource-group $RESOURCE_GROUP"
    exit 1
fi

echo ""

# ============================================================
# Step 2: Create or Select Azure Container Registry
# ============================================================

log_info "Checking for existing Azure Container Registry..."

# Look for existing ACR in resource group
EXISTING_ACR=$(az acr list --resource-group "$RESOURCE_GROUP" --query "[0].name" -o tsv 2>/dev/null || echo "")

if [ -n "$EXISTING_ACR" ]; then
    ACR_NAME="$EXISTING_ACR"
    log_success "Found existing ACR: $ACR_NAME"
else
    # Generate unique ACR name (no hyphens, lowercase only)
    ACR_NAME="coretextacr$(date +%s | tail -c 6)"

    log_info "Creating new Azure Container Registry: $ACR_NAME"
    az acr create \
        --resource-group "$RESOURCE_GROUP" \
        --name "$ACR_NAME" \
        --sku Basic \
        --location "$LOCATION" \
        --admin-enabled false

    log_success "ACR created: $ACR_NAME"
fi

# Login to ACR
log_info "Logging into ACR: $ACR_NAME"
az acr login --name "$ACR_NAME"
log_success "Logged into ACR"

echo ""

# ============================================================
# Step 3: Build and Push Docker Image
# ============================================================

FULL_IMAGE_NAME="${ACR_NAME}.azurecr.io/${IMAGE_NAME}:${IMAGE_TAG}"

log_info "Building Docker image: $FULL_IMAGE_NAME"
log_info "This may take a few minutes..."

# Change to coretext-mcp directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."

# Build image
docker build -t "$FULL_IMAGE_NAME" .
log_success "Docker image built successfully"

log_info "Pushing image to ACR: $FULL_IMAGE_NAME"
docker push "$FULL_IMAGE_NAME"
log_success "Image pushed to ACR"

echo ""

# ============================================================
# Step 4: Prompt for DeepSeek API Key
# ============================================================

log_info "DeepSeek API Key Configuration"
echo ""

if [ -f "../.env" ]; then
    # Try to read from root .env
    DEEPSEEK_KEY=$(grep "^DEEPSEEK_API_KEY=" ../.env | cut -d'=' -f2 | tr -d ' "' || echo "")
    if [ -n "$DEEPSEEK_KEY" ]; then
        log_info "Found DeepSeek API key in ../.env"
        read -p "Use this key? (y/n): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            DEEPSEEK_KEY=""
        fi
    fi
fi

if [ -z "$DEEPSEEK_KEY" ]; then
    log_warning "DeepSeek API key not found in .env"
    read -p "Enter your DeepSeek API key (or press Enter to skip): " DEEPSEEK_KEY
fi

if [ -z "$DEEPSEEK_KEY" ]; then
    log_warning "No API key provided. Server will use fallback enrichment mode."
    DEEPSEEK_KEY="not-configured"
fi

echo ""

# ============================================================
# Step 5: Deploy Infrastructure with Bicep
# ============================================================

log_info "Deploying Azure infrastructure with Bicep"
log_info "Deployment name: $DEPLOYMENT_NAME"
log_info "This will create:"
log_info "  - Cosmos DB (Free Tier)"
log_info "  - Container App (Consumption)"
log_info "  - Key Vault"
log_info "  - Log Analytics Workspace"
echo ""

cd "$SCRIPT_DIR"

az deployment group create \
    --name "$DEPLOYMENT_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --template-file main.bicep \
    --parameters \
        location="$LOCATION" \
        managedIdentityName="$MANAGED_IDENTITY" \
        containerImage="$FULL_IMAGE_NAME" \
        deepseekApiKey="$DEEPSEEK_KEY"

log_success "Infrastructure deployed successfully!"

echo ""

# ============================================================
# Step 6: Get Deployment Outputs
# ============================================================

log_info "Retrieving deployment outputs..."

CONTAINER_APP_URL=$(az deployment group show \
    --name "$DEPLOYMENT_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --query properties.outputs.containerAppUrl.value \
    -o tsv)

COSMOS_ACCOUNT=$(az deployment group show \
    --name "$DEPLOYMENT_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --query properties.outputs.cosmosAccountName.value \
    -o tsv)

KEY_VAULT=$(az deployment group show \
    --name "$DEPLOYMENT_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --query properties.outputs.keyVaultName.value \
    -o tsv)

echo ""
log_success "==================================================="
log_success "CoreText MCP Deployment Complete!"
log_success "==================================================="
echo ""
log_info "Container App URL: $CONTAINER_APP_URL"
log_info "Cosmos DB Account: $COSMOS_ACCOUNT"
log_info "Key Vault: $KEY_VAULT"
echo ""
log_info "Health Check: ${CONTAINER_APP_URL}/health"
echo ""
log_success "==================================================="
echo ""

# ============================================================
# Step 7: Post-Deployment Instructions
# ============================================================

log_info "Next Steps:"
echo ""
echo "1. Test the deployment:"
echo "   curl ${CONTAINER_APP_URL}/health"
echo ""
echo "2. View logs:"
echo "   az containerapp logs show -n \$(az containerapp list -g $RESOURCE_GROUP --query '[0].name' -o tsv) -g $RESOURCE_GROUP --follow"
echo ""
echo "3. View Cosmos DB data:"
echo "   az cosmosdb sql database show -g $RESOURCE_GROUP -a $COSMOS_ACCOUNT -n coretext"
echo ""
echo "4. Update the image:"
echo "   docker build -t $FULL_IMAGE_NAME ."
echo "   docker push $FULL_IMAGE_NAME"
echo "   az containerapp update -n \$(az containerapp list -g $RESOURCE_GROUP --query '[0].name' -o tsv) -g $RESOURCE_GROUP --image $FULL_IMAGE_NAME"
echo ""
log_success "Deployment script completed successfully!"
