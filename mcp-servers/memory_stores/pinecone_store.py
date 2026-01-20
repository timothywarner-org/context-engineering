"""
Pinecone Memory Store
=====================
Cloud-scale vector database for production semantic search.

Features:
- Managed cloud infrastructure
- Horizontal scaling
- Multi-tenant support via namespaces
- Low-latency queries

Requirements:
    pip install pinecone-client anthropic

Environment Variables:
    PINECONE_API_KEY: Your Pinecone API key
    ANTHROPIC_API_KEY: For embedding generation (optional)

Limitations:
- Requires external API calls
- Cost per operation
- Network latency

Usage:
    import os
    os.environ["PINECONE_API_KEY"] = "your-api-key"

    from memory_stores import PineconeMemoryStore

    store = PineconeMemoryStore(index_name="ai-memories")
    memory_id = store.store("Remember this fact", category="facts")
    results = store.semantic_search("related concept")
"""

import json
import os
from datetime import datetime
from typing import Optional, List, Dict, Any
import uuid

try:
    from pinecone import Pinecone, ServerlessSpec
    PINECONE_AVAILABLE = True
except ImportError:
    PINECONE_AVAILABLE = False
    Pinecone = None
    ServerlessSpec = None

from .interface import MemoryStore


class PineconeMemoryStore(MemoryStore):
    """Pinecone-based semantic memory for production scale."""

    def __init__(
        self,
        index_name: str = "ai-memories",
        api_key: Optional[str] = None,
        environment: str = "us-east-1",
        dimension: int = 1536,
        metric: str = "cosine",
        embedding_provider: str = "openai"
    ):
        """
        Initialize Pinecone memory store.

        Args:
            index_name: Name of the Pinecone index
            api_key: Pinecone API key (or use PINECONE_API_KEY env var)
            environment: Cloud region
            dimension: Embedding dimension (1536 for OpenAI, 1024 for Voyage)
            metric: Distance metric (cosine, euclidean, dotproduct)
            embedding_provider: "openai", "voyage", or "local"
        """
        if not PINECONE_AVAILABLE:
            raise ImportError(
                "Pinecone is not installed. Install it with: pip install pinecone-client"
            )

        self.api_key = api_key or os.environ.get("PINECONE_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Pinecone API key required. Set PINECONE_API_KEY environment variable "
                "or pass api_key parameter."
            )

        # Initialize Pinecone client
        self.pc = Pinecone(api_key=self.api_key)
        self.index_name = index_name
        self.dimension = dimension
        self.embedding_provider = embedding_provider

        # Create index if it doesn't exist
        existing_indexes = [idx.name for idx in self.pc.list_indexes()]
        if index_name not in existing_indexes:
            self.pc.create_index(
                name=index_name,
                dimension=dimension,
                metric=metric,
                spec=ServerlessSpec(
                    cloud="aws",
                    region=environment
                )
            )

        self.index = self.pc.Index(index_name)

        # Initialize embedding function
        self._setup_embeddings()

    def _setup_embeddings(self):
        """Set up embedding generation based on provider."""
        if self.embedding_provider == "openai":
            try:
                from openai import OpenAI
                self.openai_client = OpenAI()
                self._get_embedding = self._openai_embedding
            except ImportError:
                raise ImportError("OpenAI not installed. Run: pip install openai")

        elif self.embedding_provider == "voyage":
            try:
                import voyageai
                self.voyage_client = voyageai.Client()
                self._get_embedding = self._voyage_embedding
            except ImportError:
                raise ImportError("Voyage AI not installed. Run: pip install voyageai")

        elif self.embedding_provider == "local":
            try:
                from sentence_transformers import SentenceTransformer
                self.local_model = SentenceTransformer('all-MiniLM-L6-v2')
                self._get_embedding = self._local_embedding
            except ImportError:
                raise ImportError(
                    "sentence-transformers not installed. "
                    "Run: pip install sentence-transformers"
                )
        else:
            raise ValueError(f"Unknown embedding provider: {self.embedding_provider}")

    def _openai_embedding(self, text: str) -> List[float]:
        """Generate embedding using OpenAI."""
        response = self.openai_client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        return response.data[0].embedding

    def _voyage_embedding(self, text: str) -> List[float]:
        """Generate embedding using Voyage AI."""
        result = self.voyage_client.embed([text], model="voyage-2")
        return result.embeddings[0]

    def _local_embedding(self, text: str) -> List[float]:
        """Generate embedding using local model."""
        return self.local_model.encode(text).tolist()

    def store(
        self,
        content: str,
        category: str = "general",
        tags: List[str] = None,
        importance: int = 5,
        metadata: Dict[str, Any] = None,
        user_id: str = "default"
    ) -> str:
        """Store a memory with embedding in Pinecone."""
        memory_id = f"mem_{user_id}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:8]}"
        timestamp = datetime.utcnow().isoformat()

        # Generate embedding
        embedding = self._get_embedding(content)

        # Prepare metadata (Pinecone has size limits on metadata)
        doc_metadata = {
            "content": content[:1000] if len(content) > 1000 else content,
            "content_full": content if len(content) <= 4000 else content[:4000],
            "category": category,
            "tags": json.dumps([t.lower() for t in (tags or [])])[:500],
            "importance": max(1, min(10, importance)),
            "user_id": user_id,
            "created_at": timestamp,
            "updated_at": timestamp,
            "access_count": 0,
        }

        # Add custom metadata
        if metadata:
            for key, value in metadata.items():
                meta_key = f"meta_{key}"
                if isinstance(value, (str, int, float, bool)):
                    doc_metadata[meta_key] = value
                else:
                    serialized = json.dumps(value)
                    if len(serialized) <= 500:
                        doc_metadata[meta_key] = serialized

        # Upsert to Pinecone with namespace for multi-tenancy
        self.index.upsert(
            vectors=[{
                "id": memory_id,
                "values": embedding,
                "metadata": doc_metadata
            }],
            namespace=user_id
        )

        return memory_id

    def search(
        self,
        query: str,
        limit: int = 10,
        category: Optional[str] = None,
        min_importance: int = 0,
        user_id: str = "default"
    ) -> List[Dict[str, Any]]:
        """Search memories using semantic similarity."""
        return self.semantic_search(
            query=query,
            limit=limit,
            category=category,
            min_importance=min_importance,
            user_id=user_id
        )

    def semantic_search(
        self,
        query: str,
        limit: int = 10,
        category: Optional[str] = None,
        min_importance: int = 0,
        user_id: str = "default",
        include_metadata: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Semantic search using Pinecone.

        Args:
            query: Search query
            limit: Maximum results
            category: Optional category filter
            min_importance: Minimum importance threshold
            user_id: Namespace for multi-tenant isolation
            include_metadata: Include metadata in results

        Returns:
            List of memories with similarity scores
        """
        # Generate query embedding
        query_embedding = self._get_embedding(query)

        # Build filter
        filter_dict = {}
        if category:
            filter_dict["category"] = {"$eq": category}
        if min_importance > 0:
            filter_dict["importance"] = {"$gte": min_importance}

        # Query Pinecone
        results = self.index.query(
            vector=query_embedding,
            top_k=limit,
            namespace=user_id,
            filter=filter_dict if filter_dict else None,
            include_metadata=include_metadata
        )

        # Format results
        memories = []
        for match in results.matches:
            metadata = match.metadata or {}

            memory = {
                "id": match.id,
                "content": metadata.get("content_full", metadata.get("content", "")),
                "category": metadata.get("category", "general"),
                "tags": json.loads(metadata.get("tags", "[]")),
                "importance": metadata.get("importance", 5),
                "user_id": metadata.get("user_id", user_id),
                "created_at": metadata.get("created_at"),
                "updated_at": metadata.get("updated_at"),
                "access_count": metadata.get("access_count", 0),
                "_similarity": round(match.score, 4),
                "_relevance_score": round(match.score * 10, 2),
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

            memories.append(memory)

        return memories

    def get(self, memory_id: str, user_id: str = "default") -> Optional[Dict[str, Any]]:
        """Get a memory by ID."""
        result = self.index.fetch(
            ids=[memory_id],
            namespace=user_id
        )

        if memory_id in result.vectors:
            vector = result.vectors[memory_id]
            metadata = vector.metadata or {}

            # Update access count
            new_count = metadata.get("access_count", 0) + 1
            self.index.update(
                id=memory_id,
                set_metadata={"access_count": new_count},
                namespace=user_id
            )

            memory = {
                "id": memory_id,
                "content": metadata.get("content_full", metadata.get("content", "")),
                "category": metadata.get("category", "general"),
                "tags": json.loads(metadata.get("tags", "[]")),
                "importance": metadata.get("importance", 5),
                "user_id": metadata.get("user_id", user_id),
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

    def delete(self, memory_id: str, user_id: str = "default") -> bool:
        """Delete a memory from Pinecone."""
        try:
            # Check if exists
            result = self.index.fetch(ids=[memory_id], namespace=user_id)
            if memory_id not in result.vectors:
                return False

            self.index.delete(ids=[memory_id], namespace=user_id)
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
        metadata: Optional[Dict[str, Any]] = None,
        user_id: str = "default"
    ) -> bool:
        """Update an existing memory."""
        try:
            # Get existing
            result = self.index.fetch(ids=[memory_id], namespace=user_id)
            if memory_id not in result.vectors:
                return False

            existing = result.vectors[memory_id]
            existing_metadata = existing.metadata or {}

            # Build update metadata
            update_metadata = {}

            if content is not None:
                # Need to re-embed if content changes
                new_embedding = self._get_embedding(content)
                update_metadata["content"] = content[:1000]
                update_metadata["content_full"] = content[:4000]

                # Delete and re-insert with new embedding
                self.index.delete(ids=[memory_id], namespace=user_id)
                self.index.upsert(
                    vectors=[{
                        "id": memory_id,
                        "values": new_embedding,
                        "metadata": {**existing_metadata, **update_metadata}
                    }],
                    namespace=user_id
                )
            else:
                if category is not None:
                    update_metadata["category"] = category
                if tags is not None:
                    update_metadata["tags"] = json.dumps([t.lower() for t in tags])
                if importance is not None:
                    update_metadata["importance"] = max(1, min(10, importance))
                if metadata is not None:
                    for key, value in metadata.items():
                        if isinstance(value, (str, int, float, bool)):
                            update_metadata[f"meta_{key}"] = value
                        else:
                            update_metadata[f"meta_{key}"] = json.dumps(value)

                update_metadata["updated_at"] = datetime.utcnow().isoformat()

                self.index.update(
                    id=memory_id,
                    set_metadata=update_metadata,
                    namespace=user_id
                )

            return True
        except Exception:
            return False

    def list_all(
        self,
        category: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
        user_id: str = "default"
    ) -> List[Dict[str, Any]]:
        """List memories (uses dummy query for Pinecone)."""
        # Pinecone requires a vector for queries, so we use a semantic search
        # with a generic query to list all
        filter_dict = {}
        if category:
            filter_dict["category"] = {"$eq": category}

        # Use a common word to get all results
        results = self.semantic_search(
            query="memory information data",
            limit=limit + offset,
            category=category,
            user_id=user_id
        )

        return results[offset:offset + limit]

    def get_stats(self, user_id: str = "default") -> Dict[str, Any]:
        """Get index statistics."""
        stats = self.index.describe_index_stats()

        namespace_stats = stats.namespaces.get(user_id, {})
        vector_count = namespace_stats.vector_count if hasattr(namespace_stats, 'vector_count') else 0

        return {
            "total_memories": vector_count,
            "total_vectors_all_namespaces": stats.total_vector_count,
            "namespaces": list(stats.namespaces.keys()),
            "dimension": stats.dimension,
            "backend": "PineconeMemoryStore",
            "index_name": self.index_name,
            "embedding_provider": self.embedding_provider
        }

    def clear(self, user_id: str = "default") -> int:
        """Clear all memories in a namespace."""
        stats = self.index.describe_index_stats()
        namespace_stats = stats.namespaces.get(user_id, {})
        count = namespace_stats.vector_count if hasattr(namespace_stats, 'vector_count') else 0

        if count > 0:
            self.index.delete(delete_all=True, namespace=user_id)

        return count
