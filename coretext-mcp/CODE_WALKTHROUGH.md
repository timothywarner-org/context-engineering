# CoreText MCP Server: Code Walkthrough

**A beginner-friendly guide to understanding how this persistent memory system works.**

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

This MCP server demonstrates **five key concepts**:

1. **Persistent Memory** - Data that survives server restarts
2. **CRUD Operations** - Create, Read, Update, Delete memories
3. **AI Enrichment** - DeepSeek API integration for semantic analysis
4. **Resources** - Dynamic context that AI can access
5. **Memory Types** - Episodic (events) vs Semantic (facts)

**What it does**: Solves "AI Amnesia" by giving Claude persistent memory across sessions.

---

## File Structure

```
coretext-mcp/
├── src/
│   ├── index.js         # Main server (830+ lines)
│   └── test-client.js   # Automated test suite
├── data/
│   └── memory.json      # Persistent storage
├── scripts/
│   ├── demo-reset.js    # Reset demo data
│   ├── demo-populate.js # Add sample memories
│   └── demo-segment*.js # Teaching demos
├── package.json         # Dependencies
└── .env                 # API keys (gitignored)
```

**Key difference from Stoic MCP**: Everything in one file (index.js) for easier teaching!

---

## Core Concepts

### 1. Memory Types: Episodic vs Semantic

**Teaching Point**: Human memory works this way!

```javascript
class MemoryEntry {
  constructor(content, type = 'semantic', metadata = {}) {
    this.id = uuidv4();           // Unique ID
    this.content = content;        // The actual memory
    this.type = type;              // 'episodic' or 'semantic'
    this.metadata = {
      created: new Date().toISOString(),
      updated: new Date().toISOString(),
      accessCount: 0,              // How often accessed
      enriched: false,             // Has AI analysis?
      lastAccessed: null
    };
    this.tags = metadata.tags || [];
    this.enrichment = null;        // DeepSeek analysis
  }
}
```

**Examples**:

- **Semantic**: "MCP enables persistent AI memory" (fact/knowledge)
- **Episodic**: "Training session on Oct 31, 2024 at 11am" (event/timeline)

### 2. The Three Components of MCP

Every MCP server has three parts:

```javascript
const server = new Server(
  { name: 'coretext-mcp', version: '1.0.0' },
  {
    capabilities: {
      resources: {},    // Information AI can access
      tools: {}         // Actions AI can perform
    }
  }
);
```

**Tools** = Actions (create memory, search, delete)
**Resources** = Context (overview, knowledge graph, recent activity)

### 3. Stdio Transport

```javascript
const transport = new StdioServerTransport();
await server.connect(transport);
```

**What this means**: Server runs as child process, talks via stdin/stdout.

---

## Code Deep Dive

### 📁 MemoryManager Class - Data Layer

**Purpose**: Handle all CRUD operations and persistence.

#### Initialization

```javascript
async initialize() {
  // Create data directory if needed
  await fs.mkdir(path.dirname(DATA_PATH), { recursive: true });

  try {
    // Try to load existing memories from disk
    const data = await fs.readFile(DATA_PATH, 'utf-8');
    const parsed = JSON.parse(data);

    // Populate in-memory Map
    for (const [id, memory] of Object.entries(parsed)) {
      this.memories.set(id, memory);
    }

    console.error(`📚 Loaded ${this.memories.size} memories from disk`);
  } catch {
    // First run - create demo memories for teaching
    console.error('📝 Starting with empty memory store');
    await this.createDemoMemories();
  }
}
```

**Key pattern**: Graceful first-run experience. If no file exists, create demo data.

#### Creating Memories

```javascript
async create(content, type = 'semantic', metadata = {}) {
  const entry = new MemoryEntry(content, type, metadata);

  // Store in memory (Map for fast lookups)
  this.memories.set(entry.id, entry);

  // Persist to disk
  await this.persist();

  console.error(`💾 Created ${type} memory: ${entry.id}`);
  return entry;
}
```

**Why Map?** Fast O(1) lookups by ID. Alternative would be array with O(n) searches.

#### Persistence Strategy

```javascript
async persist() {
  // Convert Map to plain object for JSON
  const data = Object.fromEntries(this.memories);

  // Write to disk with pretty-printing
  await fs.writeFile(DATA_PATH, JSON.stringify(data, null, 2));
}
```

**Trade-off**: Simple but writes entire file on every change. Production would use a database.

#### Search Implementation

```javascript
async search(query) {
  const results = [];

  for (const memory of this.memories.values()) {
    // Case-insensitive search in content AND tags
    if (memory.content.toLowerCase().includes(query.toLowerCase()) ||
        memory.tags.some(tag => tag.toLowerCase().includes(query.toLowerCase()))) {
      results.push(memory);
    }
  }

  return results;
}
```

**Pattern**: Linear scan through all memories. Fine for demo, needs indexing at scale.

#### Access Tracking

```javascript
async read(id) {
  const memory = this.memories.get(id);

  if (memory) {
    // Track access patterns
    memory.metadata.accessCount++;
    memory.metadata.lastAccessed = new Date().toISOString();
    await this.persist();
  }

  return memory;
}
```

**Teaching point**: Metadata helps understand usage patterns!

---

### 📁 DeepseekEnrichmentService Class - AI Integration

**Purpose**: Add semantic analysis to memories using DeepSeek API.

#### Constructor with Fallback

```javascript
constructor() {
  // Check multiple environment variables
  this.apiKey = process.env.DEEPSEEK_API_KEY ||
                process.env.DEEPSEEK_KEY ||
                null;

  if (this.apiKey) {
    console.error(`🔑 Deepseek API configured`);
  } else {
    console.error('⚠️  No API key - using fallback mode');
  }
}
```

**Best practice**: Graceful degradation. Server works without API, just with reduced features.

#### Enrichment Workflow

```javascript
async enrich(memory) {
  // Guard clause - check for API key
  if (!this.apiKey) {
    return this.fallbackEnrich(memory);
  }

  const enrichmentPrompt = `Analyze this memory and provide:
1. A concise summary (max 50 words)
2. Top 5 keywords
3. Sentiment (positive/neutral/negative)
4. Category (technical/communication/education/business/personal)
5. Suggested related topics (2-3)

Memory: "${memory.content}"

Respond with valid JSON only, no markdown.`;

  const requestBody = JSON.stringify({
    model: 'deepseek-chat',
    messages: [
      {
        role: "system",
        content: "You are a memory enrichment system..."
      },
      {
        role: "user",
        content: enrichmentPrompt
      }
    ],
    temperature: 0.3,           // Low = more focused
    max_tokens: 500,
    response_format: { type: "json_object" }  // Force JSON output
  });

  const response = await this.makeAPICall(requestBody);
  const analysis = JSON.parse(response.choices[0].message.content);

  // Update memory with enrichment
  memory.metadata.enriched = true;
  memory.enrichment = analysis;

  return memory;
}
```

**Key concepts**:

- **Prompt engineering**: Specific instructions yield structured output
- **JSON mode**: Forces API to return parseable JSON
- **Low temperature**: More deterministic results

#### HTTP API Call (No External Libraries!)

```javascript
makeAPICall(requestBody) {
  return new Promise((resolve, reject) => {
    const options = {
      hostname: 'api.deepseek.com',
      path: '/v1/chat/completions',
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.apiKey}`,
        'Content-Length': Buffer.byteLength(requestBody)
      }
    };

    const req = https.request(options, (res) => {
      let data = '';

      // Accumulate chunks
      res.on('data', chunk => data += chunk);

      // Process complete response
      res.on('end', () => {
        if (res.statusCode === 200) {
          resolve(JSON.parse(data));
        } else {
          reject(new Error(`API returned ${res.statusCode}`));
        }
      });
    });

    req.on('error', reject);
    req.write(requestBody);
    req.end();
  });
}
```

**Teaching point**: Native Node.js HTTPS, no fetch or axios needed!

#### Local Fallback Enrichment

```javascript
fallbackEnrich(memory) {
  const text = memory.content.toLowerCase();

  // Simple keyword extraction
  const stopWords = new Set(['the', 'a', 'an', 'and', 'or', 'but', ...]);
  const words = text.split(/\W+/).filter(w =>
    w.length > 3 && !stopWords.has(w)
  );

  // Word frequency counting
  const wordFreq = {};
  words.forEach(w => wordFreq[w] = (wordFreq[w] || 0) + 1);

  const keywords = Object.entries(wordFreq)
    .sort((a, b) => b[1] - a[1])  // Sort by frequency
    .slice(0, 5)                   // Top 5
    .map(([word]) => word);

  // Simple sentiment analysis
  const positiveWords = ['good', 'great', 'excellent', 'success', ...];
  const negativeWords = ['bad', 'poor', 'failed', 'error', ...];

  let sentiment = 'neutral';
  const posCount = positiveWords.filter(w => text.includes(w)).length;
  const negCount = negativeWords.filter(w => text.includes(w)).length;

  if (posCount > negCount) sentiment = 'positive';
  else if (negCount > posCount) sentiment = 'negative';

  memory.enrichment = {
    keywords,
    sentiment,
    category: 'general',
    confidence: 0.7,
    method: 'local'
  };

  return memory;
}
```

**Pattern**: Rule-based NLP. Works offline, but less sophisticated than AI.

---

### 📁 CoreTextServer Class - The Main Server

**Purpose**: Wire everything together and handle MCP protocol.

#### 1. Tools Handler - Exposing Capabilities

The `ListToolsRequestSchema` handler tells AI what actions are available:

```javascript
server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [
    {
      name: 'memory_create',
      description: '📝 Create a new memory entry with optional type and metadata',
      inputSchema: {
        type: 'object',
        properties: {
          content: {
            type: 'string',
            description: 'The content to remember (fact, event, or information)'
          },
          type: {
            type: 'string',
            enum: ['episodic', 'semantic'],
            description: 'Memory type - episodic for events, semantic for facts',
            default: 'semantic'
          },
          tags: {
            type: 'array',
            items: { type: 'string' },
            description: 'Tags for categorization and search'
          },
          enrich: {
            type: 'boolean',
            description: 'Whether to enrich with AI analysis',
            default: false
          }
        },
        required: ['content']  // Only content is mandatory
      }
    },
    // ... 7 more tools
  ]
}));
```

**Critical**: Descriptions guide AI decision-making. Be specific!

#### 2. Tool Execution - The Big Switch

```javascript
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  try {
    switch (name) {
      case 'memory_create': {
        // Step 1: Create the memory
        let memory = await memoryManager.create(
          args.content,
          args.type || 'semantic',
          { tags: args.tags || [] }
        );

        // Step 2: Optionally enrich it
        if (args.enrich) {
          memory = await enrichmentService.enrich(memory);
          await memoryManager.update(memory.id, memory);
        }

        // Step 3: Return structured response
        return {
          content: [{
            type: 'text',
            text: JSON.stringify({
              success: true,
              memory: memory,
              message: `✅ Memory created with ID: ${memory.id}`
            }, null, 2)
          }]
        };
      }

      case 'memory_search': {
        const results = await memoryManager.search(args.query);
        const limited = results.slice(0, args.limit || 10);

        return {
          content: [{
            type: 'text',
            text: JSON.stringify({
              success: true,
              query: args.query,
              count: limited.length,
              total: results.length,
              memories: limited
            }, null, 2)
          }]
        };
      }

      case 'memory_stats': {
        const memories = await memoryManager.list();

        const stats = {
          total: memories.length,
          episodic: memories.filter(m => m.type === 'episodic').length,
          semantic: memories.filter(m => m.type === 'semantic').length,
          enriched: memories.filter(m => m.metadata.enriched).length,
          enrichmentRate: `${(enriched / total * 100).toFixed(1)}%`,
          tags: [...new Set(memories.flatMap(m => m.tags))],
          mostAccessed: memories
            .sort((a, b) => b.metadata.accessCount - a.metadata.accessCount)
            .slice(0, 5)
        };

        return {
          content: [{
            type: 'text',
            text: JSON.stringify({ success: true, stats }, null, 2)
          }]
        };
      }

      // ... more cases
    }
  } catch (error) {
    return {
      content: [{
        type: 'text',
        text: JSON.stringify({ success: false, error: error.message })
      }]
    };
  }
});
```

**Patterns to notice**:

- **Consistent response structure** - Always JSON with `success` flag
- **Pretty printing** - `JSON.stringify(..., null, 2)` for readability
- **Global error handler** - Catches all errors and returns valid MCP response

#### 3. Resources Handler - Dynamic Context

Resources provide information AI can read:

```javascript
server.setRequestHandler(ListResourcesRequestSchema, async () => ({
  resources: [
    {
      uri: 'memory://overview',
      name: '📊 Memory System Overview',
      description: 'Current state, statistics, and capabilities',
      mimeType: 'text/markdown'
    },
    {
      uri: 'memory://context-stream',
      name: '🌊 Active Context Stream',
      description: 'Recent memories and access patterns',
      mimeType: 'application/json'
    },
    {
      uri: 'memory://knowledge-graph',
      name: '🕸️ Knowledge Graph',
      description: 'Semantic relationships between memories',
      mimeType: 'application/json'
    }
  ]
}));
```

**Teaching point**: URIs can be custom schemes, not just HTTP!

#### 4. Resource Reader - Generating Dynamic Content

```javascript
server.setRequestHandler(ReadResourceRequestSchema, async (request) => {
  const { uri } = request.params;

  if (uri === 'memory://overview') {
    const memories = await memoryManager.list();

    // Generate markdown dynamically
    const markdown = `# 🧠 CoreText Memory System Overview

## 📊 Current Statistics
- **Total Memories**: ${memories.length}
- **Episodic**: ${memories.filter(m => m.type === 'episodic').length}
- **Semantic**: ${memories.filter(m => m.type === 'semantic').length}

## 🕐 Recent Activity
${memories
  .sort((a, b) => new Date(b.metadata.updated) - new Date(a.metadata.updated))
  .slice(0, 5)
  .map(m => `- ${new Date(m.metadata.updated).toLocaleString()}: ${m.content.substring(0, 60)}...`)
  .join('\n')}

## 💡 Teaching Examples
...
`;

    return {
      contents: [{
        uri: uri,
        mimeType: 'text/markdown',
        text: markdown
      }]
    };
  }

  if (uri === 'memory://context-stream') {
    // Group memories by recency
    const now = Date.now();
    const hour = 60 * 60 * 1000;
    const day = 24 * hour;

    const memories = await memoryManager.list();
    const sorted = memories
      .sort((a, b) =>
        new Date(b.metadata.updated) - new Date(a.metadata.updated)
      )
      .slice(0, 20);

    const grouped = {
      recent: sorted.filter(m => now - new Date(m.metadata.updated) < hour),
      today: sorted.filter(m => {
        const age = now - new Date(m.metadata.updated);
        return age >= hour && age < day;
      }),
      earlier: sorted.filter(m => now - new Date(m.metadata.updated) >= day)
    };

    return {
      contents: [{
        uri: uri,
        mimeType: 'application/json',
        text: JSON.stringify({
          timestamp: new Date().toISOString(),
          activeTopics: [...new Set(sorted.flatMap(m => m.tags))],
          recentContext: grouped.recent,
          todayContext: grouped.today.map(m => ({
            id: m.id,
            snippet: m.content.substring(0, 100),
            tags: m.tags
          })),
          statistics: {
            totalMemories: memories.length,
            inContextStream: sorted.length,
            recentlyActive: grouped.recent.length
          }
        }, null, 2)
      }]
    };
  }

  if (uri === 'memory://knowledge-graph') {
    const memories = await memoryManager.list();

    // Build graph nodes
    const nodes = memories.map(m => ({
      id: m.id,
      label: m.content.substring(0, 30) + '...',
      type: m.type,
      tags: m.tags
    }));

    // Build edges based on shared tags
    const edges = [];
    for (let i = 0; i < memories.length; i++) {
      for (let j = i + 1; j < memories.length; j++) {
        const sharedTags = memories[i].tags.filter(t =>
          memories[j].tags.includes(t)
        );

        if (sharedTags.length > 0) {
          edges.push({
            source: memories[i].id,
            target: memories[j].id,
            weight: sharedTags.length,
            sharedTags
          });
        }
      }
    }

    return {
      contents: [{
        uri: uri,
        mimeType: 'application/json',
        text: JSON.stringify({
          metadata: {
            totalNodes: nodes.length,
            totalEdges: edges.length,
            graphDensity: nodes.length > 1 ?
              (2 * edges.length / (nodes.length * (nodes.length - 1))).toFixed(3) : '0'
          },
          nodes,
          edges: edges.sort((a, b) => b.weight - a.weight),
          insights: {
            strongestConnections: edges.slice(0, 5)
          }
        }, null, 2)
      }]
    };
  }

  throw new Error(`Resource not found: ${uri}`);
});
```

**Key concepts**:

- **Dynamic generation** - Content created on-the-fly from current state
- **Different formats** - Markdown for humans, JSON for programmatic access
- **Graph algorithms** - Finding relationships between memories

---

## How It All Works Together

### Request Flow Diagram

```
┌─────────────┐
│   Claude    │
│             │
└──────┬──────┘
       │ 1. User: "Remember that our client prefers email"
       ▼
┌─────────────────────┐
│  MCP Client         │
│  (in Claude)        │
└──────┬──────────────┘
       │ 2. call_tool("memory_create", {
       │      content: "Client prefers email",
       │      type: "semantic",
       │      tags: ["client", "communication"]
       │    })
       ▼
┌─────────────────────┐
│  stdio transport    │
└──────┬──────────────┘
       │ 3. JSON-RPC over stdin/stdout
       ▼
┌─────────────────────┐
│  index.js           │
│  CoreTextServer     │
│  CallToolRequest    │
└──────┬──────────────┘
       │ 4. memoryManager.create(...)
       ▼
┌─────────────────────┐
│  MemoryManager      │
│  create() method    │
└──────┬──────────────┘
       │ 5. new MemoryEntry(...)
       │ 6. this.memories.set(id, entry)
       │ 7. this.persist()
       ▼
┌─────────────────────┐
│  data/memory.json   │
│  Written to disk    │
└──────┬──────────────┘
       │ 8. Return success + memory object
       ▼
┌─────────────────────┐
│  CoreTextServer     │
│  Format response    │
└──────┬──────────────┘
       │ 9. Return JSON response
       ▼
┌─────────────────────┐
│   Claude            │
│   "✅ Remembered!"  │
└─────────────────────┘
```

### Example: Memory with Enrichment

1. **User asks**: "Remember: Met with Sarah about Q4 planning. She seemed excited about the AI project."
2. **AI calls**: `memory_create` with `enrich: true`
3. **Server creates** memory entry
4. **DeepSeek enriches**:
   - Summary: "Meeting with Sarah discussing Q4 planning and AI project"
   - Keywords: ["Sarah", "Q4", "planning", "AI", "project"]
   - Sentiment: "positive"
   - Category: "business"
5. **Server updates** memory with enrichment
6. **Server persists** to disk
7. **Response**: Full memory object with enrichment data
8. **Next session**: Memory survives restart!

---

## Common Patterns

### 1. The Map Pattern for Fast Lookups

```javascript
class MemoryManager {
  constructor() {
    this.memories = new Map();  // Key-value store
  }

  async read(id) {
    return this.memories.get(id);  // O(1) lookup
  }
}
```

**Why Map?**

- Fast lookups by ID
- Easy conversion to/from JSON
- Native JavaScript, no dependencies

### 2. The Persist-After-Every-Change Pattern

```javascript
async create(content, type, metadata) {
  const entry = new MemoryEntry(content, type, metadata);
  this.memories.set(entry.id, entry);
  await this.persist();  // Write immediately
  return entry;
}

async update(id, updates) {
  const memory = this.memories.get(id);
  Object.assign(memory, updates);
  await this.persist();  // Write immediately
  return memory;
}
```

**Trade-off**: Simple but inefficient for high-frequency writes. Production would batch or use a database.

### 3. The Fallback Pattern

```javascript
async enrich(memory) {
  if (!this.apiKey) {
    return this.fallbackEnrich(memory);  // Graceful degradation
  }

  try {
    return await this.apiEnrich(memory);
  } catch (error) {
    console.error('API failed, using fallback');
    return this.fallbackEnrich(memory);  // Error recovery
  }
}
```

**Best practice**: System works (degraded) even when external service fails.

### 4. The Metadata Tracking Pattern

```javascript
async read(id) {
  const memory = this.memories.get(id);

  if (memory) {
    // Track every access
    memory.metadata.accessCount++;
    memory.metadata.lastAccessed = new Date().toISOString();
    await this.persist();
  }

  return memory;
}
```

**Why?** Build analytics into your data layer from day one!

### 5. The Demo Data Pattern

```javascript
async initialize() {
  try {
    const data = await fs.readFile(DATA_PATH, 'utf-8');
    this.memories = JSON.parse(data);
  } catch {
    // First run - create helpful examples
    await this.createDemoMemories();
  }
}

async createDemoMemories() {
  await this.create(
    "MCP enables persistent AI memory",
    "semantic",
    { tags: ["mcp", "demo"] }
  );
  // ... more demos
}
```

**Teaching benefit**: Server works immediately, students see examples.

---

## Extending the Server

### Adding a New Tool

**Example**: Add a `memory_export` tool to download all memories.

#### Step 1: Define the tool

```javascript
{
  name: 'memory_export',
  description: '📦 Export all memories to JSON format',
  inputSchema: {
    type: 'object',
    properties: {
      format: {
        type: 'string',
        enum: ['json', 'csv', 'markdown'],
        description: 'Export format',
        default: 'json'
      }
    }
  }
}
```

#### Step 2: Add handler in switch statement

```javascript
case 'memory_export': {
  const memories = await memoryManager.list();

  if (args.format === 'json') {
    return {
      content: [{
        type: 'text',
        text: JSON.stringify(memories, null, 2)
      }]
    };
  }

  if (args.format === 'markdown') {
    const markdown = memories.map(m =>
      `## ${m.type === 'episodic' ? '📅' : '📚'} ${m.content}\n` +
      `**Created**: ${new Date(m.metadata.created).toLocaleString()}\n` +
      `**Tags**: ${m.tags.join(', ')}\n`
    ).join('\n---\n\n');

    return {
      content: [{
        type: 'text',
        text: markdown
      }]
    };
  }

  // CSV format
  const csv = 'ID,Type,Content,Tags,Created\n' +
    memories.map(m =>
      `${m.id},"${m.type}","${m.content}","${m.tags.join(';')}","${m.metadata.created}"`
    ).join('\n');

  return {
    content: [{
      type: 'text',
      text: csv
    }]
  };
}
```

#### Step 3: Test it

```bash
npm run inspector
# Call memory_export with different formats
```

---

### Adding a New Resource

**Example**: Add a `memory://timeline` resource showing chronological view.

#### Step 1: Register the resource

```javascript
{
  uri: 'memory://timeline',
  name: '📅 Memory Timeline',
  description: 'Chronological view of all episodic memories',
  mimeType: 'text/markdown'
}
```

#### Step 2: Handle in ReadResourceRequestSchema

```javascript
if (uri === 'memory://timeline') {
  const memories = await memoryManager.list('episodic');

  // Sort by created date
  const sorted = memories.sort((a, b) =>
    new Date(a.metadata.created) - new Date(b.metadata.created)
  );

  // Group by date
  const byDate = {};
  sorted.forEach(m => {
    const date = new Date(m.metadata.created).toLocaleDateString();
    if (!byDate[date]) byDate[date] = [];
    byDate[date].push(m);
  });

  // Generate markdown
  const markdown = `# 📅 Memory Timeline

${Object.entries(byDate).map(([date, mems]) =>
  `## ${date}\n\n${mems.map(m =>
    `- **${new Date(m.metadata.created).toLocaleTimeString()}**: ${m.content}`
  ).join('\n')}`
).join('\n\n')}

---
*Total Events: ${sorted.length}*
`;

  return {
    contents: [{
      uri: uri,
      mimeType: 'text/markdown',
      text: markdown
    }]
  };
}
```

---

### Adding Memory Relationships

**Example**: Link memories to each other (like "this relates to that").

#### Step 1: Update MemoryEntry class

```javascript
class MemoryEntry {
  constructor(content, type = 'semantic', metadata = {}) {
    // ... existing code
    this.relatedTo = [];  // Array of memory IDs
  }
}
```

#### Step 2: Add new tool

```javascript
{
  name: 'memory_relate',
  description: '🔗 Create a relationship between two memories',
  inputSchema: {
    type: 'object',
    properties: {
      sourceId: { type: 'string', description: 'First memory ID' },
      targetId: { type: 'string', description: 'Second memory ID' },
      bidirectional: {
        type: 'boolean',
        description: 'Link both ways?',
        default: true
      }
    },
    required: ['sourceId', 'targetId']
  }
}
```

#### Step 3: Implement handler

```javascript
case 'memory_relate': {
  const source = await memoryManager.read(args.sourceId);
  const target = await memoryManager.read(args.targetId);

  if (!source || !target) {
    return {
      content: [{
        type: 'text',
        text: JSON.stringify({
          success: false,
          error: 'One or both memories not found'
        })
      }]
    };
  }

  // Add relationship
  if (!source.relatedTo.includes(args.targetId)) {
    source.relatedTo.push(args.targetId);
  }

  if (args.bidirectional && !target.relatedTo.includes(args.sourceId)) {
    target.relatedTo.push(args.sourceId);
  }

  await memoryManager.persist();

  return {
    content: [{
      type: 'text',
      text: JSON.stringify({
        success: true,
        message: `✅ Linked ${args.sourceId} → ${args.targetId}`
      })
    }]
  };
}
```

#### Step 4: Update knowledge graph to use explicit relationships

```javascript
// In memory://knowledge-graph resource
edges.push(...memories.flatMap(m =>
  m.relatedTo.map(targetId => ({
    source: m.id,
    target: targetId,
    weight: 10,  // Explicit links are stronger
    type: 'explicit'
  }))
));
```

---

## Key Takeaways

### For Learning MCP

1. **Tools vs Resources** - Tools = actions, Resources = information
2. **Stdio protocol** - Server is a child process communicating via stdin/stdout
3. **JSON Schema** - Defines tool parameters and validates input
4. **Persistence** - Memory survives restarts because we write to disk
5. **Graceful degradation** - Features fail independently (API optional)

### For Code Architecture

1. **Single file** - Everything in index.js makes teaching easier
2. **Class-based** - MemoryManager, DeepseekService, CoreTextServer
3. **Map for storage** - Fast lookups, easy JSON conversion
4. **Metadata-rich** - Track access patterns from day one
5. **Demo data** - First run creates helpful examples

### For Production Readiness

1. **Environment variables** - API keys never hardcoded
2. **Error handling** - Try/catch at every layer
3. **Logging to stderr** - stdout reserved for MCP protocol
4. **Health endpoint** - HTTP server for Azure Container Apps
5. **Atomic persistence** - Write entire file to avoid corruption

### For Teaching Context Engineering

1. **AI Amnesia problem** - Show ChatGPT forgetting between sessions
2. **Persistence solution** - Demonstrate server restart preserving memories
3. **Memory types** - Episodic vs semantic mirrors human cognition
4. **Enrichment value** - Show before/after with DeepSeek analysis
5. **Knowledge graphs** - Visualize how memories interconnect

---

## Next Steps

1. **Run the test suite**: `npm test` to validate all 8 tools
2. **Start Inspector**: `npm run inspector` for interactive testing
3. **Try demo scripts**: `npm run demo:all` for pre-built teaching sequences
4. **Read TEACHING_GUIDE.md**: Detailed lesson plans for instructors
5. **Deploy to Azure**: See `azure/` folder for production deployment

---

## Troubleshooting Tips

### "Server not responding"

- Check: `node --version` (needs 18+)
- Verify: Path to index.js is correct
- Look: Server stderr output for errors
- Try: `npm run kill-ports` to free port 3001

### "Memories not persisting"

- Check: `data/` directory exists and is writable
- Verify: No errors during `persist()` calls
- Look: `data/memory.json` file contents
- Try: Delete file and restart (creates demo data)

### "Enrichment not working"

- Check: `.env` file has `DEEPSEEK_API_KEY=sk-...`
- Verify: API key is valid at platform.deepseek.com
- Look: Server logs for API errors
- Fallback: Works without API using local enrichment

### "Health check fails"

- Check: Port 3001 not in use by another app
- Verify: `npm run kill-ports` clears it
- Look: HTTP response at http://localhost:3001/health
- Note: Health check is for Azure deployment, not required locally

### "Test failures"

- Run: `npm test` to see which tests fail
- Check: Demo memories exist (run `npm run demo:populate`)
- Verify: No conflicting servers running
- Clean: Delete `data/memory.json` and restart fresh

---

## File Size & Complexity Metrics

```
index.js:          830 lines
test-client.js:    280 lines
Total:           1,110 lines
```

**Teaching advantage**: All code in one file makes it easy to:

- Search for implementations
- Understand data flow
- Copy for experiments
- Deploy as single artifact

---

**Happy coding! Remember: The best way to understand this is to break it, then fix it.** 🧠✨
