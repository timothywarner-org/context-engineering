# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Working Style (Tim's preferences)

- **Working > clever.** Minimal, reliable code. Skip "elegant," "extensible," "future-proof."
- **Default to ≤3-file changes** for a feature. If you're touching more, justify it.
- **Operational escape hatches required** for anything that runs as a server/daemon (port-killers, `--kill-only`, idempotent re-runs). See `scripts/restart_server.py` as the model.
- **Terse responses.** Lead with the action; end with the verification result. Skip planning sections unless asked.
- **Absolute paths in Bash** — `cd` between tool calls has broken parallel batches in this repo.
- Tim is a senior engineer (MVP/MCT, 25+ years). Frame as peer-to-peer. Cite file paths and line numbers.

## Project Overview

Training materials and MCP server implementations for "Context Engineering with MCP" — a 4×50min course. Flagship teaching app is **WARNERCO Schematica**: FastAPI + FastMCP + LangGraph that exercises **all four CoALA memory tiers** (Working / Episodic / Semantic / Procedural) in one codebase. Source design rationale: `research_synthesis/` (Claude/ChatGPT/Gemini/Perplexity deep-research reports).

Class delivery date and audit status live in instructor memory, not here. Repo layout is discoverable via `Glob` — top-level: `src/warnerco/backend/`, `labs/lab-01-hello-mcp/`, `docs/`, `instructor/`, `config/`, `research_synthesis/`, `.claude/`.

## Development Commands

### WARNERCO Schematica

**Python 3.13 pinned** (`.python-version`). `onnxruntime` (chromadb dep) lacks 3.14 wheels — `uv sync` fails on 3.14 with a clear platform error.

```bash
cd src/warnerco/backend
uv sync                                    # Install dependencies
uv run uvicorn app.main:app --reload       # HTTP at http://localhost:8000
uv run warnerco-serve                      # Same, via console script
uv run warnerco-mcp                        # MCP stdio server (Claude Desktop / Code / VS Code)
uv run warnerco-restart                    # Force-kill port 8000, restart uvicorn
uv run warnerco-restart --kill-only        # Just free the port
uv run warnerco-restart --port 9000        # Use a different port
```

**Restart helper** (`scripts/restart_server.py`): Windows uses `netstat -ano` + `taskkill /F /T /PID` (also kills uvicorn reload children); POSIX uses `lsof -t` + SIGKILL. Refuses to kill its own PID. Exit 0 if port freed.

**Memory backend** via `MEMORY_BACKEND` in `.env`: `json` (default, keyword), `chroma` (local vectors, recommended for dev), `azure_search` (enterprise).

**Index data**:
```bash
uv run python -c "from app.adapters.chroma_store import ChromaMemoryStore; import asyncio; asyncio.run(ChromaMemoryStore().index_all())"
uv run python scripts/index_azure_search.py
uv run python scripts/index_graph.py
```

### Lab 01 (Hello MCP, beginner)

```bash
cd labs/lab-01-hello-mcp/starter
npm install && npm start
npx @modelcontextprotocol/inspector node src/index.js
```

Lab 01 is JS — the snippets in this section apply only there. The flagship is Python/FastMCP and follows FastMCP conventions (decorators on `@mcp.tool()` / `@mcp.resource()` / `@mcp.prompt()`).

**Two-SDK honesty note.** Two distinct FastMCP imports are in play, both installed:
- **WARNERCO** imports `from fastmcp import FastMCP` — the **standalone `fastmcp` package** (now Anthropic-stewarded). Introspection uses `get_tools()`.
- **Lab 02** imports `from mcp.server.fastmcp import FastMCP` — the **official `mcp` SDK's bundled FastMCP**. Introspection uses `list_tools()`.

Their introspection APIs differ (`get_tools()` vs `list_tools()`), which matters when writing introspection code against either server.

**Lab 01 conventions** (JS only):
- Tool returns `{ content: [{ type: 'text', text: <human-readable string> }] }` (the `add` tool returns `` `The sum of ${a} and ${b} is ${sum}` ``, not JSON)
- Logging via `console.error()` — stdout is reserved for MCP protocol

### Lab 02 (MCP Chat CLI, Python)

```bash
cd labs/lab-02-mcp-chat
./run.ps1                                   # on-rails: bootstraps .env, lifts key, uv run main.py
```

Vendored Anthropic course scaffold (attribution in `labs/lab-02-mcp-chat/NOTICE.md`). It is the smallest **complete Python MCP client + stdio FastMCP server + REPL** in the repo — the conceptual bridge between Lab 01 (JS hello-world) and WARNERCO (production-shaped). Server registers 2 tools (`read_doc_contents`, `edit_document`), 1 resource + 1 template (`docs://documents`, `docs://documents/{id}`), 1 prompt (`format`). The `run.ps1` launcher lifts `ANTHROPIC_API_KEY` from the repo-root `.env`. Needs `ANTHROPIC_API_KEY` and `CLAUDE_MODEL` (default `claude-sonnet-4-6`). The app is fully implemented — the upstream `# TODO` markers are kept inline as a before/after teaching artifact.

## WARNERCO Architecture

```
FastAPI + FastMCP
LangGraph (9-node CoALA-tiered RAG):
  parse_intent -> query_graph -> inject_scratchpad -> recall_episodes ->
  retrieve -> compress_context -> reason -> respond -> log_episode

CoALA tiers:
  Working (scratchpad SQLite) | Episodic (events SQLite) |
  Semantic (Chroma/Azure/JSON vector) | Procedural (versioned MCP Prompts)
Consolidation ("sleep cycle"): scratchpad+episodic --(ctx.sample)--> semantic
```

**Counts: 28 tools, 12 resources, 5 prompts.** These drift fastest in a teaching repo — verify against `app/mcp_tools.py` before quoting numbers.

**`reason` node (node 6) synthesizes prose via the official `anthropic` Python SDK** (`AsyncAnthropic`), reading `ANTHROPIC_API_KEY` and `CLAUDE_MODEL` from the backend `.env`. It degrades gracefully to a stub if no key is set. `anthropic>=0.113.0` is a backend dependency. Provider order is **Anthropic preferred**, then Azure OpenAI, then OpenAI as ordered fallbacks (`app/langgraph/flow.py`, `async def reason`).

### CoALA Tier Map (Sumers et al. 2024)

| Tier | Storage | LangGraph node | Read tools | Write tools |
|------|---------|----------------|------------|-------------|
| Working | `data/scratchpad/notes.db` | `inject_scratchpad` | `warn_scratchpad_read` | `warn_scratchpad_write` |
| Episodic | `data/episodic/events.db` | `recall_episodes` (gated to ANALYTICS/DIAGNOSTIC) + `log_episode` (always) | `warn_episodic_recall/recent/stats` | `warn_episodic_log` (auto) |
| Semantic | Vector store (Chroma/Azure/JSON) | `retrieve` | `warn_semantic_search`, `warn_get_robot`, `warn_list_robots` | `warn_index_schematic`, `warn_consolidate_memory` |
| Procedural | `@mcp.prompt()` registrations | not in pipeline (user-invoked) | `memory://procedural-catalog` | source control + CI |

**Episodic recall** (`app/adapters/episodic_store.py`) — Park et al. formula:
```
total = α_recency · 0.5^(hours/half_life) + α_importance · stored + α_relevance · cosine(query, summary+content)
```
Per-event score breakdown returned by `warn_episodic_recall`. **Pedagogical simplification**: relevance is bag-of-words cosine, not embeddings — swap-in is at `_relevance()` → `memory.semantic_search()`.

**Consolidation** (`app/langgraph/consolidate.py`) — uses `ctx.sample()` to extract durable facts from recent scratchpad+episodic, writes to vector store as synthetic `Schematic` records (`id=FACT-*`, `category=consolidated_fact`, `model=MEMORY`), and logs an OBSERVATION back to episodic. **ADD-only** — no Mem0 AUDN dedup.

**Resources**: `memory://coala-overview` (live four-tier snapshot) and `memory://procedural-catalog` (5 prompts with version metadata).

### Knowledge Graph

`data/graph/knowledge.db` (NOT `data/graph.db` — older docs lied). 117 entities, 221 relationships across 6 predicates: `has_tag` (75), `compatible_with` (50), `belongs_to_model` (25), `has_category` (25), `has_status` (25), `contains` (21). `warn_add_relationship` also accepts legacy: `depends_on`, `manufactured_by`, `related_to`. Re-index with `uv run python scripts/index_graph.py`. The `query_graph` node activates for DIAGNOSTIC/ANALYTICS intents or explicit relationship mentions.

### Progressive Tool Loading

Per Anthropic's "code execution with MCP". `warn_search_tools(query, detail, limit)` and `warn_describe_tool(name)` self-exclude from search results, so `count` ≤ 26 when `total` = 28. See `docs/tutorials/progressive-tool-loading.md`.

### Key Files

- `app/main.py` — FastAPI app
- `app/mcp_tools.py` — all 28 tools, 12 resources, 5 prompts
- `app/langgraph/flow.py` — 9-node pipeline; `GraphState` carries `session_id` + `recalled_episodes`; `run_query()` auto-generates `sess-<uuid8>` when omitted
- `app/langgraph/consolidate.py` — sleep cycle
- `app/adapters/{episodic,scratchpad,graph,chroma,azure_search,json,coala_overview}_store.py`
- `app/models/{schematic,graph,scratchpad,episodic}.py`
- `data/schematics/schematics.json` — source of truth (25 robots)

### Teaching notebooks

`notebooks/segment-1.ipynb` .. `segment-4.ipynb` — one notebook per 50-min course segment, all prepopulated and verified to run **error-free headless** from BOTH the repo root and `notebooks/`. Each opens with a **repo-root anchor cell** that walks up to the `.git` marker, so paths resolve regardless of launch directory. Live counts (tools/resources/prompts) are printed at runtime, never hardcoded. Built and validated via the user-scope **`jupyter-notebook` skill** (scaffold + headless execute + per-cell error scan).

## Environment Variables (`src/warnerco/backend/.env`)

```bash
ANTHROPIC_API_KEY=...                     # read by the reason node (node 6)
CLAUDE_MODEL=claude-sonnet-4-6            # default model for the reason node
MEMORY_BACKEND=json                       # json | chroma | azure_search
SCRATCHPAD_DB_PATH=data/scratchpad/notes.db
SCRATCHPAD_INJECT_BUDGET=1500
EPISODIC_DB_PATH=data/episodic/events.db
EPISODIC_MAX_RETRIEVAL_K=5
EPISODIC_RECENCY_HALF_LIFE_HOURS=24.0
EPISODIC_WEIGHT_RECENCY=0.4               # α_recency
EPISODIC_WEIGHT_IMPORTANCE=0.3            # α_importance
EPISODIC_WEIGHT_RELEVANCE=0.3             # α_relevance
AZURE_SEARCH_ENDPOINT=...
AZURE_SEARCH_KEY=...
AZURE_SEARCH_INDEX=warnerco-schematics
AZURE_OPENAI_ENDPOINT=...
AZURE_OPENAI_API_KEY=...
AZURE_OPENAI_DEPLOYMENT=gpt-4o-mini
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-ada-002
```

## MCP Client Configuration

Both `.vscode/mcp.json` and `.claude/mcp.json` are checked in, but they are **not symmetric** — VS Code was simplified for O'Reilly delivery:

- **`.claude/mcp.json`** (teaching dual-entry): registers the same `warnerco-mcp` binary twice — `warnerco-schematica-claude` (general entry) and `warnerco-coala-memory` (same binary, pre-pins `EPISODIC_*` env so demo weights are class-stable). Pedagogical clarity, not a runtime split — there is no separate CoALA process.
- **`.vscode/mcp.json`** (O'Reilly single-entry): one `oreilly-warnerco-schematica` server (`MEMORY_BACKEND=chroma`, `type: "stdio"`) plus the GitHub Copilot remote MCP server (`https://api.githubcopilot.com/mcp/`, PAT via `${input:github_pat}`). No `warnerco-coala-memory` entry, no `dev.watch`.

If asked to add a third client (Cursor, Continue, etc.), mirror the `.claude/mcp.json` dual-entry pattern when teaching CoALA, or the lean `.vscode/mcp.json` single-entry when you just need the server.

**Root keys differ**: VS Code uses `servers`; Claude Code uses `mcpServers`. VS Code requires `type: "stdio"|"http"|"sse"`; Claude Code defaults but set it explicitly. Variable expansion: VS Code `${env:VAR}` / `${workspaceFolder}` / `${input:id}`; Claude Code `${VAR}` / `${VAR:-default}` / absolute paths only.

**Claude Desktop** (Windows: `%APPDATA%\Claude\claude_desktop_config.json`):
```json
{ "mcpServers": { "warnerco": { "command": "uv", "args": ["run", "warnerco-mcp"], "cwd": "C:/github/context-engineering/src/warnerco/backend" } } }
```

## Testing with MCP Inspector

```bash
npx @modelcontextprotocol/inspector uv run warnerco-mcp   # http://localhost:5173
```

## Instructor Materials

- `instructor/course-plan-june-2026.md` — **canonical** course plan (context-first, delivered 2026-06-30): "consumer LLMs hide context, dev tools expose it", official-SDK-first, orchestration de-emphasized, GitHub Copilot first-class. The earlier orchestration-forward plan is archived at `instructor/archive/course-plan-april-2026-v1-ARCHIVED.md`.
- `instructor/COURSE-UPGRADE-RECOMMENDATIONS.md` — 12 ranked recommendations (P0/P1/P2) grounded in 2026 sources
- `instructor/PRE-CLASS-CHECKLIST.md` — morning-of verification flow
- `docs/tutorials/coala-explainer.md` — 15-min framework explainer with code pointers
- `docs/tutorials/coala-memory-walkthrough.md` — ~4-min classroom four-tier demo
- `docs/tutorials/progressive-tool-loading.md` — `warn_search_tools` / `warn_describe_tool` walkthrough

## Authoritative External Sources

When reasoning about MCP / context-engineering tradeoffs, prefer these over generic web search:

- **MCP spec 2025-11-25**: https://modelcontextprotocol.io/specification/2025-11-25 — current authoritative version. Three client capabilities: **Sampling, Roots, Elicitation**.
- **2026 MCP roadmap**: https://blog.modelcontextprotocol.io/posts/2026-mcp-roadmap/
- **Anthropic context engineering**: https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents — JIT loading, compaction, structured note-taking
- **Anthropic code execution with MCP**: https://www.anthropic.com/engineering/code-execution-with-mcp — progressive tool loading, ~98.7% token reduction. **Source for `warn_search_tools` / `warn_describe_tool`.**
- **Anthropic memory announcement**: https://www.anthropic.com/news/memory — managed-agents memory beta

When asked about MCP specifics, default-cite the 2025-11-25 spec.

## Claude Code Agents and Skills

- Agents: `python-mcp-server-expert` (FastMCP guidance), `azure-principal-architect` (Azure WAF)
- Skills: `mcp-server-builder` (Python/JS/TS), `warnerco-schematica` (this app)
