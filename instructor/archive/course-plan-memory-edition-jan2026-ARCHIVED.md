# Context Engineering with MCP - Memory Edition Course Plan

**Date:** Wednesday, January 29, 2026
**Duration:** 4 hours (4 x 50-minute segments with 10-minute breaks)
**Instructor:** Tim Warner

---

## Course Structure Overview

| Segment | Duration | Topic | Key Focus |
|---------|----------|-------|-----------|
| 1 | 50 min | **Memory and AI: The Complete Picture** | Memory types, cognitive architectures, why AI forgets |
| 2 | 50 min | **Built-in Memory in SaaS AI Tools** | Claude Desktop, ChatGPT, Claude Code memory features |
| 3 | 50 min | **Enterprise Memory: Copilot Studio & Integration** | Copilot Studio memory, custom connectors, orchestration |
| 4 | 50 min | **Building Your Own: The WARNERCO Approach** | Code walkthrough, architecture deep-dive, future patterns |

---

## Segment 1: Memory and AI - The Complete Picture

**Duration:** 50 minutes
**Format:** Interactive lecture with diagrams

### Learning Objectives

By the end of this segment, participants will be able to:

- Explain the four types of memory in AI systems (episodic, semantic, procedural, working)
- Articulate why context windows are fundamentally limited
- Distinguish between short-term and long-term memory approaches
- Understand the memory hierarchy in cognitive AI architectures

### Topics Covered (45 minutes)

#### 1. Human Memory as the Blueprint (10 minutes)

**The Four Memory Types:**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     MEMORY TYPES IN AI SYSTEMS                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────┐  ┌─────────────────────┐                          │
│  │   WORKING MEMORY    │  │   EPISODIC MEMORY   │                          │
│  │  "What am I doing   │  │   "What happened    │                          │
│  │      right now?"    │  │     last time?"     │                          │
│  │                     │  │                     │                          │
│  │  • Context window   │  │  • Conversation     │                          │
│  │  • Current tokens   │  │    history          │                          │
│  │  • Session state    │  │  • Past sessions    │                          │
│  │                     │  │  • Time-stamped     │                          │
│  └─────────────────────┘  └─────────────────────┘                          │
│                                                                             │
│  ┌─────────────────────┐  ┌─────────────────────┐                          │
│  │   SEMANTIC MEMORY   │  │  PROCEDURAL MEMORY  │                          │
│  │   "What do I know   │  │   "How do I do      │                          │
│  │     as facts?"      │  │      things?"       │                          │
│  │                     │  │                     │                          │
│  │  • Knowledge bases  │  │  • Learned patterns │                          │
│  │  • Vector stores    │  │  • Fine-tuning      │                          │
│  │  • RAG retrieval    │  │  • Tool sequences   │                          │
│  │                     │  │  • Best practices   │                          │
│  └─────────────────────┘  └─────────────────────┘                          │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Memory Characteristics:**

| Memory Type | Persistence | Access Pattern | AI Implementation |
|-------------|-------------|----------------|-------------------|
| Working | Session only | Immediate | Context window |
| Episodic | Long-term | Time-based | Conversation logs, summaries |
| Semantic | Permanent | Query-based | RAG, knowledge graphs |
| Procedural | Model weights | Automatic | Fine-tuning, RLHF |

#### 2. The Context Window Problem (10 minutes)

**The Fundamental Constraint:**

```
┌─────────────────────────────────────────────────────────────────┐
│              CONTEXT WINDOW ANATOMY (200K tokens)                │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  System Prompt ████████ (1-5K)                                   │
│  Memory Context ████████████████ (variable - THIS IS NEW!)       │
│  Conversation  ████████████████████████████████ (variable)       │
│  Current Query ████████ (1-2K)                                   │
│  Output Buffer ████████████ (4-8K reserved)                      │
│                                                                  │
│  [═══════════════════════════════════════════════> 200K max     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**The Four Types of Context Loss:**

1. **Window Overflow** - Oldest tokens pushed out as new ones arrive
2. **Session Boundary** - Complete amnesia between conversations
3. **Attention Dilution** - Important context buried in noise
4. **Compression Loss** - Summarization loses critical details

#### 3. Memory Architectures in Modern AI (15 minutes)

**The Memory Hierarchy:**

```
┌────────────────────────────────────────────────────────────────────────┐
│                    AI MEMORY HIERARCHY                                  │
├────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  TIER 1: IMMEDIATE (Milliseconds)                                       │
│  ├── Context Window                                                     │
│  └── In-memory cache                                                    │
│                                                                         │
│  TIER 2: SHORT-TERM (Seconds to Minutes)                               │
│  ├── Conversation summaries                                             │
│  ├── Session state                                                      │
│  └── Working memory buffers                                             │
│                                                                         │
│  TIER 3: LONG-TERM (Hours to Forever)                                  │
│  ├── Vector databases (ChromaDB, Pinecone)                             │
│  ├── Knowledge graphs (Neo4j, NetworkX)                                │
│  ├── Structured storage (SQL, JSON)                                     │
│  └── User preference stores                                             │
│                                                                         │
│  TIER 4: PERMANENT (Model level)                                        │
│  ├── Training data patterns                                             │
│  ├── Fine-tuned behaviors                                               │
│  └── RLHF learned preferences                                           │
│                                                                         │
└────────────────────────────────────────────────────────────────────────┘
```

**Key Research Concepts:**

- **MemGPT** - Self-managed memory through tool calling
- **Adaptive Retention** - Deciding what to keep vs. forget
- **Progressive Disclosure** - Context loading based on session type
- **Compression Strategies** - Episodic to semantic transformation

#### 4. Why This Matters: The Business Case (10 minutes)

**Token Economics:**

| Model | Context | Input Cost/1M | Output Cost/1M |
|-------|---------|---------------|----------------|
| Claude Sonnet 4 | 200K | $3.00 | $15.00 |
| Claude Opus 4.5 | 200K | $15.00 | $75.00 |
| GPT-4o | 128K | $2.50 | $10.00 |
| Gemini 2.0 | 2M | $0.075 | $0.30 |

**Memory Reduces Costs By:**
- Avoiding repeated context loading
- Summarizing instead of storing full transcripts
- Retrieving only relevant chunks
- Caching expensive computations

### Key Takeaways

- AI memory maps to human cognitive models
- Context windows are expensive and limited
- Four memory types serve different purposes
- Memory architecture determines AI capability

---

## Segment 2: Built-in Memory in SaaS AI Tools

**Duration:** 50 minutes
**Format:** Live demos + configuration walkthrough

### Learning Objectives

By the end of this segment, participants will be able to:

- Configure and use Claude Desktop memory features
- Enable and customize ChatGPT memory
- Leverage Claude Code's session and project memory
- Understand the trade-offs of built-in vs. custom memory

### Topics Covered (45 minutes)

#### 1. Claude Desktop Memory (15 minutes)

**Memory Features:**

- **Projects** - Organize conversations with persistent context
- **Custom Instructions** - User preferences that persist
- **Conversation Persistence** - Searchable history
- **MCP Integration** - Custom memory servers (we'll build one!)

**Demo: Setting Up a Research Project**

1. Create new Project in Claude Desktop
2. Add project instructions
3. Upload reference documents
4. Show context persistence across conversations

**Configuration:**

```json
{
  "mcpServers": {
    "memory": {
      "command": "python",
      "args": ["/path/to/memory_server.py"]
    }
  }
}
```

#### 2. ChatGPT Memory (10 minutes)

**Memory Capabilities:**

- **Automatic Memory** - Learns from conversations
- **Manual Memory** - Explicit "remember this"
- **Memory Management** - View, edit, delete memories
- **Temporary Chat** - Disable memory when needed

**Key Differences from Claude:**

| Feature | Claude Desktop | ChatGPT |
|---------|---------------|---------|
| Memory Storage | Projects + MCP | Built-in system |
| User Control | High (explicit) | Medium (implicit) |
| Memory Editing | Via Projects | Direct UI |
| Enterprise Ready | MCP integration | Limited |
| Privacy Controls | Granular | Basic |

**Demo: ChatGPT Memory in Action**

1. Enable memory in settings
2. Have ChatGPT learn preferences
3. View stored memories
4. Delete specific memories

#### 3. Claude Code Memory (15 minutes)

**Memory Layers:**

```
┌────────────────────────────────────────────────────────────────────────┐
│                    CLAUDE CODE MEMORY STACK                            │
├────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  LAYER 1: Session Memory                                               │
│  └── Current conversation context, tool calls, decisions               │
│                                                                         │
│  LAYER 2: Project Memory (.claude/mcp.json)                            │
│  └── MCP servers, project-specific tools, configurations               │
│                                                                         │
│  LAYER 3: Codebase Understanding (Implicit)                            │
│  └── File structure, patterns, conventions discovered                  │
│                                                                         │
│  LAYER 4: User Instructions (CLAUDE.md)                                │
│  └── Project preferences, coding standards, decisions                  │
│                                                                         │
│  LAYER 5: MCP Memory Servers (Custom)                                  │
│  └── Persistent memory via MCP tools                                   │
│                                                                         │
└────────────────────────────────────────────────────────────────────────┘
```

**Demo: Claude Code Session Memory**

1. Start Claude Code in a project
2. Make architectural decisions
3. Show context retention within session
4. Demonstrate CLAUDE.md for persistent preferences

**Memory MCP Configuration:**

```json
// .claude/mcp.json
{
  "servers": {
    "project-memory": {
      "command": "python",
      "args": ["./mcp-servers/memory_server.py"],
      "env": {
        "MEMORY_PATH": "./.claude/memories.json"
      }
    }
  }
}
```

#### 4. Trade-offs: Built-in vs. Custom (5 minutes)

**Decision Matrix:**

| Consideration | Built-in Memory | Custom MCP Memory |
|---------------|-----------------|-------------------|
| Setup Time | Zero | Hours to days |
| Customization | Limited | Unlimited |
| Data Control | Vendor holds | You control |
| Enterprise Compliance | Varies | Full control |
| Cross-tool Sharing | No | Yes |
| Semantic Search | Usually no | Yes with vectors |
| Cost | Included | Infrastructure + dev |

### Exercise: Memory Audit (5 minutes)

1. Check what ChatGPT remembers about you
2. Review Claude Desktop project settings
3. Identify gaps in current memory approach

### Key Takeaways

- SaaS tools now include memory features
- Each has different trade-offs
- Claude Code's MCP integration enables custom memory
- Built-in works for basic needs; custom for enterprise

---

## Segment 3: Enterprise Memory - Copilot Studio & Integration

**Duration:** 50 minutes
**Format:** Live demo + architecture discussion

### Learning Objectives

By the end of this segment, participants will be able to:

- Configure Copilot Studio for memory-enabled agents
- Integrate external memory systems via connectors
- Design enterprise memory architectures
- Implement memory patterns for compliance

### Topics Covered (40 minutes)

#### 1. Copilot Studio Memory Capabilities (15 minutes)

**Built-in Memory Features:**

- **Conversation State** - Variables persisted across turns
- **Topic Memory** - Context within conversation flows
- **User Profile** - Microsoft 365 integration
- **Knowledge Sources** - SharePoint, Dataverse, custom

**Memory Architecture in Copilot Studio:**

```
┌────────────────────────────────────────────────────────────────────────┐
│                    COPILOT STUDIO MEMORY LAYERS                        │
├────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │              MICROSOFT GRAPH (User Context)                      │   │
│  │  └── Profile, Calendar, Emails, Files, Teams                     │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                              ↓                                          │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │              KNOWLEDGE SOURCES                                   │   │
│  │  └── SharePoint, Dataverse, Custom APIs                          │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                              ↓                                          │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │              CONVERSATION MEMORY                                 │   │
│  │  └── Topic variables, User input history, Entity extraction      │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                              ↓                                          │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │              CUSTOM CONNECTORS (External Memory)                 │   │
│  │  └── MCP servers, Vector databases, Custom APIs                  │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
└────────────────────────────────────────────────────────────────────────┘
```

**Demo: Building a Memory-Enabled Copilot**

1. Create new Copilot in Copilot Studio
2. Configure knowledge sources
3. Set up conversation variables
4. Add external connector for persistent memory

#### 2. Custom Connectors for Memory (10 minutes)

**Connecting External Memory Systems:**

```
Power Automate Flow:
  Trigger: HTTP Request (from Copilot)
  → Parse JSON input
  → Call MCP Memory Server API
  → Return formatted response
```

**Example: Memory Store Connector**

```json
{
  "swagger": "2.0",
  "info": {
    "title": "Memory Store Connector",
    "version": "1.0"
  },
  "paths": {
    "/memory/store": {
      "post": {
        "operationId": "StoreMemory",
        "parameters": [
          {
            "name": "content",
            "type": "string",
            "required": true
          }
        ]
      }
    },
    "/memory/search": {
      "get": {
        "operationId": "SearchMemory",
        "parameters": [
          {
            "name": "query",
            "type": "string",
            "required": true
          }
        ]
      }
    }
  }
}
```

#### 3. Enterprise Architecture Patterns (10 minutes)

**Multi-tenant Memory Architecture:**

```
┌────────────────────────────────────────────────────────────────────────┐
│                    ENTERPRISE MEMORY ARCHITECTURE                       │
├────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                  │
│  │   Copilot    │  │   Claude     │  │    VS Code   │                  │
│  │   Studio     │  │   Desktop    │  │   + Copilot  │                  │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘                  │
│         │                 │                 │                           │
│         └─────────────────┼─────────────────┘                           │
│                           ↓                                             │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │              API GATEWAY (Authentication, Rate Limiting)         │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                           ↓                                             │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │              MCP SERVER (FastMCP + FastAPI)                      │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                           ↓                                             │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │    ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │   │
│  │    │   SQLite    │  │  ChromaDB   │  │   Pinecone  │            │   │
│  │    │  (Metadata) │  │  (Vectors)  │  │   (Scale)   │            │   │
│  │    └─────────────┘  └─────────────┘  └─────────────┘            │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
└────────────────────────────────────────────────────────────────────────┘
```

**Compliance Considerations:**

- Data residency requirements
- PII handling and encryption
- Audit logging
- Data retention policies
- Right to be forgotten

#### 4. Orchestration with LangGraph (10 minutes)

**LangGraph + MCP Memory Flow:**

```
┌─────────────────────────────────────────────────────────────────┐
│                    LANGGRAPH MEMORY FLOW                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   [User Query]                                                   │
│        ↓                                                         │
│   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│   │   PARSE     │───►│   RECALL    │───►│  RETRIEVE   │         │
│   │   INTENT    │    │   MEMORY    │    │   CONTEXT   │         │
│   └─────────────┘    └──────┬──────┘    └─────────────┘         │
│                             │                                    │
│                    [MCP Memory Server]                           │
│                             │                                    │
│   ┌─────────────┐    ┌──────┴──────┐    ┌─────────────┐         │
│   │   REASON    │───►│   STORE     │───►│   RESPOND   │         │
│   │    (LLM)    │    │   MEMORY    │    │   FORMAT    │         │
│   └─────────────┘    └─────────────┘    └─────────────┘         │
│                                                                  │
│   [Response + Updated Memory]                                    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Exercise: Design Your Memory Architecture (5 minutes)

Given requirements:
- 10,000 users
- GDPR compliance required
- Need to work with Copilot Studio AND Claude Code
- Budget: $500/month

Design the memory stack (hint: hybrid approach)

### Key Takeaways

- Copilot Studio has built-in memory capabilities
- Custom connectors enable external memory systems
- Enterprise requires multi-tenant, compliant architecture
- Orchestration frameworks like LangGraph enable complex flows

---

## Segment 4: Building Your Own - The WARNERCO Approach

**Duration:** 50 minutes
**Format:** Code walkthrough + architecture review (NO CODE CHANGES)

### Learning Objectives

By the end of this segment, participants will be able to:

- Understand production memory server architecture
- Explain the graph memory pattern
- Describe the LangGraph integration approach
- Identify future directions for AI memory

### Topics Covered (40 minutes)

#### 1. WARNERCO Schematica Architecture Review (15 minutes)

**System Overview:**

Our course companion app demonstrates real-world memory patterns.

```
┌────────────────────────────────────────────────────────────────────────┐
│                    WARNERCO SCHEMATICA ARCHITECTURE                    │
├────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  FRONTEND (React)          MCP SERVER (FastMCP)                        │
│  ├── Dashboard             ├── Memory Tools                            │
│  ├── Query Interface       │   ├── store_memory                        │
│  └── Visualization         │   ├── search_memories                     │
│                            │   └── graph_operations                    │
│         ↓                  │                                           │
│  ┌─────────────────────────┴───────────────────────────────────┐       │
│  │                    LANGGRAPH PIPELINE                        │       │
│  │  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐    │       │
│  │  │ PARSE  │→│ GRAPH  │→│RETRIEVE│→│COMPRESS│→│ REASON │    │       │
│  │  │ INTENT │ │ QUERY  │ │ VECTORS│ │CONTEXT │ │  LLM   │    │       │
│  │  └────────┘ └────────┘ └────────┘ └────────┘ └────────┘    │       │
│  └─────────────────────────────────────────────────────────────┘       │
│                            ↓                                           │
│  ┌─────────────────────────────────────────────────────────────┐       │
│  │                    HYBRID MEMORY LAYER                       │       │
│  │  ├── ChromaDB (Vector similarity)                           │       │
│  │  ├── SQLite + NetworkX (Graph relationships)                │       │
│  │  └── Azure AI Search (Production scale)                     │       │
│  └─────────────────────────────────────────────────────────────┘       │
│                                                                         │
└────────────────────────────────────────────────────────────────────────┘
```

**Code Tour (View Only):**

1. `src/warnerco/backend/app/mcp_tools.py` - MCP tool definitions
2. `src/warnerco/backend/app/adapters/` - Storage backend implementations
3. `src/warnerco/backend/app/langgraph/flow.py` - Pipeline orchestration

#### 2. Graph Memory Deep Dive (10 minutes)

**Why Graphs for Memory?**

| Query Type | Vector Search | Graph Query |
|------------|--------------|-------------|
| "Find similar items" | Excellent | Poor |
| "What depends on X?" | Poor | Excellent |
| "Path from A to B?" | N/A | Excellent |
| "Related by concept" | Good | Excellent |

**Graph Memory Architecture:**

```
┌────────────────────────────────────────────────────────────────────────┐
│                    GRAPH MEMORY ARCHITECTURE                           │
├────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  Entity (node):                Relationship (edge):                    │
│  ├── id: "WRN-00001"           ├── subject: "WRN-00001"                │
│  ├── type: robot               ├── predicate: "depends_on"            │
│  └── properties: {...}         └── object: "POW-SYSTEM"               │
│                                                                         │
│  Supported Predicates:                                                 │
│  ├── depends_on     (Component dependency)                             │
│  ├── contains       (Containment)                                      │
│  ├── has_status     (Status assignment)                                │
│  ├── manufactured_by (Manufacturing)                                   │
│  ├── compatible_with (Compatibility)                                   │
│  └── related_to     (General association)                              │
│                                                                         │
└────────────────────────────────────────────────────────────────────────┘
```

**MCP Tools for Graph Operations:**

- `warn_add_relationship` - Create triplets
- `warn_graph_neighbors` - Find connections
- `warn_graph_path` - Shortest path
- `warn_graph_stats` - Graph metrics

#### 3. The LangGraph Integration Pattern (10 minutes)

**6-Node Pipeline:**

1. **PARSE_INTENT** - Classify query type
2. **QUERY_GRAPH** - Enrich with graph relationships
3. **RETRIEVE_VECTORS** - Semantic similarity search
4. **COMPRESS_CONTEXT** - Fit within token budget
5. **REASON_LLM** - Generate response
6. **RESPOND_FORMAT** - Structure output

**Memory at Each Node:**

```python
# Conceptual flow (review only)
async def query_graph_node(state: AgentState) -> AgentState:
    """Node 2: Enrich query with graph context."""
    # Extract entities from query
    entities = extract_entities(state["query"])

    # Query graph for relationships
    graph_context = await graph_store.get_neighbors(entities)

    # Add to state for downstream nodes
    state["graph_context"] = graph_context
    return state
```

#### 4. The Future of AI Memory (10 minutes)

**Emerging Patterns:**

1. **Self-Managed Memory (MemGPT style)**
   - LLM decides what to remember/forget
   - Autonomous memory maintenance
   - Compression and summarization

2. **Cognitive Architectures**
   - Multiple memory systems working together
   - Attention-based retrieval
   - Hierarchical organization

3. **Continuous Learning**
   - Memory → Fine-tuning loop
   - Procedural memory updates
   - User preference learning

4. **Federated Memory**
   - Cross-organization sharing
   - Privacy-preserving retrieval
   - Collective intelligence

**Standards Evolution:**

- MCP 1.0 → 2.0 memory primitives
- LangChain/LangGraph memory standards
- Anthropic's memory research
- OpenAI's memory API evolution

### Exercise: Architecture Review (5 minutes)

Review the WARNERCO Schematica diagrams and identify:

1. Where episodic memory is implemented
2. Where semantic memory is implemented
3. How would you add procedural memory?

### Key Takeaways

- Hybrid memory (vectors + graphs) enables powerful queries
- LangGraph provides clean orchestration
- Production requires careful architecture decisions
- The field is rapidly evolving

---

## Course Wrap-Up & Resources

### What You Learned

- **Hour 1:** Memory types, cognitive architectures, why AI forgets
- **Hour 2:** SaaS memory in Claude Desktop, ChatGPT, Claude Code
- **Hour 3:** Enterprise patterns with Copilot Studio
- **Hour 4:** Production architecture in WARNERCO Schematica

### Resources

- [MCP Specification](https://spec.modelcontextprotocol.io/)
- [Course Repository](https://github.com/timothywarner-org/context-engineering)
- [Claude Desktop Memory Docs](https://docs.anthropic.com/)
- [Copilot Studio Documentation](https://learn.microsoft.com/copilot-studio)

### Next Steps

1. Configure memory in your current AI tools
2. Build a simple MCP memory server
3. Design your enterprise memory architecture
4. Explore the WARNERCO codebase
