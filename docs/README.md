# Student Materials - Context Engineering with MCP

Welcome! This folder contains student materials for the course.

## Before Class

1. **[STUDENT_SETUP_GUIDE.md](STUDENT_SETUP_GUIDE.md)** - Complete this 30-60 minute setup before class

## During Class

2. **[TROUBLESHOOTING_FAQ.md](TROUBLESHOOTING_FAQ.md)** - Quick fixes for common issues

## Architecture Documentation

Located in [diagrams/](diagrams/):

- **[system-overview.md](diagrams/system-overview.md)** - Full system architecture
- **[langgraph-flow.md](diagrams/langgraph-flow.md)** - 9-node CoALA-tiered RAG pipeline
- **[graph-memory-architecture.md](diagrams/graph-memory-architecture.md)** - Knowledge graph design
- **[azure-deploy.md](diagrams/azure-deploy.md)** - Azure deployment architecture
- **[mcp-primitives.md](diagrams/mcp-primitives.md)** - MCP tools, resources, and prompts

## Tutorials

- **[tutorials/coala-explainer.md](tutorials/coala-explainer.md)** — **Read this first.** What CoALA is, and where each of the four memory tiers lives in the WARNERCO codebase. ~15 minute self-paced read.
- **[tutorials/coala-memory-walkthrough.md](tutorials/coala-memory-walkthrough.md)** — **Class anchor.** ~4-minute four-tier classroom demo path with paste-ready Inspector calls.
- **[tutorials/graph-memory-tutorial.md](tutorials/graph-memory-tutorial.md)** - Hands-on knowledge graph tutorial
- **[tutorials/progressive-tool-loading.md](tutorials/progressive-tool-loading.md)** - Cheap tool discovery via `warn_search_tools` / `warn_describe_tool`
- **[tutorials/demo-sampling-vscode.md](tutorials/demo-sampling-vscode.md)** - MCP Sampling demo in VS Code
- **[tutorials/remote-mcp-oauth-azure.md](tutorials/remote-mcp-oauth-azure.md)** - Lab 04 explainer: remote MCP secured by Entra ID OAuth via APIM (the AAA lesson)

## Reference

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
