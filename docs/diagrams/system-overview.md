# WARNERCO Robotics Schematica - System Overview

```mermaid
%%{init: {'theme': 'base', 'themeVariables': { 'primaryColor': '#4a90d9', 'primaryTextColor': '#fff', 'primaryBorderColor': '#2e5984', 'lineColor': '#5a6c7d', 'secondaryColor': '#50b890', 'tertiaryColor': '#f5a623', 'fontFamily': 'Inter, system-ui, sans-serif'}}}%%
flowchart TB
    subgraph Clients["<b>CLIENT LAYER</b>"]
        direction LR
        CD["<b>Claude Desktop</b><br/>MCP stdio transport"]
        VSC["<b>VS Code</b><br/>GitHub Copilot MCP"]
        DASH["<b>Web Dashboards</b><br/>Astro SPA"]
        API["<b>REST Clients</b><br/>HTTP consumers"]
    end

    subgraph Server["<b>APPLICATION LAYER</b>"]
        subgraph FastAPI["<b>FastAPI Server</b> :8000"]
            direction LR
            ROUTES["/api/*<br/>REST endpoints"]
            MCP_EP["/mcp<br/>MCP HTTP"]
            STATIC["/dash/*<br/>Static files"]
        end
    end

    subgraph MCP["<b>MCP PRIMITIVES</b>"]
        subgraph Tools["<b>15 Tools</b>"]
            direction TB
            T_DATA["<b>Data Tools</b><br/>list_robots | get_robot<br/>semantic_search | memory_stats"]
            T_MOD["<b>Modification Tools</b><br/>index_schematic | compare_schematics"]
            T_CRUD["<b>CRUD Tools</b><br/>create | update | delete"]
            T_INT["<b>Interactive Tools</b><br/>guided_search | feedback_loop"]
            T_GRAPH["<b>Graph Tools</b><br/>add_relationship | graph_neighbors<br/>graph_path | graph_stats"]
        end

        subgraph Resources["<b>10 Resources</b>"]
            direction TB
            R_MEM["memory://<br/>overview | recent | architecture"]
            R_CAT["catalog://<br/>categories | models"]
            R_HELP["help://<br/>tools | resources | prompts"]
            R_META["schematic://{id} | mcp://capabilities"]
        end

        subgraph Prompts["<b>5 Prompts</b>"]
            direction TB
            P_ALL["diagnostic | comparison<br/>search_strategy | maintenance<br/>schematic_review"]
        end
    end

    subgraph Orchestration["<b>LANGGRAPH 7-NODE HYBRID RAG PIPELINE</b>"]
        direction LR
        LG1["parse<br/>intent"]
        LG2["query<br/>graph"]
        LG3["inject<br/>scratchpad"]
        LG4["retrieve<br/>vectors"]
        LG5["compress<br/>context"]
        LG6["reason<br/>LLM"]
        LG7["respond<br/>format"]
        LG1 --> LG2 --> LG3 --> LG4 --> LG5 --> LG6 --> LG7
    end

    subgraph Memory["<b>HYBRID MEMORY LAYER</b>"]
        direction LR
        subgraph VectorTier["<b>Vector Store</b>"]
            JSON[("<b>JSON</b><br/>Source of Truth")]
            CHROMA[("<b>ChromaDB</b><br/>Local Vectors")]
            AZURE[("<b>Azure Search</b><br/>Enterprise")]
            JSON -.-|"index"| CHROMA
            CHROMA -.-|"scale"| AZURE
        end
        subgraph GraphTier["<b>Graph Store</b>"]
            GRAPH[("<b>SQLite +<br/>NetworkX</b><br/>Knowledge Graph")]
        end
    end

    subgraph AI["<b>AI SERVICES</b>"]
        AOAI["<b>Azure OpenAI</b><br/>gpt-4o-mini | ada-002"]
    end

    %% Connections
    CD -->|stdio| MCP_EP
    VSC -->|stdio| MCP_EP
    DASH -->|HTTP| ROUTES
    API -->|HTTP| ROUTES

    ROUTES --> Tools
    MCP_EP --> Tools
    MCP_EP --> Resources
    MCP_EP --> Prompts
    STATIC -.-> DASH

    Tools --> Orchestration
    Orchestration --> Memory
    Orchestration -->|"reasoning"| AI
    Resources --> Memory

    %% Styling - High contrast colors
    classDef clientBox fill:#1e3a5f,stroke:#0d253f,color:#fff,stroke-width:2px
    classDef serverBox fill:#1a5f4a,stroke:#0d3d2e,color:#fff,stroke-width:2px
    classDef mcpBox fill:#5c3d6e,stroke:#3d2847,color:#fff,stroke-width:2px
    classDef orchBox fill:#8b4513,stroke:#5c2d0e,color:#fff,stroke-width:2px
    classDef memBox fill:#b8860b,stroke:#8b6508,color:#fff,stroke-width:2px
    classDef aiBox fill:#8b0000,stroke:#5c0000,color:#fff,stroke-width:2px

    classDef graphBox fill:#7c3aed,stroke:#5b21b6,color:#fff,stroke-width:2px

    class CD,VSC,DASH,API clientBox
    class ROUTES,MCP_EP,STATIC serverBox
    class T_DATA,T_MOD,T_CRUD,T_INT,T_GRAPH,R_MEM,R_CAT,R_HELP,R_META,P_ALL mcpBox
    class LG1,LG2,LG3,LG4,LG5,LG6,LG7 orchBox
    class JSON,CHROMA,AZURE memBox
    class GRAPH graphBox
    class AOAI aiBox
```

## Architecture Summary

### Client Layer
- **Claude Desktop**: Native MCP stdio transport for desktop AI assistant
- **VS Code**: GitHub Copilot with MCP extension support
- **Web Dashboards**: Astro-built SPA served from /dash/
- **REST Clients**: Direct HTTP API access for integrations

### Application Layer
- **FastAPI Server**: Unified server on port 8000
  - `/api/*` - REST endpoints for programmatic access
  - `/mcp` - MCP HTTP endpoint for remote clients
  - `/dash/*` - Static file serving for dashboards

### MCP Primitives (v2.0)

| Primitive | Count | Purpose |
|-----------|-------|---------|
| **Tools** | 15 | Executable actions (CRUD, search, interactive, graph) |
| **Resources** | 10 | Read-only data (memory, catalog, help, meta) |
| **Prompts** | 5 | Reusable templates (diagnostic, comparison, etc.) |

### LangGraph Hybrid RAG Pipeline

7-node flow: `parse_intent` -> `query_graph` -> `inject_scratchpad` -> `retrieve` -> `compress_context` -> `reason` -> `respond`

The `query_graph` node enriches retrieval context with relationship data from the knowledge graph. The `inject_scratchpad` node adds session-scoped working memory observations.

### Hybrid Memory Layer

**Vector Store** (similarity search):
1. **JSON**: Zero-config, keyword search (development)
2. **ChromaDB**: Local vectors, semantic search (staging)
3. **Azure AI Search**: Enterprise hybrid search (production)

**Graph Store** (relationship queries):
- **SQLite + NetworkX**: Knowledge graph for entity relationships, dependency tracking, and path finding

See [Graph Memory Architecture](./graph-memory-architecture.md) for details.
