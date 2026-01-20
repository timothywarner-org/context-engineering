"""
Memory Store Interface
======================
Abstract interface and factory for memory storage backends.

This module defines the contract that all memory stores must implement,
enabling easy swapping between backends without code changes.
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from enum import Enum
from dataclasses import dataclass
from datetime import datetime


class MemoryBackend(str, Enum):
    """Available memory storage backends."""
    JSON = "json"
    SQLITE = "sqlite"
    CHROMA = "chroma"
    PINECONE = "pinecone"


@dataclass
class Memory:
    """Standard memory data structure."""
    id: str
    content: str
    category: str = "general"
    tags: List[str] = None
    importance: int = 5
    metadata: Dict[str, Any] = None
    created_at: str = None
    updated_at: str = None
    access_count: int = 0

    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.metadata is None:
            self.metadata = {}
        if self.created_at is None:
            self.created_at = datetime.utcnow().isoformat()
        if self.updated_at is None:
            self.updated_at = self.created_at

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "id": self.id,
            "content": self.content,
            "category": self.category,
            "tags": self.tags,
            "importance": self.importance,
            "metadata": self.metadata,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "access_count": self.access_count,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Memory":
        """Create Memory from dictionary."""
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


class MemoryStore(ABC):
    """
    Abstract interface for memory stores.

    All memory storage backends must implement these methods to ensure
    consistent behavior and easy backend swapping.
    """

    @abstractmethod
    def store(
        self,
        content: str,
        category: str = "general",
        tags: List[str] = None,
        importance: int = 5,
        metadata: Dict[str, Any] = None
    ) -> str:
        """
        Store a memory and return its unique ID.

        Args:
            content: The content to remember
            category: Category for organization (default: "general")
            tags: List of tags for filtering
            importance: Importance score 1-10 (default: 5)
            metadata: Additional metadata dict

        Returns:
            Unique memory ID string
        """
        pass

    @abstractmethod
    def search(
        self,
        query: str,
        limit: int = 10,
        category: Optional[str] = None,
        min_importance: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Search for memories matching the query.

        Args:
            query: Search query string
            limit: Maximum results to return
            category: Optional category filter
            min_importance: Minimum importance threshold

        Returns:
            List of matching memories with relevance scores
        """
        pass

    @abstractmethod
    def get(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific memory by its ID.

        Args:
            memory_id: Unique identifier of the memory

        Returns:
            Memory dict if found, None otherwise
        """
        pass

    @abstractmethod
    def delete(self, memory_id: str) -> bool:
        """
        Delete a memory by its ID.

        Args:
            memory_id: Unique identifier to delete

        Returns:
            True if deleted, False if not found
        """
        pass

    def update(
        self,
        memory_id: str,
        content: Optional[str] = None,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        importance: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Update an existing memory.

        Default implementation: get, modify, delete, re-store.
        Backends should override for atomic updates.

        Args:
            memory_id: ID of memory to update
            content: New content (if provided)
            category: New category (if provided)
            tags: New tags (if provided)
            importance: New importance (if provided)
            metadata: New metadata (if provided)

        Returns:
            True if updated, False if not found
        """
        existing = self.get(memory_id)
        if not existing:
            return False

        if content is not None:
            existing["content"] = content
        if category is not None:
            existing["category"] = category
        if tags is not None:
            existing["tags"] = tags
        if importance is not None:
            existing["importance"] = importance
        if metadata is not None:
            existing["metadata"] = metadata

        existing["updated_at"] = datetime.utcnow().isoformat()

        self.delete(memory_id)
        self.store(**{k: v for k, v in existing.items() if k != "id"})
        return True

    def list_all(
        self,
        category: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        List all memories with optional filtering.

        Default implementation: search with empty query.
        Backends should override for efficiency.

        Args:
            category: Optional category filter
            limit: Maximum results
            offset: Results to skip

        Returns:
            List of memories
        """
        return self.search("", limit=limit, category=category)

    def get_stats(self) -> Dict[str, Any]:
        """
        Get storage statistics.

        Default implementation: basic counts.
        Backends should override for detailed stats.

        Returns:
            Dict with statistics
        """
        all_memories = self.list_all(limit=10000)
        categories = {}
        for m in all_memories:
            cat = m.get("category", "general")
            categories[cat] = categories.get(cat, 0) + 1

        return {
            "total_memories": len(all_memories),
            "categories": categories,
            "backend": self.__class__.__name__,
        }

    def clear(self) -> int:
        """
        Clear all memories.

        Default implementation: delete each memory.
        Backends should override for efficiency.

        Returns:
            Number of memories deleted
        """
        all_memories = self.list_all(limit=100000)
        count = 0
        for m in all_memories:
            if self.delete(m["id"]):
                count += 1
        return count


def create_memory_store(backend: MemoryBackend, **kwargs) -> MemoryStore:
    """
    Factory function to create memory stores.

    Args:
        backend: Which backend to use
        **kwargs: Backend-specific configuration

    Returns:
        Configured MemoryStore instance

    Raises:
        ValueError: If backend is unknown
        ImportError: If backend dependencies are not installed
    """
    if backend == MemoryBackend.JSON:
        from .json_store import JSONMemoryStore
        return JSONMemoryStore(**kwargs)

    elif backend == MemoryBackend.SQLITE:
        from .sqlite_store import SQLiteMemoryStore
        return SQLiteMemoryStore(**kwargs)

    elif backend == MemoryBackend.CHROMA:
        try:
            from .chroma_store import ChromaMemoryStore
            return ChromaMemoryStore(**kwargs)
        except ImportError as e:
            raise ImportError(
                "ChromaDB not installed. Run: pip install chromadb"
            ) from e

    elif backend == MemoryBackend.PINECONE:
        try:
            from .pinecone_store import PineconeMemoryStore
            return PineconeMemoryStore(**kwargs)
        except ImportError as e:
            raise ImportError(
                "Pinecone not installed. Run: pip install pinecone-client"
            ) from e

    else:
        raise ValueError(f"Unknown backend: {backend}")
