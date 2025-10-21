# Context Journal MCP - Quick Reference Card

## 🚀 Setup Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Test server
python context_journal_mcp.py --help

# Find Claude config file
# macOS
open ~/Library/Application\ Support/Claude/

# Windows
explorer %APPDATA%\Claude\
```

## 📝 Claude Desktop Config

```json
{
  "mcpServers": {
    "context-journal": {
      "command": "python",
      "args": ["/ABSOLUTE/PATH/TO/context_journal_mcp.py"]
    }
  }
}
```

**Remember:** Use absolute paths, not relative!

## 🛠️ Available Tools

| Tool | Purpose | Destructive? |
|------|---------|--------------|
| `create_context_entry` | Add new context | No |
| `read_context_entry` | Get specific entry | No |
| `update_context_entry` | Modify entry | No |
| `delete_context_entry` | Remove entry | **Yes** |
| `list_context_entries` | Browse with filters | No |
| `search_context_entries` | Full-text search | No |

## 💬 Example Prompts for Claude

### **Creating Context**
```
"Save a context entry titled 'Azure MCP Deployment' with the context 
'Deployed to Container Apps in West US region. Connection string stored 
in Key Vault. Using managed identity for auth.' Tag it with 'azure', 
'mcp', and 'deployment'."
```

### **Reading Context**
```
"Show me entry ctx_0001 in markdown format"
```

### **Updating Context**
```
"Update entry ctx_0001 to add a note: 'Scaled to 3 replicas on 2025-10-20'"
```

### **Listing with Filters**
```
"List all context entries tagged with 'python' and 'azure'"
```

### **Searching**
```
"Search for all entries mentioning 'FastAPI' or 'API design'"
```

## 🎯 Tool Patterns

### **Basic Tool Structure**
```python
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

mcp = FastMCP("your_server_name")

class YourInput(BaseModel):
    param: str = Field(..., description="What this param does")

@mcp.tool(name="your_tool_name", annotations={...})
async def your_tool_name(params: YourInput) -> str:
    """Tool description that Claude can read."""
    # Your logic here
    return json.dumps(result)
```

### **Tool Annotations**
```python
annotations={
    "title": "Human-Readable Title",
    "readOnlyHint": True,      # Doesn't modify data
    "destructiveHint": False,   # Doesn't delete/destroy
    "idempotentHint": True,     # Safe to call multiple times
    "openWorldHint": False      # Doesn't interact with external entities
}
```

### **Input Validation with Pydantic**
```python
from pydantic import BaseModel, Field, field_validator

class CreateInput(BaseModel):
    name: str = Field(
        ...,                      # Required
        description="User name",
        min_length=1,
        max_length=100
    )
    age: int = Field(
        default=0,                # Optional with default
        ge=0,                     # Greater than or equal
        le=150                    # Less than or equal
    )
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        return v.strip().lower()
```

## 🐛 Debugging Tips

### **Check if server is running**
```bash
# Should show help and exit immediately
python context_journal_mcp.py --help
```

### **Test imports**
```bash
python -c "from mcp.server.fastmcp import FastMCP; print('OK')"
```

### **View Claude logs**
```bash
# macOS
tail -f ~/Library/Logs/Claude/mcp*.log

# Windows
Get-Content $env:APPDATA\Claude\logs\mcp*.log -Wait
```

### **Common Errors**

**"ModuleNotFoundError: No module named 'mcp'"**
```bash
pip install mcp
```

**"Server not appearing in Claude Desktop"**
1. Check config file location
2. Use absolute path in config
3. Restart Claude Desktop
4. Check Python version (need 3.10+)

**"Tool call failed"**
- Check Pydantic model validation
- Look at error message in Claude UI
- Verify all required fields provided

## 🔄 Local to Azure Migration

### **Phase 1: Local JSON**
```python
def load_data():
    with open('data.json', 'r') as f:
        return json.load(f)
```

### **Phase 2: Azure Cosmos DB**
```python
async def load_data():
    async with CosmosClient(endpoint, key) as client:
        container = client.get_database_client("db") \
                          .get_container_client("items")
        return [item async for item in container.query_items("SELECT * FROM c")]
```

### **Azure Setup Commands**
```bash
# Create Cosmos DB account
az cosmosdb create \
  --name my-context-db \
  --resource-group my-rg

# Create database
az cosmosdb sql database create \
  --account-name my-context-db \
  --name context_db

# Create container
az cosmosdb sql container create \
  --account-name my-context-db \
  --database-name context_db \
  --name entries \
  --partition-key-path "/id"
```

## 📊 Data Models

### **Entry Structure**
```json
{
  "id": "ctx_0001",
  "title": "Entry Title",
  "context": "Context content...",
  "tags": ["tag1", "tag2"],
  "notes": "Optional notes",
  "created_at": "2025-10-20T10:30:00.000Z",
  "updated_at": "2025-10-20T15:45:00.000Z"
}
```

### **Response Format**
```json
{
  "success": true,
  "entry_id": "ctx_0001",
  "message": "Operation successful",
  "timestamp": "2025-10-20T10:30:00.000Z"
}
```

### **Error Format**
```json
{
  "success": false,
  "error": "Error description",
  "message": "Helpful guidance for next steps"
}
```

## 🎓 Learning Resources

- **MCP Protocol**: https://modelcontextprotocol.io
- **FastMCP SDK**: https://github.com/modelcontextprotocol/python-sdk
- **Pydantic Docs**: https://docs.pydantic.dev
- **Azure Cosmos DB**: https://docs.microsoft.com/azure/cosmos-db

## 🏆 Challenge Exercises

### **Beginner**
1. Add a tool to count total entries
2. Add a tool to get entry by title (not ID)
3. Add validation to prevent duplicate titles

### **Intermediate**
4. Add export tool (entries to JSON file)
5. Add import tool (JSON file to entries)
6. Add bulk tag operations (add/remove tags from multiple entries)

### **Advanced**
7. Implement entry versioning (keep history of changes)
8. Add related entries (link entries together)
9. Implement tag hierarchies (parent/child tags)

## 🔑 Key Takeaways

✅ **MCP servers are Python programs with decorated functions**  
✅ **Pydantic handles all input validation automatically**  
✅ **Tools should return JSON or Markdown strings**  
✅ **Error messages should guide the next action**  
✅ **Local → Cloud migration only changes data layer**  

---

**Keep this card handy during the course!** 📌
