# Context Engineering with MCP: Build AI Systems That Actually Remember

<img src="images/cover.png" alt="Context Engineering with MCP Course Cover" width="700"/>

Welcome to the training hub for mastering **Context Engineering with Model Context Protocol (MCP)**. This comprehensive course teaches you to implement production-ready semantic memory systems for AI assistants using Python, FastMCP, and multiple vector database backends.

---

## Course Structure (4 x 50 Minutes)

| Segment | Topic | Focus |
|---------|-------|-------|
| **1** | All About Context | Token economics, context loss types, why RAG isn't enough |
| **2** | All About MCP | FastMCP, FastAPI, tools, resources, prompts |
| **3** | Semantic Memory Stores | JSON, SQLite, ChromaDB, Pinecone implementations |
| **4** | MCP in Production | Claude Code, VS Code, GitHub Copilot, LangGraph |

**Total Duration:** 4 hours (with 10-minute breaks)

---

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+ (for some MCP tools)
- Claude Desktop or Claude Code

### Installation

```bash
# Clone the repository
git clone https://github.com/timothywarner-org/context-engineering.git
cd context-engineering

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt
```

### Run Your First Memory Server

```bash
# Start the memory server
cd mcp-servers/memory_server
python server.py

# Test with MCP Inspector (in another terminal)
pip install mcp-inspector
mcp-inspector python server.py
```

---

## Repository Structure

```
context-engineering/
├── mcp-servers/
│   ├── memory_server/           # Main FastMCP memory server
│   │   ├── server.py            # Full MCP implementation
│   │   └── requirements.txt
│   ├── memory_stores/           # Pluggable storage backends
│   │   ├── interface.py         # Abstract interface
│   │   ├── json_store.py        # JSON file storage
│   │   ├── sqlite_store.py      # SQLite + FTS5
│   │   ├── chroma_store.py      # ChromaDB vectors
│   │   └── pinecone_store.py    # Cloud vectors
│   └── langgraph_integration/   # Multi-agent examples
│       └── multi_agent_memory.py
├── examples/
│   ├── claude_desktop_config.json
│   ├── claude_code_mcp.json
│   └── vscode_settings.json
├── labs/
│   ├── lab-01-context-basics/
│   ├── lab-02-fastmcp-server/
│   ├── lab-03-semantic-memory/
│   └── lab-04-client-integration/
├── instructor/
│   ├── course-plan-jan-2026.md
│   └── *.pptx
└── student/
    ├── STUDENT_SETUP_GUIDE.md
    └── TROUBLESHOOTING_FAQ.md
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

Implement multiple storage backends:

| Backend | Best For | Key Feature |
|---------|----------|-------------|
| JSON | Prototyping | Zero setup |
| SQLite | Structured data | FTS5 search |
| ChromaDB | Local vectors | Auto embeddings |
| Pinecone | Production | Multi-tenant |

```python
from memory_stores import ChromaMemoryStore

store = ChromaMemoryStore(persist_directory="./chroma_data")

# Store with automatic embedding
memory_id = store.store(
    content="The API uses JWT with 1-hour expiry",
    category="architecture",
    tags=["auth", "jwt"],
    importance=8
)

# Semantic search
results = store.semantic_search("how does authentication work?")
```

### Segment 4: Client Integration

Configure Claude Desktop, Claude Code, and VS Code:

**Claude Desktop** (`~/Library/Application Support/Claude/claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "memory": {
      "command": "python",
      "args": ["/path/to/memory_server/server.py"]
    }
  }
}
```

**Claude Code** (`.claude/mcp.json`):
```json
{
  "servers": {
    "project-memory": {
      "command": "python",
      "args": ["./mcp-servers/memory_server/server.py"]
    }
  }
}
```

---

## Memory Store Comparison

| Feature | JSON | SQLite | ChromaDB | Pinecone |
|---------|------|--------|----------|----------|
| Setup | None | None | `pip install` | API key |
| Semantic Search | No | No | Yes | Yes |
| Full-Text Search | No | Yes | No | No |
| Scale | <1K | <100K | <100K | Millions |
| Cost | Free | Free | Free | Pay-per-use |

---

## API Reference

### Tools

| Tool | Description |
|------|-------------|
| `store_memory` | Store content with metadata |
| `search_memories` | Semantic/keyword search |
| `get_memory` | Retrieve by ID |
| `update_memory` | Modify existing |
| `delete_memory` | Remove memory |
| `list_memories` | Paginated listing |

### Resources

| URI | Description |
|-----|-------------|
| `memory://stats` | Storage statistics |
| `memory://recent` | Recent memories |
| `memory://important` | High-importance items |

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MEMORY_BACKEND` | `json` | Backend type |
| `MEMORY_PATH` | `memories.json` | Storage path |
| `CHROMA_PERSIST_DIR` | `./chroma_data` | ChromaDB directory |
| `PINECONE_API_KEY` | - | Pinecone API key |

---

## Resources

- **[MCP Specification](https://spec.modelcontextprotocol.io/)**
- **[FastMCP Documentation](https://github.com/jlowin/fastmcp)**
- **[Claude Documentation](https://docs.anthropic.com/)**
- **[ChromaDB Docs](https://docs.trychroma.com/)**
- **[Pinecone Docs](https://docs.pinecone.io/)**

---

## Your Instructor

### Tim Warner

**Microsoft MVP** - Azure AI and Cloud/Datacenter Management
**Microsoft Certified Trainer** (25+ years)

- Website: [techtrainertim.com](https://techtrainertim.com)
- LinkedIn: [linkedin.com/in/timothywarner](https://www.linkedin.com/in/timothywarner/)
- YouTube: [youtube.com/timothywarner](https://www.youtube.com/channel/UCim7PFtynyPuzMHtbNyYOXA)
- Email: timothywarner316@gmail.com

---

## License

© 2026 Timothy Warner. MIT License.

---

**Now go build AI systems that actually remember!** 🧠
