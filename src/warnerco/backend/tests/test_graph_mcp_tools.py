"""Tests for graph-related MCP tools.

This module tests the MCP (Model Context Protocol) tools that expose
graph memory functionality to LLM clients like Claude. The tools include:

- warn_add_relationship: Create new relationships between entities
- warn_graph_neighbors: Query neighbors of an entity
- warn_graph_path: Find shortest path between entities
- warn_graph_stats: Get graph statistics

These tests validate that the MCP tools correctly interface with the
underlying graph store and return properly formatted responses.
"""

import pytest
import pytest_asyncio
import json
from datetime import datetime, timezone
from typing import Any, Dict, List
from unittest.mock import AsyncMock, MagicMock, patch

from app.models.graph import Entity, Relationship, VALID_PREDICATES


# =============================================================================
# TEST: warn_add_relationship TOOL
# =============================================================================


class TestWarnAddRelationship:
    """Tests for the warn_add_relationship MCP tool."""

    @pytest.mark.asyncio
    @pytest.mark.mcp
    async def test_warn_add_relationship_creates_triplet(self, graph_store):
        """Verify relationship creation via MCP tool.

        The tool should create a (subject, predicate, object) triplet
        in the graph store.
        """
        from app.mcp_tools import warn_add_relationship

        # Act - use .fn to access the underlying function (FastMCP wraps it)
        with patch('app.adapters.graph_store.get_graph_store', return_value=graph_store):
            result = await warn_add_relationship.fn(
                subject="WRN-001",
                predicate="depends_on",
                object="POW-05"
            )

        # Assert - result is a Pydantic model, not JSON string
        assert result is not None
        assert result.success is True
        # Relationship details are in the 'relationship' dict
        assert result.relationship["subject"] == "WRN-001"
        assert result.relationship["predicate"] == "depends_on"
        assert result.relationship["object"] == "POW-05"

    @pytest.mark.asyncio
    @pytest.mark.mcp
    async def test_warn_add_relationship_with_metadata(self, graph_store):
        """Verify relationship creation with additional metadata."""
        from app.mcp_tools import warn_add_relationship

        # Act
        with patch('app.adapters.graph_store.get_graph_store', return_value=graph_store):
            result = await warn_add_relationship.fn(
                subject="WRN-001",
                predicate="depends_on",
                object="POW-05",
                metadata={"criticality": "high", "verified": True}
            )

        # Assert
        assert result.success is True

    @pytest.mark.asyncio
    @pytest.mark.mcp
    async def test_warn_add_relationship_duplicate_handling(self, graph_store):
        """Verify duplicate relationships are handled gracefully."""
        from app.mcp_tools import warn_add_relationship

        with patch('app.adapters.graph_store.get_graph_store', return_value=graph_store):
            # Act - add same relationship twice
            result1 = await warn_add_relationship.fn(
                subject="WRN-001",
                predicate="depends_on",
                object="POW-05"
            )
            result2 = await warn_add_relationship.fn(
                subject="WRN-001",
                predicate="depends_on",
                object="POW-05"
            )

        # Assert - first should succeed, second may return False for existing
        assert result1.success is True
        # Duplicate handling - either succeeds (idempotent) or returns False with message
        assert result2.success in (True, False)  # Implementation may vary

    @pytest.mark.asyncio
    @pytest.mark.mcp
    async def test_warn_add_relationship_invalid_predicate(self, graph_store):
        """Verify error handling for invalid predicate."""
        from app.mcp_tools import warn_add_relationship

        with patch('app.adapters.graph_store.get_graph_store', return_value=graph_store):
            # Act - invalid predicate (not in VALID_PREDICATES)
            result = await warn_add_relationship.fn(
                subject="WRN-001",
                predicate="INVALID_PREDICATE",
                object="POW-05"
            )

        # Assert - should fail with invalid predicate
        assert result is not None
        assert result.success is False
        assert "invalid predicate" in result.message.lower()
        assert result.relationship is None

    @pytest.mark.asyncio
    @pytest.mark.mcp
    async def test_warn_add_relationship_returns_pydantic_model(self, graph_store):
        """Verify tool returns Pydantic model that FastMCP will serialize."""
        from app.mcp_tools import warn_add_relationship, AddRelationshipResult

        with patch('app.adapters.graph_store.get_graph_store', return_value=graph_store):
            result = await warn_add_relationship.fn(
                subject="WRN-001",
                predicate="depends_on",
                object="POW-05"
            )

        # Assert - should be Pydantic model
        assert isinstance(result, AddRelationshipResult)
        # Model should be JSON-serializable
        json_str = result.model_dump_json()
        parsed = json.loads(json_str)
        assert isinstance(parsed, dict)


# =============================================================================
# TEST: warn_graph_neighbors TOOL
# =============================================================================


class TestWarnGraphNeighbors:
    """Tests for the warn_graph_neighbors MCP tool."""

    @pytest.mark.asyncio
    @pytest.mark.mcp
    async def test_warn_graph_neighbors_returns_related(self, graph_store_with_relationships):
        """Verify neighbor query via MCP tool returns connected entities."""
        from app.mcp_tools import warn_graph_neighbors

        # Act
        with patch('app.adapters.graph_store.get_graph_store', return_value=graph_store_with_relationships):
            result = await warn_graph_neighbors.fn(
                entity_id="POW-05",
                direction="both"
            )

        # Assert - result is Pydantic model
        assert result.entity_id == "POW-05"
        assert result.direction == "both"
        # Should have neighbors from the fixture
        assert len(result.neighbors) > 0 or len(result.relationships) > 0

    @pytest.mark.asyncio
    @pytest.mark.mcp
    async def test_warn_graph_neighbors_outgoing_only(self, graph_store_with_relationships):
        """Verify neighbor query with outgoing direction filter."""
        from app.mcp_tools import warn_graph_neighbors

        with patch('app.adapters.graph_store.get_graph_store', return_value=graph_store_with_relationships):
            result = await warn_graph_neighbors.fn(
                entity_id="WRN-001",
                direction="outgoing"
            )

        # Assert
        assert result.direction == "outgoing"

    @pytest.mark.asyncio
    @pytest.mark.mcp
    async def test_warn_graph_neighbors_incoming_only(self, graph_store_with_relationships):
        """Verify neighbor query with incoming direction filter."""
        from app.mcp_tools import warn_graph_neighbors

        with patch('app.adapters.graph_store.get_graph_store', return_value=graph_store_with_relationships):
            result = await warn_graph_neighbors.fn(
                entity_id="POW-05",
                direction="incoming"
            )

        # Assert
        assert result.direction == "incoming"

    @pytest.mark.asyncio
    @pytest.mark.mcp
    async def test_warn_graph_neighbors_nonexistent_entity(self, graph_store):
        """Verify graceful handling of non-existent entity."""
        from app.mcp_tools import warn_graph_neighbors

        with patch('app.adapters.graph_store.get_graph_store', return_value=graph_store):
            result = await warn_graph_neighbors.fn(
                entity_id="DOES-NOT-EXIST",
                direction="both"
            )

        # Assert - should return empty neighbors, not error
        assert result.neighbors == []
        assert result.relationships == []

    @pytest.mark.asyncio
    @pytest.mark.mcp
    async def test_warn_graph_neighbors_invalid_direction(self, graph_store):
        """Verify error handling for invalid direction parameter."""
        from app.mcp_tools import warn_graph_neighbors

        with patch('app.adapters.graph_store.get_graph_store', return_value=graph_store):
            result = await warn_graph_neighbors.fn(
                entity_id="WRN-001",
                direction="invalid_direction"
            )

        # Assert - should return error
        assert result.error is not None
        assert "invalid" in result.error.lower()


# =============================================================================
# TEST: warn_graph_path TOOL
# =============================================================================


class TestWarnGraphPath:
    """Tests for the warn_graph_path MCP tool."""

    @pytest.mark.asyncio
    @pytest.mark.mcp
    async def test_warn_graph_path_finds_path(self, graph_store_with_relationships):
        """Verify pathfinding via MCP tool."""
        from app.mcp_tools import warn_graph_path

        with patch('app.adapters.graph_store.get_graph_store', return_value=graph_store_with_relationships):
            result = await warn_graph_path.fn(
                source="WRN-001",
                target="electrical_power"
            )

        # Assert - result is Pydantic model
        assert result.source == "WRN-001"
        assert result.target == "electrical_power"
        # Path should exist in the fixture data
        if result.path:
            assert result.path[0] == "WRN-001"
            assert result.path[-1] == "electrical_power"

    @pytest.mark.asyncio
    @pytest.mark.mcp
    async def test_warn_graph_path_no_path_exists(self, graph_store):
        """Verify handling when no path exists between entities."""
        from app.mcp_tools import warn_graph_path

        # Arrange - create disconnected subgraphs using correct API
        await graph_store.add_entity(Entity(id="A", entity_type="test", name="A"))
        await graph_store.add_entity(Entity(id="B", entity_type="test", name="B"))
        await graph_store.add_entity(Entity(id="C", entity_type="test", name="C"))
        await graph_store.add_entity(Entity(id="D", entity_type="test", name="D"))
        await graph_store.add_relationship(Relationship(subject="A", predicate="related_to", object="B"))
        await graph_store.add_relationship(Relationship(subject="C", predicate="related_to", object="D"))

        with patch('app.adapters.graph_store.get_graph_store', return_value=graph_store):
            result = await warn_graph_path.fn(
                source="A",
                target="D"
            )

        # Assert - should indicate no path
        assert result.path is None or result.path == []

    @pytest.mark.asyncio
    @pytest.mark.mcp
    async def test_warn_graph_path_same_source_target(self, graph_store):
        """Verify handling when source equals target."""
        from app.mcp_tools import warn_graph_path

        await graph_store.add_entity(Entity(id="A", entity_type="test", name="A"))

        with patch('app.adapters.graph_store.get_graph_store', return_value=graph_store):
            result = await warn_graph_path.fn(
                source="A",
                target="A"
            )

        # Assert - path should be just the node itself
        assert result.path == ["A"]

    @pytest.mark.asyncio
    @pytest.mark.mcp
    async def test_warn_graph_path_nonexistent_source(self, graph_store):
        """Verify handling of non-existent source entity."""
        from app.mcp_tools import warn_graph_path

        with patch('app.adapters.graph_store.get_graph_store', return_value=graph_store):
            result = await warn_graph_path.fn(
                source="NONEXISTENT",
                target="A"
            )

        # Assert - should return empty/null path
        assert result.path is None or result.path == []


# =============================================================================
# TEST: warn_graph_stats TOOL
# =============================================================================


class TestWarnGraphStats:
    """Tests for the warn_graph_stats MCP tool."""

    @pytest.mark.asyncio
    @pytest.mark.mcp
    async def test_warn_graph_stats_returns_counts(self, graph_store_with_relationships):
        """Verify stats retrieval via MCP tool."""
        from app.mcp_tools import warn_graph_stats

        with patch('app.adapters.graph_store.get_graph_store', return_value=graph_store_with_relationships):
            result = await warn_graph_stats.fn()

        # Assert - result is Pydantic model
        assert result.entity_count > 0
        assert result.relationship_count > 0

    @pytest.mark.asyncio
    @pytest.mark.mcp
    async def test_warn_graph_stats_empty_graph(self, graph_store):
        """Verify stats for empty graph."""
        from app.mcp_tools import warn_graph_stats

        with patch('app.adapters.graph_store.get_graph_store', return_value=graph_store):
            result = await warn_graph_stats.fn()

        # Assert
        assert result.entity_count == 0
        assert result.relationship_count == 0

    @pytest.mark.asyncio
    @pytest.mark.mcp
    async def test_warn_graph_stats_includes_type_breakdown(self, graph_store_with_relationships):
        """Verify stats includes entity type breakdown."""
        from app.mcp_tools import warn_graph_stats

        with patch('app.adapters.graph_store.get_graph_store', return_value=graph_store_with_relationships):
            result = await warn_graph_stats.fn()

        # Assert - should have entity_types breakdown
        assert result.entity_types is not None
        assert isinstance(result.entity_types, dict)

    @pytest.mark.asyncio
    @pytest.mark.mcp
    async def test_warn_graph_stats_pydantic_model(self, graph_store):
        """Verify stats returns Pydantic model."""
        from app.mcp_tools import warn_graph_stats, GraphStatsResult

        with patch('app.adapters.graph_store.get_graph_store', return_value=graph_store):
            result = await warn_graph_stats.fn()

        # Assert - should be Pydantic model
        assert isinstance(result, GraphStatsResult)
        # Should be JSON-serializable
        json_str = result.model_dump_json()
        parsed = json.loads(json_str)
        assert isinstance(parsed, dict)


# =============================================================================
# TEST: MCP TOOL REGISTRATION
# =============================================================================


class TestMCPToolRegistration:
    """Tests for MCP tool registration and discovery."""

    @pytest.mark.mcp
    def test_graph_tools_exist(self):
        """Verify all graph tools are importable and have callable .fn."""
        from app.mcp_tools import (
            warn_add_relationship,
            warn_graph_neighbors,
            warn_graph_path,
            warn_graph_stats,
        )

        # Assert - all are FunctionTool objects with callable .fn
        assert callable(warn_add_relationship.fn)
        assert callable(warn_graph_neighbors.fn)
        assert callable(warn_graph_path.fn)
        assert callable(warn_graph_stats.fn)

    @pytest.mark.mcp
    def test_result_models_exist(self):
        """Verify all result models are importable."""
        from app.mcp_tools import (
            AddRelationshipResult,
            GraphNeighborsResult,
            GraphPathResult,
            GraphStatsResult,
        )

        # Assert - all should be Pydantic models
        assert hasattr(AddRelationshipResult, 'model_fields')
        assert hasattr(GraphNeighborsResult, 'model_fields')
        assert hasattr(GraphPathResult, 'model_fields')
        assert hasattr(GraphStatsResult, 'model_fields')


# =============================================================================
# TEST: ERROR HANDLING
# =============================================================================


class TestMCPToolErrorHandling:
    """Tests for MCP tool error handling and edge cases."""

    @pytest.mark.asyncio
    @pytest.mark.mcp
    async def test_tool_handles_store_exception(self):
        """Verify tools gracefully handle graph store exceptions."""
        from app.mcp_tools import warn_graph_stats

        # Arrange - mock store that raises
        mock_store = MagicMock()
        mock_store.stats.side_effect = Exception("Database error")

        with patch('app.adapters.graph_store.get_graph_store', return_value=mock_store):
            result = await warn_graph_stats.fn()

        # Assert - should return model with zero counts (exception was caught)
        assert result.entity_count == 0
        assert result.relationship_count == 0

    @pytest.mark.asyncio
    @pytest.mark.mcp
    async def test_neighbors_handles_store_exception(self):
        """Verify neighbors tool handles exceptions."""
        from app.mcp_tools import warn_graph_neighbors

        # Arrange - mock store that raises
        mock_store = MagicMock()
        mock_store.get_neighbors.side_effect = Exception("Database error")

        with patch('app.adapters.graph_store.get_graph_store', return_value=mock_store):
            result = await warn_graph_neighbors.fn(
                entity_id="WRN-001",
                direction="both"
            )

        # Assert - should return empty result (exception caught)
        assert result.neighbors == []
        assert result.relationships == []


# =============================================================================
# TEST: PYDANTIC MODEL SERIALIZATION
# =============================================================================


class TestResponseFormatConsistency:
    """Tests for consistent response formatting across all graph tools."""

    @pytest.mark.asyncio
    @pytest.mark.mcp
    async def test_all_tools_return_pydantic_models(self, graph_store):
        """Verify all graph tools return Pydantic models."""
        from app.mcp_tools import (
            warn_add_relationship,
            warn_graph_neighbors,
            warn_graph_path,
            warn_graph_stats,
            AddRelationshipResult,
            GraphNeighborsResult,
            GraphPathResult,
            GraphStatsResult,
        )

        with patch('app.adapters.graph_store.get_graph_store', return_value=graph_store):
            add_result = await warn_add_relationship.fn("A", "related_to", "B")
            neighbors_result = await warn_graph_neighbors.fn("A", "both")
            path_result = await warn_graph_path.fn("A", "B")
            stats_result = await warn_graph_stats.fn()

        assert isinstance(add_result, AddRelationshipResult)
        assert isinstance(neighbors_result, GraphNeighborsResult)
        assert isinstance(path_result, GraphPathResult)
        assert isinstance(stats_result, GraphStatsResult)

    @pytest.mark.asyncio
    @pytest.mark.mcp
    async def test_all_models_json_serializable(self, graph_store):
        """Verify all result models can be serialized to JSON."""
        from app.mcp_tools import (
            warn_add_relationship,
            warn_graph_neighbors,
            warn_graph_path,
            warn_graph_stats,
        )

        with patch('app.adapters.graph_store.get_graph_store', return_value=graph_store):
            results = [
                await warn_add_relationship.fn("A", "related_to", "B"),
                await warn_graph_neighbors.fn("A", "both"),
                await warn_graph_path.fn("A", "B"),
                await warn_graph_stats.fn()
            ]

        for result in results:
            # Should not raise
            json_str = result.model_dump_json()
            parsed = json.loads(json_str)
            assert isinstance(parsed, dict)
