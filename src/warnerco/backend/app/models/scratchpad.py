"""Scratchpad Memory models for WARNERCO Robotics Schematica.

This module defines Pydantic models for the session-scoped Scratchpad Memory
layer that complements vector (Chroma) and graph (SQLite + NetworkX) memory.

Key Concepts:
- Scratchpad: In-memory working memory for observations and inferences
- Triplets: Subject-predicate-object entries with content
- Minimization: LLM-powered compression on write
- Enrichment: LLM-powered expansion on read

Example:
    # Store an observation about a schematic
    ScratchpadEntry(
        subject="WRN-00006",
        predicate="observed",
        object_="thermal_system",
        content="thermal issues with hydraulics",
        original_tokens=12,
        minimized_tokens=8
    )
"""

from datetime import datetime, timezone
from typing import Optional, Dict, List

from pydantic import BaseModel, Field


# =============================================================================
# PREDICATE VOCABULARY
# =============================================================================
# Cognitive operations that describe the type of scratchpad entry.
# Using a consistent vocabulary enables meaningful filtering and analysis.

SCRATCHPAD_PREDICATES = {
    "observed": "observed",           # Direct observation from user/system
    "inferred": "inferred",           # Conclusion drawn from observations
    "relevant_to": "relevant_to",     # Connection to another entity
    "summarized_as": "summarized_as", # Condensed representation
    "contradicts": "contradicts",     # Conflicting information
    "supersedes": "supersedes",       # Replaces prior information
    "depends_on": "depends_on",       # Dependency relationship
}

# Valid predicate values for validation
VALID_SCRATCHPAD_PREDICATES = set(SCRATCHPAD_PREDICATES.values())


# =============================================================================
# DATA MODELS
# =============================================================================


class ScratchpadEntry(BaseModel):
    """A single entry in the scratchpad memory.

    Represents a triplet (subject-predicate-object) with associated content,
    token tracking, and temporal metadata.

    Attributes:
        id: Unique identifier for the entry
        subject: The entity being described (e.g., "WRN-00006", "query:thermal")
        predicate: Type of cognitive operation (observed, inferred, etc.)
        object_: Related entity or concept (e.g., "thermal_system", "issue")
        content: The actual text content (minimized if applicable)
        original_content: Original content before minimization (if minimized)
        original_tokens: Token count of original content
        minimized_tokens: Token count after minimization
        enriched_content: Expanded content (populated on read with enrich=True)
        created_at: ISO timestamp of entry creation
        expires_at: ISO timestamp when entry should be evicted
        metadata: Optional additional properties
    """

    id: str = Field(description="Unique entry identifier")
    subject: str = Field(description="Subject entity being described")
    predicate: str = Field(description="Cognitive operation type")
    object_: str = Field(description="Related entity or concept")
    content: str = Field(description="Entry content (minimized if applicable)")
    original_content: Optional[str] = Field(
        default=None, description="Original content before minimization"
    )
    original_tokens: int = Field(default=0, description="Token count of original content")
    minimized_tokens: int = Field(default=0, description="Token count after minimization")
    enriched_content: Optional[str] = Field(
        default=None, description="Expanded content from enrichment"
    )
    created_at: str = Field(description="ISO timestamp of creation")
    expires_at: str = Field(description="ISO timestamp of expiration")
    metadata: Optional[Dict] = Field(default=None, description="Additional properties")

    class Config:
        # Allow 'object' as an alias for 'object_' in JSON serialization
        populate_by_name = True


class ScratchpadStats(BaseModel):
    """Statistics about the scratchpad memory.

    Provides token usage, entry counts, and savings metrics.
    """

    entry_count: int = Field(description="Total number of entries")
    total_original_tokens: int = Field(description="Sum of original token counts")
    total_minimized_tokens: int = Field(description="Sum of minimized token counts")
    tokens_saved: int = Field(description="Tokens saved through minimization")
    savings_percentage: float = Field(description="Percentage of tokens saved")
    token_budget: int = Field(description="Maximum allowed tokens")
    token_budget_used: int = Field(description="Current tokens used")
    token_budget_remaining: int = Field(description="Remaining token budget")
    predicate_counts: Dict[str, int] = Field(
        default_factory=dict, description="Count by predicate type"
    )
    oldest_entry: Optional[str] = Field(
        default=None, description="ISO timestamp of oldest entry"
    )
    newest_entry: Optional[str] = Field(
        default=None, description="ISO timestamp of newest entry"
    )


class ScratchpadWriteResult(BaseModel):
    """Result of a scratchpad write operation.

    Includes the created entry and token savings information.
    """

    success: bool = Field(description="Whether the write succeeded")
    entry: Optional[ScratchpadEntry] = Field(
        default=None, description="The created entry"
    )
    tokens_saved: int = Field(default=0, description="Tokens saved by minimization")
    message: str = Field(description="Status message")


class ScratchpadReadResult(BaseModel):
    """Result of a scratchpad read operation.

    Contains matching entries and optional enrichment metadata.
    """

    entries: List[ScratchpadEntry] = Field(
        default_factory=list, description="Matching entries"
    )
    total: int = Field(description="Total entries matching filters")
    enriched_count: int = Field(
        default=0, description="Number of entries that were enriched"
    )


class ScratchpadClearResult(BaseModel):
    """Result of a scratchpad clear operation."""

    cleared_count: int = Field(description="Number of entries cleared")
    message: str = Field(description="Status message")
