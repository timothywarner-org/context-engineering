# Architecture Diagrams for Context Journal MCP

## Phase 1: Local Development Architecture

```mermaid
graph TB
    subgraph "Local Machine"
        CD[Claude Desktop App]
        MCP[Context Journal MCP Server<br/>Python FastMCP]
        JSON[(context_journal.json<br/>File Storage)]
    end
    
    CD -->|stdio/stdin| MCP
    MCP -->|File I/O| JSON
    
    style CD fill:#9b59b6,color:#fff
    style MCP fill:#3498db,color:#fff
    style JSON fill:#2ecc71,color:#fff
    
    classDef note fill:#ecf0f1,stroke:#95a5a6,color:#2c3e50
```

## Phase 2: Azure Production Architecture

```mermaid
graph TB
    subgraph "User Device"
        CD[Claude Desktop App]
    end
    
    subgraph "Azure Cloud"
        subgraph "Azure Container Apps"
            MCP[Context Journal MCP Server<br/>Python FastMCP<br/>Deployed Container]
        end
        
        subgraph "Azure Cosmos DB"
            DB[(Cosmos DB<br/>context_db<br/>Global Distribution)]
        end
        
        subgraph "Azure Key Vault"
            KV[Secrets<br/>Connection Strings<br/>API Keys]
        end
        
        subgraph "Azure Monitor"
            MON[Application Insights<br/>Logs & Metrics]
        end
    end
    
    CD -->|HTTP/SSE| MCP
    MCP -->|Azure SDK| DB
    MCP -.->|Fetch Secrets| KV
    MCP -.->|Send Telemetry| MON
    
    style CD fill:#9b59b6,color:#fff
    style MCP fill:#3498db,color:#fff
    style DB fill:#2ecc71,color:#fff
    style KV fill:#e74c3c,color:#fff
    style MON fill:#f39c12,color:#fff
```

## MCP Tool Architecture

```mermaid
graph LR
    subgraph "Claude Desktop"
        UI[User Interface]
        LLM[Claude LLM]
    end
    
    subgraph "MCP Server"
        T1[create_context_entry]
        T2[read_context_entry]
        T3[update_context_entry]
        T4[delete_context_entry]
        T5[list_context_entries]
        T6[search_context_entries]
        
        VAL[Pydantic Validation]
        LOGIC[Business Logic]
        STORE[Storage Layer]
    end
    
    UI --> LLM
    LLM -->|Tool Calls| T1
    LLM -->|Tool Calls| T2
    LLM -->|Tool Calls| T3
    LLM -->|Tool Calls| T4
    LLM -->|Tool Calls| T5
    LLM -->|Tool Calls| T6
    
    T1 --> VAL
    T2 --> VAL
    T3 --> VAL
    T4 --> VAL
    T5 --> VAL
    T6 --> VAL
    
    VAL --> LOGIC
    LOGIC --> STORE
    
    style UI fill:#9b59b6,color:#fff
    style LLM fill:#8e44ad,color:#fff
    style VAL fill:#e74c3c,color:#fff
    style LOGIC fill:#3498db,color:#fff
    style STORE fill:#2ecc71,color:#fff
```

## Data Flow: Create Context Entry

```mermaid
sequenceDiagram
    participant User
    participant Claude
    participant MCP Server
    participant Pydantic
    participant Storage
    
    User->>Claude: "Save this context about Azure deployment"
    Claude->>Claude: Analyze request
    Claude->>MCP Server: create_context_entry(title, context, tags)
    
    MCP Server->>Pydantic: Validate input
    
    alt Validation Success
        Pydantic->>MCP Server: ✓ Valid
        MCP Server->>Storage: Write entry
        Storage->>MCP Server: Success (entry_id)
        MCP Server->>Claude: JSON response {success: true, entry_id: "ctx_0001"}
        Claude->>User: "Context saved successfully as ctx_0001"
    else Validation Failure
        Pydantic->>MCP Server: ✗ Invalid (errors)
        MCP Server->>Claude: Error response {success: false, error: "..."}
        Claude->>User: "Error: [explanation and suggestion]"
    end
```

## Data Flow: Search and Retrieve

```mermaid
sequenceDiagram
    participant User
    participant Claude
    participant MCP Server
    participant Storage
    
    User->>Claude: "What did we decide about the API design?"
    Claude->>Claude: Determine need for context search
    Claude->>MCP Server: search_context_entries(query="API design")
    
    MCP Server->>Storage: Load all entries
    Storage->>MCP Server: Return entries array
    
    MCP Server->>MCP Server: Filter by query text<br/>Score relevance<br/>Sort by score
    
    MCP Server->>Claude: Markdown response with matches
    Claude->>User: "I found your API design decision: [context]"
```

## Migration Path: JSON to Cosmos DB

```mermaid
graph TD
    subgraph "Phase 1: Local JSON"
        J1[Load from file] --> J2[Parse JSON]
        J2 --> J3[Return data]
        
        J4[Modify data] --> J5[Serialize JSON]
        J5 --> J6[Write to file]
    end
    
    subgraph "Phase 2: Azure Cosmos DB"
        C1[Connect to Cosmos] --> C2[Query items]
        C2 --> C3[Return documents]
        
        C4[Modify data] --> C5[Serialize to dict]
        C5 --> C6[Upsert item]
    end
    
    J3 -.->|Same interface| C3
    J6 -.->|Same interface| C6
    
    style J1 fill:#95a5a6,color:#fff
    style J2 fill:#95a5a6,color:#fff
    style J3 fill:#95a5a6,color:#fff
    style J4 fill:#95a5a6,color:#fff
    style J5 fill:#95a5a6,color:#fff
    style J6 fill:#95a5a6,color:#fff
    
    style C1 fill:#3498db,color:#fff
    style C2 fill:#3498db,color:#fff
    style C3 fill:#3498db,color:#fff
    style C4 fill:#3498db,color:#fff
    style C5 fill:#3498db,color:#fff
    style C6 fill:#3498db,color:#fff
```

## Tool Annotation Effects

```mermaid
graph TD
    TOOL[MCP Tool Definition]
    
    TOOL --> RO[readOnlyHint: true]
    TOOL --> DEST[destructiveHint: false]
    TOOL --> IDEMP[idempotentHint: true]
    TOOL --> OPEN[openWorldHint: false]
    
    RO --> RO1[Claude knows:<br/>Safe to call anytime]
    DEST --> DEST1[Claude knows:<br/>Will delete/destroy data]
    IDEMP --> IDEMP1[Claude knows:<br/>Safe to retry]
    OPEN --> OPEN1[Claude knows:<br/>No external entities]
    
    style TOOL fill:#3498db,color:#fff
    style RO fill:#2ecc71,color:#fff
    style DEST fill:#e74c3c,color:#fff
    style IDEMP fill:#f39c12,color:#fff
    style OPEN fill:#9b59b6,color:#fff
```

## Error Handling Flow

```mermaid
graph TD
    START[Tool Called] --> VAL{Pydantic<br/>Validation}
    
    VAL -->|✓ Valid| EXEC[Execute Logic]
    VAL -->|✗ Invalid| ERR1[Return Validation Error]
    
    EXEC --> TRY{Try Block}
    
    TRY -->|Success| RESP[Format Response]
    TRY -->|Exception| ERR2[Catch Exception]
    
    ERR2 --> LOG[Log Error]
    LOG --> ERR3[Return Error Response]
    
    RESP --> RET[Return to Claude]
    ERR1 --> RET
    ERR3 --> RET
    
    RET --> CLAUDE[Claude Analyzes]
    CLAUDE --> USER[Presents to User]
    
    style START fill:#3498db,color:#fff
    style VAL fill:#f39c12,color:#fff
    style EXEC fill:#2ecc71,color:#fff
    style ERR1 fill:#e74c3c,color:#fff
    style ERR2 fill:#e74c3c,color:#fff
    style ERR3 fill:#e74c3c,color:#fff
    style RESP fill:#2ecc71,color:#fff
    style RET fill:#9b59b6,color:#fff
```

## Complete System Context

```mermaid
C4Context
    title System Context: Context Journal MCP

    Person(user, "Course Student", "Learning context engineering")
    
    System(claude, "Claude Desktop", "AI Assistant with MCP support")
    
    System_Boundary(mcp, "Context Journal System") {
        System(server, "MCP Server", "Manages context entries")
        SystemDb(storage, "Storage", "Persistent data")
    }
    
    System_Ext(azure, "Azure Services", "Cloud infrastructure")
    
    Rel(user, claude, "Interacts with", "Natural language")
    Rel(claude, server, "Calls tools via", "MCP Protocol")
    Rel(server, storage, "Reads/Writes", "JSON or Azure SDK")
    Rel(server, azure, "Deploys to", "Container Apps + Cosmos DB")
```

## Class Exercise: Add a Tool

```mermaid
graph LR
    START[Start] --> REQ[Define Requirements]
    REQ --> MODEL[Create Pydantic Model]
    MODEL --> TOOL[Write Tool Function]
    TOOL --> DOC[Add Docstring]
    DOC --> ANNO[Set Annotations]
    ANNO --> TEST[Test Locally]
    
    TEST --> WORKS{Works?}
    WORKS -->|Yes| DEMO[Demo to Class]
    WORKS -->|No| DEBUG[Debug Issues]
    DEBUG --> TEST
    
    DEMO --> DONE[Done!]
    
    style START fill:#2ecc71,color:#fff
    style REQ fill:#3498db,color:#fff
    style MODEL fill:#9b59b6,color:#fff
    style TOOL fill:#3498db,color:#fff
    style DOC fill:#f39c12,color:#fff
    style ANNO fill:#e67e22,color:#fff
    style TEST fill:#e74c3c,color:#fff
    style WORKS fill:#95a5a6,color:#fff
    style DEBUG fill:#e74c3c,color:#fff
    style DEMO fill:#2ecc71,color:#fff
    style DONE fill:#27ae60,color:#fff
```

---

## Using These Diagrams

### **In Presentations**
1. Copy the mermaid code block
2. Paste into any markdown renderer (GitHub, GitLab, VS Code with extensions)
3. Or use https://mermaid.live to generate PNG/SVG

### **In Claude**
- Claude can render mermaid diagrams directly
- Just paste the code blocks in conversation

### **In Documentation**
- GitHub and many platforms render mermaid automatically
- No need to generate static images

---

**All diagrams use consistent color scheme:**
- 🟣 Purple: User interfaces / Claude
- 🔵 Blue: MCP servers / Logic
- 🟢 Green: Storage / Success
- 🔴 Red: Errors / Destructive
- 🟠 Orange: Warnings / Monitoring
- ⚫ Gray: Deprecated / Old phase
