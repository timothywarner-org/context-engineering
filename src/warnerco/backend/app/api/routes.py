"""REST API routes for WARNERCO Robotics Schematica."""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.adapters import get_memory_store
from app.config import settings
from app.langgraph import run_query
from app.models import (
    MemoryStats,
    RetrievalHit,
    Schematic,
    SchematicCreate,
    SearchQuery,
    SearchResult,
)


router = APIRouter()

logger = logging.getLogger(__name__)


# Response models
class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    backend: str
    timestamp: str
    version: str = "1.0.0"


class RobotListResponse(BaseModel):
    """List of robots/schematics."""

    items: List[Schematic]
    total: int
    offset: int
    limit: int


class IndexResponse(BaseModel):
    """Indexing operation response."""

    success: bool
    schematic_id: str
    message: str


class SearchResponse(BaseModel):
    """Search results response."""

    results: List[SearchResult]
    query: str
    total: int
    query_time_ms: float
    reasoning: Optional[str] = None


# Health endpoint
@router.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    """Check system health and backend status."""
    memory = get_memory_store()
    return HealthResponse(
        status="healthy",
        backend=memory.backend_name,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )


# Robot/Schematic CRUD endpoints
@router.get("/robots", response_model=RobotListResponse, tags=["Robots"])
async def list_robots(
    category: Optional[str] = Query(None, description="Filter by category"),
    model: Optional[str] = Query(None, description="Filter by robot model"),
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(100, ge=1, le=500, description="Max results"),
    offset: int = Query(0, ge=0, description="Skip results"),
):
    """List all robot schematics with optional filtering."""
    memory = get_memory_store()

    filters = {}
    if category:
        filters["category"] = category
    if model:
        filters["model"] = model
    if status:
        filters["status"] = status

    items = await memory.list_schematics(
        filters=filters if filters else None,
        limit=limit,
        offset=offset,
    )

    # Get total count
    all_items = await memory.list_schematics(filters=filters if filters else None, limit=1000)

    return RobotListResponse(
        items=items,
        total=len(all_items),
        offset=offset,
        limit=limit,
    )


@router.get("/robots/{robot_id}", response_model=Schematic, tags=["Robots"])
async def get_robot(robot_id: str):
    """Get a specific robot schematic by ID."""
    memory = get_memory_store()
    schematic = await memory.get_schematic(robot_id)

    if not schematic:
        raise HTTPException(status_code=404, detail=f"Schematic {robot_id} not found")

    return schematic


@router.post("/robots/{robot_id}/index", response_model=IndexResponse, tags=["Robots"])
async def index_robot(robot_id: str):
    """Index a robot schematic for semantic search."""
    memory = get_memory_store()

    schematic = await memory.get_schematic(robot_id)
    if not schematic:
        raise HTTPException(status_code=404, detail=f"Schematic {robot_id} not found")

    success = await memory.embed_and_index(robot_id)

    return IndexResponse(
        success=success,
        schematic_id=robot_id,
        message="Indexed successfully" if success else "Indexing failed",
    )


@router.post("/robots/index-all", response_model=Dict[str, Any], tags=["Robots"])
async def index_all_robots():
    """Index all robot schematics for semantic search."""
    memory = get_memory_store()

    # Check if backend supports batch indexing
    if hasattr(memory, "index_all"):
        count = await memory.index_all()
        return {"success": True, "indexed_count": count, "message": f"Indexed {count} schematics"}

    # Fallback: index one by one
    schematics = await memory.list_schematics(limit=1000)
    count = 0
    for schematic in schematics:
        if await memory.embed_and_index(schematic.id):
            count += 1

    return {"success": True, "indexed_count": count, "message": f"Indexed {count} schematics"}


# Search endpoint
@router.post("/search", response_model=SearchResponse, tags=["Search"])
async def semantic_search(query: SearchQuery):
    """Perform semantic search on robot schematics."""
    start_time = datetime.now(timezone.utc)

    # Use LangGraph flow for enhanced search
    result = await run_query(
        query=query.query,
        filters=query.filters,
        top_k=query.top_k,
    )

    # Convert results back to SearchResult format
    memory = get_memory_store()
    search_results = []

    for item in result.get("results", []):
        schematic = await memory.get_schematic(item["id"])
        if schematic:
            search_results.append(
                SearchResult(
                    schematic=schematic,
                    score=item.get("score", 0.0),
                    chunk_id=item.get("id"),
                )
            )

    duration_ms = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000

    return SearchResponse(
        results=search_results,
        query=query.query,
        total=len(search_results),
        query_time_ms=duration_ms,
        reasoning=result.get("reasoning"),
    )


# Memory stats endpoints
@router.get("/memory/stats", response_model=MemoryStats, tags=["Memory"])
async def get_memory_stats():
    """Get statistics about the memory backend."""
    memory = get_memory_store()
    return await memory.get_memory_stats()


@router.get("/memory/hits", response_model=List[RetrievalHit], tags=["Memory"])
async def get_recent_hits(limit: int = Query(20, ge=1, le=100)):
    """Get recent retrieval telemetry."""
    memory = get_memory_store()
    return await memory.get_recent_hits(limit)


# Categories and models for filtering
@router.get("/categories", response_model=List[str], tags=["Metadata"])
async def get_categories():
    """Get list of available categories."""
    memory = get_memory_store()
    stats = await memory.get_memory_stats()
    return sorted(stats.categories.keys())


@router.get("/models", response_model=List[str], tags=["Metadata"])
async def get_models():
    """Get list of available robot models."""
    memory = get_memory_store()
    schematics = await memory.list_schematics(limit=1000)
    models = sorted(set(s.model for s in schematics))
    return models


# =============================================================================
# Knowledge Graph Endpoints
# =============================================================================


class GraphStatsResponse(BaseModel):
    """Knowledge Graph statistics response."""

    entity_count: int
    relationship_count: int
    entity_types: Dict[str, int]
    predicate_counts: Dict[str, int]


class GraphNeighborsResponse(BaseModel):
    """Knowledge Graph neighbors response."""

    entity_id: str
    direction: str
    neighbors: List[str]
    relationships: List[Dict[str, str]]


class GraphPathResponse(BaseModel):
    """Knowledge Graph path response."""

    source: str
    target: str
    path: Optional[List[str]]
    path_length: int


@router.get("/graph/stats", response_model=GraphStatsResponse, tags=["Graph"])
async def graph_stats():
    """Get knowledge graph statistics.

    Returns counts of entities and relationships by type.
    Useful for monitoring graph coverage.
    """
    from app.adapters.graph_store import get_graph_store

    try:
        graph_store = get_graph_store()
        stats = await graph_store.stats()

        return GraphStatsResponse(
            entity_count=stats.entity_count,
            relationship_count=stats.relationship_count,
            entity_types=stats.entity_types,
            predicate_counts=stats.predicate_counts,
        )
    except Exception as e:
        logger.exception("Graph stats operation failed")
        raise HTTPException(status_code=500, detail="Internal server error processing graph request")


@router.get("/graph/neighbors/{entity_id}", response_model=GraphNeighborsResponse, tags=["Graph"])
async def graph_neighbors(
    entity_id: str,
    direction: str = Query("both", description="Direction: outgoing, incoming, or both"),
):
    """Get neighbors of an entity in the knowledge graph.

    Returns all entities connected to the given entity.

    Args:
        entity_id: The entity to find neighbors for (e.g., WRN-00001, model:WC-100)
        direction: Direction to search (outgoing, incoming, or both)
    """
    from app.adapters.graph_store import get_graph_store

    if direction not in ("outgoing", "incoming", "both"):
        raise HTTPException(
            status_code=400,
            detail="Invalid direction. Must be 'outgoing', 'incoming', or 'both'",
        )

    try:
        graph_store = get_graph_store()

        # Get neighbor IDs
        neighbors = await graph_store.get_neighbors(entity_id, direction)

        # Get relationship details
        relationships = []

        if direction in ("outgoing", "both"):
            outgoing = await graph_store.get_related(entity_id)
            for rel in outgoing:
                relationships.append({
                    "direction": "outgoing",
                    "predicate": rel.predicate,
                    "target": rel.object,
                })

        if direction in ("incoming", "both"):
            incoming = await graph_store.get_subjects(entity_id)
            for rel in incoming:
                relationships.append({
                    "direction": "incoming",
                    "predicate": rel.predicate,
                    "source": rel.subject,
                })

        return GraphNeighborsResponse(
            entity_id=entity_id,
            direction=direction,
            neighbors=neighbors,
            relationships=relationships,
        )

    except Exception as e:
        logger.exception("Graph neighbors operation failed for entity: %s", entity_id)
        raise HTTPException(status_code=500, detail="Internal server error processing graph request")


@router.get("/graph/path", response_model=GraphPathResponse, tags=["Graph"])
async def graph_path(
    source: str = Query(..., description="Source entity ID"),
    target: str = Query(..., description="Target entity ID"),
):
    """Find the shortest path between two entities.

    Uses graph traversal to find how two entities are connected.

    Args:
        source: Starting entity ID
        target: Ending entity ID
    """
    from app.adapters.graph_store import get_graph_store

    try:
        graph_store = get_graph_store()

        path = await graph_store.shortest_path(source, target)

        if path:
            return GraphPathResponse(
                source=source,
                target=target,
                path=path,
                path_length=len(path) - 1,
            )
        else:
            return GraphPathResponse(
                source=source,
                target=target,
                path=None,
                path_length=-1,
            )

    except Exception as e:
        logger.exception("Graph path operation failed from %s to %s", source, target)
        raise HTTPException(status_code=500, detail="Internal server error processing graph request")
