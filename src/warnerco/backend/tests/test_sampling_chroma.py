"""Tests for warn_explain_schematic sampling tool with Chroma backend.

This module tests the MCP sampling tool that uses ctx.sample() to get
LLM-enriched explanations of robot schematics. Tests cover:

- Pydantic model validation (SchematicExplanation, SchematicExplainerResult)
- Not-found error handling (structured error response)
- Audience Literal validation
- Graph context assembly (outgoing/incoming relationships)
- Sampling integration (mocked ctx.sample())
- Sampling failure handling (structured error, not exception)

All external dependencies (memory store, graph store, ctx) are mocked.
"""

import pytest
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from unittest.mock import AsyncMock, MagicMock, patch

from pydantic import ValidationError

from app.mcp_tools import (
    SchematicExplanation,
    SchematicExplainerResult,
)
from app.models.schematic import Schematic, SchematicStatus


# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def valid_explanation_data() -> Dict[str, Any]:
    """Minimal valid data for constructing a SchematicExplanation."""
    return {
        "plain_language_summary": "This sensor array detects force feedback.",
        "key_capabilities": ["High resolution", "Fast response", "Wide range"],
        "typical_failure_modes": ["Calibration drift", "Connector corrosion"],
        "maintenance_tips": ["Recalibrate monthly", "Check connectors weekly"],
        "integration_notes": "Connects to the main control bus via CAN protocol.",
        "safety_considerations": "Ensure power is off before servicing.",
    }


@pytest.fixture
def valid_explainer_result_data(valid_explanation_data) -> Dict[str, Any]:
    """Minimal valid data for constructing a SchematicExplainerResult."""
    return {
        "schematic_id": "WRN-001",
        "model": "WC-100",
        "name": "Atlas Heavy Lifter",
        "component": "force feedback sensor array",
        "category": "sensors",
        "status": "active",
        "explanation": valid_explanation_data,
        "graph_context": None,
        "sampling_metadata": {"audience": "technical"},
    }


@pytest.fixture
def sample_schematic() -> Schematic:
    """A sample Schematic object for testing."""
    return Schematic(
        id="WRN-001",
        model="WC-100",
        name="Atlas Heavy Lifter",
        component="force feedback sensor array",
        version="v3.4",
        summary="Industrial lifting robot with hydraulic systems and force feedback.",
        url="https://schematics.warnerco.io/wc-100/force_feedback.pdf",
        last_verified="2025-01-15",
        category="sensors",
        status=SchematicStatus.ACTIVE,
        tags=["industrial", "lifting", "hydraulic"],
        specifications={
            "resolution": "0.1N",
            "range": "0-500N",
            "response_time": "2ms",
        },
    )


@pytest.fixture
def mock_ctx():
    """Create a mock MCP Context with sample, elicit, and info as AsyncMock."""
    ctx = MagicMock()
    ctx.sample = AsyncMock()
    ctx.elicit = AsyncMock()
    ctx.info = AsyncMock()
    return ctx


# =============================================================================
# TEST: Pydantic Model Validation
# =============================================================================


class TestSchematicExplanationModel:
    """Tests for the SchematicExplanation Pydantic model."""

    def test_valid_construction(self, valid_explanation_data):
        """SchematicExplanation accepts valid data with all required fields."""
        explanation = SchematicExplanation(**valid_explanation_data)

        assert explanation.plain_language_summary == valid_explanation_data["plain_language_summary"]
        assert len(explanation.key_capabilities) == 3
        assert len(explanation.typical_failure_modes) == 2
        assert len(explanation.maintenance_tips) == 2
        assert explanation.integration_notes == valid_explanation_data["integration_notes"]
        assert explanation.safety_considerations == valid_explanation_data["safety_considerations"]

    def test_missing_required_field_plain_language_summary(self, valid_explanation_data):
        """SchematicExplanation rejects data missing plain_language_summary."""
        del valid_explanation_data["plain_language_summary"]

        with pytest.raises(ValidationError) as exc_info:
            SchematicExplanation(**valid_explanation_data)

        assert "plain_language_summary" in str(exc_info.value)

    def test_missing_required_field_key_capabilities(self, valid_explanation_data):
        """SchematicExplanation rejects data missing key_capabilities."""
        del valid_explanation_data["key_capabilities"]

        with pytest.raises(ValidationError) as exc_info:
            SchematicExplanation(**valid_explanation_data)

        assert "key_capabilities" in str(exc_info.value)

    def test_missing_required_field_integration_notes(self, valid_explanation_data):
        """SchematicExplanation rejects data missing integration_notes."""
        del valid_explanation_data["integration_notes"]

        with pytest.raises(ValidationError) as exc_info:
            SchematicExplanation(**valid_explanation_data)

        assert "integration_notes" in str(exc_info.value)

    def test_missing_required_field_safety_considerations(self, valid_explanation_data):
        """SchematicExplanation rejects data missing safety_considerations."""
        del valid_explanation_data["safety_considerations"]

        with pytest.raises(ValidationError) as exc_info:
            SchematicExplanation(**valid_explanation_data)

        assert "safety_considerations" in str(exc_info.value)

    def test_empty_lists_are_valid(self):
        """SchematicExplanation allows empty lists for list fields."""
        explanation = SchematicExplanation(
            plain_language_summary="Test summary",
            key_capabilities=[],
            typical_failure_modes=[],
            maintenance_tips=[],
            integration_notes="None",
            safety_considerations="None",
        )

        assert explanation.key_capabilities == []
        assert explanation.typical_failure_modes == []
        assert explanation.maintenance_tips == []


class TestSchematicExplainerResultModel:
    """Tests for the SchematicExplainerResult Pydantic model."""

    def test_valid_construction(self, valid_explainer_result_data):
        """SchematicExplainerResult accepts valid data with all required fields."""
        result = SchematicExplainerResult(**valid_explainer_result_data)

        assert result.schematic_id == "WRN-001"
        assert result.model == "WC-100"
        assert result.name == "Atlas Heavy Lifter"
        assert result.component == "force feedback sensor array"
        assert result.category == "sensors"
        assert result.status == "active"
        assert isinstance(result.explanation, SchematicExplanation)
        assert result.graph_context is None
        assert result.sampling_metadata == {"audience": "technical"}

    def test_missing_required_field_schematic_id(self, valid_explainer_result_data):
        """SchematicExplainerResult rejects data missing schematic_id."""
        del valid_explainer_result_data["schematic_id"]

        with pytest.raises(ValidationError) as exc_info:
            SchematicExplainerResult(**valid_explainer_result_data)

        assert "schematic_id" in str(exc_info.value)

    def test_missing_required_field_explanation(self, valid_explainer_result_data):
        """SchematicExplainerResult rejects data missing explanation."""
        del valid_explainer_result_data["explanation"]

        with pytest.raises(ValidationError) as exc_info:
            SchematicExplainerResult(**valid_explainer_result_data)

        assert "explanation" in str(exc_info.value)

    def test_missing_required_field_sampling_metadata(self, valid_explainer_result_data):
        """SchematicExplainerResult rejects data missing sampling_metadata."""
        del valid_explainer_result_data["sampling_metadata"]

        with pytest.raises(ValidationError) as exc_info:
            SchematicExplainerResult(**valid_explainer_result_data)

        assert "sampling_metadata" in str(exc_info.value)

    def test_graph_context_with_data(self, valid_explainer_result_data):
        """SchematicExplainerResult accepts graph_context with relationship dicts."""
        valid_explainer_result_data["graph_context"] = [
            {"direction": "outgoing", "predicate": "depends_on", "target": "POW-05"},
            {"direction": "incoming", "predicate": "contains", "source": "WRN-002"},
        ]
        result = SchematicExplainerResult(**valid_explainer_result_data)

        assert len(result.graph_context) == 2
        assert result.graph_context[0]["target"] == "POW-05"
        assert result.graph_context[1]["source"] == "WRN-002"


# =============================================================================
# TEST: warn_explain_schematic - Not Found
# =============================================================================


class TestWarnExplainSchematicNotFound:
    """Tests for warn_explain_schematic when schematic is not found."""

    @pytest.mark.asyncio
    async def test_not_found_returns_structured_error(self, mock_ctx):
        """Calling with a fake schematic ID returns a SchematicExplainerResult
        with status='not_found' and error in sampling_metadata."""
        from app.mcp_tools import warn_explain_schematic

        mock_memory = MagicMock()
        mock_memory.get_schematic = AsyncMock(return_value=None)

        with patch("app.mcp_tools.get_memory_store", return_value=mock_memory):
            result = await warn_explain_schematic.fn(
                ctx=mock_ctx,
                schematic_id="FAKE-99999",
                audience="technical",
                include_graph_context=True,
            )

        assert isinstance(result, SchematicExplainerResult)
        assert result.schematic_id == "FAKE-99999"
        assert result.status == "not_found"
        assert result.model == "unknown"
        assert result.name == "unknown"
        assert result.component == "unknown"
        assert result.category == "unknown"
        assert "not found" in result.explanation.plain_language_summary.lower()
        assert "error" in result.sampling_metadata
        assert "FAKE-99999" in result.sampling_metadata["error"]
        assert result.graph_context is None


# =============================================================================
# TEST: warn_explain_schematic - Audience Validation
# =============================================================================


class TestWarnExplainSchematicAudience:
    """Tests for audience Literal validation on warn_explain_schematic."""

    def test_valid_audience_values(self):
        """The Literal type hint accepts 'technical', 'executive', 'field_technician'."""
        import inspect
        from app.mcp_tools import warn_explain_schematic

        # Get the underlying function's signature
        sig = inspect.signature(warn_explain_schematic.fn)
        audience_param = sig.parameters["audience"]

        # The default should be 'technical'
        assert audience_param.default == "technical"

    @pytest.mark.asyncio
    async def test_technical_audience_uses_correct_prompt(self, mock_ctx, sample_schematic):
        """Verify the 'technical' audience builds the correct system prompt."""
        from app.mcp_tools import warn_explain_schematic

        mock_memory = MagicMock()
        mock_memory.get_schematic = AsyncMock(return_value=sample_schematic)

        # Mock sampling to capture the system_prompt passed
        sampling_result = MagicMock()
        sampling_result.result = SchematicExplanation(
            plain_language_summary="Test",
            key_capabilities=["A"],
            typical_failure_modes=["B"],
            maintenance_tips=["C"],
            integration_notes="D",
            safety_considerations="E",
        )
        sampling_result.history = []
        mock_ctx.sample = AsyncMock(return_value=sampling_result)

        with patch("app.mcp_tools.get_memory_store", return_value=mock_memory), \
             patch("app.adapters.graph_store.get_graph_store", side_effect=ImportError("no graph")):
            result = await warn_explain_schematic.fn(
                ctx=mock_ctx,
                schematic_id="WRN-001",
                audience="technical",
                include_graph_context=True,
            )

        # Verify ctx.sample was called with a system_prompt containing 'engineer'
        call_kwargs = mock_ctx.sample.call_args
        assert "engineer" in call_kwargs.kwargs.get("system_prompt", "").lower() or \
               "engineer" in str(call_kwargs).lower()


# =============================================================================
# TEST: warn_explain_schematic - Graph Context Assembly
# =============================================================================


class TestWarnExplainSchematicGraphContext:
    """Tests for graph context assembly in warn_explain_schematic."""

    @pytest.mark.asyncio
    async def test_graph_context_outgoing_has_target_key(self, mock_ctx, sample_schematic):
        """Outgoing graph relationships should have a 'target' key."""
        from app.mcp_tools import warn_explain_schematic
        from app.models.graph import Relationship

        mock_memory = MagicMock()
        mock_memory.get_schematic = AsyncMock(return_value=sample_schematic)

        mock_graph = MagicMock()
        mock_graph.get_related = AsyncMock(return_value=[
            Relationship(subject="WRN-001", predicate="depends_on", object="POW-05"),
        ])
        mock_graph.get_subjects = AsyncMock(return_value=[])

        # Mock sampling to succeed
        sampling_result = MagicMock()
        sampling_result.result = SchematicExplanation(
            plain_language_summary="Test",
            key_capabilities=["A"],
            typical_failure_modes=["B"],
            maintenance_tips=["C"],
            integration_notes="D",
            safety_considerations="E",
        )
        sampling_result.history = []
        mock_ctx.sample = AsyncMock(return_value=sampling_result)

        with patch("app.mcp_tools.get_memory_store", return_value=mock_memory), \
             patch("app.adapters.graph_store.get_graph_store", return_value=mock_graph):
            result = await warn_explain_schematic.fn(
                ctx=mock_ctx,
                schematic_id="WRN-001",
                audience="technical",
                include_graph_context=True,
            )

        assert result.graph_context is not None
        outgoing_rels = [r for r in result.graph_context if r["direction"] == "outgoing"]
        assert len(outgoing_rels) == 1
        assert "target" in outgoing_rels[0]
        assert outgoing_rels[0]["target"] == "POW-05"
        assert outgoing_rels[0]["predicate"] == "depends_on"

    @pytest.mark.asyncio
    async def test_graph_context_incoming_has_source_key(self, mock_ctx, sample_schematic):
        """Incoming graph relationships should have a 'source' key."""
        from app.mcp_tools import warn_explain_schematic
        from app.models.graph import Relationship

        mock_memory = MagicMock()
        mock_memory.get_schematic = AsyncMock(return_value=sample_schematic)

        mock_graph = MagicMock()
        mock_graph.get_related = AsyncMock(return_value=[])
        mock_graph.get_subjects = AsyncMock(return_value=[
            Relationship(subject="WRN-002", predicate="related_to", object="WRN-001"),
        ])

        sampling_result = MagicMock()
        sampling_result.result = SchematicExplanation(
            plain_language_summary="Test",
            key_capabilities=["A"],
            typical_failure_modes=["B"],
            maintenance_tips=["C"],
            integration_notes="D",
            safety_considerations="E",
        )
        sampling_result.history = []
        mock_ctx.sample = AsyncMock(return_value=sampling_result)

        with patch("app.mcp_tools.get_memory_store", return_value=mock_memory), \
             patch("app.adapters.graph_store.get_graph_store", return_value=mock_graph):
            result = await warn_explain_schematic.fn(
                ctx=mock_ctx,
                schematic_id="WRN-001",
                audience="technical",
                include_graph_context=True,
            )

        assert result.graph_context is not None
        incoming_rels = [r for r in result.graph_context if r["direction"] == "incoming"]
        assert len(incoming_rels) == 1
        assert "source" in incoming_rels[0]
        assert incoming_rels[0]["source"] == "WRN-002"
        assert incoming_rels[0]["predicate"] == "related_to"

    @pytest.mark.asyncio
    async def test_graph_context_mixed_directions(self, mock_ctx, sample_schematic):
        """Graph context combines both outgoing and incoming relationships."""
        from app.mcp_tools import warn_explain_schematic
        from app.models.graph import Relationship

        mock_memory = MagicMock()
        mock_memory.get_schematic = AsyncMock(return_value=sample_schematic)

        mock_graph = MagicMock()
        mock_graph.get_related = AsyncMock(return_value=[
            Relationship(subject="WRN-001", predicate="depends_on", object="POW-05"),
            Relationship(subject="WRN-001", predicate="contains", object="SENSOR-01"),
        ])
        mock_graph.get_subjects = AsyncMock(return_value=[
            Relationship(subject="WRN-002", predicate="related_to", object="WRN-001"),
        ])

        sampling_result = MagicMock()
        sampling_result.result = SchematicExplanation(
            plain_language_summary="Test",
            key_capabilities=["A"],
            typical_failure_modes=["B"],
            maintenance_tips=["C"],
            integration_notes="D",
            safety_considerations="E",
        )
        sampling_result.history = []
        mock_ctx.sample = AsyncMock(return_value=sampling_result)

        with patch("app.mcp_tools.get_memory_store", return_value=mock_memory), \
             patch("app.adapters.graph_store.get_graph_store", return_value=mock_graph):
            result = await warn_explain_schematic.fn(
                ctx=mock_ctx,
                schematic_id="WRN-001",
                audience="technical",
                include_graph_context=True,
            )

        assert result.graph_context is not None
        assert len(result.graph_context) == 3
        outgoing = [r for r in result.graph_context if r["direction"] == "outgoing"]
        incoming = [r for r in result.graph_context if r["direction"] == "incoming"]
        assert len(outgoing) == 2
        assert len(incoming) == 1

    @pytest.mark.asyncio
    async def test_graph_context_disabled(self, mock_ctx, sample_schematic):
        """Setting include_graph_context=False skips graph store entirely."""
        from app.mcp_tools import warn_explain_schematic

        mock_memory = MagicMock()
        mock_memory.get_schematic = AsyncMock(return_value=sample_schematic)

        sampling_result = MagicMock()
        sampling_result.result = SchematicExplanation(
            plain_language_summary="Test",
            key_capabilities=["A"],
            typical_failure_modes=["B"],
            maintenance_tips=["C"],
            integration_notes="D",
            safety_considerations="E",
        )
        sampling_result.history = []
        mock_ctx.sample = AsyncMock(return_value=sampling_result)

        with patch("app.mcp_tools.get_memory_store", return_value=mock_memory):
            result = await warn_explain_schematic.fn(
                ctx=mock_ctx,
                schematic_id="WRN-001",
                audience="technical",
                include_graph_context=False,
            )

        # graph_context should be None when disabled
        assert result.graph_context is None


# =============================================================================
# TEST: warn_explain_schematic - Sampling Integration (Mock)
# =============================================================================


class TestWarnExplainSchematicSampling:
    """Tests for sampling integration in warn_explain_schematic."""

    @pytest.mark.asyncio
    async def test_sampling_success_returns_full_result(self, mock_ctx, sample_schematic):
        """Successful sampling returns a complete SchematicExplainerResult
        with the LLM-generated explanation and metadata."""
        from app.mcp_tools import warn_explain_schematic

        mock_memory = MagicMock()
        mock_memory.get_schematic = AsyncMock(return_value=sample_schematic)

        expected_explanation = SchematicExplanation(
            plain_language_summary="This sensor measures force applied by the robot.",
            key_capabilities=["High precision", "Fast response", "Wide dynamic range"],
            typical_failure_modes=["Calibration drift", "Connector failure"],
            maintenance_tips=["Monthly calibration", "Visual inspection"],
            integration_notes="Connects via CAN bus to main controller.",
            safety_considerations="De-energize before servicing.",
        )

        sampling_result = MagicMock()
        sampling_result.result = expected_explanation
        sampling_result.history = [{"role": "assistant", "content": "..."}]
        mock_ctx.sample = AsyncMock(return_value=sampling_result)

        with patch("app.mcp_tools.get_memory_store", return_value=mock_memory):
            result = await warn_explain_schematic.fn(
                ctx=mock_ctx,
                schematic_id="WRN-001",
                audience="executive",
                include_graph_context=False,
            )

        assert isinstance(result, SchematicExplainerResult)
        assert result.schematic_id == "WRN-001"
        assert result.model == "WC-100"
        assert result.name == "Atlas Heavy Lifter"
        assert result.component == "force feedback sensor array"
        assert result.category == "sensors"
        assert result.status == "active"
        assert result.explanation.plain_language_summary == expected_explanation.plain_language_summary
        assert result.explanation.key_capabilities == expected_explanation.key_capabilities
        assert result.sampling_metadata["audience"] == "executive"
        assert result.sampling_metadata["sampling_history_length"] == 1
        assert "generated_at" in result.sampling_metadata

    @pytest.mark.asyncio
    async def test_sampling_called_with_correct_params(self, mock_ctx, sample_schematic):
        """ctx.sample() is called with the expected parameters."""
        from app.mcp_tools import warn_explain_schematic

        mock_memory = MagicMock()
        mock_memory.get_schematic = AsyncMock(return_value=sample_schematic)

        sampling_result = MagicMock()
        sampling_result.result = SchematicExplanation(
            plain_language_summary="Test",
            key_capabilities=[],
            typical_failure_modes=[],
            maintenance_tips=[],
            integration_notes="N/A",
            safety_considerations="N/A",
        )
        sampling_result.history = []
        mock_ctx.sample = AsyncMock(return_value=sampling_result)

        with patch("app.mcp_tools.get_memory_store", return_value=mock_memory):
            await warn_explain_schematic.fn(
                ctx=mock_ctx,
                schematic_id="WRN-001",
                audience="field_technician",
                include_graph_context=False,
            )

        mock_ctx.sample.assert_called_once()
        call_kwargs = mock_ctx.sample.call_args.kwargs

        assert call_kwargs["result_type"] is SchematicExplanation
        assert call_kwargs["temperature"] == 0.3
        assert call_kwargs["max_tokens"] == 1024
        assert "field_technician" in call_kwargs["system_prompt"].lower() or \
               "technician" in call_kwargs["system_prompt"].lower()
        assert "WRN-001" in call_kwargs["messages"]

    @pytest.mark.asyncio
    async def test_sampling_returns_none_result(self, mock_ctx, sample_schematic):
        """When sampling returns no structured result, a fallback is returned."""
        from app.mcp_tools import warn_explain_schematic

        mock_memory = MagicMock()
        mock_memory.get_schematic = AsyncMock(return_value=sample_schematic)

        sampling_result = MagicMock()
        sampling_result.result = None
        sampling_result.text = "Some raw text"
        sampling_result.history = []
        mock_ctx.sample = AsyncMock(return_value=sampling_result)

        with patch("app.mcp_tools.get_memory_store", return_value=mock_memory):
            result = await warn_explain_schematic.fn(
                ctx=mock_ctx,
                schematic_id="WRN-001",
                audience="technical",
                include_graph_context=False,
            )

        assert isinstance(result, SchematicExplainerResult)
        assert result.schematic_id == "WRN-001"
        assert "no structured result" in result.explanation.plain_language_summary.lower()
        assert "error" in result.sampling_metadata


# =============================================================================
# TEST: warn_explain_schematic - Sampling Failure
# =============================================================================


class TestWarnExplainSchematicSamplingFailure:
    """Tests for sampling failure handling in warn_explain_schematic."""

    @pytest.mark.asyncio
    async def test_sampling_exception_returns_structured_error(self, mock_ctx, sample_schematic):
        """When ctx.sample() raises an exception, the tool returns a
        SchematicExplainerResult with error details instead of propagating."""
        from app.mcp_tools import warn_explain_schematic

        mock_memory = MagicMock()
        mock_memory.get_schematic = AsyncMock(return_value=sample_schematic)

        mock_ctx.sample = AsyncMock(side_effect=RuntimeError("Sampling service unavailable"))

        with patch("app.mcp_tools.get_memory_store", return_value=mock_memory):
            result = await warn_explain_schematic.fn(
                ctx=mock_ctx,
                schematic_id="WRN-001",
                audience="technical",
                include_graph_context=False,
            )

        # Should NOT raise an exception
        assert isinstance(result, SchematicExplainerResult)
        assert result.schematic_id == "WRN-001"
        assert result.model == "WC-100"
        assert result.status == "active"
        assert "sampling failed" in result.explanation.plain_language_summary.lower()
        assert "error" in result.sampling_metadata
        assert "Sampling service unavailable" in result.sampling_metadata["error"]

    @pytest.mark.asyncio
    async def test_sampling_exception_preserves_graph_context(self, mock_ctx, sample_schematic):
        """When sampling fails, graph context already fetched is still returned."""
        from app.mcp_tools import warn_explain_schematic
        from app.models.graph import Relationship

        mock_memory = MagicMock()
        mock_memory.get_schematic = AsyncMock(return_value=sample_schematic)

        mock_graph = MagicMock()
        mock_graph.get_related = AsyncMock(return_value=[
            Relationship(subject="WRN-001", predicate="depends_on", object="POW-05"),
        ])
        mock_graph.get_subjects = AsyncMock(return_value=[])

        mock_ctx.sample = AsyncMock(side_effect=Exception("LLM timeout"))

        with patch("app.mcp_tools.get_memory_store", return_value=mock_memory), \
             patch("app.adapters.graph_store.get_graph_store", return_value=mock_graph):
            result = await warn_explain_schematic.fn(
                ctx=mock_ctx,
                schematic_id="WRN-001",
                audience="technical",
                include_graph_context=True,
            )

        assert isinstance(result, SchematicExplainerResult)
        assert result.graph_context is not None
        assert len(result.graph_context) == 1
        assert result.graph_context[0]["target"] == "POW-05"

    @pytest.mark.asyncio
    async def test_graph_failure_does_not_block_sampling(self, mock_ctx, sample_schematic):
        """When graph store fails, sampling still proceeds normally."""
        from app.mcp_tools import warn_explain_schematic

        mock_memory = MagicMock()
        mock_memory.get_schematic = AsyncMock(return_value=sample_schematic)

        expected_explanation = SchematicExplanation(
            plain_language_summary="Test explanation",
            key_capabilities=["A"],
            typical_failure_modes=["B"],
            maintenance_tips=["C"],
            integration_notes="D",
            safety_considerations="E",
        )

        sampling_result = MagicMock()
        sampling_result.result = expected_explanation
        sampling_result.history = []
        mock_ctx.sample = AsyncMock(return_value=sampling_result)

        with patch("app.mcp_tools.get_memory_store", return_value=mock_memory), \
             patch("app.adapters.graph_store.get_graph_store", side_effect=Exception("Graph DB down")):
            result = await warn_explain_schematic.fn(
                ctx=mock_ctx,
                schematic_id="WRN-001",
                audience="technical",
                include_graph_context=True,
            )

        assert isinstance(result, SchematicExplainerResult)
        assert result.explanation.plain_language_summary == "Test explanation"
        # Graph context should be None due to failure
        assert result.graph_context is None
