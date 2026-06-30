# Demoing MCP Sampling in VS Code

This guide walks you through demonstrating MCP sampling using the WARNERCO Schematica server in VS Code. You will use the `warn_explain_schematic` tool to show how an MCP server can request LLM completions from the client -- a flow that inverts the normal tool-calling direction.

## What is MCP Sampling?

Most MCP interactions follow a simple pattern: the client's LLM decides to call a tool, the server runs it, and the server returns data. The LLM does the thinking; the server does the fetching.

Sampling flips this. With sampling, the **server** asks the **client's LLM** to generate content. The server provides raw data and a carefully crafted prompt, and the client's LLM does the reasoning.

```
Normal flow:
  Client (LLM) --calls tool--> Server --returns data--> Client (LLM)

Sampling flow:
  Client (LLM) --calls tool--> Server --asks LLM via ctx.sample()--> Client (LLM)
                                  ^                                       |
                                  |     LLM generates structured output   |
                                  +---------------------------------------+
  Server combines raw data + LLM reasoning --> returns enriched result to Client
```

Why does this matter? Because the server has **data** (schematics, specifications, graph relationships) and the LLM has **reasoning** (analysis, explanation, synthesis). Sampling lets one tool call produce results that neither the server nor the LLM could produce alone.

In concrete terms: `warn_explain_schematic` fetches a robot schematic from the database, optionally pulls graph relationships, then asks the client's LLM to generate a structured explanation tailored to a specific audience. The server orchestrates; the LLM reasons.

## Prerequisites

Before you begin, make sure you have:

- **VS Code** with one of the following extensions installed:
  - GitHub Copilot (Chat) -- requires a Copilot subscription
  - Claude extension for VS Code
- **Python 3.11+** and **uv** (the Python package manager)
- **Node.js 18+** (for the MCP Inspector)
- The `context-engineering` repository cloned locally
- Dependencies installed:

```bash
cd src/warnerco/backend
uv sync
```

If you plan to use the knowledge graph features, index the graph first:

```bash
cd src/warnerco/backend
uv run python scripts/index_graph.py
```

## Step 1: Configure the MCP Server in VS Code

VS Code discovers MCP servers through a `.vscode/mcp.json` file in your workspace root. This repository already includes one. Open it and verify the `vscode-warnerco-schematica` entry:

```json
{
  "servers": {
    "vscode-warnerco-schematica": {
      "command": "uv",
      "args": ["run", "warnerco-mcp"],
      "cwd": "${workspaceFolder}/src/warnerco/backend",
      "env": {
        "MEMORY_BACKEND": "chroma"
      },
      "type": "stdio"
    }
  }
}
```

Key details:

- **command/args**: Runs `uv run warnerco-mcp`, which starts the FastMCP server in stdio mode.
- **cwd**: Points to the backend directory so `uv` finds the correct `pyproject.toml`.
- **env**: Sets the memory backend. Use `"json"` for fastest startup (no embeddings needed) or `"chroma"` for semantic search support.
- **type**: Must be `"stdio"` for local MCP servers.

If you are using the Claude extension instead of GitHub Copilot, the same `.vscode/mcp.json` file works -- both extensions read the same configuration format.

After saving the file, restart VS Code or reload the window (Ctrl+Shift+P, then "Developer: Reload Window") so the extension picks up the server.

## Step 2: Start the Server

For the VS Code demo, the MCP client (Copilot or Claude) manages the server lifecycle automatically via stdio. You do not need to start the server manually -- VS Code launches it when you first interact with the chat.

However, if you want the HTTP API running simultaneously (for the dashboard or direct API calls), open a separate terminal:

```bash
cd src/warnerco/backend
uv run uvicorn app.main:app --reload
```

This gives you `http://localhost:8000/docs` for the OpenAPI UI and `http://localhost:8000/dash/scratchpad/` for the scratchpad dashboard.

## Step 3: Test with MCP Inspector First

Before demoing in VS Code, verify the tool works using the MCP Inspector. This standalone web UI lets you call tools directly and see raw responses -- invaluable for debugging.

```bash
npx @modelcontextprotocol/inspector uv run warnerco-mcp
```

This opens a browser at `http://localhost:5173`. Once the Inspector loads:

1. Click the **Tools** tab in the left sidebar.
2. Find `warn_explain_schematic` in the tool list.
3. Fill in the parameters:
   - `schematic_id`: `"WRN-00001"`
   - `audience`: `"technical"`
   - `include_graph_context`: `true`
4. Click **Run**.

**What to expect**: The Inspector will show the tool's execution flow. Because sampling requires a client-side LLM, the Inspector may not support the `ctx.sample()` call out of the box. If sampling fails in the Inspector, you will see an error like:

```
LLM sampling failed: ... Ensure the MCP client supports sampling
and has a model configured.
```

This is expected. The Inspector confirms that the tool is registered and the server starts correctly. The actual sampling demo requires a full MCP client with LLM access -- which is what VS Code provides.

**Note**: If the Inspector does support sampling (some versions include a sampling handler), you will see the full `SchematicExplainerResult` JSON with the `explanation` field populated by the LLM.

## Step 4: Use in VS Code Chat

Open VS Code and start a chat session (Ctrl+Shift+I for Copilot Chat, or the Claude extension's chat panel).

The MCP server exposes `warn_explain_schematic` as a tool the LLM can call. You do not need to call it by name -- just ask naturally and the LLM will select the right tool.

### Example Prompts

**Technical audience (default):**

```
Explain schematic WRN-00001 for a technical audience.
Include graph context.
```

**Executive audience:**

```
I need an executive briefing on robot schematic WRN-00003.
Keep it non-technical and focus on business impact.
```

**Field technician audience:**

```
Brief me on schematic WRN-00005 as if I'm a field technician
about to do maintenance. Be practical, skip the theory.
```

**Without graph context:**

```
Explain schematic WRN-00010 for a technical audience.
Do not include graph relationships.
```

### What Happens Behind the Scenes

When you send one of these prompts, the following sequence occurs:

1. The client's LLM reads your prompt and decides to call `warn_explain_schematic`.
2. The server receives the tool call with parameters (`schematic_id`, `audience`, `include_graph_context`).
3. The server fetches the schematic from the memory store (JSON, Chroma, or Azure Search).
4. If `include_graph_context` is true, the server queries the knowledge graph for relationships (e.g., "WRN-00001 depends_on POW-SYSTEM").
5. The server builds a detailed prompt containing all the raw data and calls `ctx.sample()`.
6. `ctx.sample()` sends the prompt back to the client's LLM with:
   - A system prompt tailored to the audience persona
   - The schematic data as the user message
   - `result_type=SchematicExplanation` for structured output validation
   - `temperature=0.3` for factual accuracy
   - `max_tokens=1024`
   - Model preferences hinting at `claude-sonnet-4-20250514` or `claude-haiku-4-20250414` (the client may ignore these)
7. The client's LLM generates a `SchematicExplanation` with six structured fields.
8. The server combines the original schematic metadata, the LLM explanation, graph context, and sampling metadata into a `SchematicExplainerResult`.
9. The result is returned to the client, which presents it to the user.

## What to Watch For

During the demo, point out these key observations to your audience:

**The round-trip**: The LLM calls a tool, the tool calls the LLM back. This is the defining characteristic of sampling. Watch the chat for signs of a two-phase response -- the initial tool call, then the enriched result.

**Structured output**: The response is not free-form text. It contains exactly six fields defined by the `SchematicExplanation` Pydantic model:

| Field | Description |
|-------|-------------|
| `plain_language_summary` | Jargon-free explanation of the component |
| `key_capabilities` | 3-5 bullet points of capabilities |
| `typical_failure_modes` | 2-3 common failure scenarios |
| `maintenance_tips` | 2-3 practical recommendations |
| `integration_notes` | How the component interacts with other systems |
| `safety_considerations` | Safety precautions |

**Audience adaptation**: The same schematic produces genuinely different explanations depending on the audience parameter. The system prompt changes the LLM's persona:

- `technical` -- "You are a senior robotics engineer explaining to a fellow engineer."
- `executive` -- "You are a technical advisor explaining to a C-suite executive."
- `field_technician` -- "You are a senior field technician briefing a colleague before a maintenance job."

**Graph context enrichment**: When `include_graph_context` is true, the LLM receives relationship data like "WRN-00001 depends_on POW-SYSTEM" alongside the schematic data. This produces richer explanations that reference connected components.

**Sampling metadata**: The result includes a `sampling_metadata` object showing the audience, graph relationship count, history length, and timestamp -- useful for observability and debugging.

## Comparing Audiences

This is the most visually compelling part of the demo. Run three prompts in sequence for the same schematic:

```
Explain schematic WRN-00001 for a technical audience.
```

```
Explain schematic WRN-00001 for an executive audience.
```

```
Explain schematic WRN-00001 for a field technician audience.
```

Compare the results side by side. You should see:

| Aspect | Technical | Executive | Field Technician |
|--------|-----------|-----------|------------------|
| Language | Precise, spec-heavy | Jargon-free, analogy-rich | Practical, action-oriented |
| Focus | Implementation details | Business impact and risk | What to look for, what to fix |
| Failure modes | Root cause analysis | Cost/downtime implications | Symptoms and quick diagnostics |
| Maintenance tips | Calibration procedures | Budget/scheduling impact | Step-by-step field actions |

The key teaching point: the same raw data is transformed into three fundamentally different explanations by changing only the system prompt in the `ctx.sample()` call. The server controls the framing; the LLM does the writing.

## Troubleshooting

### "Sampling not supported" or `ctx.sample()` fails

The MCP client must support the sampling capability. Not all clients do.

- **GitHub Copilot**: Check that you are using a recent version of the Copilot Chat extension. MCP support in Copilot was introduced in 2025; sampling support may require specific extension versions.
- **Claude extension**: Should support sampling natively since the Claude model and SDK support it.
- **MCP Inspector**: Older versions do not include a sampling handler. Use it only for verifying tool registration, not for testing sampling.

### Server does not appear in VS Code

- Verify `.vscode/mcp.json` is in the workspace root (not in a subdirectory).
- Confirm the `cwd` path resolves correctly. If you opened a different folder, `${workspaceFolder}` may point to the wrong location.
- Reload the VS Code window after editing `mcp.json`.
- Check the VS Code Output panel (View > Output) for MCP-related errors. Select the appropriate output channel (e.g., "GitHub Copilot" or "Claude").

### Tool call fails with "Schematic not found"

- Ensure you are using a valid schematic ID. Run `warn_list_robots` first (or ask the LLM to "list all robot schematics") to see available IDs.
- Valid IDs follow the pattern `WRN-XXXXX` (e.g., `WRN-00001` through `WRN-00025`).

### Graph context is empty

- The knowledge graph must be indexed before use. Run:

```bash
cd src/warnerco/backend
uv run python scripts/index_graph.py
```

- If the graph store is unavailable, the tool still works -- it just omits the graph relationships and proceeds with schematic data only.

### Slow response times

Sampling involves two LLM calls: the initial tool selection and the `ctx.sample()` generation. This is inherently slower than a single tool call. Expect 5-15 seconds depending on model speed.

If the demo needs to be faster, set `include_graph_context` to `false` to skip the graph query step.

### Environment variable issues

If the server fails to start, check `src/warnerco/backend/.env`:

```bash
# Minimum required for the demo
MEMORY_BACKEND=json
```

The `json` backend requires no external services and is the fastest to start. Switch to `chroma` only if you need semantic search for other tools.

## Source Code Reference

The sampling implementation lives in a single file:

- **Tool and models**: `src/warnerco/backend/app/mcp_tools.py` -- search for the `SAMPLING` section near line 4080.
- **Pydantic models**: `SchematicExplanation` (the structured output schema) and `SchematicExplainerResult` (the full return type) are defined immediately above the tool function.
- **System prompts**: The audience-specific prompts are defined in the `audience_prompts` dictionary inside `warn_explain_schematic`.

The core sampling call is six lines:

```python
sampling_result = await ctx.sample(
    messages=user_message,
    system_prompt=system_prompt,
    result_type=SchematicExplanation,
    temperature=0.3,
    max_tokens=1024,
    model_preferences=["claude-sonnet-4-20250514", "claude-haiku-4-20250414"],
)
```

Key parameters:

| Parameter | Value | Purpose |
|-----------|-------|---------|
| `messages` | Raw schematic data as a formatted string | The data for the LLM to reason over |
| `system_prompt` | Audience-specific persona | Controls tone and detail level |
| `result_type` | `SchematicExplanation` (Pydantic model) | Validates structured output automatically |
| `temperature` | `0.3` | Low creativity for factual accuracy |
| `max_tokens` | `1024` | Enough for a thorough explanation |
| `model_preferences` | Claude Sonnet 4, Claude Haiku 4 | Hints to the client (client may ignore) |

## Key Takeaways for Students

1. **Sampling inverts control flow.** Normal tools return data. Sampling tools return LLM-enriched data. The server becomes an orchestrator, not just a data source.

2. **Structured output is automatic.** By passing `result_type=SchematicExplanation` to `ctx.sample()`, FastMCP handles JSON schema generation, LLM instruction, and Pydantic validation. No manual parsing needed.

3. **The server controls framing; the LLM controls content.** The system prompt, temperature, and data selection are server decisions. The actual explanation is an LLM decision. This separation of concerns makes sampling tools predictable yet flexible.

4. **Client support is required.** Sampling only works when the MCP client implements a sampling handler. This is a capability negotiation -- not all clients support it. Always handle the failure case gracefully (the tool raises a `RuntimeError` with a clear message).

5. **Sampling enables tool chains.** Because the server can call the LLM mid-tool-execution, you can build multi-step pipelines: fetch data, reason about it, fetch more data based on the reasoning, reason again. This is the most "agentic" MCP primitive.
