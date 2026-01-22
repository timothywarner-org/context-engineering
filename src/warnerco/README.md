# WARNERCO Robotics Schematica

Agentic robot schematics system with semantic memory. A classroom prototype demonstrating Azure best practices for production MCP deployment.

## Architecture Overview

```
                    +------------------+
                    |   Astro Static   |
                    |   Dashboards     |
                    +--------+---------+
                             |
                    +--------v---------+
                    |    FastAPI +     |
                    |    FastMCP       |
                    +--------+---------+
                             |
              +--------------+--------------+
              |              |              |
      +-------v------+ +-----v------+ +----v------+
      |  LangGraph   | |   REST     | |   MCP     |
      |  Orchestr.   | |   APIs     | |   Tools   |
      +--------------+ +------------+ +-----------+
              |
      +-------v-----------------+
      |   Memory Abstraction    |
      +-------------------------+
      |  JSON  | Chroma | Azure |
      +--------+--------+-------+
```

## Quick Start

### Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) (recommended) or Poetry
- Node.js 18+ (for dashboard builds)
- Azure CLI (for deployment)

### Local Development

```bash
cd src/warnerco/backend
uv sync                                    # Install dependencies
uv run uvicorn app.main:app --reload       # Start server (http://localhost:8000)
```

The server starts at:
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Dashboard**: http://localhost:8000/dash/
- **MCP Endpoint**: http://localhost:8000/mcp

### Using Scripts

**Windows (PowerShell):**
```powershell
cd src\warnerco\scripts
.\run-local.ps1
```

**macOS/Linux:**
```bash
cd src/warnerco/scripts
chmod +x *.sh
./run-local.sh
```

### Build Dashboards

```bash
# From src/warnerco/dashboards
npm install
npm run build
```

Or use the script:
```powershell
.\run-local.ps1 -BuildDash
```

## Project Structure

```
src/warnerco/
├── backend/                    # Python FastAPI/FastMCP server
│   ├── app/
│   │   ├── api/               # REST API routes
│   │   ├── adapters/          # Memory backend implementations
│   │   ├── langgraph/         # LangGraph orchestration flow
│   │   ├── models/            # Pydantic data models
│   │   ├── config.py          # Settings management
│   │   ├── main.py            # FastAPI application
│   │   └── mcp_tools.py       # FastMCP tool definitions
│   ├── data/
│   │   ├── schematics/        # JSON source of truth (25 robot schematics)
│   │   └── chroma/            # Local vector database
│   ├── static/
│   │   ├── assets/            # Logo, favicon, robot icons
│   │   └── dash/              # Built Astro dashboard (output)
│   ├── scripts/               # Indexing utilities
│   ├── pyproject.toml         # uv/Poetry dependencies
│   └── .env.example           # Environment template
├── dashboards/                 # Astro static site project
│   ├── src/
│   │   ├── layouts/           # Page layouts
│   │   ├── components/        # UI components
│   │   ├── pages/             # Dashboard pages
│   │   └── styles/            # Global CSS
│   ├── astro.config.mjs       # Astro configuration
│   └── package.json
├── infra/
│   └── bicep/                 # Azure IaC templates
│       ├── main.bicep
│       ├── parameters.json
│       └── modules/
└── scripts/                    # Build and deploy scripts
```

## API Endpoints

### REST API (`/api`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check with backend status |
| GET | `/api/robots` | List schematics (with filters) |
| GET | `/api/robots/{id}` | Get schematic by ID |
| POST | `/api/robots/{id}/index` | Index schematic for search |
| POST | `/api/robots/index-all` | Index all schematics |
| POST | `/api/search` | Semantic search |
| GET | `/api/memory/stats` | Memory backend statistics |
| GET | `/api/memory/hits` | Recent query telemetry |
| GET | `/api/categories` | List categories |
| GET | `/api/models` | List robot models |

### MCP Tools (`/mcp`)

| Tool | Description |
|------|-------------|
| `warn_list_robots` | List schematics with filtering |
| `warn_get_robot` | Get schematic details |
| `warn_semantic_search` | Natural language search |
| `warn_memory_stats` | Memory statistics |

### MCP Resources

| URI | Description |
|-----|-------------|
| `memory://overview` | Memory system overview |
| `memory://recent-queries` | Recent search queries |

## Memory Backends

Set via `MEMORY_BACKEND` environment variable:

### `json` (Default - fastest startup)
- Reads/writes JSON files directly
- Keyword-based search fallback
- No external dependencies

### `chroma` (Recommended for development)
- Local vector embeddings
- Semantic similarity search
- Persists to `data/chroma/`

### `azure_search` (Production/Enterprise)
- Azure AI Search integration
- Enterprise-grade semantic search
- Requires `AZURE_SEARCH_ENDPOINT` and `AZURE_SEARCH_KEY`

### Index Schematics

```bash
cd src/warnerco/backend

# Chroma (local vectors)
uv run python -c "from app.adapters.chroma_store import ChromaMemoryStore; import asyncio; asyncio.run(ChromaMemoryStore().index_all())"

# Azure AI Search (enterprise vectors)
uv run python scripts/index_azure_search.py
```

## LangGraph Flow

The search pipeline uses LangGraph for orchestrated retrieval:

1. **Parse Intent** - Classify query type (lookup, diagnostic, analytics, search)
2. **Retrieve** - Fetch candidates from memory backend
3. **Compress Context** - Minimize token bloat for LLM
4. **Reason** - Generate insights (LLM or stub)
5. **Respond** - Format for dashboards and MCP

## Azure Deployment

### Deploy Resources

**PowerShell:**
```powershell
cd src\warnerco\scripts
.\deploy-azure.ps1 -ResourceGroup "warnerco-rg" -Location "eastus"
```

**Bash:**
```bash
./deploy-azure.sh warnerco-rg eastus
```

### Deployment Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `environment` | classroom | Environment tier (classroom/dev/prod) |
| `enableWaf` | false | Enable Front Door + WAF |
| `enableAiSearch` | false | Enable Azure AI Search |
| `replicaMin` | 0 | Minimum container replicas |
| `replicaMax` | 3 | Maximum container replicas |

### Teardown Resources

**PowerShell:**
```powershell
.\teardown-azure.ps1 -ResourceGroup "warnerco-rg"
```

**Bash:**
```bash
./teardown-azure.sh warnerco-rg
```

## Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
# Memory Backend: json | chroma | azure_search
MEMORY_BACKEND=chroma

# Server
HOST=0.0.0.0
PORT=8000
DEBUG=false

# LLM (optional - enables enhanced reasoning)
OPENAI_API_KEY=sk-...
# OR Azure OpenAI
AZURE_OPENAI_ENDPOINT=https://...openai.azure.com
AZURE_OPENAI_API_KEY=...
AZURE_OPENAI_DEPLOYMENT=gpt-4o

# Azure AI Search (if MEMORY_BACKEND=azure_search)
AZURE_SEARCH_ENDPOINT=https://...search.windows.net
AZURE_SEARCH_KEY=...
AZURE_SEARCH_INDEX=warnerco-schematics
```

## Development Commands

### Backend (using uv - recommended)

```bash
cd src/warnerco/backend

# Install dependencies
uv sync

# Run development server
uv run uvicorn app.main:app --reload

# Run MCP stdio server (for Claude Desktop)
uv run warnerco-mcp

# Format code
uv run black .
uv run ruff check --fix .

# Run tests
uv run pytest
```

### Backend (using Poetry - alternative)

```bash
cd src/warnerco/backend

# Install dependencies
poetry install

# Run development server
poetry run uvicorn app.main:app --reload

# Format code
poetry run black .
poetry run ruff check --fix .

# Run tests
poetry run pytest
```

### Dashboards

```bash
cd src/warnerco/dashboards

# Install dependencies
npm install

# Development server (with hot reload)
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## Sample Data

The system includes 25 sample robot schematics across 8 robot models:

| Model | Name | Description |
|-------|------|-------------|
| WC-100 | Atlas Prime | Precision manipulation robot |
| WC-200 | Titan Handler | Heavy-duty industrial robot |
| WC-300 | Nimbus Scout | Mobile reconnaissance unit |
| WC-400 | Aegis Guardian | Security patrol robot |
| WC-500 | Hercules Lifter | Heavy-lift robot |
| WC-600 | Mercury Courier | Delivery robot |
| WC-700 | Vulcan Welder | Manufacturing welding robot |
| WC-800 | Phoenix Inspector | Inspection robot |
| WC-900 | Orion Assembler | Assembly robot |

## Testing with MCP Inspector

```bash
cd src/warnerco/backend
npx @modelcontextprotocol/inspector uv run uvicorn app.main:app
```

Opens web UI at http://localhost:5173 to test MCP tools interactively.

## Claude Desktop Integration

Add to `claude_desktop_config.json`:

**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "warnerco-schematica": {
      "command": "uv",
      "args": ["run", "warnerco-mcp"],
      "cwd": "C:/github/context-engineering/src/warnerco/backend"
    }
  }
}
```

## VS Code Integration

Create `.vscode/mcp.json` in your workspace:

```json
{
  "mcpServers": {
    "warnerco-schematica": {
      "command": "uv",
      "args": ["run", "warnerco-mcp"],
      "cwd": "${workspaceFolder}/src/warnerco/backend"
    }
  }
}
```

## License

Educational demonstration for "Context Engineering with MCP" course.
