"""FastMCP tools for WARNERCO Robotics Schematica."""

from typing import Any, Dict, List, Optional

from fastmcp import FastMCP

from app.adapters import get_memory_store
from app.langgraph import run_query


# Create FastMCP instance
mcp = FastMCP("warnerco-schematica")


@mcp.tool()
async def warn_list_robots(
    category: Optional[str] = None,
    model: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 20,
) -> Dict[str, Any]:
    """List robot schematics with optional filtering.

    Args:
        category: Filter by category (sensors, power, control, etc.)
        model: Filter by robot model (WC-100, WC-200, etc.)
        status: Filter by status (active, deprecated, draft)
        limit: Maximum number of results (default 20)

    Returns:
        Dictionary with list of schematics and metadata
    """
    memory = get_memory_store()

    filters = {}
    if category:
        filters["category"] = category
    if model:
        filters["model"] = model
    if status:
        filters["status"] = status

    schematics = await memory.list_schematics(
        filters=filters if filters else None,
        limit=limit,
    )

    return {
        "count": len(schematics),
        "schematics": [
            {
                "id": s.id,
                "model": s.model,
                "name": s.name,
                "component": s.component,
                "category": s.category,
                "status": s.status.value,
                "version": s.version,
            }
            for s in schematics
        ],
    }


@mcp.tool()
async def warn_get_robot(schematic_id: str) -> Dict[str, Any]:
    """Get detailed information about a specific robot schematic.

    Args:
        schematic_id: The schematic ID (e.g., WRN-00001)

    Returns:
        Full schematic details or error message
    """
    memory = get_memory_store()
    schematic = await memory.get_schematic(schematic_id)

    if not schematic:
        return {"error": f"Schematic {schematic_id} not found"}

    return {
        "id": schematic.id,
        "model": schematic.model,
        "name": schematic.name,
        "component": schematic.component,
        "version": schematic.version,
        "category": schematic.category,
        "status": schematic.status.value,
        "summary": schematic.summary,
        "url": schematic.url,
        "tags": schematic.tags,
        "specifications": schematic.specifications,
        "last_verified": schematic.last_verified,
    }


@mcp.tool()
async def warn_semantic_search(
    query: str,
    category: Optional[str] = None,
    model: Optional[str] = None,
    top_k: int = 5,
) -> Dict[str, Any]:
    """Search robot schematics using natural language queries.

    This tool uses semantic search to find relevant schematics based on
    your query. It understands technical terms and context.

    Args:
        query: Natural language search query (e.g., "thermal sensors for heavy-duty robots")
        category: Optional filter by category
        model: Optional filter by robot model
        top_k: Number of results to return (default 5)

    Returns:
        Search results with relevance scores and reasoning
    """
    filters = {}
    if category:
        filters["category"] = category
    if model:
        filters["model"] = model

    result = await run_query(
        query=query,
        filters=filters if filters else None,
        top_k=top_k,
    )

    return {
        "query": query,
        "intent": result.get("intent", "search"),
        "results": result.get("results", []),
        "total": result.get("total_matches", 0),
        "reasoning": result.get("reasoning", ""),
        "query_time_ms": result.get("query_time_ms", 0),
    }


@mcp.tool()
async def warn_memory_stats() -> Dict[str, Any]:
    """Get statistics about the schematic memory system.

    Returns information about:
    - Total number of schematics
    - Indexed count for semantic search
    - Breakdown by category and status
    - Current memory backend

    Returns:
        Memory statistics dictionary
    """
    memory = get_memory_store()
    stats = await memory.get_memory_stats()

    return {
        "backend": stats.backend,
        "total_schematics": stats.total_schematics,
        "indexed_count": stats.indexed_count,
        "chunk_count": stats.chunk_count,
        "categories": stats.categories,
        "status_counts": stats.status_counts,
        "last_update": stats.last_update,
    }


@mcp.resource("memory://overview")
async def memory_overview() -> str:
    """Get an overview of the WARNERCO Schematica memory system."""
    memory = get_memory_store()
    stats = await memory.get_memory_stats()

    overview = f"""# WARNERCO Robotics Schematica Memory Overview

## Backend: {stats.backend}

### Statistics
- Total Schematics: {stats.total_schematics}
- Indexed for Search: {stats.indexed_count}
- Embedding Chunks: {stats.chunk_count}

### Categories
"""
    for category, count in sorted(stats.categories.items()):
        overview += f"- {category}: {count}\n"

    overview += "\n### Status Distribution\n"
    for status, count in sorted(stats.status_counts.items()):
        overview += f"- {status}: {count}\n"

    if stats.last_update:
        overview += f"\nLast Updated: {stats.last_update}"

    return overview


@mcp.resource("memory://recent-queries")
async def recent_queries() -> str:
    """Get recent search queries and their results."""
    memory = get_memory_store()
    hits = await memory.get_recent_hits(limit=10)

    if not hits:
        return "No recent queries recorded."

    output = "# Recent Queries\n\n"
    for hit in hits:
        output += f"""## Query: {hit.query}
- Time: {hit.timestamp}
- Backend: {hit.backend}
- Duration: {hit.duration_ms:.1f}ms
- Results: {len(hit.robot_ids)} matches
- IDs: {', '.join(hit.robot_ids[:5])}{'...' if len(hit.robot_ids) > 5 else ''}

"""

    return output
