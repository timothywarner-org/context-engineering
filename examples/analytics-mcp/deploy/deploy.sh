#!/bin/bash

# Azure deployment script for Analytics MCP Server
# Builds Docker image, pushes to ACR, and deploys to Container Apps

set -e

# Configuration
RESOURCE_GROUP="${RESOURCE_GROUP:-analytics-mcp-rg}"
LOCATION="${LOCATION:-eastus}"
ENVIRONMENT="${ENVIRONMENT:-dev}"
ACR_NAME="${ACR_NAME:-analyticsmcpacr$(openssl rand -hex 4)}"
IMAGE_NAME="analytics-mcp"
IMAGE_TAG="${IMAGE_TAG:-$(git rev-parse --short HEAD 2>/dev/null || echo 'latest')}"
API_KEY="${API_KEY:-$(openssl rand -base64 32)}"

echo "======================================================================"
echo "🚀 Analytics MCP Server - Azure Deployment"
echo "======================================================================"
echo ""
echo "Configuration:"
echo "  Resource Group:  $RESOURCE_GROUP"
echo "  Location:        $LOCATION"
echo "  Environment:     $ENVIRONMENT"
echo "  ACR Name:        $ACR_NAME"
echo "  Image Tag:       $IMAGE_TAG"
echo "  API Key:         ${API_KEY:0:10}... (hidden)"
echo ""
echo "======================================================================"
echo ""

# Check prerequisites
echo "📋 Checking prerequisites..."

if ! command -v az &> /dev/null; then
    echo "❌ Azure CLI not found. Install from https://aka.ms/az-cli"
    exit 1
fi

if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Install from https://docker.com"
    exit 1
fi

echo "✅ Prerequisites satisfied"
echo ""

# Login check
echo "🔐 Checking Azure login status..."
if ! az account show &> /dev/null; then
    echo "⚠️  Not logged in to Azure. Running 'az login'..."
    az login
fi

SUBSCRIPTION_ID=$(az account show --query id -o tsv)
echo "✅ Logged in to Azure (Subscription: $SUBSCRIPTION_ID)"
echo ""

# Create resource group
echo "📦 Creating resource group..."
az group create \
    --name "$RESOURCE_GROUP" \
    --location "$LOCATION" \
    --output none

echo "✅ Resource group created: $RESOURCE_GROUP"
echo ""

# Create container registry
echo "🏗️  Creating Azure Container Registry..."
az acr create \
    --resource-group "$RESOURCE_GROUP" \
    --name "$ACR_NAME" \
    --sku Basic \
    --admin-enabled true \
    --output none

echo "✅ Container Registry created: $ACR_NAME"
echo ""

# Build and push Docker image
echo "🐳 Building Docker image..."
cd "$(dirname "$0")/.."

docker build -t "${ACR_NAME}.azurecr.io/${IMAGE_NAME}:${IMAGE_TAG}" .

echo "✅ Docker image built"
echo ""

echo "⬆️  Pushing image to ACR..."
az acr login --name "$ACR_NAME"

docker push "${ACR_NAME}.azurecr.io/${IMAGE_NAME}:${IMAGE_TAG}"

echo "✅ Image pushed to ACR"
echo ""

# Deploy using Bicep
echo "🚢 Deploying to Azure Container Apps..."

az deployment group create \
    --resource-group "$RESOURCE_GROUP" \
    --template-file deploy/main.bicep \
    --parameters \
        environmentName="$ENVIRONMENT" \
        apiKey="$API_KEY" \
        imageTag="$IMAGE_TAG" \
        containerRegistryName="$ACR_NAME" \
    --output none

echo "✅ Deployment complete"
echo ""

# Assign ACR pull role to container app
echo "🔑 Configuring ACR access..."

CONTAINER_APP_NAME="analytics-mcp-${ENVIRONMENT}-app"
PRINCIPAL_ID=$(az containerapp show \
    --resource-group "$RESOURCE_GROUP" \
    --name "$CONTAINER_APP_NAME" \
    --query identity.principalId -o tsv)

ACR_ID=$(az acr show \
    --resource-group "$RESOURCE_GROUP" \
    --name "$ACR_NAME" \
    --query id -o tsv)

az role assignment create \
    --assignee "$PRINCIPAL_ID" \
    --role AcrPull \
    --scope "$ACR_ID" \
    --output none

echo "✅ ACR access configured"
echo ""

# Get deployment info
APP_URL=$(az deployment group show \
    --resource-group "$RESOURCE_GROUP" \
    --name main \
    --query properties.outputs.containerAppUrl.value -o tsv)

echo "======================================================================"
echo "✅ DEPLOYMENT SUCCESSFUL"
echo "======================================================================"
echo ""
echo "📍 Service URL:     $APP_URL"
echo "🔑 API Key:         $API_KEY"
echo ""
echo "Next steps:"
echo "  1. Test health endpoint:"
echo "     curl $APP_URL/health"
echo ""
echo "  2. Test with MCP client:"
echo "     Add to your MCP client config:"
echo ""
echo "     {"
echo "       \"analytics\": {"
echo "         \"url\": \"$APP_URL/sse\","
echo "         \"apiKey\": \"$API_KEY\""
echo "       }"
echo "     }"
echo ""
echo "  3. View logs:"
echo "     az containerapp logs show \\"
echo "       --resource-group $RESOURCE_GROUP \\"
echo "       --name $CONTAINER_APP_NAME \\"
echo "       --follow"
echo ""
echo "======================================================================"
