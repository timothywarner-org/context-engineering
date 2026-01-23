"""Index schematics.json into the Knowledge Graph.

This script populates the Knowledge Graph from the schematics.json file.
It extracts entities and relationships to enable graph-based queries
that complement semantic search.

Extracted Entities:
- Schematics (WRN-XXXXX)
- Statuses (status:active, status:deprecated, status:draft)
- Categories (category:sensors, category:power, etc.)
- Models (model:WC-100, model:WC-200, etc.)
- Components (component:hydraulic_system, component:sensor_array, etc.)
- Tags (tag:precision, tag:industrial, etc.)

Extracted Relationships:
- has_status: Schematic -> Status
- has_category: Schematic -> Category
- belongs_to_model: Schematic -> Model
- contains: Schematic -> Component (inferred from description)
- has_tag: Schematic -> Tag
- compatible_with: Schematic <-> Schematic (same model)

Usage:
    # From the backend directory:
    uv run python scripts/index_graph.py

    # Or with explicit Python:
    python scripts/index_graph.py
"""

import json
import sys
from pathlib import Path

# Add parent to path for imports
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))


def main():
    """Index schematics into the Knowledge Graph."""
    import asyncio
    from app.adapters.graph_store import GraphStore
    from app.models.graph import Entity, Relationship

    # Paths
    schematics_path = backend_dir / "data" / "schematics" / "schematics.json"
    db_path = backend_dir / "data" / "graph" / "knowledge.db"

    print(f"Loading schematics from {schematics_path}")

    if not schematics_path.exists():
        print(f"ERROR: Schematics file not found: {schematics_path}")
        sys.exit(1)

    with open(schematics_path, "r", encoding="utf-8") as f:
        schematics = json.load(f)

    print(f"Found {len(schematics)} schematics")

    # Initialize the graph store (creates database if needed)
    print(f"Initializing Knowledge Graph at {db_path}")
    graph_store = GraphStore(db_path=db_path)

    async def do_index():
        """Async indexing function."""
        result = await graph_store.index_schematics(schematics)
        return result

    # Run the async indexing
    print("\nIndexing schematics into Knowledge Graph...")
    result = asyncio.run(do_index())

    print(f"\nIndexing complete!")
    print(f"  Entities added: {result['entities_added']}")
    print(f"  Relationships added: {result['relationships_added']}")
    print(f"  Total entities: {result['total_entities']}")
    print(f"  Total relationships: {result['total_relationships']}")

    # Print graph statistics
    async def get_stats():
        return await graph_store.stats()

    stats = asyncio.run(get_stats())

    print(f"\n=== Knowledge Graph Statistics ===")
    print(f"Entity Types:")
    for entity_type, count in sorted(stats.entity_types.items()):
        print(f"  {entity_type}: {count}")

    print(f"\nPredicate Types:")
    for predicate, count in sorted(stats.predicate_counts.items()):
        print(f"  {predicate}: {count}")

    # Clean up
    graph_store.close()

    print(f"\nKnowledge Graph database saved to: {db_path}")
    print("Done!")


if __name__ == "__main__":
    main()
