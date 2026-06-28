# NOTICE - Lab 02 MCP Chat reference app

This lab (`labs/lab-02-mcp-chat/`) is a complete, runnable **MCP client + stdio FastMCP server + interactive CLI** in one place. It is reference material adapted from Anthropic's course starter scaffold, included here so learners can study a real MCP client/server pair alongside the heavier WARNERCO Schematica app.

## Attribution

- **Original source:** Anthropic, "Claude with the Anthropic API" course (https://anthropic.skilljar.com/claude-with-the-anthropic-api/)
- **Provider:** Anthropic, PBC, via Skilljar
- **Vendored by:** Tim Warner, for the "Context Engineering with MCP" O'Reilly training.
- **Snapshot date:** Captured 2026-05; re-homed into this repo 2026-06-28.

The code was distributed as downloadable starter material accompanying that course. Anthropic hands this scaffold to every learner as a foundation to build on, which is exactly how it is used here. Attribution is given in good faith; if you are the upstream author and want a change, open an issue.

## What's in it

- **`main.py`** - entry point. Loads `.env`, instantiates a `Claude` service and an `MCPClient`, opens an interactive `CliApp`.
- **`mcp_server.py`** - a `FastMCP` server exposing six sample documents as resources (`docs://documents`, `docs://documents/{id}`), `read_doc_contents` and `edit_document` tools, and a `format` prompt. Runs over stdio.
- **`mcp_client.py`** - a thin wrapper around the official `mcp.ClientSession` that exposes `list_tools`, `call_tool`, `list_prompts`, `get_prompt`, `read_resource`.
- **`core/`** - the chat loop: `claude.py` (Anthropic SDK wrapper), `chat.py` / `cli_chat.py` (orchestration with `@doc-id` retrieval and `/prompt-name` parsing), `cli.py` (prompt-toolkit shell), `tools.py` (tool-result handling).

## Why it lives here

WARNERCO Schematica (`src/warnerco/backend/`) is the flagship: a production-shaped FastAPI + FastMCP + LangGraph app with 28 tools. Lab 01 (`labs/lab-01-hello-mcp/`) is the JS "hello world." This lab fills the gap between them: the smallest complete Python MCP **client *and* server** a student can read top to bottom in one sitting, and the answer to "what does a real MCP chat client look like in production code?"

## How to run it

On-rails, one command (recommended), from this directory:

```powershell
.\run.ps1
```

That wrapper auto-creates `.env` from `.env.example` on first run, lifts `ANTHROPIC_API_KEY` from the repo-root `.env` so you do not paste the key twice, then hands off to `uv run main.py`. It does not modify any vendored file.

The manual workflow in [`README.md`](./README.md) still works unchanged.

## Modifications from the original

1. Re-homed from `examples/mcp_cli/` to `labs/lab-02-mcp-chat/`.
2. `.env` template renamed to `.env.example` so the inner `.gitignore` covers the empty-key template.
3. This `NOTICE.md` and the `run.ps1` launcher added. The launcher is Tim Warner's original work and is the only on-rails bridge; it reads `.env.example`, writes a gitignored `.env`, and invokes `uv run` as a black box.
4. `README.md` "Development" section corrected: the upstream scaffold shipped with `# TODO` markers, but **this copy already has the tools, resources, prompts, and client methods implemented** — it runs as-is.

## License

The upstream course distributes this as instructional starter material with no explicit license file. Treat it as study-and-build reference: run it, adapt the patterns, teach from it, with attribution preserved. If you intend to redistribute it as a standalone product, check with Anthropic first.
