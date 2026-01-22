# MCP Inspector Debugging Script for WARNERCO Schematica
# Usage: .\run-inspector.ps1

$ErrorActionPreference = "Stop"

Write-Host "Starting MCP Inspector for WARNERCO Schematica..." -ForegroundColor Cyan

# Navigate to backend directory
$backendPath = Join-Path $PSScriptRoot "..\src\warnerco\backend"
Push-Location $backendPath

try {
    # Ensure dependencies are installed
    Write-Host "Checking dependencies..." -ForegroundColor Yellow
    uv sync

    # Start MCP Inspector with the warnerco-mcp server
    Write-Host "`nLaunching MCP Inspector..." -ForegroundColor Green
    Write-Host "Browser will open at: http://localhost:5173" -ForegroundColor Cyan
    Write-Host "Press Ctrl+C to stop`n" -ForegroundColor Yellow

    # Run MCP Inspector pointing to our server
    npx @modelcontextprotocol/inspector uv run warnerco-mcp

} finally {
    Pop-Location
}
