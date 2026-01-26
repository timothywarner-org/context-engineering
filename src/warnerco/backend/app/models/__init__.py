"""Pydantic models for WARNERCO Robotics Schematica."""

from app.models.schematic import (
    Schematic,
    SchematicCreate,
    SchematicUpdate,
    SchematicSpecifications,
    SchematicStatus,
    SearchQuery,
    SearchResult,
    MemoryStats,
    RetrievalHit,
)

from app.models.graph import (
    Entity,
    Relationship,
    GraphQueryResult,
    GraphStats,
    PREDICATES,
    VALID_PREDICATES,
    ENTITY_TYPES,
)

from app.models.scratchpad import (
    ScratchpadEntry,
    ScratchpadStats,
    ScratchpadWriteResult,
    ScratchpadReadResult,
    ScratchpadClearResult,
    SCRATCHPAD_PREDICATES,
    VALID_SCRATCHPAD_PREDICATES,
)

__all__ = [
    # Schematic models
    "Schematic",
    "SchematicCreate",
    "SchematicUpdate",
    "SchematicSpecifications",
    "SchematicStatus",
    "SearchQuery",
    "SearchResult",
    "MemoryStats",
    "RetrievalHit",
    # Graph models
    "Entity",
    "Relationship",
    "GraphQueryResult",
    "GraphStats",
    "PREDICATES",
    "VALID_PREDICATES",
    "ENTITY_TYPES",
    # Scratchpad models
    "ScratchpadEntry",
    "ScratchpadStats",
    "ScratchpadWriteResult",
    "ScratchpadReadResult",
    "ScratchpadClearResult",
    "SCRATCHPAD_PREDICATES",
    "VALID_SCRATCHPAD_PREDICATES",
]
