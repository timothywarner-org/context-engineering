# Testing WARNERCO Schematica with MCP Inspector

A hands-on tutorial for debugging and testing the WARNERCO Schematica MCP server using the Model Context Protocol Inspector.

**Author**: [Tim Warner](https://techtrainertim.com) | [GitHub](https://github.com/timothywarner)

---

## What You Will Learn

By completing this tutorial, you will be able to:

- Launch MCP Inspector and connect to the WARNERCO Schematica server
- Navigate the Inspector UI to test tools and view resources
- Debug MCP tool calls by examining request/response JSON
- Interpret common error patterns and resolve them
- Use semantic search to query robot schematics

**Time Required**: 20-30 minutes

---

## Prerequisites

Before starting, ensure you have:

| Requirement | Minimum Version | Verification Command |
|-------------|-----------------|---------------------|
| Node.js | 18.0+ | `node --version` |
| npm | 9.0+ | `npm --version` |
| uv (Python package manager) | Latest | `uv --version` |
| Repository cloned | - | `cd C:\github\context-engineering` |
| Backend dependencies | - | `cd src\warnerco\backend && uv sync` |

> **Note**: The WARNERCO Schematica server uses Python with FastMCP. The `uv` package manager handles all Python dependencies automatically.

---

## Step 1: Start MCP Inspector

You have two options for launching MCP Inspector with the WARNERCO Schematica server.

### Option A: Use the Provided Script (Recommended)

Open PowerShell and run:

```powershell
cd C:\github\context-engineering
.\scripts\run-inspector.ps1
```

**What this script does**:

1. Navigates to the backend directory
2. Runs `uv sync` to ensure dependencies are installed
3. Launches MCP Inspector pointing to the `warnerco-mcp` server

### Option B: Run Manually

If you prefer to run commands directly:

```powershell
cd C:\github\context-engineering\src\warnerco\backend
uv sync
npx @modelcontextprotocol/inspector uv run warnerco-mcp
```

### Expected Output

You should see output similar to:

```
Starting MCP Inspector...

Starting inspector...
  Client (MCPI):  http://localhost:6274
  Proxy (MCPP):   http://127.0.0.1:6277

Press Ctrl+C to stop
```

Your default browser will automatically open to `http://localhost:6274` (or `http://localhost:5173` on older versions).

> **Why two ports?** MCP Inspector uses a client UI (port 6274) and a proxy server (port 6277). The proxy bridges the browser-based UI to your stdio-based MCP server.

---

## Step 2: Understanding the Inspector UI

The MCP Inspector interface has four main areas.

```
+------------------------------------------------------------------+
|  MCP Inspector                           [Configuration] [Restart]|
+------------------------------------------------------------------+
|                                                                   |
|  Server: warnerco-schematica              Status: [Connected]     |
|                                                                   |
+------------------------------------------------------------------+
|                                                                   |
|  [Tools]    [Resources]    [Prompts]    [Notifications]          |
|                                                                   |
+------------------------------------------------------------------+
|                                                                   |
|                    Main Content Area                              |
|                                                                   |
|  +------------------------+  +--------------------------------+   |
|  | Tool/Resource List     |  | Details / Request-Response     |   |
|  |                        |  |                                |   |
|  | - warn_list_robots     |  | Input Parameters:              |   |
|  | - warn_get_robot       |  | [category: _________ ]         |   |
|  | - warn_semantic_search |  |                                |   |
|  | - warn_memory_stats    |  | [Execute]                      |   |
|  |                        |  |                                |   |
|  +------------------------+  +--------------------------------+   |
|                                                                   |
+------------------------------------------------------------------+
```

### UI Components

| Component | Purpose |
|-----------|---------|
| **Server Name** | Shows the connected MCP server (`warnerco-schematica`) |
| **Connection Status** | Green indicator when connected successfully |
| **Tools Tab** | Lists available MCP tools with their parameters |
| **Resources Tab** | Shows MCP resources (read-only data endpoints) |
| **Prompts Tab** | Displays prompt templates (if any) |
| **Notifications Tab** | Shows server logs and real-time messages |
| **Configuration Button** | Adjust timeouts and proxy settings |

---

## Step 3: Testing MCP Tools

The WARNERCO Schematica server exposes four MCP tools. Let us test each one.

### 3.1 Test `warn_list_robots`

This tool lists robot schematics with optional filtering.

**Steps**:

1. Click the **Tools** tab
2. Select `warn_list_robots` from the tool list
3. Leave all parameters empty for now
4. Click **Execute** (or **Run Tool**)

**Expected Response**:

```json
{
  "count": 25,
  "schematics": [
    {
      "id": "WRN-00001",
      "model": "WC-100",
      "name": "Atlas Prime",
      "component": "force feedback sensor array",
      "category": "sensors",
      "status": "active",
      "version": "v3.4"
    },
    {
      "id": "WRN-00002",
      "model": "WC-200",
      "name": "Titan Handler",
      "component": "thermal management unit",
      "category": "thermal",
      "status": "active",
      "version": "v2.1"
    }
    // ... more schematics
  ]
}
```

**Now try with a filter**:

1. In the `category` parameter field, enter: `sensors`
2. Click **Execute**

You should see only schematics with `category: "sensors"` in the results.

**Available filter values**:

- **category**: `sensors`, `power`, `control`, `thermal`, `actuators`, `manipulation`, `communication`
- **model**: `WC-100`, `WC-200`, `WC-300`, `WC-400`, `WC-500`, `WC-600`, `WC-700`
- **status**: `active`, `deprecated`, `draft`

### 3.2 Test `warn_get_robot`

This tool retrieves detailed information about a specific schematic.

**Steps**:

1. Select `warn_get_robot` from the tool list
2. In the `schematic_id` field, enter: `WRN-00001`
3. Click **Execute**

**Expected Response**:

```json
{
  "id": "WRN-00001",
  "model": "WC-100",
  "name": "Atlas Prime",
  "component": "force feedback sensor array",
  "version": "v3.4",
  "category": "sensors",
  "status": "active",
  "summary": "High-precision force sensing system for WC-100 manipulation tasks. Enables delicate object handling with 0.1N resolution.",
  "url": "https://schematics.warnerco.io/wc-100/force_feedback_sensor_v3_4.pdf",
  "tags": ["manipulation", "precision", "feedback"],
  "specifications": {
    "resolution": "0.1N",
    "range": "0-500N",
    "response_time": "2ms"
  },
  "last_verified": "2025-01-15"
}
```

**Test error handling**:

Try entering an invalid ID like `INVALID-ID`. You should receive:

```json
{
  "error": "Schematic INVALID-ID not found"
}
```

### 3.3 Test `warn_semantic_search`

This is the most powerful tool. It uses semantic search to find relevant schematics based on natural language queries.

**Steps**:

1. Select `warn_semantic_search` from the tool list
2. In the `query` field, enter: `welding capabilities`
3. Set `top_k` to: `5`
4. Click **Execute**

**Expected Response**:

```json
{
  "query": "welding capabilities",
  "intent": "search",
  "results": [
    {
      "id": "WRN-00012",
      "model": "WC-700",
      "name": "Vulcan Welder",
      "component": "arc welding control unit",
      "score": 0.89,
      "summary": "Precision arc welding controller for WC-700 fabrication robots..."
    }
    // ... more results ranked by relevance
  ],
  "total": 3,
  "reasoning": "Found schematics related to welding and fabrication capabilities",
  "query_time_ms": 145
}
```

**Try these sample queries**:

| Query | What It Finds |
|-------|--------------|
| `thermal sensors for heavy-duty robots` | Thermal management components |
| `battery and power management` | Power systems and battery schematics |
| `navigation and obstacle avoidance` | LIDAR, sensors for autonomous movement |
| `gripper for precision handling` | Manipulation and gripper assemblies |

### 3.4 Test `warn_memory_stats`

This tool returns statistics about the schematic memory system.

**Steps**:

1. Select `warn_memory_stats` from the tool list
2. No parameters are required
3. Click **Execute**

**Expected Response**:

```json
{
  "backend": "json",
  "total_schematics": 25,
  "indexed_count": 25,
  "chunk_count": 0,
  "categories": {
    "sensors": 5,
    "power": 4,
    "control": 4,
    "thermal": 3,
    "actuators": 3,
    "manipulation": 3,
    "communication": 3
  },
  "status_counts": {
    "active": 22,
    "deprecated": 2,
    "draft": 1
  },
  "last_update": "2025-01-21T10:30:00Z"
}
```

> **Note**: The `backend` value indicates which memory backend is active. Values can be `json`, `chroma`, or `azure_search` depending on your `.env` configuration.

---

## Step 4: Viewing MCP Resources

MCP Resources are read-only data endpoints that provide context to AI assistants. The WARNERCO Schematica server exposes two resources.

### 4.1 View `memory://overview`

**Steps**:

1. Click the **Resources** tab
2. Select `memory://overview` from the resource list
3. Click **Read** (or the resource will load automatically)

**Expected Content**:

```markdown
# WARNERCO Robotics Schematica Memory Overview

## Backend: json

### Statistics
- Total Schematics: 25
- Indexed for Search: 25
- Embedding Chunks: 0

### Categories
- actuators: 3
- communication: 3
- control: 4
- manipulation: 3
- power: 4
- sensors: 5
- thermal: 3

### Status Distribution
- active: 22
- deprecated: 2
- draft: 1

Last Updated: 2025-01-21T10:30:00Z
```

**Why this is useful**: AI assistants can read this resource to understand the scope and organization of available schematics before making tool calls.

### 4.2 View `memory://recent-queries`

**Steps**:

1. Select `memory://recent-queries` from the resource list
2. Click **Read**

**Expected Content** (after running some searches):

```markdown
# Recent Queries

## Query: welding capabilities
- Time: 2025-01-21T10:35:00Z
- Backend: json
- Duration: 145.2ms
- Results: 3 matches
- IDs: WRN-00012, WRN-00018, WRN-00024

## Query: thermal sensors for heavy-duty robots
- Time: 2025-01-21T10:33:00Z
- Backend: json
- Duration: 98.5ms
- Results: 4 matches
- IDs: WRN-00002, WRN-00015, WRN-00019, WRN-00022
```

> **Note**: If no queries have been run yet, this resource returns "No recent queries recorded."

---

## Step 5: Reading Request/Response JSON

Understanding the raw MCP protocol messages helps diagnose issues.

### Viewing Raw Requests

When you execute a tool, the Inspector shows:

1. **Request JSON**: The MCP `tools/call` request sent to the server
2. **Response JSON**: The server's response

**Example Request** (for `warn_get_robot`):

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "warn_get_robot",
    "arguments": {
      "schematic_id": "WRN-00001"
    }
  }
}
```

**Example Response**:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "{\"id\": \"WRN-00001\", ...}"
      }
    ]
  }
}
```

### Using the Notifications Tab

The **Notifications** tab shows server logs and stderr output. This is where you will see:

- Server startup messages
- Debug logging from your MCP server
- Error stack traces

Look for lines like:

```
[INFO] WARNERCO Schematica MCP server starting...
[DEBUG] Memory backend: json
[DEBUG] Loaded 25 schematics from data/schematics/schematics.json
```

---

## Step 6: Debugging Common Issues

### Issue: Connection Failed

**Symptoms**: Inspector shows "Disconnected" or connection error.

**Diagnosis**:

1. Check if the server process started (look for output in terminal)
2. Verify no port conflicts

**Solutions**:

```powershell
# Check if ports are in use
netstat -ano | findstr :6274
netstat -ano | findstr :6277

# Kill processes if needed
taskkill /PID <PID> /F

# Restart Inspector
npx @modelcontextprotocol/inspector uv run warnerco-mcp
```

### Issue: Tool Returns Empty Results

**Symptoms**: `warn_list_robots` returns `{"count": 0, "schematics": []}`.

**Diagnosis**:

1. Check if `schematics.json` exists and is valid
2. Verify the `MEMORY_BACKEND` environment variable

**Solutions**:

```powershell
# Verify schematics file exists
Test-Path C:\github\context-engineering\src\warnerco\backend\data\schematics\schematics.json

# Check file content (should be valid JSON array)
Get-Content C:\github\context-engineering\src\warnerco\backend\data\schematics\schematics.json | ConvertFrom-Json | Measure-Object
```

### Issue: Semantic Search Returns No Results

**Symptoms**: `warn_semantic_search` returns empty results even for valid queries.

**Possible Causes**:

1. **JSON backend limitation**: The JSON backend uses keyword matching, not true semantic search
2. **Chroma not indexed**: If using Chroma backend, vectors may not be indexed

**Solutions**:

```powershell
# Index schematics into Chroma for semantic search
cd C:\github\context-engineering\src\warnerco\backend
uv run python -c "from app.adapters.chroma_store import ChromaMemoryStore; import asyncio; asyncio.run(ChromaMemoryStore().index_all())"
```

### Issue: Timeout Errors

**Symptoms**: Requests hang or return timeout errors.

**Solutions**:

1. Click the **Configuration** button in Inspector
2. Increase `MCP_SERVER_REQUEST_TIMEOUT` (default: 10000ms)
3. Set `MCP_REQUEST_MAX_TOTAL_TIMEOUT` to a higher value (default: 60000ms)

### Issue: Import or Module Errors

**Symptoms**: Server fails to start with Python import errors.

**Solutions**:

```powershell
# Ensure you're in the correct directory
cd C:\github\context-engineering\src\warnerco\backend

# Reinstall dependencies
uv sync --force-reinstall

# Try running directly to see full error
uv run python -m app.mcp_stdio
```

---

## Step 7: Advanced Debugging with CLI Mode

MCP Inspector also supports a CLI mode for scripted testing. This is useful for CI/CD pipelines or automated debugging.

### List All Tools

```powershell
npx @modelcontextprotocol/inspector --cli uv run warnerco-mcp --method tools/list
```

### Call a Tool from CLI

```powershell
npx @modelcontextprotocol/inspector --cli uv run warnerco-mcp `
  --method tools/call `
  --tool-name warn_get_robot `
  --tool-arg schematic_id=WRN-00001
```

### List Resources from CLI

```powershell
npx @modelcontextprotocol/inspector --cli uv run warnerco-mcp --method resources/list
```

---

## Architecture Diagram

The following diagram shows how MCP Inspector connects to the WARNERCO Schematica server.

```
+-------------------+     HTTP      +-------------------+
|                   |  (port 6274)  |                   |
|  Your Browser     |<------------->|  MCP Inspector    |
|                   |               |  Client (MCPI)    |
+-------------------+               +-------------------+
                                            |
                                            | Internal
                                            v
                                    +-------------------+
                                    |                   |
                                    |  MCP Proxy        |
                                    |  (MCPP, port 6277)|
                                    |                   |
                                    +-------------------+
                                            |
                                            | stdio
                                            v
                                    +-------------------+
                                    |                   |
                                    |  warnerco-mcp     |
                                    |  (Python/FastMCP) |
                                    |                   |
                                    +-------------------+
                                            |
                                            v
                                    +-------------------+
                                    |                   |
                                    |  Memory Backend   |
                                    |  (JSON/Chroma/    |
                                    |   Azure Search)   |
                                    +-------------------+
```

---

## Quick Reference

### Tool Summary

| Tool | Purpose | Key Parameters |
|------|---------|----------------|
| `warn_list_robots` | List/filter schematics | `category`, `model`, `status`, `limit` |
| `warn_get_robot` | Get schematic details | `schematic_id` (required) |
| `warn_semantic_search` | Natural language search | `query` (required), `top_k`, `category`, `model` |
| `warn_memory_stats` | System statistics | None |

### Resource Summary

| Resource URI | Content |
|--------------|---------|
| `memory://overview` | System statistics in markdown format |
| `memory://recent-queries` | History of recent search queries |

### Keyboard Shortcuts

- **Ctrl+C** in terminal: Stop the Inspector and server
- **F5** in browser: Refresh the Inspector UI

---

## Next Steps

After completing this tutorial, you can:

1. **Configure Claude Desktop** to use WARNERCO Schematica - see `config/claude_desktop_config.json`
2. **Explore the source code** at `src/warnerco/backend/app/mcp_tools.py`
3. **Test with Chroma backend** for true semantic search capabilities
4. **Deploy to Azure** - see `.claude/skills/warnerco-schematica/references/azure-deployment.md`

---

## Additional Resources

- [MCP Inspector GitHub Repository](https://github.com/modelcontextprotocol/inspector)
- [MCP Inspector Official Documentation](https://modelcontextprotocol.io/docs/tools/inspector)
- [Model Context Protocol Specification](https://spec.modelcontextprotocol.io/)
- [FastMCP Documentation](https://github.com/jlowin/fastmcp)

---

## Troubleshooting FAQ

**Q: The browser does not open automatically. What URL should I use?**

A: Navigate to `http://localhost:6274` (or `http://localhost:5173` on older Inspector versions).

**Q: I see "command not found: npx" error. What do I do?**

A: Ensure Node.js is installed and in your PATH. Run `node --version` to verify. If needed, reinstall from [nodejs.org](https://nodejs.org/).

**Q: Can I test multiple MCP servers simultaneously?**

A: Yes, but each Inspector instance needs different ports. Use environment variables:

```powershell
$env:CLIENT_PORT = "8080"
$env:SERVER_PORT = "9000"
npx @modelcontextprotocol/inspector uv run warnerco-mcp
```

**Q: How do I see more detailed server logs?**

A: Set the `DEBUG` environment variable before starting:

```powershell
$env:DEBUG = "mcp:*"
npx @modelcontextprotocol/inspector uv run warnerco-mcp
```
