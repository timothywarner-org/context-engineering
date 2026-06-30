# Classroom Walkthrough — All Four CoALA Memory Tiers

**Audience:** Tim teaching live to developers learning context engineering.
**Duration:** ~4 minutes for the demo path; ~15-20 minutes if you narrate every tier.
**Goal:** Show working / episodic / semantic / procedural memory exercised in one continuous turn-by-turn scenario, then promote a short-term observation into long-term knowledge via the consolidation cycle.

Reference: Sumers et al. (2024), *Cognitive Architectures for Language Agents* (CoALA).

---

## Pre-flight (do this once before class)

```bash
cd src/warnerco/backend

# 1. Confirm Python 3.13 + uv
uv sync

# 2. Index Chroma (semantic memory) and the knowledge graph
uv run python -c "from app.adapters.chroma_store import ChromaMemoryStore; import asyncio; asyncio.run(ChromaMemoryStore().index_all())"
uv run python scripts/index_graph.py

# 3. (Optional) wipe episodic + scratchpad so the class starts from zero
rm -f data/episodic/events.db data/scratchpad/notes.db

# 4. Free port 8000 if anything is squatting on it, then start fresh
uv run warnerco-restart
```

Server should be up at <http://localhost:8000>. Open <http://localhost:8000/docs> to confirm.

For the MCP-side demo, in a second terminal:

```bash
npx @modelcontextprotocol/inspector uv run warnerco-mcp
# Opens http://localhost:6274
```

---

## The four-tier mental model (slide before the demo)

| CoALA Tier | What it stores | Backed by | Lives where |
|------------|----------------|-----------|-------------|
| **Working** | This-session observations & inferences | Scratchpad SQLite | `data/scratchpad/notes.db` |
| **Episodic** | Timestamped past events with importance | Events SQLite | `data/episodic/events.db` |
| **Semantic** | Durable, generalizable facts | Vector store (Chroma/Azure/JSON) | `data/chroma/` |
| **Procedural** | Versioned skills/workflows | MCP Prompts | source code |

**Tell the class:** "Vector search finds *similar* things. Graphs find *connected* things. Scratchpad remembers *this session*. Episodic remembers *past sessions*. Procedural memory is the *skills the agent can perform*. We're going to see all four light up in a single continuous demo."

---

## The 4-minute demo path

The whole flow uses one stable `session_id="class-demo"` so episodic recall accumulates coherently across turns.

### Step 0 — Show the empty four-tier overview

In MCP Inspector, read the resource:

```
memory://coala-overview
```

Expect a JSON snapshot with:
- `working.current_count`: 0
- `episodic.current_count`: 0
- `semantic.current_count`: 25 (the indexed schematics)
- `procedural.current_count`: 5 (the registered prompts)

**Narrate:** "Procedural memory is already populated — it's source code, not data we accumulate. Semantic has the 25 robot schematics we indexed. Working and episodic start empty."

### Step 1 — Working memory: write a session observation

Call the tool:

```
warn_scratchpad_write
  subject:    "WRN-00006"
  predicate:  "observed"
  object_:    "thermal_system"
  content:    "Operator reports thermal subsystem trips during heavy hydraulic load"
  minimize:   true
  enrich:     true
```

**Narrate:** "This is *working memory* — a note we just took *during this session*. It's not a fact we'd commit to long-term knowledge yet. We've used the LLM to minimize the text and to enrich it with context. Watch the token-savings line."

Optionally call `warn_scratchpad_stats` to show `tokens_saved` and `savings_percentage`.

### Step 2 — First diagnostic query (DIAGNOSTIC intent → episodic recall fires)

In MCP Inspector, call `warn_semantic_search` with these args:

```
warn_semantic_search
  query:      "thermal subsystem is failing on the hydraulics line"
  session_id: "class-demo"
  top_k:      5
```

**Narrate:** "First diagnostic turn. The pipeline hits 9 nodes — `parse_intent` classifies this as DIAGNOSTIC, `inject_scratchpad` adds the note we just took, `recall_episodes` runs but finds nothing yet (we have no past events), `retrieve` does vector search, `compress_context` glues it all together, `reason` thinks, `respond` formats, and `log_episode` records this turn into episodic memory."

In the response, point out:
- `intent: "diagnostic"` — the gate passed
- `session_id: "class-demo"` — echoed back so students see it persisted
- `recalled_episodes: []` — no past events yet
- `total: <n>` — the vector store returned candidates

### Step 3 — Repeat the query (now episodic recall has something to find)

Call `warn_semantic_search` with the **exact same args** as Step 2 (same `session_id="class-demo"`).

**Narrate:** "Same query, second time. Now `recall_episodes` finds the prior turn — recency × importance × relevance scoring brings it back."

In the response, point out:
- `recalled_episodes: [...]` — at least 1 entry, formatted like `[2026-04-26T...] (user_turn, imp=0.60) Q: thermal subsystem is failing...`

Now call `warn_episodic_recall` directly to show the per-event score breakdown:

```
warn_episodic_recall
  query: "thermal hydraulic problems"
  k:     5
```

The response includes a `scores` array showing `{recency, importance, relevance, total}` for each event. **This is the Park et al. formula made visible.**

### Step 4 — LOOKUP intent skips episodic recall (gating demo)

Call:

```
warn_semantic_search
  query:      "get WRN-00006"
  session_id: "class-demo"
  top_k:      5
```

**Narrate:** "Pure ID lookup. Look at the response — `intent: lookup` and `recalled_episodes: []`. We deliberately gate episodic recall to ANALYTICS and DIAGNOSTIC. Lookups don't need session history; ungated recall just pollutes the context."

### Step 5 — Consolidation: promote working/episodic memory into semantic memory

Call the consolidation tool **from MCP Inspector** (it needs `ctx.sample()` so the host's LLM is invoked):

```
warn_consolidate_memory
  since_minutes: 60
  max_facts:     3
  session_id:    "class-demo"
```

**Narrate:** "This is the *sleep cycle*. The server reads our scratchpad notes and recent episodic events, asks YOUR LLM via MCP Sampling — server-initiated LLM calls, the most agentic primitive — to extract durable facts, and writes them as `FACT-*` records into the vector store. Notice the response: `facts_added`, `fact_ids`, and an `elapsed_ms` timing."

**Important client note:** Sampling requires a sampling-capable client. **Claude Desktop and FastMCP Client support it; MCP Inspector may not** depending on version. If sampling fails, narrate the fallback gracefully — the tool returns `success: false` with a clear message, and the class can see that "agentic primitives have a host-coverage gap" (from the research).

### Step 6 — Confirm the consolidated facts landed in semantic memory

Call:

```
warn_semantic_search
  query: "consolidated"
  top_k: 5
```

You should see `FACT-*` entries with `category: "consolidated_fact"` and `model: "MEMORY"`. **Working/episodic memory has now been promoted to semantic memory.**

Also call `warn_episodic_recent(limit=10)` and point out the `OBSERVATION` event: *"Consolidation promoted N facts to semantic memory"* — the act of consolidating is itself a memory.

### Step 7 — Show the procedural catalog

Read the resource:

```
memory://procedural-catalog
```

Expect 5 prompts (`diagnostic_prompt`, `comparison_prompt`, `search_strategy_prompt`, `maintenance_report_prompt`, `schematic_review_prompt`) with `version: "1.0.0"`.

**Narrate:** "Procedural memory is *versioned skills*. CoALA explicitly flags procedural writes as the riskiest memory operation — that's why MCP Prompts are user-invoked, not model-invoked. They live in source control; CI publishes versions. The class can see them in their slash-command UI."

### Step 8 — Final overview (the closer)

Read again:

```
memory://coala-overview
```

All four `current_count` values are now non-zero:
- `working`: ≥ 1 (from Step 1)
- `episodic`: ≥ 4 (3 user turns + 1 OBSERVATION from consolidation)
- `semantic`: 25 + N (original schematics + consolidated facts)
- `procedural`: 5

**Closer line:** "Four CoALA tiers, four MCP primitives, one continuous turn-by-turn scenario. Working memory got the in-flight observation. Episodic memory remembered every turn with timestamps. Semantic memory absorbed the consolidated facts. Procedural memory was always there as versioned skills. *That's context engineering.*"

---

## Quick reference — fallbacks if MCP Inspector is fussy

Most of the demo is MCP-Inspector-only because:
- Scratchpad **writes** are MCP tools (`warn_scratchpad_write`), not REST endpoints
- Resources (`memory://coala-overview`, `memory://procedural-catalog`) are MCP-only by design
- `ctx.sample()` for `warn_consolidate_memory` requires a sampling-capable client

The FastAPI side is read-mostly and good for sanity-checking state:

```bash
# Search via REST — does NOT pass session_id, so episodic recall won't fire from here.
# Use this to sanity-check the vector store works, not to demo the four tiers.
curl -X POST http://localhost:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{"query":"thermal subsystem failures","top_k":5}'

# Read-only state checks
curl http://localhost:8000/api/memory/stats             # semantic backend stats
curl http://localhost:8000/api/scratchpad/stats         # working memory stats
curl http://localhost:8000/api/scratchpad/entries       # working memory entries
curl http://localhost:8000/api/graph/stats              # knowledge graph stats

# Direct SQLite peek when you want to skip the layer entirely
sqlite3 data/episodic/events.db   "select id, kind, importance, summary from events order by created_at desc"
sqlite3 data/scratchpad/notes.db  "select subject, predicate, content from entries order by created_at desc"
sqlite3 data/graph/knowledge.db   "select count(*) from entities; select count(*) from triplets;"
```

API docs are at <http://localhost:8000/docs>.

---

## Common things that go sideways

| Symptom | Cause | Fix |
|---------|-------|-----|
| `recalled_episodes: []` on Turn 2 | Different `session_id` per turn (auto-generated) | Pass the same `session_id="class-demo"` explicitly |
| Turn 2 was classified `lookup` instead of `diagnostic` | Query contained `WRN-` substring | Phrase queries without IDs in Steps 2-3; use ID only in Step 4 |
| `warn_consolidate_memory` returns `success: false` | Client doesn't support sampling | Use Claude Desktop or FastMCP Client; Inspector versions vary |
| Only 1 event in episodic but you ran 3 queries | Likely all 3 queries hit LOOKUP intent | Avoid `WRN-` IDs in the query text for diagnostic turns |
| `current_count: 0` for semantic | Chroma index is empty | Re-run `ChromaMemoryStore().index_all()` from pre-flight |
| Server won't start, port in use | Stale uvicorn process | `uv run warnerco-restart --kill-only` then `uv run warnerco-restart` |

---

## Going deeper after class

- **Bag-of-words → embeddings:** `app/adapters/episodic_store.py` uses tokenized cosine for relevance. Swap to embeddings by calling `memory.semantic_search()` from `_relevance()` — flagged in the file with `# CoALA NOTE`.
- **ADD-only consolidation → Mem0 AUDN:** add UPDATE/DELETE/NOOP semantics to `app/langgraph/consolidate.py` to dedupe against existing facts.
- **Bi-temporal edges (Zep/Graphiti):** add `t_valid` / `t_invalid` columns to `events` for fact-obsolescence demos.
- **Read the source reports:** `research_synthesis/` contains four independent deep-research reports (Claude, ChatGPT, Gemini, Perplexity) on agent memory architectures.
