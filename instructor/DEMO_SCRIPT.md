# MCP in Practice: Grand Demo Script

**Course**: Context Engineering with MCP - From Prompt to Persistence
**Instructor**: Tim Warner (TechTrainerTim.com)
**Duration**: 3-4 hours live demonstration
**Last Updated**: October 30, 2025

---

## 📋 Table of Contents

1. [Pre-Demo Checklist](#pre-demo-checklist)
2. [Part 1: CoreText MCP Local](#part-1-coretext-mcp-local-60-minutes)
3. [Part 2: Stoic MCP Local](#part-2-stoic-mcp-local-60-minutes)
4. [Part 3: Client Configuration](#part-3-client-configuration-30-minutes)
5. [Part 4: Azure Deployment](#part-4-azure-deployment-walkthrough-60-minutes)
6. [Troubleshooting Guide](#troubleshooting-guide)
7. [Q&A Prompts](#qa-prompts)

---

## Pre-Demo Checklist

### Before Going Live

**Terminal Setup** (5 windows):
- [ ] Terminal 1: CoreText MCP root directory
- [ ] Terminal 2: Stoic MCP root directory
- [ ] Terminal 3: Azure CLI / deployment commands
- [ ] Terminal 4: MCP Inspector (when needed)
- [ ] Terminal 5: Backup / ad-hoc commands

**Applications Open**:
- [ ] VS Code with CoreText MCP project
- [ ] VS Code with Stoic MCP project (separate window)
- [ ] Claude Desktop (closed initially, will restart)
- [ ] Web browser with tabs:
  - MCP Specification: https://spec.modelcontextprotocol.io/
  - Azure Portal: https://portal.azure.com
  - MCP Inspector: http://localhost:5173 (start later)
  - Mermaid diagrams from `diagrams/` directory

**Environment Variables**:
```bash
# Verify these are set
echo $DEEPSEEK_API_KEY    # Should show key or be empty (fallback mode works)
az account show           # Verify Azure CLI authenticated
node --version            # Should be 20+
```

**Repository State**:
```bash
cd /c/github/context-engineering-2

# Verify clean state
git status

# Verify subprojects ready
ls -la coretext-mcp/data/memory.json    # Should exist or will be created
ls -la stoic-mcp/local/quotes.json      # Should exist with seed data
ls -la stoic-mcp/local/dist/            # Should have compiled TypeScript
```

**Azure Prerequisites** (Part 4):
```bash
# Verify Azure setup
az account show
az group exists --name stoic-rg-demo
az identity show --name context-msi --resource-group shared-rg
```

---

## Part 1: CoreText MCP Local (60 minutes)

### Introduction (5 minutes)

**Talking Points**:
> "Let's start with CoreText MCP - our memory server. This demonstrates persistent AI context across sessions. We'll explore the code, test with MCP Inspector, and see live memory operations."

**Show Architecture Diagram**:
```bash
# Open in browser or VS Code
code diagrams/coretext-mcp-local.md
```

Point out:
- stdio transport (simple stdin/stdout communication)
- MemoryManager class (CRUD operations)
- DeepSeekEnrichmentService (AI integration)
- 8 tools, 3 resources
- JSON file storage

### Code Walkthrough (15 minutes)

#### Open Project
```bash
cd coretext-mcp
code src/index.js
```

#### Key Code Sections to Highlight

**1. MemoryEntry Class (Lines 48-65)**
```javascript
// TEACHING POINT: Show the class
class MemoryEntry {
  constructor(content, type = 'semantic', metadata = {}) {
    this.id = uuidv4();           // Unique identifier
    this.content = content;       // The actual memory
    this.type = type;            // 'episodic' or 'semantic'
    this.metadata = {
      created: new Date().toISOString(),
      accessCount: 0,            // Track how often accessed
      enriched: false            // AI enrichment flag
    };
    this.tags = metadata.tags || [];
  }
}
```

**Explain**:
- Episodic: "Met with client at 2pm Tuesday" (time-based events)
- Semantic: "Client prefers email" (facts and knowledge)
- UUID for unique identification across sessions
- Metadata tracks usage patterns

**2. MemoryManager CRUD Operations (Lines 71-188)**

Scroll to and explain each method:

```javascript
async create(content, type = 'semantic', metadata = {}) {
  const entry = new MemoryEntry(content, type, metadata);
  this.memories.set(entry.id, entry);
  await this.persist();  // Write to disk immediately
  console.error(`💾 Created ${type} memory: ${entry.id}`);
  return entry;
}
```

**Point out**:
- All operations are async (I/O bound)
- Immediate persistence to `data/memory.json`
- Console.error logs (stderr keeps stdout clean for MCP protocol)

**3. DeepseekEnrichmentService (Lines ~190-300)**

Scroll to enrichment logic:

```javascript
async enrich(content) {
  if (!this.apiKey) {
    return this.fallbackEnrichment(content);  // Graceful degradation
  }

  // Call DeepSeek API with structured prompt
  const response = await this.makeAPICall(/* ... */);
  return {
    summary: response.summary,
    keywords: response.keywords,
    sentiment: response.sentiment,
    category: response.category
  };
}
```

**Explain**:
- Fallback mode: Works without API key (keyword extraction)
- Production pattern: Always have graceful degradation
- Structured prompts for consistent AI responses

**4. MCP Server Setup (Lines ~400-450)**

```javascript
const server = new Server(
  {
    name: 'coretext-mcp',
    version: '1.0.0',
  },
  {
    capabilities: {
      tools: {},      // 8 CRUD tools
      resources: {}   // 3 context resources
    },
  }
);
```

**5. Tool Registration (Lines ~417-540)**

Show the ListToolsRequestSchema handler:

```javascript
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: 'memory_create',
        description: 'Create a new memory (episodic or semantic)',
        inputSchema: {
          type: 'object',
          properties: {
            content: { type: 'string', description: 'Memory content' },
            type: { type: 'string', enum: ['episodic', 'semantic'] },
            tags: { type: 'array', items: { type: 'string' } }
          },
          required: ['content']
        }
      },
      // ... 7 more tools
    ]
  };
});
```

**Explain**:
- Tools are discoverable by AI (Claude "sees" these automatically)
- JSON Schema defines parameters
- Required vs optional fields
- AI uses descriptions to decide when to call tools

**6. Tool Execution (Lines ~547-700)**

Show the CallToolRequestSchema handler switch statement:

```javascript
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  switch (name) {
    case 'memory_create': {
      const memory = await memoryManager.create(
        args.content,
        args.type || 'semantic',
        { tags: args.tags || [] }
      );
      return {
        content: [{
          type: 'text',
          text: JSON.stringify(memory, null, 2)
        }]
      };
    }
    // ... other cases
  }
});
```

**7. Resource Handlers (Lines ~765-850)**

Explain resources vs tools:
- **Tools**: AI must explicitly call them (active)
- **Resources**: Always available context (passive)

Show example:
```javascript
case 'memory://overview': {
  const stats = await memoryManager.getStats();
  return {
    contents: [{
      uri: 'memory://overview',
      mimeType: 'text/markdown',
      text: `# Memory Overview\n\nTotal: ${stats.total}\n...`
    }]
  };
}
```

### MCP Inspector Demo (25 minutes)

#### Start Inspector

```bash
# Terminal 1: Start CoreText MCP server with Inspector
npm run inspector
```

**Expected output**:
```
🔍 Starting MCP Inspector...
📡 MCP Server connected
🌐 Inspector UI: http://localhost:5173
```

Browser should auto-open to Inspector UI.

#### Inspector Tour (10 minutes)

**1. Server Info Tab**:
- Point out server name: "coretext-mcp"
- Version: "1.0.0"
- Capabilities: tools ✓, resources ✓

**2. Tools Tab**:
- Count: Should show 8 tools
- Expand each tool:
  - `memory_create`
  - `memory_read`
  - `memory_update`
  - `memory_delete`
  - `memory_search`
  - `memory_list`
  - `memory_stats`
  - `memory_enrich`

**3. Resources Tab**:
- Count: Should show 3 resources
- URIs:
  - `memory://overview`
  - `memory://context-stream`
  - `memory://knowledge-graph`

#### Live Tool Testing (15 minutes)

**Test 1: Create Memory**

In Inspector, call `memory_create`:
```json
{
  "content": "MCP enables persistent AI memory across sessions",
  "type": "semantic",
  "tags": ["mcp", "context", "demo"]
}
```

**Expected Response**:
```json
{
  "id": "uuid-here",
  "content": "MCP enables persistent AI memory across sessions",
  "type": "semantic",
  "metadata": {
    "created": "2025-10-30T...",
    "accessCount": 0,
    "enriched": false
  },
  "tags": ["mcp", "context", "demo"]
}
```

**Copy the UUID** for next tests!

**Test 2: Read Memory**

Call `memory_read`:
```json
{
  "id": "paste-uuid-here"
}
```

**Point out**:
- accessCount incremented to 1
- lastAccessed timestamp added

**Test 3: Search Memories**

Call `memory_search`:
```json
{
  "query": "mcp"
}
```

Should return all memories containing "mcp" in content or tags.

**Test 4: Memory Stats**

Call `memory_stats` (no arguments needed).

**Expected Response**:
```json
{
  "total": 4,
  "episodic": 1,
  "semantic": 3,
  "totalAccessCount": 5,
  "mostAccessed": { "id": "...", "count": 3 },
  "recentlyCreated": [...]
}
```

**Test 5: Enrich Memory** (if API key set)

Call `memory_enrich`:
```json
{
  "id": "paste-uuid-here"
}
```

Watch the API call happen, then see enrichment added to memory.

**Test 6: Read Resource**

Switch to Resources tab, click "Read" on `memory://overview`.

**Expected Response**: Markdown dashboard with:
- Total memory count
- Episodic vs semantic breakdown
- Tag cloud
- Recent activity

#### Check Persistence

```bash
# Terminal 1: View the JSON file
cat data/memory.json
```

**Point out**:
- All memories persisted
- Metadata tracking
- Pretty-printed JSON for readability

### Demo Memory Lifecycle (10 minutes)

**Scenario**: "Let's track a student's learning journey"

**1. Create episodic memory**:
```json
{
  "content": "Student completed MCP basics module on October 30, 2024",
  "type": "episodic",
  "tags": ["learning", "student", "milestone"]
}
```

**2. Create semantic memory**:
```json
{
  "content": "Student prefers hands-on coding demos over theoretical lectures",
  "type": "semantic",
  "tags": ["learning-style", "preference"]
}
```

**3. Search for student-related memories**:
```json
{
  "query": "student"
}
```

**4. Read context stream**:
- Read `memory://context-stream` resource
- Show how recent memories appear in time-windowed view

**5. Read knowledge graph**:
- Read `memory://knowledge-graph` resource
- Point out how memories with shared tags are connected

### Key Takeaways (5 minutes)

**Summarize for audience**:
1. ✅ **CRUD operations** are the foundation
2. ✅ **Tools** enable AI to manipulate memory
3. ✅ **Resources** provide passive context
4. ✅ **Persistence** means memory survives restarts
5. ✅ **Enrichment** adds AI analysis
6. ✅ **MCP Inspector** is your debugging tool

**Show the file again**:
```bash
cat data/memory.json | jq '.[] | {id, content, type}' | head -20
```

**Stop Inspector**: Ctrl+C in terminal

---

## Part 2: Stoic MCP Local (60 minutes)

### Introduction (5 minutes)

**Talking Points**:
> "Now let's look at Stoic MCP - a TypeScript implementation focused on Stoic philosophy quotes. This demonstrates a different architecture: compiled code, dual-storage (quotes + metadata), and AI-powered explanations for developers."

**Show Architecture Diagram**:
```bash
code diagrams/stoic-mcp-local.md
```

Point out:
- TypeScript (compiled to JavaScript)
- 9 tools (more features)
- Bulk import utility
- Theme detection
- AI explanations tailored to developers

### Code Walkthrough (20 minutes)

#### Open Project
```bash
cd stoic-mcp/local
code .
```

**Show File Structure**:
```
local/
├── src/
│   ├── index.ts         # Main MCP server
│   ├── storage.ts       # Quote storage logic
│   ├── deepseek.ts      # AI service
│   ├── types.ts         # TypeScript interfaces
│   └── import-quotes.ts # Bulk import tool
├── dist/                # Compiled JavaScript
├── quotes.json          # Data file
├── quotes-source/       # Import files
└── tsconfig.json        # TypeScript config
```

#### Key Code Sections

**1. Type Definitions (src/types.ts)**

```bash
code src/types.ts
```

```typescript
export interface Quote {
  id: number;              // Auto-incrementing
  text: string;           // Quote text
  author: string;         // Stoic author
  source: string;         // Book/work
  theme: string;          // Theme category
  favorite: boolean;      // User favorite flag
  notes: string | null;   // Personal reflections
  createdAt: string;      // ISO timestamp
  addedBy: string;        // "seed" | "user" | "manual"
}

export interface QuotesData {
  metadata: {
    lastId: number;        // For ID generation
    version: string;       // Schema version
    lastModified: string;  // Last update
  };
  quotes: Quote[];
}
```

**Explain**:
- Strong typing prevents bugs
- Metadata tracks last ID (auto-increment)
- Schema versioning for migrations

**2. QuoteStorage Class (src/storage.ts)**

```bash
code src/storage.ts
```

Show key methods:

```typescript
export class QuoteStorage {
  private data: QuotesData;

  async loadData(): Promise<void> {
    const content = await fs.readFile('quotes.json', 'utf-8');
    this.data = JSON.parse(content);
  }

  async saveData(): Promise<void> {
    this.data.metadata.lastModified = new Date().toISOString();
    await fs.writeFile('quotes.json', JSON.stringify(this.data, null, 2));
  }

  async addQuote(quote: Omit<Quote, 'id' | 'createdAt'>): Promise<Quote> {
    const newQuote: Quote = {
      id: ++this.data.metadata.lastId,  // Auto-increment
      ...quote,
      createdAt: new Date().toISOString()
    };
    this.data.quotes.push(newQuote);
    await this.saveData();
    return newQuote;
  }

  async searchQuotes(params: SearchParams): Promise<Quote[]> {
    return this.data.quotes.filter(q => {
      if (params.query && !q.text.toLowerCase().includes(params.query.toLowerCase())) {
        return false;
      }
      if (params.author && !q.author.toLowerCase().includes(params.author.toLowerCase())) {
        return false;
      }
      if (params.theme && q.theme !== params.theme) {
        return false;
      }
      return true;
    });
  }
}
```

**Point out**:
- Atomic operations (load → modify → save)
- ID auto-increment from metadata
- Flexible search with multiple filters

**3. DeepSeekService Class (src/deepseek.ts)**

```bash
code src/deepseek.ts
```

Show the two AI features:

```typescript
export class DeepSeekService {

  // Feature 1: Explain quote in developer context
  async explainQuote(quote: Quote): Promise<string> {
    const prompt = `
You are explaining Stoic philosophy to software developers.

Quote: "${quote.text}"
Author: ${quote.author}
Source: ${quote.source}
Theme: ${quote.theme}

Provide a practical explanation of how this quote applies to modern software development challenges like debugging, code reviews, imposter syndrome, deadline pressure, etc. Keep it under 200 words.
`;

    const response = await this.callAPI(prompt);
    return response;
  }

  // Feature 2: Generate new Stoic-style quote
  async generateQuote(theme: string): Promise<string> {
    const prompt = `
Generate a NEW Stoic-style quote about "${theme}" in software development.
Style: Brief, profound, actionable (like Marcus Aurelius or Epictetus).
Format: Just the quote text, no attribution.
`;

    const response = await this.callAPI(prompt);
    return response;
  }
}
```

**Explain**:
- Structured prompts for consistency
- Developer-focused explanations
- AI generates quotes on demand

**4. MCP Server (src/index.ts)**

```bash
code src/index.ts
```

Scroll to tool definitions (lines 28-170):

**Show the 9 tools**:
1. `get_random_quote` - Daily inspiration
2. `search_quotes` - Filter by author/theme/keyword
3. `add_quote` - Manual entry
4. `get_quote_explanation` - AI analysis
5. `toggle_favorite` - Mark/unmark favorites
6. `get_favorites` - List favorites
7. `update_quote_notes` - Personal reflections
8. `delete_quote` - Remove quotes
9. `generate_quote` - AI generation

**Highlight unique features**:
- More tools than CoreText (9 vs 8)
- Personal customization (favorites, notes)
- AI features (explain, generate)

**5. Bulk Import Utility (src/import-quotes.ts)**

```bash
code src/import-quotes.ts
```

Show the theme detection:

```typescript
const THEME_KEYWORDS = {
  control: ['control', 'power', 'agency'],
  mindset: ['think', 'mind', 'perception', 'attitude'],
  courage: ['fear', 'brave', 'courage', 'bold'],
  wisdom: ['wise', 'wisdom', 'knowledge', 'learn'],
  discipline: ['discipline', 'practice', 'habit'],
  // ... 13 more themes
};

function detectTheme(text: string): string {
  for (const [theme, keywords] of Object.entries(THEME_KEYWORDS)) {
    if (keywords.some(kw => text.toLowerCase().includes(kw))) {
      return theme;
    }
  }
  return 'general';
}
```

**Explain**:
- Automates categorization
- 18 theme categories
- Fallback to "general" if no match

### TypeScript Build Process (5 minutes)

**Show tsconfig.json**:
```bash
code tsconfig.json
```

**Point out**:
- `outDir: "dist"` - Compiled output
- `module: "ESNext"` - Modern ES modules
- `target: "ES2022"` - Modern JavaScript features
- `strict: true` - Maximum type safety

**Build the project**:
```bash
npm run build
```

**Expected output**:
```
> stoic-mcp-local@1.0.0 build
> tsc

✓ TypeScript compilation successful
```

**Show compiled output**:
```bash
ls -la dist/
# Should see: index.js, storage.js, deepseek.js, types.d.ts, etc.
```

**Explain**:
- TypeScript → JavaScript transformation
- Type declarations preserved (.d.ts files)
- Source maps for debugging

### MCP Inspector Demo (20 minutes)

**Start the server with Inspector**:

```bash
npx @modelcontextprotocol/inspector node dist/index.js
```

**Expected output**:
```
Stoic MCP Local Server running on stdio
Inspector UI: http://localhost:5173
```

Browser opens to Inspector.

#### Inspector Tour (5 minutes)

**Server Info**:
- Name: "stoic-mcp-local"
- Version: "1.0.0"
- Tools: 9 (count them)

**Tools Tab**:
Expand and show all 9 tools with their schemas.

#### Live Tool Testing (15 minutes)

**Test 1: Get Random Quote**

Call `get_random_quote` (no arguments).

**Expected Response**:
```
"You have power over your mind - not outside events. Realize this, and you will find strength."

— Marcus Aurelius, Meditations

Theme: control
ID: 15
```

**Test 2: Search Quotes**

Call `search_quotes`:
```json
{
  "author": "Marcus Aurelius"
}
```

Should list all quotes by Marcus Aurelius with IDs.

**Test 3: Search by Theme**

Call `search_quotes`:
```json
{
  "theme": "courage"
}
```

**Test 4: Add Quote**

Call `add_quote`:
```json
{
  "text": "The best revenge is not to be like your enemy.",
  "author": "Marcus Aurelius",
  "source": "Meditations",
  "theme": "mindset"
}
```

**Expected**: Quote added with auto-incremented ID.

**Verify persistence**:
```bash
# In another terminal
tail -20 quotes.json
```

Should see the new quote at the end.

**Test 5: Toggle Favorite**

Get an ID from previous search, then call `toggle_favorite`:
```json
{
  "quote_id": "15"
}
```

**Expected**:
```
Quote marked as favorite ⭐

"You have power over your mind..."
— Marcus Aurelius
```

**Test 6: Get Favorites**

Call `get_favorites` (no arguments).

Should list all favorited quotes.

**Test 7: Update Notes**

Call `update_quote_notes`:
```json
{
  "quote_id": "15",
  "notes": "Remember this when debugging production issues!"
}
```

**Test 8: Get Quote Explanation** (if API key set)

Call `get_quote_explanation`:
```json
{
  "quote_id": "15"
}
```

**Expected**: AI-generated explanation like:
```
"You have power over your mind - not outside events..."
— Marcus Aurelius, Meditations

In software development, this quote reminds us to focus on what we can control: our code quality, testing practices, and response to bugs - not the impossible deadline or the client's changing requirements. When production breaks at 2am, we control our troubleshooting approach and emotional response, not the initial bug. This mindset reduces stress and increases effectiveness.
```

**Test 9: Generate Quote**

Call `generate_quote`:
```json
{
  "theme": "debugging"
}
```

**Expected**: AI-generated Stoic-style quote about debugging:
```
Generated quote on "debugging":

"The bug does not upset you, but your judgment about the bug. Remove the judgment, and the path to the fix becomes clear."

Would you like to add this to your collection? Use add_quote if so.
```

### Bulk Import Demo (5 minutes)

**Show import file format**:
```bash
cat quotes-source/sample-import.txt
```

**Expected format**:
```
"Quote text here" - Author Name, Source Book
"Another quote" - Different Author, Another Book
```

**Create a test import file**:
```bash
cat > quotes-source/demo-import.txt << 'EOF'
"First, say to yourself what you would be; then do what you have to do." - Epictetus, Discourses
"He who fears death will never do anything worthy of a living man." - Seneca, Letters from a Stoic
EOF
```

**Run import**:
```bash
npm run import demo-import.txt
```

**Expected output**:
```
📥 Importing quotes from quotes-source/demo-import.txt
✅ Imported: "First, say to yourself..." → Theme: action
✅ Imported: "He who fears death..." → Theme: courage
📊 Successfully imported 2 quotes
💾 Updated quotes.json
```

**Verify in Inspector**:
- Refresh or restart Inspector
- Search for "Epictetus"
- Should see newly imported quote

**Point out**:
- Themes auto-detected from keywords
- IDs auto-incremented
- Atomic file updates

### Key Takeaways (5 minutes)

**Summarize**:
1. ✅ **TypeScript** adds type safety
2. ✅ **9 tools** provide rich functionality
3. ✅ **Personal features**: favorites, notes
4. ✅ **AI features**: explain + generate
5. ✅ **Bulk import** scales data entry
6. ✅ **Theme detection** automates categorization

**Stop Inspector**: Ctrl+C

---

## Part 3: Client Configuration (30 minutes)

### Introduction (5 minutes)

**Talking Points**:
> "Now let's configure these MCP servers in real AI clients: Claude Desktop and VS Code with GitHub Copilot. This is where MCP truly shines - persistent context across your actual workflows."

### Claude Desktop Configuration (15 minutes)

#### Find Config File

**Windows**:
```bash
code %APPDATA%\Claude\claude_desktop_config.json
```

**macOS**:
```bash
code ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

**Linux**:
```bash
code ~/.config/Claude/claude_desktop_config.json
```

#### Configure Both MCP Servers

**Show the complete config**:

```json
{
  "mcpServers": {
    "coretext": {
      "command": "node",
      "args": [
        "C:\\github\\context-engineering-2\\coretext-mcp\\src\\index.js"
      ],
      "env": {
        "DEEPSEEK_API_KEY": "sk-xxxxxxxxxxxxx"
      }
    },
    "stoic": {
      "command": "node",
      "args": [
        "C:\\github\\context-engineering-2\\stoic-mcp\\local\\dist\\index.js"
      ],
      "env": {
        "DEEPSEEK_API_KEY": "sk-xxxxxxxxxxxxx"
      }
    }
  }
}
```

**Important points**:
- **Absolute paths** required (not relative)
- **Double backslashes** on Windows: `C:\\path\\to\\file`
- Forward slashes on Mac/Linux: `/Users/tim/path/to/file`
- **CoreText**: Points to `src/index.js` (JavaScript)
- **Stoic**: Points to `dist/index.js` (compiled TypeScript)
- **API key**: Optional, both servers work without it (fallback mode)

#### Test in Claude Desktop

**Close Claude Desktop completely** (important for config reload):
```bash
# Windows
taskkill /IM "Claude.exe" /F

# macOS
killall Claude

# Linux
pkill -f claude
```

**Restart Claude Desktop**.

**Verify MCP servers loaded**:
- Look for MCP icon (or indicator) in Claude UI
- Should show 2 servers connected
- Tools available: 17 total (8 CoreText + 9 Stoic)

#### Demo in Claude Desktop

**Test CoreText MCP**:

Type in Claude:
```
Create a semantic memory: "MCP revolutionizes AI context management"
```

Claude should:
1. Recognize it needs to create a memory
2. Call `memory_create` tool automatically
3. Show the created memory with UUID and metadata

**Test memory retrieval**:
```
What memories do we have about MCP?
```

Claude should:
1. Call `memory_search` with query "MCP"
2. Return matching memories
3. Demonstrate context persistence

**Test Stoic MCP**:

Type in Claude:
```
Give me a Stoic quote about courage
```

Claude should:
1. Call `search_quotes` with theme "courage"
2. Return a relevant quote
3. Show author and source

**Test AI explanation**:
```
Explain quote ID 15 in a developer context
```

Claude should:
1. Call `get_quote_explanation` tool
2. Return AI-generated explanation
3. Apply Stoic wisdom to coding challenges

**Test memory across conversations**:
1. Close Claude Desktop completely
2. Restart it
3. Ask: "What memories do you have?"
4. Claude should retrieve memories from previous session

**This demonstrates persistence!**

### VS Code Configuration (10 minutes)

#### Create MCP Config

**In workspace root**:
```bash
mkdir -p .vscode
code .vscode/mcp.json
```

**Add configuration**:
```json
{
  "mcpServers": {
    "coretext": {
      "command": "node",
      "args": [
        "${workspaceFolder}/coretext-mcp/src/index.js"
      ],
      "env": {
        "DEEPSEEK_API_KEY": "sk-xxxxxxxxxxxxx"
      }
    },
    "stoic": {
      "command": "node",
      "args": [
        "${workspaceFolder}/stoic-mcp/local/dist/index.js"
      ],
      "env": {
        "DEEPSEEK_API_KEY": "sk-xxxxxxxxxxxxx"
      }
    }
  }
}
```

**Note**:
- Use `${workspaceFolder}` variable (resolves to absolute path)
- Same structure as Claude Desktop config
- File must be named `mcp.json` in `.vscode/` directory

#### Test in VS Code Copilot

**Prerequisites**:
- GitHub Copilot extension installed
- MCP support enabled (may require VS Code Insiders or specific version)

**Open VS Code terminal** and test:

```
@coretext create a memory about TypeScript
```

(Syntax may vary depending on Copilot MCP integration version)

**Expected**: Copilot invokes CoreText MCP to create memory.

### Key Takeaways (5 minutes)

**Summarize**:
1. ✅ **Config file** location varies by platform
2. ✅ **Absolute paths** required (or workspace variables)
3. ✅ **Environment variables** pass secrets securely
4. ✅ **Restart required** after config changes
5. ✅ **Multiple servers** can coexist
6. ✅ **Context persists** across sessions (THE BIG WIN!)

---

## Part 4: Azure Deployment Walkthrough (60 minutes)

### Introduction (5 minutes)

**Talking Points**:
> "Now let's take Stoic MCP to production on Azure. We'll deploy it as a serverless container with Cosmos DB storage, scaling from 0-3 replicas automatically. This demonstrates the full local-to-cloud journey."

**Show Architecture Diagram**:
```bash
code diagrams/stoic-mcp-azure.md
```

Point out:
- Container Apps (serverless)
- Cosmos DB Free Tier (1000 RU/s, 25GB)
- Key Vault for secrets
- Managed Identity for security
- Scale-to-zero for cost savings
- Estimated cost: $3-10/month

### Prerequisites Check (5 minutes)

```bash
# Terminal 3: Azure CLI commands

# Verify authenticated
az account show

# Show subscription
az account list --output table

# Set subscription (if needed)
az account set --subscription "Your Subscription Name"

# Verify location availability
az account list-locations --query "[?name=='eastus']" --output table
```

### Step 1: Create Resource Group (5 minutes)

```bash
# Create resource group for demo
az group create \
  --name stoic-rg-demo \
  --location eastus \
  --tags \
    purpose=demo \
    course=context-engineering \
    instructor=timwarner

# Verify creation
az group show --name stoic-rg-demo --output table
```

**Explain**:
- Resource group = logical container
- Location = data residency
- Tags = cost tracking and organization

### Step 2: Create Managed Identity (5 minutes)

```bash
# Create user-assigned managed identity
az identity create \
  --name stoic-msi-demo \
  --resource-group stoic-rg-demo \
  --location eastus

# Get principal ID (needed for RBAC)
MSI_PRINCIPAL_ID=$(az identity show \
  --name stoic-msi-demo \
  --resource-group stoic-rg-demo \
  --query principalId \
  --output tsv)

echo "Managed Identity Principal ID: $MSI_PRINCIPAL_ID"

# Get client ID (needed for container app)
MSI_CLIENT_ID=$(az identity show \
  --name stoic-msi-demo \
  --resource-group stoic-rg-demo \
  --query clientId \
  --output tsv)

echo "Managed Identity Client ID: $MSI_CLIENT_ID"
```

**Explain**:
- Managed Identity = Azure AD identity for services
- No passwords or keys in code
- Used for Key Vault and Cosmos DB access

### Step 3: Build and Push Docker Image (10 minutes)

#### Show Dockerfile

```bash
cd stoic-mcp
code Dockerfile
```

**Walk through the multi-stage build**:

```dockerfile
# Stage 1: Build TypeScript
FROM node:20-alpine AS builder
WORKDIR /app
COPY local/package*.json ./
COPY local/tsconfig.json ./
COPY local/src ./src
RUN npm ci
RUN npm run build

# Stage 2: Production
FROM node:20-alpine
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
COPY local/package*.json ./
EXPOSE 3000
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s \
  CMD node -e "require('http').get('http://localhost:3000/health',(r)=>{process.exit(r.statusCode===200?0:1);})"
CMD ["node", "dist/index.js"]
```

**Point out**:
- Stage 1: Build environment (includes TypeScript compiler)
- Stage 2: Production (minimal, only runtime dependencies)
- Smaller final image (~150MB vs ~500MB)
- Health check for Container Apps probes

#### Build Image Locally

```bash
# Build the image
docker build -t stoic-mcp:demo -f Dockerfile .

# Test locally first (optional)
docker run -p 3000:3000 \
  -e DEEPSEEK_API_KEY=$DEEPSEEK_API_KEY \
  -e PORT=3000 \
  stoic-mcp:demo

# Test health endpoint in another terminal
curl http://localhost:3000/health

# Stop the test container
docker stop $(docker ps -q --filter ancestor=stoic-mcp:demo)
```

#### Push to Azure Container Registry (ACR)

**Option A: Use ACR** (recommended for production)

```bash
# Create ACR
az acr create \
  --name timwarneracr \
  --resource-group stoic-rg-demo \
  --sku Basic \
  --admin-enabled true

# Login to ACR
az acr login --name timwarneracr

# Tag image
docker tag stoic-mcp:demo timwarneracr.azurecr.io/stoic-mcp:v1

# Push image
docker push timwarneracr.azurecr.io/stoic-mcp:v1

# Verify
az acr repository list --name timwarneracr --output table
```

**Option B: Use Docker Hub** (simpler for demo)

```bash
# Tag for Docker Hub
docker tag stoic-mcp:demo yourusername/stoic-mcp:v1

# Login to Docker Hub
docker login

# Push
docker push yourusername/stoic-mcp:v1
```

### Step 4: Deploy Infrastructure with Bicep (15 minutes)

#### Show Bicep Template

```bash
code azure/main.bicep
```

**Walk through key sections**:

**1. Parameters** (lines 17-31):
```bicep
@description('DeepSeek API Key for AI explanations')
@secure()
param deepseekApiKey string

@description('Managed Identity Name')
param managedIdentityName string = 'stoic-msi-demo'
```

**2. Cosmos DB** (lines 70-167):
```bicep
resource cosmosAccount 'Microsoft.DocumentDB/databaseAccounts@2023-11-15' = {
  name: cosmosAccountName
  location: location
  properties: {
    enableFreeTier: true  // FREE TIER!
    databaseAccountOfferType: 'Standard'
  }
}

// Database: stoic
resource cosmosDatabase 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases@2023-11-15' = {
  parent: cosmosAccount
  name: 'stoic'
  properties: {
    options: {
      throughput: 400  // Minimum for free tier
    }
  }
}

// Container 1: quotes
resource cosmosContainer 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers@2023-11-15' = {
  parent: cosmosDatabase
  name: 'quotes'
  properties: {
    resource: {
      partitionKey: {
        paths: ['/id']
      }
    }
  }
}

// Container 2: metadata
resource cosmosMetadataContainer '...' = {
  // ...
}
```

**3. Key Vault** (lines 173-228):
```bicep
resource keyVault 'Microsoft.KeyVault/vaults@2023-07-01' = {
  properties: {
    enableRbacAuthorization: true  // Use RBAC instead of access policies
    softDeleteRetentionInDays: 7
  }
}

// Store DeepSeek API key
resource deepseekSecret 'Microsoft.KeyVault/vaults/secrets@2023-07-01' = {
  parent: keyVault
  name: 'deepseek-api-key'
  properties: {
    value: deepseekApiKey
  }
}

// RBAC: Grant MSI access to secrets
resource keyVaultRoleAssignment '...' = {
  properties: {
    roleDefinitionId: '<Key Vault Secrets User role>'
    principalId: managedIdentity.properties.principalId
  }
}
```

**4. Container App** (lines 252-363):
```bicep
resource containerApp 'Microsoft.App/containerApps@2023-05-01' = {
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${managedIdentity.id}': {}
    }
  }
  properties: {
    configuration: {
      ingress: {
        external: true
        targetPort: 3000
      }
      secrets: [
        {
          name: 'deepseek-api-key'
          keyVaultUrl: deepseekSecret.properties.secretUri
          identity: managedIdentity.id
        }
      ]
    }
    template: {
      containers: [{
        name: 'stoic-mcp'
        image: containerImage
        resources: {
          cpu: json('0.25')    // Minimal for cost
          memory: '0.5Gi'
        }
        env: [
          {
            name: 'DEEPSEEK_API_KEY'
            secretRef: 'deepseek-api-key'  // From Key Vault
          }
        ]
      }]
      scale: {
        minReplicas: 0  // Scale to zero!
        maxReplicas: 3
      }
    }
  }
}
```

#### Deploy the Bicep Template

```bash
# Create parameters file
cat > azure/parameters.json << EOF
{
  "\$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentParameters.json#",
  "contentVersion": "1.0.0.0",
  "parameters": {
    "managedIdentityName": {
      "value": "stoic-msi-demo"
    },
    "containerImage": {
      "value": "timwarneracr.azurecr.io/stoic-mcp:v1"
    },
    "deepseekApiKey": {
      "value": "$DEEPSEEK_API_KEY"
    }
  }
}
EOF

# Deploy (takes 5-10 minutes)
az deployment group create \
  --resource-group stoic-rg-demo \
  --template-file azure/main.bicep \
  --parameters azure/parameters.json \
  --verbose

# Watch deployment progress
az deployment group list \
  --resource-group stoic-rg-demo \
  --output table
```

**While deployment runs**, show in Azure Portal:
1. Navigate to resource group `stoic-rg-demo`
2. Watch resources appear:
   - Log Analytics Workspace (first)
   - Cosmos DB account
   - Key Vault
   - Container Apps environment
   - Container App (last)

#### Verify Deployment

```bash
# Get Container App URL
STOIC_URL=$(az containerapp show \
  --name stoic-app-* \
  --resource-group stoic-rg-demo \
  --query properties.configuration.ingress.fqdn \
  --output tsv)

echo "Stoic MCP URL: https://$STOIC_URL"

# Test health endpoint
curl https://$STOIC_URL/health

# Expected response:
# {
#   "status": "healthy",
#   "timestamp": "2025-10-30T...",
#   "quoteCount": 0,
#   "cosmosConnected": true
# }
```

### Step 5: Migrate Data to Cosmos DB (5 minutes)

**Show migration script**:

```bash
code stoic-mcp/azure/migrate-data.js
```

**Script content** (create if doesn't exist):

```javascript
import { CosmosClient } from '@azure/cosmos';
import fs from 'fs/promises';

async function migrate() {
  // Read local quotes
  const localData = JSON.parse(
    await fs.readFile('local/quotes.json', 'utf-8')
  );

  // Connect to Cosmos DB
  const client = new CosmosClient(process.env.COSMOS_CONNECTION_STRING);
  const database = client.database('stoic');
  const quotesContainer = database.container('quotes');
  const metadataContainer = database.container('metadata');

  // Migrate quotes
  console.log(`Migrating ${localData.quotes.length} quotes...`);
  for (const quote of localData.quotes) {
    await quotesContainer.items.create({
      id: quote.id.toString(),  // Cosmos needs string IDs
      ...quote
    });
    console.log(`✅ Migrated quote ${quote.id}`);
  }

  // Create metadata document
  await metadataContainer.items.create({
    id: 'stats',
    type: 'global',
    lastId: localData.metadata.lastId,
    version: localData.metadata.version,
    totalQuotes: localData.quotes.length,
    totalFavorites: localData.quotes.filter(q => q.favorite).length,
    lastModified: new Date().toISOString()
  });

  console.log('✅ Migration complete!');
}

migrate().catch(console.error);
```

**Get Cosmos DB connection string**:

```bash
COSMOS_CONN=$(az cosmosdb keys list \
  --name stoic-cosmos-* \
  --resource-group stoic-rg-demo \
  --type connection-strings \
  --query "connectionStrings[0].connectionString" \
  --output tsv)

echo $COSMOS_CONN
```

**Run migration**:

```bash
cd stoic-mcp/azure
npm install @azure/cosmos

COSMOS_CONNECTION_STRING="$COSMOS_CONN" node migrate-data.js
```

**Expected output**:
```
Migrating 42 quotes...
✅ Migrated quote 1
✅ Migrated quote 2
...
✅ Migrated quote 42
✅ Migration complete!
```

**Verify in Azure Portal**:
1. Navigate to Cosmos DB account
2. Open Data Explorer
3. Expand `stoic` database → `quotes` container
4. See all quotes with IDs

### Step 6: Configure Client to Use Azure Endpoint (5 minutes)

**Update Claude Desktop config**:

```json
{
  "mcpServers": {
    "stoic-azure": {
      "command": "node",
      "args": [
        "-e",
        "require('https').get('https://stoic-app-xxxxx.azurecontainerapps.io')"
      ]
    }
  }
}
```

**Or use HTTP transport** (if MCP server updated to support):

```json
{
  "mcpServers": {
    "stoic-azure": {
      "url": "https://stoic-app-xxxxx.azurecontainerapps.io"
    }
  }
}
```

**Note**: Current MCP servers use stdio transport. For production HTTP endpoints, server code needs HTTP transport adapter.

### Step 7: Monitor in Azure Portal (5 minutes)

#### View Logs

**In Azure Portal**:
1. Navigate to Container App
2. Click "Log stream" blade
3. See real-time logs

**Via CLI**:
```bash
# Follow logs
az containerapp logs show \
  --name stoic-app-* \
  --resource-group stoic-rg-demo \
  --follow

# View recent logs
az containerapp logs show \
  --name stoic-app-* \
  --resource-group stoic-rg-demo \
  --tail 50
```

#### Query Log Analytics

```bash
# Get Log Analytics workspace ID
LA_WORKSPACE_ID=$(az monitor log-analytics workspace show \
  --resource-group stoic-rg-demo \
  --workspace-name stoic-logs-* \
  --query customerId \
  --output tsv)

echo "Log Analytics Workspace: $LA_WORKSPACE_ID"
```

**In Azure Portal**:
1. Navigate to Log Analytics workspace
2. Click "Logs" blade
3. Run KQL query:

```kql
ContainerAppConsoleLogs_CL
| where ContainerAppName_s contains "stoic"
| project TimeGenerated, Log_s
| order by TimeGenerated desc
| take 100
```

#### View Metrics

**In Azure Portal**:
1. Navigate to Container App
2. Click "Metrics" blade
3. Add metrics:
   - Requests (count)
   - CPU Usage (%)
   - Memory Working Set (bytes)
   - Replica Count

**Show scaling behavior**:
- Initial state: 0 replicas (scaled to zero)
- After first request: 1 replica (cold start)
- Under load: scales up to 3 replicas
- After idle period: scales back to 0

### Step 8: Cost Analysis (5 minutes)

**Show cost breakdown**:

```bash
# Enable cost analysis (may take 24-48 hours for data)
az consumption budget create \
  --resource-group stoic-rg-demo \
  --budget-name stoic-monthly-budget \
  --amount 20 \
  --time-grain Monthly \
  --start-date 2025-11-01

# View current costs (portal only, no CLI for real-time costs)
```

**In Azure Portal**:
1. Navigate to resource group
2. Click "Cost analysis" blade
3. View breakdown by service:
   - Container Apps: ~$1-5/month
   - Cosmos DB Free Tier: $0
   - Key Vault: ~$0.03/month
   - Log Analytics: ~$2-5/month

**Total estimated**: $3-10/month (as shown in diagram)

### Key Takeaways (5 minutes)

**Summarize the deployment**:

1. ✅ **Containerization**: Multi-stage Docker build for efficiency
2. ✅ **Infrastructure as Code**: Bicep template for repeatability
3. ✅ **Security**: Managed Identity + Key Vault (no hardcoded secrets)
4. ✅ **Scalability**: Auto-scale 0-3 replicas based on load
5. ✅ **Cost optimization**: Free Tier + scale-to-zero = ~$3-10/month
6. ✅ **Monitoring**: Log Analytics + metrics for observability
7. ✅ **Data migration**: Local JSON → Cosmos DB

**Compare local vs Azure**:

| Feature | Local | Azure |
|---------|-------|-------|
| Storage | JSON file (100MB limit) | Cosmos DB (unlimited) |
| Scaling | Single process | 0-3 replicas |
| Availability | Dev machine only | 99.95% SLA |
| Cost | $0 | $3-10/month |
| Security | .env file | Key Vault + RBAC |
| Monitoring | Console logs | Log Analytics |

---

## Troubleshooting Guide

### Common Issues

#### Issue 1: MCP Inspector Won't Start

**Symptoms**:
```
Error: Port 5173 already in use
```

**Solution**:
```bash
# Find and kill process using port 5173
lsof -ti:5173 | xargs kill -9

# Or use different port
npx @modelcontextprotocol/inspector --port 5174 node dist/index.js
```

#### Issue 2: TypeScript Compilation Errors

**Symptoms**:
```
error TS2304: Cannot find name 'process'
```

**Solution**:
```bash
# Install Node.js type definitions
npm install --save-dev @types/node

# Rebuild
npm run build
```

#### Issue 3: Claude Desktop Doesn't Load MCP Servers

**Symptoms**:
- No MCP indicator in UI
- Tools not available

**Solutions**:

1. **Verify config file location**:
   ```bash
   # Windows
   dir %APPDATA%\Claude\claude_desktop_config.json

   # macOS
   ls ~/Library/Application\ Support/Claude/claude_desktop_config.json
   ```

2. **Validate JSON syntax**:
   ```bash
   # Use jq to check JSON
   jq . %APPDATA%\Claude\claude_desktop_config.json
   ```

3. **Check absolute paths**:
   - Must be absolute, not relative
   - Windows: Use double backslashes `C:\\path\\to\\file`
   - Mac/Linux: Use forward slashes `/path/to/file`

4. **Verify file exists**:
   ```bash
   node C:\path\to\server\index.js
   # Should start server without errors
   ```

5. **Check Claude Desktop logs**:
   - Windows: `%APPDATA%\Claude\logs\`
   - macOS: `~/Library/Logs/Claude/`

#### Issue 4: Azure Deployment Fails

**Symptoms**:
```
ERROR: Cosmos DB free tier already exists in subscription
```

**Solution**:
- Only ONE Cosmos DB free tier per subscription
- Either use existing free tier account
- Or remove free tier from template:

```bicep
properties: {
  enableFreeTier: false  // Change to false
  // ... rest of config
}
```

#### Issue 5: Container App Won't Start

**Symptoms**:
- Container App shows "Provisioning" forever
- Health checks failing

**Solutions**:

1. **Check container logs**:
   ```bash
   az containerapp logs show \
     --name stoic-app-* \
     --resource-group stoic-rg-demo \
     --tail 100
   ```

2. **Verify image pulled successfully**:
   - Check ACR logs
   - Verify image tag exists

3. **Test image locally**:
   ```bash
   docker run -p 3000:3000 timwarneracr.azurecr.io/stoic-mcp:v1
   curl http://localhost:3000/health
   ```

4. **Check environment variables**:
   ```bash
   az containerapp show \
     --name stoic-app-* \
     --resource-group stoic-rg-demo \
     --query properties.template.containers[0].env
   ```

#### Issue 6: Managed Identity Can't Access Key Vault

**Symptoms**:
```
ERROR: Access denied to Key Vault
```

**Solution**:

```bash
# Verify role assignment exists
az role assignment list \
  --assignee $MSI_PRINCIPAL_ID \
  --scope /subscriptions/.../resourceGroups/stoic-rg-demo/providers/Microsoft.KeyVault/vaults/stoic-kv-*

# If missing, create it
az role assignment create \
  --role "Key Vault Secrets User" \
  --assignee $MSI_PRINCIPAL_ID \
  --scope /subscriptions/.../resourceGroups/stoic-rg-demo/providers/Microsoft.KeyVault/vaults/stoic-kv-*
```

---

## Q&A Prompts

### Anticipated Questions

**Q: "Can I use this with ChatGPT?"**

A: Currently, Claude Desktop and VS Code have native MCP support. ChatGPT doesn't yet support MCP directly, but you can:
- Expose MCP server as REST API
- Use Custom GPT with Actions pointing to your API
- Wait for OpenAI to add MCP support

**Q: "What if I don't have a DeepSeek API key?"**

A: Both servers work without API keys:
- CoreText: Falls back to local keyword extraction
- Stoic: Returns error message for AI features
- All non-AI features work normally
- You can get a free DeepSeek key at https://platform.deepseek.com

**Q: "How do I add my own MCP tools?"**

A: Three steps:
1. Add tool definition to `ListToolsRequestSchema` handler
2. Add case to `CallToolRequestSchema` switch statement
3. Implement your logic, return formatted response

**Q: "Can I deploy CoreText MCP to Azure too?"**

A: Yes! Use the same Bicep template pattern:
- Copy `stoic-mcp/azure/` to `coretext-mcp/azure/`
- Update resource names (stoic → coretext)
- Adjust Cosmos DB container names
- Follow same deployment process

**Q: "What's the difference between tools and resources?"**

A:
- **Tools**: AI explicitly calls them (active, on-demand)
- **Resources**: Always available context (passive, background)
- Use tools for operations (create, update, delete)
- Use resources for persistent context (dashboards, streams)

**Q: "How much does Azure really cost?"**

A: For this demo architecture:
- Cosmos DB Free Tier: $0 (1000 RU/s, 25GB)
- Container Apps: $1-5/month (scale-to-zero)
- Key Vault: $0.03/month (first 10k ops free)
- Log Analytics: $2-5/month (first 5GB free)
- **Total: $3-10/month** for low-traffic workloads

Scale-to-zero means you only pay when container is running!

**Q: "Can I use PostgreSQL instead of Cosmos DB?"**

A: Yes! Replace Cosmos DB calls with PostgreSQL:
- Azure Database for PostgreSQL has free tier
- Change MemoryManager/QuoteStorage to use `pg` library
- Update connection strings in Key Vault
- Adjust Bicep template

**Q: "What about security in production?"**

A: Add these for production:
- API authentication (OAuth 2.0, API keys)
- Rate limiting (10 requests/second per client)
- Network isolation (VNET integration)
- Azure Front Door with WAF
- Audit logging to Log Analytics
- Regular key rotation in Key Vault

**Q: "How do I debug MCP servers?"**

A: Multiple options:
1. **MCP Inspector**: Visual tool, best for development
2. **Console logs**: stderr output (use console.error)
3. **VS Code debugger**: Attach to Node process
4. **Test client**: Write automated tests (see test-client.js)
5. **Claude Desktop logs**: Check client-side issues

**Q: "Can I use Python instead of JavaScript/TypeScript?"**

A: Yes! MCP has Python SDK:
```bash
pip install mcp-sdk
```

Same concepts apply:
- Define tools and resources
- Handle requests with callbacks
- Use stdio transport
- See: https://github.com/modelcontextprotocol/python-sdk

---

## Post-Demo Cleanup

### Remove Azure Resources

**Delete entire resource group** (easiest):
```bash
az group delete \
  --name stoic-rg-demo \
  --yes \
  --no-wait
```

**Or delete resources individually** (if sharing resource group):
```bash
# Delete Container App
az containerapp delete --name stoic-app-* --resource-group stoic-rg-demo --yes

# Delete Cosmos DB
az cosmosdb delete --name stoic-cosmos-* --resource-group stoic-rg-demo --yes

# Delete Key Vault (with purge protection)
az keyvault delete --name stoic-kv-* --resource-group stoic-rg-demo
az keyvault purge --name stoic-kv-* --no-wait

# Delete Log Analytics
az monitor log-analytics workspace delete --workspace-name stoic-logs-* --resource-group stoic-rg-demo --yes

# Delete Container Apps Environment
az containerapp env delete --name stoic-env-* --resource-group stoic-rg-demo --yes
```

### Reset Local Environments

**CoreText MCP**:
```bash
cd coretext-mcp
rm -f data/memory.json
npm start  # Will recreate demo memories
```

**Stoic MCP**:
```bash
cd stoic-mcp/local

# Backup current quotes
cp quotes.json quotes-backup.json

# Reset to seed data (if you have seed file)
cp quotes-seed.json quotes.json

# Or clear and reimport
echo '{"metadata":{"lastId":0,"version":"1.0.0","lastModified":""},"quotes":[]}' > quotes.json
npm run import sample-import.txt
```

---

## Demo Script Checklist

### Before Demo

- [ ] All terminals open and positioned
- [ ] Environment variables set (`$DEEPSEEK_API_KEY`)
- [ ] Azure CLI authenticated (`az account show`)
- [ ] Git repos clean (`git status`)
- [ ] CoreText MCP: `data/memory.json` exists or will auto-create
- [ ] Stoic MCP: TypeScript compiled (`npm run build`)
- [ ] Claude Desktop config backed up
- [ ] Browser tabs open (MCP spec, Azure Portal, diagrams)
- [ ] Screen sharing tested
- [ ] Backup plan if network fails

### During Demo

- [ ] Part 1: CoreText code walkthrough (15 min)
- [ ] Part 1: MCP Inspector demo (25 min)
- [ ] Part 2: Stoic code walkthrough (20 min)
- [ ] Part 2: MCP Inspector demo (20 min)
- [ ] Part 3: Claude Desktop config (15 min)
- [ ] Part 3: VS Code config (10 min)
- [ ] Part 4: Azure deployment (40 min)
- [ ] Part 4: Monitoring and cost (10 min)

### After Demo

- [ ] Show diagrams for reference
- [ ] Share GitHub repo link
- [ ] Share DEMO_SCRIPT.md link
- [ ] Q&A session
- [ ] Cleanup Azure resources (optional, can leave for students)

---

## Additional Resources

### Documentation Links

- MCP Specification: https://spec.modelcontextprotocol.io/
- MCP TypeScript SDK: https://github.com/modelcontextprotocol/typescript-sdk
- MCP Inspector: https://github.com/modelcontextprotocol/inspector
- Azure Container Apps: https://learn.microsoft.com/azure/container-apps/
- Azure Cosmos DB: https://learn.microsoft.com/azure/cosmos-db/
- Bicep: https://learn.microsoft.com/azure/azure-resource-manager/bicep/

### Course Materials

- Main README: [../README.md](README.md)
- Architecture Diagrams: [diagrams/](diagrams/)
- CoreText MCP: [coretext-mcp/](coretext-mcp/)
- Stoic MCP: [stoic-mcp/](stoic-mcp/)

### Contact

- **Instructor**: Tim Warner
- **Website**: https://techtrainertim.com
- **GitHub**: https://github.com/timothywarner-org
- **Course**: O'Reilly Live Training - Context Engineering with MCP

---

**Demo Script Version**: 1.0
**Last Updated**: October 30, 2025
**Total Duration**: ~3-4 hours (including Q&A)

**Good luck with the demo! 🚀**
