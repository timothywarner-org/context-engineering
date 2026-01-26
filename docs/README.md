# Student Materials - Context Engineering with MCP

Welcome! This folder contains student materials for the course.

## Before Class

1. **[STUDENT_SETUP_GUIDE.md](STUDENT_SETUP_GUIDE.md)** - Complete this 30-60 minute setup before class

## During Class

2. **[TROUBLESHOOTING_FAQ.md](TROUBLESHOOTING_FAQ.md)** - Quick fixes for common issues

## Architecture Documentation

Located in [diagrams/](diagrams/):

- **[system-overview.md](diagrams/system-overview.md)** - Full system architecture
- **[langgraph-flow.md](diagrams/langgraph-flow.md)** - 7-node hybrid RAG pipeline
- **[graph-memory-architecture.md](diagrams/graph-memory-architecture.md)** - Knowledge graph design
- **[azure-deploy.md](diagrams/azure-deploy.md)** - Azure deployment architecture
- **[mcp-primitives.md](diagrams/mcp-primitives.md)** - MCP tools, resources, and prompts

## Advanced Topics

- **[tutorials/graph-memory-tutorial.md](tutorials/graph-memory-tutorial.md)** - Hands-on knowledge graph tutorial
- **[api/graph-api.md](api/graph-api.md)** - Graph Memory API reference

## Quick Start: WARNERCO Schematica

```bash
cd src/warnerco/backend
uv sync
uv run uvicorn app.main:app --reload  # HTTP server at localhost:8000
uv run warnerco-mcp                   # MCP server for Claude Desktop
```

- **API docs**: http://localhost:8000/docs
- **Dashboards**: http://localhost:8000/dash/

## Need Help?

- Check the [Troubleshooting FAQ](TROUBLESHOOTING_FAQ.md)
- See [CLAUDE.md](../CLAUDE.md) for comprehensive development guidance
