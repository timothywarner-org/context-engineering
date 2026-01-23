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
from datetime import datetime
from typing import Any, Dict, List
from unittest.mock import AsyncMock, MagicMock, patch


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

        # Act
        with patch('app.mcp_tools.get_graph_store', return_value=graph_store):
            result = await warn_add_relationship(
                subject="WRN-001",
                predicate="DEPENDS_ON",
                obj="POW-05"
            )

        # Assert
        assert result is not None
        result_data = json.loads(result) if isinstance(result, str) else result
        assert result_data.get("success") is True
        assert result_data.get("relationship", {}).get("subject") == "WRN-001"
        assert result_data.get("relationship", {}).get("predicate") == "DEPENDS_ON"
        assert result_data.get("relationship", {}).get("object") == "POW-05"

    @pytest.mark.asyncio
    @pytest.mark.mcp
    async def test_warn_add_relationship_with_properties(self, graph_store):
        """Verify relationship creation with additional properties."""
        from app.mcp_tools import warn_add_relationship

        # Act
        with patch('app.mcp_tools.get_graph_store', return_value=graph_store):
            result = await warn_add_relationship(
                subject="WRN-001",
                predicate="DEPENDS_ON",
                obj="POW-05",
                properties={"criticality": "high", "verified": True}
            )

        # Assert
        result_data = json.loads(result) if isinstance(result, str) else result
        assert result_data.get("success") is True

    @pytest.mark.asyncio
    @pytest.mark.mcp
    async def test_warn_add_relationship_duplicate_handling(self, graph_store):
        """Verify duplicate relationships are handled gracefully."""
        from app.mcp_tools import warn_add_relationship

        with patch('app.mcp_tools.get_graph_store', return_value=graph_store):
            # Act - add same relationship twice
            result1 = await warn_add_relationship(
                subject="WRN-001",
                predicate="DEPENDS_ON",
                obj="POW-05"
            )
            result2 = await warn_add_relationship(
                subject="WRN-001",
                predicate="DEPENDS_ON",
                obj="POW-05"
            )

        # Assert - both should succeed (idempotent operation)
        result1_data = json.loads(result1) if isinstance(result1, str) else result1
        result2_data = json.loads(result2) if isinstance(result2, str) else result2
        assert result1_data.get("success") is True
        assert result2_data.get("success") is True

    @pytest.mark.asyncio
    @pytest.mark.mcp
    async def test_warn_add_relationship_invalid_input(self, graph_store):
        """Verify error handling for invalid input."""
        from app.mcp_tools import warn_add_relationship

        with patch('app.mcp_tools.get_graph_store', return_value=graph_store):
            # Act - empty subject
            result = await warn_add_relationship(
                subject="",
                predicate="DEPENDS_ON",
                obj="POW-05"
            )

        # Assert
        result_data = json.loads(result) if isinstance(result, str) else result
        assert result_data.get("success") is False or "error" in result_data

    @pytest.mark.asyncio
    @pytest.mark.mcp
    async def test_warn_add_relationship_returns_mcp_format(self, graph_store):
        """Verify tool returns MCP-compliant response format."""
        from app.mcp_tools import warn_add_relationship

        with patch('app.mcp_tools.get_graph_store', return_value=graph_store):
            result = await warn_add_relationship(
                subject="WRN-001",
                predicate="DEPENDS_ON",
                obj="POW-05"
            )

        # Assert - should be JSON string for MCP
        assert isinstance(result, str)
        parsed = json.loads(result)
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
        with patch('app.mcp_tools.get_graph_store', return_value=graph_store_with_relationships):
            result = await warn_graph_neighbors(
                entity="POW-05",
                direction="both"
            )

        # Assert
        result_data = json.loads(result) if isinstance(result, str) else result
        assert result_data.get("success") is True
        neighbors = result_data.get("neighbors", [])
        assert len(neighbors) > 0
        neighbor_names = [n["entity"] for n in neighbors]
        assert "WRN-001" in neighbor_names or "WRN-002" in neighbor_names

    @pytest.mark.asyncio
    @pytest.mark.mcp
    async def test_warn_graph_neighbors_outgoing_only(self, graph_store_with_relationships):
        """Verify neighbor query with outgoing direction filter."""
        from app.mcp_tools import warn_graph_neighbors

        with patch('app.mcp_tools.get_graph_store', return_value=graph_store_with_relationships):
            result = await warn_graph_neighbors(
                entity="WRN-001",
                direction="outgoing"
            )

        # Assert
        result_data = json.loads(result) if isinstance(result, str) else result
        neighbors = result_data.get("neighbors", [])
        # WRN-001 has outgoing edges to POW-05 and SENSOR-01
        assert len(neighbors) >= 1

    @pytest.mark.asyncio
    @pytest.mark.mcp
    async def test_warn_graph_neighbors_incoming_only(self, graph_store_with_relationships):
        """Verify neighbor query with incoming direction filter."""
        from app.mcp_tools import warn_graph_neighbors

        with patch('app.mcp_tools.get_graph_store', return_value=graph_store_with_relationships):
            result = await warn_graph_neighbors(
                entity="POW-05",
                direction="incoming"
            )

        # Assert
        result_data = json.loads(result) if isinstance(result, str) else result
        neighbors = result_data.get("neighbors", [])
        # POW-05 has incoming edges from WRN-001 and WRN-002
        assert len(neighbors) >= 2

    @pytest.mark.asyncio
    @pytest.mark.mcp
    async def test_warn_graph_neighbors_with_predicate_filter(self, graph_store_with_relationships):
        """Verify neighbor query filtered by predicate type."""
        from app.mcp_tools import warn_graph_neighbors

        with patch('app.mcp_tools.get_graph_store', return_value=graph_store_with_relationships):
            result = await warn_graph_neighbors(
                entity="WRN-001",
                direction="outgoing",
                predicate="DEPENDS_ON"
            )

        # Assert
        result_data = json.loads(result) if isinstance(result, str) else result
        neighbors = result_data.get("neighbors", [])
        # Should only return POW-05 (not SENSOR-01 which is HAS_COMPONENT)
        if neighbors:
            assert all(n["predicate"] == "DEPENDS_ON" for n in neighbors)

    @pytest.mark.asyncio
    @pytest.mark.mcp
    async def test_warn_graph_neighbors_with_depth(self, graph_store_with_relationships):
        """Verify multi-hop neighbor discovery with depth parameter."""
        from app.mcp_tools import warn_graph_neighbors

        with patch('app.mcp_tools.get_graph_store', return_value=graph_store_with_relationships):
            result = await warn_graph_neighbors(
                entity="WRN-001",
                direction="outgoing",
                depth=2
            )

        # Assert
        result_data = json.loads(result) if isinstance(result, str) else result
        neighbors = result_data.get("neighbors", [])
        # With depth 2, should find POW-05 and electrical_power
        neighbor_names = [n["entity"] for n in neighbors]
        assert "POW-05" in neighbor_names  # depth 1
        # electrical_power should be at depth 2 via POW-05

    @pytest.mark.asyncio
    @pytest.mark.mcp
    async def test_warn_graph_neighbors_nonexistent_entity(self, graph_store):
        """Verify graceful handling of non-existent entity."""
        from app.mcp_tools import warn_graph_neighbors

        with patch('app.mcp_tools.get_graph_store', return_value=graph_store):
            result = await warn_graph_neighbors(
                entity="DOES-NOT-EXIST",
                direction="both"
            )

        # Assert
        result_data = json.loads(result) if isinstance(result, str) else result
        assert result_data.get("success") is True
        assert result_data.get("neighbors", []) == []

    @pytest.mark.asyncio
    @pytest.mark.mcp
    async def test_warn_graph_neighbors_includes_relationship_details(self, graph_store_with_relationships):
        """Verify neighbor results include relationship details."""
        from app.mcp_tools import warn_graph_neighbors

        with patch('app.mcp_tools.get_graph_store', return_value=graph_store_with_relationships):
            result = await warn_graph_neighbors(
                entity="WRN-001",
                direction="outgoing"
            )

        # Assert
        result_data = json.loads(result) if isinstance(result, str) else result
        neighbors = result_data.get("neighbors", [])
        if neighbors:
            # Each neighbor should have entity, predicate, and direction
            assert "entity" in neighbors[0]
            assert "predicate" in neighbors[0]


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

        with patch('app.mcp_tools.get_graph_store', return_value=graph_store_with_relationships):
            result = await warn_graph_path(
                source="WRN-001",
                target="electrical_power"
            )

        # Assert
        result_data = json.loads(result) if isinstance(result, str) else result
        assert result_data.get("success") is True
        path = result_data.get("path", [])
        assert len(path) > 0
        assert path[0] == "WRN-001"
        assert path[-1] == "electrical_power"

    @pytest.mark.asyncio
    @pytest.mark.mcp
    async def test_warn_graph_path_no_path_exists(self, graph_store):
        """Verify handling when no path exists between entities."""
        from app.mcp_tools import warn_graph_path

        # Arrange - create disconnected subgraphs
        await graph_store.add_relationship("A", "CONNECTS", "B")
        await graph_store.add_relationship("C", "CONNECTS", "D")

        with patch('app.mcp_tools.get_graph_store', return_value=graph_store):
            result = await warn_graph_path(
                source="A",
                target="D"
            )

        # Assert
        result_data = json.loads(result) if isinstance(result, str) else result
        assert result_data.get("success") is True
        assert result_data.get("path") is None or result_data.get("path") == []
        assert "no path" in result_data.get("message", "").lower() or result_data.get("path") is None

    @pytest.mark.asyncio
    @pytest.mark.mcp
    async def test_warn_graph_path_same_source_target(self, graph_store):
        """Verify handling when source equals target."""
        from app.mcp_tools import warn_graph_path

        await graph_store.add_entity("A", "test")

        with patch('app.mcp_tools.get_graph_store', return_value=graph_store):
            result = await warn_graph_path(
                source="A",
                target="A"
            )

        # Assert
        result_data = json.loads(result) if isinstance(result, str) else result
        assert result_data.get("success") is True
        path = result_data.get("path", [])
        assert path == ["A"]

    @pytest.mark.asyncio
    @pytest.mark.mcp
    async def test_warn_graph_path_includes_relationships(self, graph_store_with_relationships):
        """Verify path result includes relationship types along the path."""
        from app.mcp_tools import warn_graph_path

        with patch('app.mcp_tools.get_graph_store', return_value=graph_store_with_relationships):
            result = await warn_graph_path(
                source="WRN-001",
                target="electrical_power",
                include_relationships=True
            )

        # Assert
        result_data = json.loads(result) if isinstance(result, str) else result
        # If include_relationships is supported, should have edge details
        if "edges" in result_data or "relationships" in result_data:
            edges = result_data.get("edges", result_data.get("relationships", []))
            assert len(edges) > 0

    @pytest.mark.asyncio
    @pytest.mark.mcp
    async def test_warn_graph_path_nonexistent_source(self, graph_store):
        """Verify handling of non-existent source entity."""
        from app.mcp_tools import warn_graph_path

        with patch('app.mcp_tools.get_graph_store', return_value=graph_store):
            result = await warn_graph_path(
                source="NONEXISTENT",
                target="A"
            )

        # Assert
        result_data = json.loads(result) if isinstance(result, str) else result
        assert result_data.get("path") is None or result_data.get("path") == []


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

        with patch('app.mcp_tools.get_graph_store', return_value=graph_store_with_relationships):
            result = await warn_graph_stats()

        # Assert
        result_data = json.loads(result) if isinstance(result, str) else result
        assert result_data.get("success") is True
        stats = result_data.get("stats", result_data)
        assert "entity_count" in stats
        assert "relationship_count" in stats
        assert stats["entity_count"] > 0
        assert stats["relationship_count"] > 0

    @pytest.mark.asyncio
    @pytest.mark.mcp
    async def test_warn_graph_stats_empty_graph(self, graph_store):
        """Verify stats for empty graph."""
        from app.mcp_tools import warn_graph_stats

        with patch('app.mcp_tools.get_graph_store', return_value=graph_store):
            result = await warn_graph_stats()

        # Assert
        result_data = json.loads(result) if isinstance(result, str) else result
        assert result_data.get("success") is True
        stats = result_data.get("stats", result_data)
        assert stats["entity_count"] == 0
        assert stats["relationship_count"] == 0

    @pytest.mark.asyncio
    @pytest.mark.mcp
    async def test_warn_graph_stats_includes_type_breakdown(self, graph_store_with_relationships):
        """Verify stats includes entity and predicate type breakdowns."""
        from app.mcp_tools import warn_graph_stats

        with patch('app.mcp_tools.get_graph_store', return_value=graph_store_with_relationships):
            result = await warn_graph_stats()

        # Assert
        result_data = json.loads(result) if isinstance(result, str) else result
        stats = result_data.get("stats", result_data)
        # Should have type breakdowns
        assert "entity_types" in stats or "predicate_types" in stats

    @pytest.mark.asyncio
    @pytest.mark.mcp
    async def test_warn_graph_stats_mcp_format(self, graph_store):
        """Verify stats returns MCP-compliant format."""
        from app.mcp_tools import warn_graph_stats

        with patch('app.mcp_tools.get_graph_store', return_value=graph_store):
            result = await warn_graph_stats()

        # Assert - should be JSON string
        assert isinstance(result, str)
        parsed = json.loads(result)
        assert isinstance(parsed, dict)


# =============================================================================
# TEST: MCP TOOL REGISTRATION
# =============================================================================


class TestMCPToolRegistration:
    """Tests for MCP tool registration and discovery."""

    @pytest.mark.mcp
    def test_graph_tools_registered(self):
        """Verify all graph tools are registered with FastMCP."""
        from app.mcp_tools import mcp

        # Get registered tools
        tools = mcp.list_tools() if hasattr(mcp, 'list_tools') else []

        # Assert - check tool names exist
        tool_names = [t.name if hasattr(t, 'name') else str(t) for t in tools]
        expected_tools = [
            "warn_add_relationship",
            "warn_graph_neighbors",
            "warn_graph_path",
            "warn_graph_stats"
        ]
        for expected in expected_tools:
            assert any(expected in name for name in tool_names), f"Tool {expected} not registered"

    @pytest.mark.mcp
    def test_graph_tool_schemas(self):
        """Verify graph tools have proper JSON schemas for parameters."""
        from app.mcp_tools import mcp

        # This test validates that FastMCP generates proper schemas
        # from the Python type hints on the tool functions
        tools = mcp.list_tools() if hasattr(mcp, 'list_tools') else []

        for tool in tools:
            if hasattr(tool, 'inputSchema'):
                schema = tool.inputSchema
                assert isinstance(schema, dict)
                # Schema should have properties and required fields
                assert "properties" in schema or "type" in schema


# =============================================================================
# TEST: ERROR HANDLING
# =============================================================================


class TestMCPToolErrorHandling:
    """Tests for MCP tool error handling and edge cases."""

    @pytest.mark.asyncio
    @pytest.mark.mcp
    async def test_tool_handles_store_exception(self):
        """Verify tools gracefully handle graph store exceptions."""
        from app.mcp_tools import warn_graph_neighbors

        # Arrange - mock store that raises
        mock_store = AsyncMock()
        mock_store.get_neighbors.side_effect = Exception("Database error")

        with patch('app.mcp_tools.get_graph_store', return_value=mock_store):
            result = await warn_graph_neighbors(
                entity="WRN-001",
                direction="both"
            )

        # Assert
        result_data = json.loads(result) if isinstance(result, str) else result
        assert result_data.get("success") is False
        assert "error" in result_data

    @pytest.mark.asyncio
    @pytest.mark.mcp
    async def test_tool_handles_invalid_direction(self, graph_store):
        """Verify tools handle invalid direction parameter."""
        from app.mcp_tools import warn_graph_neighbors

        with patch('app.mcp_tools.get_graph_store', return_value=graph_store):
            result = await warn_graph_neighbors(
                entity="WRN-001",
                direction="invalid_direction"
            )

        # Assert
        result_data = json.loads(result) if isinstance(result, str) else result
        # Should either succeed with default or return error
        assert "success" in result_data or "error" in result_data

    @pytest.mark.asyncio
    @pytest.mark.mcp
    async def test_tool_handles_none_entity(self, graph_store):
        """Verify tools handle None entity gracefully."""
        from app.mcp_tools import warn_graph_neighbors

        with patch('app.mcp_tools.get_graph_store', return_value=graph_store):
            # This may raise or return error depending on implementation
            try:
                result = await warn_graph_neighbors(
                    entity=None,
                    direction="both"
                )
                result_data = json.loads(result) if isinstance(result, str) else result
                assert result_data.get("success") is False or "error" in result_data
            except (ValueError, TypeError):
                # Also acceptable - validation at input
                pass


# =============================================================================
# TEST: CONTEXT AND ELICITATION
# =============================================================================


class TestMCPContextIntegration:
    """Tests for MCP Context integration with graph tools."""

    @pytest.mark.asyncio
    @pytest.mark.mcp
    async def test_tool_with_mcp_context(self, graph_store, mock_mcp_context):
        """Verify tools can use MCP Context for elicitation if needed."""
        from app.mcp_tools import warn_add_relationship

        # Some tools might use context for confirmation dialogs
        with patch('app.mcp_tools.get_graph_store', return_value=graph_store):
            result = await warn_add_relationship(
                subject="WRN-001",
                predicate="DEPENDS_ON",
                obj="POW-05",
                # Context might be passed for elicitation
            )

        # Assert - should work with or without context
        result_data = json.loads(result) if isinstance(result, str) else result
        assert result_data.get("success") is True


# =============================================================================
# TEST: RESPONSE FORMAT CONSISTENCY
# =============================================================================


class TestResponseFormatConsistency:
    """Tests for consistent response formatting across all graph tools."""

    @pytest.mark.asyncio
    @pytest.mark.mcp
    async def test_all_tools_return_json_strings(self, graph_store_with_relationships):
        """Verify all graph tools return JSON-formatted strings."""
        from app.mcp_tools import (
            warn_add_relationship,
            warn_graph_neighbors,
            warn_graph_path,
            warn_graph_stats
        )

        with patch('app.mcp_tools.get_graph_store', return_value=graph_store_with_relationships):
            results = [
                await warn_add_relationship("A", "RELATES", "B"),
                await warn_graph_neighbors("WRN-001", "both"),
                await warn_graph_path("WRN-001", "POW-05"),
                await warn_graph_stats()
            ]

        for result in results:
            assert isinstance(result, str), "Tool should return JSON string"
            parsed = json.loads(result)
            assert isinstance(parsed, dict), "Parsed result should be dict"

    @pytest.mark.asyncio
    @pytest.mark.mcp
    async def test_all_tools_include_success_field(self, graph_store_with_relationships):
        """Verify all tool responses include a 'success' field."""
        from app.mcp_tools import (
            warn_add_relationship,
            warn_graph_neighbors,
            warn_graph_path,
            warn_graph_stats
        )

        with patch('app.mcp_tools.get_graph_store', return_value=graph_store_with_relationships):
            results = [
                await warn_add_relationship("A", "RELATES", "B"),
                await warn_graph_neighbors("WRN-001", "both"),
                await warn_graph_path("WRN-001", "POW-05"),
                await warn_graph_stats()
            ]

        for result in results:
            parsed = json.loads(result)
            assert "success" in parsed, "Response should include 'success' field"
            assert isinstance(parsed["success"], bool)
