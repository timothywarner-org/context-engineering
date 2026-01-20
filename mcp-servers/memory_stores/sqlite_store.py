"""
SQLite Memory Store
===================
Structured memory storage with full-text search capabilities.

Features:
- Full-text search using FTS5
- SQL-based filtering and queries
- ACID transactions
- No external dependencies

Limitations:
- No true semantic search (keyword matching only)
- Single-file database
- Not suitable for distributed systems

Usage:
    from memory_stores import SQLiteMemoryStore

    store = SQLiteMemoryStore("./memories.db")
    memory_id = store.store("Remember this fact", category="facts")
    results = store.search("fact")
"""

import sqlite3
from datetime import datetime
from typing import Optional, List, Dict, Any
from contextlib import contextmanager
import json
import uuid

from .interface import MemoryStore


class SQLiteMemoryStore(MemoryStore):
    """SQLite-based memory store with FTS5 full-text search."""

    def __init__(self, db_path: str = "memories.db"):
        """
        Initialize SQLite memory store.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self._init_db()

    @contextmanager
    def _get_connection(self):
        """Get database connection context manager."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        try:
            yield conn
        finally:
            conn.close()

    def _init_db(self) -> None:
        """Initialize database schema with FTS5 support."""
        with self._get_connection() as conn:
            # Main memories table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id TEXT PRIMARY KEY,
                    content TEXT NOT NULL,
                    category TEXT DEFAULT 'general',
                    tags TEXT,
                    importance INTEGER DEFAULT 5 CHECK (importance >= 1 AND importance <= 10),
                    metadata TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    access_count INTEGER DEFAULT 0
                )
            """)

            # Create index for category lookups
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_memories_category
                ON memories(category)
            """)

            # Create index for importance filtering
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_memories_importance
                ON memories(importance DESC)
            """)

            # FTS5 virtual table for full-text search
            conn.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS memories_fts USING fts5(
                    content,
                    category,
                    tags,
                    content=memories,
                    content_rowid=rowid,
                    tokenize='porter unicode61'
                )
            """)

            # Triggers to keep FTS in sync with main table
            conn.execute("""
                CREATE TRIGGER IF NOT EXISTS memories_ai AFTER INSERT ON memories BEGIN
                    INSERT INTO memories_fts(rowid, content, category, tags)
                    VALUES (new.rowid, new.content, new.category, new.tags);
                END
            """)

            conn.execute("""
                CREATE TRIGGER IF NOT EXISTS memories_ad AFTER DELETE ON memories BEGIN
                    INSERT INTO memories_fts(memories_fts, rowid, content, category, tags)
                    VALUES ('delete', old.rowid, old.content, old.category, old.tags);
                END
            """)

            conn.execute("""
                CREATE TRIGGER IF NOT EXISTS memories_au AFTER UPDATE ON memories BEGIN
                    INSERT INTO memories_fts(memories_fts, rowid, content, category, tags)
                    VALUES ('delete', old.rowid, old.content, old.category, old.tags);
                    INSERT INTO memories_fts(rowid, content, category, tags)
                    VALUES (new.rowid, new.content, new.category, new.tags);
                END
            """)

            conn.commit()

    def store(
        self,
        content: str,
        category: str = "general",
        tags: List[str] = None,
        importance: int = 5,
        metadata: Dict[str, Any] = None
    ) -> str:
        """Store a memory with automatic FTS indexing."""
        memory_id = f"mem_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:8]}"
        timestamp = datetime.utcnow().isoformat()

        tags_json = json.dumps([t.lower() for t in (tags or [])])
        metadata_json = json.dumps(metadata or {})

        with self._get_connection() as conn:
            conn.execute("""
                INSERT INTO memories (
                    id, content, category, tags, importance,
                    metadata, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                memory_id,
                content,
                category,
                tags_json,
                max(1, min(10, importance)),
                metadata_json,
                timestamp,
                timestamp
            ))
            conn.commit()

        return memory_id

    def search(
        self,
        query: str,
        limit: int = 10,
        category: Optional[str] = None,
        min_importance: int = 0
    ) -> List[Dict[str, Any]]:
        """Search memories using FTS5 full-text search."""
        with self._get_connection() as conn:
            query = query.strip()

            if query:
                # Use FTS5 for searching
                # Build dynamic WHERE clause
                params = []
                where_parts = []

                if category:
                    where_parts.append("m.category = ?")
                    params.append(category)

                if min_importance > 0:
                    where_parts.append("m.importance >= ?")
                    params.append(min_importance)

                where_clause = ""
                if where_parts:
                    where_clause = "AND " + " AND ".join(where_parts)

                # Escape FTS5 special characters
                safe_query = query.replace('"', '""')

                cursor = conn.execute(f"""
                    SELECT
                        m.*,
                        bm25(memories_fts, 1.0, 0.5, 0.5) as rank
                    FROM memories m
                    JOIN memories_fts ON m.rowid = memories_fts.rowid
                    WHERE memories_fts MATCH ?
                    {where_clause}
                    ORDER BY rank, m.importance DESC
                    LIMIT ?
                """, (f'"{safe_query}"*', *params, limit))

                results = []
                for row in cursor.fetchall():
                    memory = dict(row)
                    memory["tags"] = json.loads(memory.get("tags") or "[]")
                    memory["metadata"] = json.loads(memory.get("metadata") or "{}")
                    memory["_relevance_score"] = abs(memory.pop("rank", 0)) + memory["importance"] * 0.5
                    results.append(memory)

                return results

            else:
                # No query - return filtered memories sorted by importance
                params = []
                where_parts = []

                if category:
                    where_parts.append("category = ?")
                    params.append(category)

                if min_importance > 0:
                    where_parts.append("importance >= ?")
                    params.append(min_importance)

                where_clause = ""
                if where_parts:
                    where_clause = "WHERE " + " AND ".join(where_parts)

                cursor = conn.execute(f"""
                    SELECT * FROM memories
                    {where_clause}
                    ORDER BY importance DESC, created_at DESC
                    LIMIT ?
                """, (*params, limit))

                results = []
                for row in cursor.fetchall():
                    memory = dict(row)
                    memory["tags"] = json.loads(memory.get("tags") or "[]")
                    memory["metadata"] = json.loads(memory.get("metadata") or "{}")
                    memory["_relevance_score"] = memory["importance"]
                    results.append(memory)

                return results

    def get(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """Get a memory by ID and increment access count."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM memories WHERE id = ?",
                (memory_id,)
            )
            row = cursor.fetchone()

            if row:
                # Update access count
                conn.execute("""
                    UPDATE memories
                    SET access_count = access_count + 1
                    WHERE id = ?
                """, (memory_id,))
                conn.commit()

                memory = dict(row)
                memory["tags"] = json.loads(memory.get("tags") or "[]")
                memory["metadata"] = json.loads(memory.get("metadata") or "{}")
                return memory

            return None

    def delete(self, memory_id: str) -> bool:
        """Delete a memory by ID."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "DELETE FROM memories WHERE id = ?",
                (memory_id,)
            )
            conn.commit()
            return cursor.rowcount > 0

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
        # Build dynamic UPDATE query
        updates = []
        params = []

        if content is not None:
            updates.append("content = ?")
            params.append(content)

        if category is not None:
            updates.append("category = ?")
            params.append(category)

        if tags is not None:
            updates.append("tags = ?")
            params.append(json.dumps([t.lower() for t in tags]))

        if importance is not None:
            updates.append("importance = ?")
            params.append(max(1, min(10, importance)))

        if metadata is not None:
            updates.append("metadata = ?")
            params.append(json.dumps(metadata))

        if not updates:
            return False

        updates.append("updated_at = ?")
        params.append(datetime.utcnow().isoformat())

        params.append(memory_id)

        with self._get_connection() as conn:
            cursor = conn.execute(
                f"UPDATE memories SET {', '.join(updates)} WHERE id = ?",
                params
            )
            conn.commit()
            return cursor.rowcount > 0

    def list_all(
        self,
        category: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """List memories with pagination."""
        with self._get_connection() as conn:
            if category:
                cursor = conn.execute("""
                    SELECT * FROM memories
                    WHERE category = ?
                    ORDER BY importance DESC, created_at DESC
                    LIMIT ? OFFSET ?
                """, (category, limit, offset))
            else:
                cursor = conn.execute("""
                    SELECT * FROM memories
                    ORDER BY importance DESC, created_at DESC
                    LIMIT ? OFFSET ?
                """, (limit, offset))

            results = []
            for row in cursor.fetchall():
                memory = dict(row)
                memory["tags"] = json.loads(memory.get("tags") or "[]")
                memory["metadata"] = json.loads(memory.get("metadata") or "{}")
                results.append(memory)

            return results

    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        with self._get_connection() as conn:
            # Total count
            cursor = conn.execute("SELECT COUNT(*) as total FROM memories")
            total = cursor.fetchone()["total"]

            if total == 0:
                return {
                    "total_memories": 0,
                    "categories": {},
                    "backend": "SQLiteMemoryStore",
                    "db_path": self.db_path
                }

            # Category counts
            cursor = conn.execute("""
                SELECT category, COUNT(*) as count
                FROM memories
                GROUP BY category
                ORDER BY count DESC
            """)
            categories = {row["category"]: row["count"] for row in cursor.fetchall()}

            # Average importance
            cursor = conn.execute("SELECT AVG(importance) as avg FROM memories")
            avg_importance = cursor.fetchone()["avg"]

            # Most accessed
            cursor = conn.execute("""
                SELECT id, content, access_count
                FROM memories
                ORDER BY access_count DESC
                LIMIT 5
            """)
            most_accessed = [
                {
                    "id": row["id"],
                    "content_preview": row["content"][:50],
                    "access_count": row["access_count"]
                }
                for row in cursor.fetchall()
            ]

            return {
                "total_memories": total,
                "categories": categories,
                "avg_importance": round(avg_importance, 2),
                "most_accessed": most_accessed,
                "backend": "SQLiteMemoryStore",
                "db_path": self.db_path
            }

    def clear(self) -> int:
        """Clear all memories."""
        with self._get_connection() as conn:
            cursor = conn.execute("SELECT COUNT(*) as count FROM memories")
            count = cursor.fetchone()["count"]

            conn.execute("DELETE FROM memories")
            conn.commit()

            return count

    def execute_sql(self, query: str, params: tuple = ()) -> List[Dict]:
        """
        Execute arbitrary SQL query (for advanced use cases).

        Args:
            query: SQL query string
            params: Query parameters

        Returns:
            List of result rows as dicts
        """
        with self._get_connection() as conn:
            cursor = conn.execute(query, params)
            if cursor.description:
                return [dict(row) for row in cursor.fetchall()]
            conn.commit()
            return []
