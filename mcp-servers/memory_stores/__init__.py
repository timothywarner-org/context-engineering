"""
Memory Stores Package
=====================
Pluggable storage backends for AI memory management.

Available Backends:
- JSONMemoryStore: Simple file-based storage for development
- SQLiteMemoryStore: Structured storage with full-text search
- ChromaMemoryStore: Local vector database for semantic search
- PineconeMemoryStore: Cloud-scale vector database

Usage:
    from memory_stores import create_memory_store, MemoryBackend

    # Create a store
    store = create_memory_store(MemoryBackend.CHROMA)

    # Store a memory
    memory_id = store.store("Important fact to remember", category="facts")

    # Search memories
    results = store.search("important", limit=5)
"""

from .interface import MemoryStore, MemoryBackend, create_memory_store
from .json_store import JSONMemoryStore
from .sqlite_store import SQLiteMemoryStore

# Optional imports - may not be available
try:
    from .chroma_store import ChromaMemoryStore
except ImportError:
    ChromaMemoryStore = None

try:
    from .pinecone_store import PineconeMemoryStore
except ImportError:
    PineconeMemoryStore = None

__all__ = [
    "MemoryStore",
    "MemoryBackend",
    "create_memory_store",
    "JSONMemoryStore",
    "SQLiteMemoryStore",
    "ChromaMemoryStore",
    "PineconeMemoryStore",
]
