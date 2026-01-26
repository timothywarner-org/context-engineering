"""Memory backend adapters for WARNERCO Robotics Schematica."""

from app.adapters.base import MemoryStore
from app.adapters.json_store import RawJsonStore
from app.adapters.chroma_store import ChromaMemoryStore
from app.adapters.azure_search_store import AzureAiSearchMemoryStore
from app.adapters.factory import get_memory_store
from app.adapters.graph_store import GraphStore, get_graph_store
from app.adapters.scratchpad_store import ScratchpadStore, get_scratchpad_store, reset_scratchpad_store

__all__ = [
    # Memory stores
    "MemoryStore",
    "RawJsonStore",
    "ChromaMemoryStore",
    "AzureAiSearchMemoryStore",
    "get_memory_store",
    # Knowledge Graph
    "GraphStore",
    "get_graph_store",
    # Scratchpad Memory
    "ScratchpadStore",
    "get_scratchpad_store",
    "reset_scratchpad_store",
]
