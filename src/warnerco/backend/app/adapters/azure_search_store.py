"""Azure AI Search memory store implementation."""

import uuid
from collections import Counter, deque
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.adapters.base import MemoryStore
from app.adapters.json_store import RawJsonStore
from app.config import settings
from app.models import MemoryStats, RetrievalHit, Schematic, SearchResult


def _escape_odata_string(value: str) -> str:
    """Escape single quotes in OData filter strings to prevent injection."""
    return value.replace("'", "''")


class AzureAiSearchMemoryStore(MemoryStore):
    """Memory store backed by Azure AI Search.

    Uses local JSON as source of truth, with Azure AI Search for enterprise semantic indexing.
    """

    def __init__(self):
        """Initialize the Azure AI Search store."""
        self.json_store = RawJsonStore()
        self._hits: deque[RetrievalHit] = deque(maxlen=100)
        self._client = None
        self._index_client = None
        self._initialized = False

    async def _ensure_initialized(self) -> None:
        """Lazy initialization of Azure AI Search client."""
        if self._initialized:
            return

        if not settings.azure_search_endpoint or not settings.azure_search_key:
            raise ValueError(
                "Azure AI Search requires AZURE_SEARCH_ENDPOINT and AZURE_SEARCH_KEY environment variables"
            )

        try:
            from azure.core.credentials import AzureKeyCredential
            from azure.search.documents import SearchClient
            from azure.search.documents.indexes import SearchIndexClient
            from azure.search.documents.indexes.models import (
                SearchIndex,
                SearchField,
                SearchFieldDataType,
                SimpleField,
                SearchableField,
                VectorSearch,
                HnswAlgorithmConfiguration,
                VectorSearchProfile,
            )

            credential = AzureKeyCredential(settings.azure_search_key)

            # Index client for schema management
            self._index_client = SearchIndexClient(
                endpoint=settings.azure_search_endpoint,
                credential=credential,
            )

            # Ensure index exists
            await self._ensure_index()

            # Search client for queries
            self._client = SearchClient(
                endpoint=settings.azure_search_endpoint,
                index_name=settings.azure_search_index,
                credential=credential,
            )

            self._initialized = True

        except ImportError:
            raise ImportError(
                "azure-search-documents is required for AzureAiSearchMemoryStore. "
                "Install with: poetry install --with azure"
            )

    async def _ensure_index(self) -> None:
        """Ensure the search index exists with correct schema."""
        from azure.search.documents.indexes.models import (
            SearchIndex,
            SearchField,
            SearchFieldDataType,
            SimpleField,
            SearchableField,
        )

        index_name = settings.azure_search_index

        # Check if index exists
        try:
            self._index_client.get_index(index_name)
            return  # Index exists
        except Exception:
            pass  # Index doesn't exist, create it

        # Define index schema
        fields = [
            SimpleField(name="id", type=SearchFieldDataType.String, key=True),
            SearchableField(name="model", type=SearchFieldDataType.String, filterable=True, facetable=True),
            SearchableField(name="name", type=SearchFieldDataType.String),
            SearchableField(name="component", type=SearchFieldDataType.String),
            SearchableField(name="version", type=SearchFieldDataType.String, filterable=True),
            SearchableField(name="summary", type=SearchFieldDataType.String),
            SearchableField(name="category", type=SearchFieldDataType.String, filterable=True, facetable=True),
            SimpleField(name="status", type=SearchFieldDataType.String, filterable=True, facetable=True),
            SearchableField(name="tags", type=SearchFieldDataType.Collection(SearchFieldDataType.String)),
            SearchableField(name="content", type=SearchFieldDataType.String),  # Full text for search
            SimpleField(name="last_verified", type=SearchFieldDataType.String, filterable=True),
            SimpleField(name="url", type=SearchFieldDataType.String),
        ]

        index = SearchIndex(name=index_name, fields=fields)
        self._index_client.create_or_update_index(index)

    def _schematic_to_document(self, schematic: Schematic) -> Dict[str, Any]:
        """Convert a Schematic to an Azure Search document."""
        return {
            "id": schematic.id,
            "model": schematic.model,
            "name": schematic.name,
            "component": schematic.component,
            "version": schematic.version,
            "summary": schematic.summary,
            "category": schematic.category,
            "status": schematic.status.value,
            "tags": schematic.tags,
            "content": schematic.to_embed_text(),
            "last_verified": schematic.last_verified,
            "url": schematic.url,
        }

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
        """Update JSON source and re-index in Azure Search."""
        result = await self.json_store.upsert_schematic(schematic)
        await self.embed_and_index(schematic.id)
        return result

    async def delete_schematic(self, schematic_id: str) -> bool:
        """Delete from both JSON and Azure Search."""
        await self._ensure_initialized()

        try:
            self._client.delete_documents(documents=[{"id": schematic_id}])
        except Exception:
            pass

        return await self.json_store.delete_schematic(schematic_id)

    async def embed_and_index(self, schematic_id: str) -> bool:
        """Index a schematic in Azure AI Search."""
        await self._ensure_initialized()

        schematic = await self.json_store.get_schematic(schematic_id)
        if not schematic:
            return False

        try:
            document = self._schematic_to_document(schematic)
            self._client.upload_documents(documents=[document])
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
        """Perform semantic search using Azure AI Search."""
        await self._ensure_initialized()
        start_time = datetime.now(timezone.utc)

        try:
            # Build filter expression
            filter_expr = None
            if filters:
                conditions = []
                for key, value in filters.items():
                    if key in ("category", "model", "status"):
                        conditions.append(f"{key} eq '{_escape_odata_string(str(value))}'")
                if conditions:
                    filter_expr = " and ".join(conditions)

            # Execute search
            results = self._client.search(
                search_text=query,
                filter=filter_expr,
                top=top_k,
                include_total_count=True,
            )

            # Convert results
            search_results = []
            for result in results:
                schematic = await self.json_store.get_schematic(result["id"])
                if schematic:
                    score = result.get("@search.score", 0.0)
                    # Normalize score to 0-1 range (Azure search scores can exceed 1)
                    normalized_score = min(1.0, score / 10.0)

                    search_results.append(
                        SearchResult(
                            schematic=schematic,
                            score=normalized_score,
                            chunk_id=result["id"],
                        )
                    )

            # Record telemetry
            duration_ms = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
            hit = RetrievalHit(
                id=str(uuid.uuid4()),
                timestamp=datetime.now(timezone.utc).isoformat(),
                query=query,
                robot_ids=[r.schematic.id for r in search_results],
                chunk_ids=[r.chunk_id for r in search_results if r.chunk_id],
                scores=[r.score for r in search_results],
                duration_ms=duration_ms,
                backend=self.backend_name,
            )
            self._hits.append(hit)

            return search_results

        except Exception as e:
            print(f"Azure Search error: {e}")
            return await self.json_store.semantic_search(query, filters, top_k)

    async def get_memory_stats(self) -> MemoryStats:
        """Get statistics about the Azure Search store."""
        await self._ensure_initialized()

        json_stats = await self.json_store.get_memory_stats()

        try:
            # Get document count from Azure Search
            results = self._client.search(search_text="*", top=0, include_total_count=True)
            indexed_count = results.get_count() or 0
        except Exception:
            indexed_count = 0

        return MemoryStats(
            backend=self.backend_name,
            total_schematics=json_stats.total_schematics,
            indexed_count=indexed_count,
            chunk_count=indexed_count,
            categories=json_stats.categories,
            status_counts=json_stats.status_counts,
            last_update=json_stats.last_update,
        )

    async def get_recent_hits(self, limit: int = 20) -> List[RetrievalHit]:
        """Get recent retrieval telemetry."""
        return list(self._hits)[-limit:][::-1]

    @property
    def backend_name(self) -> str:
        """Get the name of this backend implementation."""
        return "azure_search"

    async def index_all(self) -> int:
        """Index all schematics from JSON source. Returns count indexed."""
        await self._ensure_initialized()
        schematics = await self.json_store.list_schematics(limit=1000)
        count = 0
        for schematic in schematics:
            if await self.embed_and_index(schematic.id):
                count += 1
        return count
