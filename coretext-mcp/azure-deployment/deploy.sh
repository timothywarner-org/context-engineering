#!/bin/bash
# CoreText MCP - Azure Container Apps Deployment Script
# Simple, no-frills deployment for teaching/demo purposes

set -e  # Exit on any error

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}CoreText MCP - Azure Deployment${NC}"
echo -e "${BLUE}========================================${NC}"

# Azure Configuration (from azure-details.md)
SUBSCRIPTION_ID="92fd53f2-c38e-461a-9f50-e1ef3382c54c"
RESOURCE_GROUP="context-engineering-rg"
LOCATION="eastus"
MANAGED_IDENTITY="context-msi"

# Container Apps Configuration
CONTAINER_APP_ENV="coretext-env"
CONTAINER_APP_NAME="coretext-mcp"
CONTAINER_REGISTRY="coretextmcr"
IMAGE_NAME="coretext-mcp"
IMAGE_TAG="latest"

# MCP Configuration
DEEPSEEK_API_KEY="${DEEPSEEK_API_KEY:-}"

echo -e "\n${YELLOW}Step 1: Login and set subscription${NC}"
az account set --subscription $SUBSCRIPTION_ID
echo -e "${GREEN}✓ Subscription set${NC}"

echo -e "\n${YELLOW}Step 2: Create Azure Container Registry (if not exists)${NC}"
if ! az acr show --name $CONTAINER_REGISTRY --resource-group $RESOURCE_GROUP &> /dev/null; then
    echo "Creating ACR..."
    az acr create \
        --resource-group $RESOURCE_GROUP \
        --name $CONTAINER_REGISTRY \
        --sku Basic \
        --admin-enabled true
    echo -e "${GREEN}✓ ACR created${NC}"
else
    echo -e "${GREEN}✓ ACR already exists${NC}"
fi

echo -e "\n${YELLOW}Step 3: Build and push Docker image${NC}"
cd "$(dirname "$0")/.."  # Go to coretext-mcp root
az acr build \
    --registry $CONTAINER_REGISTRY \
    --image $IMAGE_NAME:$IMAGE_TAG \
    --file azure-deployment/Dockerfile \
    .
echo -e "${GREEN}✓ Image built and pushed${NC}"

echo -e "\n${YELLOW}Step 4: Get ACR credentials${NC}"
ACR_USERNAME=$(az acr credential show --name $CONTAINER_REGISTRY --query username -o tsv)
ACR_PASSWORD=$(az acr credential show --name $CONTAINER_REGISTRY --query passwords[0].value -o tsv)
ACR_LOGIN_SERVER=$(az acr show --name $CONTAINER_REGISTRY --query loginServer -o tsv)
echo -e "${GREEN}✓ Credentials retrieved${NC}"

echo -e "\n${YELLOW}Step 5: Create Container Apps Environment (if not exists)${NC}"
if ! az containerapp env show --name $CONTAINER_APP_ENV --resource-group $RESOURCE_GROUP &> /dev/null; then
    echo "Creating Container Apps Environment..."
    az containerapp env create \
        --name $CONTAINER_APP_ENV \
        --resource-group $RESOURCE_GROUP \
        --location $LOCATION
    echo -e "${GREEN}✓ Environment created${NC}"
else
    echo -e "${GREEN}✓ Environment already exists${NC}"
fi

echo -e "\n${YELLOW}Step 6: Deploy Container App${NC}"

# Build environment variables
ENV_VARS="NODE_ENV=production"
if [ -n "$DEEPSEEK_API_KEY" ]; then
    ENV_VARS="$ENV_VARS DEEPSEEK_API_KEY=$DEEPSEEK_API_KEY"
    echo -e "${GREEN}✓ Deepseek API key configured${NC}"
else
    echo -e "${YELLOW}⚠ No DEEPSEEK_API_KEY set - using fallback mode${NC}"
fi

# Deploy or update container app
if az containerapp show --name $CONTAINER_APP_NAME --resource-group $RESOURCE_GROUP &> /dev/null; then
    echo "Updating existing container app..."
    az containerapp update \
        --name $CONTAINER_APP_NAME \
        --resource-group $RESOURCE_GROUP \
        --image "$ACR_LOGIN_SERVER/$IMAGE_NAME:$IMAGE_TAG" \
        --set-env-vars $ENV_VARS
    echo -e "${GREEN}✓ Container app updated${NC}"
else
    echo "Creating new container app..."
    az containerapp create \
        --name $CONTAINER_APP_NAME \
        --resource-group $RESOURCE_GROUP \
        --environment $CONTAINER_APP_ENV \
        --image "$ACR_LOGIN_SERVER/$IMAGE_NAME:$IMAGE_TAG" \
        --registry-server $ACR_LOGIN_SERVER \
        --registry-username $ACR_USERNAME \
        --registry-password $ACR_PASSWORD \
        --target-port 3001 \
        --ingress external \
        --min-replicas 1 \
        --max-replicas 3 \
        --cpu 0.5 \
        --memory 1.0Gi \
        --env-vars $ENV_VARS
    echo -e "${GREEN}✓ Container app created${NC}"
fi

echo -e "\n${YELLOW}Step 7: Get application URL${NC}"
APP_URL=$(az containerapp show \
    --name $CONTAINER_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --query properties.configuration.ingress.fqdn -o tsv)

echo -e "\n${BLUE}========================================${NC}"
echo -e "${GREEN}Deployment Complete!${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "\n${GREEN}Application URL:${NC}"
echo -e "  https://$APP_URL"
echo -e "\n${GREEN}Health Endpoint:${NC}"
echo -e "  https://$APP_URL/health"
echo -e "\n${YELLOW}Next Steps:${NC}"
echo -e "  1. Test health endpoint: curl https://$APP_URL/health"
echo -e "  2. Check logs: az containerapp logs show -n $CONTAINER_APP_NAME -g $RESOURCE_GROUP --follow"
echo -e "  3. Configure Claude Desktop to use: https://$APP_URL"
echo -e "${BLUE}========================================${NC}\n"
