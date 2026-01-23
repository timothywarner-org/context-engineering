# Graph Memory API Reference

Complete reference for Graph Memory MCP tools and REST endpoints in WARNERCO Schematica.

## MCP Tools

### warn_add_relationship

Creates a relationship (triplet) in the knowledge graph. Relationships are directed edges connecting a subject entity to an object entity via a predicate.

**Parameters**:

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `subject` | string | Yes | Source entity ID (e.g., "WRN-00001") |
| `predicate` | string | Yes | Relationship type (see supported predicates) |
| `object` | string | Yes | Target entity ID (e.g., "POW-SYSTEM") |
| `metadata` | object | No | Additional context (timestamp, source, confidence) |

**Supported Predicates**:

| Predicate | Description | Example Usage |
|-----------|-------------|---------------|
| `depends_on` | Component or system dependency | Robot depends on power system |
| `contains` | Containment relationship | Robot contains sensor component |
| `has_status` | Status assignment | Schematic has status "active" |
| `manufactured_by` | Manufacturing attribution | Component manufactured by vendor |
| `compatible_with` | Compatibility declaration | Robot A compatible with Robot B |
| `related_to` | General association | Catch-all for loose relationships |

**Example Request**:

```json
{
  "subject": "WRN-00001",
  "predicate": "compatible_with",
  "object": "WRN-00005",
  "metadata": {
    "reason": "Same WC-100 platform, shared components",
    "confidence": 0.95,
    "added_by": "manual"
  }
}
```

**Example Response**:

```json
{
  "success": true,
  "relationship_id": "rel_a7f3b2c1",
  "message": "Relationship created: WRN-00001 compatible_with WRN-00005",
  "timestamp": "2025-01-22T14:30:00Z"
}
```

**Error Cases**:

| Error | Cause | Resolution |
|-------|-------|------------|
| `invalid_predicate` | Predicate not in allowed list | Use a supported predicate |
| `entity_not_found` | Subject or object does not exist | Verify entity IDs exist |
| `duplicate_relationship` | Exact triplet already exists | Relationship already recorded |

**Notes**:
- Relationships are idempotent; adding the same triplet twice has no effect
- Metadata is optional but recommended for audit trails
- Entity IDs are case-sensitive; use exact IDs from schematics

---

### warn_graph_neighbors

Returns all entities directly connected to a given entity. Supports filtering by relationship direction.

**Parameters**:

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `entity_id` | string | Yes | - | The entity to query neighbors for |
| `direction` | string | No | `"both"` | Filter by edge direction: `"incoming"`, `"outgoing"`, or `"both"` |
| `predicate` | string | No | - | Filter to specific relationship type |
| `limit` | integer | No | 50 | Maximum neighbors to return |

**Direction Explained**:

- `"outgoing"`: Relationships where `entity_id` is the subject (entity --> neighbor)
- `"incoming"`: Relationships where `entity_id` is the object (neighbor --> entity)
- `"both"`: All connected entities regardless of direction

**Example Request**:

```json
{
  "entity_id": "WRN-00001",
  "direction": "outgoing"
}
```

**Example Response**:

```json
{
  "entity_id": "WRN-00001",
  "neighbors": [
    {
      "id": "sensors",
      "type": "category",
      "predicate": "has_category",
      "direction": "outgoing",
      "metadata": {}
    },
    {
      "id": "force_feedback_sensor",
      "type": "component",
      "predicate": "contains",
      "direction": "outgoing",
      "metadata": {}
    },
    {
      "id": "SENSOR-SYSTEM",
      "type": "system",
      "predicate": "depends_on",
      "direction": "outgoing",
      "metadata": {}
    },
    {
      "id": "WRN-00005",
      "type": "robot",
      "predicate": "compatible_with",
      "direction": "outgoing",
      "metadata": {
        "reason": "Same WC-100 platform"
      }
    }
  ],
  "total_count": 4
}
```

**Use Cases**:
- Find all components a robot contains
- Discover what depends on a specific system
- List robots in a category
- Find compatible schematics

---

### warn_graph_path

Finds the shortest path between two entities in the graph. Uses breadth-first search for unweighted shortest path.

**Parameters**:

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `source_id` | string | Yes | - | Starting entity ID |
| `target_id` | string | Yes | - | Destination entity ID |
| `max_hops` | integer | No | 5 | Maximum path length to search |
| `predicate_filter` | array | No | - | Only traverse these relationship types |

**Example Request**:

```json
{
  "source_id": "WRN-00001",
  "target_id": "WRN-00006",
  "max_hops": 4
}
```

**Example Response** (path found):

```json
{
  "path_found": true,
  "source_id": "WRN-00001",
  "target_id": "WRN-00006",
  "length": 3,
  "path": [
    {
      "from": "WRN-00001",
      "predicate": "has_category",
      "to": "sensors",
      "direction": "outgoing"
    },
    {
      "from": "sensors",
      "predicate": "has_category",
      "to": "WRN-00004",
      "direction": "incoming"
    },
    {
      "from": "WRN-00004",
      "predicate": "related_to",
      "to": "WRN-00006",
      "direction": "outgoing"
    }
  ]
}
```

**Example Response** (no path):

```json
{
  "path_found": false,
  "source_id": "WRN-00001",
  "target_id": "DISCONNECTED-NODE",
  "message": "No path found within 5 hops"
}
```

**Use Cases**:
- Understand indirect dependencies
- Discover how two robots are related
- Trace component relationships
- Visualize connection chains

---

### warn_graph_stats

Returns aggregate statistics about the knowledge graph.

**Parameters**: None

**Example Response**:

```json
{
  "node_count": 47,
  "edge_count": 55,
  "density": 0.0254,
  "connected_components": 1,
  "predicates": {
    "depends_on": 18,
    "contains": 12,
    "has_category": 25,
    "compatible_with": 3,
    "related_to": 2
  },
  "entity_types": {
    "robot": 25,
    "component": 12,
    "category": 6,
    "system": 4
  },
  "graph_diameter": 6,
  "average_degree": 2.34,
  "last_updated": "2025-01-22T14:00:00Z"
}
```

**Metrics Explained**:

| Metric | Description |
|--------|-------------|
| `node_count` | Total entities in the graph |
| `edge_count` | Total relationships (triplets) |
| `density` | Edge count / max possible edges (0-1 scale) |
| `connected_components` | Number of disconnected subgraphs (1 = fully connected) |
| `predicates` | Breakdown by relationship type |
| `entity_types` | Breakdown by entity type |
| `graph_diameter` | Longest shortest path between any two nodes |
| `average_degree` | Average connections per node |

---

## REST API Endpoints

### GET /api/graph/stats

Returns graph statistics (same as `warn_graph_stats` tool).

**Request**:

```bash
curl http://localhost:8000/api/graph/stats
```

**Response**: Same as `warn_graph_stats`

---

### GET /api/graph/neighbors/{entity_id}

Returns neighbors of an entity.

**Path Parameters**:

| Name | Type | Description |
|------|------|-------------|
| `entity_id` | string | The entity to query |

**Query Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `direction` | string | `"both"` | `"incoming"`, `"outgoing"`, or `"both"` |
| `predicate` | string | - | Filter by relationship type |
| `limit` | integer | 50 | Maximum results |

**Request**:

```bash
curl "http://localhost:8000/api/graph/neighbors/WRN-00001?direction=outgoing"
```

**Response**: Same as `warn_graph_neighbors`

---

### POST /api/graph/path

Finds shortest path between entities.

**Request Body**:

```json
{
  "source_id": "WRN-00001",
  "target_id": "WRN-00006",
  "max_hops": 4
}
```

**Request**:

```bash
curl -X POST http://localhost:8000/api/graph/path \
  -H "Content-Type: application/json" \
  -d '{"source_id": "WRN-00001", "target_id": "WRN-00006"}'
```

**Response**: Same as `warn_graph_path`

---

### POST /api/graph/relationships

Creates a new relationship.

**Request Body**:

```json
{
  "subject": "WRN-00001",
  "predicate": "compatible_with",
  "object": "WRN-00005",
  "metadata": {"reason": "Same platform"}
}
```

**Request**:

```bash
curl -X POST http://localhost:8000/api/graph/relationships \
  -H "Content-Type: application/json" \
  -d '{"subject": "WRN-00001", "predicate": "compatible_with", "object": "WRN-00005"}'
```

**Response**: Same as `warn_add_relationship`

---

## Data Models

### Entity

```python
class Entity(BaseModel):
    """A node in the knowledge graph."""

    id: str                      # Unique identifier (e.g., "WRN-00001")
    type: str                    # Entity type (robot, component, category, system)
    properties: Dict[str, Any]   # Additional properties (name, model, etc.)
```

### Relationship

```python
class Relationship(BaseModel):
    """A directed edge in the knowledge graph."""

    id: str                      # Auto-generated relationship ID
    subject: str                 # Source entity ID
    predicate: str               # Relationship type
    object: str                  # Target entity ID
    metadata: Dict[str, Any]     # Optional context (timestamp, source, etc.)
    created_at: datetime         # Creation timestamp
```

### GraphQueryResult

```python
class GraphQueryResult(BaseModel):
    """Result from a graph query."""

    entity_id: str
    neighbors: List[NeighborInfo]
    total_count: int

class NeighborInfo(BaseModel):
    """Information about a neighboring entity."""

    id: str
    type: str
    predicate: str
    direction: Literal["incoming", "outgoing"]
    metadata: Dict[str, Any]
```

---

## Error Responses

All endpoints return consistent error responses:

```json
{
  "success": false,
  "error": {
    "code": "entity_not_found",
    "message": "Entity 'WRN-99999' does not exist in the graph",
    "details": {
      "entity_id": "WRN-99999",
      "suggestion": "Verify the entity ID matches a schematic in the database"
    }
  }
}
```

**Common Error Codes**:

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `entity_not_found` | 404 | Referenced entity does not exist |
| `invalid_predicate` | 400 | Predicate not in allowed list |
| `invalid_direction` | 400 | Direction must be incoming/outgoing/both |
| `path_not_found` | 200 | No path exists (not an error, part of response) |
| `graph_not_initialized` | 503 | Graph store not yet loaded |
| `max_hops_exceeded` | 400 | max_hops parameter too large (limit: 10) |

---

## Performance Considerations

### Latency Expectations

| Operation | Typical Latency | Notes |
|-----------|-----------------|-------|
| `warn_graph_stats` | <5ms | Cached metrics |
| `warn_graph_neighbors` | <2ms | NetworkX adjacency |
| `warn_graph_path` | <15ms | BFS, depends on graph size |
| `warn_add_relationship` | <10ms | SQLite write + NetworkX update |

### Scaling Notes

- Graph loads into memory on first query (~100ms for 50 nodes)
- Subsequent queries use in-memory NetworkX graph
- SQLite persists relationships across restarts
- For >10,000 nodes, consider Neo4j instead

---

## See Also

- [Graph Memory Architecture](../diagrams/graph-memory-architecture.md) - System design
- [Graph Memory Tutorial](../tutorials/graph-memory-tutorial.md) - Hands-on guide
- [WARNERCO Schematica Overview](../../CLAUDE.md#warnerco-schematica-architecture) - System context
