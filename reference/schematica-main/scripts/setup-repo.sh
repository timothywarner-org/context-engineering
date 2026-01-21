#!/bin/bash

# Schematica Repository Setup Script
# This script configures GitHub repository settings including topics and labels
# Prerequisites: GitHub CLI (gh) authenticated with appropriate permissions

set -e

REPO="${GITHUB_REPOSITORY:-timothywarner-org/schematica}"

echo "========================================"
echo " Schematica Repository Setup"
echo "========================================"
echo ""
echo "Repository: $REPO"
echo ""

# Check if gh CLI is available
if ! command -v gh &> /dev/null; then
    echo "Error: GitHub CLI (gh) is not installed."
    echo "Install from: https://cli.github.com/"
    exit 1
fi

# Check if authenticated
if ! gh auth status &> /dev/null; then
    echo "Error: Not authenticated with GitHub CLI."
    echo "Run: gh auth login"
    exit 1
fi

echo "Setting repository topics..."
echo ""

# Define topics for the repository
TOPICS=(
    "mcp"
    "model-context-protocol"
    "mcp-server"
    "devops"
    "devops-training"
    "docker"
    "typescript"
    "express"
    "azure"
    "azure-container-apps"
    "circleci"
    "robotics"
    "ai-integration"
    "claude"
    "anthropic"
)

# Convert array to comma-separated string
TOPICS_STRING=$(IFS=,; echo "${TOPICS[*]}")

# Set topics using GitHub API
gh api -X PUT "repos/$REPO/topics" \
    -f names="$(printf '%s\n' "${TOPICS[@]}" | jq -R . | jq -s .)" \
    --silent

echo "Topics set successfully!"
echo ""
echo "Topics applied:"
for topic in "${TOPICS[@]}"; do
    echo "  - $topic"
done

echo ""
echo "========================================"
echo " Syncing Labels"
echo "========================================"
echo ""

# Check if labels.yml exists
LABELS_FILE=".github/labels.yml"
if [ -f "$LABELS_FILE" ]; then
    echo "Found labels configuration at $LABELS_FILE"
    echo ""

    # Parse and create labels from YAML
    # Note: This requires yq to be installed for full YAML parsing
    # For simplicity, we'll use the GitHub workflow for label sync instead

    echo "To sync labels, either:"
    echo "  1. Run the 'Sync Labels' workflow from GitHub Actions"
    echo "  2. Use: gh label import $LABELS_FILE"
    echo ""
else
    echo "Warning: Labels configuration not found at $LABELS_FILE"
fi

echo "========================================"
echo " Repository Description"
echo "========================================"
echo ""

DESCRIPTION="Globomantics Robotics MCP Server - Schematic lookup service for DevOps training. A Model Context Protocol server for AI-powered robotic component documentation."

echo "Setting repository description..."
gh repo edit "$REPO" --description "$DESCRIPTION"

echo ""
echo "Description set successfully!"

echo ""
echo "========================================"
echo " Setup Complete!"
echo "========================================"
echo ""
echo "Repository URL: https://github.com/$REPO"
echo ""
echo "Next steps:"
echo "  1. Verify topics at: https://github.com/$REPO"
echo "  2. Run 'Sync Labels' workflow to create issue labels"
echo "  3. Configure branch protection rules as needed"
echo ""
