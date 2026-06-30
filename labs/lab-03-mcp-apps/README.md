# Lab 03 - MCP Apps (interactive UI over MCP)

**Segment 4 capstone.** Labs 01 and 02 returned text and structured data. **MCP Apps** returns a *rendered interface* - a chart, form, map, or dashboard that draws inline in the chat client. This lab wires three published example servers into **Claude Desktop** with **zero clone and zero build**.

## Why this belongs in a context-engineering course

The course thesis is that **dev tools expose context that consumer tools hide**. MCP Apps is the sharpest example yet of the split:

- The **model** exchanges structured JSON with your tool (the context it reasons over).
- The **human** sees a rich, interactive surface (the context they reason over).
- The **UI can call other tools back** through the host, so the surface is live, not a screenshot.

One tool call, two different audiences, two different context payloads. That is context engineering made visible.

## What it is (grounded, not hand-waved)

| Fact | Value |
|------|-------|
| Spec | **SEP-1865**, version `2026-01-26`, status **Stable** |
| Mechanism | Tool declares a **`ui://` resource** served as `text/html`; host renders it in a **sandboxed iframe**; a **postMessage + JSON-RPC bridge** carries data and tool calls |
| SDK | `@modelcontextprotocol/ext-apps` - **JS/TS only** (this is why the lab is not bolted onto Python WARNERCO) |
| Host used here | **Claude Desktop** (first-class MCP Apps client) |
| Transport | **stdio** - Claude Desktop launches the server locally; no port, no Inspector |

Three servers are published to npm and verified live: `server-budget-allocator`, `server-map`, `server-system-monitor` (all `1.7.4`).

## Fastest path: wire it into Claude Desktop (about 2 minutes)

1. Open **Claude Desktop** and sign in.
2. Go to **Settings > Developer > Edit Config**. That opens `claude_desktop_config.json`.
   - Windows location: `%APPDATA%\Claude\claude_desktop_config.json`
3. Paste the contents of [claude_desktop_config.json](claude_desktop_config.json) (next to this README). If you already have an `mcpServers` block, merge the three entries into it.
4. **Save and fully restart** Claude Desktop (quit, do not just close the window).
5. In a new chat, prompt the server (see table below). Claude calls the tool, then shows a **permission prompt to display the App**. Click **Always allow**. The UI renders inline.

### Demo prompts (real tool triggers, not invented)

| Server (config key) | Say this to Claude | What renders |
|---------------------|--------------------|--------------|
| `mcpapps-budget-allocator` | "Open the budget allocator and split a 1.2M budget across marketing, engineering, and sales." | Interactive sliders; drag a category over budget and the chart reacts |
| `mcpapps-map` | "Show me a map of Nashville, Tennessee." | CesiumJS 3D globe flown to the geocoded location |
| `mcpapps-system-monitor` | "Show my system info, then poll CPU and memory." | Live per-core CPU area chart and memory gauge |

Start with **budget-allocator** in class. It is the cleanest demonstration of the two-audience split: the model sends structured allocations, the human edits them in the UI, and the edits flow back through the bridge.

## Windows gotcha (read before you blame the config)

If servers show as **failed to start** in Claude Desktop on Windows, the bare `npx` launcher is the usual culprit - Claude Desktop cannot always resolve `npx` on `PATH`. Swap the launcher to route through `cmd`:

```json
{
  "command": "cmd",
  "args": ["/c", "npx", "-y", "--silent", "--registry=https://registry.npmjs.org/", "@modelcontextprotocol/server-budget-allocator", "--stdio"]
}
```

First launch also pulls the package from npm, so give it a few seconds before deciding it hung.

## Escape hatch: teach *building* one (local development)

When you want to show the source instead of consuming a package, clone the repo and point Claude Desktop at a local build:

```bash
git clone https://github.com/modelcontextprotocol/ext-apps.git
cd ext-apps && npm install
```

```json
{
  "mcpServers": {
    "map-local": {
      "command": "bash",
      "args": ["-c", "cd /absolute/path/to/ext-apps/examples/map-server && npm run build >&2 && node dist/index.js --stdio"]
    }
  }
}
```

The smallest source to read is `examples/basic-server-vanillajs` (one tool, one `ui://` HTML file, no framework). For an even faster authoring path, the repo ships Agent Skills - `/plugin marketplace add modelcontextprotocol/ext-apps`, then ask your coding agent to "Add UI to my MCP server."

## What to demo live vs. cut for time

- **Must show:** budget-allocator round-trip (model data in, human edits out).
- **Nice to show:** map for the visual wow.
- **Cut first:** system-monitor (the polling chart is noisier to narrate under time pressure).

## Sources

- Repo: https://github.com/modelcontextprotocol/ext-apps
- Spec `2026-01-26`: https://github.com/modelcontextprotocol/ext-apps/blob/main/specification/2026-01-26/apps.mdx
- Claude host docs: https://claude.com/docs/connectors/building/mcp-apps/getting-started
