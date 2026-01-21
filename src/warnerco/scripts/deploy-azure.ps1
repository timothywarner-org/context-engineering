# WARNERCO Robotics Schematica - Azure Deployment Script (PowerShell)
# Usage: .\deploy-azure.ps1 [-ResourceGroup <name>] [-Location <location>] [-Environment <env>]

param(
    [string]$ResourceGroup = "warnerco-schematica-rg",
    [string]$Location = "eastus",
    [string]$Environment = "classroom"
)

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir
$InfraDir = Join-Path $ProjectRoot "infra\bicep"

Write-Host "========================================" -ForegroundColor Green
Write-Host "WARNERCO Robotics Schematica" -ForegroundColor Green
Write-Host "Azure Deployment" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green

# Check for Azure CLI
if (-not (Get-Command az -ErrorAction SilentlyContinue)) {
    Write-Host "Error: Azure CLI is not installed." -ForegroundColor Red
    Write-Host "Install from: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
    exit 1
}

# Check Azure login
Write-Host "Checking Azure login..." -ForegroundColor Yellow
try {
    $account = az account show | ConvertFrom-Json
    Write-Host "Logged in to: $($account.name)" -ForegroundColor Green
}
catch {
    Write-Host "Please log in to Azure..." -ForegroundColor Yellow
    az login
}

# Create resource group
Write-Host "Creating resource group: $ResourceGroup in $Location..." -ForegroundColor Yellow
az group create --name $ResourceGroup --location $Location --output none

# Deploy Bicep template
Write-Host "Deploying infrastructure..." -ForegroundColor Yellow
az deployment group create `
    --resource-group $ResourceGroup `
    --template-file "$InfraDir\main.bicep" `
    --parameters "$InfraDir\parameters.json" `
    --parameters environment=$Environment `
    --output table

# Get outputs
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Deployment Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green

$ContainerUrl = az deployment group show `
    --resource-group $ResourceGroup `
    --name main `
    --query properties.outputs.containerAppUrl.value `
    -o tsv 2>$null

$ApimUrl = az deployment group show `
    --resource-group $ResourceGroup `
    --name main `
    --query properties.outputs.apimGatewayUrl.value `
    -o tsv 2>$null

Write-Host "Container App URL: $ContainerUrl" -ForegroundColor Green
Write-Host "APIM Gateway URL: $ApimUrl" -ForegroundColor Green
Write-Host ""
Write-Host "To tear down resources, run:" -ForegroundColor Yellow
Write-Host ".\teardown-azure.ps1 -ResourceGroup $ResourceGroup" -ForegroundColor Yellow
