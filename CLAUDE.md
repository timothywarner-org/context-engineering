# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Training materials and MCP server implementations for "Context Engineering with MCP" - a course teaching production MCP (Model Context Protocol) deployment. Contains working MCP servers in JavaScript, TypeScript, and Python, plus hands-on labs.

## Repository Structure

```
context-engineering/
├── mcp-servers/                    # Production MCP server implementations
│   ├── coretext-mcp/              # JavaScript - Main teaching example (CRUD + enrichment)
│   ├── stoic-mcp/                 # TypeScript monorepo (local/ and azure/ workspaces)
│   ├── context_journal_mcp_local/ # Python implementation
│   ├── context_journal_mcp_azure/ # Python Azure deployment
│   └── deepseek-context-demo/     # Context window visualization
├── examples/filesystem-mcp/        # Reference implementation
├── labs/lab-01-hello-mcp/         # Hands-on exercises (starter + solution)
├── config/                         # Sample MCP client configs
└── instructor/                     # Course materials and runbook
```

## Development Commands

### CoreText MCP (JavaScript) - Primary Teaching Server

```bash
cd mcp-servers/coretext-mcp
npm install
npm run dev          # Start with auto-reload
npm run inspector    # Test with MCP Inspector (http://localhost:5173)
npm test             # Run automated test suite
npm run demo:reset   # Reset demo data
```

### Stoic MCP (TypeScript) - Monorepo with Workspaces

```bash
cd mcp-servers/stoic-mcp
npm install          # Install all workspaces from root
cd local
npm run build        # Compile TypeScript
npm start            # Run compiled server
npm run inspector    # Test with MCP Inspector
npm run import       # Import quotes from source files
```

### Python MCP Servers

```bash
cd mcp-servers/context_journal_mcp_local
pip install -r requirements.txt
python context_journal_mcp.py
```

### Labs

```bash
cd labs/lab-01-hello-mcp/starter
npm install
npm start
# Test with: npx @modelcontextprotocol/inspector node src/index.js
```

## MCP Server Architecture Patterns

### Tool Response Format
All tools must return content array:
```javascript
return {
  content: [{
    type: 'text',
    text: JSON.stringify(result)
  }]
};
```

### Logging Convention
Use `console.error()` for all logging - stdout reserved for MCP protocol:
```javascript
console.error('🔧 Tool called:', toolName);  // Goes to stderr
```

### Resource URIs
Resources use URI scheme: `memory://overview`, `memory://context-stream`

### Adding New Tools (coretext-mcp pattern)
1. Add tool definition to `ListToolsRequestSchema` handler (~line 417)
2. Add case to `CallToolRequestSchema` switch statement (~line 547)
3. Return MCP-formatted response

## Key Files

- `mcp-servers/coretext-mcp/src/index.js` - Complete single-file MCP server (intentional for teaching)
- `mcp-servers/stoic-mcp/local/src/index.ts` - TypeScript MCP server entry
- `mcp-servers/stoic-mcp/local/src/storage.ts` - JSON persistence layer
- `config/claude_desktop_config.json` - Sample Claude Desktop configuration
- `config/mcp.json` - Sample VS Code MCP configuration

## MCP Client Configuration

### Claude Desktop
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
**Mac**: `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "coretext": {
      "command": "node",
      "args": ["C:/github/context-engineering/mcp-servers/coretext-mcp/src/index.js"]
    }
  }
}
```

### VS Code
Create `.vscode/mcp.json` in workspace:
```json
{
  "mcpServers": {
    "coretext": {
      "command": "node",
      "args": ["${workspaceFolder}/mcp-servers/coretext-mcp/src/index.js"]
    }
  }
}
```

## Azure Deployment

Both coretext-mcp and stoic-mcp have Azure deployment scripts:

```bash
cd mcp-servers/coretext-mcp/azure
./deploy.sh   # Deploys Container Apps + Cosmos DB + Key Vault

cd mcp-servers/stoic-mcp/azure
./deploy.sh
```

Infrastructure: Bicep templates in `azure/main.bicep`, parameters in `azure/parameters.json`

## Testing with MCP Inspector

Primary debugging tool - opens web UI to call tools and view resources:
```bash
npx @modelcontextprotocol/inspector node path/to/server.js
# Opens http://localhost:5173
```

If port conflicts occur:
```bash
npm run kill-ports   # Available in coretext-mcp and stoic-mcp
```

## Environment Variables

Optional `DEEPSEEK_API_KEY` enables AI enrichment features. Servers work without it using fallback mode.

```bash
cp .env.example .env
# Edit .env to add API key
```

## MCP Resources

- **MCP Specification**: https://spec.modelcontextprotocol.io/
- **TypeScript SDK**: `@modelcontextprotocol/sdk` (npm)
- **Python SDK**: `mcp` (pip)
- **MCP Inspector**: `@modelcontextprotocol/inspector`
