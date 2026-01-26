"""Pytest fixtures for WARNERCO Schematica Graph Memory tests.

This module provides reusable fixtures for testing the graph memory feature,
including temporary database paths, graph store instances, and sample data.
"""

import json
import os
import tempfile
from pathlib import Path
from typing import Any, Dict, List

import pytest
import pytest_asyncio


# =============================================================================
# TEMPORARY FILE FIXTURES
# =============================================================================


@pytest.fixture
def temp_db_path():
    """Create a temporary database path for testing.

    Yields:
        str: Path to a temporary SQLite database file.

    The temporary directory is automatically cleaned up after the test.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        yield os.path.join(tmpdir, "test_knowledge.db")


@pytest.fixture
def temp_schematics_json(sample_schematics):
    """Create a temporary schematics JSON file for testing.

    Args:
        sample_schematics: The sample schematic data fixture.

    Yields:
        Path: Path to the temporary JSON file.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        json_path = Path(tmpdir) / "schematics.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(sample_schematics, f, indent=2)
        yield json_path


# =============================================================================
# GRAPH STORE FIXTURES
# =============================================================================


@pytest.fixture
def graph_store(temp_db_path):
    """Create a graph store with a temporary database.

    Args:
        temp_db_path: Path to temporary database.

    Yields:
        GraphStore: An initialized graph store instance.

    Note:
        GraphStore initializes the database in __init__ and close() is sync.
    """
    from app.adapters.graph_store import GraphStore

    store = GraphStore(db_path=temp_db_path)
    yield store
    store.close()


@pytest_asyncio.fixture
async def populated_graph_store(graph_store, sample_schematics):
    """Create a graph store pre-populated with sample data.

    Args:
        graph_store: The base graph store fixture.
        sample_schematics: Sample schematic data.

    Yields:
        GraphStore: Graph store with indexed schematics.
    """
    await graph_store.index_schematics(sample_schematics)
    return graph_store


@pytest_asyncio.fixture
async def graph_store_with_relationships(populated_graph_store):
    """Create a graph store with sample relationships for pathfinding tests.

    This fixture creates a connected graph structure:
    - WRN-001 --depends_on--> POW-05
    - WRN-001 --contains--> SENSOR-01
    - WRN-002 --depends_on--> POW-05
    - WRN-002 --contains--> SENSOR-02
    - POW-05 --related_to--> electrical_power
    - SENSOR-01 --depends_on--> electrical_power

    Args:
        populated_graph_store: Graph store with schematics indexed.

    Yields:
        GraphStore: Graph store with relationships added.
    """
    from app.models.graph import Entity, Relationship

    store = populated_graph_store

    # First add entities that don't exist from schematics indexing
    additional_entities = [
        Entity(id="POW-05", entity_type="power_supply", name="Power Supply 05"),
        Entity(id="SENSOR-01", entity_type="component", name="Sensor 01"),
        Entity(id="SENSOR-02", entity_type="component", name="Sensor 02"),
        Entity(id="electrical_power", entity_type="resource", name="Electrical Power"),
    ]
    for entity in additional_entities:
        await store.add_entity(entity)

    # Add relationships using valid predicates from VALID_PREDICATES
    relationships = [
        Relationship(subject="WRN-001", predicate="depends_on", object="POW-05"),
        Relationship(subject="WRN-001", predicate="contains", object="SENSOR-01"),
        Relationship(subject="WRN-002", predicate="depends_on", object="POW-05"),
        Relationship(subject="WRN-002", predicate="contains", object="SENSOR-02"),
        Relationship(subject="POW-05", predicate="related_to", object="electrical_power"),
        Relationship(subject="SENSOR-01", predicate="depends_on", object="electrical_power"),
    ]

    for rel in relationships:
        await store.add_relationship(rel)

    return store


# =============================================================================
# SAMPLE DATA FIXTURES
# =============================================================================


@pytest.fixture
def sample_schematics() -> List[Dict[str, Any]]:
    """Sample schematic data for testing.

    Returns:
        List of schematic dictionaries matching the production schema.
    """
    return [
        {
            "id": "WRN-001",
            "model": "WC-100",
            "name": "Atlas Heavy Lifter",
            "component": "force feedback sensor array",
            "version": "v3.4",
            "summary": "Industrial lifting robot with hydraulic systems and force feedback.",
            "url": "https://schematics.warnerco.io/wc-100/force_feedback.pdf",
            "last_verified": "2025-01-15",
            "category": "sensors",
            "status": "active",
            "tags": ["industrial", "lifting", "hydraulic"],
            "specifications": {
                "resolution": "0.1N",
                "range": "0-500N",
                "response_time": "2ms"
            }
        },
        {
            "id": "WRN-002",
            "model": "WC-200",
            "name": "Precision Welder",
            "component": "thermal management unit",
            "version": "v2.1",
            "summary": "Welding robot with advanced sensor array and thermal regulation.",
            "url": "https://schematics.warnerco.io/wc-200/thermal.pdf",
            "last_verified": "2025-01-10",
            "category": "thermal",
            "status": "active",
            "tags": ["welding", "precision", "thermal"],
            "specifications": {
                "cooling_capacity": "500W",
                "temp_range": "-20C to 85C"
            }
        },
        {
            "id": "WRN-003",
            "model": "WC-300",
            "name": "Scout Drone",
            "component": "navigation module",
            "version": "v1.5",
            "summary": "Autonomous reconnaissance drone with GPS and LIDAR navigation.",
            "url": "https://schematics.warnerco.io/wc-300/navigation.pdf",
            "last_verified": "2025-01-08",
            "category": "navigation",
            "status": "active",
            "tags": ["drone", "autonomous", "navigation"],
            "specifications": {
                "gps_accuracy": "1cm",
                "lidar_range": "100m"
            }
        },
        {
            "id": "WRN-004",
            "model": "WC-400",
            "name": "Guardian Bot",
            "component": "vision processing module",
            "version": "v4.0",
            "summary": "Security robot with multi-spectral vision and AI threat detection.",
            "url": "https://schematics.warnerco.io/wc-400/vision.pdf",
            "last_verified": "2025-01-12",
            "category": "sensors",
            "status": "maintenance",
            "tags": ["security", "vision", "AI"],
            "specifications": {
                "resolution": "4K",
                "frame_rate": "60fps"
            }
        },
    ]


@pytest.fixture
def sample_entities() -> List[Dict[str, Any]]:
    """Sample entity data for testing entity creation.

    Returns:
        List of entity dictionaries with name and type.
    """
    return [
        {"name": "WRN-001", "entity_type": "robot"},
        {"name": "WRN-002", "entity_type": "robot"},
        {"name": "POW-05", "entity_type": "power_supply"},
        {"name": "SENSOR-01", "entity_type": "component"},
        {"name": "electrical_power", "entity_type": "resource"},
        {"name": "hydraulic_fluid", "entity_type": "resource"},
    ]


@pytest.fixture
def sample_relationships() -> List[tuple]:
    """Sample relationship triplets for testing.

    Returns:
        List of (subject, predicate, object) tuples.
    """
    return [
        ("WRN-001", "DEPENDS_ON", "POW-05"),
        ("WRN-001", "HAS_COMPONENT", "SENSOR-01"),
        ("WRN-002", "DEPENDS_ON", "POW-05"),
        ("POW-05", "PROVIDES", "electrical_power"),
        ("SENSOR-01", "REQUIRES", "electrical_power"),
    ]


@pytest.fixture
def complex_graph_relationships() -> List[tuple]:
    """Complex graph relationships for pathfinding tests.

    Creates a graph: A -> B -> C -> D with branching path A -> E -> D

    Returns:
        List of (subject, predicate, object) tuples.
    """
    return [
        ("A", "CONNECTS_TO", "B"),
        ("B", "CONNECTS_TO", "C"),
        ("C", "CONNECTS_TO", "D"),
        ("A", "CONNECTS_TO", "E"),
        ("E", "CONNECTS_TO", "D"),
    ]


# =============================================================================
# MOCK FIXTURES
# =============================================================================


@pytest.fixture
def mock_langgraph_state():
    """Create a mock LangGraph state for testing graph integration.

    Returns:
        Dict representing a GraphState for the flow.
    """
    from datetime import datetime, timezone

    return {
        "query": "What depends on POW-05?",
        "filters": None,
        "top_k": 5,
        "intent": None,
        "candidates": [],
        "compressed_context": "",
        "graph_context": "",  # New field for graph memory
        "response": {},
        "error": None,
        "start_time": datetime.now(timezone.utc).isoformat(),
        "timings": {},
    }


@pytest.fixture
def mock_mcp_context():
    """Create a mock MCP Context for testing MCP tools.

    Returns:
        A mock context object with elicit capability.
    """
    class MockContext:
        """Mock MCP context for testing."""

        async def elicit(self, prompt: str, schema: Any = None):
            """Mock elicit always returns a simple response."""
            return {"action": "confirm"}

    return MockContext()


# =============================================================================
# PYTEST CONFIGURATION
# =============================================================================


def pytest_configure(config):
    """Configure pytest markers for the test suite."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "mcp: marks tests that require MCP tools"
    )


# Allow async fixtures
pytest_plugins = ['pytest_asyncio']
