# WARNERCO Robotics Schematica - Azure Teardown Script (PowerShell)
# Usage: .\teardown-azure.ps1 [-ResourceGroup <name>]
# WARNING: This will delete all resources in the resource group!

param(
    [string]$ResourceGroup = "warnerco-schematica-rg"
)

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Red
Write-Host "WARNERCO Robotics Schematica" -ForegroundColor Red
Write-Host "Azure Resource Teardown" -ForegroundColor Red
Write-Host "========================================" -ForegroundColor Red

# Check for Azure CLI
if (-not (Get-Command az -ErrorAction SilentlyContinue)) {
    Write-Host "Error: Azure CLI is not installed." -ForegroundColor Red
    exit 1
}

# Confirm deletion
Write-Host "WARNING: This will permanently delete all resources in:" -ForegroundColor Yellow
Write-Host "Resource Group: $ResourceGroup" -ForegroundColor Yellow
Write-Host ""

$Confirm = Read-Host "Are you sure you want to continue? (yes/no)"
if ($Confirm -ne "yes") {
    Write-Host "Teardown cancelled." -ForegroundColor Green
    exit 0
}

# Delete resource group
Write-Host "Deleting resource group: $ResourceGroup..." -ForegroundColor Yellow
az group delete --name $ResourceGroup --yes --no-wait

Write-Host "Resource group deletion initiated." -ForegroundColor Green
Write-Host "This may take several minutes to complete." -ForegroundColor Green
Write-Host ""
Write-Host "To check status:" -ForegroundColor Yellow
Write-Host "az group show --name $ResourceGroup --query provisioningState" -ForegroundColor Yellow
