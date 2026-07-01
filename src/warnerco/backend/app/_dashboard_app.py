"""Self-contained MCP App UI for WARNERCO Schematica (SEP-1865).

This module holds a single triple-quoted HTML string, ``DASHBOARD_HTML``, that is
served verbatim from the ``ui://warnerco/dashboard`` MCP resource (see
``app/mcp_tools.py``). It is intentionally a *constant in a .py file* rather than a
file under ``static/`` so the container has no runtime file-path dependency for the
UI: the string is imported at module load and returned directly by the resource.

Why this is pure Python with zero JS build step:
    SEP-1865 (spec 2026-01-26) makes an MCP App UI just an MCP *resource* whose
    content is ``text/html;profile=mcp-app``, linked from a tool via
    ``_meta.ui.resourceUri``. The host renders that HTML in a sandboxed iframe and
    talks to it over ``window.postMessage`` using JSON-RPC 2.0. The official
    ``@modelcontextprotocol/ext-apps`` SDK is an *iframe-side convenience only*; the
    spec documents the raw bridge, which is what the inline ``<script>`` below
    implements by hand. That keeps the entire app Python + vanilla JS.

The bridge contract implemented below (host <-> iframe):
    1. iframe -> host   ``ui/initialize``                (handshake; announces display modes)
    2. host   -> iframe ``{result: {protocolVersion}}``  (handshake reply)
    3. host   -> iframe ``ui/notifications/tool-input``   (push: the tool's seed payload)
    4. iframe -> host   ``tools/call``                    (live: call warn_* tools back)

This is a deliberately MINIMAL "blend" of the full Astro dashboard: four stat tiles
seeded from the tool result, plus one search box that calls ``warn_semantic_search``
back through the host. It is a teaching artifact, not a port of the 379-line SPA.
"""

# NOTE: braces in the embedded CSS/JS are literal HTML, not Python format fields.
# This is a plain string constant (no .format()/f-string), so no brace-escaping needed.
DASHBOARD_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>WARNERCO Schematica</title>
<style>
  /* Inlined so the sandboxed iframe needs no network for styling. */
  :root {
    --bg: #0d1117; --panel: #161b22; --border: #30363d;
    --text: #e6edf3; --muted: #8b949e; --accent: #58a6ff; --good: #3fb950;
  }
  * { box-sizing: border-box; }
  body {
    margin: 0; padding: 16px; background: var(--bg); color: var(--text);
    font: 14px/1.5 -apple-system, "Segoe UI", system-ui, sans-serif;
  }
  h1 { font-size: 16px; margin: 0 0 4px; }
  .sub { color: var(--muted); font-size: 12px; margin-bottom: 16px; }
  .tiles { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 16px; }
  .tile {
    background: var(--panel); border: 1px solid var(--border); border-radius: 8px;
    padding: 12px; text-align: center;
  }
  .tile .num { font-size: 24px; font-weight: 600; color: var(--accent); }
  .tile .lbl { font-size: 11px; color: var(--muted); text-transform: uppercase; letter-spacing: .04em; }
  .search { display: flex; gap: 8px; margin-bottom: 12px; }
  .search input {
    flex: 1; background: var(--panel); border: 1px solid var(--border); border-radius: 6px;
    color: var(--text); padding: 8px 10px; font-size: 14px;
  }
  .search button {
    background: var(--accent); color: #0d1117; border: 0; border-radius: 6px;
    padding: 8px 14px; font-weight: 600; cursor: pointer;
  }
  .search button:disabled { opacity: .5; cursor: default; }
  .results { list-style: none; margin: 0; padding: 0; }
  .results li {
    background: var(--panel); border: 1px solid var(--border); border-radius: 6px;
    padding: 10px 12px; margin-bottom: 8px;
  }
  .results .rid { color: var(--good); font-family: ui-monospace, monospace; font-size: 12px; }
  .results .rname { font-weight: 600; }
  .results .rsum { color: var(--muted); font-size: 12px; }
  .status { color: var(--muted); font-size: 12px; min-height: 18px; }
</style>
</head>
<body>
  <h1>WARNERCO Robotics Schematica</h1>
  <div class="sub">Live schematics over the MCP Apps bridge</div>

  <div class="tiles">
    <div class="tile"><div class="num" id="t-total">--</div><div class="lbl">Schematics</div></div>
    <div class="tile"><div class="num" id="t-indexed">--</div><div class="lbl">Indexed</div></div>
    <div class="tile"><div class="num" id="t-cats">--</div><div class="lbl">Categories</div></div>
    <div class="tile"><div class="num" id="t-backend">--</div><div class="lbl">Backend</div></div>
  </div>

  <form class="search" id="search-form">
    <input id="q" type="text" placeholder="Semantic search, e.g. 'thermal sensor for arm joint'" autocomplete="off" />
    <button type="submit" id="go">Search</button>
  </form>
  <div class="status" id="status"></div>
  <ul class="results" id="results"></ul>

<script>
/* ----------------------------------------------------------------------------
 * SEP-1865 host <-> iframe bridge, implemented in raw postMessage + JSON-RPC 2.0.
 * No SDK. The host is the parent window; we never touch the network directly
 * (the sandbox forbids it) -- all data flows through the bridge.
 * -------------------------------------------------------------------------- */
(function () {
  "use strict";

  var PROTOCOL_VERSION = "2026-01-26";
  var nextId = 1;
  var pending = {};   // JSON-RPC id -> {resolve, reject} for our outbound calls

  // Post a JSON-RPC message up to the host. The MCP Apps host listens on the
  // iframe's parent window; "*" target origin is standard here because the host
  // assigns the iframe an opaque origin we cannot enumerate in advance.
  function post(msg) { window.parent.postMessage(msg, "*"); }

  // Fire a request and get a Promise for its result (handshake, tools/call).
  function request(method, params) {
    var id = nextId++;
    post({ jsonrpc: "2.0", id: id, method: method, params: params || {} });
    return new Promise(function (resolve, reject) { pending[id] = { resolve: resolve, reject: reject }; });
  }

  // ---- Inbound: host -> iframe ---------------------------------------------
  window.addEventListener("message", function (event) {
    var msg = event.data;
    if (!msg || msg.jsonrpc !== "2.0") return;

    // (a) Reply to one of our outbound requests.
    if (msg.id !== undefined && pending[msg.id]) {
      var p = pending[msg.id];
      delete pending[msg.id];
      if (msg.error) { p.reject(msg.error); } else { p.resolve(msg.result); }
      return;
    }

    // (b) Push notification from the host -- the tool's seed payload arrives here.
    if (msg.method === "ui/notifications/tool-input") {
      var args = (msg.params && msg.params.arguments) || {};
      if (args.seeded) renderTiles(args.seeded);
    }
  });

  // ---- Outbound helpers -----------------------------------------------------
  // Call a WARNERCO MCP tool back through the host (live search).
  function callTool(name, args) {
    return request("tools/call", { name: name, arguments: args || {} });
  }

  // ---- Rendering ------------------------------------------------------------
  function setText(id, v) { document.getElementById(id).textContent = String(v); }

  function renderTiles(seed) {
    setText("t-total", seed.total != null ? seed.total : "--");
    setText("t-indexed", seed.indexed != null ? seed.indexed : "--");
    setText("t-cats", seed.categories ? Object.keys(seed.categories).length : "--");
    setText("t-backend", seed.backend || "--");
  }

  // Defensive text rendering -- never inject untrusted strings as HTML.
  function el(tag, cls, text) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text != null) e.textContent = text;
    return e;
  }

  function renderResults(items) {
    var ul = document.getElementById("results");
    ul.innerHTML = "";
    if (!items || !items.length) { document.getElementById("status").textContent = "No matches."; return; }
    items.forEach(function (it) {
      var li = el("li");
      li.appendChild(el("div", "rid", it.id || it.schematic_id || ""));
      li.appendChild(el("div", "rname", it.name || it.component || it.model || ""));
      if (it.summary) li.appendChild(el("div", "rsum", it.summary));
      ul.appendChild(li);
    });
    document.getElementById("status").textContent = items.length + " match(es).";
  }

  // Tool results from MCP come back as content blocks; pull the structured
  // payload whether the host hands us structuredContent or a JSON text block.
  function extractResults(result) {
    if (!result) return [];
    if (result.structuredContent && result.structuredContent.results) return result.structuredContent.results;
    if (Array.isArray(result.results)) return result.results;
    if (result.content) {
      for (var i = 0; i < result.content.length; i++) {
        var c = result.content[i];
        if (c.type === "text") {
          try { var parsed = JSON.parse(c.text); if (parsed.results) return parsed.results; } catch (e) {}
        }
      }
    }
    return [];
  }

  // ---- Wiring ---------------------------------------------------------------
  document.getElementById("search-form").addEventListener("submit", function (ev) {
    ev.preventDefault();
    var q = document.getElementById("q").value.trim();
    if (!q) return;
    var btn = document.getElementById("go");
    btn.disabled = true;
    document.getElementById("status").textContent = "Searching...";
    callTool("warn_semantic_search", { query: q, top_k: 5 })
      .then(function (result) { renderResults(extractResults(result)); })
      .catch(function (err) { document.getElementById("status").textContent = "Error: " + (err.message || err); })
      .then(function () { btn.disabled = false; });
  });

  // ---- Handshake ------------------------------------------------------------
  // Announce the iframe to the host. The host replies with protocolVersion and
  // then (per the tool's result) pushes the seed via ui/notifications/tool-input.
  request("ui/initialize", { appCapabilities: { availableDisplayModes: ["inline", "fullscreen"] } })
    .then(function (res) {
      document.getElementById("status").textContent =
        "Connected (" + ((res && res.protocolVersion) || PROTOCOL_VERSION) + "). Try a search.";
    })
    .catch(function () {
      // Standalone/no-host fallback (e.g. opened directly): degrade gracefully.
      document.getElementById("status").textContent = "No MCP host detected.";
    });
})();
</script>
</body>
</html>
"""
