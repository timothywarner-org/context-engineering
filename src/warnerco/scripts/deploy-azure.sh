#!/bin/bash
# WARNERCO Robotics Schematica - Azure Deployment Script
# Usage: ./deploy-azure.sh [resource-group] [location]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
INFRA_DIR="$PROJECT_ROOT/infra/bicep"

# Default values
RESOURCE_GROUP="${1:-warnerco-schematica-rg}"
LOCATION="${2:-eastus}"
ENVIRONMENT="${3:-classroom}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}WARNERCO Robotics Schematica${NC}"
echo -e "${GREEN}Azure Deployment${NC}"
echo -e "${GREEN}========================================${NC}"

# Check for Azure CLI
if ! command -v az &> /dev/null; then
    echo -e "${RED}Error: Azure CLI is not installed.${NC}"
    echo "Install from: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
    exit 1
fi

# Check Azure login
echo -e "${YELLOW}Checking Azure login...${NC}"
az account show &> /dev/null || {
    echo -e "${YELLOW}Please log in to Azure...${NC}"
    az login
}

ACCOUNT_NAME=$(az account show --query name -o tsv)
echo -e "${GREEN}Logged in to: $ACCOUNT_NAME${NC}"

# Create resource group
echo -e "${YELLOW}Creating resource group: $RESOURCE_GROUP in $LOCATION...${NC}"
az group create --name "$RESOURCE_GROUP" --location "$LOCATION" --output none

# Deploy Bicep template
echo -e "${YELLOW}Deploying infrastructure...${NC}"
az deployment group create \
    --resource-group "$RESOURCE_GROUP" \
    --template-file "$INFRA_DIR/main.bicep" \
    --parameters "$INFRA_DIR/parameters.json" \
    --parameters environment="$ENVIRONMENT" \
    --output table

# Get outputs
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Deployment Complete!${NC}"
echo -e "${GREEN}========================================${NC}"

CONTAINER_URL=$(az deployment group show \
    --resource-group "$RESOURCE_GROUP" \
    --name main \
    --query properties.outputs.containerAppUrl.value -o tsv 2>/dev/null || echo "")

APIM_URL=$(az deployment group show \
    --resource-group "$RESOURCE_GROUP" \
    --name main \
    --query properties.outputs.apimGatewayUrl.value -o tsv 2>/dev/null || echo "")

echo -e "${GREEN}Container App URL: $CONTAINER_URL${NC}"
echo -e "${GREEN}APIM Gateway URL: $APIM_URL${NC}"
echo ""
echo -e "${YELLOW}To tear down resources, run:${NC}"
echo -e "${YELLOW}./teardown-azure.sh $RESOURCE_GROUP${NC}"
