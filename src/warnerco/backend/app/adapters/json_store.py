"""Raw JSON file-based memory store implementation."""

import json
import uuid
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.adapters.base import MemoryStore
from app.config import settings
from app.models import MemoryStats, RetrievalHit, Schematic, SearchResult


class RawJsonStore(MemoryStore):
    """Memory store backed by raw JSON files.

    This is the simplest implementation - reads/writes schematics to JSON files.
    Semantic search falls back to keyword matching.
    """

    def __init__(self, json_path: Optional[Path] = None):
        """Initialize the JSON store.

        Args:
            json_path: Path to schematics JSON file. Defaults to config setting.
        """
        self.json_path = json_path or settings.json_path
        self._schematics: Dict[str, Schematic] = {}
        self._hits: List[RetrievalHit] = []
        self._last_update: Optional[str] = None
        self._load_schematics()

    def _load_schematics(self) -> None:
        """Load schematics from JSON file."""
        if not self.json_path.exists():
            self._schematics = {}
            return

        try:
            with open(self.json_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            self._schematics = {
                item["id"]: Schematic(**item) for item in data
            }
            self._last_update = datetime.utcnow().isoformat()
        except Exception as e:
            print(f"Error loading schematics: {e}")
            self._schematics = {}

    def _save_schematics(self) -> None:
        """Save schematics to JSON file."""
        self.json_path.parent.mkdir(parents=True, exist_ok=True)

        data = [s.model_dump() for s in self._schematics.values()]
        with open(self.json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, default=str)

        self._last_update = datetime.utcnow().isoformat()

    def _matches_filters(self, schematic: Schematic, filters: Dict[str, Any]) -> bool:
        """Check if schematic matches the given filters."""
        for key, value in filters.items():
            if key == "category" and schematic.category.lower() != value.lower():
                return False
            if key == "model" and schematic.model.lower() != value.lower():
                return False
            if key == "status" and schematic.status.value.lower() != value.lower():
                return False
            if key == "tags" and isinstance(value, list):
                if not any(tag.lower() in [t.lower() for t in schematic.tags] for tag in value):
                    return False
        return True

    def _keyword_score(self, schematic: Schematic, query: str) -> float:
        """Calculate a simple keyword-based relevance score."""
        query_lower = query.lower()
        query_words = query_lower.split()

        text = schematic.to_embed_text().lower()

        # Count word matches
        matches = sum(1 for word in query_words if word in text)

        # Bonus for exact phrase match
        phrase_bonus = 0.2 if query_lower in text else 0.0

        # Calculate score (0-1 range)
        base_score = matches / max(len(query_words), 1)
        return min(1.0, base_score + phrase_bonus)

    async def list_schematics(
        self,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Schematic]:
        """List all schematics with optional filtering."""
        schematics = list(self._schematics.values())

        if filters:
            schematics = [s for s in schematics if self._matches_filters(s, filters)]

        # Sort by ID
        schematics.sort(key=lambda s: s.id)

        return schematics[offset:offset + limit]

    async def get_schematic(self, schematic_id: str) -> Optional[Schematic]:
        """Get a single schematic by ID."""
        return self._schematics.get(schematic_id)

    async def upsert_schematic(self, schematic: Schematic) -> Schematic:
        """Create or update a schematic."""
        self._schematics[schematic.id] = schematic
        self._save_schematics()
        return schematic

    async def delete_schematic(self, schematic_id: str) -> bool:
        """Delete a schematic by ID."""
        if schematic_id in self._schematics:
            del self._schematics[schematic_id]
            self._save_schematics()
            return True
        return False

    async def embed_and_index(self, schematic_id: str) -> bool:
        """JSON store doesn't do embedding - just verify schematic exists."""
        return schematic_id in self._schematics

    async def semantic_search(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        top_k: int = 5,
    ) -> List[SearchResult]:
        """Perform keyword-based search (fallback for semantic search)."""
        start_time = datetime.utcnow()

        candidates = list(self._schematics.values())

        # Apply filters
        if filters:
            candidates = [s for s in candidates if self._matches_filters(s, filters)]

        # Score and sort
        scored = [(s, self._keyword_score(s, query)) for s in candidates]
        scored = [(s, score) for s, score in scored if score > 0]
        scored.sort(key=lambda x: x[1], reverse=True)

        results = [
            SearchResult(schematic=s, score=score, chunk_id=None)
            for s, score in scored[:top_k]
        ]

        # Record telemetry
        duration_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
        hit = RetrievalHit(
            id=str(uuid.uuid4()),
            timestamp=datetime.utcnow().isoformat(),
            query=query,
            robot_ids=[r.schematic.id for r in results],
            chunk_ids=[],
            scores=[r.score for r in results],
            duration_ms=duration_ms,
            backend=self.backend_name,
        )
        self._hits.append(hit)
        if len(self._hits) > 100:
            self._hits = self._hits[-100:]

        return results

    async def get_memory_stats(self) -> MemoryStats:
        """Get statistics about the JSON store."""
        schematics = list(self._schematics.values())

        categories = Counter(s.category for s in schematics)
        status_counts = Counter(s.status.value for s in schematics)

        return MemoryStats(
            backend=self.backend_name,
            total_schematics=len(schematics),
            indexed_count=len(schematics),  # All are "indexed" in JSON
            chunk_count=0,
            categories=dict(categories),
            status_counts=dict(status_counts),
            last_update=self._last_update,
        )

    async def get_recent_hits(self, limit: int = 20) -> List[RetrievalHit]:
        """Get recent retrieval telemetry."""
        return self._hits[-limit:][::-1]

    @property
    def backend_name(self) -> str:
        """Get the name of this backend implementation."""
        return "json"
