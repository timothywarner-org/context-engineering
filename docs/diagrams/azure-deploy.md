# WARNERCO Robotics Schematica - Azure Deployment

```mermaid
flowchart TB
    subgraph External["External Clients"]
        CD["Claude Desktop"]
        WEB["Web Browser"]
        MOBILE["Mobile Apps"]
    end

    subgraph Azure["Azure Cloud"]
        subgraph Networking["API Management"]
            APIM["Azure APIM<br/>━━━━━━━━━━<br/>Rate Limiting<br/>API Keys<br/>Routing"]
        end

        subgraph Compute["Container Apps Environment"]
            CA["Container App<br/>━━━━━━━━━━<br/>FastAPI + FastMCP<br/>LangGraph Flow<br/>uvicorn"]
        end

        subgraph Data["Data Services"]
            AIS["Azure AI Search<br/>━━━━━━━━━━<br/>Vector Index<br/>Semantic Ranking<br/>Hybrid Search"]
            COSMOS["Cosmos DB<br/>(optional)<br/>━━━━━━━━━━<br/>Schematic Storage<br/>Query Logs"]
        end

        subgraph AI["AI Services"]
            AOAI["Azure OpenAI<br/>━━━━━━━━━━<br/>gpt-4o-mini<br/>text-embedding-ada-002"]
        end

        subgraph Security["Security"]
            KV["Key Vault<br/>━━━━━━━━━━<br/>API Keys<br/>Connection Strings"]
            MI["Managed Identity<br/>━━━━━━━━━━<br/>Passwordless Auth"]
        end
    end

    CD -->|MCP over HTTP| APIM
    WEB -->|HTTPS| APIM
    MOBILE -->|HTTPS| APIM

    APIM -->|Route| CA

    CA -->|Semantic Search| AIS
    CA -->|Store/Query| COSMOS
    CA -->|Embeddings & Chat| AOAI

    CA -.->|Get Secrets| KV
    CA -.->|Authenticate| MI
    MI -.->|Access| KV
    MI -.->|Access| AIS
    MI -.->|Access| AOAI

    classDef externalNode fill:#4a90d9,stroke:#2e5984,color:#fff
    classDef networkNode fill:#f39c12,stroke:#d68910,color:#fff
    classDef computeNode fill:#50b890,stroke:#2e8b57,color:#fff
    classDef dataNode fill:#9b59b6,stroke:#6c3483,color:#fff
    classDef aiNode fill:#e74c3c,stroke:#c0392b,color:#fff
    classDef securityNode fill:#34495e,stroke:#2c3e50,color:#fff

    class CD,WEB,MOBILE externalNode
    class APIM networkNode
    class CA computeNode
    class AIS,COSMOS dataNode
    class AOAI aiNode
    class KV,MI securityNode
```

## Description

This diagram shows the Azure deployment architecture for WARNERCO Robotics Schematica:

- **External Clients**: Claude Desktop, web browsers, and mobile apps connect via HTTPS
- **API Management (APIM)**: Provides rate limiting, API key management, and routing
- **Container Apps**: Hosts the FastAPI + FastMCP application with LangGraph flow
- **Data Services**: Azure AI Search for vector/semantic search, optional Cosmos DB for storage
- **AI Services**: Azure OpenAI for embeddings (text-embedding-ada-002) and chat (gpt-4o-mini)
- **Security**: Key Vault for secrets, Managed Identity for passwordless authentication
