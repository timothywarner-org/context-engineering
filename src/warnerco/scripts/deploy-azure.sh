#!/bin/bash
# WARNERCO Robotics Schematica - Azure Deployment (ACA + APIM + ACR, Entra-secured)
#
# Two-pass flow resolves the "Bicep creates the ACR but the Container App needs an
# image already in it" chicken/egg:
#   Pass 1  deploy Bicep (ACR/APIM/identities/Entra app/Container App). First
#           Container App revision fails to pull - expected, no image yet.
#   Build   az acr build pushes the image in-cloud (no local Docker).
#   Pass 2  re-point the Container App at the now-present image.
#
# Secrets come from Key Vault references in parameters.json. APIM BasicV2 takes
# ~15-20 min on first deploy. Requires Bicep CLI >= 0.36 and, for the
# Microsoft.Graph resources, Application Administrator + AppRoleAssignment.ReadWrite.All
# on the deploying identity.
#
# Usage: ./deploy-azure.sh [resource-group] [location] [environment] [tim-object-id]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
INFRA_DIR="$PROJECT_ROOT/infra/bicep"
BACKEND_DIR="$PROJECT_ROOT/backend"

RESOURCE_GROUP="${1:-warnerco-schematica-rg}"
LOCATION="${2:-eastus}"
ENVIRONMENT="${3:-classroom}"
TIM_OBJECT_ID="${4:-}"

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'

echo -e "${GREEN}WARNERCO Robotics Schematica - Azure Deployment${NC}"

command -v az >/dev/null 2>&1 || { echo -e "${RED}Azure CLI not installed.${NC}"; exit 1; }

echo -e "${YELLOW}Checking Azure login...${NC}"
az account show >/dev/null 2>&1 || az login >/dev/null
echo -e "${GREEN}Logged in to: $(az account show --query name -o tsv)${NC}"

# Microsoft.Graph extension needs a recent Bicep CLI.
az bicep upgrade --only-show-errors 2>/dev/null || true

# Resolve Tim's Entra object ID if not supplied.
if [ -z "$TIM_OBJECT_ID" ]; then
    echo -e "${YELLOW}Resolving object ID for tim@techtrainertim.com...${NC}"
    TIM_OBJECT_ID="$(az ad user show --id 'tim@techtrainertim.com' --query id -o tsv || true)"
    [ -z "$TIM_OBJECT_ID" ] && { echo -e "${RED}Could not resolve tim; pass the object ID as arg 4.${NC}"; exit 1; }
fi
echo -e "${GREEN}Tim object ID: $TIM_OBJECT_ID${NC}"

echo -e "${YELLOW}Creating resource group: $RESOURCE_GROUP in $LOCATION...${NC}"
az group create --name "$RESOURCE_GROUP" --location "$LOCATION" --output none

# --- Pass 1: deploy infrastructure -----------------------------------------
echo -e "${YELLOW}Pass 1/2: deploying infrastructure (APIM BasicV2 ~15-20 min)...${NC}"
az deployment group create \
    --resource-group "$RESOURCE_GROUP" \
    --template-file "$INFRA_DIR/main.bicep" \
    --parameters "$INFRA_DIR/parameters.json" \
    --parameters environment="$ENVIRONMENT" timUserObjectId="$TIM_OBJECT_ID" \
    --name "warnerco-main" \
    --output table

get_output() {
    az deployment group show --resource-group "$RESOURCE_GROUP" --name "warnerco-main" \
        --query "properties.outputs.$1.value" -o tsv 2>/dev/null || echo ""
}
ACR_LOGIN_SERVER="$(get_output acrLoginServer)"
CONTAINER_URL="$(get_output containerAppUrl)"
APIM_URL="$(get_output apimGatewayUrl)"
ENTRA_APP_ID="$(get_output entraAppId)"
AI_SEARCH_HOST="$(get_output aiSearchEndpoint)"

# --- Build + push image into the just-created ACR ---------------------------
ACR_NAME="${ACR_LOGIN_SERVER%%.*}"
echo -e "${YELLOW}Building image in ACR $ACR_NAME (in-cloud)...${NC}"
az acr build --registry "$ACR_NAME" --image "warnerco-schematica:latest" "$BACKEND_DIR" --output table

# --- Seed Azure AI Search ---------------------------------------------------
if [ -n "$AI_SEARCH_HOST" ]; then
    echo -e "${YELLOW}Indexing schematics into Azure AI Search...${NC}"
    ( cd "$BACKEND_DIR" && uv run python scripts/index_azure_search.py ) || \
        echo -e "${YELLOW}AI Search indexing skipped/failed.${NC}"
fi

# --- Pass 2: point the Container App at the built image ---------------------
echo -e "${YELLOW}Pass 2/2: activating Container App with the built image...${NC}"
az containerapp update \
    --name "warnerco-schematica-$ENVIRONMENT" \
    --resource-group "$RESOURCE_GROUP" \
    --image "$ACR_LOGIN_SERVER/warnerco-schematica:latest" \
    --output none

# --- Summary ----------------------------------------------------------------
echo ""
echo -e "${GREEN}Deployment Complete${NC}"
echo -e "${GREEN}Container App (direct):  $CONTAINER_URL${NC}"
echo -e "${GREEN}APIM Gateway (public):   $APIM_URL${NC}"
echo -e "${GREEN}  - REST:  $APIM_URL/api/health   (401 without a token)${NC}"
echo -e "${GREEN}  - MCP:   $APIM_URL/mcp/          (Bearer Entra JWT, role Schematica.Access)${NC}"
echo -e "${GREEN}Entra app (client) ID:   $ENTRA_APP_ID${NC}"
echo ""
echo -e "${YELLOW}Verify a token:${NC} az account get-access-token --resource api://$ENTRA_APP_ID --query accessToken -o tsv"
echo -e "${YELLOW}Tear down:${NC} ./teardown-azure.sh $RESOURCE_GROUP"
