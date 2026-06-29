# Context Engineering with MCP - Reimagined Course Plan

This document provides the complete 4-segment breakdown for the **Context Engineering with MCP** course. Each segment is 50 minutes with 10-minute breaks between segments.

---

## Course Structure Overview

| Segment | Duration | Topic | Key Deliverable |
|---------|----------|-------|-----------------|
| 1 | 50 min | All About Context | Understanding context windows, token economics, and why AI forgets |
| 2 | 50 min | All About MCP | MCP protocol deep-dive with FastMCP and FastAPI |
| 3 | 50 min | CoALA Four-Tier Memory | All four tiers (Working / Episodic / Semantic / Procedural) live in WARNERCO with the consolidation "sleep cycle" |
| 4 | 50 min | MCP in Production Clients | Claude Code, GitHub Copilot, VS Code, and LangGraph integration |

**Total Duration:** 4 hours (including breaks)

---

## Segment 1: All About Context - Why Your AI Has Amnesia

**Duration:** 50 minutes
**Format:** Interactive lecture + demonstrations

### Learning Objectives

By the end of this segment, participants will be able to:

- Explain how token budgets and context windows fundamentally limit AI capabilities
- Calculate effective context capacity for different models
- Identify the four types of context loss in AI systems
- Describe the economic implications of context management
- Articulate why traditional RAG isn't always enough

### Topics Covered (45 minutes)

#### 1. The Context Window Deep-Dive (15 minutes)

**What is a Context Window?**

The context window is the AI's "working memory" - everything the model can consider when generating a response.

```
┌─────────────────────────────────────────────────────────────────┐
│                    CONTEXT WINDOW (200K tokens)                  │
├─────────────────────────────────────────────────────────────────┤
│  System Prompt    │  Conversation History  │  Current Query     │
│  (1-5K tokens)    │  (variable)            │  + Output Buffer   │
│                   │                        │  (4-8K tokens)     │
└─────────────────────────────────────────────────────────────────┘
```

**Token Economics:**

| Model | Max Context | Cost per 1M Input | Cost per 1M Output |
|-------|-------------|-------------------|-------------------|
| Claude Sonnet 4 | 200K | $3.00 | $15.00 |
| Claude Opus 4 | 200K | $15.00 | $75.00 |
| GPT-4o | 128K | $2.50 | $10.00 |
| Gemini 2.0 | 2M | $0.075 | $0.30 |

**The Critical Formula:**

```
Effective Context = Max Tokens - System Prompt - Output Buffer - Safety Margin
                  = 200,000 - 5,000 - 8,000 - 10,000
                  = 177,000 tokens available for YOUR content
```

**Demo: Watching Context Evaporate**

Live demonstration showing:
1. Start a conversation with specific facts
2. Continue until facts are "forgotten"
3. Measure exactly where context loss occurs

#### 2. The Four Types of Context Loss (10 minutes)

**Type 1: Window Overflow**
- Oldest messages pushed out as new ones arrive
- Most common in long conversations
- Solution: Summarization + selective retention

**Type 2: Session Boundary**
- Complete context loss between sessions
- User returns next day - AI remembers nothing
- Solution: Persistent memory stores (our focus!)

**Type 3: Attention Dilution**
- Context exists but gets "lost in the noise"
- Model focuses on wrong parts
- Solution: Strategic context organization

**Type 4: Compression Loss**
- Summarization loses critical details
- Trade-off between length and fidelity
- Solution: Hierarchical memory + retrieval

#### 3. Why RAG Isn't Enough (10 minutes)

**Traditional RAG Architecture:**

```
User Query → Embedding → Vector Search → Top-K Chunks → LLM → Response
```

**RAG Limitations:**

1. **Static Knowledge**: Only retrieves what's in the index
2. **No Memory**: Doesn't remember user preferences
3. **No Learning**: Can't adapt from interactions
4. **Chunking Problems**: Context fragmentation

**What We Need: Context Engineering**

```
User Query → Context Assembly Pipeline:
              ├── Working Memory (current session)
              ├── Episodic Memory (past conversations)
              ├── Semantic Memory (knowledge base)
              └── Procedural Memory (learned patterns)
            → Optimized Context → LLM → Response + Memory Update
```

**This four-tier mental model is from CoALA — Cognitive Architectures for Language Agents (Sumers et al. 2024).** Hold this in your head; in Segment 3 we're going to see all four tiers exercised in one running app.

#### 4. The Context Engineering Solution (10 minutes)

**Definition:**

> Context Engineering is the systematic design and optimization of what information an AI system can access, remember, and utilize across interactions.

**The Three Pillars:**

1. **Capture**: What context to preserve
2. **Store**: Where and how to persist it
3. **Retrieve**: When and what to bring back

**MCP as the Standard:**

Model Context Protocol provides:
- Standardized tool interface
- Resource management
- Prompt templates
- Cross-client compatibility

**Course Roadmap:**

```
Segment 1 (Now)     → Understanding the Problem
Segment 2 (Next)    → MCP Protocol & Tools
Segment 3           → CoALA Four-Tier Memory in WARNERCO
Segment 4           → Production Client Integration
```

### Exercise: Context Capacity Calculator (5 minutes)

**Task:** Calculate the effective context for your use case.

Given:
- Model: Claude Sonnet 4 (200K context)
- System prompt: 3,000 tokens
- Conversation turns to keep: 10
- Average turn length: 500 tokens
- Output buffer: 4,000 tokens

Calculate:
1. Tokens used by conversation history
2. Remaining tokens for retrieved context
3. Cost per conversation hour (assume 60 queries)

### Key Takeaways

- Context windows are expensive and finite resources
- Four types of context loss require different solutions
- RAG solves retrieval but not memory
- Context Engineering = Capture + Store + Retrieve
- MCP standardizes context management across AI clients

---

## Segment 2: All About MCP - The Universal Context Protocol

**Duration:** 50 minutes
**Format:** Live coding with FastMCP and FastAPI

### Learning Objectives

By the end of this segment, participants will be able to:

- Explain MCP's architecture and transport mechanisms
- Build an MCP server using FastMCP (Python)
- Implement tools, resources, and prompts
- Test servers using MCP Inspector
- Expose MCP servers via FastAPI for remote access

### Topics Covered (40 minutes)

#### 1. MCP Architecture Deep-Dive (10 minutes)

**What is MCP?**

Model Context Protocol is a JSON-RPC based protocol for AI-tool communication, created by Anthropic and adopted by Microsoft.

**Protocol Components:**

```
┌─────────────────────────────────────────────────────────────────┐
│                        MCP PROTOCOL                              │
├────────────────┬────────────────┬────────────────┬──────────────┤
│     TOOLS      │   RESOURCES    │    PROMPTS     │   SAMPLING   │
│ (Functions AI  │ (Data AI can   │ (Reusable      │ (Request LLM │
│  can invoke)   │  read)         │  templates)    │  completions)│
└────────────────┴────────────────┴────────────────┴──────────────┘
```

**Transport Mechanisms:**

| Transport | Use Case | Security | Latency |
|-----------|----------|----------|---------|
| stdio | Local processes | Excellent | Lowest |
| HTTP+SSE | Remote servers | Good (with TLS) | Low |
| WebSocket | Real-time bidirectional | Good (with TLS) | Lowest |

**MCP Message Flow:**

```
Client                           Server
  │                                │
  │──── initialize ───────────────►│
  │◄─── capabilities ─────────────│
  │                                │
  │──── tools/list ───────────────►│
  │◄─── tool definitions ──────────│
  │                                │
  │──── tools/call ───────────────►│
  │◄─── tool result ──────────────│
```

#### 2. FastMCP: Python-First MCP Development (15 minutes)

**Why FastMCP?**

- Pythonic decorators for tools/resources
- Built-in Pydantic validation
- Automatic schema generation
- Development server included

**Project Setup:**

```bash
# Create project
mkdir memory-mcp-server && cd memory-mcp-server

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install fastmcp pydantic anthropic
```

**Basic FastMCP Server:**

```python
# server.py
from fastmcp import FastMCP
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import json

# Initialize MCP server
mcp = FastMCP("memory-server")

# ============================================================================
# Pydantic Models for Input Validation
# ============================================================================

class MemoryInput(BaseModel):
    """Input model for storing a memory."""
    content: str = Field(..., description="The content to remember", min_length=1, max_length=10000)
    category: str = Field(default="general", description="Memory category")
    tags: Optional[List[str]] = Field(default_factory=list, description="Tags for organization")
    importance: int = Field(default=5, ge=1, le=10, description="Importance score 1-10")

class SearchInput(BaseModel):
    """Input model for searching memories."""
    query: str = Field(..., description="Search query", min_length=1)
    limit: int = Field(default=10, ge=1, le=100, description="Max results")

# ============================================================================
# In-Memory Storage (Replace with persistent store in production)
# ============================================================================

memories: List[dict] = []

# ============================================================================
# MCP Tools
# ============================================================================

@mcp.tool()
async def store_memory(params: MemoryInput) -> str:
    """Store a new memory with metadata.

    Use this tool to save important information, facts, user preferences,
    or any content that should be remembered across sessions.
    """
    memory = {
        "id": f"mem_{len(memories):04d}",
        "content": params.content,
        "category": params.category,
        "tags": params.tags,
        "importance": params.importance,
        "created_at": datetime.utcnow().isoformat(),
    }
    memories.append(memory)

    return json.dumps({
        "success": True,
        "memory_id": memory["id"],
        "message": f"Memory stored successfully with importance {params.importance}"
    }, indent=2)

@mcp.tool()
async def search_memories(params: SearchInput) -> str:
    """Search stored memories by content or tags.

    Returns memories that match the search query, sorted by relevance.
    """
    query_lower = params.query.lower()
    results = []

    for mem in memories:
        score = 0
        if query_lower in mem["content"].lower():
            score += 10
        if any(query_lower in tag.lower() for tag in mem.get("tags", [])):
            score += 5
        if query_lower in mem.get("category", "").lower():
            score += 3

        if score > 0:
            results.append({**mem, "_score": score})

    # Sort by score, then by importance
    results.sort(key=lambda x: (x["_score"], x["importance"]), reverse=True)

    return json.dumps({
        "query": params.query,
        "count": len(results[:params.limit]),
        "results": results[:params.limit]
    }, indent=2)

@mcp.tool()
async def list_memories(category: Optional[str] = None) -> str:
    """List all memories, optionally filtered by category."""
    filtered = memories if not category else [m for m in memories if m["category"] == category]

    return json.dumps({
        "total": len(filtered),
        "memories": filtered
    }, indent=2)

@mcp.tool()
async def clear_memories() -> str:
    """Clear all stored memories. Use with caution!"""
    global memories
    count = len(memories)
    memories = []
    return json.dumps({
        "success": True,
        "cleared": count,
        "message": f"Cleared {count} memories"
    })

# ============================================================================
# MCP Resources
# ============================================================================

@mcp.resource("memory://stats")
async def get_memory_stats() -> str:
    """Get memory system statistics."""
    categories = {}
    for mem in memories:
        cat = mem.get("category", "general")
        categories[cat] = categories.get(cat, 0) + 1

    return json.dumps({
        "total_memories": len(memories),
        "categories": categories,
        "avg_importance": sum(m["importance"] for m in memories) / len(memories) if memories else 0
    }, indent=2)

@mcp.resource("memory://recent")
async def get_recent_memories() -> str:
    """Get the 10 most recent memories."""
    recent = sorted(memories, key=lambda x: x["created_at"], reverse=True)[:10]
    return json.dumps(recent, indent=2)

# ============================================================================
# MCP Prompts
# ============================================================================

@mcp.prompt()
async def summarize_context() -> str:
    """Generate a prompt for summarizing current context."""
    return f"""You have access to {len(memories)} stored memories.

Categories: {', '.join(set(m['category'] for m in memories)) or 'None'}

Please provide a brief summary of the user's context based on their stored memories.
Focus on the most important items (importance >= 7) and recent entries."""

# ============================================================================
# Entry Point
# ============================================================================

if __name__ == "__main__":
    mcp.run()
```

#### 3. Testing with MCP Inspector (5 minutes)

**Launch Inspector:**

```bash
# No install — runs on demand via npx (Node 20+ required)
npx @modelcontextprotocol/inspector python server.py

# For the WARNERCO live demo:
npx @modelcontextprotocol/inspector uv run warnerco-mcp
```

**Inspector Workflow:**

1. Open http://localhost:5173
2. View discovered tools and resources
3. Test tool invocations interactively
4. Inspect JSON-RPC messages
5. Debug errors in real-time

#### 4. FastAPI Integration for Remote Access (10 minutes)

**Why FastAPI?**

- Production-ready HTTP server
- Automatic OpenAPI documentation
- SSE support for MCP transport
- Easy authentication integration

**Combined FastMCP + FastAPI Server:**

```python
# api_server.py
from fastmcp import FastMCP
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import StreamingResponse
from sse_starlette.sse import EventSourceResponse
import uvicorn
import json
from typing import AsyncGenerator

# Initialize both frameworks
mcp = FastMCP("memory-server")
app = FastAPI(title="Memory MCP Server", version="1.0.0")

# ... (include all the MCP tools from above) ...

# ============================================================================
# FastAPI Endpoints
# ============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "memories": len(memories)}

@app.get("/sse")
async def sse_endpoint(request: Request):
    """SSE endpoint for MCP communication."""

    async def event_generator() -> AsyncGenerator:
        # Send capabilities on connect
        yield {
            "event": "message",
            "data": json.dumps({
                "jsonrpc": "2.0",
                "method": "capabilities",
                "params": {
                    "tools": True,
                    "resources": True,
                    "prompts": True
                }
            })
        }

        # Keep connection alive
        while True:
            if await request.is_disconnected():
                break
            yield {"event": "ping", "data": ""}
            await asyncio.sleep(30)

    return EventSourceResponse(event_generator())

@app.post("/message")
async def handle_message(request: Request):
    """Handle incoming MCP messages."""
    body = await request.json()

    # Route to MCP server
    response = await mcp.handle_request(body)
    return response

# ============================================================================
# REST API Convenience Endpoints
# ============================================================================

@app.post("/api/memories")
async def create_memory(content: str, category: str = "general", tags: list = []):
    """REST endpoint to create a memory (convenience wrapper)."""
    result = await store_memory(MemoryInput(content=content, category=category, tags=tags))
    return json.loads(result)

@app.get("/api/memories")
async def get_all_memories(category: str = None):
    """REST endpoint to list memories."""
    result = await list_memories(category)
    return json.loads(result)

@app.get("/api/memories/search")
async def search(query: str, limit: int = 10):
    """REST endpoint to search memories."""
    result = await search_memories(SearchInput(query=query, limit=limit))
    return json.loads(result)

# ============================================================================
# Entry Point
# ============================================================================

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### Exercise: Build Your First MCP Server (10 minutes)

**Task:** Extend the memory server with a new tool.

**Requirements:**

1. Add a `get_memory_by_id` tool
2. Input: memory ID string
3. Output: Full memory object or error
4. Add proper error handling

**Starter Code:**

```python
@mcp.tool()
async def get_memory_by_id(memory_id: str) -> str:
    """Retrieve a specific memory by its ID.

    Args:
        memory_id: The unique identifier of the memory (e.g., 'mem_0001')

    Returns:
        The memory object if found, or an error message.
    """
    # YOUR CODE HERE
    pass
```

### Key Takeaways

- MCP standardizes AI-tool communication via JSON-RPC
- FastMCP makes Python MCP development intuitive
- Tools, Resources, and Prompts serve different purposes
- FastAPI enables production HTTP/SSE deployment
- MCP Inspector is essential for development and debugging

---

## Segment 3: CoALA Four-Tier Memory — Persistent AI Memory in WARNERCO

**Duration:** 50 minutes
**Format:** Hands-on tour of the WARNERCO app with multiple memory tiers

### Learning Objectives

By the end of this segment, participants will be able to:

- Name and distinguish the four CoALA memory tiers (Working / Episodic / Semantic / Procedural)
- Choose the right storage backend per tier (JSON / SQLite / Chroma / Azure AI Search)
- Recognize when episodic recall should fire (gated by query intent)
- Trace the Park et al. recency × importance × relevance scoring formula in `warn_episodic_recall` output
- Trigger a consolidation cycle (the "sleep cycle") and observe the side effects across tiers
- Identify which MCP primitive carries each tier's reads and writes (Tools, Resources, Prompts, Sampling)

### Topics Covered (40 minutes)

#### 1. Memory Storage Spectrum (5 minutes)

**Choosing the Right Backend:**

```
Simple ←──────────────────────────────────────────────────→ Powerful

JSON File    SQLite       ChromaDB        Pinecone/Weaviate
  │            │             │                   │
  │            │             │                   │
Quick Start  Structured   Local Vectors    Cloud Scale
No Setup     SQL Queries  Semantic Search  Production Ready
Dev Only     Good for     Great for        Enterprise
             Medium       Most Cases       Features
```

**Decision Matrix:**

| Backend | Best For | Limitations |
|---------|----------|-------------|
| JSON | Prototyping, <1000 items | No search, no concurrent writes |
| SQLite | Structured data, SQL queries | No vector search built-in |
| ChromaDB | Local vector search, development | Single-node only |
| Pinecone | Production vector search, scale | Cost, external dependency |

#### 2. JSON Memory Store (5 minutes)

**Simple but Effective:**

```python
# memory_stores/json_store.py
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any
from threading import Lock

class JSONMemoryStore:
    """Thread-safe JSON-based memory store for development."""

    def __init__(self, filepath: str = "memories.json"):
        self.filepath = Path(filepath)
        self.lock = Lock()
        self._ensure_file()

    def _ensure_file(self):
        """Create file if it doesn't exist."""
        if not self.filepath.exists():
            self._save({"memories": [], "metadata": {"version": "1.0"}})

    def _load(self) -> Dict[str, Any]:
        with open(self.filepath, 'r') as f:
            return json.load(f)

    def _save(self, data: Dict[str, Any]):
        with open(self.filepath, 'w') as f:
            json.dump(data, f, indent=2)

    def store(self, content: str, metadata: Dict[str, Any] = None) -> str:
        """Store a memory and return its ID."""
        with self.lock:
            data = self._load()
            memory_id = f"mem_{len(data['memories']):06d}"

            memory = {
                "id": memory_id,
                "content": content,
                "metadata": metadata or {},
                "created_at": datetime.utcnow().isoformat(),
            }

            data["memories"].append(memory)
            self._save(data)
            return memory_id

    def search(self, query: str, limit: int = 10) -> List[Dict]:
        """Simple substring search."""
        data = self._load()
        query_lower = query.lower()

        results = [
            m for m in data["memories"]
            if query_lower in m["content"].lower()
        ]
        return results[:limit]

    def get(self, memory_id: str) -> Optional[Dict]:
        """Get a specific memory by ID."""
        data = self._load()
        for m in data["memories"]:
            if m["id"] == memory_id:
                return m
        return None

    def delete(self, memory_id: str) -> bool:
        """Delete a memory by ID."""
        with self.lock:
            data = self._load()
            original_len = len(data["memories"])
            data["memories"] = [m for m in data["memories"] if m["id"] != memory_id]

            if len(data["memories"]) < original_len:
                self._save(data)
                return True
            return False
```

#### 3. SQLite Memory Store (5 minutes)

**Structured and Queryable:**

```python
# memory_stores/sqlite_store.py
import sqlite3
from datetime import datetime
from typing import Optional, List, Dict, Any
from contextlib import contextmanager
import json

class SQLiteMemoryStore:
    """SQLite-based memory store with full-text search."""

    def __init__(self, db_path: str = "memories.db"):
        self.db_path = db_path
        self._init_db()

    @contextmanager
    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def _init_db(self):
        """Initialize database schema."""
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id TEXT PRIMARY KEY,
                    content TEXT NOT NULL,
                    category TEXT DEFAULT 'general',
                    tags TEXT,  -- JSON array
                    importance INTEGER DEFAULT 5,
                    metadata TEXT,  -- JSON object
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Create FTS5 table for full-text search
            conn.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS memories_fts USING fts5(
                    content,
                    category,
                    tags,
                    content=memories,
                    content_rowid=rowid
                )
            """)

            # Triggers to keep FTS in sync
            conn.execute("""
                CREATE TRIGGER IF NOT EXISTS memories_ai AFTER INSERT ON memories BEGIN
                    INSERT INTO memories_fts(rowid, content, category, tags)
                    VALUES (new.rowid, new.content, new.category, new.tags);
                END
            """)

            conn.commit()

    def store(self, content: str, category: str = "general",
              tags: List[str] = None, importance: int = 5,
              metadata: Dict[str, Any] = None) -> str:
        """Store a memory with metadata."""
        memory_id = f"mem_{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}"

        with self._get_connection() as conn:
            conn.execute("""
                INSERT INTO memories (id, content, category, tags, importance, metadata)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                memory_id,
                content,
                category,
                json.dumps(tags or []),
                importance,
                json.dumps(metadata or {})
            ))
            conn.commit()

        return memory_id

    def search(self, query: str, limit: int = 10) -> List[Dict]:
        """Full-text search using FTS5."""
        with self._get_connection() as conn:
            cursor = conn.execute("""
                SELECT m.*, bm25(memories_fts) as rank
                FROM memories m
                JOIN memories_fts ON m.rowid = memories_fts.rowid
                WHERE memories_fts MATCH ?
                ORDER BY rank
                LIMIT ?
            """, (query, limit))

            return [dict(row) for row in cursor.fetchall()]

    def get(self, memory_id: str) -> Optional[Dict]:
        """Get a specific memory by ID."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM memories WHERE id = ?", (memory_id,)
            )
            row = cursor.fetchone()
            return dict(row) if row else None

    def list_by_category(self, category: str, limit: int = 50) -> List[Dict]:
        """List memories by category."""
        with self._get_connection() as conn:
            cursor = conn.execute("""
                SELECT * FROM memories
                WHERE category = ?
                ORDER BY importance DESC, created_at DESC
                LIMIT ?
            """, (category, limit))
            return [dict(row) for row in cursor.fetchall()]

    def delete(self, memory_id: str) -> bool:
        """Delete a memory by ID."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "DELETE FROM memories WHERE id = ?", (memory_id,)
            )
            conn.commit()
            return cursor.rowcount > 0
```

#### 4. CoALA Four-Tier Memory in WARNERCO (20 minutes) — **THE LIVE DEMO**

This block replaces the standalone ChromaDB + Pinecone walkthroughs from earlier drafts of the plan. The flagship app already implements all four CoALA tiers — we'll show them in one continuous turn-by-turn scenario. Full classroom script: [`docs/tutorials/coala-memory-walkthrough.md`](../docs/tutorials/coala-memory-walkthrough.md).

**The four tiers, mapped to the WARNERCO app:**

| CoALA Tier | What it stores | Backed by | LangGraph node | Read tools |
|---|---|---|---|---|
| Working | This-session observations & inferences | `data/scratchpad/notes.db` (SQLite) | `inject_scratchpad` | `warn_scratchpad_read` |
| Episodic | Timestamped events with importance | `data/episodic/events.db` (SQLite) | `recall_episodes` (gated) + `log_episode` | `warn_episodic_recall` |
| Semantic | Durable facts (incl. consolidated `FACT-*`) | Vector store (Chroma / Azure / JSON) | `retrieve` | `warn_semantic_search` |
| Procedural | Versioned skills/workflows | `@mcp.prompt()` registrations | (user-invoked) | `memory://procedural-catalog` |

Pre-flight (do once before class — see `instructor/PRE-CLASS-CHECKLIST.md`):

```bash
cd src/warnerco/backend
uv sync
uv run python -c "from app.adapters.chroma_store import ChromaMemoryStore; import asyncio; asyncio.run(ChromaMemoryStore().index_all())"
uv run python scripts/index_graph.py
rm -f data/episodic/events.db data/scratchpad/notes.db   # fresh slate for class
uv run warnerco-restart
# Second terminal:
npx @modelcontextprotocol/inspector uv run warnerco-mcp
```

**Live demo path (4 minutes — hits all four tiers):**

| Step | Tool / Resource | What students see |
|---|---|---|
| 0 | Read `memory://coala-overview` | Empty snapshot: working=0, episodic=0, semantic=25, procedural=5 |
| 1 | `warn_scratchpad_write` (working) | LLM minimization + enrichment, token-savings metrics |
| 2 | `warn_semantic_search` with `session_id="class-demo"` | Diagnostic intent fires the 9-node pipeline; `recalled_episodes=[]` first time |
| 3 | Same query, second time | `recalled_episodes=[...]` — episodic recall surfaces turn 1 |
| 3b | `warn_episodic_recall` | **Park et al. score breakdown** visible: `{recency, importance, relevance, total}` per event |
| 4 | `warn_semantic_search("get WRN-00006")` | Lookup intent SKIPS episodic recall (gating works) |
| 5 | `warn_consolidate_memory` | Sleep cycle: `ctx.sample()` extracts durable facts → `FACT-*` records appear in vector store |
| 6 | `warn_semantic_search("consolidated")` | The new FACT records show up |
| 7 | Read `memory://procedural-catalog` | 5 versioned prompts as procedural memory |
| 8 | Read `memory://coala-overview` again | All four tiers now have non-zero counts — close the loop |

**Episodic recall scoring** (the slide-worthy moment of the segment):

```
total = α_recency · 0.5^(hours_since / half_life)
      + α_importance · stored_importance
      + α_relevance · bag_of_words_cosine(query, summary+content)
```

Defaults: `α_recency=0.4, α_importance=0.3, α_relevance=0.3, half_life=24h`. Override via `EPISODIC_*` env vars (already pre-pinned in `.claude/mcp.json` and `.vscode/mcp.json` under the `warnerco-coala-memory` server entry).

**Pedagogical simplifications to call out:**

- Relevance uses bag-of-words cosine, not embeddings. Three lines of code, zero embedding spend per recall. Swap-in to embeddings is a 3-line edit at `_relevance()` in `app/adapters/episodic_store.py`. Production agents use the latter.
- Consolidation is **ADD-only**. Mem0's full ADD/UPDATE/DELETE/NOOP is left as homework.
- Consolidated facts ride the existing `Schematic` shape with `category="consolidated_fact"`, not a separate "fact" collection. Filterable by tag.

**Pinecone, Weaviate, and other production vector stores** — covered as slide-only material with the line: *"Same idea as Azure AI Search above — swap the adapter, keep the LangGraph nodes. The scoring formula and the four CoALA tiers don't change."*

#### 6. Unified Memory Interface (5 minutes)

**Abstract Interface for Any Backend:**

```python
# memory_stores/interface.py
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from enum import Enum

class MemoryBackend(str, Enum):
    JSON = "json"
    SQLITE = "sqlite"
    CHROMA = "chroma"
    PINECONE = "pinecone"

class MemoryStore(ABC):
    """Abstract interface for memory stores."""

    @abstractmethod
    def store(self, content: str, **kwargs) -> str:
        """Store a memory and return its ID."""
        pass

    @abstractmethod
    def search(self, query: str, limit: int = 10, **kwargs) -> List[Dict]:
        """Search for memories."""
        pass

    @abstractmethod
    def get(self, memory_id: str) -> Optional[Dict]:
        """Get a specific memory by ID."""
        pass

    @abstractmethod
    def delete(self, memory_id: str) -> bool:
        """Delete a memory by ID."""
        pass

def create_memory_store(backend: MemoryBackend, **kwargs) -> MemoryStore:
    """Factory function to create memory stores."""
    if backend == MemoryBackend.JSON:
        from .json_store import JSONMemoryStore
        return JSONMemoryStore(**kwargs)
    elif backend == MemoryBackend.SQLITE:
        from .sqlite_store import SQLiteMemoryStore
        return SQLiteMemoryStore(**kwargs)
    elif backend == MemoryBackend.CHROMA:
        from .chroma_store import ChromaMemoryStore
        return ChromaMemoryStore(**kwargs)
    elif backend == MemoryBackend.PINECONE:
        from .pinecone_store import PineconeMemoryStore
        return PineconeMemoryStore(**kwargs)
    else:
        raise ValueError(f"Unknown backend: {backend}")
```

### Exercise: Trigger Consolidation in WARNERCO (10 minutes)

**Task:** Drive the WARNERCO app through one full consolidation cycle and observe the side effects across all four CoALA tiers.

**Requirements:**

1. Start with a clean `data/episodic/events.db` and `data/scratchpad/notes.db`
2. Write 2–3 working-memory notes via `warn_scratchpad_write`
3. Run 2–3 diagnostic queries with the same `session_id` so episodic memory accumulates real events
4. Call `warn_consolidate_memory(since_minutes=60, max_facts=3)`
5. Verify:
   - Vector store gained `FACT-*` records (search for `consolidated`)
   - Episodic memory gained an `OBSERVATION` event ("Consolidation promoted N facts")
   - `memory://coala-overview` reflects the new counts

**Bonus:** Re-run a related diagnostic query and watch the consolidated facts surface in retrieval (Tier 3 now informs the answer to a question that was originally answered from Tier 1 + 2). This is the moment the "memory engineering" thesis becomes self-evident.

**What to type (paste-ready):**

```bash
# In MCP Inspector, call these tools in order:
warn_scratchpad_write subject="WRN-00006" predicate="observed" object_="thermal_system" \
  content="Operator reports thermal subsystem trips during heavy hydraulic load"

warn_semantic_search query="thermal subsystem failing on hydraulics" session_id="class-demo"
warn_semantic_search query="thermal subsystem failing on hydraulics" session_id="class-demo"  # twice

warn_consolidate_memory since_minutes=60 max_facts=3 session_id="class-demo"

warn_semantic_search query="consolidated"   # see FACT-* records
warn_episodic_recent limit=10               # see the OBSERVATION event
```

The complete walkthrough with narration cues is in [`docs/tutorials/coala-memory-walkthrough.md`](../docs/tutorials/coala-memory-walkthrough.md).

### Key Takeaways

- JSON for prototyping, SQLite for structure, vector stores (Chroma / Azure / Pinecone) for semantics
- The CoALA framework (Sumers et al. 2024) gives you the *vocabulary* — Working / Episodic / Semantic / Procedural — for talking about agent memory
- WARNERCO implements all four tiers in one Python codebase under `src/warnerco/backend/app/`
- The "sleep cycle" (`warn_consolidate_memory`) uses MCP Sampling to promote short-term observations into durable knowledge
- Episodic recall is gated by query intent — LOOKUP and SEARCH skip it; DIAGNOSTIC and ANALYTICS use it
- Pedagogical simplifications (bag-of-words relevance, ADD-only consolidation) are flagged in code with `# CoALA NOTE` comments — production hardening is the homework
- Abstract interfaces (`MemoryStore`, `EpisodicStore`, `ScratchpadStore`) let you swap backends without touching the LangGraph nodes

---

## Segment 4: MCP in Production Clients - Real-World Integration

**Duration:** 50 minutes
**Format:** Live integration demos + hands-on exercises

### Learning Objectives

By the end of this segment, participants will be able to:

- Configure Claude Desktop and Claude Code with custom MCP servers
- Integrate MCP with GitHub Copilot in VS Code
- Build multi-agent workflows with LangGraph and MCP
- Deploy production-ready MCP infrastructure
- Implement proper authentication and monitoring

### Topics Covered (40 minutes)

#### 1. Claude Desktop Integration (10 minutes)

**Configuration File Locations:**

| OS | Config Path |
|-----|------------|
| macOS | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| Windows | `%APPDATA%\Claude\claude_desktop_config.json` |
| Linux | `~/.config/Claude/claude_desktop_config.json` |

**Basic Configuration:**

```json
{
  "mcpServers": {
    "memory": {
      "command": "python",
      "args": ["/path/to/memory_server.py"],
      "env": {
        "ANTHROPIC_API_KEY": "your-key-here"
      }
    },
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/workspace"]
    }
  }
}
```

**Remote Server Configuration (SSE):**

```json
{
  "mcpServers": {
    "remote-memory": {
      "url": "https://your-server.azurewebsites.net/sse",
      "transport": "sse",
      "headers": {
        "Authorization": "Bearer ${MEMORY_API_KEY}"
      }
    }
  }
}
```

**Demo: Memory-Enabled Claude Desktop**

1. Configure memory MCP server
2. Store project context
3. Close and reopen conversation
4. Verify context persistence

#### 2. Claude Code Integration (10 minutes)

**Claude Code MCP Configuration:**

Claude Code reads `.mcp.json` (project root) or `.claude/mcp.json` (project-scoped). Root key is `mcpServers` (note the camelCase — it's different from VS Code, which uses `servers`).

```json
// .claude/mcp.json in your project root
{
  "mcpServers": {
    "warnerco-coala-memory": {
      "type": "stdio",
      "command": "uv",
      "args": ["run", "warnerco-mcp"],
      "cwd": "C:/github/context-engineering/src/warnerco/backend",
      "env": {
        "MEMORY_BACKEND": "chroma",
        "EPISODIC_DB_PATH": "data/episodic/events.db"
      },
      "permissions": {
        "sampling": "allowed"
      }
    }
  }
}
```

This is the **actual config** checked into this repo at `.claude/mcp.json` — the WARNERCO server exposes 28 tools including all four CoALA tiers.

**Using Memory in Claude Code:**

```bash
# Initialize Claude Code in your project
claude

# Claude Code will automatically discover MCP servers
# You can now use memory tools in your coding session

> Remember that we decided to use FastAPI for the backend
[Claude stores this in memory via MCP]

> What framework did we decide to use?
[Claude retrieves from memory: "FastAPI for the backend"]
```

**Project Context Persistence:**

```python
# Example: Project-aware memory server
from fastmcp import FastMCP
import os
import json

mcp = FastMCP("project-memory")

PROJECT_ROOT = os.environ.get("PROJECT_ROOT", ".")
MEMORY_FILE = os.path.join(PROJECT_ROOT, ".claude", "project_memory.json")

@mcp.tool()
async def remember_decision(decision: str, context: str, tags: list = []) -> str:
    """Store a project decision with context."""
    data = load_or_create_memory()

    data["decisions"].append({
        "decision": decision,
        "context": context,
        "tags": tags,
        "timestamp": datetime.utcnow().isoformat()
    })

    save_memory(data)
    return f"Decision recorded: {decision[:50]}..."

@mcp.tool()
async def get_project_context() -> str:
    """Get all project decisions and context."""
    data = load_or_create_memory()
    return json.dumps(data, indent=2)
```

#### 3. VS Code + GitHub Copilot (10 minutes)

**VS Code MCP Configuration:**

VS Code reads `.vscode/mcp.json` (NOT `settings.json`). Root key is `servers` (singular `mcp` namespace is older/deprecated). Per-server `"type"` is required — values: `stdio`, `http`, `sse`.

```json
// .vscode/mcp.json
{
  "servers": {
    "warnerco-coala-memory": {
      "type": "stdio",
      "command": "uv",
      "args": ["run", "warnerco-mcp"],
      "cwd": "${workspaceFolder}/src/warnerco/backend",
      "env": {
        "MEMORY_BACKEND": "chroma",
        "EPISODIC_DB_PATH": "data/episodic/events.db"
      },
      "dev": {
        "watch": "src/warnerco/backend/app/**/*.py",
        "debug": { "type": "python" }
      }
    }
  }
}
```

This is the **actual config** in this repo at `.vscode/mcp.json`. The `dev.watch` block is VS-Code-only — it hot-reloads the server when you edit `.py` files during a live demo.

To list/start servers: `Cmd/Ctrl+Shift+P → MCP: List Servers`. In Copilot Chat: `@warnerco-coala-memory <prompt>` to scope a query to that server.

#### 4. LangGraph Multi-Agent Integration (10 minutes)

**LangGraph + MCP Architecture:**

```
┌─────────────────────────────────────────────────────────────┐
│                    LANGGRAPH WORKFLOW                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   ┌─────────┐      ┌─────────┐      ┌─────────┐           │
│   │Research │ ───► │ Analyze │ ───► │ Generate│           │
│   │ Agent   │      │  Agent  │      │  Agent  │           │
│   └────┬────┘      └────┬────┘      └────┬────┘           │
│        │                │                │                 │
│        └────────────────┼────────────────┘                 │
│                         │                                   │
│                         ▼                                   │
│              ┌──────────────────┐                          │
│              │   MCP Memory     │                          │
│              │     Server       │                          │
│              └──────────────────┘                          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**LangGraph with MCP Memory:**

```python
# langgraph_mcp.py
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, AIMessage
from typing import TypedDict, Annotated, Sequence
import operator

# MCP Client for memory access
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# ============================================================================
# State Definition
# ============================================================================

class AgentState(TypedDict):
    messages: Annotated[Sequence[HumanMessage | AIMessage], operator.add]
    memory_context: str
    current_task: str

# ============================================================================
# MCP Memory Integration
# ============================================================================

class MCPMemoryClient:
    """Client for interacting with MCP memory server."""

    def __init__(self, server_command: list):
        self.server_params = StdioServerParameters(
            command=server_command[0],
            args=server_command[1:]
        )
        self.session = None

    async def connect(self):
        """Establish connection to MCP server."""
        self.read, self.write = await stdio_client(self.server_params).__aenter__()
        self.session = ClientSession(self.read, self.write)
        await self.session.initialize()

    async def store_memory(self, content: str, category: str = "general") -> str:
        """Store a memory via MCP tool."""
        result = await self.session.call_tool(
            "store_memory",
            {"content": content, "category": category}
        )
        return result.content[0].text

    async def search_memories(self, query: str, limit: int = 5) -> str:
        """Search memories via MCP tool."""
        result = await self.session.call_tool(
            "search_memories",
            {"query": query, "limit": limit}
        )
        return result.content[0].text

    async def get_context(self) -> str:
        """Get relevant context for current task."""
        result = await self.session.read_resource("memory://recent")
        return result.contents[0].text

# ============================================================================
# Agent Nodes
# ============================================================================

memory_client = MCPMemoryClient(["python", "memory_server.py"])

async def research_node(state: AgentState) -> AgentState:
    """Research node that retrieves relevant memories."""
    # Get relevant context from memory
    context = await memory_client.search_memories(state["current_task"])

    model = ChatAnthropic(model="claude-sonnet-4-20250514")

    response = await model.ainvoke([
        HumanMessage(content=f"""
        Task: {state["current_task"]}

        Relevant context from memory:
        {context}

        Research this topic and provide key findings.
        """)
    ])

    # Store findings in memory
    await memory_client.store_memory(
        response.content,
        category="research"
    )

    return {
        **state,
        "messages": state["messages"] + [response],
        "memory_context": context
    }

async def analyze_node(state: AgentState) -> AgentState:
    """Analyze node that processes research findings."""
    model = ChatAnthropic(model="claude-sonnet-4-20250514")

    response = await model.ainvoke([
        HumanMessage(content=f"""
        Based on the research:
        {state["messages"][-1].content}

        Analyze and synthesize the key insights.
        """)
    ])

    # Store analysis
    await memory_client.store_memory(
        response.content,
        category="analysis"
    )

    return {
        **state,
        "messages": state["messages"] + [response]
    }

async def generate_node(state: AgentState) -> AgentState:
    """Generate final output based on analysis."""
    model = ChatAnthropic(model="claude-sonnet-4-20250514")

    response = await model.ainvoke([
        HumanMessage(content=f"""
        Based on the analysis:
        {state["messages"][-1].content}

        Generate a comprehensive response to: {state["current_task"]}
        """)
    ])

    return {
        **state,
        "messages": state["messages"] + [response]
    }

# ============================================================================
# Graph Construction
# ============================================================================

def create_workflow():
    """Create the LangGraph workflow with MCP memory."""
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("research", research_node)
    workflow.add_node("analyze", analyze_node)
    workflow.add_node("generate", generate_node)

    # Define edges
    workflow.set_entry_point("research")
    workflow.add_edge("research", "analyze")
    workflow.add_edge("analyze", "generate")
    workflow.add_edge("generate", END)

    return workflow.compile()

# ============================================================================
# Usage
# ============================================================================

async def main():
    # Connect to MCP memory server
    await memory_client.connect()

    # Create and run workflow
    workflow = create_workflow()

    result = await workflow.ainvoke({
        "messages": [],
        "memory_context": "",
        "current_task": "Analyze the best practices for API authentication"
    })

    print("Final response:", result["messages"][-1].content)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

#### 5. Production Deployment (5 minutes)

**Azure Deployment with Authentication:**

```python
# production_server.py
from fastmcp import FastMCP
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os

mcp = FastMCP("production-memory")
app = FastAPI()
security = HTTPBearer()

# Authentication
async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify JWT or API key."""
    token = credentials.credentials

    # In production, verify against Azure AD or your auth provider
    valid_tokens = os.environ.get("API_TOKENS", "").split(",")

    if token not in valid_tokens:
        raise HTTPException(status_code=401, detail="Invalid token")

    return token

# Protected MCP endpoint
@app.post("/mcp/message", dependencies=[Depends(verify_token)])
async def handle_mcp_message(request: dict):
    """Authenticated MCP message handler."""
    return await mcp.handle_request(request)
```

**Docker Deployment:**

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "production_server:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Azure Container Apps:**

```bash
# Deploy to Azure
az containerapp create \
  --name memory-mcp-server \
  --resource-group mcp-production \
  --environment mcp-env \
  --image myregistry.azurecr.io/memory-mcp:latest \
  --target-port 8000 \
  --ingress external \
  --secrets api-tokens=secretref:api-tokens \
  --env-vars API_TOKENS=secretref:api-tokens
```

### Exercise: End-to-End Integration (10 minutes)

**Task:** Set up a complete memory-enabled development workflow.

**Steps:**

1. Start the memory MCP server locally
2. Configure Claude Desktop to use it
3. Store some project decisions
4. Verify persistence across sessions
5. (Bonus) Configure Claude Code in a project

**Verification Checklist:**

- [ ] MCP server starts without errors
- [ ] Claude Desktop shows MCP tools available
- [ ] Can store and retrieve memories
- [ ] Memories persist after restart
- [ ] Search returns relevant results

### Key Takeaways

- Claude Desktop, Claude Code, and VS Code all support MCP
- Configuration varies by client but follows similar patterns
- LangGraph enables multi-agent workflows with shared memory
- Production deployment requires authentication and monitoring
- Start local, scale to cloud when needed

---

## Course Wrap-Up & Next Steps

### What You Built

During this 4-hour course, you:

✅ Understood context windows, token economics, and the four types of context loss
✅ Built MCP servers using FastMCP with Python
✅ Toured all four CoALA memory tiers (Working / Episodic / Semantic / Procedural) live in the WARNERCO app
✅ Triggered the consolidation "sleep cycle" via MCP Sampling and saw short-term observations promote into durable knowledge
✅ Integrated MCP with Claude Desktop, Claude Code, and VS Code Copilot using the actual `.claude/mcp.json` and `.vscode/mcp.json` configs in this repo
✅ Walked the 9-node LangGraph pipeline that exercises every tier in one turn
✅ Learned production deployment patterns (Azure Container Apps + APIM)

### Repository Contents

```
context-engineering/
├── src/warnerco/backend/             # WARNERCO Schematica — flagship teaching app
│   ├── app/
│   │   ├── adapters/                 # Memory backends (JSON, Chroma, Azure, Graph, Scratchpad, Episodic, CoALA overview)
│   │   ├── langgraph/                # 9-node CoALA-tiered RAG pipeline + consolidation cycle
│   │   ├── models/                   # Pydantic models (schematic, graph, scratchpad, episodic)
│   │   ├── main.py                   # FastAPI + FastMCP combined server
│   │   └── mcp_tools.py              # 28 tools, 11 resources, 5 prompts
│   ├── data/
│   │   ├── schematics/schematics.json  # 25 robot schematics (source of truth)
│   │   └── graph/knowledge.db          # 117 entities, 221 relationships
│   └── scripts/                      # Index helpers + warnerco-restart
├── labs/lab-01-hello-mcp/            # Beginner Node.js MCP lab (starter + solution)
├── docs/
│   ├── tutorials/
│   │   ├── coala-memory-walkthrough.md   # ★ Tim's class-anchor demo script
│   │   ├── graph-memory-tutorial.md
│   │   ├── progressive-tool-loading.md
│   │   └── demo-sampling-vscode.md
│   ├── diagrams/                     # Mermaid + rendered SVG/PNG architecture diagrams
│   ├── INSTRUCTOR_DEMO_WALKTHROUGH.md
│   ├── STUDENT_SETUP_GUIDE.md
│   └── TROUBLESHOOTING_FAQ.md
├── instructor/                       # Instructor-only materials (this plan, deck, checklist)
├── research_synthesis/               # 4 deep-research reports on agent memory
├── config/claude_desktop_config.json # Sample Claude Desktop MCP config
├── .vscode/mcp.json                  # VS Code Copilot MCP config (checked in)
├── .claude/mcp.json                  # Claude Code project-scoped MCP config (checked in)
├── CLAUDE.md                         # Source of truth for development
└── README.md
```

There is no `mcp-servers/` directory and no `lab-02..04` — earlier plan drafts referenced those; they were folded into `src/warnerco/backend/` (which IS the production-quality MCP server) and a single hands-on lab respectively. The four-segment course covers more memory ground than four labs ever could.

### Taking It Further

**Immediate Next Steps:**

1. Deploy your memory server to Azure
2. Add more sophisticated retrieval (hybrid search)
3. Implement memory summarization for long-term storage
4. Build domain-specific memory schemas
5. Add monitoring and analytics

**Advanced Topics to Explore:**

- Memory compression and summarization
- Multi-tenant memory isolation
- Real-time memory synchronization
- Custom embedding models
- Memory lifecycle management

### Community Resources

- [MCP Specification](https://spec.modelcontextprotocol.io/)
- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [Anthropic Claude Documentation](https://docs.anthropic.com/)
- [Course Repository](https://github.com/timothywarner-org/context-engineering)

---

**Thank you for participating! Now go build AI systems that actually remember!** 🧠
