"""Knowledge Graph models for WARNERCO Robotics Schematica.

This module defines Pydantic models for the Knowledge Graph layer that
complements the RAG system. Knowledge Graphs excel at representing
relationships between entities - something that vector search alone
cannot capture well.

Key Concepts:
- Entity: A node in the graph (schematic, component, status, etc.)
- Relationship: A directed edge (triplet) connecting two entities
- Predicates: The vocabulary of relationship types

Example:
    # A schematic depends on a component
    Relationship(
        subject="WRN-00006",
        predicate="contains",
        object="hydraulic_system"
    )
"""

from typing import Optional

from pydantic import BaseModel, Field


# =============================================================================
# PREDICATE VOCABULARY
# =============================================================================
# Standardized relationship types used in the knowledge graph.
# Using a consistent vocabulary enables meaningful graph traversal.

PREDICATES = {
    "DEPENDS_ON": "depends_on",
    "CONTAINS": "contains",
    "HAS_STATUS": "has_status",
    "MANUFACTURED_BY": "manufactured_by",
    "COMPATIBLE_WITH": "compatible_with",
    "RELATED_TO": "related_to",
    "HAS_CATEGORY": "has_category",
    "BELONGS_TO_MODEL": "belongs_to_model",
    "HAS_TAG": "has_tag",
}

# Valid predicate values for validation
VALID_PREDICATES = set(PREDICATES.values())


# =============================================================================
# ENTITY TYPES
# =============================================================================
# Standard entity types in the knowledge graph.

ENTITY_TYPES = {
    "SCHEMATIC": "schematic",
    "COMPONENT": "component",
    "STATUS": "status",
    "CATEGORY": "category",
    "MODEL": "model",
    "TAG": "tag",
    "MANUFACTURER": "manufacturer",
}


# =============================================================================
# DATA MODELS
# =============================================================================


class Entity(BaseModel):
    """A node in the knowledge graph.

    Entities represent distinct concepts in the robotics domain:
    schematics, components, statuses, categories, etc.

    Attributes:
        id: Unique identifier for the entity (e.g., "WRN-00001", "hydraulic_system")
        entity_type: Type classification (schematic, component, status, etc.)
        name: Human-readable name for display
        metadata: Optional dictionary for additional properties
    """

    id: str = Field(description="Unique entity identifier")
    entity_type: str = Field(description="Entity type (schematic, component, status, etc.)")
    name: str = Field(description="Human-readable name")
    metadata: Optional[dict] = Field(default=None, description="Additional entity properties")


class Relationship(BaseModel):
    """A directed edge (triplet) in the knowledge graph.

    Relationships connect two entities with a predicate, forming
    subject-predicate-object triplets (SPO triples).

    Example:
        WRN-00006 --contains--> hydraulic_system
        WRN-00001 --has_status--> active

    Attributes:
        subject: Source entity ID
        predicate: Relationship type (from PREDICATES vocabulary)
        object: Target entity ID
        metadata: Optional properties for the relationship
    """

    subject: str = Field(description="Source entity ID")
    predicate: str = Field(description="Relationship type (depends_on, contains, etc.)")
    object: str = Field(description="Target entity ID")
    metadata: Optional[dict] = Field(default=None, description="Relationship properties")


class GraphQueryResult(BaseModel):
    """Result from a graph query operation.

    Contains entities and relationships matching the query,
    plus optional path information for traversal queries.

    Attributes:
        entities: List of entities found
        relationships: List of relationships connecting entities
        paths: Optional list of paths (each path is a list of entity IDs)
    """

    entities: list[Entity] = Field(default_factory=list, description="Matched entities")
    relationships: list[Relationship] = Field(default_factory=list, description="Matched relationships")
    paths: Optional[list[list[str]]] = Field(default=None, description="Traversal paths")


class GraphStats(BaseModel):
    """Statistics about the knowledge graph.

    Provides overview metrics for monitoring and debugging.
    """

    entity_count: int = Field(description="Total number of entities")
    relationship_count: int = Field(description="Total number of relationships")
    entity_types: dict[str, int] = Field(
        default_factory=dict, description="Count by entity type"
    )
    predicate_counts: dict[str, int] = Field(
        default_factory=dict, description="Count by predicate type"
    )
