# Copilot Instructions for Context Engineering Course

## Project Overview

This is an **educational repository** for the O'Reilly live training course "Context Engineering with MCP". It contains multiple working MCP (Model Context Protocol) server implementations demonstrating persistent AI memory patterns. This is NOT a production codebase—it's teaching material where clarity trumps optimization.

**Primary Audience**: Course instructors and students learning MCP fundamentals
**Key Pattern**: Local development → Azure deployment progression

## Architecture: Three-Layer Learning Progression

```
1. Simple (coretext-mcp)     → JavaScript, JSON storage, teaching comments
2. Production (stoic-mcp)     → TypeScript, Cosmos DB, workspace pattern
3. Alternative (context_journal_mcp) → Python implementation for comparison
```

### MCP Server Implementations

- **[coretext-mcp/](../mcp-servers/coretext-mcp/)**: Main teaching server. Single `src/index.js` file (~1200 lines) with extensive inline documentation. Implements episodic/semantic memory with DeepSeek AI enrichment (optional). Demonstrates CRUD operations, resources, and Azure migration path.

- **[stoic-mcp/](../mcp-servers/stoic-mcp/)**: Production-quality TypeScript implementation using npm workspaces (`local/` and `azure/` packages). Shows proper separation of concerns, build tooling, and Cosmos DB integration.

- **[context_journal_mcp_local/](../mcp-servers/context_journal_mcp_local/)** and **[\_azure/](../mcp-servers/context_journal_mcp_azure/)**: Python MCP servers using `mcp-sdk`. Demonstrates cross-language protocol compatibility.

## Development Commands by Server

### CoreText MCP (JavaScript)

```bash
cd mcp-servers/coretext-mcp
npm install
npm run dev              # Auto-reload on changes
npm run inspector        # Launch MCP Inspector for debugging
npm test                 # Run test client
npm run demo:segment1    # Execute segment-specific demos
```

**Key Files**:

- `src/index.js`: Complete server implementation (read this first)
- `data/memory.json`: Persistent memory storage
- `scripts/demo-*.js`: Scripted demos for each course segment
- `.env.example`: Template for DeepSeek API key (fallback mode available)

### Stoic MCP (TypeScript)

```bash
cd mcp-servers/stoic-mcp
npm install                        # Hydrates workspaces
npm run build --workspace local    # Compile TypeScript
npm start --workspace local        # Run local server
```

**Workspace Structure**:

- `local/`: Self-contained TypeScript MCP server
- `azure/`: Azure Container Apps deployment variant
- Both share same tool schemas but different storage backends

### Context Journal (Python)

```bash
cd mcp-servers/context_journal_mcp_local
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python context_journal_mcp.py --help
```

## Configuration Patterns

### MCP Client Integration

**Claude Desktop**: `%APPDATA%\Claude\claude_desktop_config.json` (Windows) or `~/Library/Application Support/Claude/claude_desktop_config.json` (Mac/Linux)

```json
{
  "mcpServers": {
    "coretext": {
      "command": "node",
      "args": [
        "C:/github/context-engineering/mcp-servers/coretext-mcp/src/index.js"
      ]
    }
  }
}
```

**VS Code**: Create `.vscode/mcp.json` in workspace root:

```json
{
  "mcpServers": {
    "coretext": {
      "command": "node",
      "args": ["${workspaceFolder}/mcp-servers/coretext-mcp/src/index.js"]
    }
  }
}
```

### Environment Variables

All servers use `.env` files (never committed). Copy from `.env.example`:

- `DEEPSEEK_API_KEY`: Optional for AI enrichment (coretext-mcp has fallback)
- Azure servers require `AZURE_COSMOS_*` variables (documented in respective READMEs)

## Critical Teaching Patterns

### Memory Types

```javascript
// Episodic: Time-bound events ("I did X at Y time")
{ type: 'episodic', content: "Met with client on Tuesday 2pm" }

// Semantic: Timeless facts ("X is related to Y")
{ type: 'semantic', content: "Client prefers email communication" }
```

### CRUD Operations

All MCP memory servers follow consistent CRUD pattern:

- `create_memory`: Add new entry, returns UUID
- `read_memory`: Retrieve by ID, increments access count
- `update_memory`: Modify existing entry
- `delete_memory`: Remove entry, soft-delete in production variants
- `search_memories`: Query by tags, content, or type

### Resource vs Tool

- **Tools**: AI invokes actions (create_memory, enrich_content)
- **Resources**: AI reads data streams (context://recent, memory://all)

## Testing & Validation

### Pre-Course Environment Check

```bash
node scripts/validate-environment.js
```

Verifies Node.js (>=20), npm, Docker (optional), Python (>=3.11), and repository structure.

### MCP Inspector Workflow

```bash
cd mcp-servers/coretext-mcp
npm run inspector
```

Opens browser-based debugger at `http://localhost:5173`. Use to:

1. Test tool invocations without AI client
2. Inspect JSON-RPC messages
3. Validate resource URIs

### Demo Scripts

Each `scripts/demo-segmentN.js` demonstrates course segment N capabilities. Run with `--auto` flag for non-interactive mode or manual step-through for teaching.

## Azure Deployment Pattern

Both coretext-mcp and stoic-mcp follow this progression:

1. **Local**: JSON file storage, stdio transport
2. **Azure**: Cosmos DB storage, SSE transport, Container Apps hosting

**Key Files**:

- `*/azure/deploy.sh` or `*/azure/deploy.ps1`: Deployment automation
- `*/azure/Dockerfile`: Containerization
- `*/azure/README.md`: Step-by-step deployment guide

**Teaching Point**: Show local implementation first, then demonstrate Azure migration changes (storage adapter, transport layer, environment config).

## File Organization Conventions

- `instructor/`: Private teaching materials (demos, runbooks, slides)
- `student/`: Public student resources (setup guides, troubleshooting)
- `reference/`: Conceptual documentation (MCP tutorials, implementation guides)
- `labs/`: Hands-on exercises with starter/solution pairs
- `diagrams/`: Mermaid architecture diagrams (both local and Azure variants)

## Common Pitfalls

### Port Conflicts

CoreText MCP includes health check server (port 3000). If crashes leave zombie processes:

```bash
npm run kill-ports  # Windows netstat + taskkill cleanup
```

### Stdio vs SSE Transports

- **Local servers**: Use stdio transport (JSON-RPC over stdin/stdout)
- **Azure servers**: Use SSE transport (Server-Sent Events over HTTP)
- **Don't mix**: Claude Desktop requires stdio, remote clients need SSE

### Memory Persistence

Local servers persist to JSON files. Always check:

- File paths are absolute or properly resolved
- `data/` directory exists (created automatically)
- Write permissions available

## Contributing to Course Materials

When adding/modifying servers:

1. **Keep teaching focus**: Prefer clarity over cleverness
2. **Match existing patterns**: CRUD operations, memory types, demo scripts
3. **Document inline**: Assume reader is learning MCP for first time
4. **Test both transports**: Verify stdio (Claude) and inspector work
5. **Update parallel docs**: If changing coretext-mcp, check if stoic-mcp/Python variants need alignment

## Quick Reference: MCP Protocol Concepts

- **JSON-RPC 2.0**: All MCP communication uses this protocol
- **Capabilities**: Servers advertise tools/resources/prompts on connect
- **Request/Response**: Async operations with correlation IDs
- **Schemas**: Zod validation in TypeScript, Pydantic in Python
- **Transport Independence**: Protocol works over stdio, SSE, or custom transports

## Essential Reading Before Coding

1. [README.md](../README.md) - Repository structure and quick start
2. [reference/IMPLEMENTATION_GUIDE.md](../reference/IMPLEMENTATION_GUIDE.md) - Choose right pattern
3. [mcp-servers/coretext-mcp/CODE_WALKTHROUGH.md](../mcp-servers/coretext-mcp/CODE_WALKTHROUGH.md) - Line-by-line explanation
4. [instructor/DEMO_SCRIPT.md](../instructor/DEMO_SCRIPT.md) - Teaching narrative flow

For questions about MCP specification itself, refer to official docs at <https://spec.modelcontextprotocol.io/>
