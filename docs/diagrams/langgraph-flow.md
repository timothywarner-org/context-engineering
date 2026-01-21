# WARNERCO Robotics Schematica - LangGraph RAG Flow

```mermaid
flowchart LR
    subgraph Input["Query Input"]
        Q["Natural Language<br/>Query"]
        F["Filters<br/>(category, model)"]
        K["top_k<br/>parameter"]
    end

    subgraph Flow["LangGraph RAG Flow"]
        direction LR

        N1["1. parse_intent<br/>━━━━━━━━━━<br/>Classify query type"]
        N2["2. retrieve<br/>━━━━━━━━━━<br/>Fetch from memory"]
        N3["3. compress_context<br/>━━━━━━━━━━<br/>Minimize tokens"]
        N4["4. reason<br/>━━━━━━━━━━<br/>LLM generation"]
        N5["5. respond<br/>━━━━━━━━━━<br/>Format output"]
    end

    subgraph Intents["Intent Classification"]
        direction TB
        I1["LOOKUP<br/>Direct ID/name fetch"]
        I2["DIAGNOSTIC<br/>Troubleshooting queries"]
        I3["ANALYTICS<br/>Stats & aggregations"]
        I4["SEARCH<br/>Semantic matching"]
    end

    subgraph State["GraphState"]
        direction TB
        S1["query: string"]
        S2["intent: QueryIntent"]
        S3["candidates: SearchResult[]"]
        S4["compressed_context: string"]
        S5["response: dict"]
        S6["timings: dict"]
    end

    subgraph Output["Response"]
        R["QueryResponse<br/>━━━━━━━━━━<br/>success<br/>intent<br/>results<br/>reasoning<br/>query_time_ms"]
    end

    Q --> N1
    F --> N1
    K --> N1

    N1 --> N2
    N2 --> N3
    N3 --> N4
    N4 --> N5
    N5 --> R

    N1 -.->|classifies| Intents
    N1 -.->|updates| S2
    N2 -.->|updates| S3
    N3 -.->|updates| S4
    N4 -.->|calls LLM| S5
    N5 -.->|formats| S5

    classDef inputNode fill:#4a90d9,stroke:#2e5984,color:#fff
    classDef flowNode fill:#50b890,stroke:#2e8b57,color:#fff
    classDef intentNode fill:#f39c12,stroke:#d68910,color:#fff
    classDef stateNode fill:#9b59b6,stroke:#6c3483,color:#fff
    classDef outputNode fill:#e74c3c,stroke:#c0392b,color:#fff

    class Q,F,K inputNode
    class N1,N2,N3,N4,N5 flowNode
    class I1,I2,I3,I4 intentNode
    class S1,S2,S3,S4,S5,S6 stateNode
    class R outputNode
```

## Description

This diagram illustrates the 5-node LangGraph RAG (Retrieval-Augmented Generation) flow:

1. **parse_intent**: Classifies the query into one of four intent types (LOOKUP, DIAGNOSTIC, ANALYTICS, SEARCH)
2. **retrieve**: Fetches candidate schematics from the memory backend based on intent
3. **compress_context**: Minimizes token usage by extracting only relevant fields
4. **reason**: Calls Azure OpenAI (gpt-4o-mini) for intelligent response generation
5. **respond**: Formats the final output for dashboards and MCP consumers

The GraphState TypedDict tracks query, intent, candidates, compressed context, response, and timing telemetry throughout the flow.
