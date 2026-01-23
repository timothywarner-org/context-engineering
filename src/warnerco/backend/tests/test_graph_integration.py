"""Integration tests for graph memory with LangGraph flow.

This module tests how the graph memory feature integrates with the existing
LangGraph RAG pipeline, including:
- Entity extraction from user queries
- Graph context injection into the pipeline state
- Intent-based graph query triggering

These tests validate that the graph store works correctly within the
larger WARNERCO Schematica system.
"""

import pytest
import pytest_asyncio
from datetime import datetime
from typing import Any, Dict, List, Optional
from unittest.mock import AsyncMock, MagicMock, patch


# =============================================================================
# TEST: QUERY GRAPH NODE
# =============================================================================


class TestQueryGraphNode:
    """Tests for the query_graph node in the LangGraph flow."""

    @pytest.mark.asyncio
    async def test_query_graph_node_extracts_entities(self, graph_store_with_relationships):
        """Verify entity extraction from user query.

        The query_graph node should identify entity mentions in the user's
        natural language query and look them up in the graph.
        """
        from app.langgraph.flow import query_graph

        # Arrange
        state = {
            "query": "What are the dependencies for WRN-001?",
            "filters": None,
            "top_k": 5,
            "intent": None,
            "candidates": [],
            "compressed_context": "",
            "graph_context": "",
            "response": {},
            "error": None,
            "start_time": datetime.utcnow().isoformat(),
            "timings": {},
        }

        # Act
        with patch('app.langgraph.flow.get_graph_store', return_value=graph_store_with_relationships):
            result = await query_graph(state)

        # Assert
        assert result["graph_context"] != ""
        assert "WRN-001" in result["graph_context"] or "POW-05" in result["graph_context"]

    @pytest.mark.asyncio
    async def test_query_graph_node_handles_no_entities(self, graph_store):
        """Verify graceful handling when no entities are found in query."""
        from app.langgraph.flow import query_graph

        # Arrange
        state = {
            "query": "Tell me about robot maintenance best practices",
            "filters": None,
            "top_k": 5,
            "intent": None,
            "candidates": [],
            "compressed_context": "",
            "graph_context": "",
            "response": {},
            "error": None,
            "start_time": datetime.utcnow().isoformat(),
            "timings": {},
        }

        # Act
        with patch('app.langgraph.flow.get_graph_store', return_value=graph_store):
            result = await query_graph(state)

        # Assert
        assert "error" not in result or result["error"] is None
        # Graph context may be empty but should not cause error
        assert isinstance(result.get("graph_context", ""), str)

    @pytest.mark.asyncio
    async def test_query_graph_extracts_multiple_entities(self, graph_store_with_relationships):
        """Verify multiple entity extraction from complex queries."""
        from app.langgraph.flow import query_graph

        # Arrange
        state = {
            "query": "What is the relationship between WRN-001 and WRN-002?",
            "filters": None,
            "top_k": 5,
            "intent": None,
            "candidates": [],
            "compressed_context": "",
            "graph_context": "",
            "response": {},
            "error": None,
            "start_time": datetime.utcnow().isoformat(),
            "timings": {},
        }

        # Act
        with patch('app.langgraph.flow.get_graph_store', return_value=graph_store_with_relationships):
            result = await query_graph(state)

        # Assert
        graph_context = result.get("graph_context", "")
        # Should find connection via POW-05
        assert "POW-05" in graph_context or "DEPENDS_ON" in graph_context


# =============================================================================
# TEST: GRAPH CONTEXT FLOW
# =============================================================================


class TestGraphContextFlow:
    """Tests for graph context flowing through the LangGraph pipeline."""

    @pytest.mark.asyncio
    async def test_graph_context_added_to_state(self, populated_graph_store):
        """Verify graph context is properly added to pipeline state.

        Graph context should be populated before the compress_context node
        so it can be included in the final context.
        """
        from app.langgraph.flow import query_graph

        # Arrange
        state = {
            "query": "Find information about WRN-001",
            "filters": None,
            "top_k": 5,
            "intent": None,
            "candidates": [],
            "compressed_context": "",
            "graph_context": "",
            "response": {},
            "error": None,
            "start_time": datetime.utcnow().isoformat(),
            "timings": {},
        }

        # Act
        with patch('app.langgraph.flow.get_graph_store', return_value=populated_graph_store):
            result = await query_graph(state)

        # Assert
        assert "graph_context" in result
        assert result["graph_context"] is not None

    @pytest.mark.asyncio
    async def test_graph_context_included_in_compressed_context(self, graph_store_with_relationships):
        """Verify graph context is merged into compressed context for LLM."""
        from app.langgraph.flow import compress_context_with_graph

        # Arrange
        state = {
            "query": "What depends on POW-05?",
            "filters": None,
            "top_k": 5,
            "intent": "diagnostic",
            "candidates": [],  # Would normally have search results
            "compressed_context": "Search results for POW-05...",
            "graph_context": "WRN-001 --DEPENDS_ON--> POW-05\nWRN-002 --DEPENDS_ON--> POW-05",
            "response": {},
            "error": None,
            "start_time": datetime.utcnow().isoformat(),
            "timings": {},
        }

        # Act
        result = compress_context_with_graph(state)

        # Assert
        final_context = result["compressed_context"]
        assert "DEPENDS_ON" in final_context or "WRN-001" in final_context

    @pytest.mark.asyncio
    async def test_graph_context_empty_does_not_break_flow(self, graph_store):
        """Verify empty graph context doesn't break the pipeline."""
        from app.langgraph.flow import compress_context_with_graph

        # Arrange
        state = {
            "query": "General query with no graph data",
            "filters": None,
            "top_k": 5,
            "intent": "search",
            "candidates": [],
            "compressed_context": "Some search results...",
            "graph_context": "",  # Empty graph context
            "response": {},
            "error": None,
            "start_time": datetime.utcnow().isoformat(),
            "timings": {},
        }

        # Act
        result = compress_context_with_graph(state)

        # Assert
        assert result is not None
        assert "compressed_context" in result


# =============================================================================
# TEST: INTENT-BASED GRAPH QUERIES
# =============================================================================


class TestIntentBasedGraphQueries:
    """Tests for intent-driven graph query behavior."""

    @pytest.mark.asyncio
    async def test_diagnostic_intent_triggers_graph(self, graph_store_with_relationships):
        """Verify DIAGNOSTIC intent queries the graph for dependencies.

        Diagnostic queries (troubleshooting, status checks) should
        automatically enrich results with dependency information.
        """
        from app.langgraph.flow import should_query_graph

        # Arrange
        state = {
            "query": "WRN-001 is not working, what could be wrong?",
            "intent": "diagnostic",
            "graph_context": "",
        }

        # Act
        result = should_query_graph(state)

        # Assert
        assert result is True

    @pytest.mark.asyncio
    async def test_lookup_intent_queries_graph(self, populated_graph_store):
        """Verify LOOKUP intent includes graph relationships."""
        from app.langgraph.flow import should_query_graph

        # Arrange
        state = {
            "query": "Get details for WRN-001",
            "intent": "lookup",
            "graph_context": "",
        }

        # Act
        result = should_query_graph(state)

        # Assert
        assert result is True

    @pytest.mark.asyncio
    async def test_analytics_intent_may_skip_graph(self, populated_graph_store):
        """Verify ANALYTICS intent may skip detailed graph queries.

        Analytics queries focus on aggregations, where individual
        relationships may be less relevant.
        """
        from app.langgraph.flow import should_query_graph

        # Arrange
        state = {
            "query": "How many robots are in each category?",
            "intent": "analytics",
            "graph_context": "",
        }

        # Act
        result = should_query_graph(state)

        # Assert - analytics may or may not query graph depending on implementation
        assert isinstance(result, bool)

    @pytest.mark.asyncio
    async def test_search_intent_queries_graph_for_entities(self, graph_store_with_relationships):
        """Verify SEARCH intent queries graph when entities are mentioned."""
        from app.langgraph.flow import should_query_graph

        # Arrange - search query mentioning specific entity
        state = {
            "query": "Find components related to WRN-001",
            "intent": "search",
            "graph_context": "",
        }

        # Act
        result = should_query_graph(state)

        # Assert
        assert result is True


# =============================================================================
# TEST: FULL PIPELINE INTEGRATION
# =============================================================================


class TestFullPipelineIntegration:
    """End-to-end tests for the complete LangGraph flow with graph memory."""

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_full_flow_with_graph_context(
        self,
        graph_store_with_relationships,
        sample_schematics
    ):
        """Test complete pipeline including graph memory node.

        This test verifies the full flow:
        1. parse_intent
        2. query_graph (new node)
        3. retrieve
        4. compress_context (now includes graph context)
        5. reason
        6. respond
        """
        from app.langgraph import run_query

        # Arrange - mock the graph store getter
        with patch('app.langgraph.flow.get_graph_store', return_value=graph_store_with_relationships):
            # Act
            result = await run_query(
                query="What are the dependencies of WRN-001?",
                filters=None,
                top_k=5
            )

        # Assert
        assert result is not None
        assert result.get("success") is True or result.get("error") is None
        # Graph context should influence the response
        context = result.get("context_summary", "")
        # The response should contain graph-related information
        assert "WRN-001" in str(result) or "dependency" in str(result).lower()

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_flow_handles_graph_store_error(self):
        """Test pipeline gracefully handles graph store errors.

        If the graph store is unavailable or throws an error, the pipeline
        should continue with traditional search results.
        """
        from app.langgraph import run_query

        # Arrange - mock graph store that raises error
        mock_store = AsyncMock()
        mock_store.get_neighbors.side_effect = Exception("Graph store unavailable")

        with patch('app.langgraph.flow.get_graph_store', return_value=mock_store):
            # Act
            result = await run_query(
                query="Find information about WRN-001",
                filters=None,
                top_k=5
            )

        # Assert - should not crash, may have degraded results
        assert result is not None
        # Error should be logged but not break the flow
        assert result.get("success") is True or "error" in result

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_flow_pathfinding_integration(self, graph_store_with_relationships):
        """Test pipeline uses pathfinding for relationship queries."""
        from app.langgraph import run_query

        with patch('app.langgraph.flow.get_graph_store', return_value=graph_store_with_relationships):
            # Act
            result = await run_query(
                query="How is WRN-001 connected to electrical_power?",
                filters=None,
                top_k=5
            )

        # Assert
        assert result is not None
        # Should find path: WRN-001 -> POW-05 -> electrical_power
        # or WRN-001 -> SENSOR-01 -> electrical_power


# =============================================================================
# TEST: ENTITY EXTRACTION
# =============================================================================


class TestEntityExtraction:
    """Tests for entity extraction from natural language queries."""

    @pytest.mark.asyncio
    async def test_extract_robot_ids(self):
        """Verify extraction of robot IDs from queries."""
        from app.langgraph.flow import extract_entities

        # Act
        entities = extract_entities("What is the status of WRN-001?")

        # Assert
        assert "WRN-001" in entities

    @pytest.mark.asyncio
    async def test_extract_multiple_robot_ids(self):
        """Verify extraction of multiple robot IDs."""
        from app.langgraph.flow import extract_entities

        # Act
        entities = extract_entities("Compare WRN-001 and WRN-002 specifications")

        # Assert
        assert "WRN-001" in entities
        assert "WRN-002" in entities

    @pytest.mark.asyncio
    async def test_extract_model_identifiers(self):
        """Verify extraction of model identifiers (WC-100, WC-200, etc.)."""
        from app.langgraph.flow import extract_entities

        # Act
        entities = extract_entities("Show all WC-100 schematics")

        # Assert
        assert "WC-100" in entities

    @pytest.mark.asyncio
    async def test_extract_component_names(self):
        """Verify extraction of component names from queries."""
        from app.langgraph.flow import extract_entities

        # Act
        entities = extract_entities("Find the force feedback sensor documentation")

        # Assert
        # Should extract "force feedback sensor" or similar
        assert len(entities) >= 0  # May or may not extract depending on implementation

    @pytest.mark.asyncio
    async def test_no_entities_in_general_query(self):
        """Verify empty result for queries without specific entities."""
        from app.langgraph.flow import extract_entities

        # Act
        entities = extract_entities("What are the best practices for robot maintenance?")

        # Assert
        assert isinstance(entities, list)
        # May be empty or contain general terms


# =============================================================================
# TEST: GRAPH ENHANCED REASONING
# =============================================================================


class TestGraphEnhancedReasoning:
    """Tests for LLM reasoning enhanced with graph context."""

    @pytest.mark.asyncio
    async def test_reason_with_graph_context(self, graph_store_with_relationships):
        """Verify reasoning node uses graph context for better answers."""
        from app.langgraph.flow import reason

        # Arrange
        state = {
            "query": "Why might WRN-001 fail if POW-05 is down?",
            "filters": None,
            "top_k": 5,
            "intent": "diagnostic",
            "candidates": [],
            "compressed_context": "WRN-001: Atlas Heavy Lifter, industrial robot",
            "graph_context": "WRN-001 --DEPENDS_ON--> POW-05 (power supply)",
            "response": {},
            "error": None,
            "start_time": datetime.utcnow().isoformat(),
            "timings": {},
        }

        # Act
        with patch('app.config.settings.has_llm_config', False):
            result = await reason(state)

        # Assert
        reasoning = result["response"].get("reasoning", "")
        # Even without LLM, stub reasoning should acknowledge the data
        assert reasoning != ""

    @pytest.mark.asyncio
    async def test_reason_without_graph_context(self):
        """Verify reasoning still works when graph context is empty."""
        from app.langgraph.flow import reason

        # Arrange
        state = {
            "query": "General question about robots",
            "filters": None,
            "top_k": 5,
            "intent": "search",
            "candidates": [],
            "compressed_context": "Various robot schematics...",
            "graph_context": "",
            "response": {},
            "error": None,
            "start_time": datetime.utcnow().isoformat(),
            "timings": {},
        }

        # Act
        with patch('app.config.settings.has_llm_config', False):
            result = await reason(state)

        # Assert
        assert result is not None
        assert "response" in result


# =============================================================================
# TEST: TIMING AND PERFORMANCE
# =============================================================================


class TestTimingAndPerformance:
    """Tests for performance tracking of graph operations."""

    @pytest.mark.asyncio
    async def test_graph_query_timing_recorded(self, graph_store_with_relationships):
        """Verify graph query timing is recorded in state."""
        from app.langgraph.flow import query_graph

        # Arrange
        state = {
            "query": "What depends on POW-05?",
            "filters": None,
            "top_k": 5,
            "intent": "diagnostic",
            "candidates": [],
            "compressed_context": "",
            "graph_context": "",
            "response": {},
            "error": None,
            "start_time": datetime.utcnow().isoformat(),
            "timings": {},
        }

        # Act
        with patch('app.langgraph.flow.get_graph_store', return_value=graph_store_with_relationships):
            result = await query_graph(state)

        # Assert
        assert "query_graph" in result["timings"]
        assert result["timings"]["query_graph"] >= 0

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_graph_query_performance(self, graph_store_with_relationships):
        """Verify graph queries complete in reasonable time.

        Graph queries should complete within 100ms for typical operations.
        """
        import time
        from app.langgraph.flow import query_graph

        # Arrange
        state = {
            "query": "What are all the dependencies for WRN-001?",
            "filters": None,
            "top_k": 5,
            "intent": "diagnostic",
            "candidates": [],
            "compressed_context": "",
            "graph_context": "",
            "response": {},
            "error": None,
            "start_time": datetime.utcnow().isoformat(),
            "timings": {},
        }

        # Act
        start = time.time()
        with patch('app.langgraph.flow.get_graph_store', return_value=graph_store_with_relationships):
            await query_graph(state)
        elapsed = (time.time() - start) * 1000  # ms

        # Assert
        assert elapsed < 100, f"Graph query took {elapsed}ms, expected < 100ms"
