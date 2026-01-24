# WARNERCO Schematica - Diagram Summary

## Overview

This directory contains architecture diagrams for **WARNERCO Robotics Schematica**, the production MCP server implementation taught in the Context Engineering with MCP course.

## Primary Diagram Location

The main diagrams are in **[docs/diagrams/](../docs/diagrams/)**:

| File | Lines | Description |
|------|-------|-------------|
| `system-overview.md` | ~150 | Full system architecture with all layers |
| `langgraph-flow.md` | ~200 | 6-node RAG pipeline details |
| `azure-deploy.md` | ~250 | Azure production deployment |
| `mcp-primitives.md` | ~180 | MCP tools, resources, prompts catalog |
| `graph-memory-architecture.md` | ~290 | Knowledge graph integration |

## WARNERCO Schematica Architecture

### System Components

```
src/warnerco/backend/
├── app/
│   ├── main.py              # FastAPI application entry
│   ├── mcp_tools.py         # FastMCP tool definitions (15 tools)
│   ├── api/                 # REST API routes
│   ├── langgraph/
│   │   └── flow.py          # 6-node RAG pipeline
│   ├── adapters/
│   │   ├── json_store.py    # JSON memory backend
│   │   ├── chroma_store.py  # ChromaDB memory backend
│   │   ├── azure_search_store.py  # Azure AI Search backend
│   │   └── graph_store.py   # SQLite + NetworkX graph store
│   └── models/
│       └── graph.py         # Entity/Relationship models
├── data/
│   ├── schematics/
│   │   └── schematics.json  # 25 robot schematics
│   └── graph.db             # Knowledge graph database
├── static/
│   └── dash/                # Astro SPA dashboards
└── scripts/
    ├── index_azure_search.py
    └── index_graph.py
```

### MCP Primitives Count

| Primitive | Count | Details |
|-----------|-------|---------|
| **Tools** | 15 | Data (4), Modification (5), Interactive (2), Graph (4) |
| **Resources** | 10 | memory://, catalog://, help://, schematic://, mcp:// |
| **Prompts** | 5 | diagnostic, comparison, search_strategy, maintenance, schematic_review |
| **Elicitations** | 2 | guided_search, feedback_loop |

### LangGraph 6-Node Pipeline

| Node | Function | Purpose |
|------|----------|---------|
| 1 | `parse_intent` | Classify query (lookup, diagnostic, analytics, search) |
| 2 | `query_graph` | Enrich context with knowledge graph relationships |
| 3 | `retrieve` | Vector search using selected memory backend |
| 4 | `compress_context` | Minimize tokens, combine vector + graph context |
| 5 | `reason` | LLM synthesis (Azure OpenAI or stub fallback) |
| 6 | `respond` | Format response for MCP/dashboard consumption |

### Memory Backend Tiers

| Backend | Use Case | Search Type | Config |
|---------|----------|-------------|--------|
| **JSON** | Development | Keyword | `MEMORY_BACKEND=json` |
| **ChromaDB** | Staging | Semantic | `MEMORY_BACKEND=chroma` |
| **Azure AI Search** | Production | Hybrid | `MEMORY_BACKEND=azure_search` |
| **SQLite + NetworkX** | All | Graph traversal | Auto-enabled |

### Azure Deployment Resources

| Resource | SKU | Purpose |
|----------|-----|---------|
| Container App | Consumption | FastAPI + FastMCP server |
| Azure AI Search | Basic | Vector + keyword search |
| Azure OpenAI | Standard | gpt-4o-mini + ada-002 |
| Storage Account | Standard | Blob storage |

## Diagram Validation

All diagrams verified for:
- Mermaid syntax correctness
- Accurate component names
- Current tool/resource counts
- Proper data flow representation

## Educational Use

### For Students
- Visual understanding of MCP architecture
- Clear separation of concerns across layers
- See how local and Azure deployments differ
- Understand hybrid RAG pipeline flow

### For Instructors
- Teaching aids during course segments
- Reference during live coding demos
- Basis for whiteboard discussions

## Maintenance

When updating diagrams:
1. Verify tool/resource counts match `mcp_tools.py`
2. Ensure LangGraph nodes match `flow.py`
3. Check memory backends match `adapters/__init__.py`
4. Test Mermaid syntax at [mermaid.live](https://mermaid.live/)

---

**Course**: O'Reilly Live Training - Context Engineering with MCP
**Last Updated**: January 2026
