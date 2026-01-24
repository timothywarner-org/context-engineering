# WARNERCO Robotics Schematica - Complete Architecture

## System Overview

```mermaid
%%{init: {'theme': 'base', 'themeVariables': { 'primaryColor': '#4a90d9', 'primaryTextColor': '#fff', 'primaryBorderColor': '#2e5984', 'lineColor': '#5a6c7d', 'secondaryColor': '#50b890', 'tertiaryColor': '#f5a623', 'fontFamily': 'Inter, system-ui, sans-serif'}}}%%
flowchart TB
    subgraph Clients["CLIENT LAYER"]
        direction LR
        CD["Claude Desktop<br/><i>MCP stdio transport</i>"]
        VSC["VS Code<br/><i>GitHub Copilot MCP</i>"]
        DASH["Web Dashboards<br/><i>Astro SPA</i>"]
        API["REST Clients<br/><i>HTTP consumers</i>"]
    end

    subgraph Server["APPLICATION LAYER - FastAPI :8000"]
        direction LR
        ROUTES["/api/*<br/>REST endpoints"]
        MCP_EP["/mcp<br/>FastMCP HTTP"]
        STATIC["/dash/*<br/>Static files"]
        DOCS["/docs<br/>OpenAPI"]
    end

    subgraph MCPPrimitives["MCP PRIMITIVES"]
        subgraph Tools["15 TOOLS"]
            direction TB
            T_DATA["Data Tools<br/>warn_list_robots<br/>warn_get_robot<br/>warn_semantic_search<br/>warn_memory_stats"]
            T_MOD["Modification Tools<br/>warn_index_schematic<br/>warn_compare_schematics<br/>warn_create_schematic<br/>warn_update_schematic<br/>warn_delete_schematic"]
            T_INT["Interactive Tools<br/>warn_guided_search<br/>warn_feedback_loop"]
            T_GRAPH["Graph Tools<br/>warn_add_relationship<br/>warn_graph_neighbors<br/>warn_graph_path<br/>warn_graph_stats"]
        end

        subgraph Resources["10 RESOURCES"]
            direction TB
            R_MEM["memory://overview<br/>memory://recent<br/>memory://architecture"]
            R_CAT["catalog://categories<br/>catalog://models"]
            R_HELP["help://tools<br/>help://resources<br/>help://prompts"]
            R_META["schematic://{id}<br/>mcp://capabilities"]
        end

        subgraph Prompts["5 PROMPTS"]
            P_ALL["diagnostic<br/>comparison<br/>search_strategy<br/>maintenance<br/>schematic_review"]
        end
    end

    subgraph RAG["LANGGRAPH 6-NODE HYBRID RAG PIPELINE"]
        direction LR
        LG1["1. PARSE<br/>INTENT"]
        LG2["2. QUERY<br/>GRAPH"]
        LG3["3. RETRIEVE<br/>VECTORS"]
        LG4["4. COMPRESS<br/>CONTEXT"]
        LG5["5. REASON<br/>LLM"]
        LG6["6. RESPOND<br/>FORMAT"]
        LG1 --> LG2 --> LG3 --> LG4 --> LG5 --> LG6
    end

    subgraph Memory["HYBRID MEMORY LAYER"]
        direction TB
        subgraph VectorTier["VECTOR STORE (3-TIER)"]
            direction LR
            JSON[("JSON<br/><i>Development</i><br/>Keyword Search")]
            CHROMA[("ChromaDB<br/><i>Staging</i><br/>Semantic Search")]
            AZURE_SEARCH[("Azure AI Search<br/><i>Production</i><br/>Hybrid Search")]
            JSON -.->|"upgrade"| CHROMA
            CHROMA -.->|"scale"| AZURE_SEARCH
        end
        subgraph GraphTier["GRAPH STORE"]
            GRAPH[("SQLite +<br/>NetworkX<br/><i>Knowledge Graph</i>")]
        end
    end

    subgraph AI["AI SERVICES"]
        AOAI["Azure OpenAI<br/>gpt-4o-mini<br/>text-embedding-ada-002"]
    end

    subgraph Data["DATA SOURCES"]
        SCHEMATICS[("schematics.json<br/>25 robot schematics")]
        GRAPHDB[("graph.db<br/>Entity relationships")]
    end

    %% Client connections
    CD -->|"stdio"| MCP_EP
    VSC -->|"stdio"| MCP_EP
    DASH -->|"HTTP"| ROUTES
    API -->|"HTTP"| ROUTES

    %% Server routing
    ROUTES --> Tools
    MCP_EP --> Tools
    MCP_EP --> Resources
    MCP_EP --> Prompts
    STATIC -.-> DASH

    %% Tool to RAG
    Tools --> RAG

    %% RAG to Memory
    LG2 --> GraphTier
    LG3 --> VectorTier
    LG5 -->|"reasoning"| AI

    %% Resources to Memory
    Resources --> Memory

    %% Data sources
    SCHEMATICS --> VectorTier
    SCHEMATICS --> GRAPHDB
    GRAPHDB --> GraphTier

    %% Styling
    classDef clientBox fill:#1e3a5f,stroke:#0d253f,color:#fff,stroke-width:2px
    classDef serverBox fill:#1a5f4a,stroke:#0d3d2e,color:#fff,stroke-width:2px
    classDef toolBox fill:#5c3d6e,stroke:#3d2847,color:#fff,stroke-width:2px
    classDef ragBox fill:#8b4513,stroke:#5c2d0e,color:#fff,stroke-width:2px
    classDef memBox fill:#b8860b,stroke:#8b6508,color:#fff,stroke-width:2px
    classDef graphBox fill:#7c3aed,stroke:#5b21b6,color:#fff,stroke-width:2px
    classDef aiBox fill:#8b0000,stroke:#5c0000,color:#fff,stroke-width:2px
    classDef dataBox fill:#2f4f4f,stroke:#1a3030,color:#fff,stroke-width:2px

    class CD,VSC,DASH,API clientBox
    class ROUTES,MCP_EP,STATIC,DOCS serverBox
    class T_DATA,T_MOD,T_INT,T_GRAPH,R_MEM,R_CAT,R_HELP,R_META,P_ALL toolBox
    class LG1,LG2,LG3,LG4,LG5,LG6 ragBox
    class JSON,CHROMA,AZURE_SEARCH memBox
    class GRAPH graphBox
    class AOAI aiBox
    class SCHEMATICS,GRAPHDB dataBox
```

## Architecture Summary

### Client Layer
- **Claude Desktop**: Native MCP stdio transport for desktop AI assistant
- **VS Code**: GitHub Copilot with MCP extension support
- **Web Dashboards**: Astro-built SPA served from /dash/
- **REST Clients**: Direct HTTP API access for integrations

### Application Layer (FastAPI :8000)
- **/api/*** - REST endpoints for programmatic access
- **/mcp** - FastMCP HTTP endpoint for remote MCP clients
- **/dash/*** - Static file serving for Astro dashboards
- **/docs** - OpenAPI documentation

### MCP Primitives

#### 15 Tools

| Category | Tools | Purpose |
|----------|-------|---------|
| **Data** | `warn_list_robots`, `warn_get_robot`, `warn_semantic_search`, `warn_memory_stats` | Read operations |
| **Modification** | `warn_index_schematic`, `warn_compare_schematics`, `warn_create_schematic`, `warn_update_schematic`, `warn_delete_schematic` | Write operations |
| **Interactive** | `warn_guided_search`, `warn_feedback_loop` | Multi-turn with elicitations |
| **Graph** | `warn_add_relationship`, `warn_graph_neighbors`, `warn_graph_path`, `warn_graph_stats` | Knowledge graph operations |

#### 10 Resources

| URI Pattern | Description |
|-------------|-------------|
| `memory://overview` | Memory system status |
| `memory://recent` | Recently accessed schematics |
| `memory://architecture` | System architecture info |
| `catalog://categories` | List of schematic categories |
| `catalog://models` | List of robot models |
| `help://tools` | Tool documentation |
| `help://resources` | Resource documentation |
| `help://prompts` | Prompt documentation |
| `schematic://{id}` | Individual schematic data |
| `mcp://capabilities` | Server capabilities |

#### 5 Prompts

| Prompt | Purpose |
|--------|---------|
| `diagnostic` | Troubleshooting guidance |
| `comparison` | Schematic comparison |
| `search_strategy` | Search optimization |
| `maintenance` | Maintenance procedures |
| `schematic_review` | Technical review |

### LangGraph 6-Node Pipeline

```
parse_intent --> query_graph --> retrieve --> compress_context --> reason --> respond
```

| Node | Function | Input | Output |
|------|----------|-------|--------|
| 1. `parse_intent` | Classify query type | Raw query | Intent (lookup/diagnostic/analytics/search) |
| 2. `query_graph` | Knowledge graph enrichment | Intent + query | Graph context (related entities) |
| 3. `retrieve` | Vector similarity search | Graph context + query | Candidate schematics |
| 4. `compress_context` | Token optimization | Candidates + graph context | Compressed context string |
| 5. `reason` | LLM synthesis | Compressed context | Reasoning explanation |
| 6. `respond` | Format output | All state | JSON response |

### Hybrid Memory Layer

#### Vector Store (3-Tier)

| Tier | Backend | Use Case | Features |
|------|---------|----------|----------|
| **Development** | JSON | Local dev | Keyword search, zero config |
| **Staging** | ChromaDB | Testing | Semantic search, local vectors |
| **Production** | Azure AI Search | Enterprise | Hybrid search, scale, SLA |

Set via `MEMORY_BACKEND` environment variable.

#### Graph Store

- **SQLite**: Persistent storage for entity relationships
- **NetworkX**: In-memory graph for fast traversal algorithms
- **Predicates**: `depends_on`, `contains`, `has_status`, `manufactured_by`, `compatible_with`, `related_to`

### AI Services

- **Azure OpenAI gpt-4o-mini**: Reasoning and synthesis
- **Azure OpenAI text-embedding-ada-002**: Vector embeddings

## Data Flow

### Query Flow

```
1. Client sends query via MCP or REST
2. parse_intent classifies query type
3. query_graph enriches with knowledge graph relationships
4. retrieve performs vector search
5. compress_context minimizes token usage
6. reason synthesizes response (LLM or stub)
7. respond formats for client consumption
```

### Indexing Flow

```
1. schematics.json contains 25 robot schematics
2. Vector indexing: JSON -> ChromaDB -> Azure AI Search
3. Graph indexing: scripts/index_graph.py -> graph.db -> NetworkX
```

## Quick Start

```bash
# Navigate to WARNERCO backend
cd src/warnerco/backend

# Install dependencies
uv sync

# Start server (development)
uv run uvicorn app.main:app --reload

# Access points:
# - Dashboard: http://localhost:8000/dash/
# - API docs:  http://localhost:8000/docs
# - MCP:       http://localhost:8000/mcp
```

## Configuration

### Environment Variables

```bash
# Memory backend selection
MEMORY_BACKEND=json|chroma|azure_search

# Azure AI Search (production)
AZURE_SEARCH_ENDPOINT=https://your-search.search.windows.net
AZURE_SEARCH_KEY=your-key
AZURE_SEARCH_INDEX=warnerco-schematics

# Azure OpenAI (reasoning)
AZURE_OPENAI_ENDPOINT=https://your-openai.openai.azure.com/
AZURE_OPENAI_API_KEY=your-key
AZURE_OPENAI_DEPLOYMENT=gpt-4o-mini
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-ada-002
```

## File Structure

```
src/warnerco/backend/
├── app/
│   ├── main.py              # FastAPI application
│   ├── mcp_tools.py         # 15 MCP tools + 10 resources + 5 prompts
│   ├── config.py            # Settings management
│   ├── api/                 # REST API routes
│   │   └── routes.py
│   ├── langgraph/
│   │   └── flow.py          # 6-node RAG pipeline
│   ├── adapters/
│   │   ├── __init__.py      # Factory functions
│   │   ├── base.py          # Abstract base class
│   │   ├── json_store.py    # JSON backend
│   │   ├── chroma_store.py  # ChromaDB backend
│   │   ├── azure_search_store.py  # Azure backend
│   │   └── graph_store.py   # SQLite + NetworkX
│   └── models/
│       ├── __init__.py
│       ├── schematic.py     # Schematic model
│       └── graph.py         # Entity/Relationship models
├── data/
│   ├── schematics/
│   │   └── schematics.json  # 25 robot schematics
│   ├── chroma/              # ChromaDB persistence
│   └── graph.db             # Knowledge graph
├── static/
│   └── dash/                # Astro SPA
└── scripts/
    ├── index_azure_search.py
    └── index_graph.py
```

---

**Course**: O'Reilly Live Training - Context Engineering with MCP
**Last Updated**: January 2026
