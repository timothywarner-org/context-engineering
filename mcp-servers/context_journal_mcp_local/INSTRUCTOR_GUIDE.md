# Instructor Script: Context Journal MCP Demo

## 🎬 Pre-Demo Setup (5 minutes before class)

### **Environment Check**

```bash
# Verify Python version
python --version  # Should be 3.10+

# Install dependencies
pip install -r requirements.txt

# Test server runs
python context_journal_mcp.py --help

# Check Claude Desktop config
# macOS: ~/Library/Application Support/Claude/claude_desktop_config.json
# Windows: %APPDATA%\Claude\claude_desktop_config.json
```

### **Config File Content**

```json
{
  "mcpServers": {
    "context-journal": {
      "command": "python",
      "args": ["/absolute/path/to/context_journal_mcp.py"]
    }
  }
}
```

---

## 🎭 Demo Script

### **Act 1: The Problem (5 minutes)**

**SHOW:** *Open Claude Desktop (MCP server NOT enabled yet)*

**SAY:**
> "Let me show you the fundamental problem we're solving. Watch this..."

**DEMO:**

1. Ask Claude: *"I'm building a FastAPI project for invoice processing. The key decision is to use PostgreSQL for storage and Redis for caching. Can you remember this?"*

2. Claude responds: *"I'll remember that during this conversation..."*

3. **Close Claude Desktop completely**

4. **Reopen Claude Desktop**

5. Ask Claude: *"What database did we choose for the invoice project?"*

6. Claude responds: *"I don't have information about previous conversations..."*

**SAY:**
> "This is the **amnesia problem**. Every time you close Claude, it forgets everything. This is by design - LLMs are stateless. But what if we could give Claude **persistent memory**? That's what MCP enables."

---

### **Act 2: The Solution (10 minutes)**

**SHOW:** *Enable the MCP server*

**SAY:**
> "Now I'm going to restart Claude with our Context Journal MCP server enabled. Watch for the 🔌 icon..."

**DEMO:**

1. **Restart Claude Desktop**

2. **Point to the 🔌 icon:**
   > "See this plug icon? That means Claude now has access to external tools."

3. **Click the 🔌 icon to show tools:**

   ```
   context-journal
   ├── create_context_entry
   ├── read_context_entry
   ├── update_context_entry
   ├── delete_context_entry
   ├── list_context_entries
   └── search_context_entries
   ```

4. **Ask Claude:** *"Let's save our project decision. Create a context entry titled 'Invoice Project: Architecture Decision' with the context 'Using FastAPI framework with PostgreSQL database for invoice storage and Redis for caching. Target deployment: Azure Container Apps.' Tag it with 'fastapi', 'postgresql', 'redis', and 'architecture'."*

5. **Watch Claude work:**
   - Claude uses `create_context_entry` tool
   - Shows the API call parameters
   - Returns success with entry ID (e.g., "ctx_0001")

**SAY:**
> "Notice how Claude is now **using a tool** to store this information externally. Let's prove it works..."

6. **Close Claude Desktop completely**

7. **Reopen Claude Desktop**

8. **Ask Claude:** *"What database did we choose for the invoice project?"*

9. **Watch the magic:**
   - Claude uses `search_context_entries` tool
   - Queries for "invoice" or "database"
   - Retrieves the saved context
   - **Responds with the correct information!**

**SAY:**
> "**This is MCP in action.** Claude just accessed external persistent storage through the tools we provided. Let's look at how this works under the hood..."

---

### **Act 3: The Mechanics (15 minutes)**

**SHOW:** *Open `context_journal_mcp.py` in VS Code*

**SAY:**
> "An MCP server is just a Python program that registers tools. Let's break down the key components..."

#### **Component 1: Server Initialization**

**SHOW CODE:**

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("context_journal_mcp")
```

**SAY:**
> "We initialize the FastMCP server with a name. This is what shows up in Claude Desktop as 'context-journal'."

#### **Component 2: Input Validation**

**SHOW CODE:**

```python
class CreateEntryInput(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )
    
    title: str = Field(
        ...,
        description="Title for this context entry",
        min_length=1,
        max_length=200
    )
    context: str = Field(
        ...,
        description="The actual context content",
        min_length=1,
        max_length=10000
    )
```

**SAY:**
> "We use Pydantic models for **type-safe input validation**. This prevents errors before they happen. Notice:
>
> - Field constraints (min_length, max_length)
> - Descriptions that Claude can read
> - Automatic validation (whitespace stripping, extra field rejection)"

#### **Component 3: Tool Registration**

**SHOW CODE:**

```python
@mcp.tool(
    name="create_context_entry",
    annotations={
        "title": "Create Context Journal Entry",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": False
    }
)
async def create_context_entry(params: CreateEntryInput) -> str:
    '''Create a new context journal entry...'''
```

**SAY:**
> "The `@mcp.tool` decorator does the magic:
>
> - **name**: How Claude refers to this tool
> - **annotations**: Metadata about what this tool does
>   - readOnlyHint: Doesn't modify external state
>   - destructiveHint: Performs deletion/destructive operations
>   - idempotentHint: Safe to call multiple times
>   - openWorldHint: Interacts with external entities
>
> These hints help Claude decide **when** to use each tool."

#### **Component 4: Business Logic**

**SHOW CODE:**

```python
async def create_context_entry(params: CreateEntryInput) -> str:
    try:
        journal = load_journal()
        
        entry_id = f"ctx_{len(journal['entries']) + 1:04d}"
        timestamp = datetime.utcnow().isoformat()
        
        entry = {
            "id": entry_id,
            "title": params.title,
            "context": params.context,
            "tags": params.tags,
            # ... more fields
        }
        
        journal["entries"].append(entry)
        save_journal(journal)
        
        return json.dumps(response, indent=2)
    except Exception as e:
        return json.dumps(error_response, indent=2)
```

**SAY:**
> "Notice the pattern:
>
> 1. Load data (from JSON file currently)
> 2. Perform operation (add entry)
> 3. Save data
> 4. Return structured response
>
> The beauty is: **when we migrate to Azure, only steps 1 and 3 change!**"

---

### **Act 4: Advanced Features (10 minutes)**

**DEMO:** *Live coding with students*

#### **Challenge: Add a Statistics Tool**

**SAY:**
> "Let's add a new tool together. We want to see which tags are most commonly used."

**LIVE CODE:**

```python
class TagStatsInput(BaseModel):
    """Input for tag statistics tool."""
    model_config = ConfigDict(extra='forbid')
    
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format"
    )

@mcp.tool(
    name="get_tag_statistics",
    annotations={
        "title": "Get Tag Usage Statistics",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False
    }
)
async def get_tag_statistics(params: TagStatsInput) -> str:
    """Get statistics about tag usage across all entries."""
    try:
        journal = load_journal()
        
        # Count tag occurrences
        tag_counts = {}
        for entry in journal["entries"]:
            for tag in entry.get("tags", []):
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        # Sort by frequency
        sorted_tags = sorted(tag_counts.items(), 
                           key=lambda x: x[1], 
                           reverse=True)
        
        if params.response_format == ResponseFormat.MARKDOWN:
            output = "# Tag Statistics\n\n"
            output += f"**Total Unique Tags:** {len(tag_counts)}\n\n"
            output += "| Tag | Usage Count |\n"
            output += "|-----|-------------|\n"
            for tag, count in sorted_tags:
                output += f"| {tag} | {count} |\n"
            return output
        else:
            return json.dumps({
                "total_unique_tags": len(tag_counts),
                "tag_counts": dict(sorted_tags)
            }, indent=2)
            
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e)
        }, indent=2)
```

**SAY:**
> "Now restart Claude Desktop and ask: 'Show me tag statistics for my context journal'
>
> **Students:** Try it! Claude will now call your new tool."

---

### **Act 5: Azure Migration (15 minutes)**

**SAY:**
> "Everything we've built runs locally on a JSON file. But what if you want:
>
> - Global access from any device
> - Multi-user collaboration
> - Enterprise-grade reliability
> - Automatic backups
>
> That's where **Azure Cosmos DB** comes in. Let's see the migration path..."

#### **Current Implementation**

**SHOW CODE:**

```python
def load_journal() -> Dict[str, Any]:
    """Load from JSON file."""
    with open(JOURNAL_FILE, 'r') as f:
        return json.load(f)

def save_journal(data: Dict[str, Any]) -> None:
    """Save to JSON file."""
    with open(JOURNAL_FILE, 'w') as f:
        json.dump(data, f, indent=2)
```

#### **Azure Implementation**

**SHOW CODE:**

```python
from azure.cosmos.aio import CosmosClient
import os

COSMOS_ENDPOINT = os.getenv("COSMOS_ENDPOINT")
COSMOS_KEY = os.getenv("COSMOS_KEY")

async def load_journal() -> Dict[str, Any]:
    """Load from Cosmos DB."""
    async with CosmosClient(COSMOS_ENDPOINT, COSMOS_KEY) as client:
        database = client.get_database_client("context_db")
        container = database.get_container_client("entries")
        
        query = "SELECT * FROM c ORDER BY c.created_at DESC"
        entries = [item async for item in container.query_items(query)]
        
        return {"entries": entries}

async def save_entry(entry: Dict[str, Any]) -> None:
    """Save to Cosmos DB."""
    async with CosmosClient(COSMOS_ENDPOINT, COSMOS_KEY) as client:
        database = client.get_database_client("context_db")
        container = database.get_container_client("entries")
        await container.upsert_item(entry)
```

**SAY:**
> "Notice:
>
> - **Same data structures** - entries are still JSON
> - **Same tool interfaces** - Claude uses tools the same way
> - **Different backend** - Now globally distributed
>
> The beauty of this architecture: **refactor the storage layer without touching the tool definitions.**"

#### **Azure Deployment**

**SHOW:** *Azure Portal demo*

**SAY:**
> "Here's the complete Azure architecture we'll deploy in Segment 4:

```
┌─────────────────┐
│ Claude Desktop  │
└────────┬────────┘
         │ MCP (stdio)
         ↓
┌─────────────────────────┐
│ Azure Container Apps    │
│ ┌─────────────────────┐ │
│ │ MCP Server (Python) │ │
│ └──────────┬──────────┘ │
└────────────┼────────────┘
             │ Azure SDK
             ↓
┌─────────────────────────┐
│ Azure Cosmos DB         │
│ ┌─────────────────────┐ │
│ │ context_db          │ │
│ │  └── entries        │ │
│ └─────────────────────┘ │
└─────────────────────────┘
```

> **Benefits:**
>
> - **Global distribution:** Low latency worldwide
> - **Automatic scaling:** Handles traffic spikes
> - **Built-in backups:** Point-in-time recovery
> - **Multi-region writes:** Conflict resolution
> - **99.999% SLA:** Enterprise reliability"

---

## 🎯 Key Talking Points Throughout Demo

### **Why MCP Matters**

- Solves the statelessness problem
- Extends LLM capabilities without retraining
- Production-ready protocol (Microsoft + Anthropic)
- Works with any LLM (Claude, ChatGPT, Copilot)

### **Architecture Principles**

- Tools are just functions with metadata
- Input validation prevents errors early
- Clear response formats (JSON/Markdown)
- Error messages guide next actions

### **Design Patterns**

- CRUD operations everyone understands
- Pagination for large datasets
- Search + filter for discoverability
- Consistent naming conventions

### **Enterprise Considerations**

- Authentication via environment variables
- Secrets management (Azure Key Vault)
- Rate limiting and throttling
- Monitoring and logging
- Cost optimization strategies

---

## 📋 Post-Demo Checklist

- [ ] Students can install and run the server locally
- [ ] Students understand the `@mcp.tool` decorator
- [ ] Students can add a new tool
- [ ] Students understand the Azure migration path
- [ ] Students have the GitHub repo URL for reference

---

## 🚨 Common Issues & Solutions

### **"Server not showing in Claude Desktop"**

- Check config file path
- Verify Python path is absolute
- Restart Claude Desktop
- Check Claude logs

### **"Import errors"**

```bash
pip install --upgrade mcp pydantic
```

### **"Tool not being called"**

- Check tool name matches documentation
- Verify annotations are correct
- Look at Claude's reasoning (visible in UI)

### **"Azure deployment failing"**

- Check connection string format
- Verify firewall rules allow connections
- Ensure managed identity has Cosmos DB permissions

---

## 📚 Student Takeaways

1. **MCP servers are just Python programs** - no magic
2. **Tools extend LLM capabilities** - give them superpowers
3. **Local → Cloud migration is straightforward** - same patterns
4. **This works with ANY LLM** - not just Claude
5. **You can build this TODAY** - all tools are production-ready

---

**End of Script** ✨
