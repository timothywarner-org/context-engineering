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
├── src/warnerco/backend/          # WARNERCO Schematica - Agentic RAG application
│   ├── app/                       # FastAPI + FastMCP + LangGraph
│   ├── data/                      # JSON schematics + Chroma vectors
│   ├── static/dash/               # SPA dashboards
│   └── scripts/                   # Indexing utilities
├── examples/filesystem-mcp/        # Reference implementation
├── labs/lab-01-hello-mcp/         # Hands-on exercises (starter + solution)
├── config/                         # Sample MCP client configs
├── docs/diagrams/                  # Architecture diagrams (Mermaid SVG)
├── .claude/agents/                 # Claude Code agents
└── .claude/skills/                 # Claude Code skills
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

### MCP Teaching Servers
- `mcp-servers/coretext-mcp/src/index.js` - Complete single-file MCP server (intentional for teaching)
- `mcp-servers/stoic-mcp/local/src/index.ts` - TypeScript MCP server entry
- `mcp-servers/stoic-mcp/local/src/storage.ts` - JSON persistence layer

### WARNERCO Schematica
- `src/warnerco/backend/app/main.py` - FastAPI application
- `src/warnerco/backend/app/mcp_tools.py` - FastMCP tool definitions (including graph tools)
- `src/warnerco/backend/app/langgraph/flow.py` - 6-node hybrid RAG orchestration
- `src/warnerco/backend/app/adapters/` - Memory backends (JSON, Chroma, Azure, Graph)
- `src/warnerco/backend/app/models/graph.py` - Entity and Relationship models
- `src/warnerco/backend/app/adapters/graph_store.py` - SQLite + NetworkX graph store
- `src/warnerco/backend/data/schematics/schematics.json` - Source of truth (25 robot schematics)
- `src/warnerco/backend/scripts/index_graph.py` - Graph indexing script

### Configuration
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

### MCP Teaching Servers

Both coretext-mcp and stoic-mcp have Azure deployment scripts:

```bash
cd mcp-servers/coretext-mcp/azure
./deploy.sh   # Deploys Container Apps + Cosmos DB + Key Vault

cd mcp-servers/stoic-mcp/azure
./deploy.sh
```

Infrastructure: Bicep templates in `azure/main.bicep`, parameters in `azure/parameters.json`

### WARNERCO Schematica (Azure)

```
warnerco-rg/
├── warnerco-app (Container App)     # FastAPI + FastMCP server
├── warnerco-apim (API Management)   # Proxy to Container App
├── warnerco-search (AI Search)      # Schematic vectors (25 docs indexed)
├── warnerco-openai (Azure OpenAI)   # gpt-4o-mini + text-embedding-ada-002
└── warnercostorage (Storage)        # Blob containers
```

**Environment Variables** (production):
```bash
MEMORY_BACKEND=azure_search
AZURE_SEARCH_ENDPOINT=https://warnerco-search.search.windows.net
AZURE_SEARCH_KEY=<from-portal>
AZURE_SEARCH_INDEX=warnerco-schematics
AZURE_OPENAI_ENDPOINT=https://warnerco-openai.openai.azure.com/
AZURE_OPENAI_API_KEY=<from-portal>
AZURE_OPENAI_DEPLOYMENT=gpt-4o-mini
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-ada-002
```

See `.claude/skills/warnerco-schematica/references/azure-deployment.md` for full deployment guide.

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

## WARNERCO Schematica Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     FastAPI + FastMCP                       │
├─────────────────────────────────────────────────────────────┤
│  LangGraph Flow (6-node Hybrid RAG)                         │
│  parse_intent → query_graph → retrieve → compress → reason → respond │
├─────────────────────────────────────────────────────────────┤
│  Hybrid Memory Layer                                        │
│  ┌─────────────────────┐  ┌─────────────────────┐          │
│  │ Vector Store        │  │ Graph Store         │          │
│  │ JSON → Chroma →     │  │ SQLite + NetworkX   │          │
│  │ Azure AI Search     │  │ (Knowledge Graph)   │          │
│  └─────────────────────┘  └─────────────────────┘          │
└─────────────────────────────────────────────────────────────┘
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

WARNERCO Schematica includes an optional Graph Memory layer demonstrating hybrid RAG architectures. It runs alongside the vector store to enable relationship-based queries.

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
- **Python SDK**: `mcp` (pip)
- **MCP Inspector**: `@modelcontextprotocol/inspector`
