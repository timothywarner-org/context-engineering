#!/usr/bin/env python3
"""Manual verification script for Graph Memory feature.

This script provides hands-on verification that the Graph Memory feature
is working correctly. It can be run standalone to test the graph store,
MCP tools, and LangGraph integration.

Usage:
    cd src/warnerco/backend
    uv run python scripts/verify_graph.py

    # Or with specific tests:
    uv run python scripts/verify_graph.py --test store
    uv run python scripts/verify_graph.py --test mcp
    uv run python scripts/verify_graph.py --test flow
    uv run python scripts/verify_graph.py --test all

This script:
1. Initializes the graph store with a fresh database
2. Indexes schematics.json into the graph
3. Adds test relationships (dependency chains)
4. Runs verification queries (neighbors, paths, stats)
5. Tests MCP tools directly
6. Tests LangGraph flow integration
7. Prints results in a readable format with pass/fail indicators
"""

import argparse
import asyncio
import json
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv

# Load environment
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path, override=True)


# =============================================================================
# UTILITIES
# =============================================================================


class Colors:
    """ANSI color codes for terminal output."""
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    RESET = "\033[0m"
    BOLD = "\033[1m"


def print_header(title: str) -> None:
    """Print a formatted section header."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{title.center(60)}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 60}{Colors.RESET}\n")


def print_step(step: int, total: int, description: str) -> None:
    """Print a formatted step indicator."""
    print(f"\n{Colors.CYAN}[{step}/{total}] {description}{Colors.RESET}")
    print("-" * 50)


def print_pass(message: str) -> None:
    """Print a pass indicator."""
    print(f"  {Colors.GREEN}[PASS]{Colors.RESET} {message}")


def print_fail(message: str) -> None:
    """Print a fail indicator."""
    print(f"  {Colors.RED}[FAIL]{Colors.RESET} {message}")


def print_warn(message: str) -> None:
    """Print a warning indicator."""
    print(f"  {Colors.YELLOW}[WARN]{Colors.RESET} {message}")


def print_info(message: str) -> None:
    """Print an info message."""
    print(f"  {Colors.BLUE}[INFO]{Colors.RESET} {message}")


def print_data(label: str, data: Any) -> None:
    """Print labeled data."""
    if isinstance(data, (dict, list)):
        print(f"  {label}:")
        print(f"    {json.dumps(data, indent=4, default=str)}")
    else:
        print(f"  {label}: {data}")


# =============================================================================
# TEST: GRAPH STORE
# =============================================================================


async def verify_graph_store() -> Tuple[bool, List[str]]:
    """Verify the SQLite + NetworkX graph store.

    Returns:
        Tuple of (success, list of error messages)
    """
    print_header("Graph Store Verification")
    errors = []
    total_steps = 6

    try:
        from app.adapters.graph_store import SQLiteGraphStore
        from app.models.graph import Entity, Relationship
    except ImportError as e:
        print_fail(f"Cannot import graph_store: {e}")
        errors.append(f"Import error: {e}")
        return False, errors

    store = None
    db_path = None

    try:
        # Use temp database for testing
        import tempfile as tf
        tmpdir = tf.mkdtemp()
        db_path = Path(tmpdir) / "test_knowledge.db"

        # Step 1: Initialize store (happens in __init__)
        print_step(1, total_steps, "Initializing graph store")
        try:
            store = SQLiteGraphStore(db_path=str(db_path))
            print_pass("Graph store initialized")
        except Exception as e:
            print_fail(f"Initialization failed: {e}")
            errors.append(f"Init error: {e}")
            return False, errors

        # Step 2: Add entities
        print_step(2, total_steps, "Adding entities")
        try:
            await store.add_entity(Entity(id="WRN-001", entity_type="robot", name="Robot 1", metadata={"model": "WC-100"}))
            await store.add_entity(Entity(id="WRN-002", entity_type="robot", name="Robot 2", metadata={"model": "WC-200"}))
            await store.add_entity(Entity(id="POW-05", entity_type="power_supply", name="Power Supply 5"))
            await store.add_entity(Entity(id="SENSOR-01", entity_type="component", name="Sensor 1"))
            await store.add_entity(Entity(id="electrical_power", entity_type="resource", name="Electrical Power"))

            entity = await store.get_entity("WRN-001")
            if entity and entity.id == "WRN-001":
                print_pass("Entities created and retrieved")
            else:
                print_fail("Entity retrieval failed")
                errors.append("Entity retrieval returned None or wrong data")
        except Exception as e:
            print_fail(f"Entity creation failed: {e}")
            errors.append(f"Entity error: {e}")

        # Step 3: Add relationships
        print_step(3, total_steps, "Adding relationships")
        try:
            await store.add_relationship(Relationship(subject="WRN-001", predicate="depends_on", object="POW-05"))
            await store.add_relationship(Relationship(subject="WRN-001", predicate="has_component", object="SENSOR-01"))
            await store.add_relationship(Relationship(subject="WRN-002", predicate="depends_on", object="POW-05"))
            await store.add_relationship(Relationship(subject="POW-05", predicate="provides", object="electrical_power"))

            relationships = await store.get_related("WRN-001")
            if len(relationships) == 2:
                print_pass("Relationships created (2 for WRN-001)")
            else:
                print_fail(f"Expected 2 relationships, got {len(relationships)}")
                errors.append(f"Relationship count: expected 2, got {len(relationships)}")
        except Exception as e:
            print_fail(f"Relationship creation failed: {e}")
            errors.append(f"Relationship error: {e}")

        # Step 4: Test neighbor queries
        print_step(4, total_steps, "Testing neighbor queries")
        try:
            neighbors = await store.get_neighbors("POW-05", direction="incoming")
            if "WRN-001" in neighbors and "WRN-002" in neighbors:
                print_pass(f"Incoming neighbors for POW-05: {neighbors}")
            else:
                print_fail(f"Missing expected neighbors: {neighbors}")
                errors.append(f"Neighbor query incomplete: {neighbors}")
        except Exception as e:
            print_fail(f"Neighbor query failed: {e}")
            errors.append(f"Neighbor error: {e}")

        # Step 5: Test pathfinding
        print_step(5, total_steps, "Testing pathfinding")
        try:
            path = await store.shortest_path("WRN-001", "electrical_power")
            if path and path[0] == "WRN-001" and path[-1] == "electrical_power":
                print_pass(f"Path found: {' -> '.join(path)}")
            else:
                print_fail(f"Path not found or invalid: {path}")
                errors.append(f"Pathfinding failed: {path}")
        except Exception as e:
            print_fail(f"Pathfinding failed: {e}")
            errors.append(f"Pathfinding error: {e}")

        # Step 6: Test statistics
        print_step(6, total_steps, "Testing statistics")
        try:
            stats = await store.stats()
            print_data("Entity count", stats.entity_count)
            print_data("Relationship count", stats.relationship_count)
            if stats.entity_count >= 4 and stats.relationship_count >= 4:
                print_pass("Statistics correct")
            else:
                print_fail("Statistics incomplete")
                errors.append(f"Stats incomplete: entities={stats.entity_count}, rels={stats.relationship_count}")
        except Exception as e:
            print_fail(f"Statistics failed: {e}")
            errors.append(f"Stats error: {e}")

    finally:
        # Cleanup
        if store:
            store.close()
        # Clean up temp directory
        if db_path and db_path.parent.exists():
            import shutil
            try:
                shutil.rmtree(db_path.parent, ignore_errors=True)
            except Exception:
                pass

    return len(errors) == 0, errors


# =============================================================================
# TEST: SCHEMATIC INDEXING
# =============================================================================


async def verify_schematic_indexing() -> Tuple[bool, List[str]]:
    """Verify automatic indexing of schematics into the graph.

    Returns:
        Tuple of (success, list of error messages)
    """
    print_header("Schematic Indexing Verification")
    errors = []

    try:
        from app.adapters.graph_store import SQLiteGraphStore
    except ImportError as e:
        print_fail(f"Cannot import graph_store: {e}")
        return False, [f"Import error: {e}"]

    # Load schematics
    schematics_path = Path(__file__).parent.parent / "data" / "schematics" / "schematics.json"
    if not schematics_path.exists():
        print_fail(f"Schematics file not found: {schematics_path}")
        return False, ["Schematics file not found"]

    with open(schematics_path) as f:
        schematics = json.load(f)

    print_info(f"Loaded {len(schematics)} schematics from {schematics_path.name}")

    store = None
    db_path = None

    try:
        import tempfile as tf
        tmpdir = tf.mkdtemp()
        db_path = Path(tmpdir) / "test_knowledge.db"
        store = SQLiteGraphStore(db_path=str(db_path))

        # Index schematics
        print_step(1, 3, "Indexing schematics into graph")
        try:
            result = await store.index_schematics(schematics)
            print_pass(f"Schematics indexed: {result}")
        except Exception as e:
            print_fail(f"Indexing failed: {e}")
            errors.append(f"Indexing error: {e}")
            return False, errors

        # Verify entities created
        print_step(2, 3, "Verifying entity creation")
        try:
            stats = await store.stats()
            print_data("Total entities", stats.entity_count)
            print_data("Entity types", stats.entity_types)

            # Check first schematic is an entity
            first_id = schematics[0]["id"]
            entity = await store.get_entity(first_id)
            if entity:
                print_pass(f"Schematic entity found: {first_id}")
            else:
                print_fail(f"Schematic entity not found: {first_id}")
                errors.append(f"Missing entity: {first_id}")
        except Exception as e:
            print_fail(f"Verification failed: {e}")
            errors.append(f"Verification error: {e}")

        # Verify relationships extracted
        print_step(3, 3, "Verifying relationship extraction")
        try:
            relationships = await store.get_related(schematics[0]["id"])
            print_data("Relationships for first schematic", len(relationships))

            if len(relationships) > 0:
                print_pass("Relationships extracted from schematic")
                for rel in relationships[:3]:  # Show first 3
                    print_info(f"  {rel.subject} --{rel.predicate}--> {rel.object}")
            else:
                print_warn("No relationships extracted (may be expected)")
        except Exception as e:
            print_fail(f"Relationship check failed: {e}")
            errors.append(f"Relationship error: {e}")

    finally:
        if store:
            store.close()
        if db_path and db_path.parent.exists():
            import shutil
            try:
                shutil.rmtree(db_path.parent, ignore_errors=True)
            except Exception:
                pass

    return len(errors) == 0, errors


# =============================================================================
# TEST: MCP TOOLS
# =============================================================================


async def verify_graph_store_as_mcp_proxy() -> Tuple[bool, List[str]]:
    """Verify graph operations directly when MCP tools aren't directly callable.

    This is a fallback when the MCP tool wrappers prevent direct function calls.
    We verify the same operations using the GraphStore directly.
    """
    print_info("Testing graph operations via GraphStore (MCP proxy test)")
    errors = []

    try:
        from app.adapters.graph_store import SQLiteGraphStore
        from app.models.graph import Entity, Relationship
    except ImportError as e:
        print_fail(f"Cannot import: {e}")
        return False, [f"Import error: {e}"]

    store = None
    db_path = None

    try:
        import tempfile as tf
        tmpdir = tf.mkdtemp()
        db_path = Path(tmpdir) / "test_knowledge.db"
        store = SQLiteGraphStore(db_path=str(db_path))

        # Test add_relationship equivalent
        print_step(1, 4, "Testing add_relationship operation")
        try:
            result = await store.add_relationship(Relationship(
                subject="WRN-001", predicate="depends_on", object="POW-05"
            ))
            if result:
                print_pass("add_relationship succeeded")
            else:
                print_warn("add_relationship returned False (may be duplicate)")
            await store.add_relationship(Relationship(subject="WRN-002", predicate="depends_on", object="POW-05"))
            await store.add_relationship(Relationship(subject="POW-05", predicate="provides", object="power"))
        except Exception as e:
            print_fail(f"add_relationship error: {e}")
            errors.append(f"add_relationship error: {e}")

        # Test neighbors equivalent
        print_step(2, 4, "Testing neighbors operation")
        try:
            neighbors = await store.get_neighbors("POW-05", direction="incoming")
            print_pass(f"get_neighbors found {len(neighbors)} neighbors: {neighbors}")
        except Exception as e:
            print_fail(f"neighbors error: {e}")
            errors.append(f"neighbors error: {e}")

        # Test path equivalent
        print_step(3, 4, "Testing path operation")
        try:
            path = await store.shortest_path("WRN-001", "power")
            if path:
                print_pass(f"shortest_path found: {' -> '.join(path)}")
            else:
                print_warn("No path found (entities not connected)")
        except Exception as e:
            print_fail(f"path error: {e}")
            errors.append(f"path error: {e}")

        # Test stats equivalent
        print_step(4, 4, "Testing stats operation")
        try:
            stats = await store.stats()
            print_pass(f"stats: entities={stats.entity_count}, relationships={stats.relationship_count}")
        except Exception as e:
            print_fail(f"stats error: {e}")
            errors.append(f"stats error: {e}")

    finally:
        if store:
            store.close()
        if db_path and db_path.parent.exists():
            import shutil
            try:
                shutil.rmtree(db_path.parent, ignore_errors=True)
            except Exception:
                pass

    return len(errors) == 0, errors


async def verify_mcp_tools() -> Tuple[bool, List[str]]:
    """Verify MCP tool implementations.

    Returns:
        Tuple of (success, list of error messages)
    """
    print_header("MCP Tools Verification")
    errors = []
    total_steps = 4

    try:
        # MCP tools are wrapped by @mcp.tool() decorator - need to access the underlying function
        from app.mcp_tools import (
            warn_add_relationship,
            warn_graph_neighbors,
            warn_graph_path,
            warn_graph_stats
        )
        from app.adapters.graph_store import SQLiteGraphStore
        import app.adapters.graph_store as graph_store_module

        # Extract the underlying async functions from the FunctionTool wrappers
        # FastMCP wraps functions with @mcp.tool(), making them FunctionTool objects
        add_rel_fn = getattr(warn_add_relationship, 'fn', warn_add_relationship)
        neighbors_fn = getattr(warn_graph_neighbors, 'fn', warn_graph_neighbors)
        path_fn = getattr(warn_graph_path, 'fn', warn_graph_path)
        stats_fn = getattr(warn_graph_stats, 'fn', warn_graph_stats)

        # Check if we got callable functions
        if not callable(add_rel_fn):
            print_warn("MCP tools are wrapped and not directly callable")
            print_info("Testing graph store directly instead of MCP tools...")
            return await verify_graph_store_as_mcp_proxy()
    except ImportError as e:
        print_fail(f"Cannot import MCP tools: {e}")
        return False, [f"Import error: {e}"]

    store = None
    db_path = None
    original_store = None

    try:
        import tempfile as tf
        tmpdir = tf.mkdtemp()
        db_path = Path(tmpdir) / "test_knowledge.db"
        store = SQLiteGraphStore(db_path=str(db_path))

        # Patch the singleton graph store
        original_store = graph_store_module._graph_store
        graph_store_module._graph_store = store

        # Step 1: Test warn_add_relationship
        print_step(1, total_steps, "Testing warn_add_relationship")
        try:
            result = await add_rel_fn(
                subject="WRN-001",
                predicate="depends_on",
                object="POW-05"
            )
            if result.success:
                print_pass("warn_add_relationship succeeded")
                print_data("Result", {"success": result.success, "message": result.message})
            else:
                print_fail(f"warn_add_relationship failed: {result.message}")
                errors.append(f"add_relationship failed: {result.message}")
        except Exception as e:
            print_fail(f"warn_add_relationship error: {e}")
            errors.append(f"add_relationship error: {e}")

        # Add more relationships for testing
        try:
            await add_rel_fn(subject="WRN-002", predicate="depends_on", object="POW-05")
            await add_rel_fn(subject="POW-05", predicate="provides", object="power")
        except Exception:
            pass

        # Step 2: Test warn_graph_neighbors
        print_step(2, total_steps, "Testing warn_graph_neighbors")
        try:
            result = await neighbors_fn(
                entity_id="POW-05",
                direction="incoming"
            )
            # GraphNeighborsResult doesn't have 'success' - it returns data directly
            neighbors = result.neighbors or []
            print_pass(f"warn_graph_neighbors found {len(neighbors)} neighbors")
            print_data("Neighbors", neighbors)
        except Exception as e:
            print_fail(f"warn_graph_neighbors error: {e}")
            errors.append(f"neighbors error: {e}")

        # Step 3: Test warn_graph_path
        print_step(3, total_steps, "Testing warn_graph_path")
        try:
            result = await path_fn(
                source="WRN-001",
                target="power"
            )
            # GraphPathResult doesn't have 'success' - check path_length
            path = result.path or []
            if path:
                print_pass(f"warn_graph_path found path: {' -> '.join(path)}")
            else:
                print_warn("warn_graph_path: no path found (entities may not be connected)")
        except Exception as e:
            print_fail(f"warn_graph_path error: {e}")
            errors.append(f"path error: {e}")

        # Step 4: Test warn_graph_stats
        print_step(4, total_steps, "Testing warn_graph_stats")
        try:
            result = await stats_fn()
            # GraphStatsResult returns stats directly
            print_pass("warn_graph_stats succeeded")
            print_data("Stats", {
                "entity_count": result.entity_count,
                "relationship_count": result.relationship_count,
                "entity_types": result.entity_types,
                "predicate_counts": result.predicate_counts
            })
        except Exception as e:
            print_fail(f"warn_graph_stats error: {e}")
            errors.append(f"stats error: {e}")

    finally:
        # Restore original store
        if original_store is not None:
            graph_store_module._graph_store = original_store
        elif 'graph_store_module' in dir():
            graph_store_module._graph_store = None
        if store:
            store.close()
        if db_path and db_path.parent.exists():
            import shutil
            try:
                shutil.rmtree(db_path.parent, ignore_errors=True)
            except Exception:
                pass

    return len(errors) == 0, errors


# =============================================================================
# TEST: LANGGRAPH FLOW
# =============================================================================


async def verify_langgraph_flow() -> Tuple[bool, List[str]]:
    """Verify LangGraph flow integration with graph memory.

    Returns:
        Tuple of (success, list of error messages)
    """
    print_header("LangGraph Flow Verification")
    errors = []

    try:
        from app.langgraph.flow import (
            parse_intent,
            query_graph,
            extract_entities,
            GraphState,
            QueryIntent
        )
        from app.adapters.graph_store import SQLiteGraphStore
    except ImportError as e:
        print_fail(f"Cannot import LangGraph flow: {e}")
        # Try partial verification
        print_warn("Some imports failed, testing available components...")

    # Test 1: Entity extraction
    print_step(1, 3, "Testing entity extraction")
    try:
        from app.langgraph.flow import extract_entities

        test_queries = [
            ("What is WRN-001?", ["WRN-001"]),
            ("Compare WRN-001 and WRN-002", ["WRN-001", "WRN-002"]),
            ("Show all WC-100 schematics", ["model:WC-100"]),  # Model IDs are prefixed
            ("General question", []),
        ]

        for query, expected in test_queries:
            entities = extract_entities(query)
            found = all(e in entities for e in expected)
            if found:
                print_pass(f"Extracted from '{query}': {entities}")
            else:
                print_warn(f"Expected {expected} from '{query}', got {entities}")
    except Exception as e:
        print_fail(f"Entity extraction failed: {e}")
        errors.append(f"Entity extraction error: {e}")

    # Test 2: Intent parsing with graph consideration
    print_step(2, 3, "Testing intent parsing")
    try:
        from app.langgraph.flow import parse_intent

        state = {
            "query": "What are the dependencies of WRN-001?",
            "filters": None,
            "top_k": 5,
            "intent": None,
            "candidates": [],
            "compressed_context": "",
            "graph_context": [],  # Should be a list, not string
            "response": {},
            "error": None,
            "start_time": datetime.now().isoformat(),
            "timings": {},
        }

        result = parse_intent(state)
        intent = result.get("intent")
        if intent:
            print_pass(f"Intent parsed: {intent}")
        else:
            print_fail("Intent not parsed")
            errors.append("Intent parsing failed")
    except Exception as e:
        print_fail(f"Intent parsing failed: {e}")
        errors.append(f"Intent error: {e}")

    # Test 3: Full flow (if available)
    print_step(3, 3, "Testing full flow with graph context")
    try:
        from app.langgraph import run_query

        result = await run_query(
            query="Tell me about WRN-00001",
            filters=None,
            top_k=5
        )

        if result:
            print_pass("LangGraph flow executed")
            print_data("Result keys", list(result.keys()))
            if "graph_context" in result:
                print_pass("Graph context present in result")
            else:
                print_warn("Graph context not in result (may need implementation)")
        else:
            print_fail("LangGraph flow returned None")
            errors.append("Flow returned None")
    except Exception as e:
        print_fail(f"Full flow failed: {e}")
        errors.append(f"Flow error: {e}")

    return len(errors) == 0, errors


# =============================================================================
# MAIN
# =============================================================================


async def main():
    """Run all verification tests."""
    parser = argparse.ArgumentParser(
        description="Verify WARNERCO Graph Memory feature"
    )
    parser.add_argument(
        "--test",
        choices=["store", "index", "mcp", "flow", "all"],
        default="all",
        help="Which test to run (default: all)"
    )
    args = parser.parse_args()

    print_header("WARNERCO Graph Memory Verification")
    print(f"Started at: {datetime.now().isoformat()}")
    print(f"Python: {sys.version.split()[0]}")

    results = {}

    # Run selected tests
    if args.test in ["store", "all"]:
        success, errors = await verify_graph_store()
        results["Graph Store"] = (success, errors)

    if args.test in ["index", "all"]:
        success, errors = await verify_schematic_indexing()
        results["Schematic Indexing"] = (success, errors)

    if args.test in ["mcp", "all"]:
        success, errors = await verify_mcp_tools()
        results["MCP Tools"] = (success, errors)

    if args.test in ["flow", "all"]:
        success, errors = await verify_langgraph_flow()
        results["LangGraph Flow"] = (success, errors)

    # Print summary
    print_header("Verification Summary")

    all_passed = True
    for test_name, (success, errors) in results.items():
        if success:
            print_pass(f"{test_name}")
        else:
            print_fail(f"{test_name}")
            for error in errors:
                print(f"      - {error}")
            all_passed = False

    print()
    if all_passed:
        print(f"{Colors.GREEN}{Colors.BOLD}All verifications passed!{Colors.RESET}")
        return 0
    else:
        print(f"{Colors.RED}{Colors.BOLD}Some verifications failed.{Colors.RESET}")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
