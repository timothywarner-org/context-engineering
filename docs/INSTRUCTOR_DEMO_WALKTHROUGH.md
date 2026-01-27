# WARNERCO Schematica - Instructor Demo Walkthrough

**For Tim Warner's O'Reilly Course**

This document provides step-by-step demo instructions with real sample data, prompts, and expected outputs. Everything is ready to copy-paste.

---

## Table of Contents

- [A. Starting the Apps](#a-starting-the-apps)
- [B. Testing Schematica Dashboard](#b-testing-schematica-dashboard)
- [C. Testing with MCP Inspector](#c-testing-with-mcp-inspector)
- [D. Testing in VS Code / GitHub Copilot](#d-testing-in-vs-code--github-copilot)
- [E. Testing Scratchpad Memory](#e-testing-scratchpad-memory)
- [F. Graph Memory Demo](#f-graph-memory-demo)
- [G. Full RAG Pipeline Demo](#g-full-rag-pipeline-demo)
- [Quick Reference](#quick-reference)

---

## A. Starting the Apps

### 1. Navigate to the Backend Directory

```bash
cd src/warnerco/backend
```

### 2. Install Dependencies (if not already done)

```bash
uv sync
```

### 3. Start the FastAPI Server

```bash
uv run uvicorn app.main:app --reload
```

### Expected Console Output

```
INFO:     Will watch for changes in these directories: ['C:\\github\\context-engineering\\src\\warnerco\\backend']
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using WatchFiles
Starting WARNERCO Robotics Schematica...
Memory Backend: json
Debug Mode: True
Loaded 25 schematics
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### 4. Verify the Server is Running

Open a browser to: **http://localhost:8000**

You should be redirected to the dashboard at `/dash/`

### Alternative: Start MCP Stdio Server (for Claude Desktop)

If you want to test with Claude Desktop instead:

```bash
uv run warnerco-mcp
```

This starts the server in stdio mode for MCP client connections.

---

## B. Testing Schematica Dashboard

### Dashboard URLs

| URL | Description |
|-----|-------------|
| http://localhost:8000/dash/ | Main dashboard |
| http://localhost:8000/dash/schematics/ | Browse schematics |
| http://localhost:8000/dash/memory/ | Memory backend stats |
| http://localhost:8000/dash/scratchpad/ | Scratchpad memory viewer |
| http://localhost:8000/docs | OpenAPI documentation |

### What Students Will See

#### Main Dashboard (`/dash/`)

The main dashboard shows:
- WARNERCO Robotics Schematica title
- Three feature cards:
  - **Semantic Search** - Natural language queries powered by vector embeddings
  - **LangGraph Orchestration** - RAG pipeline with intent classification
  - **MCP Integration** - FastMCP tools for AI assistants
- Quick Start section with API endpoints and MCP tools list
- Navigation to Schematics, Memory, Scratchpad, and API Docs

#### Schematics Browser (`/dash/schematics/`)

- Grid of schematic cards
- Filter by category (sensors, power, control, etc.)
- Filter by status (active, deprecated, draft)
- Click on any schematic to see details

#### Memory Dashboard (`/dash/memory/`)

- Shows active memory backend (json, chroma, or azure_search)
- Total schematics count
- Category breakdown pie chart
- Status distribution

#### Scratchpad Dashboard (`/dash/scratchpad/`)

- Current token usage vs budget
- List of scratchpad entries
- Predicate type distribution
- Clear/refresh controls

### API Docs Demo

Navigate to http://localhost:8000/docs to show:
- Interactive Swagger UI
- All API endpoints
- Try out endpoints directly

---

## C. Testing with MCP Inspector

### Launch MCP Inspector

```bash
npx @modelcontextprotocol/inspector uv run warnerco-mcp
```

Opens web UI at: **http://localhost:5173**

### Demo Sequence

#### Step 1: List All Robots

**Tool:** `warn_list_robots`

**Parameters:** (leave all empty for all schematics)
```json
{}
```

**Expected Output (abbreviated):**
```json
{
  "count": 25,
  "schematics": [
    {
      "id": "WRN-00001",
      "model": "WC-100",
      "name": "Atlas Prime",
      "component": "force feedback sensor array",
      "category": "sensors",
      "status": "active",
      "version": "v3.4"
    },
    {
      "id": "WRN-00002",
      "model": "WC-200",
      "name": "Titan Handler",
      "component": "thermal management unit",
      "category": "thermal",
      "status": "active",
      "version": "v2.1"
    }
    // ... 23 more schematics
  ]
}
```

#### Step 2: Filter by Category

**Tool:** `warn_list_robots`

**Parameters:**
```json
{
  "category": "sensors",
  "status": "active"
}
```

**Expected Output:**
```json
{
  "count": 8,
  "schematics": [
    {
      "id": "WRN-00001",
      "model": "WC-100",
      "name": "Atlas Prime",
      "component": "force feedback sensor array",
      "category": "sensors",
      "status": "active",
      "version": "v3.4"
    },
    {
      "id": "WRN-00004",
      "model": "WC-400",
      "name": "Aegis Guardian",
      "component": "vision processing module",
      "category": "sensors",
      "status": "active",
      "version": "v4.0"
    },
    {
      "id": "WRN-00007",
      "model": "WC-300",
      "name": "Nimbus Scout",
      "component": "LIDAR navigation module",
      "category": "sensors",
      "status": "active",
      "version": "v2.0"
    },
    {
      "id": "WRN-00012",
      "model": "WC-100",
      "name": "Atlas Prime",
      "component": "joint encoder module",
      "category": "sensors",
      "status": "active",
      "version": "v4.2"
    },
    {
      "id": "WRN-00013",
      "model": "WC-500",
      "name": "Hercules Lifter",
      "component": "load cell array",
      "category": "sensors",
      "status": "active",
      "version": "v2.0"
    },
    {
      "id": "WRN-00016",
      "model": "WC-800",
      "name": "Phoenix Inspector",
      "component": "thermal imaging camera",
      "category": "sensors",
      "status": "active",
      "version": "v2.8"
    },
    {
      "id": "WRN-00018",
      "model": "WC-300",
      "name": "Nimbus Scout",
      "component": "ultrasonic sensor array",
      "category": "sensors",
      "status": "active",
      "version": "v1.6"
    },
    {
      "id": "WRN-00019",
      "model": "WC-400",
      "name": "Aegis Guardian",
      "component": "audio detection module",
      "category": "sensors",
      "status": "active",
      "version": "v2.2"
    }
  ]
}
```

#### Step 3: Get Specific Robot Details

**Tool:** `warn_get_robot`

**Parameters:**
```json
{
  "schematic_id": "WRN-00001"
}
```

**Expected Output:**
```json
{
  "id": "WRN-00001",
  "model": "WC-100",
  "name": "Atlas Prime",
  "component": "force feedback sensor array",
  "version": "v3.4",
  "category": "sensors",
  "status": "active",
  "summary": "High-precision force sensing system for WC-100 manipulation tasks. Enables delicate object handling with 0.1N resolution.",
  "url": "https://schematics.warnerco.io/wc-100/force_feedback_sensor_v3_4.pdf",
  "tags": ["manipulation", "precision", "feedback"],
  "specifications": {
    "resolution": "0.1N",
    "range": "0-500N",
    "response_time": "2ms"
  },
  "last_verified": "2025-01-15"
}
```

#### Step 4: Semantic Search

**Tool:** `warn_semantic_search`

**Parameters:**
```json
{
  "query": "force sensors for precision manipulation",
  "top_k": 3
}
```

**Expected Output (with JSON backend):**
```json
{
  "query": "force sensors for precision manipulation",
  "intent": "search",
  "results": [
    {
      "id": "WRN-00001",
      "model": "WC-100",
      "name": "Atlas Prime",
      "component": "force feedback sensor array",
      "score": 0.85,
      "summary": "High-precision force sensing system for WC-100 manipulation tasks. Enables delicate object handling with 0.1N resolution."
    },
    {
      "id": "WRN-00005",
      "model": "WC-100",
      "name": "Atlas Prime",
      "component": "precision gripper assembly",
      "score": 0.72,
      "summary": "Adaptive gripper system for WC-100 precision handling. Features variable force control and tactile feedback for delicate operations."
    },
    {
      "id": "WRN-00012",
      "model": "WC-100",
      "name": "Atlas Prime",
      "component": "joint encoder module",
      "score": 0.65,
      "summary": "High-resolution position sensing for WC-100 articulated arms. Provides absolute position feedback for precise motion control."
    }
  ],
  "total": 3,
  "reasoning": "Searched for schematics matching: force sensors for precision manipulation",
  "query_time_ms": 12
}
```

#### Step 5: Memory Stats

**Tool:** `warn_memory_stats`

**Parameters:** (none)

**Expected Output:**
```json
{
  "backend": "json",
  "total_schematics": 25,
  "indexed_count": 0,
  "chunk_count": 0,
  "categories": {
    "sensors": 8,
    "thermal": 1,
    "power": 1,
    "manipulation": 1,
    "actuators": 1,
    "control": 2,
    "communication": 1,
    "safety": 2,
    "tooling": 2,
    "environmental": 1,
    "structural": 2,
    "mechanical": 3
  },
  "status_counts": {
    "active": 23,
    "deprecated": 1,
    "draft": 1
  },
  "last_update": null
}
```

---

## D. Testing in VS Code / GitHub Copilot

### 1. Configure MCP in VS Code

Create or edit `.vscode/mcp.json` in your workspace:

```json
{
  "mcpServers": {
    "warnerco": {
      "command": "uv",
      "args": ["run", "warnerco-mcp"],
      "cwd": "${workspaceFolder}/src/warnerco/backend"
    }
  }
}
```

### 2. Restart VS Code / Reload Window

Press `Ctrl+Shift+P` and run "Developer: Reload Window"

### 3. Open GitHub Copilot Chat

Press `Ctrl+Shift+I` or click the Copilot icon in the sidebar

### Sample Prompts to Type in Copilot Chat

These prompts will trigger MCP tool calls:

#### Prompt 1: List Thermal Components

```
What robots have thermal management components?
```

**Expected Copilot Behavior:**
- Calls `warn_list_robots` with category filter or `warn_semantic_search`
- Returns information about:
  - WRN-00002 (Titan Handler - thermal management unit)
  - WRN-00016 (Phoenix Inspector - thermal imaging camera)

#### Prompt 2: Compare Two Schematics

```
Compare WRN-00003 and WRN-00007
```

**Expected Copilot Behavior:**
- Calls `warn_compare_schematics` with id1="WRN-00003" and id2="WRN-00007"
- Returns comparison showing:
  - WRN-00003: Nimbus Scout battery management system (power)
  - WRN-00007: Nimbus Scout LIDAR navigation module (sensors)
  - Similarity: Same robot model (WC-300), same robot name (Nimbus Scout)
  - Differences: Different categories (power vs sensors), different components

#### Prompt 3: Find Safety Systems

```
Find schematics related to safety systems
```

**Expected Copilot Behavior:**
- Calls `warn_semantic_search` with query about safety
- Returns:
  - WRN-00009: Aegis Guardian safety interlock system
  - WRN-00017: Titan Handler emergency stop module
  - WRN-00013: Hercules Lifter load cell array (safety-related)

#### Prompt 4: Specific Robot Lookup

```
Tell me about the Atlas Prime force feedback sensor
```

**Expected Copilot Behavior:**
- Calls `warn_get_robot` with "WRN-00001" or `warn_semantic_search`
- Returns full details including:
  - Resolution: 0.1N
  - Range: 0-500N
  - Response time: 2ms
  - Tags: manipulation, precision, feedback

#### Prompt 5: Category Statistics

```
How many sensor schematics do we have?
```

**Expected Copilot Behavior:**
- Calls `warn_memory_stats` or `warn_list_robots` with category="sensors"
- Returns: 8 sensor schematics

### Demo: Chroma Embeddings (Semantic Search)

To show Chroma working (if configured):

1. Set `MEMORY_BACKEND=chroma` in `.env`
2. Index the schematics:

```bash
cd src/warnerco/backend
uv run python -c "from app.adapters.chroma_store import ChromaMemoryStore; import asyncio; asyncio.run(ChromaMemoryStore().index_all())"
```

3. Restart the server
4. Try semantic search - it will now use vector embeddings:

```
Find components for harsh temperature environments
```

Expected: Better semantic matching - finds thermal sensors, cooling systems, and temperature-rated components even if they don't use exact keywords.

---

## E. Testing Scratchpad Memory

The scratchpad provides session-scoped working memory for observations and inferences.

### MCP Inspector Examples

#### Write an Observation

**Tool:** `warn_scratchpad_write`

**Parameters:**
```json
{
  "subject": "WRN-00001",
  "predicate": "observed",
  "object_": "thermal_calibration",
  "content": "Force sensor calibration drift detected at high temperatures above 60C. The 0.1N resolution degrades to approximately 0.3N when operating in warm environments. Recommend thermal compensation algorithm.",
  "minimize": true
}
```

**Expected Output:**
```json
{
  "success": true,
  "entry_id": "sp_abc123",
  "tokens_saved": 15,
  "original_tokens": 42,
  "minimized_tokens": 27,
  "message": "Entry stored successfully"
}
```

#### Read Scratchpad Entries

**Tool:** `warn_scratchpad_read`

**Parameters:**
```json
{
  "subject": "WRN-00001"
}
```

**Expected Output:**
```json
{
  "entries": [
    {
      "id": "sp_abc123",
      "subject": "WRN-00001",
      "predicate": "observed",
      "object": "thermal_calibration",
      "content": "Force sensor calibration drifts >60C: 0.1N->0.3N resolution. Needs thermal compensation.",
      "original_tokens": 42,
      "minimized_tokens": 27,
      "created_at": "2025-01-27T10:30:00Z",
      "expires_at": "2025-01-27T11:00:00Z"
    }
  ],
  "total": 1,
  "enriched_count": 0
}
```

#### Check Scratchpad Stats

**Tool:** `warn_scratchpad_stats`

**Parameters:** (none)

**Expected Output:**
```json
{
  "entry_count": 1,
  "total_original_tokens": 42,
  "total_minimized_tokens": 27,
  "tokens_saved": 15,
  "savings_percentage": 35.7,
  "token_budget": 2000,
  "token_budget_used": 27,
  "token_budget_remaining": 1973,
  "predicate_counts": {
    "observed": 1
  }
}
```

### VS Code / Copilot Prompts for Scratchpad

#### Store an Observation

```
I noticed the Atlas Prime force sensor has calibration issues at high temps. Remember that.
```

**Expected Copilot Behavior:**
- Calls `warn_scratchpad_write` with:
  - subject: "WRN-00001" (or "Atlas Prime")
  - predicate: "observed"
  - content: extracted observation

#### Recall an Observation

```
What did I observe about WRN-00001 earlier?
```

**Expected Copilot Behavior:**
- Calls `warn_scratchpad_read` with subject="WRN-00001"
- Returns the stored observation about calibration issues

#### Store an Inference

```
Based on the thermal issues, I think the Atlas Prime needs a cooling solution when used with the Titan Handler thermal unit. Note that.
```

**Expected Copilot Behavior:**
- Calls `warn_scratchpad_write` with predicate="inferred"

#### Check Memory Usage

```
How much scratchpad memory am I using?
```

**Expected Copilot Behavior:**
- Calls `warn_scratchpad_stats`
- Reports token budget usage

---

## F. Graph Memory Demo

The Knowledge Graph stores relationships between entities.

### Index the Graph First

```bash
cd src/warnerco/backend
uv run python scripts/index_graph.py
```

Expected output:
```
Indexing schematics to graph...
Added entity: WRN-00001
Added relationship: WRN-00001 -> has_status -> status:active
Added relationship: WRN-00001 -> has_category -> category:sensors
...
Graph indexing complete. Stats:
  Entities: 85
  Relationships: 175
```

### MCP Inspector Examples

#### Add a Relationship

**Tool:** `warn_add_relationship`

**Parameters:**
```json
{
  "subject": "WRN-00001",
  "predicate": "depends_on",
  "object": "WRN-00005"
}
```

**Expected Output:**
```json
{
  "success": true,
  "message": "Relationship added successfully",
  "relationship": {
    "subject": "WRN-00001",
    "predicate": "depends_on",
    "object": "WRN-00005"
  }
}
```

**Explanation:** This creates a dependency - the force feedback sensor array (WRN-00001) depends on the precision gripper assembly (WRN-00005).

#### Get Neighbors

**Tool:** `warn_graph_neighbors`

**Parameters:**
```json
{
  "entity_id": "WRN-00001",
  "direction": "both"
}
```

**Expected Output:**
```json
{
  "entity_id": "WRN-00001",
  "direction": "both",
  "neighbors": [
    "status:active",
    "category:sensors",
    "model:WC-100",
    "tag:manipulation",
    "tag:precision",
    "tag:feedback",
    "WRN-00005"
  ],
  "relationships": [
    {
      "direction": "outgoing",
      "predicate": "has_status",
      "target": "status:active"
    },
    {
      "direction": "outgoing",
      "predicate": "has_category",
      "target": "category:sensors"
    },
    {
      "direction": "outgoing",
      "predicate": "belongs_to_model",
      "target": "model:WC-100"
    },
    {
      "direction": "outgoing",
      "predicate": "has_tag",
      "target": "tag:manipulation"
    },
    {
      "direction": "outgoing",
      "predicate": "depends_on",
      "target": "WRN-00005"
    }
  ]
}
```

#### Find Path Between Entities

**Tool:** `warn_graph_path`

**Parameters:**
```json
{
  "source": "WRN-00006",
  "target": "category:actuators"
}
```

**Expected Output:**
```json
{
  "source": "WRN-00006",
  "target": "category:actuators",
  "path": ["WRN-00006", "category:actuators"],
  "path_length": 1
}
```

**Explanation:** WRN-00006 (Hercules Lifter hydraulic actuator system) is directly connected to the actuators category.

#### Graph Statistics

**Tool:** `warn_graph_stats`

**Parameters:** (none)

**Expected Output:**
```json
{
  "entity_count": 85,
  "relationship_count": 175,
  "entity_types": {
    "schematic": 25,
    "status": 3,
    "category": 13,
    "model": 9,
    "tag": 35
  },
  "predicate_counts": {
    "has_status": 25,
    "has_category": 25,
    "belongs_to_model": 25,
    "has_tag": 75,
    "depends_on": 25
  }
}
```

### VS Code / Copilot Prompts for Graph

```
What is WRN-00006 related to in the knowledge graph?
```

```
How is the force sensor connected to other components?
```

```
Create a dependency: WRN-00008 depends on WRN-00014
```

---

## G. Full RAG Pipeline Demo

This demonstrates the complete 7-node LangGraph pipeline:

```
parse_intent -> query_graph -> inject_scratchpad -> retrieve -> compress_context -> reason -> respond
```

### Setup for Full Demo

1. Ensure graph is indexed (run `scripts/index_graph.py`)
2. Add some scratchpad observations
3. Set `MEMORY_BACKEND=chroma` for best results

### Complex Query Example

**In Copilot Chat:**

```
I'm troubleshooting a problem with the Hercules Lifter. The hydraulic system seems to be overheating. What related schematics should I check, and what do we know about thermal issues?
```

**Expected Pipeline Execution:**

1. **parse_intent**: Detects DIAGNOSTIC intent (keywords: "troubleshooting", "problem", "overheating")

2. **query_graph**:
   - Extracts entity: "Hercules Lifter" -> WRN-00006, WRN-00013, WRN-00020
   - Extracts component: "hydraulic" -> component:hydraulic_system
   - Gets neighbors of WRN-00006 from graph

3. **inject_scratchpad**: Adds any session observations about thermal issues or hydraulic systems

4. **retrieve**: Semantic search for thermal management and hydraulic components

5. **compress_context**: Filters and ranks results by relevance

6. **reason**: Generates explanation of connections

7. **respond**: Final structured response

**Expected Results:**

The response should reference:
- WRN-00006: Hercules Lifter hydraulic actuator system (direct match)
- WRN-00002: Titan Handler thermal management unit (thermal solution)
- WRN-00013: Hercules Lifter load cell array (same robot)
- WRN-00020: Hercules Lifter structural frame assembly (same robot)
- Any scratchpad observations about thermal issues

### Another Complex Query

```
Compare the navigation capabilities of the Nimbus Scout and Mercury Courier. Which sensors do they use?
```

**Expected Results:**
- WRN-00007: Nimbus Scout LIDAR navigation module (200m range, 1.2M points/sec)
- WRN-00018: Nimbus Scout ultrasonic sensor array (0.02-4m range)
- WRN-00014: Mercury Courier navigation computer
- WRN-00008: Mercury Courier motor controller board

### Diagnostic Query with Graph Context

```
What depends on the precision gripper assembly?
```

**Expected Behavior:**
- Graph lookup for WRN-00005 incoming relationships
- Shows any schematics that have `depends_on` relationship to WRN-00005

---

## Quick Reference

### Robot Models

| Model | Name | Description |
|-------|------|-------------|
| WC-100 | Atlas Prime | Precision manipulation robot |
| WC-200 | Titan Handler | Heavy-duty industrial handler |
| WC-300 | Nimbus Scout | Mobile reconnaissance unit |
| WC-400 | Aegis Guardian | Security robot |
| WC-500 | Hercules Lifter | Heavy-lift industrial robot |
| WC-600 | Mercury Courier | Delivery robot |
| WC-700 | Vulcan Welder | Manufacturing/welding robot |
| WC-800 | Phoenix Inspector | Inspection robot |
| WC-900 | Orion Assembler | Assembly robot |

### All Schematic IDs

| ID | Model | Component | Category | Status |
|----|-------|-----------|----------|--------|
| WRN-00001 | WC-100 | force feedback sensor array | sensors | active |
| WRN-00002 | WC-200 | thermal management unit | thermal | active |
| WRN-00003 | WC-300 | battery management system | power | active |
| WRN-00004 | WC-400 | vision processing module | sensors | active |
| WRN-00005 | WC-100 | precision gripper assembly | manipulation | active |
| WRN-00006 | WC-500 | hydraulic actuator system | actuators | active |
| WRN-00007 | WC-300 | LIDAR navigation module | sensors | active |
| WRN-00008 | WC-600 | motor controller board | control | active |
| WRN-00009 | WC-400 | safety interlock system | safety | active |
| WRN-00010 | WC-200 | wireless communication module | communication | active |
| WRN-00011 | WC-700 | arc welding head assembly | tooling | active |
| WRN-00012 | WC-100 | joint encoder module | sensors | active |
| WRN-00013 | WC-500 | load cell array | sensors | active |
| WRN-00014 | WC-600 | navigation computer | control | active |
| WRN-00015 | WC-700 | fume extraction system | environmental | active |
| WRN-00016 | WC-800 | thermal imaging camera | sensors | active |
| WRN-00017 | WC-200 | emergency stop module | safety | active |
| WRN-00018 | WC-300 | ultrasonic sensor array | sensors | active |
| WRN-00019 | WC-400 | audio detection module | sensors | active |
| WRN-00020 | WC-500 | structural frame assembly | structural | active |
| WRN-00021 | WC-100 | cable management system | structural | **deprecated** |
| WRN-00022 | WC-600 | cargo bay mechanism | mechanical | active |
| WRN-00023 | WC-700 | wire feed mechanism | mechanical | active |
| WRN-00024 | WC-800 | articulated inspection arm | mechanical | active |
| WRN-00025 | WC-900 | precision screw driver unit | tooling | **draft** |

### Categories

| Category | Count | Example Components |
|----------|-------|-------------------|
| sensors | 8 | Force sensors, LIDAR, cameras, encoders |
| safety | 2 | Safety interlock, emergency stop |
| control | 2 | Motor controller, navigation computer |
| power | 1 | Battery management |
| thermal | 1 | Thermal management |
| manipulation | 1 | Precision gripper |
| actuators | 1 | Hydraulic actuators |
| communication | 1 | Wireless module |
| tooling | 2 | Welding head, screwdriver |
| environmental | 1 | Fume extraction |
| structural | 2 | Frame assembly, cable management |
| mechanical | 3 | Cargo bay, wire feed, inspection arm |

### MCP Tools Reference

| Tool | Purpose | Key Parameters |
|------|---------|----------------|
| `warn_list_robots` | List schematics | category, model, status, limit |
| `warn_get_robot` | Get schematic details | schematic_id |
| `warn_semantic_search` | Natural language search | query, category, model, top_k |
| `warn_memory_stats` | Memory backend stats | (none) |
| `warn_compare_schematics` | Compare two schematics | id1, id2 |
| `warn_add_relationship` | Add graph edge | subject, predicate, object |
| `warn_graph_neighbors` | Get connected entities | entity_id, direction |
| `warn_graph_path` | Find shortest path | source, target |
| `warn_graph_stats` | Graph statistics | (none) |
| `warn_scratchpad_write` | Store observation | subject, predicate, object_, content |
| `warn_scratchpad_read` | Retrieve entries | subject, predicate, enrich |
| `warn_scratchpad_clear` | Clear entries | subject, older_than_minutes |
| `warn_scratchpad_stats` | Token usage stats | (none) |

### Valid Predicates

**Graph Predicates:**
- `depends_on` - Subject depends on object
- `contains` - Subject contains object
- `has_status` - Subject has status
- `manufactured_by` - Subject manufactured by object
- `compatible_with` - Subject compatible with object
- `related_to` - General relationship
- `has_category` - Subject belongs to category
- `belongs_to_model` - Subject belongs to model
- `has_tag` - Subject has tag

**Scratchpad Predicates:**
- `observed` - Direct observation
- `inferred` - Conclusion from observations
- `relevant_to` - Connection to entity
- `summarized_as` - Condensed representation
- `contradicts` - Conflicting information
- `supersedes` - Replaces prior info
- `depends_on` - Dependency

### Useful URLs

| URL | Description |
|-----|-------------|
| http://localhost:8000 | Main app (redirects to dashboard) |
| http://localhost:8000/dash/ | Dashboard |
| http://localhost:8000/dash/schematics/ | Browse schematics |
| http://localhost:8000/dash/memory/ | Memory stats |
| http://localhost:8000/dash/scratchpad/ | Scratchpad viewer |
| http://localhost:8000/docs | OpenAPI/Swagger UI |
| http://localhost:8000/mcp | MCP HTTP endpoint |
| http://localhost:5173 | MCP Inspector (when running) |

---

## Troubleshooting

### Server Won't Start

1. Check Python version: `python --version` (needs 3.11+)
2. Check dependencies: `uv sync`
3. Check port: Another process might be using 8000

### MCP Inspector Won't Connect

1. Make sure server is NOT running in HTTP mode when using Inspector
2. Inspector runs its own stdio connection to `warnerco-mcp`
3. Check: `npx @modelcontextprotocol/inspector --help`

### Semantic Search Returns Poor Results

1. Check memory backend: `MEMORY_BACKEND=chroma` for best results
2. Index schematics for Chroma: run the indexing command
3. JSON backend uses keyword matching only

### Graph Queries Return Empty

1. Run `scripts/index_graph.py` to populate the graph
2. Check if `data/graph.db` exists

### Scratchpad Entries Disappear

1. Entries expire after 30 minutes (configurable)
2. Session reset clears scratchpad
3. Check `warn_scratchpad_stats` for current state

---

**Document Last Updated:** January 2025

**For use with:** WARNERCO Robotics Schematica v1.0.0
