# Tutorial: Knowledge Graphs for Context Engineering

This hands-on tutorial teaches you to use the Graph Memory feature in WARNERCO Schematica. You will build and query a knowledge graph, then combine graph context with semantic search for hybrid retrieval-augmented generation (RAG).

## Learning Objectives

By the end of this tutorial, you will:

- Understand the difference between graph-based and vector-based retrieval
- Build a knowledge graph from structured data
- Query relationships using MCP tools
- Combine graph and vector context for richer AI responses

## Prerequisites

Before starting, ensure you have:

- Completed [Lab 01: Hello MCP](../../labs/lab-01-hello-mcp/README.md)
- WARNERCO Schematica running locally (see setup below)
- Basic familiarity with Python and MCP concepts
- Claude Desktop or VS Code with MCP configured

### Quick Setup Check

```bash
# Navigate to the WARNERCO backend (from repository root)
cd src/warnerco/backend

# Install dependencies
uv sync

# Start the HTTP server
uv run uvicorn app.main:app --reload
```

Visit http://localhost:8000/docs to confirm the API is running.

## Part 1: Understanding Knowledge Graphs (10 minutes)

### What is a Knowledge Graph?

A knowledge graph represents information as **entities** (nodes) connected by **relationships** (edges). Each relationship is a **triplet**: subject, predicate, object.

```
[Atlas Prime] --depends_on--> [Force Feedback Sensor]
   subject        predicate          object
```

Think of it as a network of facts. Unlike a flat database table, a graph makes connections explicit and traversable.

### Graph Terminology

| Term | Definition | Example |
|------|------------|---------|
| **Entity** | A thing with an identity | Robot "WRN-00001", Component "thermal_mgmt" |
| **Relationship** | A directed connection | "depends_on", "contains", "compatible_with" |
| **Triplet** | Subject + Predicate + Object | (WRN-00001, depends_on, POW-SYSTEM) |
| **Neighbor** | Directly connected entity | All entities one hop away |
| **Path** | Sequence of relationships | WRN-00001 -> POW-SYSTEM -> WRN-00003 |

### When to Use Graphs vs. Vectors

Both retrieval methods have strengths. Use them together for hybrid RAG.

| Query Type | Vector Search | Graph Query | Best Approach |
|------------|--------------|-------------|---------------|
| "Find robots similar to Atlas Prime" | Excellent | Poor | Vector |
| "What depends on the power system?" | Poor | Excellent | Graph |
| "Robots with thermal issues" | Good | Good | Hybrid |
| "How is WRN-001 connected to WRN-005?" | Cannot answer | Excellent | Graph |
| "Mobile robots for reconnaissance" | Excellent | Moderate | Vector |

**Key insight**: Vectors find *similar* things. Graphs find *connected* things.

### The WARNERCO Graph Model

WARNERCO Schematica uses this graph structure:

```
Entity Types:
  - robot: Full schematic records (WRN-00001, WRN-00002, ...)
  - component: Named components (force_feedback_sensor, thermal_mgmt_unit, ...)
  - category: Classification (sensors, power, manipulation, ...)
  - system: Cross-cutting systems (POW-SYSTEM, THERMAL-SYSTEM, ...)

Relationship Types (Predicates):
  - depends_on: Component dependency
  - contains: Containment (robot contains component)
  - has_status: Status assignment
  - manufactured_by: Manufacturer link
  - compatible_with: Compatibility between schematics
  - related_to: General association
```

## Part 2: Building the Graph (15 minutes)

### Step 1: Index the Schematics

The `index_graph.py` script reads `schematics.json` and creates the knowledge graph.

```bash
# From repository root
cd src/warnerco/backend
uv run python scripts/index_graph.py
```

Expected output:

```
Loading schematics from data/schematics/schematics.json...
Found 25 schematics
Creating entities...
  - 25 robot entities
  - 12 component entities
  - 6 category entities
  - 4 system entities
Inferring relationships...
  - 25 robot->category relationships
  - 18 robot->system relationships
  - 12 component->robot relationships
Writing to graph.db...
Building NetworkX graph...
Done! Graph has 47 nodes and 55 edges.
```

### Step 2: Verify the Graph

Use the MCP Inspector to verify the graph was created:

```bash
# In a separate terminal
npx @modelcontextprotocol/inspector uv run warnerco-mcp
```

In the Inspector UI:

1. Navigate to the "Tools" tab
2. Find `warn_graph_stats`
3. Click "Execute"

You should see:

```json
{
  "node_count": 47,
  "edge_count": 55,
  "density": 0.025,
  "connected_components": 1,
  "predicates": {
    "depends_on": 18,
    "contains": 12,
    "has_category": 25
  }
}
```

### Step 3: Explore the Graph Structure

Let's examine a specific robot's connections. In the Inspector, use `warn_graph_neighbors`:

**Input**:
```json
{
  "entity_id": "WRN-00001"
}
```

**Expected output**:
```json
{
  "entity_id": "WRN-00001",
  "neighbors": [
    {
      "id": "sensors",
      "predicate": "has_category",
      "direction": "outgoing"
    },
    {
      "id": "force_feedback_sensor",
      "predicate": "contains",
      "direction": "outgoing"
    },
    {
      "id": "SENSOR-SYSTEM",
      "predicate": "depends_on",
      "direction": "outgoing"
    }
  ]
}
```

This tells us WRN-00001 (Atlas Prime) is in the "sensors" category, contains a "force_feedback_sensor" component, and depends on the "SENSOR-SYSTEM."

### Step 4: Add a Custom Relationship

Now add your own relationship. Perhaps WRN-00001 is compatible with WRN-00005 (both are WC-100 models):

**Tool**: `warn_add_relationship`

**Input**:
```json
{
  "subject": "WRN-00001",
  "predicate": "compatible_with",
  "object": "WRN-00005",
  "metadata": {
    "reason": "Same WC-100 platform",
    "added_by": "tutorial"
  }
}
```

**Expected output**:
```json
{
  "success": true,
  "relationship_id": "rel_abc123",
  "message": "Relationship created: WRN-00001 compatible_with WRN-00005"
}
```

Verify by checking neighbors again - WRN-00005 should now appear.

## Part 3: Querying the Graph (15 minutes)

### Finding Neighbors

Neighbor queries are the most common graph operation. They answer: "What is directly connected to X?"

**Use case**: Troubleshooting a failing robot.

In Claude Desktop or your MCP-enabled chat:

```
User: What systems does WRN-00002 depend on?
```

Claude will use `warn_graph_neighbors` to find outgoing "depends_on" relationships, providing a precise answer instead of guessing from semantic similarity.

**Try these neighbor queries**:

1. "Show me all robots in the sensors category"
   - Graph finds: All entities with "has_category" -> "sensors"

2. "What components does the Hercules Lifter contain?"
   - Graph finds: Outgoing "contains" relationships from WRN-00006

3. "Which robots depend on the power system?"
   - Graph finds: All entities with "depends_on" -> "POW-SYSTEM"

### Path Finding

Path queries answer: "How are X and Y connected?"

**Use case**: Understanding indirect dependencies.

**Tool**: `warn_graph_path`

**Input**:
```json
{
  "source_id": "WRN-00001",
  "target_id": "WRN-00006",
  "max_hops": 4
}
```

**Expected output**:
```json
{
  "path_found": true,
  "length": 3,
  "path": [
    {"entity": "WRN-00001", "predicate": "has_category", "next": "sensors"},
    {"entity": "sensors", "predicate": "has_category", "next": "WRN-00004"},
    {"entity": "WRN-00004", "predicate": "related_to", "next": "WRN-00006"}
  ]
}
```

This shows the connection chain between Atlas Prime and Hercules Lifter.

**Try these path queries**:

1. "How is WRN-00003 connected to WRN-00007?"
2. "Find the path from the battery management system to the hydraulic actuator"
3. "What's the shortest route between sensors and power categories?"

### Combining Graph and Text Queries

The real power comes from combining graph structure with natural language:

```
User: I'm having thermal issues with robots that depend on the power system.
      Which schematics should I check?
```

Behind the scenes, WARNERCO:
1. Parses intent as DIAGNOSTIC
2. Uses graph to find all robots depending on POW-SYSTEM
3. Filters to those in "thermal" category or with thermal components
4. Retrieves semantic matches for "thermal issues"
5. Combines and ranks results

## Part 4: Hybrid RAG in Action (10 minutes)

### How the LangGraph Flow Works

The 7-node pipeline:

```
1. parse_intent      - Classify query (LOOKUP, DIAGNOSTIC, ANALYTICS, SEARCH)
2. query_graph       - Find graph context if intent benefits from it
3. inject_scratchpad - Add session working memory (observations, inferences)
4. retrieve          - Get candidates from vector store (boosted by graph context)
5. compress_context  - Minimize tokens while preserving key info
6. reason            - LLM synthesizes response
7. respond           - Format final output
```

### When Does query_graph Activate?

The node runs when:
- Intent is DIAGNOSTIC (relationships often matter)
- Intent is ANALYTICS (aggregations benefit from structure)
- Query mentions explicit relationships ("depends on", "connected to", "related to")

It skips for pure semantic searches like "find robots for precision handling."

### Observing Hybrid Retrieval

Use the `/api/search` endpoint with verbose output:

```bash
curl -X POST http://localhost:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What robots depend on thermal management and have sensor issues?",
    "verbose": true
  }'
```

Response includes timing breakdown:

```json
{
  "results": [...],
  "timings": {
    "parse_intent": 2.1,
    "query_graph": 8.4,
    "retrieve": 45.2,
    "compress_context": 3.1,
    "reason": 234.5,
    "respond": 1.2
  },
  "graph_context": {
    "entities_found": ["WRN-00002", "WRN-00012"],
    "relationships_used": 4
  }
}
```

### Try It Yourself

Open Claude Desktop with WARNERCO configured and try these prompts:

**Pure vector search** (graph adds little):
```
Find robots designed for mobile reconnaissance.
```

**Graph-enhanced** (relationships matter):
```
What components does WRN-00004 contain, and are any of them failing?
```

**Hybrid** (both contribute):
```
I need to service the thermal systems. Which robots are affected and what are their statuses?
```

Notice how responses differ in precision and completeness depending on the query type.

## Summary

You have learned:

1. **Graph vs. Vector**: Graphs find connections; vectors find similarities. Use both.

2. **WARNERCO Graph Model**: Entities (robots, components, categories, systems) connected by predicates (depends_on, contains, compatible_with, etc.).

3. **MCP Tools**: Four tools expose graph functionality:
   - `warn_add_relationship` - Create triplets
   - `warn_graph_neighbors` - Find connections
   - `warn_graph_path` - Find shortest paths
   - `warn_graph_stats` - Graph metrics

4. **Hybrid RAG**: The LangGraph flow's `query_graph` node enriches context before vector retrieval, producing more accurate responses for relationship-heavy queries.

## Exercises

**Exercise 1**: Add 5 new "compatible_with" relationships between robots that share the same model (WC-100, WC-200, etc.). Then query to find all robots compatible with WRN-00001.

**Exercise 2**: Use `warn_graph_path` to find the connection between the farthest-apart entities in the graph. What's the longest shortest path?

**Exercise 3**: Modify your queries to compare responses with and without graph context. Which query types benefit most from the graph?

## Next Steps

- Review the [Graph Memory Architecture](../diagrams/graph-memory-architecture.md) for technical details
- Explore the [Graph API Reference](../api/graph-api.md) for complete tool documentation
- Try [building your own graph-enhanced MCP server](../../labs/) using these patterns

## Troubleshooting

**Graph is empty after indexing**

Check that `schematics.json` exists and is valid:
```bash
cat data/schematics/schematics.json | python -m json.tool
```

**"Entity not found" errors**

Entity IDs are case-sensitive. Use exact IDs from the schematics (e.g., "WRN-00001" not "wrn-00001").

**Slow graph queries**

The NetworkX graph loads on first query. Subsequent queries should be fast (<10ms). If still slow, check if `graph.db` is very large or corrupted.

**MCP tools not appearing**

Restart the MCP server and reconnect Claude Desktop. Verify with MCP Inspector that all 4 graph tools are listed.
