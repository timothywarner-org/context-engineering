# MCP Configuration Guide

This guide explains how to configure Claude Desktop and VS Code GitHub Copilot to connect to the CoreText and Stoic MCP servers in this repository.

## Prerequisites

- **Node.js 18+** installed
- **CoreText MCP**: No build step needed (uses plain JavaScript)
- **Stoic MCP**: Requires TypeScript compilation before use

## Build Stoic MCP Server (Required)

Before using the Stoic MCP server, you must compile it:

```bash
cd stoic-mcp/local
npm install
npm run build
```

This creates the `dist/index.js` file that the MCP configuration references.

## Configuration Files

### 1. Claude Desktop Configuration

**Location:**

- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

**Sample file**: `claude_desktop_config.json` (in this repository root)

Copy the contents of this sample file to your Claude Desktop configuration location.

**Configuration:**

```json
{
  "mcpServers": {
    "coretext": {
      "command": "node",
      "args": [
        "C:\\github\\context-engineering-2\\coretext-mcp\\src\\index.js"
      ],
      "env": {
        "DEEPSEEK_API_KEY": "sk-1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p"
      }
    },
    "stoic-mcp": {
      "command": "node",
      "args": [
        "C:\\github\\context-engineering-2\\stoic-mcp\\local\\dist\\index.js"
      ],
      "env": {
        "DEEPSEEK_API_KEY": "sk-1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p"
      }
    }
  }
}
```

**Notes:**

- Replace `C:\\github\\context-engineering-2` with your actual repository path
- Use double backslashes (`\\`) for Windows paths
- Use forward slashes (`/`) for macOS/Linux paths
- Replace the fictional API key with your real DeepSeek API key

### 2. VS Code GitHub Copilot Configuration

**Location:** `.vscode/mcp.json` in your workspace (or this repository root)

**Sample file**: `mcp.json` (in this repository root)

**Configuration:**

```json
{
  "mcpServers": {
    "coretext": {
      "command": "node",
      "args": [
        "C:\\github\\context-engineering-2\\coretext-mcp\\src\\index.js"
      ],
      "env": {
        "DEEPSEEK_API_KEY": "sk-1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p"
      }
    },
    "stoic-mcp": {
      "command": "node",
      "args": [
        "C:\\github\\context-engineering-2\\stoic-mcp\\local\\dist\\index.js"
      ],
      "env": {
        "DEEPSEEK_API_KEY": "sk-1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p"
      }
    }
  }
}
```

**Notes:**

- Update paths to match your repository location
- Replace the fictional API key with your real DeepSeek API key
- VS Code will load this configuration when you open the workspace

## DeepSeek API Key

The fictional API key in these samples is: `sk-1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p`

**To get a real API key:**
1. Visit https://platform.deepseek.com/
2. Sign up for an account
3. Navigate to API Keys section
4. Generate a new API key
5. Replace the fictional key in your configuration files

**Alternative (for testing without API key):**
Both servers support fallback modes:
- **CoreText MCP**: Uses local keyword extraction instead of AI enrichment
- **Stoic MCP**: Still provides quotes, but explanations will use fallback messages

To test without an API key, simply omit the `env` section:

```json
{
  "mcpServers": {
    "coretext": {
      "command": "node",
      "args": [
        "C:\\github\\context-engineering-2\\coretext-mcp\\src\\index.js"
      ]
    }
  }
}
```

## Path Customization

If your repository is in a different location, update all paths:

### Windows Example

```json
"args": ["D:\\Projects\\my-mcp-servers\\coretext-mcp\\src\\index.js"]
```

### macOS/Linux Example

```json
"args": ["/Users/yourname/projects/context-engineering-2/coretext-mcp/src/index.js"]
```

### Using Relative Paths (VS Code only)

For workspace-relative paths in VS Code:

```json
"args": ["${workspaceFolder}/coretext-mcp/src/index.js"]
```

## Verifying Configuration

### Claude Desktop

1. Close and restart Claude Desktop completely
2. In a new conversation, check the tools menu (hammer icon)
3. You should see tools from both servers:
   - **CoreText**: memory_create, memory_read, memory_list, etc.
   - **Stoic MCP**: get_random_quote, search_quotes, add_quote, etc.

### VS Code

1. Reload VS Code window (`Ctrl+Shift+P` → "Reload Window")
2. Open GitHub Copilot Chat
3. Check available tools/extensions in Copilot settings

## Troubleshooting

### Server Not Appearing

**Check 1: Build Status**

```bash
# Stoic MCP must be built
cd stoic-mcp/local
npm run build
# Should create dist/index.js
```

**Check 2: Path Accuracy**

- Verify paths point to actual files
- Use absolute paths (not relative)
- Windows: Use double backslashes (`\\`)

**Check 3: Node.js Version**

```bash
node --version
# Should be v18 or higher
```

### API Key Issues

**Error: "DeepSeek API key not found"**

- Check that `DEEPSEEK_API_KEY` is set in config
- Verify the key format (should start with `sk-`)
- Try fallback mode (remove `env` section to test)

**Error: "Invalid API key"**

- The fictional key won't work with real API calls
- Replace with actual key from https://platform.deepseek.com/

### Log Files

**Claude Desktop Logs:**

- Windows: `%APPDATA%\Claude\logs`
- macOS: `~/Library/Logs/Claude`

Look for MCP server connection errors in the logs.

## Testing the Servers

### CoreText MCP

In Claude Desktop or VS Code Copilot:

```
Create a new memory: "MCP enables persistent AI context across sessions"
```

Expected response: Memory created with ID, enrichment data, and metadata.

### Stoic MCP

In Claude Desktop or VS Code Copilot:

```
Get me a random Stoic quote
```

Expected response: Quote text, author, source, and theme.

## Security Notes

**IMPORTANT:**
- Never commit real API keys to version control
- The fictional key in these samples is for demonstration only
- Use environment variables for production deployments
- For Azure deployments, use Azure Key Vault instead

## Additional Resources

- **MCP Documentation**: https://modelcontextprotocol.io/docs
- **CoreText MCP README**: `coretext-mcp/README.md`
- **Stoic MCP README**: `stoic-mcp/README.md`
- **Claude Desktop Config**: https://docs.anthropic.com/claude/docs/claude-desktop
