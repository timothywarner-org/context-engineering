# Context Journal MCP Server

**A pedagogical MCP server for teaching context engineering fundamentals**

## 🎯 Learning Objectives

This MCP server is designed to teach:

1. **MCP Protocol Fundamentals**: How tools, schemas, and responses work
2. **Context Persistence**: Why LLMs need external memory systems
3. **CRUD Operations**: Classic Create, Read, Update, Delete patterns
4. **Input Validation**: Using Pydantic for robust type checking
5. **Azure Migration Path**: Clear progression from JSON → Cosmos DB

## 🏗️ Architecture

### **Local Development (Phase 1)**
```
Claude Desktop ←→ MCP Server ←→ context_journal.json
```

### **Azure Production (Phase 2)**
```
Claude Desktop ←→ MCP Server (Azure Container App) ←→ Azure Cosmos DB
```

## 🚀 Quick Start

### **Prerequisites**

- Python 3.10+
- Claude Desktop app (get MCP built-in)
- Basic Python knowledge

### **Installation**

1. **Install dependencies:**
```bash
pip install mcp anthropic-sdk pydantic
```

2. **Test the server:**
```bash
python context_journal_mcp.py --help
```

3. **Configure Claude Desktop:**

Edit your Claude Desktop config file:

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

Add this configuration:

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

4. **Restart Claude Desktop**

5. **Verify it's working:**
   - Look for the 🔌 icon in Claude Desktop
   - Click it to see "context-journal" listed
   - Available tools should show 6 context management tools

## 🎓 Teaching Guide

### **Segment 1: MCP Basics (15 minutes)**

**Demonstration:**
1. Show the "amnesia problem" - ask Claude something, close app, reopen
2. Enable the Context Journal MCP server
3. Create a context entry about the current conversation
4. Close and reopen Claude Desktop
5. Read the context entry back - **memory restored!**

**Key Teaching Points:**
- MCP tools extend LLM capabilities
- Tools = functions the LLM can call
- Server = collection of related tools
- Stdio transport = communication via stdin/stdout

**Live Coding:**
Show students the `@mcp.tool` decorator:
```python
@mcp.tool(name="create_context_entry", annotations={...})
async def create_context_entry(params: CreateEntryInput) -> str:
    # This becomes callable by Claude!
    pass
```

### **Segment 2: Tool Design Patterns (20 minutes)**

**Walk through the 6 tools:**

1. **create_context_entry** - Write operations (destructive=False)
2. **read_context_entry** - Read operations (readOnly=True, idempotent=True)
3. **update_context_entry** - Modification (idempotent=True)
4. **delete_context_entry** - Deletion (destructive=True)
5. **list_context_entries** - Collection access with pagination
6. **search_context_entries** - Full-text search

**Key Teaching Points:**
- Tool annotations guide LLM behavior
- Input validation with Pydantic prevents errors
- Consistent response formats (JSON/Markdown)
- Error messages should guide next actions

### **Segment 3: Hands-On Exercise (15 minutes)**

**Challenge:** Have students modify the server to add a new tool

```python
@mcp.tool(name="tag_statistics")
async def tag_statistics() -> str:
    """Return statistics about tag usage across all entries."""
    # Students implement this
    pass
```

**Solution walks them through:**
- Loading the journal
- Counting tag occurrences
- Formatting output (markdown/json)
- Error handling

### **Segment 4: Azure Migration Path (20 minutes)**

**Show the progression:**

**Phase 1 (Current):** Local JSON file
```python
def load_journal():
    with open(JOURNAL_FILE, 'r') as f:
        return json.load(f)
```

**Phase 2 (Azure):** Cosmos DB
```python
async def load_journal():
    container = cosmos_client.get_database_client("context_db")
                             .get_container_client("entries")
    query = "SELECT * FROM c"
    return [item async for item in container.query_items(query)]
```

**Key Teaching Points:**
- Same tool interfaces, different backends
- Azure Cosmos DB = globally distributed JSON database
- Connection strings and authentication
- Environment variables for secrets

## 🔧 Tool Reference

### **create_context_entry**
```python
{
    "title": "Project Decision: FastAPI",
    "context": "Team chose FastAPI for async support...",
    "tags": ["python", "architecture"],
    "notes": "Consider migration path from Flask"
}
```

### **read_context_entry**
```python
{
    "entry_id": "ctx_0001",
    "response_format": "markdown"  # or "json"
}
```

### **update_context_entry**
```python
{
    "entry_id": "ctx_0001",
    "tags": ["python", "fastapi", "production"],
    "notes": "Deployed to production 2025-10-20"
}
```

### **delete_context_entry**
```python
{
    "entry_id": "ctx_0001"
}
```

### **list_context_entries**
```python
{
    "tags": ["python"],
    "search_text": "API",
    "limit": 20,
    "offset": 0,
    "response_format": "markdown"
}
```

### **search_context_entries**
```python
{
    "query": "azure deployment",
    "response_format": "json"
}
```

## 📝 Example Conversation Flow

**Student:** "What did we decide about the API framework?"

**Claude:** Let me check your context journal...
*[calls search_context_entries with query="API framework"]*

**Claude:** Found it! *[displays saved decision from context entry]*

**Student:** "Add a note that we deployed this to production today"

**Claude:** *[calls update_context_entry to add deployment note]*
Done! Updated the entry with deployment information.

## 🐛 Troubleshooting

### **Server not appearing in Claude Desktop**

1. Check config file path is correct
2. Verify absolute path to Python script
3. Check Python version: `python --version` (need 3.10+)
4. View Claude Desktop logs:
   - macOS: `~/Library/Logs/Claude/`
   - Windows: `%APPDATA%\Claude\logs\`

### **Import errors**

```bash
# Install all dependencies
pip install mcp anthropic-sdk pydantic httpx
```

### **Permission errors**

```bash
# Make script executable (macOS/Linux)
chmod +x context_journal_mcp.py
```

## 🔄 Migration to Azure Cosmos DB

### **Step 1: Create Azure Resources**

```bash
# Azure CLI commands
az cosmosdb create \
  --name context-journal-db \
  --resource-group mcp-training \
  --default-consistency-level Session

az cosmosdb sql database create \
  --account-name context-journal-db \
  --resource-group mcp-training \
  --name context_db

az cosmosdb sql container create \
  --account-name context-journal-db \
  --database-name context_db \
  --name entries \
  --partition-key-path "/id" \
  --throughput 400
```

### **Step 2: Update Server Code**

Replace storage functions:

```python
from azure.cosmos.aio import CosmosClient
import os

COSMOS_ENDPOINT = os.getenv("COSMOS_ENDPOINT")
COSMOS_KEY = os.getenv("COSMOS_KEY")

async def load_journal():
    """Load journal from Cosmos DB instead of JSON file."""
    async with CosmosClient(COSMOS_ENDPOINT, COSMOS_KEY) as client:
        database = client.get_database_client("context_db")
        container = database.get_container_client("entries")
        
        query = "SELECT * FROM c ORDER BY c.created_at DESC"
        entries = []
        async for item in container.query_items(query):
            entries.append(item)
        
        return {"entries": entries}

async def save_entry(entry):
    """Save entry to Cosmos DB."""
    async with CosmosClient(COSMOS_ENDPOINT, COSMOS_KEY) as client:
        database = client.get_database_client("context_db")
        container = database.get_container_client("entries")
        await container.upsert_item(entry)
```

### **Step 3: Deploy to Azure Container Apps**

```bash
# Build container
docker build -t context-journal-mcp .

# Push to Azure Container Registry
az acr build --registry myregistry --image context-journal-mcp .

# Deploy to Container Apps
az containerapp create \
  --name context-journal-mcp \
  --resource-group mcp-training \
  --image myregistry.azurecr.io/context-journal-mcp \
  --environment mcp-environment \
  --secrets cosmos-key=$COSMOS_KEY \
  --env-vars COSMOS_ENDPOINT=$COSMOS_ENDPOINT
```

## 📊 Data Model

### **Entry Structure**
```json
{
  "id": "ctx_0001",
  "title": "Python Project Setup",
  "context": "Detailed context content...",
  "tags": ["python", "setup"],
  "notes": "Optional additional notes",
  "created_at": "2025-10-20T10:30:00.000Z",
  "updated_at": "2025-10-20T15:45:00.000Z"
}
```

### **Journal Structure**
```json
{
  "entries": [...],
  "metadata": {
    "created_at": "2025-10-20T10:00:00.000Z",
    "version": "1.0"
  }
}
```

## 🎯 Key Pedagogical Features

1. **Progressive Complexity**: Starts simple (JSON file), scales to cloud
2. **Real Utility**: Actually solves the LLM memory problem
3. **Clear Patterns**: CRUD operations everyone understands
4. **Visible Results**: Students see immediate impact in Claude Desktop
5. **Enterprise Path**: Natural progression to production Azure deployment

## 📚 Additional Resources

- [MCP Protocol Documentation](https://modelcontextprotocol.io)
- [FastMCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [Azure Cosmos DB Documentation](https://docs.microsoft.com/azure/cosmos-db/)
- [Pydantic V2 Documentation](https://docs.pydantic.dev/latest/)

## 🤝 Contributing

Students can extend this server with:
- Export/import functionality
- Tag management tools
- Search with fuzzy matching
- Context versioning
- Sharing contexts between users

## 📄 License

MIT License - Perfect for educational use and modification

---

**Built for O'Reilly "Context Engineering with MCP" Training**  
*Teaching context persistence from local JSON to global Azure scale*
