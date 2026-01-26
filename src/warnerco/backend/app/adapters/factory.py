"""Factory for creating memory store instances."""

import threading
from typing import Optional

from app.adapters.base import MemoryStore
from app.config import MemoryBackend, settings


# Singleton instance with thread-safe initialization
_memory_store: Optional[MemoryStore] = None
_memory_store_lock = threading.Lock()


def get_memory_store() -> MemoryStore:
    """Get or create the configured memory store instance.

    Thread-safe singleton pattern using double-checked locking.

    Returns:
        MemoryStore: The configured memory store implementation.
    """
    global _memory_store

    if _memory_store is not None:
        return _memory_store

    with _memory_store_lock:
        # Double-check after acquiring lock
        if _memory_store is not None:
            return _memory_store

        if settings.memory_backend == MemoryBackend.JSON:
            from app.adapters.json_store import RawJsonStore
            _memory_store = RawJsonStore()

        elif settings.memory_backend == MemoryBackend.CHROMA:
            from app.adapters.chroma_store import ChromaMemoryStore
            _memory_store = ChromaMemoryStore()

        elif settings.memory_backend == MemoryBackend.AZURE_SEARCH:
            from app.adapters.azure_search_store import AzureAiSearchMemoryStore
            _memory_store = AzureAiSearchMemoryStore()

        else:
            raise ValueError(f"Unknown memory backend: {settings.memory_backend}")

        return _memory_store


def reset_memory_store() -> None:
    """Reset the memory store singleton (useful for testing)."""
    global _memory_store
    _memory_store = None
