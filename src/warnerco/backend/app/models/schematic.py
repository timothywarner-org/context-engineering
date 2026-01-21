"""Schematic data models for WARNERCO Robotics Schematica."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class SchematicStatus(str, Enum):
    """Status of a schematic document."""

    ACTIVE = "active"
    DEPRECATED = "deprecated"
    DRAFT = "draft"


class SchematicSpecifications(BaseModel):
    """Technical specifications for a schematic component."""

    model_config = {"extra": "allow"}

    # Common specification fields (all optional, allows any additional fields)
    resolution: Optional[str] = None
    range: Optional[str] = None
    capacity: Optional[str] = None
    accuracy: Optional[str] = None
    response_time: Optional[str] = None


class SchematicBase(BaseModel):
    """Base schematic model with common fields."""

    model: str = Field(..., description="Robot model identifier (e.g., WC-100)")
    name: str = Field(..., description="Robot name (e.g., Atlas Prime)")
    component: str = Field(..., description="Component name")
    version: str = Field(..., description="Component version")
    summary: str = Field(..., description="Technical summary of the component")
    url: str = Field(..., description="URL to schematic document")
    category: str = Field(..., description="Component category")
    status: SchematicStatus = Field(default=SchematicStatus.ACTIVE)
    tags: List[str] = Field(default_factory=list, description="Searchable tags")
    specifications: Optional[Dict[str, Any]] = Field(
        default=None, description="Technical specifications"
    )


class Schematic(SchematicBase):
    """Complete schematic model with ID and timestamps."""

    id: str = Field(..., description="Unique schematic identifier (e.g., WRN-00001)")
    last_verified: str = Field(..., description="ISO date of last verification")

    def to_embed_text(self) -> str:
        """Generate text representation for embedding."""
        parts = [
            f"Model: {self.model} ({self.name})",
            f"Component: {self.component}",
            f"Version: {self.version}",
            f"Category: {self.category}",
            f"Summary: {self.summary}",
        ]
        if self.tags:
            parts.append(f"Tags: {', '.join(self.tags)}")
        if self.specifications:
            specs = ", ".join(f"{k}: {v}" for k, v in self.specifications.items())
            parts.append(f"Specifications: {specs}")
        return "\n".join(parts)


class SchematicCreate(SchematicBase):
    """Model for creating a new schematic."""

    id: Optional[str] = Field(None, description="Optional ID (auto-generated if not provided)")
    last_verified: Optional[str] = Field(None, description="ISO date (defaults to today)")


class SchematicUpdate(BaseModel):
    """Model for updating an existing schematic."""

    model: Optional[str] = None
    name: Optional[str] = None
    component: Optional[str] = None
    version: Optional[str] = None
    summary: Optional[str] = None
    url: Optional[str] = None
    category: Optional[str] = None
    status: Optional[SchematicStatus] = None
    tags: Optional[List[str]] = None
    specifications: Optional[Dict[str, Any]] = None
    last_verified: Optional[str] = None


class SearchQuery(BaseModel):
    """Query model for semantic search."""

    query: str = Field(..., description="Natural language search query")
    filters: Optional[Dict[str, Any]] = Field(
        default=None, description="Optional filters (category, model, status, etc.)"
    )
    top_k: int = Field(default=5, ge=1, le=50, description="Number of results to return")


class SearchResult(BaseModel):
    """Individual search result with relevance score."""

    schematic: Schematic
    score: float = Field(..., description="Relevance score (0-1)")
    chunk_id: Optional[str] = Field(None, description="ID of matched chunk if applicable")


class MemoryStats(BaseModel):
    """Statistics about the memory backend."""

    backend: str = Field(..., description="Active memory backend name")
    total_schematics: int = Field(..., description="Total number of schematics")
    indexed_count: int = Field(..., description="Number of indexed schematics")
    chunk_count: int = Field(default=0, description="Total embedding chunks")
    categories: Dict[str, int] = Field(default_factory=dict, description="Count by category")
    status_counts: Dict[str, int] = Field(default_factory=dict, description="Count by status")
    last_update: Optional[str] = Field(None, description="ISO timestamp of last update")


class RetrievalHit(BaseModel):
    """Telemetry record for a retrieval operation."""

    id: str = Field(..., description="Unique hit ID")
    timestamp: str = Field(..., description="ISO timestamp")
    query: str = Field(..., description="Original query")
    robot_ids: List[str] = Field(default_factory=list, description="Matched robot IDs")
    chunk_ids: List[str] = Field(default_factory=list, description="Matched chunk IDs")
    scores: List[float] = Field(default_factory=list, description="Relevance scores")
    duration_ms: float = Field(..., description="Query duration in milliseconds")
    backend: str = Field(..., description="Memory backend used")
