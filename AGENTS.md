# Repository Guidelines

## Project Structure and Module Organization

- `src/warnerco/backend/` - **WARNERCO Schematica**: The flagship FastAPI + FastMCP + LangGraph teaching application
- `labs/` - Course exercises; `labs/lab-01-hello-mcp/` includes `starter/` and `solution/`
- `docs/` - Student materials including setup guides, tutorials, and API reference
- `diagrams/` - High-level architecture diagrams (Mermaid)
- `instructor/` - Course plans, demo scripts, and teaching materials
- `config/` - Sample MCP client configuration files
- `examples/` - Configuration examples for Claude Code and VS Code

## Build, Test, and Development Commands

### WARNERCO Schematica (Primary)

```bash
cd src/warnerco/backend
uv sync                                    # Install dependencies
uv run uvicorn app.main:app --reload       # Start FastAPI server (http://localhost:8000)
uv run warnerco-mcp                        # MCP stdio server (for Claude Desktop)
uv run pytest                              # Run test suite
```

### Lab 01 - Hello MCP (Beginner)

```bash
cd labs/lab-01-hello-mcp/starter
npm install
npm start                                  # Run MCP server
npx @modelcontextprotocol/inspector node src/index.js  # Test with Inspector
```

## Coding Style and Naming Conventions

- JavaScript and TypeScript use 2-space indentation and ES modules (`import ... from`)
- Python files use 4-space indentation and snake_case filenames (example: `graph_store.py`)
- Match existing naming patterns: `main.py`, `mcp_tools.py`, `flow.py`
- Documentation files use UPPER_SNAKE.md format (example: `STUDENT_SETUP_GUIDE.md`)

## Testing Guidelines

- WARNERCO Schematica has a test suite: run `uv run pytest` in `src/warnerco/backend`
- MCP servers can be tested with MCP Inspector: `npx @modelcontextprotocol/inspector`
- Add or update tests alongside tool changes when possible
- Document manual verification if no tests exist

## Commit and Pull Request Guidelines

- Commit messages are short, imperative, sentence case (example: "Add graph memory indexing script")
- PRs should describe scope, affected components, and how you verified changes
- Include screenshots for diagram or documentation updates when useful
- Link related issues if applicable

## Security and Configuration Tips

- Use `.env.example` files as templates; do not commit secrets
- Keep config samples in `config/` and update docs when configuration steps change
- Never commit API keys, passwords, or connection strings

## Agent-Specific Instructions

- Review `CLAUDE.md` before automated edits for architecture context
- The primary focus is WARNERCO Schematica under `src/warnerco/backend/`
- Lab 01 is the beginner entry point for students
