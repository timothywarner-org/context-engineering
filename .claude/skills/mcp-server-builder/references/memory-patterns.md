# Memory Server Patterns

## Memory Types

### Episodic Memory
Time-bound events with context:
```python
@mcp.tool()
async def create_episodic(content: str, context: str = "") -> str:
    """Store a time-bound memory event."""
    memory = {
        "id": str(uuid.uuid4()),
        "type": "episodic",
        "content": content,
        "context": context,
        "timestamp": datetime.utcnow().isoformat(),
        "access_count": 0
    }
    # Store and return ID
```

### Semantic Memory
Timeless facts and relationships:
```python
@mcp.tool()
async def create_semantic(content: str, tags: list[str] = []) -> str:
    """Store a timeless fact or relationship."""
    memory = {
        "id": str(uuid.uuid4()),
        "type": "semantic",
        "content": content,
        "tags": tags,
        "created_at": datetime.utcnow().isoformat()
    }
```

## CRUD Operations

Standard memory server tools:

| Tool | Purpose |
|------|---------|
| `create_memory` | Add new entry, return UUID |
| `read_memory` | Get by ID, increment access_count |
| `update_memory` | Modify existing entry |
| `delete_memory` | Remove (soft-delete in production) |
| `search_memories` | Query by tags, content, type |

## Storage Backends

### JSON File (Development)
```python
from pathlib import Path
import json

DATA_FILE = Path("data/memory.json")

def load_memories():
    if DATA_FILE.exists():
        return json.loads(DATA_FILE.read_text())
    return []

def save_memories(memories):
    DATA_FILE.parent.mkdir(exist_ok=True)
    DATA_FILE.write_text(json.dumps(memories, indent=2))
```

### Cosmos DB (Production)
```python
from azure.cosmos import CosmosClient

client = CosmosClient(endpoint, credential)
container = client.get_database_client(db).get_container_client(container)

async def create_memory(memory: dict):
    return container.create_item(body=memory)

async def search_memories(query: str):
    return list(container.query_items(
        query=f"SELECT * FROM c WHERE CONTAINS(c.content, '{query}')",
        enable_cross_partition_query=True
    ))
```

## Resource Patterns

```python
@mcp.resource("memory://recent")
async def recent_memories() -> str:
    """Last 10 memories accessed."""
    memories = sorted(load_memories(), key=lambda m: m.get("timestamp", ""), reverse=True)[:10]
    return json.dumps(memories)

@mcp.resource("memory://stats")
async def memory_stats() -> str:
    """Memory system statistics."""
    memories = load_memories()
    return json.dumps({
        "total": len(memories),
        "episodic": sum(1 for m in memories if m["type"] == "episodic"),
        "semantic": sum(1 for m in memories if m["type"] == "semantic")
    })
```

## Enrichment Pattern

Optional AI enhancement:
```python
@mcp.tool()
async def enrich_memory(memory_id: str) -> str:
    """Add AI-generated tags and summary to memory."""
    memory = get_memory(memory_id)

    # Call LLM for enrichment
    enrichment = await llm.generate(f"Extract tags and summary: {memory['content']}")

    memory["tags"] = enrichment.tags
    memory["summary"] = enrichment.summary
    memory["enriched_at"] = datetime.utcnow().isoformat()

    save_memory(memory)
    return f"Enriched memory {memory_id}"
```
