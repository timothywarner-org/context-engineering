# Context Engineering with MCP - Hands-On Labs

These progressive labs take you from building your first MCP server to connecting an OAuth-secured remote MCP server on Azure.

**Progression**: **Lab 01** (JS hello-world) -> **Lab 02** (Python client + server) -> **Lab 03** (interactive UI) -> **Lab 04** (remote + OAuth on Azure). JS to Python to UI to production-auth.

**Primary Teaching Example**: WARNERCO Robotics Schematica at `src/warnerco/backend/` demonstrates all advanced concepts (FastMCP, LangGraph, Graph Memory, etc.).

## Lab Structure

Each lab includes:
- **README.md** - Lab objectives and instructions
- **starter/** - Starting code template
- **solution/** - Reference solution
- **tests/** - Validation scripts (where applicable)

## Available Labs

### Lab 01: Hello MCP (30 minutes)
**Objective**: Create your first MCP server with a single tool

**What you'll learn**:
- MCP server basics and structure
- Tool registration and schema definition
- stdio transport communication
- Testing with MCP Inspector

**Start**: [lab-01-hello-mcp/](./lab-01-hello-mcp/)

---

### Lab 02: MCP Chat CLI (45 minutes)
**Objective**: Build and run the smallest **complete MCP client + stdio FastMCP server + REPL** in Python

**What you'll learn**:
- How an **MCP client** connects to a **stdio FastMCP server** and drives a chat REPL
- Server registration of **2 tools** (`read_doc_contents`, `edit_document`)
- **1 resource plus 1 template** (`docs://documents`, `docs://documents/{id}`)
- **1 prompt** (`format`)
- On-rails launch with `run.ps1` (bootstraps `.env`, lifts `ANTHROPIC_API_KEY` from the repo-root `.env`, runs `main.py`)

**Start**: [lab-02-mcp-chat/](./lab-02-mcp-chat/) (run `./run.ps1`)

---

### Lab 03: MCP Apps (45 minutes)
**Objective**: Return a rendered, interactive UI over MCP instead of plain text (Segment 4 capstone)

**What you'll learn**:
- **MCP Apps** (SEP-1865, spec 2026-01-26, status Stable): a tool declares a `ui://` resource served as `text/html`, the host renders it in a **sandboxed iframe**, and a **postMessage plus JSON-RPC bridge** carries data and lets the UI call tools back
- The JS/TS SDK `@modelcontextprotocol/ext-apps`
- Wiring **three published example servers** into Claude Desktop with **zero clone, zero build, via stdio**: `budget-allocator` (interactive sliders plus reactive chart), `map` (CesiumJS 3D globe), `system-monitor` (live CPU/memory charts)

**Start**: [lab-03-mcp-apps/README.md](./lab-03-mcp-apps/README.md)

---

### Lab 04: Remote MCP with OAuth on Azure (60 minutes)
**Objective**: Deploy and connect to an **OAuth-secured remote MCP server** on Azure, and learn **OAuth AAA** (Authentication, Authorization, Accounting) with **Entra ID** and **Azure API Management (APIM)**

**What you'll learn**:
- **APIM as the AI Gateway and OAuth authorization-server facade** in front of an Azure Functions Python MCP server
- **Entra ID app registration plus Federated Identity Credential** for **secretless** confidential-client auth (APIM uses its managed identity, no client secret)
- Why a plain browser hit on the MCP endpoint returns **401** by design (no token, no access)
- Connecting through an MCP client via **MCP Inspector over SSE** (the client runs the Entra consent flow)
- **Same-day teardown** to control cost (APIM Basicv2 meters hourly)

**Start**: [../remote-mcp-apim-functions-python/QUICKSTART.md](../remote-mcp-apim-functions-python/QUICKSTART.md)

---

## What's Next

- **Known next step**: deploy the remote MCP server on **Azure Container Apps (ACA)** and adopt **native APIM MCP mode** as a follow-up to Lab 04.

Additional labs may be added over time.

---

## Quick Start

Each lab has its own launch path. The fastest start per lab:

```bash
# Lab 01 (JS) - Hello MCP
cd labs/lab-01-hello-mcp/starter && npm install && npm start

# Lab 02 (Python) - MCP Chat CLI (on-rails launcher lifts the API key)
cd labs/lab-02-mcp-chat && ./run.ps1

# Lab 03 (JS/TS) - MCP Apps: no clone, no build. Paste the config into Claude Desktop
#   see labs/lab-03-mcp-apps/README.md and claude_desktop_config.json

# Lab 04 (Azure) - Remote MCP with OAuth: deploy, then connect with an MCP client
cd remote-mcp-apim-functions-python && azd up   # see QUICKSTART.md to connect; azd down --purge --force to tear down
```

### Testing Your Solution

```bash
# In the lab's starter/ directory
npm test

# Or test with MCP Inspector
npx @modelcontextprotocol/inspector node src/index.js
```

---

## Lab Completion Checklist

Track your progress:

- [ ] **Lab 01**: Hello MCP - Build your first MCP server
- [ ] **Lab 02**: MCP Chat CLI - Run a complete Python MCP client, stdio server, and REPL
- [ ] **Lab 03**: MCP Apps - Render an interactive `ui://` surface in Claude Desktop
- [ ] **Lab 04**: Remote MCP with OAuth on Azure - Deploy and connect to an OAuth-secured remote MCP server

---

## Getting Help

### During Labs

1. **Check the README**: Each lab has detailed step-by-step instructions
2. **Review the solution**: Solutions are provided for reference
3. **Use MCP Inspector**: Debug your server interactively
4. **Check docs/TROUBLESHOOTING_FAQ.md**: Common issues and solutions

### Common Issues

#### "Server won't start"
```bash
# Check for syntax errors
node --check src/index.js

# Look for port conflicts
lsof -ti:3000 | xargs kill -9  # macOS/Linux
```

#### "Tool not appearing in Inspector"
- Ensure tool is registered BEFORE `server.connect()`
- Check tool schema for syntax errors
- Restart MCP Inspector

#### "Dependencies not found"
```bash
# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install
```

---

## Lab Tips

### Best Practices

1. **Read the entire lab README first** - understand the objectives
2. **Start with the starter code** - don't jump to the solution
3. **Test incrementally** - validate each step as you go
4. **Use console.error()** - for debugging (goes to stderr, not MCP)
5. **Check the solution if stuck** - but try on your own first

### Time Management

- **Each lab has an estimated time** - don't rush
- **Skip optional sections** if you're behind schedule
- **Focus on understanding over completion** - quality over speed

### Code Quality

- **Add comments** to explain your thinking
- **Handle errors gracefully** - return useful error messages
- **Validate inputs** - use JSON Schema effectively
- **Keep it simple** - solve the problem, then refactor

---

## Beyond the Labs

### Next Steps After the Four Labs

Once you have worked through Lab 01 through Lab 04, you can:

1. **Explore WARNERCO Schematica** - Study `src/warnerco/backend/` for a production-grade MCP implementation
2. **Read the MCP specification** - Deepen your understanding of the protocol
3. **Build your own MCP App** - Author a `ui://` surface from the Lab 03 escape hatch (`examples/basic-server-vanillajs` upstream)
4. **Try the dashboards** - Run WARNERCO Schematica and explore `http://localhost:8000/dash/`
5. **Study the Graph Memory tutorial** - See `docs/tutorials/graph-memory-tutorial.md`

### Resources

- **MCP Specification**: <https://spec.modelcontextprotocol.io/>
- **MCP SDK Docs**: <https://github.com/modelcontextprotocol/typescript-sdk>
- **Example Servers**: <https://github.com/modelcontextprotocol/servers>
- **Community Discord**: <https://discord.gg/modelcontextprotocol>

---

## Contributing to Labs

Found an issue or have an improvement?

1. Note the problem or enhancement idea
2. Test your proposed fix
3. Share as course feedback

---

**Happy Learning!**

*Remember: The goal is not just to complete the labs, but to understand the patterns so you can apply them in real-world scenarios.*
