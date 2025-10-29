# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

CoreText MCP Server is a teaching-focused implementation of the Model Context Protocol (MCP) that demonstrates persistent AI memory through CRUD operations and AI enrichment. Built for the O'Reilly "Context Engineering with MCP" course, it showcases local development with JSON storage and a migration path to Azure production deployment (Container Apps + Cosmos DB).

**Purpose**: Teaching MCP concepts through a simple, intentionally educational server that runs both locally and can be deployed to Azure for comparison.

## Development Commands

### Local Development
```bash
# Install dependencies (Node.js >=18 required)
npm install

# Start server with auto-reload on file changes
npm run dev

# Start server normally
npm start

# Test with MCP Inspector (primary debugging tool)
npm run inspector

# Run test client
npm test

# Test API key configuration
npm test-api
```

### Environment Setup
```bash
# Copy example configuration
cp .env.example .env

# Edit .env to add Deepseek API key (optional - has fallback mode)
# DEEPSEEK_API_KEY=your_api_key_here
```

### MCP Client Integration

#### Claude Desktop

**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
**Mac/Linux**: `~/Library/Application Support/Claude/claude_desktop_config.json`

**Without API key** (uses fallback enrichment):
```json
{
  "mcpServers": {
    "coretext": {
      "command": "node",
      "args": ["C:/github/coretext-mcp/src/index.js"]
    }
  }
}
```

**With Deepseek API key** (enables AI enrichment):
```json
{
  "mcpServers": {
    "coretext": {
      "command": "node",
      "args": ["C:/github/coretext-mcp/src/index.js"],
      "env": {
        "DEEPSEEK_API_KEY": "sk-1234567890abcdef1234567890abcdef"
      }
    }
  }
}
```

#### VS Code

Create `.vscode/mcp.json` in your workspace:

**Without API key** (uses fallback enrichment):
```json
{
  "mcpServers": {
    "coretext": {
      "command": "node",
      "args": ["${workspaceFolder}/src/index.js"]
    }
  }
}
```

**With Deepseek API key** (enables AI enrichment):
```json
{
  "mcpServers": {
    "coretext": {
      "command": "node",
      "args": ["${workspaceFolder}/src/index.js"],
      "env": {
        "DEEPSEEK_API_KEY": "sk-1234567890abcdef1234567890abcdef"
      }
    }
  }
}
```

**Note**: The API key examples use `sk-1234...` format for teaching demonstrations. In production, use environment variables or Azure Key Vault instead of hardcoding keys in config files.

## Architecture

### Core Classes (src/index.js)

**MemoryEntry**: Represents a single memory unit with:
- `id` (UUID)
- `content` (the actual memory text)
- `type` (episodic vs semantic)
- `metadata` (created, updated, accessCount, lastAccessed, enriched)
- `tags` (array for categorization)
- `enrichment` (AI analysis data)

**MemoryManager**: Handles all CRUD operations
- Persists to `data/memory.json` for local development
- Auto-creates 3 demo memories on first run
- Tracks access patterns (accessCount, lastAccessed) for context stream
- Builds knowledge graph clusters based on shared tags/keywords

**DeepseekEnrichmentService**: AI analysis layer
- Primary mode: Deepseek API (when `DEEPSEEK_API_KEY` set)
- Fallback mode: Local keyword extraction + sentiment analysis (always works)
- Extracts: summary, keywords, sentiment, category, related topics
- Graceful degradation pattern for production resilience

**CoreTextServer**: Main MCP server implementation
- 8 Tools: memory_create, memory_read, memory_update, memory_delete, memory_search, memory_list, memory_stats, memory_enrich
- 3 Resources: memory://overview (markdown dashboard), memory://context-stream (working memory view), memory://knowledge-graph (semantic connections)
- Uses @modelcontextprotocol/sdk with stdio transport

### Memory Types (Teaching Concept)

**Semantic Memory**: Fact-based, conceptual knowledge
- Example: "MCP enables persistent AI context"
- Use for: Documentation, preferences, knowledge base

**Episodic Memory**: Time-based, event-focused memories
- Example: "Meeting with client on Oct 31, 2024 at 2pm"
- Use for: Conversation history, event tracking, timeline

### Data Flow

1. Client calls tool (e.g., `memory_create`)
2. Server validates and processes via `CallToolRequestSchema` handler
3. MemoryManager creates MemoryEntry with UUID
4. Optional: DeepseekEnrichmentService analyzes content
5. MemoryManager persists to `data/memory.json`
6. Response returns success + memory object with metadata

### Resource Architecture

Resources provide **always-available context** (unlike tools that must be called):

- **memory://overview**: Dashboard with stats, recent activity, tag cloud (Markdown)
- **memory://context-stream**: Time-windowed view (recent/today/earlier) for conversation continuity (JSON)
- **memory://knowledge-graph**: Nodes (memories), edges (shared tags/keywords), clusters (related groups) (JSON)

## Key Implementation Patterns

### Authentication Hierarchy
1. Environment variable: `DEEPSEEK_API_KEY` (production via Azure Key Vault)
2. .env file: Development convenience
3. Fallback mode: No API key required, uses local enrichment

### Graceful Degradation
- Enrichment works WITH or WITHOUT API key
- Demo memories auto-created if `data/memory.json` missing
- Fallback enrichment uses basic NLP (stopwords, sentiment keywords, category patterns)

### Production Migration Path
**Current** (Local Development):
- Storage: `data/memory.json` (100MB limit)
- Compute: Local Node.js process
- Enrichment: Optional Deepseek API

**Future** (Azure Production):
- Storage: Azure Cosmos DB (unlimited scale)
- Compute: Azure Container Apps (serverless containers)
- Enrichment: Azure OpenAI Service or Deepseek
- Secrets: Azure Key Vault
- Search: Azure AI Search (for vector embeddings)

To migrate: Replace MemoryManager file I/O with `@azure/cosmos` SDK calls. Connection strings via environment variables.

## Debugging with MCP Inspector

Primary tool for development and teaching demonstrations:

```bash
npm run inspector
# Opens web interface at http://localhost:5173
# Shows: Available tools, resources, recent requests
# Can: Call tools manually, read resources, view JSON responses
```

**Common debugging scenarios**:
- Tool not appearing: Check `ListToolsRequestSchema` handler
- Resource not found: Check URI string in `ReadResourceRequestSchema`
- Enrichment failing: Check console.error logs (all logged to stderr)
- Memory not persisting: Verify `data/memory.json` permissions

## File Structure

```
coretext-mcp/
├── src/
│   ├── index.js              # Complete MCP server (single file by design)
│   └── test-client.js        # Test harness for tool validation
├── data/
│   └── memory.json           # Persisted memories (auto-created)
├── .env.example              # Configuration template
├── package.json              # Dependencies + scripts
├── README.md                 # User-facing documentation
├── TEACHING_GUIDE.md         # Complete 4-segment lesson plan
└── CLAUDE.md                 # This file
```

**Single-file design**: All classes in `src/index.js` for teaching clarity - students can see entire architecture in one file.

## Common Modifications

### Adding a new tool
1. Add tool definition to `ListToolsRequestSchema` handler (line ~417)
2. Add case to `CallToolRequestSchema` switch statement (line ~547)
3. Implement logic using MemoryManager methods
4. Return `{ content: [{ type: 'text', text: JSON.stringify(...) }] }`

### Adding a new resource
1. Add resource to `ListResourcesRequestSchema` handler (line ~765)
2. Add URI check to `ReadResourceRequestSchema` handler (line ~789)
3. Generate content (markdown or JSON)
4. Return `{ contents: [{ uri, mimeType, text }] }`

### Changing storage backend
Replace MemoryManager methods:
- `initialize()`: Connect to DB instead of reading file
- `persist()`: Write to DB instead of file
- `create/read/update/delete`: Use DB SDK

### Adding new enrichment provider
Modify DeepseekEnrichmentService:
- Change `baseUrl` and `model` properties
- Update `makeAPICall()` request format
- Parse response in `enrich()` method
- Maintain fallback for resilience

## Testing Workflow

### Automated Testing (Recommended Before Class)
```bash
# Run full test suite - validates all 8 tools and 3 resources
npm test

# Expected output:
# ✅ 14 tests covering:
#    - All 8 tools (create, read, update, delete, search, list, stats, enrich)
#    - All 3 resources (overview, context-stream, knowledge-graph)
#    - Cleanup (deletes test memories)
#
# Success rate: 100% means server is ready for teaching
```

**What the test client validates**:
- Tool availability (all 8 tools present)
- Resource availability (all 3 resources present)
- CRUD operations (create, read, update, delete)
- Search functionality
- Statistics generation
- Enrichment (both API and fallback modes)
- Resource content integrity

### Manual Testing (During Class Demos)
```bash
# Start Inspector for visual demos
npm run inspector

# Test basic CRUD
1. memory_create with content
2. memory_list to see it
3. memory_read with ID
4. memory_update with changes
5. memory_delete to remove

# Test enrichment
1. memory_create with enrich: true
2. Verify enrichment object in response

# Test resources
1. Read memory://overview
2. Read memory://context-stream
3. Read memory://knowledge-graph
```

### Health Endpoint (Azure Deployment)
```bash
# Check server health (runs automatically on port 3000)
curl http://localhost:3000/health

# Returns:
{
  "status": "healthy",
  "timestamp": "2025-10-29T...",
  "memoryCount": 5,
  "enrichmentConfigured": true,
  "uptime": 123.45
}
```

This endpoint is used by:
- Docker HEALTHCHECK in Dockerfile
- Azure Container Apps health probes
- Load balancers and monitoring systems

## Teaching Context

This server is intentionally simple for educational purposes:

**What's included**: CRUD operations, two memory types, AI enrichment, knowledge graphs, context streams

**What's excluded**: Authentication, multi-user, rate limiting, full vector search (Azure AI Search needed)

**Design decisions**:
- Single file architecture for teaching clarity
- Console.error for all logging (stderr keeps stdout clean for MCP protocol)
- Demo memories auto-created (students see working examples)
- Emoji in logs (makes debugging more engaging)
- Graceful fallback (works without API key)

## Integration Patterns

### Claude Desktop
Primary use case - native MCP support. Memories persist across Claude conversations.

### VS Code
Via MCP extensions. Memories shared across workspace sessions.

### Custom Applications
Import `@modelcontextprotocol/sdk` and connect via stdio transport.

## Security Considerations

**Current** (Teaching/Local):
- API keys in .env (gitignored)
- No authentication on tools
- Local file system storage

**Production** (Azure):
- Azure Key Vault for secrets
- Managed Identity for service-to-service auth
- Cosmos DB with RBAC
- Network isolation via VNET

## Performance Characteristics

- Memory operations: <10ms (local JSON)
- Search latency: <50ms (linear scan)
- Enrichment: 500-2000ms (API dependent)
- Storage limit: 100MB (JSON file size)

For scale: Migrate to Cosmos DB (unlimited), add indexing, implement vector search.
