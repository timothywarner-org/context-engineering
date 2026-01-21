---
name: mcp-server-builder
description: Build Model Context Protocol (MCP) servers in Python (FastMCP), JavaScript, or TypeScript. Use when creating new MCP servers, adding tools/resources/prompts, configuring transports (stdio/HTTP), or debugging MCP protocol issues. Triggers on requests for MCP development, AI tool creation, or Claude Desktop integration.
---

# MCP Server Builder

Build production-ready MCP servers with proper tool schemas, resources, and transport configuration.

## Quick Start

### Python (FastMCP)

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("my-server")

@mcp.tool()
async def greet(name: str) -> str:
    """Greet someone by name."""
    return f"Hello, {name}!"

if __name__ == "__main__":
    mcp.run()
```

### JavaScript

```javascript
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";

const server = new Server({ name: "my-server", version: "1.0.0" }, { capabilities: { tools: {} } });

server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [{ name: "greet", description: "Greet someone", inputSchema: { type: "object", properties: { name: { type: "string" } }, required: ["name"] } }]
}));

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  if (request.params.name === "greet") {
    return { content: [{ type: "text", text: `Hello, ${request.params.arguments.name}!` }] };
  }
});

const transport = new StdioServerTransport();
await server.connect(transport);
```

## Language Selection

| Criterion | Python (FastMCP) | JavaScript/TypeScript |
|-----------|------------------|----------------------|
| Rapid prototyping | Best | Good |
| Type safety | Via Pydantic | Native (TS) |
| Async I/O | Native | Native |
| Package ecosystem | pip/uv | npm |
| Production deploy | Container Apps | Container Apps |

## Project Structure

### Python

```
my-mcp/
├── pyproject.toml
├── src/
│   └── my_mcp/
│       ├── __init__.py
│       ├── server.py      # FastMCP instance
│       └── tools/         # Tool implementations
├── data/                  # Persistent storage
└── .env.example
```

### JavaScript/TypeScript

```
my-mcp/
├── package.json
├── src/
│   ├── index.js           # Server entry
│   └── tools/             # Tool handlers
├── data/                  # Persistent storage
└── .env.example
```

## Tool Patterns

### Structured Output (Python)

```python
from pydantic import BaseModel, Field

class SearchResult(BaseModel):
    id: str
    title: str
    score: float = Field(ge=0, le=1)

@mcp.tool()
async def search(query: str, limit: int = 10) -> list[SearchResult]:
    """Search documents by query."""
    # Implementation...
    return [SearchResult(id="1", title="Result", score=0.95)]
```

### Context for Logging (Python)

```python
from mcp.server.fastmcp import Context

@mcp.tool()
async def process(data: str, ctx: Context) -> str:
    """Process data with progress reporting."""
    await ctx.info(f"Processing {len(data)} chars")
    await ctx.report_progress(0, 100, "Starting...")
    # Work...
    await ctx.report_progress(100, 100, "Done")
    return result
```

### Resources (Python)

```python
@mcp.resource("memory://overview")
async def memory_overview() -> str:
    """Current memory state summary."""
    return json.dumps({"total": 100, "active": 85})

@mcp.resource("file://{path}")  # Dynamic URI template
async def read_file(path: str) -> str:
    """Read file contents."""
    return Path(path).read_text()
```

## Transport Configuration

### Stdio (Local - Claude Desktop)

**Python**: `mcp.run()` (default)
**JavaScript**: `new StdioServerTransport()`

**Claude Desktop config** (`claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "my-server": {
      "command": "python",
      "args": ["-m", "my_mcp.server"]
    }
  }
}
```

### HTTP (Remote - Azure/Cloud)

**Python**:
```python
mcp.run(transport="streamable-http", host="0.0.0.0", port=8000)
```

**For ASGI mounting**:
```python
app = mcp.streamable_http_app()
# Mount to FastAPI/Starlette
```

## Testing

### MCP Inspector

```bash
# Python
uv run mcp dev server.py

# JavaScript
npx @modelcontextprotocol/inspector node src/index.js
```

Opens `http://localhost:5173` for interactive testing.

### Programmatic Testing

```python
import pytest
from my_mcp.server import mcp

@pytest.mark.asyncio
async def test_greet():
    result = await mcp.call_tool("greet", {"name": "World"})
    assert "Hello, World" in result
```

## Common Patterns

### Memory/CRUD Server

See `references/memory-patterns.md` for episodic/semantic memory implementations.

### API Wrapper Server

See `references/api-patterns.md` for wrapping external APIs as MCP tools.

### File Processing Server

See `references/file-patterns.md` for document processing workflows.

## Checklist

- [ ] Tools return `content: [{ type: "text", text: ... }]` format
- [ ] All logging uses stderr (`console.error` in JS, `ctx.info` in Python)
- [ ] Docstrings describe tool purpose (become protocol descriptions)
- [ ] Type hints drive schema generation
- [ ] Environment variables for secrets (never hardcoded)
- [ ] `.env.example` documents required config
- [ ] Test with MCP Inspector before Claude integration
