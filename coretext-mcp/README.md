# CoreText MCP Server 🧠

> **Context Engineering with Persistent AI Memory**  
> Teaching implementation for O'Reilly Live Training by Tim Warner

## 🎯 What This Demonstrates

This MCP server showcases the core concepts from the "Context Engineering with MCP" course:

1. **Persistent Memory**: AI that remembers across sessions
2. **CRUD Operations**: Create, Read, Update, Delete context
3. **Memory Types**: Episodic (events) vs Semantic (facts)
4. **AI Enrichment**: Deepseek integration with authentication
5. **Production Path**: JSON → Cosmos DB migration ready

## 🚀 Quick Start

### 1. Install Dependencies

```bash
npm install
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your Deepseek API key (optional)
```

### 3. Test with MCP Inspector

```bash
npm run inspector
```

### 4. Run Tests

```bash
npm test
```

## 🔧 Available Tools

### `memory_create`

Store new context with type and tags

```json
{
  "content": "Important fact to remember",
  "type": "semantic",
  "tags": ["important", "fact"],
  "enrich": true
}
```

### `memory_read`

Retrieve specific memory by ID

### `memory_update`

Modify existing memory content or metadata

### `memory_delete`

Permanently remove a memory

### `memory_search`

Full-text search across all memories

### `memory_list`

List memories with optional type filter

### `memory_stats`

Get system statistics and usage patterns

### `memory_enrich`

Apply AI analysis to existing memory

## 📚 Memory Types

### Episodic Memory

- **What**: Time-based, event-focused memories
- **Example**: "Meeting with client on Oct 31, 2024"
- **Use Case**: Conversation history, event tracking

### Semantic Memory

- **What**: Fact-based, conceptual knowledge
- **Example**: "MCP enables persistent AI context"
- **Use Case**: Documentation, reference material

## 🔐 Authentication Pattern

The Deepseek integration demonstrates production authentication:

1. API key stored in environment variables
2. Optional enrichment when configured
3. Graceful fallback when not authenticated
4. Ready for Azure Key Vault integration

## 📄 Resources

The server provides three resources that maintain context:

### `memory://overview`

- Markdown dashboard with statistics
- Recent activity and most accessed memories
- Tag cloud visualization
- System configuration status

### `memory://context-stream`

- Real-time view of active context
- Time-windowed memory groups (recent/today/earlier)
- Active topics extraction
- Perfect for maintaining conversation continuity

### `memory://knowledge-graph`

- Semantic network of memory connections
- Identifies knowledge clusters
- Shows connection strength between memories
- Demonstrates how concepts interconnect

## 🏗️ Architecture

```
coretext-mcp/
├── src/
│   ├── index.js         # Main MCP server
│   └── test-client.js   # Test harness
├── data/
│   └── memory.json      # Local storage (dev)
├── package.json         # Dependencies
├── .env                 # Configuration
└── README.md            # Documentation
```

## 🌐 Claude Desktop Integration

### Windows (claude_desktop_config.json)

```json
{
  "mcpServers": {
    "coretext": {
      "command": "node",
      "args": ["C:/github/coretext-mcp/src/index.js"]
    }
  }
}
```

Location: `%APPDATA%\Claude\claude_desktop_config.json`

### Mac/Linux

```json
{
  "mcpServers": {
    "coretext": {
      "command": "node",
      "args": ["/home/user/github/coretext-mcp/src/index.js"]
    }
  }
}
```

Location: `~/Library/Application Support/Claude/claude_desktop_config.json`

## 🚢 Production Deployment

### Azure Container Apps

```bash
# Build container
docker build -t coretext-mcp .

# Push to Azure Container Registry
az acr build --registry myregistry --image coretext-mcp .

# Deploy to Container Apps
az containerapp create \
  --name coretext-mcp \
  --resource-group mygroup \
  --image myregistry.azurecr.io/coretext-mcp \
  --environment myenvironment
```

### Cosmos DB Integration

Replace the file-based MemoryManager with:

```javascript
// Use @azure/cosmos SDK
const { CosmosClient } = require("@azure/cosmos");
// Store memories in Cosmos DB instead of JSON file
```

## 📊 Teaching Points

### 1. Context Window Problems

- Tokens are expensive and limited
- Copy-paste doesn't scale
- AI forgets between sessions

### 2. MCP Solution

- Universal protocol for context
- Tool-based memory access
- Persistent across sessions

### 3. Enterprise Patterns

- Authentication (API keys)
- Structured data (CRUD)
- Cloud-ready architecture

### 4. Memory Architecture

- Episodic: Timeline-based
- Semantic: Knowledge-based
- Vector: Similarity-based (future)

## 🎓 Course Integration

This server demonstrates all concepts from:

- **Segment 1**: MCP basics and context loss
- **Segment 2**: GitHub + MCP integration patterns
- **Segment 3**: Multi-agent memory systems
- **Segment 4**: Production deployment

## 🛠️ VS Code Workflow

1. Open in VS Code
2. Install recommended extensions
3. Use MCP Inspector for debugging
4. Deploy to Azure via VS Code Azure extension

## 📈 Performance Metrics

- Memory operations: < 10ms
- Search latency: < 50ms  
- Storage: 100MB JSON limit (local)
- Cosmos DB: Unlimited scale

## ☁️ Azure Deployment

**MVP Production Deployment (~$3-10/month)**

Deploy to Azure with cost-optimized infrastructure:

- Cosmos DB Free Tier (1000 RU/s, 25GB)
- Container Apps (scales to zero)
- Key Vault for secrets
- Managed Identity authentication

```bash
cd azure
./deploy.sh
```

**Full documentation**: See [azure/README.md](azure/README.md)

## 🔒 Security Considerations

- API keys in environment variables
- No sensitive data in JSON storage
- Azure Key Vault for production
- Role-based access control ready

## 📝 License

MIT - Use freely for teaching and learning

## 👨‍💻 Author

**Tim Warner**  
Microsoft MVP | O'Reilly Instructor  
[TechTrainerTim.com](https://techtrainertim.com)

---

*Built for the O'Reilly Live Training: "Context Engineering with MCP"*
