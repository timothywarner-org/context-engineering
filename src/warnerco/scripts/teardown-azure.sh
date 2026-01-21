#!/bin/bash
# WARNERCO Robotics Schematica - Azure Teardown Script
# Usage: ./teardown-azure.sh [resource-group]
# WARNING: This will delete all resources in the resource group!

set -e

RESOURCE_GROUP="${1:-warnerco-schematica-rg}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${RED}========================================${NC}"
echo -e "${RED}WARNERCO Robotics Schematica${NC}"
echo -e "${RED}Azure Resource Teardown${NC}"
echo -e "${RED}========================================${NC}"

# Check for Azure CLI
if ! command -v az &> /dev/null; then
    echo -e "${RED}Error: Azure CLI is not installed.${NC}"
    exit 1
fi

# Confirm deletion
echo -e "${YELLOW}WARNING: This will permanently delete all resources in:${NC}"
echo -e "${YELLOW}Resource Group: $RESOURCE_GROUP${NC}"
echo ""
read -p "Are you sure you want to continue? (yes/no): " CONFIRM

if [[ "$CONFIRM" != "yes" ]]; then
    echo -e "${GREEN}Teardown cancelled.${NC}"
    exit 0
fi

# Delete resource group
echo -e "${YELLOW}Deleting resource group: $RESOURCE_GROUP...${NC}"
az group delete --name "$RESOURCE_GROUP" --yes --no-wait

echo -e "${GREEN}Resource group deletion initiated.${NC}"
echo -e "${GREEN}This may take several minutes to complete.${NC}"
echo ""
echo -e "${YELLOW}To check status:${NC}"
echo -e "${YELLOW}az group show --name $RESOURCE_GROUP --query provisioningState${NC}"
