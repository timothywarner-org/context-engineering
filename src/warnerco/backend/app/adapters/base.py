"""Abstract base class for memory backend adapters."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from app.models import MemoryStats, RetrievalHit, Schematic, SearchResult


class MemoryStore(ABC):
    """Abstract interface for memory backend implementations."""

    @abstractmethod
    async def list_schematics(
        self,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Schematic]:
        """List all schematics with optional filtering."""
        pass

    @abstractmethod
    async def get_schematic(self, schematic_id: str) -> Optional[Schematic]:
        """Get a single schematic by ID."""
        pass

    @abstractmethod
    async def upsert_schematic(self, schematic: Schematic) -> Schematic:
        """Create or update a schematic."""
        pass

    @abstractmethod
    async def delete_schematic(self, schematic_id: str) -> bool:
        """Delete a schematic by ID. Returns True if deleted."""
        pass

    @abstractmethod
    async def embed_and_index(self, schematic_id: str) -> bool:
        """Embed and index a schematic for semantic search. Returns True if successful."""
        pass

    @abstractmethod
    async def semantic_search(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        top_k: int = 5,
    ) -> List[SearchResult]:
        """Perform semantic search on indexed schematics."""
        pass

    @abstractmethod
    async def get_memory_stats(self) -> MemoryStats:
        """Get statistics about the memory backend."""
        pass

    @abstractmethod
    async def get_recent_hits(self, limit: int = 20) -> List[RetrievalHit]:
        """Get recent retrieval telemetry."""
        pass

    @property
    @abstractmethod
    def backend_name(self) -> str:
        """Get the name of this backend implementation."""
        pass
