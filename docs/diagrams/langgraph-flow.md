# WARNERCO Robotics Schematica - LangGraph RAG Flow

```mermaid
%%{init: {'theme': 'base', 'themeVariables': { 'primaryColor': '#2d5016', 'primaryTextColor': '#fff', 'primaryBorderColor': '#1a3009', 'lineColor': '#4a5568', 'fontFamily': 'JetBrains Mono, monospace'}}}%%
flowchart LR
    subgraph Input["<b>INPUT</b>"]
        direction TB
        Q["<b>query</b><br/>string"]
        F["<b>filters</b><br/>category, model"]
        K["<b>top_k</b><br/>int"]
    end

    subgraph Pipeline["<b>LANGGRAPH 5-NODE PIPELINE</b>"]
        direction LR

        N1["<b>1. PARSE INTENT</b><br/><br/>Classify query type<br/>Extract entities<br/>Set strategy"]

        N2["<b>2. RETRIEVE</b><br/><br/>Query memory backend<br/>Apply filters<br/>Score candidates"]

        N3["<b>3. COMPRESS</b><br/><br/>Extract key fields<br/>Minimize tokens<br/>Preserve context"]

        N4["<b>4. REASON</b><br/><br/>Call Azure OpenAI<br/>Generate insights<br/>Synthesize response"]

        N5["<b>5. RESPOND</b><br/><br/>Format output<br/>Add metadata<br/>Return result"]

        N1 ==> N2 ==> N3 ==> N4 ==> N5
    end

    subgraph Intents["<b>INTENT TYPES</b>"]
        direction TB
        I1["<b>LOOKUP</b><br/>Direct fetch by ID/name"]
        I2["<b>DIAGNOSTIC</b><br/>Troubleshooting queries"]
        I3["<b>ANALYTICS</b><br/>Stats and aggregations"]
        I4["<b>SEARCH</b><br/>Semantic matching"]
    end

    subgraph State["<b>GRAPH STATE</b>"]
        direction TB
        S["<b>TypedDict</b><br/><br/>query: str<br/>intent: QueryIntent<br/>filters: dict<br/>candidates: list<br/>compressed: str<br/>reasoning: str<br/>response: dict<br/>timings: dict"]
    end

    subgraph Output["<b>OUTPUT</b>"]
        R["<b>QueryResponse</b><br/><br/>success: bool<br/>intent: str<br/>results: list<br/>reasoning: str<br/>query_time_ms: int"]
    end

    %% Main flow
    Q --> N1
    F --> N1
    K --> N1
    N5 --> R

    %% Side connections
    N1 -.->|"classifies"| Intents
    Pipeline -.->|"tracks"| State

    %% Styling with high contrast
    classDef inputNode fill:#1e40af,stroke:#1e3a8a,color:#fff,stroke-width:2px
    classDef pipeNode fill:#166534,stroke:#14532d,color:#fff,stroke-width:3px
    classDef intentNode fill:#9a3412,stroke:#7c2d12,color:#fff,stroke-width:2px
    classDef stateNode fill:#6b21a8,stroke:#581c87,color:#fff,stroke-width:2px
    classDef outputNode fill:#be123c,stroke:#9f1239,color:#fff,stroke-width:2px

    class Q,F,K inputNode
    class N1,N2,N3,N4,N5 pipeNode
    class I1,I2,I3,I4 intentNode
    class S stateNode
    class R outputNode
```

## Pipeline Details

### Node 1: Parse Intent
Analyzes the incoming query to determine the best retrieval strategy.

| Intent | Description | Strategy |
|--------|-------------|----------|
| **LOOKUP** | Direct ID or name reference | Exact match, bypass semantic |
| **DIAGNOSTIC** | "Why is X failing?" | Include specs, prioritize recent |
| **ANALYTICS** | "How many sensors?" | Aggregate, count operations |
| **SEARCH** | General semantic query | Vector similarity, ranking |

### Node 2: Retrieve
Fetches candidates from the active memory backend.

```python
# Chroma (semantic)
results = collection.query(
    query_texts=[compressed_query],
    n_results=top_k,
    where=filters
)

# JSON (keyword fallback)
results = [s for s in schematics if matches_filters(s, filters)]
```

### Node 3: Compress Context
Reduces token usage while preserving essential information.

- Extracts: `id`, `name`, `summary`, `category`
- Omits: full specifications, URLs, verbose metadata
- Target: <2000 tokens for LLM context

### Node 4: Reason
Calls Azure OpenAI with compressed context.

```python
response = await client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Query: {query}\nContext: {compressed}"}
    ]
)
```

### Node 5: Respond
Formats the final response with metadata.

```python
return QueryResponse(
    success=True,
    intent=state["intent"],
    results=state["candidates"],
    reasoning=state["reasoning"],
    query_time_ms=elapsed
)
```

## State Management

The `GraphState` TypedDict maintains context across all nodes:

| Field | Type | Updated By |
|-------|------|------------|
| `query` | str | Input |
| `intent` | QueryIntent | Node 1 |
| `filters` | dict | Input |
| `candidates` | list[SearchResult] | Node 2 |
| `compressed_context` | str | Node 3 |
| `reasoning` | str | Node 4 |
| `response` | dict | Node 5 |
| `timings` | dict | All nodes |
