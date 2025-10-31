# Stoic MCP Server: Code Walkthrough

**A beginner-friendly guide to understanding how this MCP server works.**

---

## 📋 Table of Contents

1. [Project Overview](#project-overview)
2. [File Structure](#file-structure)
3. [Core Concepts](#core-concepts)
4. [Code Deep Dive](#code-deep-dive)
5. [How It All Works Together](#how-it-all-works-together)
6. [Common Patterns](#common-patterns)
7. [Extending the Server](#extending-the-server)

---

## Project Overview

This MCP server demonstrates **three key concepts**:

1. **MCP Protocol Implementation** - How to build a server that AI assistants can talk to
2. **Tool Registration** - How to expose functions that AI can call
3. **External API Integration** - How to connect to services like DeepSeek for AI features

**What it does**: Serves Stoic philosophy quotes with CRUD operations and AI-powered explanations.

---

## File Structure

```
stoic-mcp/local/
├── src/
│   ├── index.ts         # Main server entry point
│   ├── types.ts         # TypeScript interfaces
│   ├── storage.ts       # JSON file operations
│   ├── deepseek.ts      # AI integration
│   └── import-quotes.ts # Data import utility
├── quotes.json          # Quote database
├── package.json         # Dependencies
└── tsconfig.json        # TypeScript config
```

**Key takeaway**: Clean separation of concerns. Each file has one job.

---

## Core Concepts

### 1. The MCP Server Instance

Every MCP server starts with creating a `Server` object:

```typescript
import { Server } from '@modelcontextprotocol/sdk/server/index.js';

const server = new Server(
  {
    name: 'stoic-mcp-local',    // Your server's name
    version: '1.0.0',            // Semantic version
  },
  {
    capabilities: {
      tools: {},                 // Declares we support tools
    },
  }
);
```

**Why this matters**: This tells AI assistants what your server can do.

### 2. Request Handlers

MCP uses request/response patterns. You register handlers for different types of requests:

```typescript
// Tell the AI what tools are available
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return { tools: [...] };
});

// Execute tools when the AI calls them
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  // Handle the tool call
});
```

### 3. Transport Layer

The server communicates via **stdio** (standard input/output):

```typescript
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';

const transport = new StdioServerTransport();
await server.connect(transport);
```

**What this means**: Your MCP server runs as a child process, communicating through stdin/stdout.

---

## Code Deep Dive

### 📁 types.ts - Data Models

**Purpose**: Define the shape of our data using TypeScript interfaces.

```typescript
export interface Quote {
  id: number;              // Unique identifier
  text: string;            // The quote itself
  author: string;          // Who said it
  source: string;          // Book/work it's from
  theme: string;           // Category (courage, wisdom, etc.)
  favorite: boolean;       // User's favorite flag
  notes: string | null;    // Personal reflections
  createdAt: string;       // Timestamp
  addedBy: string;         // Who added it
}
```

**Key concept**: Strong typing helps catch errors at compile time.

**The metadata wrapper**:

```typescript
export interface QuotesData {
  metadata: {
    lastId: number;           // Auto-increment counter
    version: string;          // Schema version
    lastModified: string;     // Last update timestamp
  };
  quotes: Quote[];            // Array of all quotes
}
```

**Why metadata?**: Tracks database state without scanning all records.

---

### 📁 storage.ts - Data Persistence

**Purpose**: Handle all file I/O operations. This is your data layer.

#### Reading Data

```typescript
private async readQuotes(): Promise<QuotesData> {
  try {
    const data = await readFile(QUOTES_FILE, 'utf-8');
    return JSON.parse(data);
  } catch (error) {
    // Return empty structure if file doesn't exist
    return {
      metadata: {
        lastId: 0,
        version: '1.0.0',
        lastModified: new Date().toISOString()
      },
      quotes: []
    };
  }
}
```

**Pattern**: Graceful degradation. If the file doesn't exist, start fresh.

#### Writing Data

```typescript
private async writeQuotes(data: QuotesData): Promise<void> {
  // Always update timestamp before saving
  data.metadata.lastModified = new Date().toISOString();

  // Pretty-print JSON for human readability
  await writeFile(QUOTES_FILE, JSON.stringify(data, null, 2), 'utf-8');
}
```

**Pro tip**: The `null, 2` arguments to `JSON.stringify()` make the output readable.

#### Search Implementation

```typescript
async searchQuotes(params: SearchParams): Promise<Quote[]> {
  const data = await this.readQuotes();
  let results = data.quotes;

  // Filter by author
  if (params.author) {
    results = results.filter(q =>
      q.author.toLowerCase().includes(params.author!.toLowerCase())
    );
  }

  // Filter by exact theme
  if (params.theme) {
    results = results.filter(q =>
      q.theme.toLowerCase() === params.theme!.toLowerCase()
    );
  }

  // Full-text search across multiple fields
  if (params.query) {
    const searchLower = params.query.toLowerCase();
    results = results.filter(q =>
      q.text.toLowerCase().includes(searchLower) ||
      q.author.toLowerCase().includes(searchLower) ||
      q.theme.toLowerCase().includes(searchLower)
    );
  }

  return results;
}
```

**Key pattern**: Progressive filtering. Each condition narrows the results.

#### Adding Quotes

```typescript
async addQuote(quote: Omit<Quote, 'id'>): Promise<Quote> {
  const data = await this.readQuotes();

  // Auto-increment ID from metadata
  const newId = data.metadata.lastId + 1;

  const newQuote: Quote = { ...quote, id: newId };

  data.quotes.push(newQuote);
  data.metadata.lastId = newId;  // Update metadata
  await this.writeQuotes(data);

  return newQuote;
}
```

**Important**: `Omit<Quote, 'id'>` means "all Quote fields except id". The server generates IDs.

---

### 📁 deepseek.ts - AI Integration

**Purpose**: Connect to DeepSeek API for AI-powered explanations and generation.

#### Constructor Pattern

```typescript
export class DeepSeekService {
  private apiKey: string;

  constructor() {
    // Read from environment variable
    this.apiKey = process.env.DEEPSEEK_API_KEY || '';

    if (!this.apiKey) {
      console.warn('DEEPSEEK_API_KEY not set. AI features disabled.');
    }
  }
}
```

**Best practice**: Fail gracefully. The server runs even without AI features.

#### Explaining Quotes

```typescript
async explainQuote(quote: Quote): Promise<string> {
  // Guard clause - check for API key
  if (!this.apiKey) {
    return 'DeepSeek API key not configured...';
  }

  // Craft a specific prompt for developer context
  const prompt = `You are a Stoic philosophy expert. Explain this quote
in practical terms for a modern software developer...

Quote: "${quote.text}"
Author: ${quote.author}
Source: ${quote.source}

Provide a concise, actionable explanation...`;

  const response = await fetch(DEEPSEEK_API_URL, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${this.apiKey}`
    },
    body: JSON.stringify({
      model: 'deepseek-chat',
      messages: [{ role: 'user', content: prompt }],
      temperature: 0.7,      // Creativity level
      max_tokens: 500        // Response length limit
    })
  });

  const data = await response.json();
  return data.choices[0].message.content;
}
```

**Key concepts**:

- **Prompt engineering**: Clear instructions to the AI
- **Temperature**: Lower = more focused, higher = more creative
- **Max tokens**: Controls response length

---

### 📁 index.ts - The Main Server

**Purpose**: Wire everything together and handle MCP protocol.

#### 1. Setup & Initialization

```typescript
import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { QuoteStorage } from './storage.js';
import { DeepSeekService } from './deepseek.js';

// Create service instances
const storage = new QuoteStorage();
const deepseek = new DeepSeekService();

// Create MCP server
const server = new Server(
  { name: 'stoic-mcp-local', version: '1.0.0' },
  { capabilities: { tools: {} } }
);
```

**Pattern**: Dependency injection. Create services once, reuse them.

#### 2. Tool Registration

Each tool needs:

- **name**: Unique identifier
- **description**: What it does (AI reads this!)
- **inputSchema**: JSON Schema for parameters

Example tool definition:

```typescript
{
  name: 'search_quotes',
  description: 'Search for quotes by author, theme, or keyword',
  inputSchema: {
    type: 'object',
    properties: {
      query: {
        type: 'string',
        description: 'Keyword to search in quote text, author, or theme',
      },
      author: {
        type: 'string',
        description: 'Filter by author name (e.g., "Marcus Aurelius")',
      },
      theme: {
        type: 'string',
        description: 'Filter by theme (e.g., "courage")',
      },
    },
    // Note: No 'required' array - all parameters are optional
  },
}
```

**Critical**: Good descriptions help the AI choose the right tool!

#### 3. Tool Execution

The `CallToolRequestSchema` handler is a big switch statement:

```typescript
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  try {
    switch (name) {
      case 'get_random_quote': {
        const quote = await storage.getRandomQuote();

        // Handle empty database
        if (!quote) {
          return {
            content: [{ type: 'text', text: 'No quotes available' }],
          };
        }

        // Format response for readability
        return {
          content: [{
            type: 'text',
            text: `"${quote.text}"\n\n— ${quote.author}, ${quote.source}\n\n` +
                  `Theme: ${quote.theme}\nID: ${quote.id}` +
                  `${quote.favorite ? ' ⭐' : ''}` +
                  `${quote.notes ? `\n\nYour notes: ${quote.notes}` : ''}`
          }],
        };
      }

      case 'search_quotes': {
        const quotes = await storage.searchQuotes(args as any);

        if (quotes.length === 0) {
          return {
            content: [{ type: 'text', text: 'No quotes found...' }],
          };
        }

        const formatted = quotes
          .map(q =>
            `[${q.id}${q.favorite ? ' ⭐' : ''}] "${q.text}"\n` +
            `— ${q.author}, ${q.source} (Theme: ${q.theme})`
          )
          .join('\n\n');

        return {
          content: [{
            type: 'text',
            text: `Found ${quotes.length} quote(s):\n\n${formatted}`
          }],
        };
      }

      // ... more cases ...

      default:
        return {
          content: [{ type: 'text', text: `Unknown tool: ${name}` }],
          isError: true,
        };
    }
  } catch (error) {
    // Global error handler
    return {
      content: [{
        type: 'text',
        text: `Error: ${error instanceof Error ? error.message : 'Unknown error'}`
      }],
      isError: true,
    };
  }
});
```

**Patterns to notice**:

- **Early returns** for edge cases
- **Consistent response format** (always `{ content: [...] }`)
- **Error handling** at multiple levels
- **Type assertions** (`args as any`) because MCP sends generic objects

#### 4. Server Startup

```typescript
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);

  // Log to stderr (not stdout, which is used for protocol)
  console.error('Stoic MCP Local Server running on stdio');
}

main().catch((error) => {
  console.error('Fatal error:', error);
  process.exit(1);
});
```

**Critical**: Use `console.error()` for logging, not `console.log()`. stdout is reserved for MCP protocol!

---

## How It All Works Together

### Request Flow Diagram

```
┌─────────────┐
│ AI Assistant│
│  (Claude)   │
└──────┬──────┘
       │ 1. "Get me a random Stoic quote"
       ▼
┌─────────────────────┐
│  MCP Client         │
│  (in Claude)        │
└──────┬──────────────┘
       │ 2. call_tool("get_random_quote", {})
       ▼
┌─────────────────────┐
│  stdio transport    │  (stdin/stdout)
└──────┬──────────────┘
       │ 3. JSON-RPC message
       ▼
┌─────────────────────┐
│  index.ts           │
│  CallToolRequest    │
│  handler            │
└──────┬──────────────┘
       │ 4. storage.getRandomQuote()
       ▼
┌─────────────────────┐
│  storage.ts         │
│  QuoteStorage class │
└──────┬──────────────┘
       │ 5. Read quotes.json
       ▼
┌─────────────────────┐
│  quotes.json        │
│  [{ id: 1, ... }]   │
└──────┬──────────────┘
       │ 6. Return random quote
       ▼
┌─────────────────────┐
│  index.ts           │
│  Format response    │
└──────┬──────────────┘
       │ 7. Return { content: [...] }
       ▼
┌─────────────────────┐
│  AI Assistant       │
│  Display to user    │
└─────────────────────┘
```

### Example: Adding a Quote

1. **User asks**: "Add this quote: 'You have power over your mind...'"
2. **AI decides**: Use `add_quote` tool
3. **AI calls**: `add_quote({ text: "...", author: "Marcus Aurelius", ... })`
4. **Server receives**: CallToolRequest with name="add_quote" and args object
5. **Switch statement**: Routes to `add_quote` case
6. **Storage layer**:
   - Reads current quotes.json
   - Generates new ID from metadata
   - Adds quote to array
   - Updates metadata.lastId
   - Writes updated JSON
7. **Response**: Returns confirmation with new quote details
8. **AI formats**: Presents success message to user

---

## Common Patterns

### 1. The Guard Clause Pattern

Check for problems first, then proceed:

```typescript
case 'delete_quote': {
  // Guard: Check arguments exist
  if (!args) {
    return {
      content: [{ type: 'text', text: 'Missing required arguments' }],
      isError: true,
    };
  }

  const deleted = await storage.deleteQuote(Number(args.quote_id));

  // Guard: Check quote was found
  if (!deleted) {
    return {
      content: [{ type: 'text', text: `Quote ${args.quote_id} not found` }],
    };
  }

  // Happy path
  return {
    content: [{ type: 'text', text: `Quote ${args.quote_id} deleted` }],
  };
}
```

### 2. The Null Object Pattern

Return empty structures instead of null:

```typescript
async readQuotes(): Promise<QuotesData> {
  try {
    const data = await readFile(QUOTES_FILE, 'utf-8');
    return JSON.parse(data);
  } catch (error) {
    // Don't return null - return valid empty structure
    return {
      metadata: { lastId: 0, version: '1.0.0', lastModified: new Date().toISOString() },
      quotes: []
    };
  }
}
```

### 3. The Error Wrapper Pattern

Catch errors and return MCP-compliant responses:

```typescript
try {
  // Attempt operation
  const result = await someOperation();
  return { content: [{ type: 'text', text: result }] };
} catch (error) {
  // Convert any error to MCP format
  return {
    content: [{
      type: 'text',
      text: `Error: ${error instanceof Error ? error.message : 'Unknown error'}`
    }],
    isError: true,
  };
}
```

### 4. The Filter Chain Pattern

Progressive refinement of results:

```typescript
async searchQuotes(params: SearchParams): Promise<Quote[]> {
  let results = await this.getAllQuotes();

  if (params.author) results = results.filter(/* author filter */);
  if (params.theme) results = results.filter(/* theme filter */);
  if (params.query) results = results.filter(/* text search */);

  return results;
}
```

---

## Extending the Server

### Adding a New Tool

**Example**: Add a `get_quote_by_id` tool

#### Step 1: Define the tool in `ListToolsRequestSchema`

```typescript
{
  name: 'get_quote_by_id',
  description: 'Retrieve a specific quote by its ID number',
  inputSchema: {
    type: 'object',
    properties: {
      id: {
        type: 'number',
        description: 'The unique ID of the quote',
      },
    },
    required: ['id'],  // This parameter is mandatory
  },
}
```

#### Step 2: Add storage method in `storage.ts`

```typescript
async getQuoteById(id: number): Promise<Quote | null> {
  const data = await this.readQuotes();
  return data.quotes.find(q => q.id === id) || null;
}
```

#### Step 3: Handle the tool call in `index.ts`

```typescript
case 'get_quote_by_id': {
  if (!args) {
    return {
      content: [{ type: 'text', text: 'Missing required arguments' }],
      isError: true,
    };
  }

  const quote = await storage.getQuoteById(Number(args.id));

  if (!quote) {
    return {
      content: [{ type: 'text', text: `No quote found with ID ${args.id}` }],
    };
  }

  return {
    content: [{
      type: 'text',
      text: `[${quote.id}] "${quote.text}"\n— ${quote.author}, ${quote.source}`
    }],
  };
}
```

#### Step 4: Rebuild and test

```bash
npm run build
npm run inspector
```

---

### Adding a New Data Field

**Example**: Add a `difficulty` field to rate philosophical complexity

#### Step 1: Update the type in `types.ts`

```typescript
export interface Quote {
  id: number;
  text: string;
  author: string;
  source: string;
  theme: string;
  difficulty: 'beginner' | 'intermediate' | 'advanced';  // NEW
  favorite: boolean;
  notes: string | null;
  createdAt: string;
  addedBy: string;
}
```

#### Step 2: Update the add_quote tool schema

```typescript
{
  name: 'add_quote',
  inputSchema: {
    type: 'object',
    properties: {
      text: { type: 'string', description: '...' },
      author: { type: 'string', description: '...' },
      source: { type: 'string', description: '...' },
      theme: { type: 'string', description: '...' },
      difficulty: {                                        // NEW
        type: 'string',
        enum: ['beginner', 'intermediate', 'advanced'],
        description: 'Philosophical complexity level',
      },
    },
    required: ['text', 'author', 'source', 'theme', 'difficulty'],  // Add to required
  },
}
```

#### Step 3: Update the handler

```typescript
case 'add_quote': {
  const newQuote = await storage.addQuote({
    text: args.text as string,
    author: args.author as string,
    source: args.source as string,
    theme: args.theme as string,
    difficulty: args.difficulty as 'beginner' | 'intermediate' | 'advanced',  // NEW
    favorite: false,
    notes: null,
    createdAt: new Date().toISOString(),
    addedBy: 'user',
  });
  // ...
}
```

#### Step 4: Migrate existing data

Add a migration script to set default values:

```typescript
// scripts/migrate-difficulty.ts
const data = await readQuotes();
data.quotes.forEach(quote => {
  if (!quote.difficulty) {
    quote.difficulty = 'intermediate';  // Default value
  }
});
await writeQuotes(data);
```

---

## Key Takeaways

### For Learning MCP

1. **Servers are just request handlers** - Listen for tool calls, execute them, return results
2. **stdio is the transport** - Your server is a child process
3. **JSON Schema defines contracts** - The AI reads your schemas to understand what to call
4. **Error handling matters** - Always return valid MCP responses, even for errors

### For Code Architecture

1. **Separation of concerns** - Each file has one responsibility
2. **Type safety** - TypeScript catches errors before runtime
3. **Graceful degradation** - Features fail independently
4. **Data validation** - Check arguments before using them

### For Production Readiness

1. **Environment variables** - Never hardcode secrets
2. **Logging to stderr** - stdout is for protocol only
3. **Metadata tracking** - Don't scan files to get next ID
4. **Atomic operations** - Read-modify-write as one unit

---

## Next Steps

1. **Run the Inspector**: `npm run inspector` to see the protocol in action
2. **Add a tool**: Follow the "Adding a New Tool" section above
3. **Integrate with Claude**: Update your `claude_desktop_config.json`
4. **Explore Azure version**: See how `../azure/` replaces JSON with Cosmos DB

---

## Troubleshooting Tips

### "Server not responding"

- Check that you built with `npm run build`
- Verify the path in your MCP config is correct
- Look for errors in the server's stderr output

### "Tool not found"

- Did you rebuild after adding the tool?
- Check spelling in both the tool definition and the switch case
- Restart Claude to reload the server

### "Type errors"

- Run `npm run build` to see TypeScript errors
- Check that your interfaces match your JSON data
- Use type assertions (`as`) only when necessary

### "Data not persisting"

- Verify `quotes.json` exists and is writable
- Check file paths (use absolute paths in production)
- Look for write errors in server logs

---

## Azure Deployment

### From JSON to Cosmos DB

The Azure version of this server replaces the local JSON file with **Cosmos DB**, Microsoft's globally distributed NoSQL database.

#### Architecture Differences

**Local Version**:

```
JSON File (quotes.json)
└── QuotesData
    ├── metadata (lastId, version, lastModified)
    └── quotes[] (array of Quote objects)
```

**Azure Version**:

```
Cosmos DB Account (stoic-cosmos-xxx)
└── Database: stoic
    ├── Container: quotes (partition key: /id)
    │   └── Individual quote documents
    └── Container: metadata (partition key: /type)
        └── System metadata documents
```

**Key change**: Instead of reading/writing one big JSON file, we read/write individual documents to Cosmos DB containers.

---

### Infrastructure Components

The Azure deployment creates these resources:

```typescript
// What main.bicep creates:

1. Cosmos DB Account (FREE TIER)
   - Cost: $0/month (1000 RU/s, 25GB storage included)
   - Consistency: Session level
   - Location: Single region

2. Cosmos DB Database: "stoic"
   - Shared throughput: 400 RU/s

3. Cosmos DB Containers:
   - quotes (partition key: /id)
   - metadata (partition key: /type)

4. Azure Container Apps
   - Scale: 0-3 replicas (scale-to-zero!)
   - Resources: 0.25 CPU, 0.5Gi RAM
   - Image: Built from Dockerfile

5. Key Vault
   - Stores: DeepSeek API key, Cosmos connection string
   - Access: Managed Identity with RBAC

6. Log Analytics Workspace
   - Retention: 30 days
   - Cost: ~$2-5/month

7. Managed Identity
   - No passwords needed
   - RBAC access to Key Vault
```

**Total Cost**: ~$8-15/month for production workload

---

### Dockerfile: Multi-Stage Build

The production Dockerfile uses **two stages** to minimize image size:

#### Stage 1: Builder

```dockerfile
FROM node:20-alpine AS builder

WORKDIR /app

# Install dependencies (including TypeScript)
COPY package*.json tsconfig.json ./
RUN npm install

# Build TypeScript to JavaScript
COPY src/ ./src/
COPY quotes.json ./quotes.json
RUN npm run build
# Creates dist/ folder with compiled .js files
```

**Purpose**: Compile TypeScript in a separate stage. We don't include TypeScript compiler in the final image.

#### Stage 2: Production

```dockerfile
FROM node:20-alpine

# Install dumb-init (proper signal handling for Docker)
RUN apk add --no-cache dumb-init

# Create non-root user for security
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nodejs -u 1001

WORKDIR /app

# Install ONLY production dependencies
COPY package*.json ./
RUN npm install --only=production

# Copy ONLY compiled code from builder
COPY --from=builder --chown=nodejs:nodejs /app/dist ./dist
COPY --from=builder --chown=nodejs:nodejs /app/quotes.json ./quotes.json

# Health check endpoint
HEALTHCHECK --interval=30s --timeout=3s \
  CMD node -e "require('http').get('http://localhost:3000/health', ...)"

# Run as non-root user
USER nodejs

ENTRYPOINT ["dumb-init", "--"]
CMD ["node", "dist/index.js"]
```

**Key patterns**:

- **Multi-stage**: Keeps final image small (~150MB vs ~500MB)
- **Non-root user**: Security best practice
- **dumb-init**: Properly handles SIGTERM for graceful shutdown
- **Health check**: Container Apps uses this for liveness/readiness

---

### Code Changes for Cosmos DB

The Azure version modifies the `QuoteStorage` class:

#### Local Version (JSON)

```typescript
private async readQuotes(): Promise<QuotesData> {
  const data = await readFile(QUOTES_FILE, 'utf-8');
  return JSON.parse(data);
}

private async writeQuotes(data: QuotesData): Promise<void> {
  await writeFile(QUOTES_FILE, JSON.stringify(data, null, 2));
}
```

#### Azure Version (Cosmos DB)

```typescript
// Cosmos DB client initialization
import { CosmosClient } from '@azure/cosmos';

const client = new CosmosClient(process.env.COSMOS_CONNECTION_STRING);
const database = client.database('stoic');
const quotesContainer = database.container('quotes');
const metadataContainer = database.container('metadata');

// Read a single quote
async getQuoteById(id: number): Promise<Quote | null> {
  try {
    const { resource } = await quotesContainer.item(id.toString(), id.toString()).read();
    return resource;
  } catch (error) {
    if (error.code === 404) return null;
    throw error;
  }
}

// Add a quote
async addQuote(quote: Omit<Quote, 'id'>): Promise<Quote> {
  // Get next ID from metadata container
  const metadata = await this.getMetadata();
  const newId = metadata.lastId + 1;

  const newQuote: Quote = { ...quote, id: newId };

  // Create document in Cosmos DB
  await quotesContainer.items.create(newQuote);

  // Update metadata
  metadata.lastId = newId;
  await this.updateMetadata(metadata);

  return newQuote;
}

// Search quotes (query all documents)
async searchQuotes(params: SearchParams): Promise<Quote[]> {
  const querySpec = {
    query: 'SELECT * FROM c WHERE CONTAINS(LOWER(c.text), @query) OR CONTAINS(LOWER(c.author), @query)',
    parameters: [{ name: '@query', value: params.query.toLowerCase() }]
  };

  const { resources } = await quotesContainer.items.query(querySpec).fetchAll();
  return resources;
}
```

**Key differences**:

- **No file I/O**: Use Cosmos SDK instead of `fs.readFile/writeFile`
- **Document-based**: Each quote is a separate document
- **Queries**: Use SQL-like syntax for searching
- **Partition keys**: Each document has `id` as partition key
- **Async/await**: All operations are async (network calls)

---

### Deployment Workflow

#### Step 1: Build Docker Image

```bash
cd stoic-mcp/local
docker build -t stoic-mcp:latest .
```

**What happens**:

1. TypeScript compilation (`npm run build`)
2. Production dependencies only
3. Non-root user creation
4. Health check configuration
5. Image tagged as `stoic-mcp:latest`

#### Step 2: Push to Azure Container Registry

```bash
# Tag for ACR
docker tag stoic-mcp:latest myacr.azurecr.io/stoic-mcp:v1

# Login to ACR
az acr login --name myacr

# Push image
docker push myacr.azurecr.io/stoic-mcp:v1
```

#### Step 3: Deploy Infrastructure with Bicep

```bash
az deployment group create \
  --resource-group context-engineering-rg \
  --template-file azure/main.bicep \
  --parameters \
    containerImage=myacr.azurecr.io/stoic-mcp:v1 \
    deepseekApiKey=$DEEPSEEK_API_KEY \
    managedIdentityName=context-msi
```

**What Bicep deploys**:

1. Cosmos DB account, database, containers
2. Container App with your Docker image
3. Key Vault with secrets
4. Log Analytics for monitoring
5. RBAC role assignments

**Deployment time**: 10-15 minutes

#### Step 4: Verify Deployment

```bash
# Get Container App URL
APP_URL=$(az containerapp show \
  --name stoic-app-xxx \
  --resource-group context-engineering-rg \
  --query properties.configuration.ingress.fqdn -o tsv)

# Test health endpoint
curl https://$APP_URL/health

# Expected response:
# {"status":"healthy","timestamp":"2025-10-31T12:00:00Z","service":"stoic-mcp"}
```

---

### Environment Variables in Azure

**Local version** uses `.env` file:

```bash
DEEPSEEK_API_KEY=sk-xxxxx
```

**Azure version** uses Key Vault secrets injected as environment variables:

```bicep
env: [
  {
    name: 'DEEPSEEK_API_KEY'
    secretRef: 'deepseek-api-key'  // Pulled from Key Vault
  }
  {
    name: 'COSMOS_CONNECTION_STRING'
    secretRef: 'cosmos-connection-string'  // Generated by Bicep
  }
  {
    name: 'COSMOS_DATABASE'
    value: 'stoic'
  }
  {
    name: 'COSMOS_CONTAINER_QUOTES'
    value: 'quotes'
  }
  {
    name: 'COSMOS_CONTAINER_METADATA'
    value: 'metadata'
  }
]
```

**Security benefit**: Secrets never appear in code or logs!

---

### Scaling Behavior

The Container App automatically scales based on load:

```bicep
scale: {
  minReplicas: 0      // Scale to ZERO when idle (cost savings!)
  maxReplicas: 3      // Scale up under load
  rules: [
    {
      name: 'http-scaling'
      http: {
        metadata: {
          concurrentRequests: '10'  // Trigger: >10 concurrent requests
        }
      }
    }
  ]
}
```

**Example scaling scenario**:

- **0 requests**: 0 replicas (cost: $0)
- **5 requests**: 1 replica spins up (5-10 second cold start)
- **25 requests**: 3 replicas running
- **0 requests again**: Scales back to 0 after 5 minutes

**Cost impact**: Pay only for active time!

---

### Monitoring and Logs

#### View Container Logs

```bash
az containerapp logs show \
  --name stoic-app-xxx \
  --resource-group context-engineering-rg \
  --follow
```

**Output**:

```
🚀 Stoic MCP Server starting...
🔑 Deepseek API configured
📊 Connected to Cosmos DB: stoic
✅ Server ready on port 3000
```

#### Query Logs with KQL (Kusto Query Language)

In Azure Portal → Log Analytics → Logs:

```kql
ContainerAppConsoleLogs_CL
| where ContainerAppName_s contains "stoic"
| project TimeGenerated, Log_s
| order by TimeGenerated desc
| take 100
```

#### Application Insights (Optional)

Add to Dockerfile:

```typescript
import * as appInsights from 'applicationinsights';

appInsights.setup(process.env.APPLICATIONINSIGHTS_CONNECTION_STRING)
  .setAutoCollectRequests(true)
  .setAutoCollectPerformance(true)
  .start();
```

**Benefits**: Performance metrics, dependency tracking, custom events

---

### Cost Breakdown

| Service | Tier/SKU | Monthly Cost |
|---------|----------|--------------|
| Cosmos DB | Free Tier (1000 RU/s, 25GB) | $0 |
| Container Apps | Consumption (0.25 CPU, 0.5Gi) | $1-5 |
| Key Vault | Standard | $0.03 |
| Log Analytics | 30-day retention | $2-5 |
| Container Registry | Basic (shared) | $5 |
| Managed Identity | N/A | $0 |
| **Total** | | **$8-15/month** |

**Optimization tips**:

- **Use free tier Cosmos DB** (one per subscription)
- **Scale to zero** when not in use
- **Share ACR** across multiple projects
- **Limit log retention** to 30 days

---

### Production Readiness Checklist

When the Azure version is deployed, you get:

- ✅ **High availability**: Multi-zone redundancy (if enabled)
- ✅ **Auto-scaling**: 0-3 replicas based on load
- ✅ **Secure secrets**: Key Vault with RBAC
- ✅ **Monitoring**: Log Analytics + Container Insights
- ✅ **Health checks**: Liveness and readiness probes
- ✅ **Non-root container**: Security hardened
- ✅ **HTTPS only**: Ingress configured for TLS
- ✅ **Managed Identity**: No passwords in code
- ✅ **Backup**: Cosmos DB point-in-time restore
- ✅ **CI/CD ready**: GitHub Actions workflow included

---

### Quick Deployment Script

The `azure/deploy.sh` script automates everything:

```bash
#!/bin/bash
# Stoic MCP Azure Deployment Script

# 1. Pre-flight checks
check_prerequisites() {
  command -v az >/dev/null || { echo "Install Azure CLI"; exit 1; }
  command -v docker >/dev/null || { echo "Install Docker"; exit 1; }
  az account show >/dev/null || { echo "Run: az login"; exit 1; }
}

# 2. Get/create Azure Container Registry
get_or_create_acr() {
  ACR_NAME=$(az acr list --query "[0].name" -o tsv)
  if [ -z "$ACR_NAME" ]; then
    echo "Creating ACR..."
    az acr create --name myacr --sku Basic
  fi
}

# 3. Build and push Docker image
build_and_push() {
  cd ../local
  docker build -t stoic-mcp:latest .
  docker tag stoic-mcp:latest $ACR_NAME.azurecr.io/stoic-mcp:v1
  az acr login --name $ACR_NAME
  docker push $ACR_NAME.azurecr.io/stoic-mcp:v1
}

# 4. Deploy Bicep template
deploy_infrastructure() {
  az deployment group create \
    --resource-group context-engineering-rg \
    --template-file main.bicep \
    --parameters containerImage=$ACR_NAME.azurecr.io/stoic-mcp:v1
}

# 5. Verify deployment
verify() {
  APP_URL=$(az containerapp show --name stoic-app-* --query ...)
  curl https://$APP_URL/health
}

# Run all steps
check_prerequisites
get_or_create_acr
build_and_push
deploy_infrastructure
verify
```

**Usage**: `./deploy.sh` (one command!)

---

### Comparison: Local vs Azure

| Aspect | Local | Azure |
|--------|-------|-------|
| **Storage** | JSON file | Cosmos DB |
| **Persistence** | Local filesystem | Cloud database |
| **Scaling** | Single instance | 0-3 replicas |
| **Cost** | $0 | ~$8-15/month |
| **Availability** | Depends on laptop | 99.95% SLA |
| **Security** | .env file | Key Vault |
| **Monitoring** | Console logs | Log Analytics |
| **Deployment** | `npm start` | Docker + Bicep |
| **Access** | localhost only | HTTPS endpoint |
| **Backup** | Manual copy | Automatic |

**Learning progression**: Start local → Deploy to Azure → Understand cloud patterns

---

### Troubleshooting Azure Deployment

#### "Free tier already used in subscription"

```bicep
// Change in main.bicep
enableFreeTier: false  // Use standard pricing instead
```

**Cost impact**: ~$25/month for Cosmos DB

#### Container fails to start

```bash
# Check logs
az containerapp logs show --name stoic-app-xxx --tail 100

# Common issues:
# - Missing environment variables
# - Cosmos DB connection string invalid
# - Port 3000 not exposed
```

#### Health check fails

```bash
# Test locally first
docker run -p 3000:3000 -e DEEPSEEK_API_KEY=xxx stoic-mcp:latest
curl http://localhost:3000/health

# Expected: 200 OK
```

#### Bicep deployment errors

```bash
# Validate template
az bicep build --file main.bicep

# Check for:
# - Parameter types
# - Resource dependencies
# - API versions
```

---

## Key Takeaways: Azure Deployment

### For Learning Cloud Patterns

1. **Storage abstraction** - Same API, different backend (JSON → Cosmos DB)
2. **Containerization** - Docker packages your app for any environment
3. **Infrastructure as Code** - Bicep defines your entire cloud setup
4. **Secrets management** - Key Vault instead of .env files
5. **Observability** - Logs, metrics, and health checks built-in

### For Production Readiness

1. **Scale-to-zero** - Pay only when app is active
2. **Auto-scaling** - Handle traffic spikes automatically
3. **Security hardening** - Non-root containers, RBAC, secret management
4. **High availability** - Multi-zone deployment (optional)
5. **Monitoring** - Log Analytics for troubleshooting

### For Cost Optimization

1. **Free tier Cosmos DB** - $0 for first 1000 RU/s
2. **Consumption pricing** - No idle costs with scale-to-zero
3. **Shared ACR** - One registry for all projects
4. **Minimal resources** - 0.25 CPU, 0.5Gi RAM is enough
5. **Log retention** - 30 days balances cost and usefulness

---

## Next Steps with Azure

1. **Deploy locally first**: `cd stoic-mcp/local && npm run inspector`
2. **Understand the code**: Walk through this guide again
3. **Build Docker image**: Test containerization locally
4. **Deploy to Azure**: Run `azure/deploy.sh`
5. **Monitor in Portal**: Watch logs and metrics
6. **Set up CI/CD**: Automate deployment with GitHub Actions
7. **Optimize costs**: Review Azure Cost Management

---

**Happy coding! Remember: Start local, understand the patterns, then deploy to the cloud.** 🏛️☁️✨
