"""Unit tests for the SQLite + NetworkX graph store.

This module tests the graph store adapter that provides:
- Entity and relationship (triplet) management
- SQLite persistence with UNIQUE constraints
- NetworkX graph construction for pathfinding
- Statistics and neighbor queries

These tests validate the graph_store.py implementation.
"""

import pytest
import pytest_asyncio
import tempfile
import os
from pathlib import Path
from typing import List

from app.models.graph import Entity, Relationship


# =============================================================================
# TEST: ENTITY MANAGEMENT
# =============================================================================


class TestEntityManagement:
    """Tests for entity creation and retrieval."""

    @pytest.mark.asyncio
    async def test_add_entity(self, graph_store):
        """Verify entities can be added and retrieved.

        Entities are nodes in the knowledge graph, representing robots,
        components, resources, or concepts extracted from schematics.
        """
        # Act
        entity = Entity(
            id="WRN-001",
            entity_type="robot",
            name="WRN-001",
            metadata={"model": "WC-100", "status": "active"}
        )
        result = await graph_store.add_entity(entity)

        # Assert
        assert result is True
        retrieved = await graph_store.get_entity("WRN-001")
        assert retrieved is not None
        assert retrieved.name == "WRN-001"
        assert retrieved.entity_type == "robot"
        assert retrieved.metadata["model"] == "WC-100"

    @pytest.mark.asyncio
    async def test_add_entity_without_metadata(self, graph_store):
        """Verify entities can be added with minimal information."""
        # Act
        entity = Entity(
            id="simple-entity",
            entity_type="concept",
            name="Simple Entity"
        )
        result = await graph_store.add_entity(entity)

        # Assert
        retrieved = await graph_store.get_entity("simple-entity")
        assert retrieved is not None
        assert retrieved.name == "Simple Entity"
        assert retrieved.entity_type == "concept"

    @pytest.mark.asyncio
    async def test_get_nonexistent_entity(self, graph_store):
        """Verify None is returned for non-existent entities."""
        # Act
        entity = await graph_store.get_entity("does-not-exist")

        # Assert
        assert entity is None

    @pytest.mark.asyncio
    async def test_add_entity_replaces_existing(self, graph_store):
        """Verify adding entity with same ID replaces existing (INSERT OR REPLACE)."""
        # Arrange
        entity1 = Entity(
            id="WRN-001",
            entity_type="robot",
            name="Original Name",
            metadata={"status": "active"}
        )
        await graph_store.add_entity(entity1)

        # Act - add entity with same ID but different data
        entity2 = Entity(
            id="WRN-001",
            entity_type="robot",
            name="Updated Name",
            metadata={"status": "maintenance", "priority": "high"}
        )
        await graph_store.add_entity(entity2)

        # Assert
        retrieved = await graph_store.get_entity("WRN-001")
        assert retrieved.name == "Updated Name"
        assert retrieved.metadata["status"] == "maintenance"
        assert retrieved.metadata["priority"] == "high"

    @pytest.mark.asyncio
    async def test_query_entities_by_type(self, graph_store, sample_entities):
        """Verify entities can be filtered by type."""
        # Arrange
        for entity_data in sample_entities:
            entity = Entity(
                id=entity_data["name"],
                entity_type=entity_data["entity_type"],
                name=entity_data["name"]
            )
            await graph_store.add_entity(entity)

        # Act
        robots = await graph_store.query_by_entity_type("robot")

        # Assert
        assert len(robots) == 2  # WRN-001 and WRN-002
        assert all(e.entity_type == "robot" for e in robots)


# =============================================================================
# TEST: RELATIONSHIP MANAGEMENT
# =============================================================================


class TestRelationshipManagement:
    """Tests for relationship (triplet) creation and queries."""

    @pytest.mark.asyncio
    async def test_add_relationship(self, graph_store):
        """Verify relationships (triplets) can be added.

        Relationships are edges in the knowledge graph, connecting
        entities with typed predicates (e.g., depends_on, contains).
        """
        # Arrange
        await graph_store.add_entity(Entity(id="WRN-001", entity_type="robot", name="WRN-001"))
        await graph_store.add_entity(Entity(id="POW-05", entity_type="power_supply", name="POW-05"))

        # Act
        rel = Relationship(
            subject="WRN-001",
            predicate="depends_on",
            object="POW-05",
            metadata={"criticality": "high"}
        )
        success = await graph_store.add_relationship(rel)

        # Assert
        assert success is True
        relationships = await graph_store.get_related("WRN-001")
        assert len(relationships) == 1
        assert relationships[0].subject == "WRN-001"
        assert relationships[0].predicate == "depends_on"
        assert relationships[0].object == "POW-05"

    @pytest.mark.asyncio
    async def test_add_relationship_creates_edges_without_entities(self, graph_store):
        """Verify relationships can be added even without pre-creating entities.

        The graph store should still create edges in NetworkX even if
        entities aren't explicitly created first.
        """
        # Act - add relationship without pre-creating entities
        rel = Relationship(
            subject="NEW-ROBOT",
            predicate="contains",
            object="NEW-SENSOR"
        )
        success = await graph_store.add_relationship(rel)

        # Assert
        assert success is True
        # The relationship exists in NetworkX graph
        nx_graph = graph_store.get_nx_graph()
        assert nx_graph.has_edge("NEW-ROBOT", "NEW-SENSOR")

    @pytest.mark.asyncio
    async def test_duplicate_relationship_ignored(self, graph_store):
        """Verify UNIQUE constraint works - no duplicate relationships.

        Adding the same (subject, predicate, object) triplet multiple times
        should not create duplicates in the database.
        """
        # Arrange
        await graph_store.add_entity(Entity(id="WRN-001", entity_type="robot", name="WRN-001"))
        await graph_store.add_entity(Entity(id="POW-05", entity_type="power_supply", name="POW-05"))

        # Act - add same relationship twice
        rel = Relationship(subject="WRN-001", predicate="depends_on", object="POW-05")
        await graph_store.add_relationship(rel)
        await graph_store.add_relationship(rel)
        await graph_store.add_relationship(rel)

        # Assert - should only have one relationship
        relationships = await graph_store.get_related("WRN-001")
        matching = [r for r in relationships
                   if r.predicate == "depends_on" and r.object == "POW-05"]
        assert len(matching) == 1

    @pytest.mark.asyncio
    async def test_get_related_outgoing(self, graph_store, sample_relationships):
        """Verify get_related returns objects for a subject.

        Given a subject entity, return all objects it relates to.
        """
        # Arrange
        for subj, pred, obj in sample_relationships:
            rel = Relationship(subject=subj, predicate=pred.lower(), object=obj)
            await graph_store.add_relationship(rel)

        # Act
        related = await graph_store.get_related("WRN-001")

        # Assert
        assert len(related) == 2  # POW-05 and SENSOR-01
        related_objects = [r.object for r in related]
        assert "POW-05" in related_objects
        assert "SENSOR-01" in related_objects

    @pytest.mark.asyncio
    async def test_get_subjects_incoming(self, graph_store, sample_relationships):
        """Verify reverse lookup works - get subjects pointing to an entity.

        Given an object entity, return all subjects that relate to it.
        """
        # Arrange
        for subj, pred, obj in sample_relationships:
            rel = Relationship(subject=subj, predicate=pred.lower(), object=obj)
            await graph_store.add_relationship(rel)

        # Act
        related = await graph_store.get_subjects("POW-05")

        # Assert
        assert len(related) == 2  # WRN-001 and WRN-002
        related_subjects = [r.subject for r in related]
        assert "WRN-001" in related_subjects
        assert "WRN-002" in related_subjects

    @pytest.mark.asyncio
    async def test_get_related_by_predicate(self, graph_store, sample_relationships):
        """Verify filtering relationships by predicate type."""
        # Arrange
        for subj, pred, obj in sample_relationships:
            rel = Relationship(subject=subj, predicate=pred.lower(), object=obj)
            await graph_store.add_relationship(rel)

        # Act
        depends = await graph_store.get_related("WRN-001", predicate="depends_on")

        # Assert
        assert len(depends) == 1
        assert depends[0].object == "POW-05"
        assert depends[0].predicate == "depends_on"


# =============================================================================
# TEST: NEIGHBOR QUERIES
# =============================================================================


class TestNeighborQueries:
    """Tests for bidirectional neighbor discovery."""

    @pytest.mark.asyncio
    async def test_get_neighbors_both_directions(self, graph_store_with_relationships):
        """Verify bidirectional neighbor query returns all connected nodes.

        Neighbors include both incoming and outgoing connections.
        """
        store = graph_store_with_relationships

        # Act
        neighbors = await store.get_neighbors("POW-05", direction="both")

        # Assert
        # Incoming: WRN-001, WRN-002 (depends_on)
        # Outgoing: electrical_power (related_to)
        assert "WRN-001" in neighbors
        assert "WRN-002" in neighbors
        assert "electrical_power" in neighbors

    @pytest.mark.asyncio
    async def test_get_neighbors_outgoing_only(self, graph_store_with_relationships):
        """Verify outgoing neighbor discovery."""
        store = graph_store_with_relationships

        # Act
        neighbors = await store.get_neighbors("WRN-001", direction="outgoing")

        # Assert - should find POW-05 and SENSOR-01
        assert "POW-05" in neighbors
        assert "SENSOR-01" in neighbors

    @pytest.mark.asyncio
    async def test_get_neighbors_empty_for_isolated_node(self, graph_store):
        """Verify empty list returned for nodes with no connections."""
        # Arrange
        await graph_store.add_entity(Entity(id="isolated-node", entity_type="concept", name="Isolated"))

        # Act
        neighbors = await graph_store.get_neighbors("isolated-node", direction="both")

        # Assert
        assert neighbors == []


# =============================================================================
# TEST: PATHFINDING
# =============================================================================


class TestPathfinding:
    """Tests for NetworkX-based shortest path discovery."""

    @pytest.mark.asyncio
    async def test_shortest_path_exists(self, graph_store, complex_graph_relationships):
        """Verify NetworkX pathfinding finds shortest path.

        Graph: A -> B -> C -> D (length 3)
               A -> E -> D (length 2)

        Shortest path from A to D should be [A, E, D].
        """
        # Arrange
        for subj, pred, obj in complex_graph_relationships:
            rel = Relationship(subject=subj, predicate=pred.lower(), object=obj)
            await graph_store.add_relationship(rel)

        # Act
        path = await graph_store.shortest_path("A", "D")

        # Assert
        assert path is not None
        assert len(path) == 3  # A -> E -> D is shorter than A -> B -> C -> D
        assert path[0] == "A"
        assert path[-1] == "D"

    @pytest.mark.asyncio
    async def test_shortest_path_linear(self, graph_store):
        """Verify pathfinding works for linear paths.

        Setup: A -> B -> C -> D
        Query: shortest_path(A, D) should return [A, B, C, D]
        """
        # Arrange
        await graph_store.add_relationship(Relationship(subject="A", predicate="related_to", object="B"))
        await graph_store.add_relationship(Relationship(subject="B", predicate="related_to", object="C"))
        await graph_store.add_relationship(Relationship(subject="C", predicate="related_to", object="D"))

        # Act
        path = await graph_store.shortest_path("A", "D")

        # Assert
        assert path == ["A", "B", "C", "D"]

    @pytest.mark.asyncio
    async def test_shortest_path_no_connection(self, graph_store):
        """Verify None returned when no path exists between entities."""
        # Arrange - two disconnected subgraphs
        await graph_store.add_relationship(Relationship(subject="A", predicate="related_to", object="B"))
        await graph_store.add_relationship(Relationship(subject="C", predicate="related_to", object="D"))

        # Act
        path = await graph_store.shortest_path("A", "D")

        # Assert
        assert path is None

    @pytest.mark.asyncio
    async def test_shortest_path_same_node(self, graph_store):
        """Verify pathfinding handles source == target."""
        # Arrange
        await graph_store.add_entity(Entity(id="A", entity_type="concept", name="A"))

        # Act
        path = await graph_store.shortest_path("A", "A")

        # Assert
        assert path == ["A"]

    @pytest.mark.asyncio
    async def test_shortest_path_nonexistent_nodes(self, graph_store):
        """Verify graceful handling of non-existent nodes."""
        # Act
        path = await graph_store.shortest_path("nonexistent1", "nonexistent2")

        # Assert
        assert path is None


# =============================================================================
# TEST: NETWORKX GRAPH CONSTRUCTION
# =============================================================================


class TestNetworkXGraph:
    """Tests for NetworkX DiGraph construction from stored relationships."""

    @pytest.mark.asyncio
    async def test_get_nx_graph_structure(self, graph_store_with_relationships):
        """Verify NetworkX DiGraph is correctly constructed from relationships."""
        store = graph_store_with_relationships

        # Act - get_nx_graph is SYNC, not async
        nx_graph = store.get_nx_graph()

        # Assert
        assert nx_graph is not None
        # Check node count
        assert nx_graph.number_of_nodes() > 0
        # Check edge count
        assert nx_graph.number_of_edges() > 0
        # Verify specific edge exists
        assert nx_graph.has_edge("WRN-001", "POW-05")

    @pytest.mark.asyncio
    async def test_get_nx_graph_edge_attributes(self, graph_store):
        """Verify edge attributes (predicates) are preserved in NetworkX graph."""
        # Arrange
        rel = Relationship(
            subject="WRN-001",
            predicate="depends_on",
            object="POW-05",
            metadata={"criticality": "high"}
        )
        await graph_store.add_relationship(rel)

        # Act - get_nx_graph is SYNC
        nx_graph = graph_store.get_nx_graph()

        # Assert
        edge_data = nx_graph.get_edge_data("WRN-001", "POW-05")
        assert edge_data is not None
        assert edge_data.get("predicate") == "depends_on"

    @pytest.mark.asyncio
    async def test_get_nx_graph_empty(self, graph_store):
        """Verify empty graph is handled correctly."""
        # Act - get_nx_graph is SYNC
        nx_graph = graph_store.get_nx_graph()

        # Assert
        assert nx_graph is not None
        assert nx_graph.number_of_nodes() == 0
        assert nx_graph.number_of_edges() == 0


# =============================================================================
# TEST: STATISTICS
# =============================================================================


class TestStatistics:
    """Tests for graph statistics reporting."""

    @pytest.mark.asyncio
    async def test_stats_returns_correct_counts(self, graph_store_with_relationships):
        """Verify stats returns accurate entity and relationship counts."""
        store = graph_store_with_relationships

        # Act
        stats = await store.stats()

        # Assert - stats returns GraphStats model
        assert stats is not None
        assert stats.entity_count > 0
        assert stats.relationship_count >= 6  # From fixture
        assert stats.entity_types is not None
        assert stats.predicate_counts is not None

    @pytest.mark.asyncio
    async def test_stats_empty_store(self, graph_store):
        """Verify stats handles empty graph correctly."""
        # Act
        stats = await graph_store.stats()

        # Assert
        assert stats.entity_count == 0
        assert stats.relationship_count == 0

    @pytest.mark.asyncio
    async def test_stats_entity_type_breakdown(self, graph_store, sample_entities):
        """Verify entity type breakdown in stats."""
        # Arrange
        for entity_data in sample_entities:
            entity = Entity(
                id=entity_data["name"],
                entity_type=entity_data["entity_type"],
                name=entity_data["name"]
            )
            await graph_store.add_entity(entity)

        # Act
        stats = await graph_store.stats()

        # Assert
        assert stats.entity_types["robot"] == 2
        assert stats.entity_types["power_supply"] == 1
        assert stats.entity_types["component"] == 1
        assert stats.entity_types["resource"] == 2


# =============================================================================
# TEST: SCHEMATIC INDEXING
# =============================================================================


class TestSchematicIndexing:
    """Tests for automatic entity/relationship extraction from schematics."""

    @pytest.mark.asyncio
    async def test_index_schematics_creates_entities(self, graph_store, sample_schematics):
        """Verify indexing creates entity nodes for each schematic."""
        # Act
        await graph_store.index_schematics(sample_schematics)

        # Assert
        for schematic in sample_schematics:
            entity = await graph_store.get_entity(schematic["id"])
            assert entity is not None
            assert entity.entity_type == "schematic"

    @pytest.mark.asyncio
    async def test_index_schematics_extracts_categories(self, graph_store, sample_schematics):
        """Verify indexing creates category entities and relationships."""
        # Act
        await graph_store.index_schematics(sample_schematics)

        # Assert - check category entities exist (format is category:sensors)
        sensors_entity = await graph_store.get_entity("category:sensors")
        assert sensors_entity is not None
        assert sensors_entity.entity_type == "category"

        # Assert - check has_category relationships
        wrn001_relationships = await graph_store.get_related("WRN-001")
        category_rels = [r for r in wrn001_relationships if r.predicate == "has_category"]
        assert len(category_rels) > 0

    @pytest.mark.asyncio
    async def test_index_schematics_extracts_models(self, graph_store, sample_schematics):
        """Verify indexing creates model entities and relationships."""
        # Act
        await graph_store.index_schematics(sample_schematics)

        # Assert - check model entities exist (format is model:WC-100)
        wc100_entity = await graph_store.get_entity("model:WC-100")
        assert wc100_entity is not None
        assert wc100_entity.entity_type == "model"

        # Assert - check belongs_to_model relationships
        wrn001_relationships = await graph_store.get_related("WRN-001")
        model_rels = [r for r in wrn001_relationships if r.predicate == "belongs_to_model"]
        assert len(model_rels) > 0

    @pytest.mark.asyncio
    async def test_index_schematics_extracts_tags(self, graph_store, sample_schematics):
        """Verify indexing creates tag entities and relationships."""
        # Act
        await graph_store.index_schematics(sample_schematics)

        # Assert - check a tag entity exists (format is tag:industrial)
        industrial_entity = await graph_store.get_entity("tag:industrial")
        assert industrial_entity is not None
        assert industrial_entity.entity_type == "tag"

    @pytest.mark.asyncio
    async def test_index_schematics_idempotent(self, graph_store, sample_schematics):
        """Verify re-indexing doesn't create duplicates."""
        # Act - index twice
        await graph_store.index_schematics(sample_schematics)
        stats_first = await graph_store.stats()

        await graph_store.index_schematics(sample_schematics)
        stats_second = await graph_store.stats()

        # Assert - counts should be the same
        assert stats_first.entity_count == stats_second.entity_count
        assert stats_first.relationship_count == stats_second.relationship_count


# =============================================================================
# TEST: PERSISTENCE
# =============================================================================


class TestPersistence:
    """Tests for SQLite persistence across store instances."""

    @pytest.mark.asyncio
    async def test_data_persists_across_instances(self, temp_db_path):
        """Verify data survives closing and reopening the store."""
        from app.adapters.graph_store import GraphStore

        # Arrange - create store, add data, close
        store1 = GraphStore(db_path=temp_db_path)
        await store1.add_entity(Entity(id="persistent-entity", entity_type="test", name="Persistent"))
        await store1.add_relationship(Relationship(subject="A", predicate="related_to", object="B"))
        store1.close()

        # Act - reopen store
        store2 = GraphStore(db_path=temp_db_path)

        # Assert - data should be there
        entity = await store2.get_entity("persistent-entity")
        assert entity is not None

        relationships = await store2.get_related("A")
        assert len(relationships) == 1

        store2.close()

    @pytest.mark.asyncio
    async def test_concurrent_writes(self, graph_store):
        """Verify concurrent writes don't cause corruption.

        This is a basic concurrency test - full stress testing would
        require more sophisticated tooling.
        """
        import asyncio

        # Act - add many entities concurrently
        async def add_entity(i):
            entity = Entity(id=f"concurrent-{i}", entity_type="test", name=f"Concurrent {i}")
            await graph_store.add_entity(entity)

        tasks = [add_entity(i) for i in range(50)]
        await asyncio.gather(*tasks)

        # Assert - all entities should exist
        stats = await graph_store.stats()
        assert stats.entity_count >= 50


# =============================================================================
# TEST: EDGE CASES
# =============================================================================


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    @pytest.mark.asyncio
    async def test_special_characters_in_names(self, graph_store):
        """Verify entities with special characters are handled correctly."""
        # Act
        await graph_store.add_entity(Entity(id="entity/with/slashes", entity_type="test", name="Slashes"))
        await graph_store.add_entity(Entity(id="entity:with:colons", entity_type="test", name="Colons"))
        await graph_store.add_entity(Entity(id="entity with spaces", entity_type="test", name="Spaces"))

        # Assert
        assert await graph_store.get_entity("entity/with/slashes") is not None
        assert await graph_store.get_entity("entity:with:colons") is not None
        assert await graph_store.get_entity("entity with spaces") is not None

    @pytest.mark.asyncio
    async def test_unicode_in_names(self, graph_store):
        """Verify unicode entity names are supported."""
        # Act
        await graph_store.add_entity(Entity(id="robot_unicode", entity_type="test", name="Robot Unicode"))
        await graph_store.add_entity(Entity(id="entity_chinese", entity_type="test", name="Entity Chinese"))

        # Assert
        assert await graph_store.get_entity("robot_unicode") is not None
        assert await graph_store.get_entity("entity_chinese") is not None

    @pytest.mark.asyncio
    async def test_very_long_name(self, graph_store):
        """Verify very long entity names are handled."""
        long_name = "x" * 1000

        # Act
        await graph_store.add_entity(Entity(id=long_name, entity_type="test", name=long_name))

        # Assert
        entity = await graph_store.get_entity(long_name)
        assert entity is not None
        assert entity.name == long_name

    @pytest.mark.asyncio
    async def test_search_entities(self, graph_store):
        """Verify search_entities finds entities by name or ID."""
        # Arrange
        await graph_store.add_entity(Entity(id="WRN-001", entity_type="robot", name="Atlas Heavy Lifter"))
        await graph_store.add_entity(Entity(id="WRN-002", entity_type="robot", name="Precision Welder"))

        # Act
        results = await graph_store.search_entities("Atlas")

        # Assert
        assert len(results) >= 1
        assert any(e.id == "WRN-001" for e in results)
