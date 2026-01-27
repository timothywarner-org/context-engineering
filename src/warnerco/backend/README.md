# WARNERCO Robotics Schematica

Agentic robot schematics system with semantic memory. Features LangGraph orchestration, FastMCP tools, and a 3-tier data store architecture.

## Data Store Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Memory Abstraction Layer                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────────────┐ │
│  │    JSON     │    │   Chroma    │    │   Azure AI Search   │ │
│  │   (source   │───▶│  (vectors)  │    │   (enterprise)      │ │
│  │   of truth) │    │   local     │    │   cloud             │ │
│  └─────────────┘    └─────────────┘    └─────────────────────┘ │
│         │                  │                     │              │
│         └──────────────────┴─────────────────────┘              │
│                            │                                     │
│                    All backends use JSON                         │
│                    as the source of truth                        │
└─────────────────────────────────────────────────────────────────┘
```

## Quick Start

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

| Tool | Description |
|------|-------------|
| `warn_list_robots` | List robot schematics with optional filtering |
| `warn_get_robot` | Get detailed information about a specific schematic |
| `warn_semantic_search` | Search schematics using natural language |
| `warn_memory_stats` | Get statistics about the memory system |
| `warn_add_relationship` | Create graph triplet (subject, predicate, object) |
| `warn_graph_neighbors` | Get connected entities from knowledge graph |
| `warn_graph_path` | Find shortest path between entities |
| `warn_graph_stats` | Graph node/edge/density statistics |
| `warn_scratchpad_write` | Store session observation with optional minimization |
| `warn_scratchpad_read` | Retrieve session entries with filtering |
| `warn_scratchpad_clear` | Clear session entries by subject or age |
| `warn_scratchpad_stats` | Token budget and savings statistics |

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
| `AZURE_OPENAI_ENDPOINT` | OpenAI endpoint | For LangGraph reasoning |
| `AZURE_OPENAI_API_KEY` | OpenAI key | For LangGraph reasoning |

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
