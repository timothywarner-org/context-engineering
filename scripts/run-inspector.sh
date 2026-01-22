#!/bin/bash
# MCP Inspector Debugging Script for WARNERCO Schematica
# Usage: ./run-inspector.sh

set -e

echo -e "\033[36mStarting MCP Inspector for WARNERCO Schematica...\033[0m"

# Navigate to backend directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_PATH="$SCRIPT_DIR/../src/warnerco/backend"
cd "$BACKEND_PATH"

# Ensure dependencies are installed
echo -e "\033[33mChecking dependencies...\033[0m"
uv sync

# Start MCP Inspector with the warnerco-mcp server
echo -e "\n\033[32mLaunching MCP Inspector...\033[0m"
echo -e "\033[36mBrowser will open at: http://localhost:5173\033[0m"
echo -e "\033[33mPress Ctrl+C to stop\n\033[0m"

# Run MCP Inspector pointing to our server
npx @modelcontextprotocol/inspector uv run warnerco-mcp
