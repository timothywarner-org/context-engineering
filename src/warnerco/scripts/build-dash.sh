#!/bin/bash
# WARNERCO Robotics Schematica - Build Astro Dashboards
# Outputs to backend/static/dash for serving

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DASH_DIR="$PROJECT_ROOT/dashboards"

echo "Building WARNERCO Schematica dashboards..."

cd "$DASH_DIR"

# Install dependencies
npm install

# Build
npm run build

echo "Dashboard build complete!"
echo "Output: $PROJECT_ROOT/backend/static/dash"
