# Sample Configuration Files

Sample configuration files for integrating MCP servers with AI clients.

## Contents

| File | Description |
|------|-------------|
| `claude_desktop_config.json` | Sample Claude Desktop MCP configuration |

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
      "args": ["C:/path/to/context-engineering/mcp-servers/coretext-mcp/src/index.js"]
    }
  }
}
```

Restart Claude Desktop after modifying the configuration.

## VS Code Configuration

For VS Code MCP configuration examples, see the `examples/` directory:

- `examples/vscode_settings.json` - VS Code settings example
- `examples/claude_code_mcp.json` - Claude Code MCP configuration example

VS Code configurations are placed in `.vscode/mcp.json` within your workspace.
