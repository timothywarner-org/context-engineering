# Context Engineering with MCP: Build AI Systems That Actually Remember

<img src="images/cover.png" alt="Context Engineering with MCP Course Cover" width="700"/>

Welcome to the training hub for mastering **Context Engineering with Model Context Protocol (MCP)**. This comprehensive course teaches you to implement production-ready semantic memory systems for AI assistants using Python, JavaScript, TypeScript, and multiple vector database backends.

---

## Course Structure (4 x 50 Minutes)

| Segment | Topic | Focus |
|---------|-------|-------|
| **1** | All About Context | Token economics, context loss types, why RAG isn't enough |
| **2** | All About MCP | FastMCP, FastAPI, tools, resources, prompts |
| **3** | Semantic Memory Stores | JSON, ChromaDB, Azure AI Search implementations |
| **4** | MCP in Production | Claude Code, VS Code, GitHub Copilot, LangGraph |

**Total Duration:** 4 hours (with 10-minute breaks)

---

## Quick Start

### Prerequisites

- Python 3.11+ (for WARNERCO Schematica and Python MCP servers)
- Node.js 20+ (for JavaScript/TypeScript MCP servers and labs)
- [uv](https://docs.astral.sh/uv/) package manager (recommended for Python)
- Claude Desktop or Claude Code

### Option 1: Hello MCP Lab (Beginner)

The hands-on lab is the fastest way to build your first MCP server.

```bash
# Clone the repository
git clone https://github.com/timothywarner-org/context-engineering.git
cd context-engineering

# Navigate to the starter lab
cd labs/lab-01-hello-mcp/starter
npm install
npm start

# Test with MCP Inspector (in another terminal)
npx @modelcontextprotocol/inspector node src/index.js
# Opens http://localhost:5173
```

### Option 2: WARNERCO Schematica (Advanced)

The full-featured FastAPI + FastMCP + LangGraph application demonstrates production patterns.

```bash
# Navigate to the backend
cd src/warnerco/backend

# Install dependencies with uv
uv sync

# Start the server
uv run uvicorn app.main:app --reload
# Opens http://localhost:8000

# Or run as MCP stdio server (for Claude Desktop)
uv run warnerco-mcp
```

---

## Repository Structure

```
context-engineering/
├── .claude/                        # Claude Code extensions
│   ├── agents/                     # Custom agents
│   │   ├── azure-principal-architect/
│   │   └── python-mcp-server-expert/
│   ├── skills/                     # Custom skills
│   │   ├── mcp-server-builder/
│   │   └── warnerco-schematica/
│   └── settings.local.json
├── .github/                        # GitHub configuration
│   ├── agents/                     # GitHub Copilot agents
│   ├── chatmodes/                  # Copilot chat modes
│   ├── instructions/               # Copilot instructions
│   ├── skills/                     # Copilot skills
│   ├── workflows/                  # CI/CD workflows
│   └── copilot-instructions.md
├── config/                         # Sample MCP client configurations
│   ├── claude_desktop_config.json  # Claude Desktop example
│   └── README.md
├── diagrams/                       # Architecture diagrams (Mermaid)
│   ├── coretext-mcp-azure.md
│   ├── coretext-mcp-local.md
│   ├── stoic-mcp-azure.md
│   ├── stoic-mcp-local.md
│   └── INDEX.md
├── docs/                           # Student materials
│   ├── STUDENT_SETUP_GUIDE.md      # Pre-course setup instructions
│   ├── TROUBLESHOOTING_FAQ.md      # Common issues and fixes
│   ├── POST_COURSE_RESOURCES.md    # Continued learning
│   └── diagrams/                   # System architecture SVGs
│       ├── system-overview.svg
│       ├── langgraph-flow.svg
│       └── azure-deploy.svg
├── examples/                       # Configuration examples
│   ├── claude_code_mcp.json        # Claude Code MCP config
│   └── vscode_settings.json        # VS Code settings
├── images/                         # Course images
│   └── cover.png
├── infra/                          # Azure IaC templates (empty)
├── instructor/                     # Instructor materials
│   ├── DEMO_SCRIPT.md              # Live demo walkthrough
│   ├── DEMO_QUICK_REFERENCE.md     # Quick reference card
│   ├── RUNBOOK.md                  # Operational runbook
│   ├── course-plan-jan-2026.md     # Detailed course plan
│   └── *.pptx                      # Slide decks
├── labs/                           # Hands-on exercises
│   ├── lab-01-hello-mcp/           # Build your first MCP server
│   │   ├── starter/                # Starting point
│   │   └── solution/               # Completed version
│   └── README.md
├── reference/                      # External reference implementations
│   ├── globomantics-robot-fleet-main/
│   ├── globomantics-robotics-api-main/
│   └── schematica-main/
├── scripts/                        # Utility scripts (empty)
├── src/warnerco/                   # WARNERCO Robotics Schematica
│   ├── backend/                    # FastAPI + FastMCP + LangGraph
│   │   ├── app/                    # Application code
│   │   ├── data/                   # JSON schematics + Chroma vectors
│   │   ├── static/                 # SPA dashboards
│   │   └── scripts/                # Indexing utilities
│   ├── dashboards/                 # Dashboard assets
│   ├── data/                       # Shared data files
│   ├── infra/                      # Azure deployment
│   ├── scripts/                    # Utility scripts
│   └── README.md
├── CLAUDE.md                       # Claude Code instructions
├── GEMINI.md                       # Gemini instructions
├── AGENTS.md                       # Agent documentation
└── requirements.txt                # Root Python dependencies
```

---

## What You'll Build

### Segment 1: Understanding Context

Learn why AI "forgets" and how to fix it:

- **Window Overflow** - Messages pushed out of context
- **Session Boundary** - Complete loss between sessions
- **Attention Dilution** - Context ignored in noise
- **Compression Loss** - Summarization loses details

### Segment 2: MCP Server Development

Build production MCP servers with FastMCP:

```python
from fastmcp import FastMCP
from pydantic import BaseModel, Field

mcp = FastMCP("memory-server")

class MemoryInput(BaseModel):
    content: str = Field(..., description="Content to remember")
    importance: int = Field(default=5, ge=1, le=10)

@mcp.tool()
async def store_memory(params: MemoryInput) -> str:
    """Store a memory for future retrieval."""
    memory_id = save_to_store(params.content, params.importance)
    return f"Stored memory {memory_id}"
```

### Segment 3: Semantic Memory Stores

Implement multiple storage backends with the WARNERCO Schematica pattern:

| Backend | Best For | Key Feature |
|---------|----------|-------------|
| JSON | Prototyping | Zero setup, keyword search |
| ChromaDB | Local development | Auto embeddings, semantic search |
| Azure AI Search | Production | Enterprise scale, multi-tenant |

```python
# WARNERCO Schematica memory backend pattern
from app.adapters.chroma_store import ChromaMemoryStore

store = ChromaMemoryStore()

# Semantic search across robot schematics
results = await store.search("hydraulic arm specifications", top_k=5)
```

### Segment 4: Client Integration

Configure Claude Desktop, Claude Code, and VS Code:

**Claude Desktop** (`%APPDATA%\Claude\claude_desktop_config.json` on Windows):

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

**VS Code** (`.vscode/mcp.json`):

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

---

## Memory Store Comparison

| Feature | JSON | ChromaDB | Azure AI Search |
|---------|------|----------|-----------------|
| Setup | None | `pip install` | Azure subscription |
| Semantic Search | No | Yes | Yes |
| Full-Text Search | Keyword only | No | Yes |
| Scale | <1K | <100K | Millions |
| Cost | Free | Free | Pay-per-use |
| Best For | Prototyping | Local dev | Production |

---

## WARNERCO Schematica Architecture

The flagship teaching application demonstrates production MCP patterns:

```
+---------------------------------------------------------------+
|                     FastAPI + FastMCP                         |
+---------------------------------------------------------------+
|  LangGraph Flow (5-node RAG)                                  |
|  parse_intent -> retrieve -> compress_context -> reason -> respond |
+---------------------------------------------------------------+
|  3-Tier Memory                                                |
|  JSON (source) -> Chroma (vectors) -> Azure AI Search (enterprise) |
+---------------------------------------------------------------+
```

**MCP Tools:**

| Tool | Description |
|------|-------------|
| `warn_list_robots` | List all robot schematics |
| `warn_get_robot` | Get schematic by ID |
| `warn_semantic_search` | Semantic search across schematics |
| `warn_memory_stats` | Backend statistics |

**API Endpoints:**

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/robots` | List schematics |
| GET | `/api/robots/{id}` | Get by ID |
| POST | `/api/search` | Semantic search |
| GET | `/api/memory/stats` | Backend stats |
| GET | `/docs` | OpenAPI documentation |

---

## Environment Variables

Set in `src/warnerco/backend/.env`:

| Variable | Default | Description |
|----------|---------|-------------|
| `MEMORY_BACKEND` | `json` | Backend type: `json`, `chroma`, `azure_search` |
| `AZURE_SEARCH_ENDPOINT` | - | Azure AI Search endpoint |
| `AZURE_SEARCH_KEY` | - | Azure AI Search API key |
| `AZURE_OPENAI_ENDPOINT` | - | Azure OpenAI endpoint |
| `AZURE_OPENAI_API_KEY` | - | Azure OpenAI API key |

---

## Testing with MCP Inspector

The MCP Inspector is the primary debugging tool for MCP servers:

```bash
# Test any MCP server
npx @modelcontextprotocol/inspector node path/to/server.js

# Test Python servers
npx @modelcontextprotocol/inspector uv run warnerco-mcp

# Opens web UI at http://localhost:5173
```

---

## Resources

- **[MCP Specification](https://spec.modelcontextprotocol.io/)** - Official protocol documentation
- **[FastMCP Documentation](https://github.com/jlowin/fastmcp)** - Python MCP framework
- **[MCP TypeScript SDK](https://www.npmjs.com/package/@modelcontextprotocol/sdk)** - Official TypeScript SDK
- **[Claude Documentation](https://docs.anthropic.com/)** - Anthropic's Claude docs
- **[ChromaDB Docs](https://docs.trychroma.com/)** - Vector database
- **[Azure AI Search Docs](https://learn.microsoft.com/azure/search/)** - Enterprise search

---

## Your Instructor

### Tim Warner

**Microsoft MVP** - Azure AI and Cloud/Datacenter Management
**Microsoft Certified Trainer** (25+ years)

- Website: [techtrainertim.com](https://techtrainertim.com)
- GitHub: [@timothywarner](https://github.com/timothywarner)
- LinkedIn: [linkedin.com/in/timothywarner](https://www.linkedin.com/in/timothywarner/)
- YouTube: [youtube.com/timothywarner](https://www.youtube.com/channel/UCim7PFtynyPuzMHtbNyYOXA)

---

## License

MIT License - 2026 Timothy Warner

---

**Now go build AI systems that actually remember!**
