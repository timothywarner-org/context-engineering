# Context Engineering with MCP - Course Plan v2 (Context-First)

**Status:** DRAFT for Tim's review. Repositions the April 2026 plan around a single thesis. Does not replace `course-plan-april-2026.md` yet - keep both side by side until the v2 framing is approved.

## The thesis (the spine of all four segments)

> Consumer LLM front-ends **hide** context from you. Developer tools **expose** it. Context engineering is the craft of moving from the opaque view to the engineered view - and MCP is the standard lever for doing it.

A non-developer in ChatGPT, the Claude app, or Gemini gets **no clues** about the context window: no token meter, no warning before the top of the conversation is silently dropped. A developer in **Claude Code** or **GitHub Copilot in VS Code** sees context as a managed resource: files entering the window, `/context`, compaction, MCP servers loading tools on demand. The course walks the learner from opaque to engineered.

## What changed from v1, and why

| Change | v1 | v2 | Reason |
|--------|----|----|--------|
| **Cold open** | Token-window diagram + cost table (abstract) | Claude Code / Copilot vs consumer front-ends (concrete) | Lead with what every attendee has lived; the concepts land *after* the hook |
| **Orchestration** | LangGraph taught in Seg 3 + Seg 4 | LangGraph hidden; pipeline is a black box | Tim is de-emphasizing orchestration; the *memory tiers* are the lesson, not the graph |
| **SDK stance** | Mixed (fastmcp, mcp, langchain) | Official-first: `mcp` Python SDK + `anthropic` SDK | "Stay on official Anthropic SDKs"; LangChain/LangGraph become "aware of" |
| **GH Copilot** | One 10-min block in Seg 4 | First-class throughout (Seg 1 hook, Seg 4 deep-dive) | Strongest "context made visible" exhibit alongside Claude Code |
| **MCP framing** | Protocol mechanics | Protocol mechanics **+ current best-practice server/client craft** | Tim wants latest stable practices, not just "here's JSON-RPC" |

## Course structure

| Seg | Title | One-line topic |
|-----|-------|----------------|
| 1 | **Context, Made Visible** | Why consumer LLMs hide context and dev tools expose it; the concepts that comparison motivates |
| 2 | **MCP: The Standard for Working With Context** | The protocol + building a server on the **official** Python SDK; current best practices |
| 3 | **Memory Tiers in a Real App** | WARNERCO's four CoALA memory tiers, live - orchestration kept under the hood |
| 4 | **MCP in the Tools You Use** | Claude Code + GitHub Copilot in VS Code as context-engineering surfaces; client config craft |

---

## Segment 1: Context, Made Visible (50 min)

**Learning objectives**
- Contrast how consumer front-ends vs. developer tools surface (or hide) the context window
- Name the four ways context is lost (overflow, session boundary, attention dilution, compression loss)
- Read the context signals a developer tool gives you (Claude Code `/context`, Copilot's working set)
- Define context engineering as Capture / Store / Retrieve

**Cold open (10 min) - the comparison**
Side-by-side, live:
- **ChatGPT / Claude app (consumer):** paste a long doc, keep chatting, watch it silently forget the top. No meter, no warning. *"This is the default experience for most of the world."*
- **Claude Code (developer):** run `/context`, show the token budget, show files entering and a compaction event. *"Same model family, totally different relationship with context - because the tool exposes it."*
- **GitHub Copilot in VS Code (developer):** show the working-set / context picker - the IDE deciding what goes in the window, and letting you steer it.

Talk track: *"If you're not a dev, the front-end gives you almost no clues about context limits. Today we move to the other side of that glass."*

**Concepts the hook motivates (30 min)**
1. The context window as a finite, priced resource (keep the token-economics table - but now it *explains* what the room just watched)
2. The four types of context loss (overflow / session boundary / attention dilution / compression loss)
3. Why RAG is necessary but not sufficient - it retrieves, it doesn't *remember* or *manage*
4. Context engineering = Capture + Store + Retrieve; MCP named as the standard that operationalizes it

**Exercise (10 min):** in Claude Code, run `/context` before and after loading a large file; estimate the effective budget left for real work.

**Notebook:** `notebooks/segment-1.ipynb` (adapt: add a context-signals section; the Lab 01 anatomy can move to Seg 2 where the protocol is taught).

---

## Segment 2: MCP - The Standard for Working With Context (50 min)

**Learning objectives**
- Explain MCP's primitives (Tools / Resources / Prompts) and the three client capabilities (**Sampling / Roots / Elicitation**, per spec 2025-11-25)
- Build a minimal server on the **official `mcp` Python SDK** (`mcp.server.fastmcp`)
- Test it with MCP Inspector
- State current best practices: stdio for local, progressive tool loading, least-privilege

**Topics**
1. **Protocol mechanics (10 min):** JSON-RPC, the initialize/capabilities handshake, transports (stdio local-first; HTTP for remote). Cite spec **2025-11-25**.
2. **Primitives + capabilities (10 min):** Tools/Resources/Prompts the server offers; Sampling/Roots/Elicitation the client offers. This is the up-to-date capability set - drop the old "Sampling is a 4th primitive" framing.
3. **Build on the official SDK (15 min):** Lab 01 (JS) as the 60-second "what one tool looks like," then the same idea in Python on `mcp.server.fastmcp`. **Honesty note:** WARNERCO ships on standalone `fastmcp` (now Anthropic-stewarded); call out the difference between `from mcp.server.fastmcp import FastMCP` (official SDK) and `from fastmcp import FastMCP` (standalone) so nobody is surprised by the import.
4. **Inspector (5 min):** `npx @modelcontextprotocol/inspector` against the server.

**Current best practices to state plainly:**
- stdio for local, HTTP only when you need remote (with TLS)
- Progressive tool loading when a server grows past ~10 tools (Seg 4 shows WARNERCO's discovery tool)
- Least-privilege: only enable Sampling/elicitation a server actually needs
- Pin the spec version you target

**Notebook:** `notebooks/segment-2.ipynb` (already demos Lab 02's real primitives + the two-SDK distinction - extend with an official-SDK minimal server cell).

---

## Segment 3: Memory Tiers in a Real App (50 min)

**Framing:** orchestration stays under the hood. *"A query goes in, four kinds of memory light up, an answer comes out. How the nodes are wired is an implementation detail we won't dwell on."*

**Learning objectives**
- Name and distinguish the four CoALA tiers (Working / Episodic / Semantic / Procedural)
- See each tier read/written via an MCP primitive
- Trigger consolidation (the "sleep cycle") and observe cross-tier side effects
- Map each tier to a storage choice (SQLite / vector / prompt registration)

**Topics (orchestration-free narration)**
1. **The four tiers (10 min):** the CoALA vocabulary as a *mental model*, mapped to WARNERCO storage. No LangGraph diagram on screen.
2. **Live demo (25 min):** the existing four-tier walkthrough - scratchpad write, semantic search, episodic recall with the Park et al. score breakdown, consolidation, coala-overview close-the-loop. The 9-node pipeline runs; you just don't teach it. (`notebooks/segment-3.ipynb` already treats it as a black box.)
3. **Where each tier lives (10 min):** SQLite for working/episodic, vector store for semantic, `@mcp.prompt()` for procedural.
4. **Reason node (5 min):** prose synthesis now via the **`anthropic` API** (one verified course key). *Decision flagged below.*

**Notebook:** `notebooks/segment-3.ipynb` (works as-is; remove any LangGraph-teaching language from markdown, keep the live tier demo).

---

## Segment 4: MCP in the Tools You Use (50 min)

**Framing:** close the loop from Seg 1 - the dev tools that *expose* context are also MCP *clients*. Now you wire your own server into them.

**Learning objectives**
- Configure Claude Code with a custom MCP server (`.claude/mcp.json`)
- Configure GitHub Copilot in VS Code (`.vscode/mcp.json`) - schema differences and the input/PAT flow
- Use progressive tool loading to keep a 28-tool server cheap
- State production basics (auth, transport, monitoring) without a LangGraph detour

**Topics**
1. **Progressive tool loading (10 min):** `warn_search_tools` / `warn_describe_tool` - load schemas on demand. Live: `count=20` default-capped, `26` with `limit=100`, of `28` total. The "code execution with MCP" pattern.
2. **Claude Code as an MCP client (12 min):** the real `.claude/mcp.json` (two entries, pinned CoALA weights). Show context made visible: tools loading, `/context`.
3. **GitHub Copilot in VS Code (12 min) - FIRST-CLASS:** the real `.vscode/mcp.json` (your server + GitHub's remote MCP). Schema contrasts (`servers` vs `mcpServers`, required `type`, `${input:github_pat}`). Agent mode picking up both servers.
4. **Production basics (6 min):** stdio vs HTTP, auth on remote, monitoring. Mention LangGraph/LangChain here as **one ecosystem option** for multi-agent - not taught, just situated.

**Notebook:** `notebooks/segment-4.ipynb` (already demos progressive loading + both client configs live).

---

## Open decisions for Tim (before I touch notebooks)

1. **~~`anthropic` SDK vs raw httpx in the reason node.~~ DONE.** The reason node now uses the official `anthropic` SDK (`AsyncAnthropic`), added to the backend deps. Verified: `run_query` returns live grounded prose via the SDK. The demo no longer calls raw HTTP while teaching the SDK.

2. **WARNERCO on standalone `fastmcp` vs official `mcp.server.fastmcp`.** The flagship imports `from fastmcp import FastMCP`. Migrating to the official SDK is a real refactor (decorators differ subtly). Options: (a) keep standalone, label it clearly as Anthropic-stewarded; (b) migrate WARNERCO to the official SDK (significant, not a night-before move); (c) build a *small* official-SDK server for Seg 2 and keep WARNERCO standalone for Seg 3. **(c) is my recommendation** - teaches the official path without risking the flagship.

3. **Lab 01 placement.** v2 moves the Lab 01 anatomy from Seg 1 into Seg 2 (where the protocol is actually taught). Confirm that's the right home.

4. **Does Seg 3 keep the consolidation/"sleep cycle" exercise?** It's the strongest memory-engineering moment but it's also the most orchestration-flavored. Keep as a demo, drop as an exercise, or keep both?
