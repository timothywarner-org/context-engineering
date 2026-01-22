# Testing WARNERCO Schematica MCP Agent in VS Code with GitHub Copilot

This tutorial walks you through connecting the WARNERCO Schematica MCP server to GitHub Copilot in VS Code on Windows 11. By the end, you will be able to query robot schematics data directly from Copilot Chat.

## What You Will Learn

- Configure VS Code to recognize an MCP server
- Start and verify the WARNERCO Schematica server connection
- Use natural language prompts in Copilot Chat to invoke MCP tools
- Interpret the results and troubleshoot common issues

## Prerequisites

Before starting, ensure you have the following installed and configured.

### Required Software

| Software | Minimum Version | Verification Command |
|----------|-----------------|----------------------|
| VS Code | 1.96+ | `code --version` |
| GitHub Copilot Extension | Latest | Check Extensions panel |
| Python | 3.11+ | `python --version` |
| uv (Python package manager) | 0.4+ | `uv --version` |

### Install uv (if not already installed)

Open PowerShell and run:

```powershell
irm https://astral.sh/uv/install.ps1 | iex
```

Restart your terminal after installation. Verify with `uv --version`.

### GitHub Copilot Requirements

You must have an active GitHub Copilot subscription (Individual, Business, or Enterprise). The MCP integration is available in GitHub Copilot Chat.

> **Note**: MCP support in VS Code requires the GitHub Copilot extension version that supports agent mode. Ensure your extension is up to date.

## Step 1: Verify the MCP Configuration File

The repository includes a pre-configured MCP settings file at `.vscode/mcp.json`. Let me walk you through what it contains.

Open the file at `C:\github\context-engineering\.vscode\mcp.json`:

```json
{
  "mcpServers": {
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

**Configuration breakdown:**

| Field | Value | Purpose |
|-------|-------|---------|
| `command` | `uv` | The Python package manager that runs the server |
| `args` | `["run", "warnerco-mcp"]` | Executes the `warnerco-mcp` entry point |
| `cwd` | `${workspaceFolder}/src/warnerco/backend` | Working directory for the server |
| `env.MEMORY_BACKEND` | `chroma` | Uses ChromaDB for local vector search |

**Why ChromaDB?** The Chroma memory backend provides semantic search capabilities locally without requiring Azure credentials. It automatically indexes the 25 robot schematics into vector embeddings for natural language queries.

## Step 2: Install Python Dependencies

Before the MCP server can start, you must install its dependencies.

Open a terminal and navigate to the backend directory:

```powershell
cd C:\github\context-engineering\src\warnerco\backend
uv sync
```

This command installs all dependencies specified in `pyproject.toml`, including FastMCP, LangGraph, and ChromaDB.

**Expected output:**

```
Resolved 45 packages in 2.5s
Installed 45 packages in 1.2s
```

## Step 3: Start VS Code from the Repository Root

**This step is critical.** VS Code must be opened from the repository root for the `${workspaceFolder}` variable in `mcp.json` to resolve correctly.

Open PowerShell and run:

```powershell
cd C:\github\context-engineering
code .
```

Alternatively, if VS Code is already open:

1. Press `Ctrl+K Ctrl+O` to open a folder
2. Navigate to `C:\github\context-engineering`
3. Click **Select Folder**

## Step 4: Open the MCP Panel in VS Code

VS Code provides an MCP panel to manage server connections.

### Finding the MCP Panel

1. Press `Ctrl+Shift+P` to open the Command Palette
2. Type `MCP` and look for one of these commands:
   - **MCP: List Servers** - Shows configured MCP servers
   - **MCP: Start Server** - Manually starts a server
   - **MCP: Show Output** - Displays server logs

Alternatively, you can access MCP settings through:

1. Open **Settings** (`Ctrl+,`)
2. Search for `mcp`
3. Look for **GitHub Copilot** > **MCP** settings

### Starting the Server

The server should start automatically when you open Copilot Chat and reference MCP tools. However, you can manually start it:

1. Press `Ctrl+Shift+P`
2. Type `MCP: Start Server`
3. Select `warnerco-schematica`

## Step 5: Verify the Server Connection

Once the server starts, verify the connection is healthy.

### Check Server Status

1. Press `Ctrl+Shift+P`
2. Type `MCP: List Servers`
3. Look for `warnerco-schematica` with a green status indicator

### View Server Logs

1. Press `Ctrl+Shift+P`
2. Type `MCP: Show Output`
3. Select `warnerco-schematica`

**Expected log output on successful startup:**

```
Starting WARNERCO Schematica MCP server...
Memory backend: chroma
Loaded 25 schematics
ChromaDB collection initialized
MCP server ready
```

### First-Time ChromaDB Indexing

The first time the server starts with ChromaDB, it indexes all 25 schematics into vector embeddings. This may take 30-60 seconds and requires an internet connection for the embedding model.

## Step 6: Test Prompts in Copilot Chat

Open GitHub Copilot Chat by pressing `Ctrl+Alt+I` or clicking the Copilot icon in the sidebar.

### Available MCP Tools

The WARNERCO Schematica server exposes four tools:

| Tool | Purpose | Example Use |
|------|---------|-------------|
| `warn_list_robots` | List schematics with optional filters | Browse by model or category |
| `warn_get_robot` | Get detailed schematic by ID | Look up specific part numbers |
| `warn_semantic_search` | Natural language search | Find components by description |
| `warn_memory_stats` | System statistics | Check index health |

### Test Prompt 1: List All Robots

Type in Copilot Chat:

```
List all available robots in the WARNERCO system
```

**Expected behavior:** Copilot invokes `warn_list_robots` and returns a table of all 25 schematics showing ID, model, name, component, and status.

**Sample response:**

```
The WARNERCO system contains 25 robot schematics:

| ID | Model | Name | Component |
|----|-------|------|-----------|
| WRN-00001 | WC-100 | Atlas Prime | force feedback sensor array |
| WRN-00002 | WC-200 | Titan Handler | thermal management unit |
| WRN-00003 | WC-300 | Nimbus Scout | battery management system |
...
```

### Test Prompt 2: Search for Welding Robots

Type in Copilot Chat:

```
Search for welding robots in the schematics database
```

**Expected behavior:** Copilot invokes `warn_semantic_search` with a query about welding. The semantic search understands context and returns relevant results even if "welding" is not an exact keyword match.

**Sample response:**

```
Found 3 schematics related to welding:

1. WRN-00011 - WC-700 Vulcan Welder - arc welding head assembly
   Precision welding system supporting MIG, TIG, and spot welding

2. WRN-00015 - WC-700 Vulcan Welder - fume extraction system
   Integrated fume removal for welding operations

3. WRN-00023 - WC-700 Vulcan Welder - wire feed mechanism
   Precision wire feeding for MIG welding operations
```

### Test Prompt 3: Get Details About a Specific Robot

Type in Copilot Chat:

```
Get details about the WC-700 Vulcan Welder arc welding head
```

**Expected behavior:** Copilot invokes `warn_get_robot` with schematic ID `WRN-00011` and returns full specifications.

**Sample response:**

```
WC-700 Vulcan Welder - Arc Welding Head Assembly (WRN-00011)

Version: v1.5
Category: tooling
Status: active

Summary: Precision welding system for WC-700 manufacturing robots.
Supports MIG, TIG, and spot welding with adaptive seam tracking.

Specifications:
- Current range: 5-500A
- Wire feed: 2-20 m/min
- Accuracy: 0.1mm

Tags: welding, manufacturing, precision
Last verified: 2024-12-20
```

### Test Prompt 4: Memory Statistics

Type in Copilot Chat:

```
What are the memory statistics for the schematic system?
```

**Expected behavior:** Copilot invokes `warn_memory_stats` and returns backend health information.

**Sample response:**

```
WARNERCO Schematica Memory Statistics:

Backend: chroma
Total schematics: 25
Indexed for search: 25
Embedding chunks: 25

Categories:
- actuators: 1
- communication: 1
- control: 2
- environmental: 1
- manipulation: 1
- mechanical: 3
- power: 1
- safety: 2
- sensors: 8
- structural: 2
- thermal: 1
- tooling: 2

Status distribution:
- active: 23
- deprecated: 1
- draft: 1
```

### Advanced Test Prompts

Try these prompts to explore the full capabilities:

```
Find robots with thermal sensors
```

```
List all WC-100 Atlas Prime components
```

```
Search for heavy-duty industrial robots with safety features
```

```
Which robots have deprecated components?
```

```
Find precision manipulation systems with sub-millimeter accuracy
```

## Step 7: Troubleshooting Common Issues

### Server Fails to Start

**Symptom:** MCP panel shows `warnerco-schematica` as disconnected or errored.

**Check 1: Verify uv is in PATH**

```powershell
uv --version
```

If not found, restart VS Code after installing uv.

**Check 2: Verify dependencies are installed**

```powershell
cd C:\github\context-engineering\src\warnerco\backend
uv sync
```

**Check 3: Test the server manually**

```powershell
cd C:\github\context-engineering\src\warnerco\backend
uv run warnerco-mcp
```

The server should start and wait for MCP protocol messages on stdin. Press `Ctrl+C` to stop.

### ChromaDB Indexing Errors

**Symptom:** Server starts but searches return no results.

**Solution:** Re-index the ChromaDB collection:

```powershell
cd C:\github\context-engineering\src\warnerco\backend
uv run python -c "from app.adapters.chroma_store import ChromaMemoryStore; import asyncio; asyncio.run(ChromaMemoryStore().index_all())"
```

### Copilot Does Not Invoke MCP Tools

**Symptom:** Copilot responds but does not use the WARNERCO tools.

**Check 1: Verify MCP is enabled in Copilot settings**

1. Open Settings (`Ctrl+,`)
2. Search for `copilot mcp`
3. Ensure MCP integration is enabled

**Check 2: Be explicit about using the tool**

```
Use the warnerco-schematica MCP server to list all robots
```

**Check 3: Restart VS Code**

Sometimes the MCP connection requires a full restart to initialize.

### Permission Denied Errors

**Symptom:** Server fails with file access errors.

**Solution:** Ensure the ChromaDB data directory is writable:

```powershell
$chromaPath = "C:\github\context-engineering\src\warnerco\backend\data\chroma"
if (Test-Path $chromaPath) {
    Get-Acl $chromaPath
}
```

### Port Conflicts

**Symptom:** Server fails to bind to a port.

The MCP server uses stdio transport, not HTTP, so port conflicts are unlikely. If you see port-related errors, they may be from a previous debug session.

**Solution:** Kill orphaned Python processes:

```powershell
Get-Process python* | Stop-Process -Force
```

## Understanding the Architecture

The WARNERCO Schematica system uses a three-tier architecture:

```
+-------------------+     +-------------------+     +-------------------+
|   VS Code +       |     |   FastMCP         |     |   ChromaDB        |
|   GitHub Copilot  | --> |   MCP Server      | --> |   Vector Store    |
|   (MCP Client)    |     |   (stdio)         |     |   (Local)         |
+-------------------+     +-------------------+     +-------------------+
                                    |
                                    v
                          +-------------------+
                          |   LangGraph       |
                          |   RAG Pipeline    |
                          +-------------------+
```

**Data flow for a semantic search:**

1. You type a natural language query in Copilot Chat
2. Copilot sends an MCP `tool/call` request via stdio
3. FastMCP routes to `warn_semantic_search`
4. LangGraph orchestrates a 5-node RAG pipeline:
   - Parse intent
   - Retrieve from ChromaDB
   - Compress context
   - Reason about results
   - Format response
5. Results return through MCP protocol to Copilot Chat

## Robot Models Reference

The schematics database contains components for these robot models:

| Model | Name | Primary Application |
|-------|------|---------------------|
| WC-100 | Atlas Prime | Precision manipulation |
| WC-200 | Titan Handler | Heavy-duty industrial |
| WC-300 | Nimbus Scout | Mobile reconnaissance |
| WC-400 | Aegis Guardian | Security operations |
| WC-500 | Hercules Lifter | Heavy lifting |
| WC-600 | Mercury Courier | Autonomous delivery |
| WC-700 | Vulcan Welder | Manufacturing/welding |
| WC-800 | Phoenix Inspector | Industrial inspection |
| WC-900 | Orion Assembler | Assembly operations |

## Next Steps

After completing this tutorial, try these advanced scenarios:

1. **Filter by category**: Ask Copilot to "list all sensor components"
2. **Filter by status**: Ask about "deprecated schematics that need updates"
3. **Cross-model queries**: Ask "which robots share similar thermal management systems"
4. **Specification lookups**: Ask "find components with response times under 10ms"

## Additional Resources

- [MCP Specification](https://spec.modelcontextprotocol.io/) - Protocol documentation
- [FastMCP Documentation](https://gofastmcp.com/) - Python MCP framework
- [GitHub Copilot Documentation](https://docs.github.com/en/copilot) - Copilot features and settings
- [ChromaDB Documentation](https://docs.trychroma.com/) - Vector database reference

---

**Tutorial Version**: 1.0
**Last Updated**: 2025-01-21
**Author**: Tim Warner ([@timothywarner](https://github.com/timothywarner))
