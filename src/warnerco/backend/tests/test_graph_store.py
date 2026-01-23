"""Unit tests for the SQLite + NetworkX graph store.

This module tests the graph store adapter that provides:
- Entity and relationship (triplet) management
- SQLite persistence with UNIQUE constraints
- NetworkX graph construction for pathfinding
- Statistics and neighbor queries

These tests are designed to validate the graph_store.py implementation
that will be created by the implementation agent.
"""

import pytest
import pytest_asyncio
import tempfile
import os
from pathlib import Path
from typing import List


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
        entity_id = await graph_store.add_entity(
            name="WRN-001",
            entity_type="robot",
            properties={"model": "WC-100", "status": "active"}
        )

        # Assert
        assert entity_id is not None
        entity = await graph_store.get_entity("WRN-001")
        assert entity is not None
        assert entity["name"] == "WRN-001"
        assert entity["entity_type"] == "robot"
        assert entity["properties"]["model"] == "WC-100"

    @pytest.mark.asyncio
    async def test_add_entity_without_properties(self, graph_store):
        """Verify entities can be added with minimal information."""
        # Act
        entity_id = await graph_store.add_entity(
            name="simple-entity",
            entity_type="concept"
        )

        # Assert
        entity = await graph_store.get_entity("simple-entity")
        assert entity is not None
        assert entity["name"] == "simple-entity"
        assert entity["entity_type"] == "concept"

    @pytest.mark.asyncio
    async def test_get_nonexistent_entity(self, graph_store):
        """Verify None is returned for non-existent entities."""
        # Act
        entity = await graph_store.get_entity("does-not-exist")

        # Assert
        assert entity is None

    @pytest.mark.asyncio
    async def test_update_entity_properties(self, graph_store):
        """Verify entity properties can be updated."""
        # Arrange
        await graph_store.add_entity(
            name="WRN-001",
            entity_type="robot",
            properties={"status": "active"}
        )

        # Act
        await graph_store.update_entity(
            name="WRN-001",
            properties={"status": "maintenance", "priority": "high"}
        )

        # Assert
        entity = await graph_store.get_entity("WRN-001")
        assert entity["properties"]["status"] == "maintenance"
        assert entity["properties"]["priority"] == "high"

    @pytest.mark.asyncio
    async def test_list_entities_by_type(self, graph_store, sample_entities):
        """Verify entities can be filtered by type."""
        # Arrange
        for entity in sample_entities:
            await graph_store.add_entity(
                name=entity["name"],
                entity_type=entity["entity_type"]
            )

        # Act
        robots = await graph_store.list_entities(entity_type="robot")

        # Assert
        assert len(robots) == 2  # WRN-001 and WRN-002
        assert all(e["entity_type"] == "robot" for e in robots)


# =============================================================================
# TEST: RELATIONSHIP MANAGEMENT
# =============================================================================


class TestRelationshipManagement:
    """Tests for relationship (triplet) creation and queries."""

    @pytest.mark.asyncio
    async def test_add_relationship(self, graph_store):
        """Verify relationships (triplets) can be added.

        Relationships are edges in the knowledge graph, connecting
        entities with typed predicates (e.g., DEPENDS_ON, HAS_COMPONENT).
        """
        # Arrange
        await graph_store.add_entity("WRN-001", "robot")
        await graph_store.add_entity("POW-05", "power_supply")

        # Act
        success = await graph_store.add_relationship(
            subject="WRN-001",
            predicate="DEPENDS_ON",
            obj="POW-05",
            properties={"criticality": "high"}
        )

        # Assert
        assert success is True
        relationships = await graph_store.get_relationships("WRN-001")
        assert len(relationships) == 1
        assert relationships[0]["subject"] == "WRN-001"
        assert relationships[0]["predicate"] == "DEPENDS_ON"
        assert relationships[0]["object"] == "POW-05"

    @pytest.mark.asyncio
    async def test_add_relationship_auto_creates_entities(self, graph_store):
        """Verify relationships auto-create entities if they don't exist.

        This simplifies usage - callers don't need to explicitly create
        entities before adding relationships.
        """
        # Act - add relationship without pre-creating entities
        success = await graph_store.add_relationship(
            subject="NEW-ROBOT",
            predicate="HAS_COMPONENT",
            obj="NEW-SENSOR"
        )

        # Assert
        assert success is True
        # Entities should be auto-created
        robot = await graph_store.get_entity("NEW-ROBOT")
        sensor = await graph_store.get_entity("NEW-SENSOR")
        assert robot is not None
        assert sensor is not None

    @pytest.mark.asyncio
    async def test_duplicate_relationship_ignored(self, graph_store):
        """Verify UNIQUE constraint works - no duplicate relationships.

        Adding the same (subject, predicate, object) triplet multiple times
        should not create duplicates in the database.
        """
        # Arrange
        await graph_store.add_entity("WRN-001", "robot")
        await graph_store.add_entity("POW-05", "power_supply")

        # Act - add same relationship twice
        await graph_store.add_relationship("WRN-001", "DEPENDS_ON", "POW-05")
        await graph_store.add_relationship("WRN-001", "DEPENDS_ON", "POW-05")
        await graph_store.add_relationship("WRN-001", "DEPENDS_ON", "POW-05")

        # Assert - should only have one relationship
        relationships = await graph_store.get_relationships("WRN-001")
        matching = [r for r in relationships
                   if r["predicate"] == "DEPENDS_ON" and r["object"] == "POW-05"]
        assert len(matching) == 1

    @pytest.mark.asyncio
    async def test_get_related_outgoing(self, graph_store, sample_relationships):
        """Verify get_related returns objects for a subject.

        Given a subject entity, return all objects it relates to.
        """
        # Arrange
        for subj, pred, obj in sample_relationships:
            await graph_store.add_relationship(subj, pred, obj)

        # Act
        related = await graph_store.get_related(
            entity="WRN-001",
            direction="outgoing"
        )

        # Assert
        assert len(related) == 2  # POW-05 and SENSOR-01
        related_names = [r["entity"] for r in related]
        assert "POW-05" in related_names
        assert "SENSOR-01" in related_names

    @pytest.mark.asyncio
    async def test_get_related_incoming(self, graph_store, sample_relationships):
        """Verify reverse lookup works - get subjects pointing to an entity.

        Given an object entity, return all subjects that relate to it.
        """
        # Arrange
        for subj, pred, obj in sample_relationships:
            await graph_store.add_relationship(subj, pred, obj)

        # Act
        related = await graph_store.get_related(
            entity="POW-05",
            direction="incoming"
        )

        # Assert
        assert len(related) == 2  # WRN-001 and WRN-002
        related_names = [r["entity"] for r in related]
        assert "WRN-001" in related_names
        assert "WRN-002" in related_names

    @pytest.mark.asyncio
    async def test_get_related_by_predicate(self, graph_store, sample_relationships):
        """Verify filtering relationships by predicate type."""
        # Arrange
        for subj, pred, obj in sample_relationships:
            await graph_store.add_relationship(subj, pred, obj)

        # Act
        depends = await graph_store.get_related(
            entity="WRN-001",
            direction="outgoing",
            predicate="DEPENDS_ON"
        )

        # Assert
        assert len(depends) == 1
        assert depends[0]["entity"] == "POW-05"
        assert depends[0]["predicate"] == "DEPENDS_ON"


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
        neighbors = await store.get_neighbors(
            entity="POW-05",
            direction="both"
        )

        # Assert
        neighbor_names = [n["entity"] for n in neighbors]
        # Incoming: WRN-001, WRN-002 (DEPENDS_ON)
        # Outgoing: electrical_power (PROVIDES)
        assert "WRN-001" in neighbor_names
        assert "WRN-002" in neighbor_names
        assert "electrical_power" in neighbor_names

    @pytest.mark.asyncio
    async def test_get_neighbors_with_depth(self, graph_store_with_relationships):
        """Verify multi-hop neighbor discovery with depth parameter.

        With depth=2, should find neighbors of neighbors.
        """
        store = graph_store_with_relationships

        # Act
        neighbors = await store.get_neighbors(
            entity="WRN-001",
            direction="outgoing",
            depth=2
        )

        # Assert - should find POW-05 at depth 1 and electrical_power at depth 2
        neighbor_names = [n["entity"] for n in neighbors]
        assert "POW-05" in neighbor_names
        assert "electrical_power" in neighbor_names

    @pytest.mark.asyncio
    async def test_get_neighbors_empty_for_isolated_node(self, graph_store):
        """Verify empty list returned for nodes with no connections."""
        # Arrange
        await graph_store.add_entity("isolated-node", "concept")

        # Act
        neighbors = await graph_store.get_neighbors(
            entity="isolated-node",
            direction="both"
        )

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
            await graph_store.add_relationship(subj, pred, obj)

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
        await graph_store.add_relationship("A", "CONNECTS_TO", "B")
        await graph_store.add_relationship("B", "CONNECTS_TO", "C")
        await graph_store.add_relationship("C", "CONNECTS_TO", "D")

        # Act
        path = await graph_store.shortest_path("A", "D")

        # Assert
        assert path == ["A", "B", "C", "D"]

    @pytest.mark.asyncio
    async def test_shortest_path_no_connection(self, graph_store):
        """Verify None returned when no path exists between entities."""
        # Arrange - two disconnected subgraphs
        await graph_store.add_relationship("A", "CONNECTS_TO", "B")
        await graph_store.add_relationship("C", "CONNECTS_TO", "D")

        # Act
        path = await graph_store.shortest_path("A", "D")

        # Assert
        assert path is None

    @pytest.mark.asyncio
    async def test_shortest_path_same_node(self, graph_store):
        """Verify pathfinding handles source == target."""
        # Arrange
        await graph_store.add_entity("A", "concept")

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

        # Act
        nx_graph = await store.get_nx_graph()

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
        await graph_store.add_relationship(
            "WRN-001", "DEPENDS_ON", "POW-05",
            properties={"criticality": "high"}
        )

        # Act
        nx_graph = await store.get_nx_graph()

        # Assert
        edge_data = nx_graph.get_edge_data("WRN-001", "POW-05")
        assert edge_data is not None
        assert edge_data.get("predicate") == "DEPENDS_ON"

    @pytest.mark.asyncio
    async def test_get_nx_graph_empty(self, graph_store):
        """Verify empty graph is handled correctly."""
        # Act
        nx_graph = await graph_store.get_nx_graph()

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

        # Assert
        assert stats is not None
        assert stats["entity_count"] > 0
        assert stats["relationship_count"] == 6  # From fixture
        assert "entity_types" in stats
        assert "predicate_types" in stats

    @pytest.mark.asyncio
    async def test_stats_empty_store(self, graph_store):
        """Verify stats handles empty graph correctly."""
        # Act
        stats = await graph_store.stats()

        # Assert
        assert stats["entity_count"] == 0
        assert stats["relationship_count"] == 0

    @pytest.mark.asyncio
    async def test_stats_entity_type_breakdown(self, graph_store, sample_entities):
        """Verify entity type breakdown in stats."""
        # Arrange
        for entity in sample_entities:
            await graph_store.add_entity(
                name=entity["name"],
                entity_type=entity["entity_type"]
            )

        # Act
        stats = await graph_store.stats()

        # Assert
        assert stats["entity_types"]["robot"] == 2
        assert stats["entity_types"]["power_supply"] == 1
        assert stats["entity_types"]["component"] == 1
        assert stats["entity_types"]["resource"] == 2


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
            assert entity["entity_type"] == "schematic"

    @pytest.mark.asyncio
    async def test_index_schematics_extracts_categories(self, graph_store, sample_schematics):
        """Verify indexing creates category entities and relationships."""
        # Act
        await graph_store.index_schematics(sample_schematics)

        # Assert - check category entities exist
        sensors_entity = await graph_store.get_entity("sensors")
        assert sensors_entity is not None
        assert sensors_entity["entity_type"] == "category"

        # Assert - check HAS_CATEGORY relationships
        wrn001_relationships = await graph_store.get_relationships("WRN-001")
        category_rels = [r for r in wrn001_relationships if r["predicate"] == "HAS_CATEGORY"]
        assert len(category_rels) > 0

    @pytest.mark.asyncio
    async def test_index_schematics_extracts_models(self, graph_store, sample_schematics):
        """Verify indexing creates model entities and relationships."""
        # Act
        await graph_store.index_schematics(sample_schematics)

        # Assert - check model entities exist
        wc100_entity = await graph_store.get_entity("WC-100")
        assert wc100_entity is not None
        assert wc100_entity["entity_type"] == "model"

        # Assert - check IS_MODEL relationships
        wrn001_relationships = await graph_store.get_relationships("WRN-001")
        model_rels = [r for r in wrn001_relationships if r["predicate"] == "IS_MODEL"]
        assert len(model_rels) > 0

    @pytest.mark.asyncio
    async def test_index_schematics_extracts_tags(self, graph_store, sample_schematics):
        """Verify indexing creates tag entities and relationships."""
        # Act
        await graph_store.index_schematics(sample_schematics)

        # Assert - check a tag entity exists
        industrial_entity = await graph_store.get_entity("industrial")
        assert industrial_entity is not None
        assert industrial_entity["entity_type"] == "tag"

    @pytest.mark.asyncio
    async def test_index_schematics_idempotent(self, graph_store, sample_schematics):
        """Verify re-indexing doesn't create duplicates."""
        # Act - index twice
        await graph_store.index_schematics(sample_schematics)
        stats_first = await graph_store.stats()

        await graph_store.index_schematics(sample_schematics)
        stats_second = await graph_store.stats()

        # Assert - counts should be the same
        assert stats_first["entity_count"] == stats_second["entity_count"]
        assert stats_first["relationship_count"] == stats_second["relationship_count"]


# =============================================================================
# TEST: PERSISTENCE
# =============================================================================


class TestPersistence:
    """Tests for SQLite persistence across store instances."""

    @pytest.mark.asyncio
    async def test_data_persists_across_instances(self, temp_db_path):
        """Verify data survives closing and reopening the store."""
        from app.adapters.graph_store import SQLiteGraphStore

        # Arrange - create store, add data, close
        store1 = SQLiteGraphStore(db_path=temp_db_path)
        await store1.initialize()
        await store1.add_entity("persistent-entity", "test")
        await store1.add_relationship("A", "LINKS_TO", "B")
        await store1.close()

        # Act - reopen store
        store2 = SQLiteGraphStore(db_path=temp_db_path)
        await store2.initialize()

        # Assert - data should be there
        entity = await store2.get_entity("persistent-entity")
        assert entity is not None

        relationships = await store2.get_relationships("A")
        assert len(relationships) == 1

        await store2.close()

    @pytest.mark.asyncio
    async def test_concurrent_writes(self, graph_store):
        """Verify concurrent writes don't cause corruption.

        This is a basic concurrency test - full stress testing would
        require more sophisticated tooling.
        """
        import asyncio

        # Act - add many entities concurrently
        async def add_entity(i):
            await graph_store.add_entity(f"concurrent-{i}", "test")

        tasks = [add_entity(i) for i in range(50)]
        await asyncio.gather(*tasks)

        # Assert - all entities should exist
        stats = await graph_store.stats()
        assert stats["entity_count"] >= 50


# =============================================================================
# TEST: EDGE CASES
# =============================================================================


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    @pytest.mark.asyncio
    async def test_special_characters_in_names(self, graph_store):
        """Verify entities with special characters are handled correctly."""
        # Act
        await graph_store.add_entity("entity/with/slashes", "test")
        await graph_store.add_entity("entity:with:colons", "test")
        await graph_store.add_entity("entity with spaces", "test")

        # Assert
        assert await graph_store.get_entity("entity/with/slashes") is not None
        assert await graph_store.get_entity("entity:with:colons") is not None
        assert await graph_store.get_entity("entity with spaces") is not None

    @pytest.mark.asyncio
    async def test_unicode_in_names(self, graph_store):
        """Verify unicode entity names are supported."""
        # Act
        await graph_store.add_entity("robot_", "test")
        await graph_store.add_entity("entity", "test")

        # Assert
        assert await graph_store.get_entity("robot_") is not None
        assert await graph_store.get_entity("entity") is not None

    @pytest.mark.asyncio
    async def test_empty_name_rejected(self, graph_store):
        """Verify empty entity names are rejected."""
        # Act & Assert
        with pytest.raises(ValueError):
            await graph_store.add_entity("", "test")

    @pytest.mark.asyncio
    async def test_none_name_rejected(self, graph_store):
        """Verify None entity names are rejected."""
        # Act & Assert
        with pytest.raises((ValueError, TypeError)):
            await graph_store.add_entity(None, "test")

    @pytest.mark.asyncio
    async def test_very_long_name(self, graph_store):
        """Verify very long entity names are handled."""
        long_name = "x" * 1000

        # Act
        await graph_store.add_entity(long_name, "test")

        # Assert
        entity = await graph_store.get_entity(long_name)
        assert entity is not None
        assert entity["name"] == long_name
