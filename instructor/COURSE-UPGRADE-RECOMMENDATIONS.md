# Course Upgrade Recommendations — "Best Run Ever" Edition

**Owner:** Tim Warner
**Date:** 2026-04-26
**For:** Context Engineering with MCP — class 2026-06-30 and beyond

This memo nominates targeted, high-leverage changes informed by the latest Anthropic
engineering posts and the **MCP 2025-11-25** specification. Each recommendation is
ranked **P0 (do before tomorrow)**, **P1 (this week)**, or **P2 (next iteration)** with
the source that motivated it.

---

## Executive Summary

The repo is **green** for tomorrow. The recommendations below are about staying on the
front edge of the spec and Anthropic's latest engineering guidance. Three themes
dominate the 2026 narrative:

1. **Context as a finite attention budget** — JIT loading, compaction, structured notes
   ([Anthropic context engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)).
2. **Code execution with MCP** — load tools on demand, filter data before it reaches
   the model, ~98% token reduction ([Anthropic code execution with MCP](https://www.anthropic.com/engineering/code-execution-with-mcp)).
3. **Spec maturity** — 2025-11-25 is the current spec; Tasks, Elicitation, and
   stateless transports dominate the [2026 roadmap](https://blog.modelcontextprotocol.io/posts/2026-mcp-roadmap/).

WARNERCO already demonstrates pillars 1 and 2 well. Closing the gap on pillar 3 (spec
currency) and adding a few teachable contrasts will turn this into a standout course.

---

## P0 — Before Tomorrow's Class (≤30 min each)

### 1. Verify spec currency in the slide deck and one tutorial
**Why:** The current spec is **2025-11-25**, listing **Sampling, Roots, Elicitation**
as the three client capabilities. Many older course materials reference the
2024-11-05 / 2025-03-26 spec only.
**Where to apply:**
- `instructor/context-engineering-unified-jan2026.pptx` — confirm Elicitation is named
  alongside Sampling and Roots.
- `docs/diagrams/mcp-primitives.md` — confirm three client capabilities are listed.
**Source:** [MCP Specification 2025-11-25](https://modelcontextprotocol.io/specification/2025-11-25)

### 2. Add one "context budget" framing slide
**Why:** Anthropic's headline framing for 2026 is "context is a finite attention
budget." This sentence reframes the whole course in students' minds.
**Suggested phrasing:** "Context engineering = finding the smallest set of high-signal
tokens that reliably produce the desired behavior."
**Source:** [Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)

### 3. Confirm the graph DB is on disk
**Done as part of this audit.** `data/graph/knowledge.db` now contains:
- 117 entities (25 schematics + 12 categories + 12 components + 9 models + 56 tags + 3 statuses)
- 221 relationships across 6 predicates
**Demo-ready** for `warn_graph_neighbors`, `warn_graph_path`, `warn_graph_stats`.

---

## P1 — This Week (post-class polish, ≤2 hr each)

### 4. Add a "Progressive Tool Loading" lab or demo segment
**Why:** Anthropic's code-execution-with-MCP post reports a **98.7% token reduction**
(150K → 2K) by loading tool definitions from a filesystem on demand instead of pinning
all schemas. This is the single most viral idea in MCP teaching right now.
**Where:** a 10-min demo in Segment 4 (shipped as `warn_search_tools` / `warn_describe_tool` plus `docs/tutorials/progressive-tool-loading.md`).
**Concrete demo:** Show WARNERCO's 28 tools loaded normally, then show `warn_search_tools`
exposing only matching tool schemas.
**Source:** [Code execution with MCP](https://www.anthropic.com/engineering/code-execution-with-mcp)

### 5. Add Elicitation to WARNERCO as a teaching contrast
**Why:** Elicitation (server requests structured data from the user mid-conversation)
is a 2025-11-25 capability most courses skip. WARNERCO's `warn_create_schematic` is a
natural fit — the server can elicit missing fields instead of failing validation.
**Where:** `app/mcp_tools.py` — wrap `warn_create_schematic` with an elicitation
fallback when required fields are missing.
**Source:** [MCP Elicitation spec](https://modelcontextprotocol.io/specification/draft/client/elicitation)

### 6. Document the "memory vs scratchpad vs graph" decision matrix
**Why:** WARNERCO uniquely demonstrates **three** memory layers, but students will
struggle to internalize *when* to use which. A single comparison table beats five
paragraphs.
**Where:** New section in `docs/tutorials/graph-memory-tutorial.md` or a standalone
`docs/MEMORY-DECISION-MATRIX.md`.
**Suggested table:**

| Need | Use | Latency | Persistence |
|---|---|---|---|
| "Things similar to X" | Vector (Chroma / Azure Search) | ~50ms | Permanent |
| "Things connected to X" | Graph (SQLite + NetworkX) | ~5ms | Permanent |
| "What did we just discuss?" | Scratchpad | <1ms | Session |
| "What did we learn last week?" | Anthropic memory tool / files | varies | Cross-session |

**Source:** Synthesis of [Anthropic memory announcement](https://www.anthropic.com/news/memory) +
[context engineering post](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents).

### 7. Add a compaction demo slide
**Why:** Anthropic's recommendation: "maximize recall first, then iterate to improve
precision." This is teachable in 5 minutes and directly justifies the
`compress_context` node in the LangGraph flow.
**Where:** Add narration to the existing `langgraph-flow.svg` walkthrough.
**Source:** [Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)

---

## P2 — Next Iteration (course v2, ≤1 day each)

### 8. Spec-version annotation on every MCP code sample
**Why:** Help students mentally diff what changed. Add a header to every YAML/JSON
code sample: `# MCP spec: 2025-11-25`. Future you will thank present you when
2026-XX-XX ships.

### 9. New "MCP at scale" segment based on the 2026 roadmap
**Why:** The roadmap explicitly calls out "stateful sessions fight with load
balancers, horizontal scaling requires workarounds." Adding a 15-min "MCP in
production" segment covering stateless sessions, `.well-known` server discovery, and
gateway patterns turns the course from "intro" into "intermediate."
**Source:** [2026 MCP Roadmap](https://blog.modelcontextprotocol.io/posts/2026-mcp-roadmap/)

### 10. Where the patterns above landed (lab ladder, as shipped)
The four real labs on disk are the ladder; the patterns from recs #4-#7 are folded into
WARNERCO and the tutorials rather than into separate numbered labs.

- **Lab 01** (`labs/lab-01-hello-mcp/`): Hello MCP, single `add` tool, JS.
- **Lab 02** (`labs/lab-02-mcp-chat/`): MCP Chat CLI — complete Python client + stdio server + REPL.
- **Lab 03** (`labs/lab-03-mcp-apps/`): MCP Apps — interactive `ui://` surfaces in Claude Desktop (SEP-1865).
- **Lab 04** (`remote-mcp-apim-functions-python/`): Remote MCP secured by Entra ID OAuth via APIM (the production-deployment pattern, deployed live in Azure).

Patterns delivered without a separate lab number:
- **Progressive tool loading** (rec #4): shipped as `warn_search_tools` / `warn_describe_tool` plus `docs/tutorials/progressive-tool-loading.md`.
- **Sampling** (rec #5 sibling): shipped in `warn_explain_schematic` + `warn_consolidate_memory`, walked through in `docs/tutorials/demo-sampling-vscode.md`.
- **Elicitation** (rec #5): demonstrated by the interactive tools (`warn_guided_search`, `warn_feedback_loop`, `warn_replacement_advisor`).
- **Hybrid memory** (rec #6): covered by `docs/tutorials/graph-memory-tutorial.md` and the four-tier CoALA walkthrough.

### 11. Add a "Tool Design Anti-Patterns" appendix
**Why:** Anthropic explicitly calls out: bloated toolsets, overlapping functionality,
exhaustive edge-case enumerations, hardcoded if-else logic. WARNERCO's 28 tools are a
useful case study — some (like `warn_explain_schematic` vs `warn_get_robot`) walk
right up to the overlap line and would generate great discussion.

### 12. Add the Anthropic "Memory for Managed Agents" beta as a forward-looking slide
**Why:** Memory is in public beta as of `managed-agents-2026-04-01`. Mentioning it
positions the course as current and gives students a "what's next" hook.
**Source:** [Memory for Claude Managed Agents](https://docs.anthropic.com/en/release-notes/overview)

---

## What NOT to Change

- **Don't rebuild the LangGraph flow.** The 9-node hybrid RAG pipeline is unusually
  well-aligned with the 2026 agentic-RAG patterns (plan → retrieve → reason → respond
  with hybrid memory across all four CoALA tiers). It's a strength.
- **Don't rename the 28 tools.** They're frozen and tested. Surface the overlap as
  *teaching material* (rec #11), not as cleanup.
- **Don't gate Lab 01 on the new labs.** Lab 01 is the entry point and works as-is.

---

## Verification Checklist (before walking into class)

- [ ] `data/graph/knowledge.db` exists ✅ (done by this audit)
- [ ] `uv run warnerco-serve` starts on `http://localhost:8000`
- [ ] `/dash`, `/dash/schematics/`, `/dash/memory/`, `/dash/scratchpad/` all load
- [ ] MCP Inspector connects: `npx @modelcontextprotocol/inspector uv run warnerco-mcp`
- [ ] `warn_graph_stats` returns 117 entities / 221 relationships
- [ ] `warn_semantic_search` returns results for "actuator"
- [ ] `warn_scratchpad_write` then `warn_scratchpad_read` round-trips

---

## Sources

- [Effective context engineering for AI agents — Anthropic](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
- [Code execution with MCP — Anthropic](https://www.anthropic.com/engineering/code-execution-with-mcp)
- [Claude introduces memory for teams — Anthropic](https://www.anthropic.com/news/memory)
- [MCP Specification 2025-11-25](https://modelcontextprotocol.io/specification/2025-11-25)
- [The 2026 MCP Roadmap](https://blog.modelcontextprotocol.io/posts/2026-mcp-roadmap/)
- [MCP Elicitation (draft)](https://modelcontextprotocol.io/specification/draft/client/elicitation)
- [MCP Sampling (draft)](https://modelcontextprotocol.io/specification/draft/client/sampling)
