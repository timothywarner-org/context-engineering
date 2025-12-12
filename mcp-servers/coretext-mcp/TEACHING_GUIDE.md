# 📚 CORETEXT MCP SERVER - COMPLETE TEACHING GUIDE

## 🎯 CORE TEACHING OBJECTIVES

1. **The Problem**: AI has amnesia - forgets everything between sessions
2. **The Solution**: MCP provides persistent context via tools and resources  
3. **The Implementation**: CRUD operations, memory types, enrichment
4. **The Production Path**: Local JSON → Azure Container Apps → Cosmos DB

---

## 🚀 DEMO FLOW (4 SEGMENTS)

### SEGMENT 1: FROM PROMPTS TO PERSISTENT CONTEXT (55 min)

#### Demo 1: The Amnesia Problem (10 min)

```bash
# Show ChatGPT forgetting
ChatGPT: "Remember my favorite color is blue"
[New Session]
ChatGPT: "What's my favorite color?"
→ It doesn't know!
```

**TEACHING POINT**: Context windows are temporary. Tokens are expensive. Copy-paste doesn't scale.

#### Demo 2: Deploy CoreText MCP (10 min)

```bash
cd C:\github\coretext-mcp
npm install
npm run inspector

# Show the tool list in Inspector
# Point out the 8 tools and 3 resources
```

**TEACHING POINT**: MCP is a universal protocol. Works with Claude, ChatGPT (via plugins), Copilot.

#### Demo 3: Create Your First Memory (10 min)

```javascript
// In MCP Inspector, call memory_create
{
  "content": "Tim prefers dark themes and uses VS Code with Monokai Pro",
  "type": "semantic",
  "tags": ["preferences", "tim", "vscode"],
  "enrich": false  // Start without enrichment
}

// Response shows:
// - Unique ID generated
// - Metadata with timestamps
// - Ready for persistence
```

**TEACHING POINT**: Semantic memory = facts. Episodic memory = events.

#### Demo 4: Prove Persistence (10 min)

```bash
# Stop the server (Ctrl+C)
# Restart it
npm run inspector

# Call memory_list
→ Memory is still there!

# Show the JSON file
cat data/memory.json
```

**TEACHING POINT**: Context survives restarts. This is the "aha!" moment.

#### Exercise 1: Students Create Memories (10 min)

Have students create:

- One semantic memory (a fact)
- One episodic memory (an event)
- Search for their memories

---

### SEGMENT 2: BUILDING YOUR CONTEXT STACK (55 min)

#### Demo 5: The Two Memory Types (15 min)

```javascript
// Create episodic memory
{
  "content": "Had breakthrough discussion about MCP authentication at 2:15pm with the team",
  "type": "episodic",
  "tags": ["meeting", "mcp", "authentication", "team"],
  "enrich": false
}

// Create related semantic memory
{
  "content": "MCP authentication uses API keys stored in environment variables for security",
  "type": "semantic", 
  "tags": ["mcp", "authentication", "security", "api"],
  "enrich": false
}

// Call memory_stats
→ Shows breakdown of memory types
```

**TEACHING POINT**: Episodic = timeline, Semantic = knowledge base. Humans use both!

#### Demo 6: Search and Discovery (10 min)

```javascript
// Search for "authentication"
{
  "query": "authentication",
  "limit": 10
}
→ Returns both memories!

// Search for "meeting"
{
  "query": "meeting",
  "limit": 10  
}
→ Returns only episodic memory
```

**TEACHING POINT**: Tags and content are both searchable. This is how AI finds relevant context.

#### Demo 7: Enrichment with Deepseek (15 min)

```javascript
// Create and enrich in one step
{
  "content": "Azure Container Apps provides serverless containers with automatic scaling and built-in KEDA support",
  "type": "semantic",
  "tags": ["azure", "containers", "serverless"],
  "enrich": true  // NOW we enrich!
}

// Response shows:
// - Keywords extracted
// - Sentiment analyzed
// - Category identified
// - Summary generated

// Or enrich existing memory
{
  "id": "existing-memory-id"
}
// Call memory_enrich tool
```

**TEACHING POINT**: Enrichment adds AI analysis. Works WITH key (Deepseek) or WITHOUT (fallback).

#### Demo 8: Resource Access (10 min)

```javascript
// Access the overview resource
Read resource: memory://overview

→ Shows markdown dashboard with:
  - Statistics
  - Recent activity
  - Most accessed memories
  - Tag cloud

// Access the context stream
Read resource: memory://context-stream

→ Shows JSON with:
  - Recent memories (last hour)
  - Today's context
  - Active topics
```

**TEACHING POINT**: Resources are always available. AI doesn't need to call tools to see them.

---

### SEGMENT 3: ADVANCED PATTERNS - MULTI-AGENT MEMORY (55 min)

#### Demo 9: The Knowledge Graph (15 min)

```javascript
// Create interconnected memories
1. "MCP enables persistent context for AI assistants"
   tags: ["mcp", "context", "ai"]

2. "Context persistence solves the token window limitation"
   tags: ["context", "tokens", "limitation"]

3. "AI assistants like Claude and ChatGPT benefit from MCP"
   tags: ["ai", "claude", "chatgpt", "mcp"]

// Access knowledge graph
Read resource: memory://knowledge-graph

→ Shows:
  - Nodes (memories)
  - Edges (connections via shared tags)
  - Clusters (groups of related memories)
  - Connection strength
```

**TEACHING POINT**: Memories don't exist in isolation. They form semantic networks!

#### Demo 10: Context Stream in Action (15 min)

```javascript
// Rapid-fire memory creation to show stream
- Create 5 memories quickly
- Access memory://context-stream after each

→ Watch as memories move through:
  - recentContext (< 1 hour)
  - todayContext (< 24 hours)
  - earlierContext (older)
```

**TEACHING POINT**: Working memory (recent) vs long-term memory (earlier). Just like human cognition!

#### Demo 11: CRUD Operations Deep Dive (10 min)

```javascript
// Full CRUD cycle
1. CREATE: memory_create
2. READ: memory_read with ID
3. UPDATE: memory_update to change content
4. DELETE: memory_delete to remove

// Show how metadata tracks everything:
- created timestamp
- updated timestamp
- accessCount increments
- lastAccessed updates
```

**TEACHING POINT**: Every operation is tracked. This enables analytics and optimization.

#### Demo 12: Multi-Agent Scenario (10 min)

```
Scenario: Customer Service + Technical Support

1. Customer Service Agent creates:
   "Customer reported login issues with error code 403"
   type: episodic, tags: ["customer", "login", "error"]

2. Technical Support Agent searches:
   query: "error 403"
   → Finds the customer service memory

3. Technical Support creates:
   "Error 403 is caused by expired authentication tokens"
   type: semantic, tags: ["error", "authentication", "solution"]

4. Knowledge graph shows connection!
```

**TEACHING POINT**: Different agents share the same memory pool. Context flows between them!

---

### SEGMENT 4: PRODUCTION REALITY (45 min)

#### Demo 13: Security Patterns (10 min)

```bash
# Show authentication hierarchy
1. System environment variable (most secure)
   echo $DEEPSEEK_API_KEY

2. .env file (development)
   cat .env

3. Config file (demo only)
   cat claude_desktop_config.json

4. Never hardcode!
```

**TEACHING POINT**: API keys follow hierarchy. Production uses Azure Key Vault.

#### Demo 14: Azure Deployment Path (10 min)

```bash
# Show Docker setup
cat Dockerfile

# Explain migration path:
1. Current: JSON file (data/memory.json)
2. Next: Azure Cosmos DB
3. Future: Azure AI Search (vectors)

# Show where to modify:
- MemoryManager class
- Replace file operations with Cosmos SDK
- Add connection string from Key Vault
```

**TEACHING POINT**: Architecture is cloud-ready. Minimal changes for production.

#### Demo 15: Performance & Scale (10 min)

```javascript
// Show stats
memory_stats

// Discuss metrics:
- Memory operations: < 10ms (local)
- Search latency: < 50ms
- Storage: 100MB JSON limit
- Cosmos DB: Unlimited scale
- Vector search: Semantic similarity

// Cost considerations:
- Tokens saved by not repeating context
- API calls reduced via caching
- Enrichment on-demand vs automatic
```

**TEACHING POINT**: MCP saves money by reducing token usage. Context is cached, not repeated.

#### Demo 16: Real-World Integration (10 min)

```json
// Show Claude Desktop config
{
  "mcpServers": {
    "coretext": {
      "command": "node",
      "args": ["C:\\github\\coretext-mcp\\src\\index.js"]
    }
  }
}

// Explain integration points:
- Claude: Native MCP support
- ChatGPT: Via plugins/actions
- Copilot: Through extensions
- Custom apps: MCP SDK
```

**TEACHING POINT**: MCP is becoming the standard. Early adoption = competitive advantage.

---

## 🎓 KEY TEACHING MOMENTS

### The "Aha!" Moments

1. **Persistence Demo**: Stop/start server, memory survives
2. **Knowledge Graph**: See memories connect automatically
3. **Context Stream**: Watch conversation continuity in real-time
4. **Enrichment**: AI analyzes and categorizes memories

### Common Questions & Answers

**Q: Why not just use a database directly?**
A: MCP provides a standard interface that works across AI tools. It's the protocol layer.

**Q: How is this different from RAG?**
A: RAG retrieves documents. MCP manages structured context with CRUD operations.

**Q: What about privacy?**
A: Local deployment, encrypted storage, API key management, RBAC ready.

**Q: Can this scale?**
A: Yes! Cosmos DB for storage, Container Apps for compute, AI Search for vectors.

### Troubleshooting Tips

1. **"Cannot find module"**
   - Run `npm install`
   - Check Node version (>=18)

2. **"API key not found"**
   - Check environment variable: `echo $DEEPSEEK_API_KEY`
   - Fallback mode still works!

3. **"Memory not persisting"**
   - Check data/memory.json exists
   - Verify write permissions

4. **"Inspector not working"**
   - Update to latest: `npm update @modelcontextprotocol/inspector`
   - Try direct start: `node src/index.js`

---

## 📝 STUDENT EXERCISES

### Exercise 1: Basic CRUD (10 min)

1. Create a semantic memory about yourself
2. Create an episodic memory about today
3. Search for one of your memories
4. Update it with new content
5. Check the stats

### Exercise 2: Enrichment (10 min)

1. Create a technical memory
2. Enrich it (with or without API)
3. Compare enriched vs non-enriched
4. View the enrichment metadata

### Exercise 3: Knowledge Building (15 min)

1. Create 5 related memories about a topic
2. Use consistent tags
3. View the knowledge graph
4. Identify the cluster formed
5. Find the strongest connections

### Exercise 4: Context Stream (10 min)

1. Create memories at different times
2. Access some memories (to update lastAccessed)
3. View context stream
4. Observe the time windows
5. Note which memories are "hot"

---

## 🚀 TAKEAWAYS FOR STUDENTS

### What You've Learned

✅ MCP solves the context persistence problem
✅ CRUD operations enable structured memory management
✅ Episodic vs Semantic memory mirrors human cognition
✅ Resources provide always-available context
✅ Authentication patterns for production systems
✅ Migration path from local to cloud

### What You Can Do Now

✅ Build MCP servers for your use cases
✅ Integrate with Claude, ChatGPT, Copilot
✅ Deploy to Azure Container Apps
✅ Implement Cosmos DB storage
✅ Add vector search with Azure AI

### Next Steps

1. **Today**: Install and run CoreText locally
2. **This Week**: Build your own MCP server
3. **This Month**: Deploy to production
4. **This Quarter**: Integrate with your apps

---

## 📚 ADDITIONAL RESOURCES

### Documentation

- [MCP Specification](https://modelcontextprotocol.io)
- [Azure Container Apps](https://learn.microsoft.com/azure/container-apps)
- [Cosmos DB](https://learn.microsoft.com/azure/cosmos-db)
- [Azure AI Search](https://learn.microsoft.com/azure/search)

### Code Samples

- [CoreText MCP Server](https://github.com/timothywarner-org/context-engineering)
- [MCP SDK Examples](https://github.com/modelcontextprotocol/sdk)

### Tim's Resources

- [TechTrainerTim.com](https://techtrainertim.com)
- [YouTube Channel](https://youtube.com/@techtrainertim)
- [O'Reilly Courses](https://oreilly.com/instructors/tim-warner)

---

*Remember: The goal isn't just to teach MCP, but to show how persistent context transforms AI from a goldfish into an elephant that never forgets!*
