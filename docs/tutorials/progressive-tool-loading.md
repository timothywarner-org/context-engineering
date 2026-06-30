# Tutorial: Progressive Tool Loading for MCP Servers

This hands-on tutorial teaches you to use the **progressive tool-loading** pattern in WARNERCO Schematica. You will measure the cost of dumping every tool schema into context up front, then use two small discovery tools - `warn_search_tools` and `warn_describe_tool` - to slash that cost without losing any capability.

## Learning Objectives

By the end of this tutorial, you will:

- Understand why "load all tool schemas" scales badly as servers grow
- Measure the real token cost of WARNERCO's 28 tools at three detail levels
- Use `warn_search_tools` to discover tools by keyword and detail level
- Use `warn_describe_tool` to fetch one full schema on demand
- Decide when this pattern is worth the extra round-trip and when it is not

## Prerequisites

Before starting, ensure you have:

- WARNERCO Schematica running locally (Python 3.13, `uv sync`, see [STUDENT_SETUP_GUIDE.md](../STUDENT_SETUP_GUIDE.md))
- Familiarity with MCP tool calls (review the [Graph Memory tutorial](graph-memory-tutorial.md) if needed)
- Claude Desktop, VS Code with MCP, or the MCP Inspector

### Quick Setup Check

```bash
cd src/warnerco/backend
uv sync
uv run uvicorn app.main:app --reload
```

Visit http://localhost:8000/docs to confirm the API is running. In a second terminal:

```bash
npx @modelcontextprotocol/inspector uv run warnerco-mcp
```

You should see **28 tools** listed.

## Part 1: The Problem (10 minutes)

### Why Pre-Loading Every Schema Hurts

The default MCP handshake sends every tool's full JSON schema to the client at connect time. The client (and therefore the model) pays that cost on every turn that includes the tool list.

For a small server (3-5 tools) this is fine. For a maturing server it gets expensive fast. Anthropic's engineering team described this exact failure mode in [Code execution with MCP](https://www.anthropic.com/engineering/code-execution-with-mcp), where they observed agents hitting context exhaustion mostly because of pre-loaded tool definitions.

### Measure It on This Server

WARNERCO Schematica registers 28 tools. The full schema dump - description plus JSON input schema for every tool - measures:

| Detail level | Tokens for 28 tools | Per-tool cost | Saving vs. full |
|--------------|---------------------|---------------|-----------------|
| `full` (default MCP behavior) | ~9064 | ~394 | baseline |
| `summary` (name + first docstring line) | ~533 | ~23 | **94.1%** |
| `name` (name only) | ~176 | ~7.7 | **98.1%** |

(Numbers measured against the live server with `tiktoken` cl100k_base. They will drift as tools are added or descriptions edited - re-measure with `warn_search_tools` whenever you want fresh figures.)

A `summary` listing buys back roughly **8.5K tokens** of context per turn. On a 200K-token model that may sound trivial; on a 32K-context client it is the difference between "agent works" and "agent forgets the user's question."

### The Fix in One Sentence

> Stop sending every schema by default. Send a tiny index. Let the model ask for the one schema it actually needs.

That is exactly what `warn_search_tools` and `warn_describe_tool` do.

## Part 2: The Two Tools (5 minutes)

Both tools live in `app/mcp_tools.py` and use FastMCP's `mcp.get_tools()` introspection - no extra registry, no duplicated metadata.

### `warn_search_tools(query, detail, limit)`

Discover tools by keyword without loading every full schema.

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `query` | `str` | `""` | Case-insensitive substring matched against tool name and description. Empty string returns all tools. |
| `detail` | `"name" \| "summary" \| "full"` | `"summary"` | How much to return per tool. |
| `limit` | `int` | `20` | Max tools returned (capped at 100). |

Returns a `ToolSearchResult` with: `query`, `detail`, `count` (matched), `total` (registered), and `tools` (list of dicts at the requested detail level). The tool excludes itself and `warn_describe_tool` from results to avoid recursive confusion in demos.

### `warn_describe_tool(name)`

Return the full schema for one tool by name.

| Argument | Type | Description |
|----------|------|-------------|
| `name` | `str` | Exact tool name, e.g. `"warn_semantic_search"`. |

Returns a dict with `name`, `description`, `inputSchema`, and `outputSchema`. Raises `ValueError` if the name is unknown - so the model gets a hard signal to call `warn_search_tools` again instead of hallucinating.

### Mental Model

```
Old way:                          Progressive way:
+----------------------+          +-------------------------+
| handshake: 28 full   |          | handshake: 2 tools      |
| schemas (~9K tokens) |          | (search + describe)     |
+----------+-----------+          +-----------+-------------+
           |                                  |
           v                                  v
     model picks one              model: search_tools("graph")
     of 28 it can see                        |
                                             v
                                  ~140 tokens of summaries
                                             |
                                             v
                                  model: describe_tool("warn_graph_neighbors")
                                             |
                                             v
                                  ~400 tokens for one schema
                                             |
                                             v
                                  model calls the tool
```

Total spent on tool plumbing: roughly **600 tokens** instead of **9000+**, and the model only ever loaded the schema it actually used.

## Part 3: Three Worked Examples (15 minutes)

Run these in MCP Inspector. Each example also shows the equivalent direct Python call - useful for tests and for understanding what the model sees.

### Example A: Cheap Discovery - "what is on this server?"

Goal: get a complete inventory at minimum cost. Use `detail="name"`.

In MCP Inspector, call `warn_search_tools` with:

```json
{
  "query": "",
  "detail": "name"
}
```

Expected (truncated):

```json
{
  "query": "",
  "detail": "name",
  "count": 20,
  "total": 28,
  "tools": [
    {"name": "warn_add_relationship"},
    {"name": "warn_compare_schematics"},
    {"name": "warn_create_schematic"},
    {"name": "warn_delete_schematic"},
    {"name": "warn_explain_schematic"},
    {"name": "warn_feedback_loop"},
    {"name": "warn_get_robot"},
    {"name": "warn_graph_neighbors"},
    {"name": "warn_graph_path"},
    {"name": "warn_graph_stats"}
  ]
}
```

Note `count: 20` vs `total: 28`: the search tool excludes itself and `warn_describe_tool` from results, and the default `limit=20` caps the listing at 20 (pass `limit=100` to see all 26 non-meta tools).

This payload is ~176 tokens. Compare with the ~9064 tokens of dumping every full schema. **98% cheaper, same coverage.**

### Example B: Narrowing - "show me the graph stuff"

Goal: just enough info to choose the right tool. Use `detail="summary"`.

```json
{
  "query": "graph",
  "detail": "summary"
}
```

Expected:

```json
{
  "query": "graph",
  "detail": "summary",
  "count": 4,
  "total": 28,
  "tools": [
    {
      "name": "warn_add_relationship",
      "summary": "Create a triplet (subject, predicate, object) in the knowledge graph."
    },
    {
      "name": "warn_graph_neighbors",
      "summary": "Return entities directly connected to the given entity."
    },
    {
      "name": "warn_graph_path",
      "summary": "Return the shortest path between two entities, if one exists."
    },
    {
      "name": "warn_graph_stats",
      "summary": "Return node count, edge count, and density of the knowledge graph."
    }
  ]
}
```

The model now has four candidates and a one-line reason to pick each. Roughly 120 tokens.

### Example C: Drill-In - "I want the full schema for one tool"

Goal: get the exact JSON schema before calling. Use `warn_describe_tool`.

```json
{
  "name": "warn_graph_neighbors"
}
```

Expected (abridged):

```json
{
  "name": "warn_graph_neighbors",
  "description": "Return entities directly connected to the given entity...",
  "inputSchema": {
    "type": "object",
    "properties": {
      "entity_id": {"type": "string"},
      "direction": {
        "type": "string",
        "enum": ["incoming", "outgoing", "both"],
        "default": "both"
      },
      "limit": {"type": "integer", "default": 50}
    },
    "required": ["entity_id"]
  },
  "outputSchema": { ... }
}
```

Now the model has exactly the contract it needs - and only for the tool it is about to invoke.

## Part 4: Testing the Pattern (10 minutes)

### Via MCP Inspector

1. Start the stdio server with `npx @modelcontextprotocol/inspector uv run warnerco-mcp` from `src/warnerco/backend`.
2. Open the Inspector UI at http://localhost:6274.
3. In the **Tools** tab, find `warn_search_tools` and run the three example payloads above.
4. Then run `warn_describe_tool` with `{"name": "warn_graph_neighbors"}`.

The Inspector shows the raw response and approximate size, so you can confirm the token math against your own model's tokenizer.

### Via Direct Python

Useful for unit tests and for the deeper "I want to see the function, not the protocol" view. FastMCP exposes the underlying Python callable as `tool.fn`:

```python
import asyncio
from app.mcp_tools import mcp

async def demo():
    tools = await mcp.get_tools()

    # Example A: cheapest possible inventory
    res = await tools["warn_search_tools"].fn(query="", detail="name")
    print("Inventory:", res.count, "tools")

    # Example B: narrow to graph
    res = await tools["warn_search_tools"].fn(query="graph", detail="summary")
    for t in res.tools:
        print(f"  {t['name']}: {t['summary']}")

    # Example C: full schema for one tool
    schema = await tools["warn_describe_tool"].fn(name="warn_graph_neighbors")
    print("Schema keys:", list(schema.keys()))

asyncio.run(demo())
```

Run it from the backend folder:

```bash
cd src/warnerco/backend
uv run python -c "
import asyncio
from app.mcp_tools import mcp

async def demo():
    tools = await mcp.get_tools()
    res = await tools['warn_search_tools'].fn(query='', detail='name')
    print(f'count={res.count} total={res.total}')

asyncio.run(demo())
"
```

You should see `count=20 total=28` (the default `limit=20` caps the listing; the two discovery tools also omit themselves from results).

## Part 5: When NOT to Use This

Progressive tool loading is not free - you trade one big upfront cost for two small ones plus a discovery round-trip. Skip it when:

- **The server has fewer than ~10 tools.** Below that, the full schema dump is already small (a few thousand tokens). The extra round-trip and the cognitive overhead of "search then describe" cost more than they save.

- **The client already caches schemas across turns.** Some clients (notably IDE-integrated ones with their own tool indexes) only pay the schema cost once per session, not per turn. The savings shrink dramatically.

- **Your workflow is single-call and latency-sensitive.** A voice assistant that answers in one tool call does not benefit from a discovery hop - it benefits from having every tool in front of the model immediately.

- **Tools change every request and the index would never be cached.** Progressive loading assumes the inventory is reasonably stable. If your registry mutates per request, the discovery step becomes its own bottleneck.

If two or more of those conditions apply, keep the default behavior and revisit when the server grows.

## Summary

You have learned:

1. **Cost the problem first.** WARNERCO's 28 tools cost ~9064 tokens fully expanded, ~533 in summary form, ~176 by name. Measure your own server before deciding it is "fine."

2. **Two-step discovery beats blast-everything.** `warn_search_tools` returns a tiny index; `warn_describe_tool` returns one full schema on demand. Together they replicate the "code execution with MCP" pattern Anthropic published.

3. **Detail levels are a knob, not a setting.** `name` for inventory, `summary` for choosing, `full` only when you really do want the schema in the listing.

4. **The pattern has a sweet spot.** Use it on servers with many tools, in clients that re-send schemas every turn, in workflows that tolerate one extra hop. Skip it elsewhere.

## Exercises

**Exercise 1**: Run `warn_search_tools` with `detail="full"` and `limit=100`, capture the response, and count tokens with the tokenizer your client uses. Compare to your own measurement of `detail="summary"`. Does the ratio match the ~94% saving claimed above?

**Exercise 2**: Use `warn_search_tools(query="scratchpad", detail="summary")` and pick the right tool to clear all scratchpad entries older than 5 minutes. Confirm via `warn_describe_tool` before calling it.

**Exercise 3**: In your own MCP server (Lab 01 or otherwise), add a `search_tools` analog. How small can you make the per-tool footprint without losing the ability to choose correctly?

## References

- Anthropic Engineering, *Code execution with MCP*: <https://www.anthropic.com/engineering/code-execution-with-mcp>
- Tool source: `src/warnerco/backend/app/mcp_tools.py` (search for `warn_search_tools` and `warn_describe_tool`)
- Related tutorial: [Graph Memory for Context Engineering](graph-memory-tutorial.md)

## Troubleshooting

**`warn_search_tools` returns `count: 20` but I expected 28**

That is correct. Two things shrink the listing: the default `limit=20` caps the rows returned, and the discovery tools intentionally omit themselves and each other from results so the index does not advertise the index machinery. Use `total` (28) to confirm the real registered count, and pass `limit=100` to see all 26 non-meta tools.

**`warn_describe_tool` raises ValueError**

The `name` argument is exact-match and case-sensitive. Re-run `warn_search_tools` with no query to copy the exact spelling.

**Token counts do not match the table**

The numbers above were measured with cl100k_base against the live server on 2026-04-26. Descriptions drift. Re-measure with your client's tokenizer for current figures.
