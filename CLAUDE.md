# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Training materials and MCP server implementations for "Context Engineering with MCP" - a course teaching production MCP (Model Context Protocol) deployment. The flagship teaching application is WARNERCO Schematica, a FastAPI + FastMCP + LangGraph application demonstrating hybrid RAG with vector and graph memory.

## Repository Structure

```
context-engineering/
├── src/warnerco/backend/          # WARNERCO Schematica - Primary Teaching App
│   ├── app/                       # FastAPI + FastMCP + LangGraph
│   │   ├── adapters/              # Memory backends (JSON, Chroma, Azure, Graph)
│   │   ├── langgraph/             # 6-node hybrid RAG pipeline
│   │   ├── models/                # Pydantic models
│   │   ├── main.py                # FastAPI application
│   │   └── mcp_tools.py           # FastMCP tool definitions
│   ├── data/                      # JSON schematics + vector stores
│   ├── scripts/                   # Indexing utilities
│   ├── static/                    # SPA dashboards
│   └── tests/                     # Test suite
├── labs/lab-01-hello-mcp/         # Hands-on exercises (starter + solution)
├── docs/                          # Student materials and tutorials
│   ├── diagrams/                  # Architecture diagrams (SVG + Mermaid)
│   ├── tutorials/                 # Step-by-step tutorials
│   └── api/                       # API reference docs
├── config/                        # Sample MCP client configs
├── diagrams/                      # High-level architecture (Mermaid)
├── instructor/                    # Instructor materials
├── .claude/agents/                # Claude Code agents
└── .claude/skills/                # Claude Code skills
```

## Development Commands

### WARNERCO Schematica (FastAPI + FastMCP + LangGraph)

```bash
cd src/warnerco/backend
uv sync                                    # Install dependencies
uv run uvicorn app.main:app --reload       # Start server (http://localhost:8000)
uv run warnerco-mcp                        # MCP stdio server (for Claude Desktop)
```

**Memory Backends** (set `MEMORY_BACKEND` in `.env`):
- `json` - Fastest startup, keyword search (default)
- `chroma` - Local semantic search (recommended for dev)
- `azure_search` - Enterprise deployment

**Index Schematics**:
```bash
# Chroma (local vectors)
uv run python -c "from app.adapters.chroma_store import ChromaMemoryStore; import asyncio; asyncio.run(ChromaMemoryStore().index_all())"

# Azure AI Search (enterprise vectors)
uv run python scripts/index_azure_search.py

# Graph Memory (knowledge graph)
uv run python scripts/index_graph.py
```

### Lab 01 - Hello MCP (Beginner Entry Point)

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
console.error('Tool called:', toolName);  // Goes to stderr
```

### Resource URIs
Resources use URI scheme: `memory://overview`, `memory://context-stream`

## Key Files

### WARNERCO Schematica
- `src/warnerco/backend/app/main.py` - FastAPI application
- `src/warnerco/backend/app/mcp_tools.py` - FastMCP tool definitions (all MCP primitives)
- `src/warnerco/backend/app/langgraph/flow.py` - 6-node hybrid RAG orchestration
- `src/warnerco/backend/app/adapters/` - Memory backends (JSON, Chroma, Azure, Graph)
- `src/warnerco/backend/app/models/graph.py` - Entity and Relationship models
- `src/warnerco/backend/app/adapters/graph_store.py` - SQLite + NetworkX graph store
- `src/warnerco/backend/data/schematics/schematics.json` - Source of truth (25 robot schematics)
- `src/warnerco/backend/scripts/index_graph.py` - Graph indexing script

### Lab 01
- `labs/lab-01-hello-mcp/starter/src/index.js` - Starting point for students
- `labs/lab-01-hello-mcp/solution/src/index.js` - Completed solution

### Configuration
- `config/claude_desktop_config.json` - Sample Claude Desktop configuration

## MCP Client Configuration

### Claude Desktop
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
**Mac**: `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "warnerco": {
      "command": "uv",
      "args": ["run", "warnerco-mcp"],
      "cwd": "C:/github/context-engineering/src/warnerco/backend"
    }
  }
}
```

### VS Code
Create `.vscode/mcp.json` in workspace:
```json
{
  "mcpServers": {
    "warnerco": {
      "command": "uv",
      "args": ["run", "warnerco-mcp"],
      "cwd": "${workspaceFolder}/src/warnerco/backend"
    }
  }
}
```

## Testing with MCP Inspector

Primary debugging tool - opens web UI to call tools and view resources:
```bash
npx @modelcontextprotocol/inspector uv run warnerco-mcp
# Opens http://localhost:5173
```

## Environment Variables

Set in `src/warnerco/backend/.env`:

```bash
# Memory backend selection
MEMORY_BACKEND=json  # json, chroma, or azure_search

# Azure AI Search (production)
AZURE_SEARCH_ENDPOINT=https://your-search.search.windows.net
AZURE_SEARCH_KEY=<from-portal>
AZURE_SEARCH_INDEX=warnerco-schematics

# Azure OpenAI (for embeddings and reasoning)
AZURE_OPENAI_ENDPOINT=https://your-openai.openai.azure.com/
AZURE_OPENAI_API_KEY=<from-portal>
AZURE_OPENAI_DEPLOYMENT=gpt-4o-mini
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-ada-002
```

## WARNERCO Schematica Architecture

```
+---------------------------------------------------------------+
|                     FastAPI + FastMCP                         |
+---------------------------------------------------------------+
|  LangGraph Flow (6-node Hybrid RAG)                           |
|  parse_intent -> query_graph -> retrieve -> compress -> reason -> respond |
+---------------------------------------------------------------+
|  Hybrid Memory Layer                                          |
|  +--------------------------+  +--------------------------+   |
|  | Vector Store             |  | Graph Store              |   |
|  | JSON -> Chroma ->        |  | SQLite + NetworkX        |   |
|  | Azure AI Search          |  | (Knowledge Graph)        |   |
|  +--------------------------+  +--------------------------+   |
+---------------------------------------------------------------+
```

**MCP Tools**: `warn_list_robots`, `warn_get_robot`, `warn_semantic_search`, `warn_memory_stats`, `warn_add_relationship`, `warn_graph_neighbors`, `warn_graph_path`, `warn_graph_stats`

**API Endpoints**:
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/robots` | List schematics |
| GET | `/api/robots/{id}` | Get by ID |
| POST | `/api/search` | Semantic search |
| GET | `/api/memory/stats` | Backend stats |
| GET | `/docs` | OpenAPI docs |
| GET | `/api/graph/stats` | Graph statistics |
| GET | `/api/graph/neighbors/{id}` | Entity neighbors |

### Graph Memory (Knowledge Graph Layer)

WARNERCO Schematica includes a Graph Memory layer demonstrating hybrid RAG architectures. It runs alongside the vector store to enable relationship-based queries.

**Why Graph Memory?** Vector search finds *similar* things; graph queries find *connected* things. Use both for comprehensive retrieval.

**Components**:

| File | Purpose |
|------|---------|
| `app/models/graph.py` | Entity and Relationship Pydantic models |
| `app/adapters/graph_store.py` | SQLite persistence + NetworkX traversal |
| `scripts/index_graph.py` | Populate graph from schematics.json |
| `data/graph.db` | SQLite database (created by indexing) |

**MCP Graph Tools**:

| Tool | Description |
|------|-------------|
| `warn_add_relationship` | Create triplet (subject, predicate, object) |
| `warn_graph_neighbors` | Get connected entities (in/out/both) |
| `warn_graph_path` | Find shortest path between entities |
| `warn_graph_stats` | Node count, edge count, density |

**Supported Predicates**: `depends_on`, `contains`, `has_status`, `manufactured_by`, `compatible_with`, `related_to`

**Index the Graph**:

```bash
cd src/warnerco/backend
uv run python scripts/index_graph.py
```

**LangGraph Integration**: The `query_graph` node (Node 2 in the pipeline) enriches retrieval context with graph relationships before vector search. It activates for DIAGNOSTIC and ANALYTICS intents, or when queries mention explicit relationships.

**Documentation**:
- [Graph Memory Architecture](docs/diagrams/graph-memory-architecture.md) - Technical design
- [Graph Memory Tutorial](docs/tutorials/graph-memory-tutorial.md) - Hands-on walkthrough
- [Graph API Reference](docs/api/graph-api.md) - Complete tool documentation

## Claude Code Agents and Skills

This repo includes Claude Code agents (`.claude/agents/`) and skills (`.claude/skills/`):

**Agents**:
- `python-mcp-server-expert` - FastMCP development guidance
- `azure-principal-architect` - Azure WAF assessments

**Skills**:
- `mcp-server-builder` - Build MCP servers in Python/JS/TS
- `warnerco-schematica` - WARNERCO Robotics Schematica development

## MCP Resources

- **MCP Specification**: https://spec.modelcontextprotocol.io/
- **TypeScript SDK**: `@modelcontextprotocol/sdk` (npm)
- **Python SDK**: `mcp` (pip) or `fastmcp` (pip)
- **MCP Inspector**: `@modelcontextprotocol/inspector`
