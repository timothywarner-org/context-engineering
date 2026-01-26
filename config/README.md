# Sample Configuration Files

Sample configuration files for integrating MCP servers with AI clients.

## Contents

| File                         | Description                                              |
| ---------------------------- | -------------------------------------------------------- |
| `claude_desktop_config.json` | Sample Claude Desktop MCP configuration                  |
| `mcp.json.example`           | VS Code MCP configuration with Azure deployment examples |

## Claude Desktop Configuration

Copy `claude_desktop_config.json` to the appropriate location for your OS:

- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

After copying, update the paths in the configuration to match your local installation:

```json
{
  "mcpServers": {
    "coretext": {
      "command": "node",
      "args": [
        "C:/path/to/context-engineering/mcp-servers/coretext-mcp/src/index.js"
      ]
    }
  }
}
```

Restart Claude Desktop after modifying the configuration.

## VS Code Configuration

For VS Code, you have two options:

### Option 1: Local Development (stdio transport)

Use the existing `.vscode/mcp.json` in the workspace root for local development:

```json
{
  "servers": {
    "warnerco-schematica": {
      "command": "uv",
      "args": ["run", "warnerco-mcp"],
      "cwd": "${workspaceFolder}/src/warnerco/backend",
      "env": {
        "MEMORY_BACKEND": "chroma"
      }
    }
  }
}
```

### Option 2: Azure Deployment (HTTP transport)

Copy `mcp.json.example` to `.vscode/mcp.json` and configure for Azure:

```bash
# Get your Container App URL
az containerapp show \
  --name warnerco-schematica-prod \
  --resource-group warnerco-rg \
  --query properties.configuration.ingress.fqdn -o tsv

# Get your APIM Gateway URL (if using API Management)
az apim show \
  --name warnerco-apim \
  --resource-group warnerco-rg \
  --query gatewayUrl -o tsv
```

Update `.vscode/mcp.json`:

```json
{
  "servers": {
    "warnerco-schematica-azure": {
      "url": "https://YOUR-CONTAINER-APP-FQDN/mcp",
      "transport": "http"
    }
  }
}
```

For API Management (with authentication):

```json
{
  "servers": {
    "warnerco-schematica-apim": {
      "url": "https://YOUR-APIM-GATEWAY/mcp",
      "transport": "http",
      "headers": {
        "Ocp-Apim-Subscription-Key": "YOUR-SUBSCRIPTION-KEY"
      }
    }
  }
}
```

### Getting APIM Subscription Keys

```bash
# Create subscription
az apim subscription create \
  --resource-group warnerco-rg \
  --service-name warnerco-apim \
  --name vscode-mcp-client \
  --scope /apis/schematica-api

# Get primary key
az apim subscription show \
  --resource-group warnerco-rg \
  --service-name warnerco-apim \
  --subscription-id vscode-mcp-client \
  --query primaryKey -o tsv
```

## MCP Transport Types

| Transport | Use Case                                        | Supported Clients                    |
| --------- | ----------------------------------------------- | ------------------------------------ |
| **stdio** | Local development, direct process communication | Claude Desktop, VS Code, CLI tools   |
| **http**  | Remote servers, Azure deployments               | VS Code, Claude Code, custom clients |

- **stdio**: Server runs as subprocess, communicates via stdin/stdout
- **http**: Server runs independently, communicates via HTTP requests to `/mcp` endpoint
