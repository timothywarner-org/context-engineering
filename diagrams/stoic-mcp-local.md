# Stoic MCP - Local Architecture

```mermaid
graph TB
    subgraph "Client Layer"
        CD[Claude Desktop]
        VSC[VS Code + Copilot]
        INSP[MCP Inspector]
    end

    subgraph "MCP Server - Stoic Local"
        STDIO[StdioServerTransport<br/>stdin/stdout]

        subgraph "Server Core - TypeScript"
            SRV[MCP Server<br/>@modelcontextprotocol/sdk]
            BUILD[TypeScript Compilation<br/>src/ → dist/]
            TOOLS[Tool Handlers<br/>9 Tools]
        end

        subgraph "Business Logic"
            STORAGE[QuoteStorage Class<br/>CRUD Operations]
            QUOTE[Quote Interface<br/>id, text, author, source]
            META[Metadata Management<br/>lastId, version, lastModified]
        end

        subgraph "AI Integration"
            DEEP[DeepSeekService Class]
            EXPLAIN[explainQuote()<br/>Developer Context]
            GEN[generateQuote()<br/>Theme-based]
        end

        subgraph "Storage Layer"
            JSON[(quotes.json<br/>Local File Storage)]
            STRUCT[JSON Structure<br/>metadata + quotes array]
        end

        subgraph "Import Utility"
            IMP[import-quotes.ts<br/>Bulk Import Tool]
            SRC[quotes-source/<br/>Import Files]
            THEME[Auto Theme Detection<br/>18 Categories]
        end
    end

    subgraph "External Services"
        DAPI[DeepSeek API<br/>api.deepseek.com]
    end

    subgraph "Tools Available"
        T1[get_random_quote<br/>Random Inspiration]
        T2[search_quotes<br/>Author/Theme/Keyword]
        T3[add_quote<br/>Manual Entry]
        T4[get_quote_explanation<br/>AI Analysis]
        T5[toggle_favorite<br/>Mark/Unmark]
        T6[get_favorites<br/>List All Favorites]
        T7[update_quote_notes<br/>Personal Reflections]
        T8[delete_quote<br/>Remove Quote]
        T9[generate_quote<br/>AI Generation]
    end

    CD -->|stdio protocol| STDIO
    VSC -->|stdio protocol| STDIO
    INSP -->|stdio protocol| STDIO

    STDIO <-->|JSON-RPC 2.0| SRV

    SRV --> TOOLS
    BUILD -.->|Compiles to| SRV

    TOOLS --> T1
    TOOLS --> T2
    TOOLS --> T3
    TOOLS --> T4
    TOOLS --> T5
    TOOLS --> T6
    TOOLS --> T7
    TOOLS --> T8
    TOOLS --> T9

    T1 --> STORAGE
    T2 --> STORAGE
    T3 --> STORAGE
    T5 --> STORAGE
    T6 --> STORAGE
    T7 --> STORAGE
    T8 --> STORAGE

    T4 --> DEEP
    T9 --> DEEP

    STORAGE --> QUOTE
    STORAGE --> META
    STORAGE <-->|Read/Write| JSON
    JSON --> STRUCT

    DEEP --> EXPLAIN
    DEEP --> GEN
    DEEP -->|DEEPSEEK_API_KEY| DAPI

    IMP --> SRC
    IMP --> THEME
    IMP -->|Append| JSON

    style CD fill:#e1f5ff
    style VSC fill:#e1f5ff
    style INSP fill:#e1f5ff
    style SRV fill:#fff4e6
    style STORAGE fill:#e8f5e9
    style DEEP fill:#f3e5f5
    style JSON fill:#fff9c4
    style DAPI fill:#ffe0b2
    style BUILD fill:#e0f2f1
    style IMP fill:#fce4ec

    classDef toolStyle fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    classDef aiStyle fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px

    class T1,T2,T3,T5,T6,T7,T8 toolStyle
    class T4,T9 aiStyle
```

## Architecture Overview

### Local Development Setup

**Language**: TypeScript (compiled to JavaScript)
**Communication**: stdio transport over stdin/stdout
**Storage**: JSON file at `local/quotes.json`
**AI Integration**: DeepSeek API for explanations and generation
**Build System**: TypeScript compiler (tsc)

### Quote Structure

```typescript
interface Quote {
  id: number;              // Auto-incrementing from metadata.lastId
  text: string;           // Quote text
  author: string;         // Stoic author name
  source: string;         // Book/work name
  theme: string;          // Theme category
  favorite: boolean;      // User favorite flag
  notes: string | null;   // Personal reflections
  createdAt: string;      // ISO timestamp
  addedBy: string;        // "seed" | "user" | "manual"
}
```

### Storage Schema v1.0.0

```json
{
  "metadata": {
    "lastId": 42,
    "version": "1.0.0",
    "lastModified": "2025-10-30T12:34:56.789Z"
  },
  "quotes": [
    { /* Quote objects */ }
  ]
}
```

### Key Features

#### 9 Tools for Quote Management

1. **get_random_quote**: Random quote for daily inspiration
2. **search_quotes**: Filter by author, theme, or keyword
3. **add_quote**: Manually add new quotes to collection
4. **get_quote_explanation**: AI-powered developer context
5. **toggle_favorite**: Mark/unmark quotes as favorites
6. **get_favorites**: List all favorite quotes
7. **update_quote_notes**: Add personal reflections
8. **delete_quote**: Remove quotes from collection
9. **generate_quote**: AI-generate Stoic-style quotes on themes

#### AI-Powered Features

**Quote Explanations** (`get_quote_explanation`):
- Receives quote ID
- DeepSeek API analyzes quote
- Returns modern developer context
- Explains application to coding challenges

**Quote Generation** (`generate_quote`):
- Receives theme (e.g., "debugging", "code review")
- DeepSeek API creates Stoic-style quote
- Returns formatted quote text
- User can add to collection with `add_quote`

#### Theme Categories (18 Total)

**Core Stoic Themes**:
- Control, Mindset, Courage, Wisdom
- Discipline, Acceptance, Virtue, Justice

**Developer Themes**:
- Focus, Resilience, Learning, Simplicity
- Perspective, Action, Tranquility, Reason

**Universal Themes**:
- Time, Change

### Data Flow

#### Quote Retrieval Flow
1. Client requests `get_random_quote`
2. MCP Server receives via stdio
3. QuoteStorage reads `quotes.json`
4. Random quote selected
5. Access metadata updated (favorite, notes)
6. Formatted response returned

#### AI Explanation Flow
1. Client requests `get_quote_explanation` with ID
2. QuoteStorage retrieves quote by ID
3. DeepSeekService calls API with structured prompt
4. API returns developer-focused explanation
5. Combined quote + explanation returned to client

### Bulk Import System

**Location**: `local/quotes-source/`

**Import Format** (one per line):
```
"Quote text here" - Author Name, Source Book
```

**Usage**:
```bash
cd local
npm run import sample-import.txt
```

**Features**:
- Auto-detects themes from keywords
- Generates sequential IDs from metadata.lastId
- Atomically appends to quotes.json
- Updates metadata (lastId, lastModified)
- Validates format before import
- See `local/IMPORT_GUIDE.md` for full docs

**Theme Detection**:
```typescript
// Keywords mapped to themes
control: ["control", "power", "agency"]
mindset: ["think", "mind", "perception"]
courage: ["fear", "brave", "courage"]
// ... 15 more categories
```

### TypeScript Build Process

```bash
# Development workflow
npm run watch      # Watch mode (auto-compile on save)
npm run build      # One-time compilation
npm run dev        # Build + run in one command

# File structure
local/
├── src/
│   ├── index.ts         # Main MCP server
│   ├── storage.ts       # Quote storage logic
│   ├── deepseek.ts      # AI integration
│   ├── types.ts         # TypeScript interfaces
│   └── import-quotes.ts # Bulk import utility
├── dist/                # Compiled JavaScript (gitignored)
│   └── *.js
├── quotes.json          # Data file
└── tsconfig.json        # TypeScript config
```

### Configuration

#### Environment Variables

**Required for AI Features**:
```bash
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxx
```

**Can be set via**:
1. `.env` file in `local/` directory
2. Claude Desktop config (system environment)
3. Shell export (e.g., `export DEEPSEEK_API_KEY=...`)

#### Claude Desktop Integration

**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
**Mac**: `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "stoic-mcp": {
      "command": "node",
      "args": ["C:\\github\\stoic-mcp\\local\\dist\\index.js"],
      "env": {
        "DEEPSEEK_API_KEY": "sk-xxxxxxxxxxxxx"
      }
    }
  }
}
```

**Notes**:
- Path must point to **compiled** `dist/index.js`
- Use double backslashes on Windows
- API key in config is optional (can use system env)

#### VS Code Integration

**Location**: `.vscode/mcp.json` in workspace

```json
{
  "mcpServers": {
    "stoic-mcp": {
      "command": "node",
      "args": ["${workspaceFolder}/local/dist/index.js"],
      "env": {
        "DEEPSEEK_API_KEY": "sk-xxxxxxxxxxxxx"
      }
    }
  }
}
```

### Development Workflow

#### Initial Setup
```bash
# Clone repository
git clone <repo-url>
cd stoic-mcp/local

# Install dependencies
npm install

# Build TypeScript
npm run build

# Test with MCP Inspector
npx @modelcontextprotocol/inspector node dist/index.js
```

#### Daily Development
```bash
# Start watch mode (auto-rebuild on save)
npm run watch

# In another terminal, test changes
# (restart Claude Desktop to reload MCP server)
```

#### Adding Quotes
```bash
# Option 1: Use bulk import
echo '"New quote" - Author, Source' >> quotes-source/my-quotes.txt
npm run import my-quotes.txt

# Option 2: Use add_quote tool in Claude Desktop
# (manually via AI conversation)
```

### Error Handling

**Missing API Key**:
```javascript
// DeepSeekService provides fallback message
if (!process.env.DEEPSEEK_API_KEY) {
  return "AI explanation requires DEEPSEEK_API_KEY. Set it in environment or .env file.";
}
```

**Quote Not Found**:
```javascript
// Returns null, handled by tool
const quote = await storage.searchQuotes({}).find(q => q.id === quoteId);
if (!quote) {
  return { content: [{ type: 'text', text: 'Quote not found' }] };
}
```

**Import Errors**:
- Validates format before processing
- Skips malformed lines with warning
- Continues processing remaining lines

### Performance Characteristics

- Quote operations: <5ms (local JSON read)
- Search: <10ms (linear scan through array)
- AI explanation: 500-2000ms (API latency)
- AI generation: 1000-3000ms (API latency)
- Import: ~10ms per quote

### Testing

```bash
# Test MCP Inspector connection
npx @modelcontextprotocol/inspector node dist/index.js

# Test tools manually in Inspector UI:
# 1. get_random_quote → verify quote returned
# 2. search_quotes (query: "courage") → verify filtering
# 3. add_quote → verify new quote appears
# 4. get_quote_explanation (with API key) → verify AI response
```

### Module System

**ES Modules** (`"type": "module"` in package.json):
- Import with `.js` extensions (TypeScript convention)
- Use `fileURLToPath` for `__dirname` equivalent
- Top-level `await` supported

```typescript
// Example import
import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
```

### Logging

All logging to `console.error` (stderr):
- Keeps stdout clean for MCP protocol
- Visible in Claude Desktop logs
- Format: Emoji + descriptive message

```javascript
console.error('📖 Loading quotes from storage...');
console.error('✅ Found 42 quotes');
console.error('🤖 Generating AI explanation...');
```

### Next Steps for Production

See `stoic-mcp-azure.md` for:
- Migration to Cosmos DB
- Azure Container Apps deployment
- Multi-container architecture (2 containers)
- Metadata tracking container
- Production scaling and monitoring
