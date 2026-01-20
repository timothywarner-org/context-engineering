"""
JSON Memory Store
=================
Simple file-based memory storage for development and prototyping.

Features:
- Zero dependencies (uses standard library)
- Human-readable storage format
- Thread-safe operations
- Automatic file creation

Limitations:
- No semantic search (substring matching only)
- Not suitable for large datasets (>1000 memories)
- Single-node only (no concurrent multi-process access)

Usage:
    from memory_stores import JSONMemoryStore

    store = JSONMemoryStore("./memories.json")
    memory_id = store.store("Remember this fact", category="facts")
    results = store.search("fact")
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any
from threading import Lock

from .interface import MemoryStore


class JSONMemoryStore(MemoryStore):
    """Thread-safe JSON file-based memory store."""

    def __init__(self, filepath: str = "memories.json"):
        """
        Initialize JSON memory store.

        Args:
            filepath: Path to JSON file (created if doesn't exist)
        """
        self.filepath = Path(filepath)
        self.lock = Lock()
        self._ensure_file()

    def _ensure_file(self) -> None:
        """Create storage file if it doesn't exist."""
        if not self.filepath.exists():
            self.filepath.parent.mkdir(parents=True, exist_ok=True)
            self._save({
                "memories": [],
                "metadata": {
                    "version": "1.0",
                    "created_at": datetime.utcnow().isoformat(),
                    "counter": 0
                }
            })

    def _load(self) -> Dict[str, Any]:
        """Load data from file."""
        with open(self.filepath, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _save(self, data: Dict[str, Any]) -> None:
        """Save data to file."""
        with open(self.filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def store(
        self,
        content: str,
        category: str = "general",
        tags: List[str] = None,
        importance: int = 5,
        metadata: Dict[str, Any] = None
    ) -> str:
        """Store a memory and return its ID."""
        with self.lock:
            data = self._load()

            # Increment counter for unique ID
            counter = data["metadata"].get("counter", len(data["memories"]))
            counter += 1
            data["metadata"]["counter"] = counter

            memory_id = f"mem_{counter:06d}"
            timestamp = datetime.utcnow().isoformat()

            memory = {
                "id": memory_id,
                "content": content,
                "category": category,
                "tags": [t.lower() for t in (tags or [])],
                "importance": max(1, min(10, importance)),
                "metadata": metadata or {},
                "created_at": timestamp,
                "updated_at": timestamp,
                "access_count": 0
            }

            data["memories"].append(memory)
            self._save(data)

            return memory_id

    def search(
        self,
        query: str,
        limit: int = 10,
        category: Optional[str] = None,
        min_importance: int = 0
    ) -> List[Dict[str, Any]]:
        """Search memories using substring matching."""
        data = self._load()
        query_lower = query.lower().strip()
        results = []

        for mem in data["memories"]:
            # Apply filters
            if category and mem["category"] != category:
                continue
            if mem["importance"] < min_importance:
                continue

            # Calculate relevance score
            score = 0

            # Empty query returns all (filtered) memories
            if not query_lower:
                score = mem["importance"]
            else:
                # Content match (highest weight)
                content_lower = mem["content"].lower()
                if query_lower in content_lower:
                    score += 10
                    # Bonus for exact match or content starting with query
                    if content_lower.startswith(query_lower):
                        score += 3
                    # Bonus for word boundary match
                    if f" {query_lower}" in content_lower or content_lower.startswith(query_lower):
                        score += 2

                # Tag match
                for tag in mem.get("tags", []):
                    if query_lower in tag:
                        score += 5
                    if query_lower == tag:
                        score += 3

                # Category match
                if query_lower in mem.get("category", "").lower():
                    score += 3

            if score > 0:
                # Add importance bonus
                score += mem["importance"] * 0.5

                results.append({
                    **mem,
                    "_relevance_score": round(score, 2)
                })

        # Sort by score (desc), then importance (desc), then recency (desc)
        results.sort(
            key=lambda x: (
                x["_relevance_score"],
                x["importance"],
                x["created_at"]
            ),
            reverse=True
        )

        return results[:limit]

    def get(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """Get a memory by ID."""
        with self.lock:
            data = self._load()

            for mem in data["memories"]:
                if mem["id"] == memory_id:
                    # Update access count
                    mem["access_count"] = mem.get("access_count", 0) + 1
                    self._save(data)
                    return mem.copy()

            return None

    def delete(self, memory_id: str) -> bool:
        """Delete a memory by ID."""
        with self.lock:
            data = self._load()
            original_count = len(data["memories"])

            data["memories"] = [
                m for m in data["memories"]
                if m["id"] != memory_id
            ]

            if len(data["memories"]) < original_count:
                self._save(data)
                return True

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
        with self.lock:
            data = self._load()

            for mem in data["memories"]:
                if mem["id"] == memory_id:
                    if content is not None:
                        mem["content"] = content
                    if category is not None:
                        mem["category"] = category
                    if tags is not None:
                        mem["tags"] = [t.lower() for t in tags]
                    if importance is not None:
                        mem["importance"] = max(1, min(10, importance))
                    if metadata is not None:
                        mem["metadata"] = metadata

                    mem["updated_at"] = datetime.utcnow().isoformat()
                    self._save(data)
                    return True

            return False

    def list_all(
        self,
        category: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """List all memories with pagination."""
        data = self._load()
        memories = data["memories"]

        if category:
            memories = [m for m in memories if m["category"] == category]

        # Sort by importance desc, then by created_at desc
        memories.sort(
            key=lambda x: (x["importance"], x["created_at"]),
            reverse=True
        )

        return memories[offset:offset + limit]

    def get_stats(self) -> Dict[str, Any]:
        """Get storage statistics."""
        data = self._load()
        memories = data["memories"]

        if not memories:
            return {
                "total_memories": 0,
                "categories": {},
                "avg_importance": 0,
                "backend": "JSONMemoryStore",
                "filepath": str(self.filepath)
            }

        categories = {}
        tags_count = {}
        total_importance = 0

        for mem in memories:
            cat = mem.get("category", "general")
            categories[cat] = categories.get(cat, 0) + 1

            for tag in mem.get("tags", []):
                tags_count[tag] = tags_count.get(tag, 0) + 1

            total_importance += mem.get("importance", 5)

        return {
            "total_memories": len(memories),
            "categories": categories,
            "top_tags": dict(sorted(
                tags_count.items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]),
            "avg_importance": round(total_importance / len(memories), 2),
            "backend": "JSONMemoryStore",
            "filepath": str(self.filepath),
            "file_size_bytes": self.filepath.stat().st_size
        }

    def clear(self) -> int:
        """Clear all memories."""
        with self.lock:
            data = self._load()
            count = len(data["memories"])

            data["memories"] = []
            data["metadata"]["counter"] = 0
            self._save(data)

            return count
