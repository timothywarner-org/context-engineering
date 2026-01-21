# WARNERCO Robotics Schematica - APIM Configuration Script
# Configures API Management to proxy to Container App

param(
    [string]$ResourceGroup = "warnerco",
    [string]$ApimName = "warnerco-apim",
    [string]$ContainerAppFqdn = "warnerco-schematica-classroom.wonderfulground-26566597.eastus2.azurecontainerapps.io"
)

$ErrorActionPreference = "Stop"

Write-Host "Configuring APIM: $ApimName" -ForegroundColor Cyan

# Wait for APIM to be ready
Write-Host "Checking APIM provisioning state..." -ForegroundColor Yellow
$maxRetries = 60
$retryCount = 0
do {
    $apim = az apim show --name $ApimName --resource-group $ResourceGroup --query provisioningState -o tsv 2>$null
    if ($apim -eq "Succeeded") {
        Write-Host "APIM is ready!" -ForegroundColor Green
        break
    }
    Write-Host "  State: $apim - waiting 30 seconds... ($retryCount/$maxRetries)"
    Start-Sleep -Seconds 30
    $retryCount++
} while ($retryCount -lt $maxRetries)

if ($apim -ne "Succeeded") {
    Write-Error "APIM did not become ready in time"
    exit 1
}

# Get APIM gateway URL
$gatewayUrl = az apim show --name $ApimName --resource-group $ResourceGroup --query gatewayUrl -o tsv
Write-Host "Gateway URL: $gatewayUrl" -ForegroundColor Cyan

# Create the API - Schematica API
Write-Host "Creating Schematica API..." -ForegroundColor Yellow

# Create API via REST (az apim api commands are limited)
az apim api create `
    --resource-group $ResourceGroup `
    --service-name $ApimName `
    --api-id "schematica-api" `
    --display-name "WARNERCO Schematica API" `
    --path "api" `
    --service-url "https://$ContainerAppFqdn/api" `
    --protocols https `
    --subscription-required false

# Create operations for the API
Write-Host "Creating API operations..." -ForegroundColor Yellow

# Health endpoint
az apim api operation create `
    --resource-group $ResourceGroup `
    --service-name $ApimName `
    --api-id "schematica-api" `
    --operation-id "health" `
    --display-name "Health Check" `
    --method GET `
    --url-template "/health"

# List robots
az apim api operation create `
    --resource-group $ResourceGroup `
    --service-name $ApimName `
    --api-id "schematica-api" `
    --operation-id "list-robots" `
    --display-name "List Robots" `
    --method GET `
    --url-template "/robots"

# Get robot by ID
az apim api operation create `
    --resource-group $ResourceGroup `
    --service-name $ApimName `
    --api-id "schematica-api" `
    --operation-id "get-robot" `
    --display-name "Get Robot" `
    --method GET `
    --url-template "/robots/{id}"

# Search robots
az apim api operation create `
    --resource-group $ResourceGroup `
    --service-name $ApimName `
    --api-id "schematica-api" `
    --operation-id "search-robots" `
    --display-name "Search Robots" `
    --method POST `
    --url-template "/search"

# Create MCP API for tool exposure
Write-Host "Creating MCP Tools API..." -ForegroundColor Yellow

az apim api create `
    --resource-group $ResourceGroup `
    --service-name $ApimName `
    --api-id "mcp-tools" `
    --display-name "WARNERCO MCP Tools" `
    --path "mcp" `
    --service-url "https://$ContainerAppFqdn/mcp" `
    --protocols https `
    --subscription-required false

# MCP SSE endpoint (for streaming)
az apim api operation create `
    --resource-group $ResourceGroup `
    --service-name $ApimName `
    --api-id "mcp-tools" `
    --operation-id "mcp-sse" `
    --display-name "MCP SSE Stream" `
    --method GET `
    --url-template "/sse"

# MCP messages endpoint
az apim api operation create `
    --resource-group $ResourceGroup `
    --service-name $ApimName `
    --api-id "mcp-tools" `
    --operation-id "mcp-messages" `
    --display-name "MCP Messages" `
    --method POST `
    --url-template "/messages"

# Create Dashboard API (static files)
Write-Host "Creating Dashboard API..." -ForegroundColor Yellow

az apim api create `
    --resource-group $ResourceGroup `
    --service-name $ApimName `
    --api-id "dashboard" `
    --display-name "WARNERCO Dashboard" `
    --path "" `
    --service-url "https://$ContainerAppFqdn" `
    --protocols https `
    --subscription-required false

# Root dashboard
az apim api operation create `
    --resource-group $ResourceGroup `
    --service-name $ApimName `
    --api-id "dashboard" `
    --operation-id "root" `
    --display-name "Dashboard Home" `
    --method GET `
    --url-template "/"

# Static assets wildcard
az apim api operation create `
    --resource-group $ResourceGroup `
    --service-name $ApimName `
    --api-id "dashboard" `
    --operation-id "static-assets" `
    --display-name "Static Assets" `
    --method GET `
    --url-template "/*"

Write-Host "`nAPIM Configuration Complete!" -ForegroundColor Green
Write-Host "Gateway URL: $gatewayUrl" -ForegroundColor Cyan
Write-Host "API Endpoints:" -ForegroundColor Cyan
Write-Host "  - Dashboard: $gatewayUrl/" -ForegroundColor White
Write-Host "  - API: $gatewayUrl/api/*" -ForegroundColor White
Write-Host "  - MCP: $gatewayUrl/mcp/*" -ForegroundColor White
