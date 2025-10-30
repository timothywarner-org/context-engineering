# CoreText MCP - Local Architecture

```mermaid
graph TB
    subgraph "Client Layer"
        CD[Claude Desktop]
        VSC[VS Code + Copilot]
        INSP[MCP Inspector]
    end

    subgraph "MCP Server - CoreText Local"
        STDIO[StdioServerTransport<br/>stdin/stdout]

        subgraph "Server Core"
            SRV[MCP Server<br/>@modelcontextprotocol/sdk]
            TOOLS[Tool Handlers<br/>8 Tools]
            RES[Resource Handlers<br/>3 Resources]
        end

        subgraph "Business Logic"
            MGR[MemoryManager<br/>CRUD Operations]
            ENTRY[MemoryEntry Class<br/>UUID, Metadata, Tags]
        end

        subgraph "AI Enrichment"
            DEEP[DeepSeekEnrichmentService]
            FALL[Fallback Enrichment<br/>Keyword + Sentiment]
        end

        subgraph "Storage Layer"
            JSON[(memory.json<br/>Local File Storage)]
        end
    end

    subgraph "External Services"
        DAPI[DeepSeek API<br/>api.deepseek.com]
    end

    subgraph "Tools Available"
        T1[memory_create]
        T2[memory_read]
        T3[memory_update]
        T4[memory_delete]
        T5[memory_search]
        T6[memory_list]
        T7[memory_stats]
        T8[memory_enrich]
    end

    subgraph "Resources Available"
        R1[memory://overview<br/>Markdown Dashboard]
        R2[memory://context-stream<br/>Time-windowed View]
        R3[memory://knowledge-graph<br/>Semantic Network]
    end

    CD -->|stdio protocol| STDIO
    VSC -->|stdio protocol| STDIO
    INSP -->|stdio protocol| STDIO

    STDIO <-->|JSON-RPC 2.0| SRV

    SRV --> TOOLS
    SRV --> RES

    TOOLS --> T1
    TOOLS --> T2
    TOOLS --> T3
    TOOLS --> T4
    TOOLS --> T5
    TOOLS --> T6
    TOOLS --> T7
    TOOLS --> T8

    RES --> R1
    RES --> R2
    RES --> R3

    T1 --> MGR
    T2 --> MGR
    T3 --> MGR
    T4 --> MGR
    T5 --> MGR
    T6 --> MGR
    T7 --> MGR
    T8 --> DEEP

    MGR --> ENTRY
    MGR <-->|Read/Write| JSON

    DEEP -->|API Key Present| DAPI
    DEEP -->|API Key Missing| FALL

    R1 --> MGR
    R2 --> MGR
    R3 --> MGR

    style CD fill:#e1f5ff
    style VSC fill:#e1f5ff
    style INSP fill:#e1f5ff
    style SRV fill:#fff4e6
    style MGR fill:#e8f5e9
    style DEEP fill:#f3e5f5
    style JSON fill:#fff9c4
    style DAPI fill:#ffe0b2

    classDef toolStyle fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    classDef resourceStyle fill:#f1f8e9,stroke:#558b2f,stroke-width:2px

    class T1,T2,T3,T4,T5,T6,T7,T8 toolStyle
    class R1,R2,R3 resourceStyle
```

## Architecture Overview

### Local Development Setup

**Communication**: stdio transport over stdin/stdout
**Storage**: JSON file at `data/memory.json`
**AI Enrichment**: DeepSeek API with fallback to local NLP
**Deployment**: Single Node.js process on developer machine

### Memory Types

1. **Episodic Memory**: Time-based events and conversations
2. **Semantic Memory**: Facts, knowledge, and concepts

### Key Features

- 8 CRUD tools for memory operations
- 3 resources for context visualization
- UUID-based memory identification
- Auto-creates 3 demo memories on first run
- Graceful API fallback when no key provided
- Access tracking and statistics

### Data Flow

1. Client sends tool/resource request via stdio
2. MCP Server receives JSON-RPC 2.0 message
3. Request routed to appropriate handler
4. MemoryManager performs CRUD operation
5. Optional DeepSeek enrichment
6. Data persisted to `memory.json`
7. Response returned via stdio

### Configuration

**Location**: `.env` file in project root

```bash
DEEPSEEK_API_KEY=sk-xxxxx  # Optional, falls back to local enrichment
```

**Claude Desktop Config**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "coretext": {
      "command": "node",
      "args": ["C:/path/to/coretext-mcp/src/index.js"],
      "env": {
        "DEEPSEEK_API_KEY": "sk-xxxxx"
      }
    }
  }
}
```

### Performance Characteristics

- Memory operations: <10ms (local JSON)
- Search latency: <50ms (linear scan)
- Enrichment: 500-2000ms (API dependent)
- Storage limit: 100MB (JSON file size)

### Development Workflow

```bash
npm install          # Install dependencies
npm run dev         # Start with auto-reload
npm run inspector   # Open MCP Inspector UI
npm test           # Run test suite (14 tests)
```
