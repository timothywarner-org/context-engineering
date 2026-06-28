# WARNERCO Robotics Schematica

Agentic robot schematics system that exercises **all four CoALA memory tiers** (Working / Episodic / Semantic / Procedural) in one coherent app. Built on FastAPI + FastMCP + LangGraph with a 9-node hybrid RAG pipeline.

## Memory Architecture (CoALA Four-Tier)

```
+--------------------------------------------------------------------------+
|  Four CoALA Memory Tiers (Sumers et al. 2024)                            |
|  +------------+  +-----------+  +----------+  +------------------------+ |
|  | Working    |  | Episodic  |  | Semantic |  | Procedural             | |
|  | Scratchpad |  | events.db |  | Vector   |  | MCP Prompts (versioned)| |
|  | (SQLite)   |  | (SQLite)  |  | store    |  | catalog://procedural   | |
|  +------------+  +-----------+  +----------+  +------------------------+ |
+--------------------------------------------------------------------------+
|  Consolidation ("sleep cycle"): scratchpad+episodic --(ctx.sample)--> semantic |
+--------------------------------------------------------------------------+
```

The **semantic tier** is itself a 3-tier abstraction (JSON source-of-truth → Chroma local vectors → Azure AI Search enterprise). All semantic backends use JSON as the source of truth.

## Quick Start

### Prerequisites

- **Python 3.13** (pinned via `.python-version`). `onnxruntime` (a `chromadb` dependency) does not yet ship 3.14 wheels.

### Using uv (Recommended for Local Development)

```bash
cd src/warnerco/backend

# Create venv and install dependencies
uv sync

# Copy environment file and configure
cp .env.example .env

# Run HTTP server
uv run warnerco-serve

# Run MCP stdio server (for Claude Desktop)
uv run warnerco-mcp

# Free port 8000 and restart the HTTP server (cross-platform)
uv run warnerco-restart
```

### Using Poetry

```bash
cd src/warnerco/backend

# Install dependencies
poetry install

# With Azure support
poetry install --with azure

# Run HTTP server
poetry run warnerco-serve

# Run MCP stdio server
poetry run warnerco-mcp
```

## MCP Client Configuration

### Claude Desktop

Add to your Claude Desktop config:

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

Create `.vscode/mcp.json` in your workspace:

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

## Available MCP Tools

The server exposes **28 MCP tools** plus **12 resources** and **5 prompts**, organized by CoALA tier:

| Group | Tools |
|-------|-------|
| **Semantic memory (vector store)** | `warn_list_robots`, `warn_get_robot`, `warn_semantic_search`, `warn_memory_stats`, `warn_index_schematic`, `warn_compare_schematics`, `warn_create_schematic`, `warn_update_schematic`, `warn_delete_schematic`, `warn_explain_schematic` |
| **Interactive (Elicitation/Sampling)** | `warn_guided_search`, `warn_feedback_loop`, `warn_replacement_advisor` |
| **Knowledge graph** | `warn_add_relationship`, `warn_graph_neighbors`, `warn_graph_path`, `warn_graph_stats` |
| **Working memory (CoALA Tier 1 — scratchpad)** | `warn_scratchpad_write`, `warn_scratchpad_read`, `warn_scratchpad_clear`, `warn_scratchpad_stats` |
| **Episodic memory (CoALA Tier 2)** | `warn_episodic_log`, `warn_episodic_recall`, `warn_episodic_recent`, `warn_episodic_stats` |
| **Consolidation (sleep cycle)** | `warn_consolidate_memory` |
| **Tool discovery (progressive loading)** | `warn_search_tools`, `warn_describe_tool` |

### Resources

| URI | Purpose |
|-----|---------|
| `memory://overview` | Backend snapshot |
| `memory://recent-queries` | Telemetry of recent retrievals |
| `memory://architecture` | Static architecture explainer |
| `memory://coala-overview` | **Live four-tier CoALA snapshot** (the class-anchor resource) |
| `memory://procedural-catalog` | Versioned MCP prompts as procedural memory |
| `schematic://{id}` | Single schematic as Markdown |
| `catalog://categories`, `catalog://models` | Catalog enumerations |
| `help://tools`, `help://resources`, `help://prompts` | Self-documenting help |
| `mcp://capabilities` | Server capabilities introspection |

### Episodic recall (Park et al.)

`warn_episodic_recall` returns events scored by:

```
total = α_recency · 0.5^(hours_since / half_life)
      + α_importance · stored_importance
      + α_relevance · bag_of_words_cosine(query, summary+content)
```

The per-event score breakdown is exposed in the response so students can see why each memory surfaced. Defaults: `α_recency=0.4`, `α_importance=0.3`, `α_relevance=0.3`, `half_life_hours=24`. Override via `EPISODIC_*` env vars.

### Consolidation (sleep cycle)

`warn_consolidate_memory` uses **MCP Sampling** (`ctx.sample()`) to read recent scratchpad + episodic memory, extract durable facts, and write them as synthetic `Schematic` records into the vector store (tagged `category=consolidated_fact`, `model=MEMORY`, `id=FACT-*`). Logs an `OBSERVATION` back to episodic memory so consolidation itself becomes a memory.

**ADD-only**: no Mem0 AUDN-style dedup. Production agents would extend this with UPDATE/DELETE/NOOP semantics.

### Progressive Tool Loading

`warn_search_tools` and `warn_describe_tool` implement Anthropic's progressive tool-loading pattern: clients discover tools cheaply and fetch detail on demand. Both tools self-exclude from search results, so `count` is up to 26 even when `total` is 28.

```python
warn_search_tools(query="episodic", detail="summary")  # 95%+ token savings vs full schemas
warn_describe_tool(name="warn_consolidate_memory")     # full schema for one tool
```

Example calls:

```python
# 1. Cheap discovery: which tools handle the graph?
warn_search_tools(query="graph", detail="summary", limit=10)

# 2. Even cheaper: just the names
warn_search_tools(query="scratchpad", detail="name")

# 3. On-demand detail for a single tool
warn_describe_tool(name="warn_graph_path")
```

`warn_describe_tool` raises `ValueError` for unknown tool names.

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Health check |
| `/api/robots` | GET | List schematics |
| `/api/robots/{id}` | GET | Get schematic details |
| `/api/search` | POST | Semantic search |
| `/api/memory/stats` | GET | Memory statistics |
| `/docs` | GET | Swagger UI |

## Environment Variables

See `.env.example` for full documentation. Key variables:

| Variable | Description | Required |
|----------|-------------|----------|
| `MEMORY_BACKEND` | `json`, `chroma`, or `azure_search` | Yes |
| `AZURE_SEARCH_ENDPOINT` | AI Search endpoint | If using azure_search |
| `AZURE_SEARCH_KEY` | AI Search admin key | If using azure_search |
| `AZURE_OPENAI_ENDPOINT` | OpenAI endpoint | For LangGraph reasoning + sampling |
| `AZURE_OPENAI_API_KEY` | OpenAI key | For LangGraph reasoning + sampling |
| `SCRATCHPAD_DB_PATH` | Working-memory SQLite path | No (default `data/scratchpad/notes.db`) |
| `SCRATCHPAD_INJECT_BUDGET` | Tokens for LangGraph scratchpad injection | No (default 1500) |
| `EPISODIC_DB_PATH` | Episodic events SQLite path | No (default `data/episodic/events.db`) |
| `EPISODIC_MAX_RETRIEVAL_K` | Top-k for episodic recall | No (default 5) |
| `EPISODIC_RECENCY_HALF_LIFE_HOURS` | Park et al. half-life | No (default 24.0) |
| `EPISODIC_WEIGHT_RECENCY` | α_recency | No (default 0.4) |
| `EPISODIC_WEIGHT_IMPORTANCE` | α_importance | No (default 0.3) |
| `EPISODIC_WEIGHT_RELEVANCE` | α_relevance | No (default 0.3) |

## Development

```bash
# Run with hot reload
uv run uvicorn app.main:app --reload

# Run tests
uv run pytest

# Lint
uv run ruff check .

# Format
uv run ruff format .
```

### Restarting the HTTP server

`warnerco-restart` (source: `scripts/restart_server.py`) is a cross-platform helper that frees a port and relaunches the HTTP server. It refuses to kill its own PID.

```bash
# Free port 8000 (or $PORT) and relaunch warnerco-serve
uv run warnerco-restart

# Use a custom port
uv run warnerco-restart --port 8080

# Free the port without relaunching
uv run warnerco-restart --kill-only
uv run warnerco-restart --no-start
```

Implementation: Windows uses `netstat -ano` plus `taskkill /F /T /PID`; POSIX uses `lsof -t` plus `SIGKILL`. Exits `0` if the port was freed, `1` otherwise.

### Knowledge Graph

The graph database lives at `data/graph/knowledge.db` and is populated by:

```bash
uv run python scripts/index_graph.py
```

Current contents: **117 entities** (25 schematic, 12 category, 12 component, 9 model, 56 tag, 3 status) and **221 relationships** (`has_tag`: 75, `compatible_with`: 50, `belongs_to_model`: 25, `has_category`: 25, `has_status`: 25, `contains`: 21).

## Docker

```bash
# Build
docker build -t warnerco-schematica .

# Run
docker run -p 8000:8000 -e MEMORY_BACKEND=chroma warnerco-schematica
```

## Azure Deployment

The infrastructure is deployed to Azure with:
- **Container App**: warnerco-schematica-classroom
- **API Management**: warnerco-apim (Basic tier)
- **AI Search**: warnerco-search (Free tier)
- **Azure OpenAI**: warnerco-openai (text-embedding-ada-002)

Access via APIM: `https://warnerco-apim.azure-api.net/api/*`
