"""Chroma vector database memory store implementation."""

import uuid
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.adapters.base import MemoryStore
from app.adapters.json_store import RawJsonStore
from app.config import settings
from app.models import MemoryStats, RetrievalHit, Schematic, SearchResult


class ChromaMemoryStore(MemoryStore):
    """Memory store backed by Chroma vector database.

    Uses local JSON as source of truth, with Chroma for semantic indexing.
    """

    def __init__(
        self,
        chroma_path: Optional[Path] = None,
        json_path: Optional[Path] = None,
    ):
        """Initialize the Chroma store.

        Args:
            chroma_path: Path to Chroma persist directory.
            json_path: Path to source JSON file for schematics.
        """
        self.chroma_path = chroma_path or settings.chroma_path
        self.json_store = RawJsonStore(json_path)
        self._hits: List[RetrievalHit] = []
        self._collection = None
        self._client = None
        self._initialized = False

    async def _ensure_initialized(self) -> None:
        """Lazy initialization of Chroma client."""
        if self._initialized:
            return

        try:
            import chromadb
            from chromadb.config import Settings as ChromaSettings

            self.chroma_path.mkdir(parents=True, exist_ok=True)

            self._client = chromadb.PersistentClient(
                path=str(self.chroma_path),
                settings=ChromaSettings(
                    anonymized_telemetry=False,
                    allow_reset=True,
                ),
            )

            self._collection = self._client.get_or_create_collection(
                name="warnerco_schematics",
                metadata={"description": "WARNERCO robot schematics embeddings"},
            )

            self._initialized = True
        except ImportError:
            raise ImportError(
                "chromadb is required for ChromaMemoryStore. "
                "Install with: poetry install"
            )

    async def list_schematics(
        self,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Schematic]:
        """List schematics from JSON source."""
        return await self.json_store.list_schematics(filters, limit, offset)

    async def get_schematic(self, schematic_id: str) -> Optional[Schematic]:
        """Get a schematic from JSON source."""
        return await self.json_store.get_schematic(schematic_id)

    async def upsert_schematic(self, schematic: Schematic) -> Schematic:
        """Update JSON source and re-index in Chroma."""
        result = await self.json_store.upsert_schematic(schematic)
        # Auto-index after upsert
        await self.embed_and_index(schematic.id)
        return result

    async def delete_schematic(self, schematic_id: str) -> bool:
        """Delete from both JSON and Chroma."""
        await self._ensure_initialized()

        # Remove from Chroma
        try:
            self._collection.delete(ids=[schematic_id])
        except Exception:
            pass  # May not exist in Chroma

        return await self.json_store.delete_schematic(schematic_id)

    async def embed_and_index(self, schematic_id: str) -> bool:
        """Embed and index a schematic in Chroma."""
        await self._ensure_initialized()

        schematic = await self.json_store.get_schematic(schematic_id)
        if not schematic:
            return False

        try:
            # Prepare document text and metadata
            document = schematic.to_embed_text()
            metadata = {
                "id": schematic.id,
                "model": schematic.model,
                "name": schematic.name,
                "component": schematic.component,
                "category": schematic.category,
                "status": schematic.status.value,
                "version": schematic.version,
            }

            # Upsert into Chroma (uses built-in embedding)
            self._collection.upsert(
                ids=[schematic.id],
                documents=[document],
                metadatas=[metadata],
            )

            return True
        except Exception as e:
            print(f"Error indexing schematic {schematic_id}: {e}")
            return False

    async def semantic_search(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        top_k: int = 5,
    ) -> List[SearchResult]:
        """Perform semantic search using Chroma."""
        await self._ensure_initialized()
        start_time = datetime.utcnow()

        try:
            # Build where clause from filters
            where = None
            if filters:
                conditions = []
                for key, value in filters.items():
                    if key in ("category", "model", "status"):
                        conditions.append({key: {"$eq": value.lower() if isinstance(value, str) else value}})

                if len(conditions) == 1:
                    where = conditions[0]
                elif len(conditions) > 1:
                    where = {"$and": conditions}

            # Query Chroma
            results = self._collection.query(
                query_texts=[query],
                n_results=top_k,
                where=where,
                include=["documents", "metadatas", "distances"],
            )

            # Convert results
            search_results = []
            ids = results.get("ids", [[]])[0]
            distances = results.get("distances", [[]])[0]
            metadatas = results.get("metadatas", [[]])[0]

            for i, schematic_id in enumerate(ids):
                schematic = await self.json_store.get_schematic(schematic_id)
                if schematic:
                    # Convert distance to similarity score (Chroma uses L2 distance)
                    # Lower distance = higher similarity
                    distance = distances[i] if i < len(distances) else 1.0
                    score = max(0.0, 1.0 - (distance / 2.0))  # Normalize to 0-1

                    search_results.append(
                        SearchResult(
                            schematic=schematic,
                            score=score,
                            chunk_id=schematic_id,
                        )
                    )

            # Record telemetry
            duration_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
            hit = RetrievalHit(
                id=str(uuid.uuid4()),
                timestamp=datetime.utcnow().isoformat(),
                query=query,
                robot_ids=[r.schematic.id for r in search_results],
                chunk_ids=ids,
                scores=[r.score for r in search_results],
                duration_ms=duration_ms,
                backend=self.backend_name,
            )
            self._hits.append(hit)
            if len(self._hits) > 100:
                self._hits = self._hits[-100:]

            return search_results

        except Exception as e:
            print(f"Chroma search error: {e}")
            # Fallback to JSON keyword search
            return await self.json_store.semantic_search(query, filters, top_k)

    async def get_memory_stats(self) -> MemoryStats:
        """Get statistics about the Chroma store."""
        await self._ensure_initialized()

        json_stats = await self.json_store.get_memory_stats()

        try:
            collection_count = self._collection.count()
        except Exception:
            collection_count = 0

        return MemoryStats(
            backend=self.backend_name,
            total_schematics=json_stats.total_schematics,
            indexed_count=collection_count,
            chunk_count=collection_count,
            categories=json_stats.categories,
            status_counts=json_stats.status_counts,
            last_update=json_stats.last_update,
        )

    async def get_recent_hits(self, limit: int = 20) -> List[RetrievalHit]:
        """Get recent retrieval telemetry."""
        return self._hits[-limit:][::-1]

    @property
    def backend_name(self) -> str:
        """Get the name of this backend implementation."""
        return "chroma"

    async def index_all(self) -> int:
        """Index all schematics from JSON source. Returns count indexed."""
        await self._ensure_initialized()
        schematics = await self.json_store.list_schematics(limit=1000)
        count = 0
        for schematic in schematics:
            if await self.embed_and_index(schematic.id):
                count += 1
        return count
