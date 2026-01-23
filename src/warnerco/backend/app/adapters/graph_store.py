"""SQLite-backed Knowledge Graph store with NetworkX integration.

This module implements a triplet store for the Knowledge Graph memory layer.
It uses SQLite for persistence and NetworkX for graph algorithms like
shortest path computation.

Architecture:
- SQLite stores entities and triplets (relationships) persistently
- NetworkX DiGraph provides in-memory graph algorithms
- The store syncs between SQLite and NetworkX on initialization

Usage:
    from app.adapters.graph_store import GraphStore

    store = GraphStore()
    await store.add_entity(Entity(id="WRN-00001", entity_type="schematic", name="Atlas Prime"))
    await store.add_relationship(Relationship(subject="WRN-00001", predicate="has_status", object="active"))

    neighbors = await store.get_neighbors("WRN-00001")
    path = await store.shortest_path("WRN-00001", "hydraulic_system")
"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional

import networkx as nx

from app.models.graph import (
    Entity,
    GraphQueryResult,
    GraphStats,
    Relationship,
    VALID_PREDICATES,
)


class GraphStore:
    """SQLite-backed triplet store with NetworkX graph algorithms.

    The store maintains both a SQLite database for persistence and a
    NetworkX DiGraph for efficient graph traversal algorithms.

    Attributes:
        db_path: Path to the SQLite database file
        _conn: SQLite connection
        _graph: NetworkX directed graph for algorithms
    """

    def __init__(self, db_path: Optional[Path | str] = None):
        """Initialize the graph store.

        Args:
            db_path: Path to SQLite database. Defaults to data/graph/knowledge.db
                     relative to the backend directory. Can be a Path or string.
        """
        if db_path is None:
            # Default path: backend/data/graph/knowledge.db
            backend_dir = Path(__file__).parent.parent.parent.resolve()
            db_path = backend_dir / "data" / "graph" / "knowledge.db"
        elif isinstance(db_path, str):
            db_path = Path(db_path)

        self.db_path = db_path
        self._conn: Optional[sqlite3.Connection] = None
        self._graph: nx.DiGraph = nx.DiGraph()

        # Initialize database and load into NetworkX
        self._init_db()
        self._load_graph()

    def _init_db(self) -> None:
        """Initialize the SQLite database schema."""
        # Ensure directory exists
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        self._conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        self._conn.row_factory = sqlite3.Row

        cursor = self._conn.cursor()

        # Create entities table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS entities (
                id TEXT PRIMARY KEY,
                entity_type TEXT NOT NULL,
                name TEXT NOT NULL,
                metadata TEXT
            )
        """)

        # Create triplets table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS triplets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject TEXT NOT NULL,
                predicate TEXT NOT NULL,
                object TEXT NOT NULL,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(subject, predicate, object)
            )
        """)

        # Create indexes for efficient lookups
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_subject ON triplets(subject)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_object ON triplets(object)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_predicate ON triplets(predicate)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_entity_type ON entities(entity_type)")

        self._conn.commit()

    def _load_graph(self) -> None:
        """Load graph data from SQLite into NetworkX DiGraph."""
        if self._conn is None:
            return

        cursor = self._conn.cursor()

        # Load entities as nodes
        cursor.execute("SELECT id, entity_type, name, metadata FROM entities")
        for row in cursor.fetchall():
            metadata = json.loads(row["metadata"]) if row["metadata"] else {}
            self._graph.add_node(
                row["id"],
                entity_type=row["entity_type"],
                name=row["name"],
                **metadata
            )

        # Load triplets as edges
        cursor.execute("SELECT subject, predicate, object, metadata FROM triplets")
        for row in cursor.fetchall():
            metadata = json.loads(row["metadata"]) if row["metadata"] else {}
            self._graph.add_edge(
                row["subject"],
                row["object"],
                predicate=row["predicate"],
                **metadata
            )

    async def add_entity(self, entity: Entity) -> bool:
        """Add an entity to the graph.

        Args:
            entity: Entity to add

        Returns:
            True if entity was added, False if it already exists
        """
        if self._conn is None:
            return False

        cursor = self._conn.cursor()

        try:
            metadata_json = json.dumps(entity.metadata) if entity.metadata else None
            cursor.execute(
                "INSERT OR REPLACE INTO entities (id, entity_type, name, metadata) VALUES (?, ?, ?, ?)",
                (entity.id, entity.entity_type, entity.name, metadata_json)
            )
            self._conn.commit()

            # Update NetworkX graph
            node_attrs = {"entity_type": entity.entity_type, "name": entity.name}
            if entity.metadata:
                node_attrs.update(entity.metadata)
            self._graph.add_node(entity.id, **node_attrs)

            return True

        except sqlite3.Error as e:
            print(f"Error adding entity: {e}", flush=True)
            return False

    async def add_relationship(self, rel: Relationship) -> bool:
        """Add a relationship (triplet) to the graph.

        Args:
            rel: Relationship to add

        Returns:
            True if relationship was added, False on error or duplicate
        """
        if self._conn is None:
            return False

        cursor = self._conn.cursor()

        try:
            metadata_json = json.dumps(rel.metadata) if rel.metadata else None
            cursor.execute(
                """INSERT OR IGNORE INTO triplets (subject, predicate, object, metadata)
                   VALUES (?, ?, ?, ?)""",
                (rel.subject, rel.predicate, rel.object, metadata_json)
            )
            self._conn.commit()

            # Update NetworkX graph
            edge_attrs = {"predicate": rel.predicate}
            if rel.metadata:
                edge_attrs.update(rel.metadata)
            self._graph.add_edge(rel.subject, rel.object, **edge_attrs)

            return cursor.rowcount > 0

        except sqlite3.Error as e:
            print(f"Error adding relationship: {e}", flush=True)
            return False

    async def get_entity(self, entity_id: str) -> Optional[Entity]:
        """Get an entity by ID.

        Args:
            entity_id: Unique entity identifier

        Returns:
            Entity if found, None otherwise
        """
        if self._conn is None:
            return None

        cursor = self._conn.cursor()
        cursor.execute(
            "SELECT id, entity_type, name, metadata FROM entities WHERE id = ?",
            (entity_id,)
        )
        row = cursor.fetchone()

        if row is None:
            return None

        metadata = json.loads(row["metadata"]) if row["metadata"] else None
        return Entity(
            id=row["id"],
            entity_type=row["entity_type"],
            name=row["name"],
            metadata=metadata
        )

    async def get_related(
        self,
        subject: str,
        predicate: Optional[str] = None
    ) -> list[Relationship]:
        """Get relationships where the given entity is the subject.

        This finds all outgoing relationships from an entity.

        Args:
            subject: Subject entity ID
            predicate: Optional predicate filter

        Returns:
            List of matching relationships
        """
        if self._conn is None:
            return []

        cursor = self._conn.cursor()

        if predicate:
            cursor.execute(
                "SELECT subject, predicate, object, metadata FROM triplets WHERE subject = ? AND predicate = ?",
                (subject, predicate)
            )
        else:
            cursor.execute(
                "SELECT subject, predicate, object, metadata FROM triplets WHERE subject = ?",
                (subject,)
            )

        relationships = []
        for row in cursor.fetchall():
            metadata = json.loads(row["metadata"]) if row["metadata"] else None
            relationships.append(Relationship(
                subject=row["subject"],
                predicate=row["predicate"],
                object=row["object"],
                metadata=metadata
            ))

        return relationships

    async def get_subjects(
        self,
        object_id: str,
        predicate: Optional[str] = None
    ) -> list[Relationship]:
        """Get relationships where the given entity is the object (reverse lookup).

        This finds all incoming relationships to an entity.

        Args:
            object_id: Object entity ID
            predicate: Optional predicate filter

        Returns:
            List of matching relationships
        """
        if self._conn is None:
            return []

        cursor = self._conn.cursor()

        if predicate:
            cursor.execute(
                "SELECT subject, predicate, object, metadata FROM triplets WHERE object = ? AND predicate = ?",
                (object_id, predicate)
            )
        else:
            cursor.execute(
                "SELECT subject, predicate, object, metadata FROM triplets WHERE object = ?",
                (object_id,)
            )

        relationships = []
        for row in cursor.fetchall():
            metadata = json.loads(row["metadata"]) if row["metadata"] else None
            relationships.append(Relationship(
                subject=row["subject"],
                predicate=row["predicate"],
                object=row["object"],
                metadata=metadata
            ))

        return relationships

    async def get_neighbors(
        self,
        entity_id: str,
        direction: str = "both"
    ) -> list[str]:
        """Get all entities connected to the given entity.

        Args:
            entity_id: Entity to find neighbors for
            direction: 'outgoing' (subject->object), 'incoming' (object<-subject), or 'both'

        Returns:
            List of neighbor entity IDs
        """
        neighbors = set()

        if direction in ("outgoing", "both"):
            # Get successors (outgoing edges)
            if entity_id in self._graph:
                neighbors.update(self._graph.successors(entity_id))

        if direction in ("incoming", "both"):
            # Get predecessors (incoming edges)
            if entity_id in self._graph:
                neighbors.update(self._graph.predecessors(entity_id))

        return list(neighbors)

    async def shortest_path(
        self,
        source: str,
        target: str
    ) -> Optional[list[str]]:
        """Find the shortest path between two entities.

        Uses NetworkX's shortest path algorithm on the underlying graph.

        Args:
            source: Source entity ID
            target: Target entity ID

        Returns:
            List of entity IDs forming the path, or None if no path exists
        """
        if source not in self._graph or target not in self._graph:
            return None

        try:
            # Use undirected view for path finding (edges can be traversed both ways)
            undirected = self._graph.to_undirected()
            path = nx.shortest_path(undirected, source, target)
            return path
        except nx.NetworkXNoPath:
            return None
        except nx.NodeNotFound:
            return None

    def get_nx_graph(self) -> nx.DiGraph:
        """Get the underlying NetworkX directed graph.

        Returns:
            NetworkX DiGraph instance for advanced graph operations
        """
        return self._graph

    async def index_schematics(self, schematics: list[dict]) -> dict:
        """Auto-extract entities and relationships from schematics.

        This method processes schematic data and extracts:
        - Schematic entities
        - Status entities and has_status relationships
        - Category entities and has_category relationships
        - Model entities and belongs_to_model relationships
        - Component entities inferred from descriptions
        - Tag entities and has_tag relationships

        Args:
            schematics: List of schematic dictionaries from schematics.json

        Returns:
            Dictionary with counts of entities and relationships added
        """
        entities_added = 0
        relationships_added = 0

        # Track unique entities to avoid duplicates
        seen_entities = set()

        for schematic in schematics:
            schematic_id = schematic["id"]

            # 1. Add schematic entity
            schematic_entity = Entity(
                id=schematic_id,
                entity_type="schematic",
                name=f"{schematic['model']} - {schematic['name']}: {schematic['component']}",
                metadata={
                    "model": schematic["model"],
                    "robot_name": schematic["name"],
                    "component": schematic["component"],
                    "version": schematic["version"],
                }
            )
            if await self.add_entity(schematic_entity):
                entities_added += 1

            # 2. Add status entity and relationship
            status = schematic.get("status", "active")
            status_id = f"status:{status}"
            if status_id not in seen_entities:
                await self.add_entity(Entity(
                    id=status_id,
                    entity_type="status",
                    name=status.title()
                ))
                seen_entities.add(status_id)
                entities_added += 1

            if await self.add_relationship(Relationship(
                subject=schematic_id,
                predicate="has_status",
                object=status_id
            )):
                relationships_added += 1

            # 3. Add category entity and relationship
            category = schematic.get("category", "unknown")
            category_id = f"category:{category}"
            if category_id not in seen_entities:
                await self.add_entity(Entity(
                    id=category_id,
                    entity_type="category",
                    name=category.replace("_", " ").title()
                ))
                seen_entities.add(category_id)
                entities_added += 1

            if await self.add_relationship(Relationship(
                subject=schematic_id,
                predicate="has_category",
                object=category_id
            )):
                relationships_added += 1

            # 4. Add model entity and relationship
            model = schematic.get("model", "")
            if model:
                model_id = f"model:{model}"
                if model_id not in seen_entities:
                    await self.add_entity(Entity(
                        id=model_id,
                        entity_type="model",
                        name=model
                    ))
                    seen_entities.add(model_id)
                    entities_added += 1

                if await self.add_relationship(Relationship(
                    subject=schematic_id,
                    predicate="belongs_to_model",
                    object=model_id
                )):
                    relationships_added += 1

            # 5. Extract component entities from description
            summary = schematic.get("summary", "").lower()
            component_name = schematic.get("component", "").lower()

            # Check for common component keywords
            component_keywords = {
                "hydraulic": "hydraulic_system",
                "sensor": "sensor_array",
                "motor": "motor_system",
                "battery": "power_system",
                "thermal": "thermal_system",
                "lidar": "lidar_system",
                "camera": "vision_system",
                "wireless": "communication_system",
                "safety": "safety_system",
                "gripper": "manipulation_system",
                "welding": "welding_system",
                "navigation": "navigation_system",
            }

            for keyword, component_id in component_keywords.items():
                if keyword in summary or keyword in component_name:
                    full_component_id = f"component:{component_id}"
                    if full_component_id not in seen_entities:
                        await self.add_entity(Entity(
                            id=full_component_id,
                            entity_type="component",
                            name=component_id.replace("_", " ").title()
                        ))
                        seen_entities.add(full_component_id)
                        entities_added += 1

                    if await self.add_relationship(Relationship(
                        subject=schematic_id,
                        predicate="contains",
                        object=full_component_id
                    )):
                        relationships_added += 1

            # 6. Add tag entities and relationships
            tags = schematic.get("tags", [])
            for tag in tags:
                tag_id = f"tag:{tag}"
                if tag_id not in seen_entities:
                    await self.add_entity(Entity(
                        id=tag_id,
                        entity_type="tag",
                        name=tag.replace("-", " ").title()
                    ))
                    seen_entities.add(tag_id)
                    entities_added += 1

                if await self.add_relationship(Relationship(
                    subject=schematic_id,
                    predicate="has_tag",
                    object=tag_id
                )):
                    relationships_added += 1

            # 7. Add compatibility relationships between schematics of the same model
            # (Deferred to a second pass for efficiency)

        # Second pass: Add compatibility relationships between schematics of the same model
        model_schematics: dict[str, list[str]] = {}
        for schematic in schematics:
            model = schematic.get("model", "")
            if model:
                if model not in model_schematics:
                    model_schematics[model] = []
                model_schematics[model].append(schematic["id"])

        for model, schematic_ids in model_schematics.items():
            # Create compatibility edges between schematics of the same model
            for i, sid1 in enumerate(schematic_ids):
                for sid2 in schematic_ids[i + 1:]:
                    if await self.add_relationship(Relationship(
                        subject=sid1,
                        predicate="compatible_with",
                        object=sid2
                    )):
                        relationships_added += 1
                    if await self.add_relationship(Relationship(
                        subject=sid2,
                        predicate="compatible_with",
                        object=sid1
                    )):
                        relationships_added += 1

        return {
            "entities_added": entities_added,
            "relationships_added": relationships_added,
            "total_entities": len(self._graph.nodes),
            "total_relationships": len(self._graph.edges),
        }

    async def stats(self) -> GraphStats:
        """Get statistics about the knowledge graph.

        Returns:
            GraphStats with entity counts, relationship counts, etc.
        """
        if self._conn is None:
            return GraphStats(
                entity_count=0,
                relationship_count=0,
                entity_types={},
                predicate_counts={}
            )

        cursor = self._conn.cursor()

        # Count entities by type
        cursor.execute("SELECT entity_type, COUNT(*) as count FROM entities GROUP BY entity_type")
        entity_types = {row["entity_type"]: row["count"] for row in cursor.fetchall()}

        # Count relationships by predicate
        cursor.execute("SELECT predicate, COUNT(*) as count FROM triplets GROUP BY predicate")
        predicate_counts = {row["predicate"]: row["count"] for row in cursor.fetchall()}

        return GraphStats(
            entity_count=len(self._graph.nodes),
            relationship_count=len(self._graph.edges),
            entity_types=entity_types,
            predicate_counts=predicate_counts
        )

    async def query_by_entity_type(self, entity_type: str) -> list[Entity]:
        """Get all entities of a specific type.

        Args:
            entity_type: Type to filter by (schematic, component, status, etc.)

        Returns:
            List of entities matching the type
        """
        if self._conn is None:
            return []

        cursor = self._conn.cursor()
        cursor.execute(
            "SELECT id, entity_type, name, metadata FROM entities WHERE entity_type = ?",
            (entity_type,)
        )

        entities = []
        for row in cursor.fetchall():
            metadata = json.loads(row["metadata"]) if row["metadata"] else None
            entities.append(Entity(
                id=row["id"],
                entity_type=row["entity_type"],
                name=row["name"],
                metadata=metadata
            ))

        return entities

    async def search_entities(self, query: str) -> list[Entity]:
        """Search entities by name or ID (simple keyword match).

        Args:
            query: Search query string

        Returns:
            List of entities matching the query
        """
        if self._conn is None:
            return []

        cursor = self._conn.cursor()
        query_pattern = f"%{query}%"
        cursor.execute(
            """SELECT id, entity_type, name, metadata FROM entities
               WHERE id LIKE ? OR name LIKE ?""",
            (query_pattern, query_pattern)
        )

        entities = []
        for row in cursor.fetchall():
            metadata = json.loads(row["metadata"]) if row["metadata"] else None
            entities.append(Entity(
                id=row["id"],
                entity_type=row["entity_type"],
                name=row["name"],
                metadata=metadata
            ))

        return entities

    def close(self) -> None:
        """Close the database connection."""
        if self._conn:
            self._conn.close()
            self._conn = None


# =============================================================================
# SINGLETON INSTANCE
# =============================================================================

_graph_store: Optional[GraphStore] = None


def get_graph_store() -> GraphStore:
    """Get or create the singleton GraphStore instance.

    Returns:
        GraphStore singleton
    """
    global _graph_store
    if _graph_store is None:
        _graph_store = GraphStore()
    return _graph_store


# Alias for backwards compatibility with tests
SQLiteGraphStore = GraphStore
