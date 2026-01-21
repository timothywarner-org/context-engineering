# WARNERCO Robotics Schematica - Local Development Runner (PowerShell)
# Usage: .\run-local.ps1 [-BuildDash]

param(
    [switch]$BuildDash
)

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir
$BackendDir = Join-Path $ProjectRoot "backend"
$DashDir = Join-Path $ProjectRoot "dashboards"

Write-Host "========================================" -ForegroundColor Green
Write-Host "WARNERCO Robotics Schematica" -ForegroundColor Green
Write-Host "Local Development Server" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green

# Check for Poetry
if (-not (Get-Command poetry -ErrorAction SilentlyContinue)) {
    Write-Host "Error: Poetry is not installed." -ForegroundColor Red
    Write-Host "Install with: (Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -"
    exit 1
}

# Build dashboards if requested
if ($BuildDash) {
    Write-Host "Building Astro dashboards..." -ForegroundColor Yellow
    Set-Location $DashDir

    if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
        Write-Host "Error: npm is not installed." -ForegroundColor Red
        exit 1
    }

    npm install
    npm run build
    Write-Host "Dashboards built successfully!" -ForegroundColor Green
}

# Install backend dependencies
Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
Set-Location $BackendDir
poetry install

# Copy .env.example if .env doesn't exist
$EnvFile = Join-Path $BackendDir ".env"
$EnvExample = Join-Path $BackendDir ".env.example"
if (-not (Test-Path $EnvFile)) {
    Write-Host "Creating .env from .env.example..." -ForegroundColor Yellow
    Copy-Item $EnvExample $EnvFile
}

# Run the server
Write-Host "Starting WARNERCO Schematica server..." -ForegroundColor Green
Write-Host "API: http://localhost:8000" -ForegroundColor Green
Write-Host "API Docs: http://localhost:8000/docs" -ForegroundColor Green
Write-Host "Dashboard: http://localhost:8000/dash/" -ForegroundColor Green
Write-Host ""

poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
