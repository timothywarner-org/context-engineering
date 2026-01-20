"""
ChromaDB Memory Store
=====================
Local vector database for semantic search capabilities.

Features:
- True semantic search using embeddings
- Automatic embedding generation
- Persistent local storage
- Metadata filtering

Requirements:
    pip install chromadb

Limitations:
- Single-node only
- Local storage only
- Performance degrades >100K documents

Usage:
    from memory_stores import ChromaMemoryStore

    store = ChromaMemoryStore(persist_directory="./chroma_data")
    memory_id = store.store("Remember this fact", category="facts")
    results = store.semantic_search("related concept")
"""

import json
from datetime import datetime
from typing import Optional, List, Dict, Any
import uuid

try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    chromadb = None
    Settings = None

from .interface import MemoryStore


class ChromaMemoryStore(MemoryStore):
    """ChromaDB-based semantic memory store with automatic embeddings."""

    def __init__(
        self,
        persist_directory: str = "./chroma_data",
        collection_name: str = "memories",
        embedding_function: Any = None
    ):
        """
        Initialize ChromaDB memory store.

        Args:
            persist_directory: Directory for persistent storage
            collection_name: Name of the ChromaDB collection
            embedding_function: Optional custom embedding function
        """
        if not CHROMADB_AVAILABLE:
            raise ImportError(
                "ChromaDB is not installed. Install it with: pip install chromadb"
            )

        # Initialize ChromaDB with persistence
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )

        # Get or create collection
        # ChromaDB uses cosine similarity by default with sentence-transformers
        collection_kwargs = {
            "name": collection_name,
            "metadata": {"hnsw:space": "cosine"}
        }

        if embedding_function:
            collection_kwargs["embedding_function"] = embedding_function

        self.collection = self.client.get_or_create_collection(**collection_kwargs)
        self.persist_directory = persist_directory

    def store(
        self,
        content: str,
        category: str = "general",
        tags: List[str] = None,
        importance: int = 5,
        metadata: Dict[str, Any] = None
    ) -> str:
        """Store a memory with automatic embedding generation."""
        memory_id = f"mem_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:8]}"
        timestamp = datetime.utcnow().isoformat()

        # Prepare metadata (ChromaDB requires flat metadata)
        doc_metadata = {
            "category": category,
            "tags": json.dumps([t.lower() for t in (tags or [])]),
            "importance": max(1, min(10, importance)),
            "created_at": timestamp,
            "updated_at": timestamp,
            "access_count": 0,
        }

        # Add custom metadata (flatten nested objects)
        if metadata:
            for key, value in metadata.items():
                if isinstance(value, (str, int, float, bool)):
                    doc_metadata[f"meta_{key}"] = value
                else:
                    doc_metadata[f"meta_{key}"] = json.dumps(value)

        # Add to collection (ChromaDB generates embeddings automatically)
        self.collection.add(
            documents=[content],
            metadatas=[doc_metadata],
            ids=[memory_id]
        )

        return memory_id

    def search(
        self,
        query: str,
        limit: int = 10,
        category: Optional[str] = None,
        min_importance: int = 0
    ) -> List[Dict[str, Any]]:
        """Search memories using semantic similarity."""
        return self.semantic_search(
            query=query,
            limit=limit,
            category=category,
            min_importance=min_importance
        )

    def semantic_search(
        self,
        query: str,
        limit: int = 10,
        category: Optional[str] = None,
        min_importance: int = 0,
        include_distances: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Semantic search using vector similarity.

        Args:
            query: Search query (embedded for comparison)
            limit: Maximum results
            category: Optional category filter
            min_importance: Minimum importance threshold
            include_distances: Include similarity scores

        Returns:
            List of memories with similarity scores
        """
        # Build where filter
        where = None
        where_conditions = []

        if category:
            where_conditions.append({"category": {"$eq": category}})

        if min_importance > 0:
            where_conditions.append({"importance": {"$gte": min_importance}})

        if len(where_conditions) == 1:
            where = where_conditions[0]
        elif len(where_conditions) > 1:
            where = {"$and": where_conditions}

        # Query with semantic similarity
        include = ["documents", "metadatas"]
        if include_distances:
            include.append("distances")

        results = self.collection.query(
            query_texts=[query],
            n_results=limit,
            where=where,
            include=include
        )

        # Format results
        memories = []
        if results["ids"] and results["ids"][0]:
            for i, doc_id in enumerate(results["ids"][0]):
                metadata = results["metadatas"][0][i]

                memory = {
                    "id": doc_id,
                    "content": results["documents"][0][i],
                    "category": metadata.get("category", "general"),
                    "tags": json.loads(metadata.get("tags", "[]")),
                    "importance": metadata.get("importance", 5),
                    "created_at": metadata.get("created_at"),
                    "updated_at": metadata.get("updated_at"),
                    "access_count": metadata.get("access_count", 0),
                }

                # Add similarity score (convert distance to similarity)
                if include_distances and results.get("distances"):
                    distance = results["distances"][0][i]
                    # Cosine distance to similarity: 1 - distance (for cosine)
                    memory["_similarity"] = round(1 - distance, 4)
                    memory["_relevance_score"] = memory["_similarity"] * 10

                # Extract custom metadata
                memory["metadata"] = {}
                for key, value in metadata.items():
                    if key.startswith("meta_"):
                        clean_key = key[5:]  # Remove 'meta_' prefix
                        try:
                            memory["metadata"][clean_key] = json.loads(value)
                        except (json.JSONDecodeError, TypeError):
                            memory["metadata"][clean_key] = value

                memories.append(memory)

        return memories

    def get(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """Get a memory by ID."""
        result = self.collection.get(
            ids=[memory_id],
            include=["documents", "metadatas"]
        )

        if result["ids"]:
            metadata = result["metadatas"][0]

            # Update access count
            new_count = metadata.get("access_count", 0) + 1
            self.collection.update(
                ids=[memory_id],
                metadatas=[{**metadata, "access_count": new_count}]
            )

            memory = {
                "id": result["ids"][0],
                "content": result["documents"][0],
                "category": metadata.get("category", "general"),
                "tags": json.loads(metadata.get("tags", "[]")),
                "importance": metadata.get("importance", 5),
                "created_at": metadata.get("created_at"),
                "updated_at": metadata.get("updated_at"),
                "access_count": new_count,
            }

            # Extract custom metadata
            memory["metadata"] = {}
            for key, value in metadata.items():
                if key.startswith("meta_"):
                    clean_key = key[5:]
                    try:
                        memory["metadata"][clean_key] = json.loads(value)
                    except (json.JSONDecodeError, TypeError):
                        memory["metadata"][clean_key] = value

            return memory

        return None

    def delete(self, memory_id: str) -> bool:
        """Delete a memory by ID."""
        try:
            # Check if exists first
            result = self.collection.get(ids=[memory_id])
            if not result["ids"]:
                return False

            self.collection.delete(ids=[memory_id])
            return True
        except Exception:
            return False

    def update(
        self,
        memory_id: str,
        content: Optional[str] = None,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        importance: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Update an existing memory."""
        try:
            # Get existing
            result = self.collection.get(
                ids=[memory_id],
                include=["documents", "metadatas"]
            )

            if not result["ids"]:
                return False

            existing_metadata = result["metadatas"][0]
            existing_content = result["documents"][0]

            # Build update
            new_content = content if content is not None else existing_content
            new_metadata = existing_metadata.copy()

            if category is not None:
                new_metadata["category"] = category
            if tags is not None:
                new_metadata["tags"] = json.dumps([t.lower() for t in tags])
            if importance is not None:
                new_metadata["importance"] = max(1, min(10, importance))
            if metadata is not None:
                for key, value in metadata.items():
                    if isinstance(value, (str, int, float, bool)):
                        new_metadata[f"meta_{key}"] = value
                    else:
                        new_metadata[f"meta_{key}"] = json.dumps(value)

            new_metadata["updated_at"] = datetime.utcnow().isoformat()

            # Update in collection
            self.collection.update(
                ids=[memory_id],
                documents=[new_content] if content is not None else None,
                metadatas=[new_metadata]
            )

            return True
        except Exception:
            return False

    def list_all(
        self,
        category: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """List all memories with pagination."""
        where = {"category": {"$eq": category}} if category else None

        # ChromaDB doesn't support offset, so we fetch more and slice
        result = self.collection.get(
            where=where,
            limit=limit + offset,
            include=["documents", "metadatas"]
        )

        memories = []
        if result["ids"]:
            for i, doc_id in enumerate(result["ids"]):
                if i < offset:
                    continue
                if len(memories) >= limit:
                    break

                metadata = result["metadatas"][i]
                memory = {
                    "id": doc_id,
                    "content": result["documents"][i],
                    "category": metadata.get("category", "general"),
                    "tags": json.loads(metadata.get("tags", "[]")),
                    "importance": metadata.get("importance", 5),
                    "created_at": metadata.get("created_at"),
                    "updated_at": metadata.get("updated_at"),
                    "access_count": metadata.get("access_count", 0),
                }
                memories.append(memory)

        # Sort by importance
        memories.sort(key=lambda x: x["importance"], reverse=True)
        return memories

    def get_stats(self) -> Dict[str, Any]:
        """Get collection statistics."""
        count = self.collection.count()

        if count == 0:
            return {
                "total_memories": 0,
                "categories": {},
                "backend": "ChromaMemoryStore",
                "persist_directory": self.persist_directory,
                "collection_name": self.collection.name
            }

        # Get all for stats (limit to 10K for performance)
        result = self.collection.get(
            limit=10000,
            include=["metadatas"]
        )

        categories = {}
        total_importance = 0
        total_access = 0

        for metadata in result["metadatas"]:
            cat = metadata.get("category", "general")
            categories[cat] = categories.get(cat, 0) + 1
            total_importance += metadata.get("importance", 5)
            total_access += metadata.get("access_count", 0)

        return {
            "total_memories": count,
            "categories": categories,
            "avg_importance": round(total_importance / count, 2) if count else 0,
            "total_accesses": total_access,
            "backend": "ChromaMemoryStore",
            "persist_directory": self.persist_directory,
            "collection_name": self.collection.name
        }

    def clear(self) -> int:
        """Clear all memories from collection."""
        count = self.collection.count()

        # Delete collection and recreate
        self.client.delete_collection(self.collection.name)
        self.collection = self.client.create_collection(
            name=self.collection.name,
            metadata={"hnsw:space": "cosine"}
        )

        return count

    def get_similar(
        self,
        memory_id: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Find memories similar to a given memory.

        Args:
            memory_id: ID of the reference memory
            limit: Number of similar memories to return

        Returns:
            List of similar memories (excluding the reference)
        """
        # Get the reference memory
        result = self.collection.get(
            ids=[memory_id],
            include=["documents"]
        )

        if not result["ids"]:
            return []

        # Search for similar (add 1 to limit to account for self)
        similar = self.semantic_search(
            query=result["documents"][0],
            limit=limit + 1
        )

        # Remove self from results
        return [m for m in similar if m["id"] != memory_id][:limit]
