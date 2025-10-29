# MCP Inspector - Complete Tour Guide

> **Your visual debugging tool for MCP servers**
> Learn every feature, button, and panel in the MCP Inspector

## What is MCP Inspector?

MCP Inspector is a **browser-based debugging tool** for Model Context Protocol servers. Think of it as "Postman for MCP" - it lets you:

- 🔍 Explore available tools and resources
- 🧪 Test tool calls with custom parameters
- 📊 View server responses in real-time
- 🐛 Debug MCP protocol messages
- 📝 Inspect server capabilities

**Official Docs**: https://github.com/modelcontextprotocol/inspector

---

## Starting the Inspector

### Launch Command

```bash
# From coretext-mcp directory
npm run inspector
```

**What happens:**
1. Inspector starts your MCP server as a child process
2. Opens a web interface at http://localhost:5173
3. Connects to your server via stdio
4. Shows "Connected" status in the UI

**Expected output:**
```
Starting MCP inspector...
🔍 MCP Inspector is up and running at http://localhost:5173 🚀
```

### Troubleshooting Startup

**Issue**: Port 5173 already in use
```bash
# Kill existing process
lsof -ti:5173 | xargs kill -9  # Mac/Linux
netstat -ano | findstr :5173   # Windows (find PID, then taskkill)
```

**Issue**: Server won't start
- Check `src/index.js` has no syntax errors
- Verify `npm install` completed successfully
- Look for error messages in terminal

---

## Inspector Interface Overview

When you open http://localhost:5173, you'll see 4 main sections:

```
┌─────────────────────────────────────────────────┐
│  MCP Inspector Header                           │
│  [Connection Status] [Server Info]              │
├─────────────┬───────────────────────────────────┤
│             │                                   │
│  LEFT       │  RIGHT PANEL                      │
│  SIDEBAR    │                                   │
│             │  [Current View Content]           │
│  • Tools    │                                   │
│  • Resources│                                   │
│  • Prompts  │                                   │
│  • Sampling │                                   │
│  • Logs     │                                   │
│             │                                   │
└─────────────┴───────────────────────────────────┘
```

---

## Section 1: Connection Status (Top Bar)

### What You See

**Green Dot + "Connected"**
- ✅ Server is running and responsive
- ✅ Protocol messages flowing correctly
- ✅ Ready to test

**Red Dot + "Disconnected"**
- ❌ Server crashed or exited
- ❌ Check terminal for error messages
- ❌ Restart inspector to reconnect

**Server Info Button** (ℹ️ icon)
- Click to see server metadata
- Shows: name, version, protocol version
- Useful for debugging version mismatches

### Try It Now

1. Click the **ℹ️ Server Info** button
2. You should see:
   ```json
   {
     "name": "CoreText MCP Server",
     "version": "1.0.0",
     "protocolVersion": "2024-11-05"
   }
   ```

---

## Section 2: Tools Tab (Left Sidebar)

**Purpose**: Discover and test all tools your server exposes

### What You See

A list of tool names with their descriptions:

```
🔧 Tools
  ├─ memory_create
  │  Store new context with type and tags
  ├─ memory_read
  │  Read a specific memory by ID
  ├─ memory_update
  │  Update an existing memory
  ├─ memory_delete
  │  Delete a memory by ID
  ├─ memory_search
  │  Search memories by query
  ├─ memory_list
  │  List all memories
  ├─ memory_stats
  │  Get memory statistics
  └─ memory_enrich
     Enrich a memory with AI analysis
```

### Testing a Tool (Step-by-Step)

#### Example 1: Create a Memory

1. **Click "memory_create"** in the left sidebar

2. **Right panel shows:**
   - Tool name and description
   - Input schema (required/optional parameters)
   - Empty JSON editor for parameters
   - "Execute" button

3. **Fill in parameters:**
   ```json
   {
     "content": "MCP enables persistent AI memory across conversations",
     "type": "semantic",
     "tags": ["mcp", "memory", "context"],
     "enrich": false
   }
   ```

4. **Click "Execute"** button

5. **Response appears below:**
   ```json
   {
     "success": true,
     "memory": {
       "id": "550e8400-e29b-41d4-a716-446655440000",
       "content": "MCP enables persistent AI memory...",
       "type": "semantic",
       "tags": ["mcp", "memory", "context"],
       "metadata": {
         "created": "2025-10-29T19:30:00Z",
         "updated": "2025-10-29T19:30:00Z"
       }
     }
   }
   ```

6. **What this means:**
   - ✅ Tool executed successfully
   - ✅ Server created a new memory
   - ✅ UUID was auto-generated
   - ✅ Timestamps added automatically
   - 📝 Copy the `id` for next steps

#### Example 2: Read the Memory

1. **Click "memory_read"** in left sidebar

2. **Fill in parameters:**
   ```json
   {
     "id": "550e8400-e29b-41d4-a716-446655440000"
   }
   ```
   (Use the ID from previous step)

3. **Click "Execute"**

4. **Response shows the memory details:**
   ```json
   {
     "memory": {
       "id": "550e8400-...",
       "content": "MCP enables persistent AI memory...",
       "type": "semantic",
       ...
     }
   }
   ```

#### Example 3: List All Memories

1. **Click "memory_list"**

2. **No parameters needed** (this tool takes no input)

3. **Click "Execute"**

4. **Response shows array of memories:**
   ```json
   {
     "memories": [
       {
         "id": "550e8400-...",
         "content": "MCP enables persistent AI memory...",
         ...
       },
       {
         "id": "660f9511-...",
         "content": "Another memory...",
         ...
       }
     ],
     "total": 2
   }
   ```

### Understanding Tool Parameters

**Input Schema Box** shows:
- **type**: Data type (string, number, boolean, object, array)
- **required**: Must provide this parameter
- **optional**: Can omit this parameter
- **description**: What the parameter does
- **enum**: Limited set of allowed values

**Example schema:**
```json
{
  "type": "object",
  "properties": {
    "content": {
      "type": "string",
      "description": "The memory content to store"
    },
    "type": {
      "type": "string",
      "enum": ["semantic", "episodic"],
      "description": "Memory type"
    },
    "tags": {
      "type": "array",
      "items": { "type": "string" },
      "description": "Optional tags for categorization"
    }
  },
  "required": ["content", "type"]
}
```

**How to read this:**
- `content` is required (string)
- `type` is required (must be "semantic" or "episodic")
- `tags` is optional (array of strings)

### Common Tool Testing Patterns

**Pattern 1: CRUD Operations**
```
1. Create → memory_create
2. Read → memory_read (use ID from step 1)
3. Update → memory_update (same ID)
4. Delete → memory_delete (same ID)
5. Verify → memory_read (should return "not found")
```

**Pattern 2: Search and Filter**
```
1. Create multiple memories
2. Use memory_search with different queries
3. Compare results
4. Verify relevance
```

**Pattern 3: Enrichment Testing**
```
1. Create memory with enrich: true
2. Check response for enrichment data
3. If no API key: verify fallback enrichment
4. If API key set: verify AI-powered enrichment
```

---

## Section 3: Resources Tab (Left Sidebar)

**Purpose**: View always-available context that doesn't require calling tools

### What You See

A list of resource URIs:

```
📁 Resources
  ├─ memory://overview
  │  Dashboard with stats and tag cloud
  ├─ memory://context-stream
  │  Time-windowed memory view
  └─ memory://knowledge-graph
     Semantic connections between memories
```

### Reading a Resource (Step-by-Step)

#### Example 1: Memory Overview Dashboard

1. **Click "memory://overview"** in left sidebar

2. **Right panel shows:**
   - Resource URI
   - MIME type (text/markdown or application/json)
   - "Read" button

3. **Click "Read"** button

4. **Response shows markdown content:**
   ```markdown
   # Memory Overview

   ## 📊 Statistics
   - Total Memories: 5
   - Semantic: 3
   - Episodic: 2

   ## 🏷️ Tag Cloud
   - mcp (3)
   - memory (2)
   - context (2)
   - learning (1)

   ## 📝 Recent Activity
   - Last created: 2 minutes ago
   - Last accessed: 1 minute ago
   ```

5. **What this means:**
   - Resources are **read-only** (no parameters, no modifications)
   - Content is **generated dynamically** (reflects current state)
   - Useful for **dashboards** and **status displays**

#### Example 2: Context Stream

1. **Click "memory://context-stream"**

2. **Click "Read"**

3. **Response shows JSON with time-grouped memories:**
   ```json
   {
     "contextStream": {
       "recent": [
         {
           "id": "...",
           "content": "Memory from 5 minutes ago",
           "accessed": "2025-10-29T19:25:00Z"
         }
       ],
       "today": [
         {
           "id": "...",
           "content": "Memory from this morning",
           "accessed": "2025-10-29T10:00:00Z"
         }
       ],
       "earlier": [
         {
           "id": "...",
           "content": "Memory from yesterday",
           "accessed": "2025-10-28T15:00:00Z"
         }
       ]
     }
   }
   ```

4. **Use case**: Show AI what's "top of mind" vs. background knowledge

#### Example 3: Knowledge Graph

1. **Click "memory://knowledge-graph"**

2. **Click "Read"**

3. **Response shows graph structure:**
   ```json
   {
     "nodes": [
       {
         "id": "550e8400-...",
         "label": "MCP enables persistent...",
         "type": "semantic"
       },
       {
         "id": "660f9511-...",
         "label": "Context window is...",
         "type": "semantic"
       }
     ],
     "edges": [
       {
         "from": "550e8400-...",
         "to": "660f9511-...",
         "relationship": "shared_tags",
         "tags": ["mcp", "context"]
       }
     ],
     "clusters": [
       {
         "theme": "MCP Concepts",
         "memoryIds": ["550e8400-...", "660f9511-..."]
       }
     ]
   }
   ```

4. **Use case**: Visualize how memories relate to each other

### Resources vs. Tools

| Feature | Resources | Tools |
|---------|-----------|-------|
| **Action** | Read only | Execute/Modify |
| **Parameters** | None | Required/Optional |
| **Updates** | Dynamic (auto-refresh) | Manual (call each time) |
| **Use Case** | Status, dashboards | CRUD operations |
| **Speed** | Very fast | Depends on operation |

**When to use Resources:**
- Get current status without modifying
- Dashboard displays
- Context for AI prompts
- Always-available information

**When to use Tools:**
- Create/Update/Delete data
- Perform searches
- Execute operations
- Modify server state

---

## Section 4: Prompts Tab (Left Sidebar)

**Purpose**: Discover reusable prompt templates your server provides

### What You See

For CoreText MCP:
```
📝 Prompts
  (No prompts defined)
```

**Why empty?** CoreText MCP focuses on tools and resources, not prompt templates.

### What Prompts Are

Prompts are **reusable templates** with **variable placeholders**:

**Example prompt** (from another server):
```json
{
  "name": "summarize_memory",
  "description": "Create a summary of a memory",
  "arguments": [
    {
      "name": "memory_id",
      "description": "ID of memory to summarize",
      "required": true
    },
    {
      "name": "max_length",
      "description": "Maximum summary length",
      "required": false
    }
  ]
}
```

**When used by AI**:
```
User: "Summarize memory 550e8400..."
AI calls prompt: summarize_memory(memory_id="550e8400...")
Server returns: "Based on memory 550e8400, here's a summary: ..."
```

**Use cases:**
- Standardized prompt patterns
- Few-shot examples
- System prompts with context injection
- Multi-step workflows

---

## Section 5: Sampling Tab (Left Sidebar)

**Purpose**: Let your server request LLM completions

### What You See

```
🎲 Sampling
  (Depends on server capabilities)
```

**What is Sampling?**
- **Server** can ask the **client** (Claude Desktop, Inspector, etc.) to generate text
- Reverse of normal flow: Server → Client → LLM → Server
- Useful for servers that need AI reasoning

**Example use case:**
```
1. User asks: "What's the best memory about MCP?"
2. Tool: memory_list returns 10 memories
3. Server: "I need AI to rank these"
4. Sampling request → LLM ranks memories
5. Server: Returns top-ranked memory
```

**For CoreText MCP**: Not currently implemented (future enhancement)

---

## Section 6: Logs Tab (Left Sidebar)

**Purpose**: See all MCP protocol messages in real-time

### What You See

A scrolling log of JSON-RPC messages:

```
🗂️ Logs
  ↓ Request: tools/list
  ↑ Response: [8 tools]

  ↓ Request: tools/call (memory_create)
  ↑ Response: {"success": true, ...}

  ↓ Request: resources/list
  ↑ Response: [3 resources]
```

### Log Entry Details

**Request Log:**
```json
{
  "type": "request",
  "method": "tools/call",
  "params": {
    "name": "memory_create",
    "arguments": {
      "content": "Test memory",
      "type": "semantic"
    }
  },
  "id": 1,
  "timestamp": "2025-10-29T19:30:00.123Z"
}
```

**Response Log:**
```json
{
  "type": "response",
  "id": 1,
  "result": {
    "success": true,
    "memory": { ... }
  },
  "timestamp": "2025-10-29T19:30:00.456Z"
}
```

### Using Logs for Debugging

**Scenario 1: Tool Call Failed**

**Log shows:**
```json
{
  "type": "error",
  "id": 1,
  "error": {
    "code": -32602,
    "message": "Invalid params: missing required field 'content'"
  }
}
```

**What to do:**
1. Check the error message
2. Review tool schema
3. Ensure all required parameters provided
4. Check parameter types match schema

**Scenario 2: Slow Response**

**Log shows:**
```
↓ Request: 19:30:00.000Z
↑ Response: 19:30:05.000Z  (5 second delay!)
```

**What to check:**
1. Is enrichment enabled? (API calls add latency)
2. Large dataset? (search across many memories)
3. Database slow? (check Cosmos DB connection)

**Scenario 3: Unexpected Response**

**Log comparison:**
```
Expected:
{ "success": true, "memory": {...} }

Actual:
{ "error": "Memory not found" }
```

**What to do:**
1. Verify memory ID exists
2. Check if memory was deleted
3. Ensure database has data

### Log Filters

**Filter by type:**
- ☑️ Requests
- ☑️ Responses
- ☑️ Errors
- ☑️ Notifications

**Filter by method:**
- `tools/list`
- `tools/call`
- `resources/list`
- `resources/read`

---

## Complete Workflow Example

Let's walk through a **complete testing session**:

### Goal: Test the full memory lifecycle

#### Step 1: Check Server Status

1. **Open Inspector**: http://localhost:5173
2. **Verify**: Green "Connected" dot
3. **Click**: ℹ️ Server Info
4. **Confirm**: Server name is "CoreText MCP Server"

#### Step 2: Explore Available Tools

1. **Click**: Tools tab
2. **Count**: Should see 8 tools
3. **Read descriptions**: Understand what each does

#### Step 3: Check Current State

1. **Click**: "memory_list" tool
2. **Click**: "Execute" (no parameters needed)
3. **Note**: Current memory count

#### Step 4: Create a New Memory

1. **Click**: "memory_create" tool
2. **Enter parameters**:
   ```json
   {
     "content": "MCP Inspector is a powerful debugging tool for testing MCP servers",
     "type": "semantic",
     "tags": ["mcp", "tools", "debugging"],
     "enrich": false
   }
   ```
3. **Click**: "Execute"
4. **Copy**: The `id` from response

#### Step 5: Read the Memory

1. **Click**: "memory_read" tool
2. **Enter parameters**:
   ```json
   {
     "id": "YOUR_ID_FROM_STEP_4"
   }
   ```
3. **Click**: "Execute"
4. **Verify**: Content matches what you created

#### Step 6: Update the Memory

1. **Click**: "memory_update" tool
2. **Enter parameters**:
   ```json
   {
     "id": "YOUR_ID_FROM_STEP_4",
     "content": "MCP Inspector is an ESSENTIAL debugging tool for testing MCP servers",
     "tags": ["mcp", "tools", "debugging", "essential"]
   }
   ```
3. **Click**: "Execute"
4. **Note**: Updated timestamp changed

#### Step 7: Search for the Memory

1. **Click**: "memory_search" tool
2. **Enter parameters**:
   ```json
   {
     "query": "debugging"
   }
   ```
3. **Click**: "Execute"
4. **Verify**: Your memory appears in results

#### Step 8: View in Context Stream

1. **Click**: Resources tab
2. **Click**: "memory://context-stream"
3. **Click**: "Read"
4. **Find**: Your memory in "recent" section

#### Step 9: Check Statistics

1. **Click**: "memory://overview"
2. **Click**: "Read"
3. **See**: Updated memory count and tag cloud

#### Step 10: Delete the Memory

1. **Click**: Tools tab
2. **Click**: "memory_delete" tool
3. **Enter parameters**:
   ```json
   {
     "id": "YOUR_ID_FROM_STEP_4"
   }
   ```
4. **Click**: "Execute"
5. **Verify**: Success message

#### Step 11: Verify Deletion

1. **Click**: "memory_read" tool
2. **Enter parameters**:
   ```json
   {
     "id": "YOUR_ID_FROM_STEP_4"
   }
   ```
3. **Click**: "Execute"
4. **Expect**: "Memory not found" error

#### Step 12: Review Logs

1. **Click**: Logs tab
2. **Scroll through**: All 11 previous operations
3. **See**: Request/response pairs
4. **Understand**: Protocol flow

**🎉 Congratulations!** You've completed a full tour of MCP Inspector.

---

## Tips & Tricks

### Keyboard Shortcuts

- **`Cmd/Ctrl + K`**: Focus search in sidebar
- **`Cmd/Ctrl + Enter`**: Execute current tool
- **`Cmd/Ctrl + L`**: Clear logs
- **`Esc`**: Close modals/panels

### JSON Editing Tips

**Auto-format JSON:**
```json
// Paste this messy JSON:
{"content":"test","type":"semantic","tags":["a","b"]}

// Press Cmd/Ctrl + Shift + F:
{
  "content": "test",
  "type": "semantic",
  "tags": ["a", "b"]
}
```

**Copy from previous response:**
1. Execute a tool
2. Click "Copy" button on response
3. Paste into next tool's parameters
4. Edit as needed

### Testing Patterns

**Pattern 1: Rapid prototyping**
- Quickly test tool variations
- Try different parameter combinations
- See immediate results

**Pattern 2: Error discovery**
- Intentionally send invalid params
- See error messages
- Improve error handling

**Pattern 3: Performance testing**
- Create many memories
- Time search operations
- Check enrichment latency

**Pattern 4: Integration testing**
- Test full workflows
- Verify state changes
- Check resource updates

---

## Common Issues & Solutions

### Issue 1: "Connection Lost"

**Symptoms**: Red dot, no tools visible

**Causes**:
- Server crashed
- Syntax error in `src/index.js`
- Port conflict

**Solution**:
1. Check terminal for error messages
2. Fix any syntax errors
3. Restart inspector: `Ctrl+C`, then `npm run inspector`

### Issue 2: "Tool execution failed"

**Symptoms**: Error response after clicking Execute

**Causes**:
- Missing required parameter
- Wrong parameter type
- Server logic error

**Solution**:
1. Check Logs tab for detailed error
2. Review tool schema
3. Verify parameter types match

### Issue 3: "No response"

**Symptoms**: Infinite loading after Execute

**Causes**:
- Server hung/frozen
- Long-running operation (enrichment with AI)
- Database timeout

**Solution**:
1. Wait 30 seconds (API calls can be slow)
2. Check terminal for logs
3. Restart if truly frozen

### Issue 4: "Empty response"

**Symptoms**: Success but no data returned

**Causes**:
- Database empty (no memories)
- Search returned no results
- Resource not yet populated

**Solution**:
1. Create test data first
2. Check search query
3. Verify database has content

---

## Advanced Features

### Custom Request IDs

The inspector auto-generates request IDs, but you can track specific requests:

1. Open browser DevTools (F12)
2. Go to Network tab
3. Watch WebSocket messages
4. See request/response correlation

### Protocol Inspection

Want to see raw MCP protocol?

1. **Click**: Logs tab
2. **Enable**: All filters
3. **Execute**: Any tool
4. **See**: JSON-RPC 2.0 messages

**Example request:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "memory_create",
    "arguments": {
      "content": "test",
      "type": "semantic"
    }
  }
}
```

**Example response:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "success": true,
    "memory": { ... }
  }
}
```

### Testing with Real Data

**Import JSON data:**

1. Prepare test memories in JSON file:
   ```json
   [
     {
       "content": "Memory 1",
       "type": "semantic",
       "tags": ["test"]
     },
     {
       "content": "Memory 2",
       "type": "episodic",
       "tags": ["test"]
     }
   ]
   ```

2. Use a script to bulk-create:
   ```bash
   # Call memory_create for each entry
   ```

3. Then test search/list/stats operations

---

## Teaching with MCP Inspector

### Lesson Plan Ideas

**Lesson 1: Introduction to MCP**
- Show the 4 main concepts (Tools, Resources, Prompts, Sampling)
- Live demo: Create and read a memory
- Explain request/response flow

**Lesson 2: Tool Development**
- Show how tool schema becomes UI
- Test parameter validation
- Demonstrate error handling

**Lesson 3: Resource Patterns**
- Compare static vs. dynamic resources
- Show dashboard use case (overview)
- Explain context streams for AI

**Lesson 4: Debugging Techniques**
- Use Logs tab to trace issues
- Find and fix parameter errors
- Optimize slow operations

### Student Exercises

**Exercise 1: Basic CRUD**
```
1. Create 3 memories (2 semantic, 1 episodic)
2. Read each one back
3. Update one with new tags
4. Delete one
5. Verify final count is 2
```

**Exercise 2: Search & Filter**
```
1. Create 5 memories with different tags
2. Search for tag "mcp"
3. Search for keyword "context"
4. Compare result counts
5. Explain why results differ
```

**Exercise 3: Error Handling**
```
1. Try to create memory without 'content'
2. Try to read non-existent ID
3. Try to update with invalid type
4. Screenshot each error
5. Write down error codes
```

**Exercise 4: Resource Monitoring**
```
1. Read memory://overview
2. Create 2 new memories
3. Read memory://overview again
4. Compare before/after statistics
5. Explain what changed
```

### Assessment Questions

1. **What's the difference between a tool and a resource?**
   - Answer: Tools modify state, resources provide read-only views

2. **Why use MCP Inspector instead of curl/Postman?**
   - Answer: MCP-specific protocol, visual tool discovery, integrated logs

3. **How do you debug a failed tool call?**
   - Answer: Check Logs tab, review error message, verify parameters against schema

4. **When would you use resources vs. tool calls?**
   - Answer: Resources for status/dashboards, tools for CRUD operations

---

## Next Steps

### After Mastering Inspector

1. **Connect to Claude Desktop**
   - Configure `claude_desktop_config.json`
   - Test from actual AI chat
   - See tool calls in real conversation

2. **Build Custom Tools**
   - Modify `src/index.js`
   - Add new tool definitions
   - Test immediately in Inspector

3. **Deploy to Azure**
   - Use deployment scripts
   - Test remote server
   - Point Inspector to production URL

4. **Create Complex Workflows**
   - Chain multiple tool calls
   - Build context-aware responses
   - Implement memory patterns

---

## Quick Reference

### Common Commands

```bash
# Start Inspector
npm run inspector

# Run server without Inspector
npm start

# Run test suite
npm test

# Watch for changes
npm run dev
```

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Cmd/Ctrl + K` | Focus search |
| `Cmd/Ctrl + Enter` | Execute tool |
| `Cmd/Ctrl + L` | Clear logs |
| `Esc` | Close modal |

### URL Endpoints

- **Inspector UI**: http://localhost:5173
- **WebSocket**: ws://localhost:5173/mcp (internal)

### MCP Concepts

| Concept | Purpose | Example |
|---------|---------|---------|
| **Tools** | Execute actions | memory_create |
| **Resources** | Read-only data | memory://overview |
| **Prompts** | Template patterns | (not used in CoreText) |
| **Sampling** | Server→LLM requests | (not used in CoreText) |

---

## Troubleshooting Reference

| Problem | Check | Solution |
|---------|-------|----------|
| Can't connect | Terminal errors | Restart inspector |
| Tool fails | Logs tab | Fix parameters |
| Slow response | Network tab | Check API latency |
| Wrong data | Resources tab | Refresh/re-create |
| Missing tools | Server info | Verify server running |

---

**Guide Version**: 1.0.0
**Last Updated**: 2025-10-29
**For**: CoreText MCP Server v1.0.0
**MCP Inspector**: Latest (installed via npm)

---

**Questions?** Check the logs tab - it has all the answers! 🔍
