# WARNERCO Schematica - Architecture Diagrams

## Primary Diagram Location

The main architecture diagrams for this course are in **[docs/diagrams/](../docs/diagrams/)**. This folder contains supplementary reference material.

## WARNERCO Robotics Schematica

The course centers on **WARNERCO Robotics Schematica**, a production MCP server demonstrating:

- FastAPI + FastMCP server architecture
- LangGraph 6-node hybrid RAG pipeline
- 3-tier memory backends (JSON, ChromaDB, Azure AI Search)
- Knowledge graph integration (SQLite + NetworkX)

### Diagram Index

| Diagram | Location | Description |
|---------|----------|-------------|
| **System Overview** | [docs/diagrams/system-overview.md](../docs/diagrams/system-overview.md) | Full architecture diagram |
| **LangGraph Flow** | [docs/diagrams/langgraph-flow.md](../docs/diagrams/langgraph-flow.md) | 6-node RAG pipeline |
| **Azure Deployment** | [docs/diagrams/azure-deploy.md](../docs/diagrams/azure-deploy.md) | Production Azure resources |
| **MCP Primitives** | [docs/diagrams/mcp-primitives.md](../docs/diagrams/mcp-primitives.md) | 15 tools, 10 resources, 5 prompts |
| **Graph Memory** | [docs/diagrams/graph-memory-architecture.md](../docs/diagrams/graph-memory-architecture.md) | Knowledge graph integration |

### Quick Reference

```
WARNERCO Schematica Architecture
================================

CLIENT LAYER
  Claude Desktop (MCP stdio)
  VS Code + GitHub Copilot
  Web Dashboards (Astro SPA)
  REST API Clients

APPLICATION LAYER
  FastAPI Server (:8000)
    /api/* - REST endpoints
    /mcp   - FastMCP HTTP endpoint
    /dash  - Static dashboards

MCP PRIMITIVES (v2.0)
  15 Tools: CRUD, search, graph, interactive
  10 Resources: memory://, catalog://, help://, schematic://
   5 Prompts: diagnostic, comparison, maintenance, etc.

LANGGRAPH 6-NODE PIPELINE
  parse_intent -> query_graph -> retrieve -> compress -> reason -> respond

HYBRID MEMORY LAYER
  Vector Store: JSON -> ChromaDB -> Azure AI Search
  Graph Store:  SQLite + NetworkX (Knowledge Graph)

AI SERVICES
  Azure OpenAI: gpt-4o-mini, text-embedding-ada-002
```

## MCP Tools Summary

### Data Tools
| Tool | Description |
|------|-------------|
| `warn_list_robots` | List all robot schematics with optional filters |
| `warn_get_robot` | Get detailed schematic by ID |
| `warn_semantic_search` | Natural language search with LangGraph RAG |
| `warn_memory_stats` | Memory backend statistics |

### Modification Tools
| Tool | Description |
|------|-------------|
| `warn_index_schematic` | Index a schematic for search |
| `warn_compare_schematics` | Compare two schematics |
| `warn_create_schematic` | Create new schematic |
| `warn_update_schematic` | Update existing schematic |
| `warn_delete_schematic` | Delete schematic |

### Interactive Tools
| Tool | Description |
|------|-------------|
| `warn_guided_search` | Multi-turn guided search with elicitations |
| `warn_feedback_loop` | Collect user feedback on schematics |

### Graph Tools
| Tool | Description |
|------|-------------|
| `warn_add_relationship` | Create triplet in knowledge graph |
| `warn_graph_neighbors` | Find connected entities |
| `warn_graph_path` | Shortest path between entities |
| `warn_graph_stats` | Graph metrics (nodes, edges, density) |

## LangGraph 6-Node Pipeline

```
1. PARSE_INTENT    - Classify query (lookup, diagnostic, analytics, search)
2. QUERY_GRAPH     - Enrich context with knowledge graph relationships
3. RETRIEVE        - Vector search with semantic similarity
4. COMPRESS        - Minimize token bloat, combine vector + graph context
5. REASON          - LLM synthesis (Azure OpenAI or stub)
6. RESPOND         - Format response for MCP/dashboard
```

## Memory Backends

### Development (JSON)
- Zero configuration
- Keyword search
- Source: `data/schematics/schematics.json`

### Staging (ChromaDB)
- Local vector embeddings
- Semantic search
- Index: `uv run python -c "from app.adapters.chroma_store import ChromaMemoryStore; import asyncio; asyncio.run(ChromaMemoryStore().index_all())"`

### Production (Azure AI Search)
- Enterprise-scale hybrid search
- Vector + keyword + semantic ranking
- Index: `uv run python scripts/index_azure_search.py`

### Knowledge Graph (SQLite + NetworkX)
- Entity relationships
- Path finding
- Index: `uv run python scripts/index_graph.py`

## Viewing Diagrams

### VS Code (Recommended)
1. Install [Mermaid Preview extension](https://marketplace.visualstudio.com/items?itemName=vstirbu.vscode-mermaid-preview)
2. Open any diagram `.md` file
3. Use preview pane (Ctrl+Shift+V)

### GitHub
Diagrams render automatically in GitHub markdown viewer.

### Mermaid Live Editor
Copy Mermaid code blocks to [mermaid.live](https://mermaid.live/) for interactive editing.

## Related Documentation

- **[CLAUDE.md](../CLAUDE.md)** - Project-level AI guidance
- **[docs/tutorials/](../docs/tutorials/)** - Hands-on tutorials
- **[docs/api/](../docs/api/)** - API reference documentation

---

**Course**: O'Reilly Live Training - Context Engineering with MCP
**Last Updated**: January 2026
