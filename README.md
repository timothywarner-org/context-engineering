# Context Engineering with MCP: Build AI Systems That Actually Remember

<img src="images/cover.png" alt="Context Engineering with MCP Course Cover" width="700"/>

Welcome to the training hub for mastering **Context Engineering with Model Context Protocol (MCP)**. This course teaches you to implement production-ready semantic memory systems for AI assistants using Python, FastAPI, FastMCP, and LangGraph.

---

## Quick Start

### Prerequisites

- Python 3.11+ (3.12+ recommended for WARNERCO Schematica)
- Node.js 20+ (for Lab 01 and MCP Inspector)
- [uv](https://docs.astral.sh/uv/) package manager (recommended for Python)
- Claude Desktop or Claude Code

### Option 1: Hello MCP Lab (Beginner Entry Point)

```bash
git clone https://github.com/timothywarner-org/context-engineering.git
cd context-engineering/labs/lab-01-hello-mcp/starter
npm install && npm start

# Test with MCP Inspector (in another terminal)
npx @modelcontextprotocol/inspector node src/index.js
```

### Option 2: WARNERCO Schematica (Flagship Teaching App)

```bash
cd src/warnerco/backend
uv sync
uv run uvicorn app.main:app --reload    # HTTP server at http://localhost:8000
uv run warnerco-mcp                      # MCP stdio server for Claude Desktop
```

---

## Course Structure (4 x 50 Minutes)

| Segment | Topic                  | Focus                                                           |
| ------- | ---------------------- | --------------------------------------------------------------- |
| **1**   | All About Context      | Token economics, context loss types, why RAG isn't enough       |
| **2**   | All About MCP          | FastMCP, FastAPI, tools, resources, prompts, elicitations       |
| **3**   | Semantic Memory Stores | JSON, ChromaDB, Azure AI Search, Graph Memory, Scratchpad       |
| **4**   | MCP in Production      | Claude Desktop, Claude Code, VS Code, GitHub Copilot, LangGraph |

---

## WARNERCO Schematica Architecture

The flagship teaching application demonstrates production MCP patterns with a 7-node hybrid RAG pipeline:

```
+---------------------------------------------------------------+
|                     FastAPI + FastMCP                         |
+---------------------------------------------------------------+
|  LangGraph Flow (7-node Hybrid RAG)                           |
|  parse_intent -> query_graph -> inject_scratchpad -> retrieve |
|  -> compress -> reason -> respond                             |
+---------------------------------------------------------------+
|  Hybrid Memory Layer                                          |
|  +-------------------+  +-------------------+  +-------------+ |
|  | Vector Store      |  | Graph Store       |  | Scratchpad  | |
|  | JSON -> Chroma -> |  | SQLite + NetworkX |  | In-memory   | |
|  | Azure AI Search   |  | (Knowledge Graph) |  | (Session)   | |
|  +-------------------+  +-------------------+  +-------------+ |
+---------------------------------------------------------------+
```

### Memory Store Comparison

| Feature              | JSON         | ChromaDB      | Azure AI Search    | Graph       | Scratchpad     |
| -------------------- | ------------ | ------------- | ------------------ | ----------- | -------------- |
| Semantic Search      | No           | Yes           | Yes                | No          | No             |
| Relationship Queries | No           | No            | No                 | Yes         | No             |
| Session Memory       | No           | No            | No                 | No          | Yes            |
| Best For             | Prototyping  | Local dev     | Production         | Connections | Working memory |

---

## Repository Structure

```
context-engineering/
├── src/warnerco/backend/      # WARNERCO Schematica (FastAPI + FastMCP + LangGraph)
├── labs/lab-01-hello-mcp/     # Hands-on beginner lab
├── docs/                      # Student materials, tutorials, diagrams
├── instructor/                # Instructor-only materials
├── config/                    # Sample MCP client configurations
├── .vscode/                   # VS Code workspace configuration
├── .claude/                   # Claude Code agents and skills
└── CLAUDE.md                  # Development instructions (SOURCE OF TRUTH)
```

**For development details, see [CLAUDE.md](CLAUDE.md)** - the source of truth for:
- Complete MCP tool reference
- API endpoint documentation
- Environment variable configuration
- LangGraph pipeline details
- Graph and Scratchpad Memory features

---

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

See `.vscode/mcp.json` in the repository for local and Azure APIM configurations.

---

## Testing with MCP Inspector

```bash
npx @modelcontextprotocol/inspector uv run warnerco-mcp
# Opens http://localhost:5173
```

---

## Resources

- **[MCP Specification](https://spec.modelcontextprotocol.io/)** - Official protocol documentation
- **[FastMCP Documentation](https://github.com/jlowin/fastmcp)** - Python MCP framework
- **[CLAUDE.md](CLAUDE.md)** - Development instructions for this repository

---

## Your Instructor

### Tim Warner

**Microsoft MVP** - Azure AI and Cloud/Datacenter Management
**Microsoft Certified Trainer** (25+ years)

- Website: [techtrainertim.com](https://techtrainertim.com)
- GitHub: [@timothywarner](https://github.com/timothywarner)
- LinkedIn: [linkedin.com/in/timothywarner](https://www.linkedin.com/in/timothywarner/)

---

## License

MIT License - 2026 Timothy Warner

---

**Now go build AI systems that actually remember!**
