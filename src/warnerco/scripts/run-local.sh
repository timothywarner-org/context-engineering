#!/bin/bash
# WARNERCO Robotics Schematica - Local Development Runner
# Usage: ./run-local.sh [--build-dash]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BACKEND_DIR="$PROJECT_ROOT/backend"
DASH_DIR="$PROJECT_ROOT/dashboards"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}WARNERCO Robotics Schematica${NC}"
echo -e "${GREEN}Local Development Server${NC}"
echo -e "${GREEN}========================================${NC}"

# Check for Poetry
if ! command -v poetry &> /dev/null; then
    echo -e "${RED}Error: Poetry is not installed.${NC}"
    echo "Install with: curl -sSL https://install.python-poetry.org | python3 -"
    exit 1
fi

# Build dashboards if requested
if [[ "$1" == "--build-dash" ]]; then
    echo -e "${YELLOW}Building Astro dashboards...${NC}"
    cd "$DASH_DIR"

    if ! command -v npm &> /dev/null; then
        echo -e "${RED}Error: npm is not installed.${NC}"
        exit 1
    fi

    npm install
    npm run build
    echo -e "${GREEN}Dashboards built successfully!${NC}"
fi

# Install backend dependencies
echo -e "${YELLOW}Installing Python dependencies...${NC}"
cd "$BACKEND_DIR"
poetry install

# Copy .env.example if .env doesn't exist
if [ ! -f "$BACKEND_DIR/.env" ]; then
    echo -e "${YELLOW}Creating .env from .env.example...${NC}"
    cp "$BACKEND_DIR/.env.example" "$BACKEND_DIR/.env"
fi

# Run the server
echo -e "${GREEN}Starting WARNERCO Schematica server...${NC}"
echo -e "${GREEN}API: http://localhost:8000${NC}"
echo -e "${GREEN}API Docs: http://localhost:8000/docs${NC}"
echo -e "${GREEN}Dashboard: http://localhost:8000/dash/${NC}"
echo ""

poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
