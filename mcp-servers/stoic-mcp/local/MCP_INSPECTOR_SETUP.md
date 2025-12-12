# MCP Inspector Setup for Stoic MCP

## Overview

This document describes the MCP Inspector integration for the Stoic MCP local server, including automatic port management to prevent conflicts.

## Changes Made

### 1. Port Management Script

Created `scripts/kill-ports.js` - automatically cleans ports before inspector starts:
- Port 3000: Inspector backend server
- Port 5173: Inspector Vite UI (if using older version)

### 2. Package.json Scripts

Added two new scripts:

```json
"kill-ports": "node scripts/kill-ports.js"
"inspector": "npm run build --if-present && npm run kill-ports && npx @modelcontextprotocol/inspector node dist/index.js"
```

### 3. Dependencies

Added `@modelcontextprotocol/inspector` as a dev dependency (downloaded via npx on first run).

## Usage

### Start MCP Inspector

```bash
cd stoic-mcp/local
npm run inspector
```

This will:
1. Build TypeScript to JavaScript (if needed)
2. Clean ports 3000 and 5173
3. Start the MCP Inspector with authentication
4. Automatically open your browser

### Manual Port Cleanup

If you encounter port conflicts:

```bash
npm run kill-ports
```

### Start Server Without Inspector

```bash
npm start
```

## Inspector Features

The inspector provides:
- **Tool Testing**: Call all 9 Stoic tools interactively
- **Request/Response Viewer**: See JSON-RPC messages
- **Server Logs**: Monitor stderr output from the server
- **Authentication**: Secure token-based access (URL includes token)

## Available Tools

Test these tools in the inspector:

1. **get_random_quote** - Get a random Stoic quote
2. **search_quotes** - Search by author, theme, or keyword
3. **add_quote** - Add new quote to collection
4. **get_quote_explanation** - AI-powered modern application
5. **toggle_favorite** - Mark/unmark favorites
6. **get_favorites** - View all favorite quotes
7. **update_quote_notes** - Add personal reflections
8. **delete_quote** - Remove quotes
9. **generate_quote** - AI-generate Stoic-style quotes

## Port Configuration

The inspector uses dynamic ports with authentication tokens. The URL format is:

```
http://localhost:<PORT>/?MCP_PROXY_AUTH_TOKEN=<TOKEN>
```

The token is unique per session and automatically included in the URL when the browser opens.

## Troubleshooting

### Inspector Won't Start

1. **Check for port conflicts:**
   ```bash
   npm run kill-ports
   ```

2. **Verify build succeeded:**
   ```bash
   npm run build
   ```

3. **Check TypeScript compilation:**
   ```bash
   npx tsc --noEmit
   ```

### Server Not Responding

1. Check server logs in terminal (stderr output)
2. Verify `dist/index.js` exists after build
3. Test server directly: `npm start`

### Authentication Issues

The inspector uses session tokens. If you see auth errors:
- Copy the full URL including the `MCP_PROXY_AUTH_TOKEN` parameter
- Or set `DANGEROUSLY_OMIT_AUTH=true` environment variable (not recommended)

## Comparison with CoreText MCP

Both servers now have identical inspector setups:

| Feature | CoreText MCP | Stoic MCP Local |
|---------|-------------|-----------------|
| Port Cleanup | ✅ Automatic | ✅ Automatic |
| Inspector Script | ✅ `npm run inspector` | ✅ `npm run inspector` |
| Kill Ports Script | ✅ `npm run kill-ports` | ✅ `npm run kill-ports` |
| Auto-build | ✅ (N/A - pure JS) | ✅ TypeScript → JS |

## Development Workflow

### During Development

```bash
# Terminal 1: Watch TypeScript compilation
npm run watch

# Terminal 2: Run inspector
npm run inspector
```

### Before Committing

```bash
# Clean build
npm run clean
npm run build

# Test with inspector
npm run inspector
```

## Technical Details

### Why Port Cleanup?

MCP Inspector needs specific ports. If previous sessions crashed or didn't shut down cleanly, those ports remain occupied. The `kill-ports` script ensures a clean state.

### Why Build Before Inspector?

The inspector runs `dist/index.js` (compiled JavaScript), not the TypeScript source. The build step ensures the latest code is used.

### TypeScript Compilation

```bash
# One-time build
npm run build

# Watch mode (auto-rebuild on save)
npm run watch
```

## Integration with MCP Clients

After testing in the inspector, integrate with:

### Claude Desktop

**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
**Mac/Linux**: `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "stoic": {
      "command": "node",
      "args": ["C:/github/context-engineering-2/stoic-mcp/local/dist/index.js"]
    }
  }
}
```

### VS Code

Create `.vscode/mcp.json`:

```json
{
  "mcpServers": {
    "stoic": {
      "command": "node",
      "args": ["${workspaceFolder}/local/dist/index.js"]
    }
  }
}
```

## Next Steps

1. Test all tools in the inspector
2. Verify quote database is populated (`data/quotes.json`)
3. Test AI features (requires `DEEPSEEK_API_KEY` environment variable)
4. Integrate with Claude Desktop or other MCP clients

## Resources

- [MCP Inspector Documentation](https://github.com/modelcontextprotocol/inspector)
- [MCP Specification](https://spec.modelcontextprotocol.io/)
- [Stoic MCP README](../README.md)
