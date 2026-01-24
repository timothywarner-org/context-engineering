# Student Materials - Context Engineering with MCP

Welcome, students! This folder contains everything you need before, during, and after the course.

## Before Class

1. **[STUDENT_SETUP_GUIDE.md](STUDENT_SETUP_GUIDE.md)** - Complete this 30-60 minute setup before class

## During Class

2. **[TROUBLESHOOTING_FAQ.md](TROUBLESHOOTING_FAQ.md)** - Keep this open for quick fixes
3. **[TUTORIAL_DASHBOARDS.md](TUTORIAL_DASHBOARDS.md)** - Explore WARNERCO Schematica dashboards
4. **[TUTORIAL_MCP_INSPECTOR.md](TUTORIAL_MCP_INSPECTOR.md)** - Debug MCP servers with Inspector
5. **[TUTORIAL_GITHUB_COPILOT.md](TUTORIAL_GITHUB_COPILOT.md)** - Use MCP with VS Code and GitHub Copilot

## After Class

6. **[POST_COURSE_RESOURCES.md](POST_COURSE_RESOURCES.md)** - Continue your learning journey

## Architecture Documentation

Located in [diagrams/](diagrams/):

- **[system-overview.md](diagrams/system-overview.md)** - Full system architecture diagram
- **[langgraph-flow.md](diagrams/langgraph-flow.md)** - 6-node hybrid RAG pipeline
- **[graph-memory-architecture.md](diagrams/graph-memory-architecture.md)** - Knowledge graph design
- **[azure-deploy.md](diagrams/azure-deploy.md)** - Azure deployment architecture
- **[mcp-primitives.md](diagrams/mcp-primitives.md)** - MCP tools, resources, and prompts

## Advanced Topics

Located in [tutorials/](tutorials/) and [api/](api/):

- **[tutorials/graph-memory-tutorial.md](tutorials/graph-memory-tutorial.md)** - Hands-on knowledge graph tutorial
- **[api/graph-api.md](api/graph-api.md)** - Graph Memory API reference

## Primary Teaching System: WARNERCO Schematica

All examples and tutorials focus on WARNERCO Robotics Schematica:

- **Location**: `src/warnerco/backend/`
- **Start HTTP server**: `uv run uvicorn app.main:app --reload`
- **Start MCP server**: `uv run warnerco-mcp`
- **API docs**: http://localhost:8000/docs
- **Dashboards**: http://localhost:8000/dash/

## Need Help?

- Check the [Troubleshooting FAQ](TROUBLESHOOTING_FAQ.md) first
- Ask in class chat
- Open an [issue on GitHub](https://github.com/timothywarner-org/context-engineering/issues)
