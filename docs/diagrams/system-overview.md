# WARNERCO Robotics Schematica - System Overview

```mermaid
flowchart TB
    subgraph Clients["Client Layer"]
        CD["Claude Desktop<br/>(MCP stdio)"]
        DASH["Web Dashboards<br/>(SPA)"]
        API["REST API<br/>Consumers"]
    end

    subgraph App["Application Layer"]
        subgraph FastAPI["FastAPI Server"]
            ROUTES["/api Routes"]
            MCP_MOUNT["/mcp Endpoint"]
            STATIC["/dash Static"]
        end

        subgraph FastMCP["FastMCP Tools"]
            T1["warn_list_robots"]
            T2["warn_get_robot"]
            T3["warn_semantic_search"]
            T4["warn_memory_stats"]
        end

        subgraph LangGraph["LangGraph Orchestration"]
            LG["5-Node RAG Flow<br/>(parse → retrieve → compress → reason → respond)"]
        end
    end

    subgraph Memory["3-Tier Memory Layer"]
        direction LR
        JSON["JSON Store<br/>(Source of Truth)"]
        CHROMA["Chroma DB<br/>(Vector Embeddings)"]
        AZURE_SEARCH["Azure AI Search<br/>(Enterprise Scale)"]
    end

    subgraph LLM["LLM Layer"]
        OPENAI["Azure OpenAI<br/>gpt-4o-mini"]
    end

    CD -->|stdio| MCP_MOUNT
    DASH -->|HTTP| ROUTES
    API -->|HTTP| ROUTES

    ROUTES --> FastMCP
    MCP_MOUNT --> FastMCP
    STATIC --> DASH

    FastMCP --> LangGraph
    LangGraph --> Memory
    LangGraph -->|reasoning| LLM

    JSON -.->|migrate| CHROMA
    CHROMA -.->|scale| AZURE_SEARCH

    classDef clientNode fill:#4a90d9,stroke:#2e5984,color:#fff
    classDef appNode fill:#50b890,stroke:#2e8b57,color:#fff
    classDef memoryNode fill:#f5a623,stroke:#d4880f,color:#fff
    classDef llmNode fill:#9b59b6,stroke:#6c3483,color:#fff

    class CD,DASH,API clientNode
    class ROUTES,MCP_MOUNT,STATIC,T1,T2,T3,T4,LG appNode
    class JSON,CHROMA,AZURE_SEARCH memoryNode
    class OPENAI llmNode
```

## Description

This diagram shows the layered architecture of WARNERCO Robotics Schematica:

- **Client Layer**: Multiple access points including Claude Desktop (MCP stdio), web dashboards, and REST API consumers
- **Application Layer**: FastAPI server with mounted FastMCP tools and LangGraph orchestration
- **3-Tier Memory Layer**: Progressive memory backends from JSON (source of truth) to Chroma (vectors) to Azure AI Search (enterprise)
- **LLM Layer**: Azure OpenAI for reasoning capabilities
