# MCP Server Implementations

This folder contains complete MCP server implementations for learning and production use.

## Server Overview

| Server | Language | Description | Best For |
|--------|----------|-------------|----------|
| [coretext-mcp](coretext-mcp/) | JavaScript | Main teaching example - context journal | Learning MCP basics |
| [stoic-mcp](stoic-mcp/) | TypeScript | Production-ready daily quotes server | Production patterns |
| [context_journal_mcp_local](context_journal_mcp_local/) | Python | Local Python implementation | Python developers |
| [context_journal_mcp_azure](context_journal_mcp_azure/) | Python | Azure-deployed version | Cloud deployment |
| [deepseek-context-demo](deepseek-context-demo/) | JavaScript | DeepSeek API integration | AI API integration |

## Getting Started

### For Learning (Start Here)

1. **[coretext-mcp](coretext-mcp/)** - Simple JavaScript server
   ```bash
   cd coretext-mcp
   npm install
   npm start
   ```

### For Production

2. **[stoic-mcp](stoic-mcp/)** - TypeScript with proper structure
   ```bash
   cd stoic-mcp
   npm install
   npm run build
   npm start
   ```

## Testing with MCP Inspector

```bash
# Install inspector globally
npm install -g @modelcontextprotocol/inspector

# Test any server
npx @modelcontextprotocol/inspector node path/to/server/index.js
```

## Documentation

Each server includes:
- `README.md` - Overview and quick start
- `CODE_WALKTHROUGH.md` - Detailed code explanation (where available)
- Azure deployment files in `azure/` subdirectory (where applicable)
