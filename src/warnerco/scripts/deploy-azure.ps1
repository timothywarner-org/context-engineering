<#
.SYNOPSIS
    Deploy WARNERCO Robotics Schematica to Azure: ACA + APIM (Entra-secured) + ACR,
    fully from the Bicep in infra/bicep. Reconstitutable end to end.

.DESCRIPTION
    Resolves the chicken/egg between "Bicep creates the ACR" and "the Container App
    needs an image already in that ACR" with a two-pass flow:

      Pass 1  Deploy the Bicep. ACR, APIM, identities, storage, Entra app, and the
              Container App are all created. The first Container App revision will
              fail to pull (the image does not exist yet) - that is expected.
      Build   az acr build pushes the image into the just-created registry (in-cloud,
              no local Docker required).
      Pass 2  Re-point the Container App at the now-present image and activate.

    Secrets (Anthropic, AI Search) come from Key Vault references in parameters.json -
    nothing sensitive is passed on the command line or stored in the template.

.PARAMETER ResourceGroup
    Target resource group. Created if absent.

.PARAMETER Location
    Azure region. Defaults to eastus.

.PARAMETER Environment
    classroom | dev | prod. Drives resource naming and DEBUG behaviour.

.PARAMETER TimUserObjectId
    Entra object ID for tim@techtrainertim.com (granted the Schematica.Access role).
    If omitted, the script resolves it via `az ad user show`.

.EXAMPLE
    .\deploy-azure.ps1 -ResourceGroup warnerco-rg -Location eastus

.NOTES
    APIM BasicV2 provisions in ~15-20 min on first deploy. Budget accordingly.
    Requires: Azure CLI, Bicep CLI >= 0.36 (az bicep upgrade), and the deploying
    identity must hold Application Administrator (Entra) + AppRoleAssignment.ReadWrite.All
    for the Microsoft.Graph resources in the template.
#>
param(
    [string]$ResourceGroup = "warnerco-schematica-rg",
    [string]$Location = "eastus",
    [ValidateSet("classroom", "dev", "prod")]
    [string]$Environment = "classroom",
    [string]$TimUserObjectId = ""
)

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir
$InfraDir = Join-Path $ProjectRoot "infra\bicep"
$BackendDir = Join-Path $ProjectRoot "backend"

Write-Host "========================================" -ForegroundColor Green
Write-Host "WARNERCO Robotics Schematica - Azure Deployment" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green

# --- Pre-flight -------------------------------------------------------------
if (-not (Get-Command az -ErrorAction SilentlyContinue)) {
    Write-Host "Error: Azure CLI is not installed." -ForegroundColor Red
    exit 1
}

Write-Host "Checking Azure login..." -ForegroundColor Yellow
try { $account = az account show | ConvertFrom-Json } catch { az login; $account = az account show | ConvertFrom-Json }
Write-Host "Logged in to: $($account.name)" -ForegroundColor Green

# Ensure Bicep CLI is new enough for the Microsoft.Graph extension.
az bicep upgrade --only-show-errors 2>$null

# Resolve Tim's Entra object ID if not supplied. This is the one identity input
# the template needs; keeping it as a value (not a UPN lookup inside Bicep) avoids
# requiring User.Read.All on the deploying principal.
if ([string]::IsNullOrWhiteSpace($TimUserObjectId)) {
    Write-Host "Resolving object ID for tim@techtrainertim.com..." -ForegroundColor Yellow
    $TimUserObjectId = az ad user show --id "tim@techtrainertim.com" --query id -o tsv
    if ([string]::IsNullOrWhiteSpace($TimUserObjectId)) {
        Write-Host "Could not resolve tim@techtrainertim.com. Pass -TimUserObjectId explicitly." -ForegroundColor Red
        exit 1
    }
}
Write-Host "Tim object ID: $TimUserObjectId" -ForegroundColor Green

# --- Resource group ---------------------------------------------------------
Write-Host "Creating resource group: $ResourceGroup in $Location..." -ForegroundColor Yellow
az group create --name $ResourceGroup --location $Location --output none

# --- Pass 1: deploy infrastructure -----------------------------------------
# Container App will report an image-pull failure on its first revision because
# the image is not in ACR yet. Expected; corrected after the build below.
Write-Host "Pass 1/2: deploying infrastructure (APIM BasicV2 ~15-20 min)..." -ForegroundColor Yellow
az deployment group create `
    --resource-group $ResourceGroup `
    --template-file "$InfraDir\main.bicep" `
    --parameters "$InfraDir\parameters.json" `
    --parameters environment=$Environment timUserObjectId=$TimUserObjectId `
    --name "warnerco-main" `
    --output table

# --- Read outputs -----------------------------------------------------------
function Get-Output($name) {
    az deployment group show --resource-group $ResourceGroup --name "warnerco-main" `
        --query "properties.outputs.$name.value" -o tsv 2>$null
}
$AcrLoginServer = Get-Output "acrLoginServer"
$ContainerUrl   = Get-Output "containerAppUrl"
$ApimUrl        = Get-Output "apimGatewayUrl"
$EntraAppId     = Get-Output "entraAppId"
$AiSearchHost   = Get-Output "aiSearchEndpoint"

# --- Build + push image into the just-created ACR ---------------------------
$AcrName = ($AcrLoginServer -split '\.')[0]
Write-Host "Building image in ACR $AcrName (in-cloud, no local Docker)..." -ForegroundColor Yellow
az acr build --registry $AcrName --image "warnerco-schematica:latest" $BackendDir --output table

# --- Seed Azure AI Search ---------------------------------------------------
# The reason node and semantic tier read the index at app startup, so seed before
# first request. Endpoint+key are picked up from the backend .env / environment.
if (-not [string]::IsNullOrWhiteSpace($AiSearchHost)) {
    Write-Host "Indexing schematics into Azure AI Search..." -ForegroundColor Yellow
    Push-Location $BackendDir
    try { uv run python scripts/index_azure_search.py }
    catch { Write-Host "AI Search indexing skipped/failed: $_" -ForegroundColor Yellow }
    Pop-Location
}

# --- Pass 2: point the Container App at the now-present image ----------------
Write-Host "Pass 2/2: activating Container App with the built image..." -ForegroundColor Yellow
az containerapp update `
    --name "warnerco-schematica-$Environment" `
    --resource-group $ResourceGroup `
    --image "$AcrLoginServer/warnerco-schematica:latest" `
    --output none

# --- Summary ----------------------------------------------------------------
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Deployment Complete" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host "Container App (direct):  $ContainerUrl" -ForegroundColor Green
Write-Host "APIM Gateway (public):   $ApimUrl" -ForegroundColor Green
Write-Host "  - REST:  $ApimUrl/api/health   (401 without a token)" -ForegroundColor Green
Write-Host "  - MCP:   $ApimUrl/mcp/          (Bearer Entra JWT, role Schematica.Access)" -ForegroundColor Green
Write-Host "Entra app (client) ID:   $EntraAppId" -ForegroundColor Green
Write-Host ""
Write-Host "Next: get a token and verify -" -ForegroundColor Yellow
Write-Host "  az account get-access-token --resource api://$EntraAppId --query accessToken -o tsv" -ForegroundColor Yellow
Write-Host "To tear down: .\teardown-azure.ps1 -ResourceGroup $ResourceGroup" -ForegroundColor Yellow
