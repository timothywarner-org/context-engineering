"""
Memory MCP Server with FastMCP
==============================
A production-ready MCP server for AI memory management.
Demonstrates FastMCP best practices with multiple storage backends.

Usage:
    # Development with stdio
    python server.py

    # With MCP Inspector
    mcp-inspector python server.py

Author: Tim Warner
Course: Context Engineering with MCP
"""

from fastmcp import FastMCP
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
import json
import os
import sys

# Add parent directory to path for memory_stores imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Initialize MCP server
mcp = FastMCP(
    "memory-mcp-server",
    version="1.0.0",
    description="Persistent memory for AI assistants with semantic search capabilities"
)


# ============================================================================
# Configuration
# ============================================================================

class MemoryBackend(str, Enum):
    """Available memory storage backends."""
    JSON = "json"
    SQLITE = "sqlite"
    CHROMA = "chroma"
    PINECONE = "pinecone"


# Get backend from environment, default to JSON for development
MEMORY_BACKEND = os.environ.get("MEMORY_BACKEND", "json")
MEMORY_PATH = os.environ.get("MEMORY_PATH", "memories.json")


# ============================================================================
# Pydantic Models for Input Validation
# ============================================================================

class StoreMemoryInput(BaseModel):
    """Input model for storing a memory."""
    model_config = ConfigDict(str_strip_whitespace=True, extra='forbid')

    content: str = Field(
        ...,
        description="The content to remember (facts, decisions, preferences, etc.)",
        min_length=1,
        max_length=10000
    )
    category: str = Field(
        default="general",
        description="Memory category for organization (e.g., 'decision', 'fact', 'preference')"
    )
    tags: Optional[List[str]] = Field(
        default_factory=list,
        description="Tags for filtering and organization",
        max_length=20
    )
    importance: int = Field(
        default=5,
        ge=1,
        le=10,
        description="Importance score from 1 (low) to 10 (critical)"
    )


class SearchMemoriesInput(BaseModel):
    """Input model for searching memories."""
    model_config = ConfigDict(str_strip_whitespace=True, extra='forbid')

    query: str = Field(
        ...,
        description="Search query to find relevant memories",
        min_length=1,
        max_length=500
    )
    limit: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Maximum number of results to return"
    )
    category: Optional[str] = Field(
        default=None,
        description="Filter by category"
    )
    min_importance: int = Field(
        default=0,
        ge=0,
        le=10,
        description="Minimum importance score to include"
    )


class GetMemoryInput(BaseModel):
    """Input model for retrieving a specific memory."""
    memory_id: str = Field(..., description="Unique identifier of the memory")


class DeleteMemoryInput(BaseModel):
    """Input model for deleting a memory."""
    memory_id: str = Field(..., description="Unique identifier of the memory to delete")


class UpdateMemoryInput(BaseModel):
    """Input model for updating a memory."""
    model_config = ConfigDict(str_strip_whitespace=True, extra='forbid')

    memory_id: str = Field(..., description="Unique identifier of the memory to update")
    content: Optional[str] = Field(default=None, max_length=10000)
    category: Optional[str] = Field(default=None)
    tags: Optional[List[str]] = Field(default=None)
    importance: Optional[int] = Field(default=None, ge=1, le=10)


# ============================================================================
# In-Memory Storage (Simple implementation for demo)
# Replace with memory_stores implementations for production
# ============================================================================

memories: List[Dict[str, Any]] = []
memory_counter = 0


def load_memories():
    """Load memories from file if using JSON backend."""
    global memories, memory_counter
    if MEMORY_BACKEND == "json" and os.path.exists(MEMORY_PATH):
        try:
            with open(MEMORY_PATH, 'r') as f:
                data = json.load(f)
                memories = data.get("memories", [])
                memory_counter = data.get("counter", len(memories))
        except Exception:
            memories = []
            memory_counter = 0


def save_memories():
    """Save memories to file if using JSON backend."""
    if MEMORY_BACKEND == "json":
        with open(MEMORY_PATH, 'w') as f:
            json.dump({"memories": memories, "counter": memory_counter}, f, indent=2)


# Load on startup
load_memories()


# ============================================================================
# MCP Tools
# ============================================================================

@mcp.tool(
    name="store_memory",
    annotations={
        "title": "Store Memory",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False
    }
)
async def store_memory(params: StoreMemoryInput) -> str:
    """Store a new memory for future retrieval.

    Use this tool to save important information, facts, user preferences,
    decisions, or any content that should be remembered across sessions.

    The memory will be indexed for semantic search and can be retrieved
    by content similarity, tags, or category.

    Args:
        params: StoreMemoryInput with content, category, tags, and importance

    Returns:
        JSON response with success status and memory ID
    """
    global memory_counter

    memory_counter += 1
    memory_id = f"mem_{memory_counter:06d}"
    timestamp = datetime.utcnow().isoformat()

    memory = {
        "id": memory_id,
        "content": params.content,
        "category": params.category,
        "tags": [t.lower() for t in params.tags] if params.tags else [],
        "importance": params.importance,
        "created_at": timestamp,
        "updated_at": timestamp,
        "access_count": 0
    }

    memories.append(memory)
    save_memories()

    return json.dumps({
        "success": True,
        "memory_id": memory_id,
        "message": f"Memory stored successfully (importance: {params.importance}/10)",
        "created_at": timestamp
    }, indent=2)


@mcp.tool(
    name="search_memories",
    annotations={
        "title": "Search Memories",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True
    }
)
async def search_memories(params: SearchMemoriesInput) -> str:
    """Search stored memories by content similarity.

    Performs semantic search across all stored memories, returning
    the most relevant results based on content matching.

    Results are ranked by relevance score and filtered by optional
    category and minimum importance.

    Args:
        params: SearchMemoriesInput with query, limit, and filters

    Returns:
        JSON response with matching memories and relevance scores
    """
    query_lower = params.query.lower()
    results = []

    for mem in memories:
        # Skip if category filter doesn't match
        if params.category and mem["category"] != params.category:
            continue

        # Skip if importance is below threshold
        if mem["importance"] < params.min_importance:
            continue

        # Calculate relevance score
        score = 0

        # Content match (highest weight)
        if query_lower in mem["content"].lower():
            score += 10
            # Bonus for exact phrase match
            if query_lower == mem["content"].lower():
                score += 5

        # Tag match
        if any(query_lower in tag for tag in mem.get("tags", [])):
            score += 7

        # Category match
        if query_lower in mem.get("category", "").lower():
            score += 3

        # Importance bonus
        score += mem["importance"] * 0.5

        if score > 0:
            results.append({
                **mem,
                "_relevance_score": round(score, 2)
            })

    # Sort by relevance score, then by importance
    results.sort(key=lambda x: (x["_relevance_score"], x["importance"]), reverse=True)

    # Limit results
    results = results[:params.limit]

    # Update access counts
    for result in results:
        for mem in memories:
            if mem["id"] == result["id"]:
                mem["access_count"] = mem.get("access_count", 0) + 1

    save_memories()

    return json.dumps({
        "query": params.query,
        "filters": {
            "category": params.category,
            "min_importance": params.min_importance
        },
        "total_results": len(results),
        "results": results
    }, indent=2)


@mcp.tool(
    name="get_memory",
    annotations={
        "title": "Get Memory by ID",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True
    }
)
async def get_memory(params: GetMemoryInput) -> str:
    """Retrieve a specific memory by its unique ID.

    Args:
        params: GetMemoryInput with memory_id

    Returns:
        JSON response with memory details or error if not found
    """
    for mem in memories:
        if mem["id"] == params.memory_id:
            # Update access count
            mem["access_count"] = mem.get("access_count", 0) + 1
            save_memories()

            return json.dumps({
                "success": True,
                "memory": mem
            }, indent=2)

    return json.dumps({
        "success": False,
        "error": f"Memory '{params.memory_id}' not found",
        "message": "Use search_memories to find available memories"
    }, indent=2)


@mcp.tool(
    name="update_memory",
    annotations={
        "title": "Update Memory",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": True
    }
)
async def update_memory(params: UpdateMemoryInput) -> str:
    """Update an existing memory's content or metadata.

    Only provided fields will be updated; others remain unchanged.

    Args:
        params: UpdateMemoryInput with memory_id and fields to update

    Returns:
        JSON response with success status and updated fields
    """
    for mem in memories:
        if mem["id"] == params.memory_id:
            updated_fields = []

            if params.content is not None:
                mem["content"] = params.content
                updated_fields.append("content")

            if params.category is not None:
                mem["category"] = params.category
                updated_fields.append("category")

            if params.tags is not None:
                mem["tags"] = [t.lower() for t in params.tags]
                updated_fields.append("tags")

            if params.importance is not None:
                mem["importance"] = params.importance
                updated_fields.append("importance")

            mem["updated_at"] = datetime.utcnow().isoformat()
            save_memories()

            return json.dumps({
                "success": True,
                "memory_id": params.memory_id,
                "updated_fields": updated_fields,
                "updated_at": mem["updated_at"]
            }, indent=2)

    return json.dumps({
        "success": False,
        "error": f"Memory '{params.memory_id}' not found"
    }, indent=2)


@mcp.tool(
    name="delete_memory",
    annotations={
        "title": "Delete Memory",
        "readOnlyHint": False,
        "destructiveHint": True,
        "idempotentHint": True
    }
)
async def delete_memory(params: DeleteMemoryInput) -> str:
    """Permanently delete a memory.

    WARNING: This action cannot be undone.

    Args:
        params: DeleteMemoryInput with memory_id

    Returns:
        JSON response with success status
    """
    global memories

    for i, mem in enumerate(memories):
        if mem["id"] == params.memory_id:
            deleted = memories.pop(i)
            save_memories()

            return json.dumps({
                "success": True,
                "message": f"Memory '{params.memory_id}' deleted",
                "deleted_content_preview": deleted["content"][:100] + "..." if len(deleted["content"]) > 100 else deleted["content"]
            }, indent=2)

    return json.dumps({
        "success": False,
        "error": f"Memory '{params.memory_id}' not found"
    }, indent=2)


@mcp.tool(
    name="list_memories",
    annotations={
        "title": "List All Memories",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True
    }
)
async def list_memories(
    category: Optional[str] = None,
    limit: int = 20,
    offset: int = 0
) -> str:
    """List all stored memories with optional filtering.

    Args:
        category: Filter by category (optional)
        limit: Maximum number of memories to return (default: 20)
        offset: Number of memories to skip for pagination (default: 0)

    Returns:
        JSON response with paginated memory list
    """
    filtered = memories if not category else [
        m for m in memories if m["category"] == category
    ]

    # Sort by importance (descending), then by created_at (newest first)
    filtered.sort(key=lambda x: (x["importance"], x["created_at"]), reverse=True)

    total = len(filtered)
    paginated = filtered[offset:offset + limit]
    has_more = (offset + len(paginated)) < total

    return json.dumps({
        "total": total,
        "returned": len(paginated),
        "offset": offset,
        "has_more": has_more,
        "memories": [
            {
                "id": m["id"],
                "content_preview": m["content"][:200] + "..." if len(m["content"]) > 200 else m["content"],
                "category": m["category"],
                "tags": m["tags"],
                "importance": m["importance"],
                "created_at": m["created_at"]
            }
            for m in paginated
        ]
    }, indent=2)


@mcp.tool(
    name="clear_memories",
    annotations={
        "title": "Clear All Memories",
        "readOnlyHint": False,
        "destructiveHint": True,
        "idempotentHint": True
    }
)
async def clear_memories(confirm: bool = False) -> str:
    """Clear all stored memories.

    WARNING: This permanently deletes ALL memories and cannot be undone.

    Args:
        confirm: Must be True to actually clear memories

    Returns:
        JSON response with result
    """
    global memories, memory_counter

    if not confirm:
        return json.dumps({
            "success": False,
            "message": "Set confirm=True to clear all memories. This action cannot be undone.",
            "current_count": len(memories)
        }, indent=2)

    count = len(memories)
    memories = []
    memory_counter = 0
    save_memories()

    return json.dumps({
        "success": True,
        "message": f"Cleared {count} memories",
        "cleared_count": count
    }, indent=2)


# ============================================================================
# MCP Resources
# ============================================================================

@mcp.resource("memory://stats")
async def get_memory_stats() -> str:
    """Get memory system statistics and usage patterns."""
    if not memories:
        return json.dumps({
            "total_memories": 0,
            "message": "No memories stored yet"
        }, indent=2)

    categories = {}
    tags_count = {}
    total_importance = 0
    total_access = 0

    for mem in memories:
        cat = mem.get("category", "general")
        categories[cat] = categories.get(cat, 0) + 1

        for tag in mem.get("tags", []):
            tags_count[tag] = tags_count.get(tag, 0) + 1

        total_importance += mem.get("importance", 5)
        total_access += mem.get("access_count", 0)

    # Get most accessed memories
    most_accessed = sorted(memories, key=lambda x: x.get("access_count", 0), reverse=True)[:5]

    return json.dumps({
        "total_memories": len(memories),
        "categories": categories,
        "top_tags": dict(sorted(tags_count.items(), key=lambda x: x[1], reverse=True)[:10]),
        "avg_importance": round(total_importance / len(memories), 2),
        "total_accesses": total_access,
        "most_accessed": [
            {"id": m["id"], "content_preview": m["content"][:50], "access_count": m.get("access_count", 0)}
            for m in most_accessed
        ],
        "backend": MEMORY_BACKEND,
        "storage_path": MEMORY_PATH if MEMORY_BACKEND == "json" else "N/A"
    }, indent=2)


@mcp.resource("memory://recent")
async def get_recent_memories() -> str:
    """Get the 10 most recently created memories."""
    recent = sorted(memories, key=lambda x: x["created_at"], reverse=True)[:10]

    return json.dumps({
        "recent_memories": recent,
        "count": len(recent)
    }, indent=2)


@mcp.resource("memory://important")
async def get_important_memories() -> str:
    """Get memories with importance >= 8."""
    important = [m for m in memories if m.get("importance", 5) >= 8]
    important.sort(key=lambda x: x["importance"], reverse=True)

    return json.dumps({
        "important_memories": important,
        "count": len(important)
    }, indent=2)


# ============================================================================
# MCP Prompts
# ============================================================================

@mcp.prompt("summarize_context")
async def summarize_context() -> str:
    """Generate a prompt for summarizing the user's context."""
    stats = json.loads(await get_memory_stats())

    return f"""You have access to {stats.get('total_memories', 0)} stored memories.

Categories: {', '.join(stats.get('categories', {}).keys()) or 'None'}
Average importance: {stats.get('avg_importance', 'N/A')}
Top tags: {', '.join(list(stats.get('top_tags', {}).keys())[:5]) or 'None'}

Please provide a brief summary of the user's context based on their stored memories.
Focus on:
1. High-importance items (importance >= 7)
2. Frequently accessed memories
3. Recent additions

Use the search_memories and get_memory tools to retrieve specific content as needed."""


@mcp.prompt("memory_hygiene")
async def memory_hygiene() -> str:
    """Generate a prompt for memory maintenance and cleanup."""
    return """Review the stored memories and suggest cleanup actions:

1. Identify duplicate or near-duplicate memories
2. Find outdated information that should be updated or deleted
3. Suggest tag consolidation for better organization
4. Highlight low-importance memories that might be candidates for removal

Use list_memories and search_memories to analyze the current state."""


# ============================================================================
# Entry Point
# ============================================================================

if __name__ == "__main__":
    print(f"Starting Memory MCP Server (backend: {MEMORY_BACKEND})", file=sys.stderr)
    mcp.run()
