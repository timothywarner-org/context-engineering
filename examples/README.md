# MCP Server Examples

A collection of production-quality MCP (Model Context Protocol) server implementations demonstrating various patterns, deployment strategies, and use cases.

## Overview

This directory contains four complete MCP server implementations:

- **2 Local Servers** (stdio transport): Designed for local development and simple use cases
- **2 Remote Servers** (HTTP/SSE transport): Designed for Azure deployment and production use

Each example includes full documentation, deployment scripts, and production-ready code suitable for learning and adaptation.

---

## Local MCP Servers

### 1. Weather API MCP

**Directory:** `weather-api-mcp/`

**Purpose:** Demonstrates external API integration with caching and fallback patterns.

**Features:**
- OpenWeatherMap API integration
- Current weather, 5-day forecast, air quality data
- Response caching with TTL (10 minutes)
- Graceful fallback to stale cache on errors
- Human-readable output formatting

**Tools:**
- `get_current_weather` - Get current weather for a city
- `get_forecast` - Get 5-day weather forecast
- `get_air_quality` - Get air quality information

**Resources:**
- `weather://cache` - View cached weather data

**Use Cases:**
- Learning API integration patterns
- Understanding caching strategies
- Building weather-aware applications
- External data fetching with MCP

**Quick Start:**
```bash
cd weather-api-mcp
npm install
npm start
```

**Documentation:** See [weather-api-mcp/README.md](weather-api-mcp/README.md)

---

### 2. Task Manager MCP

**Directory:** `task-manager-mcp/`

**Purpose:** Demonstrates CRUD operations with file-based persistence.

**Features:**
- Create, read, update, delete tasks
- Status tracking (todo, in-progress, done)
- Priority levels (low, medium, high)
- Due date management with overdue detection
- JSON file persistence
- Task filtering and sorting

**Tools:**
- `create_task` - Create a new task
- `get_task` - Get a task by ID
- `update_task` - Update an existing task
- `delete_task` - Delete a task
- `list_tasks` - List all tasks with optional filters
- `complete_task` - Mark a task as complete

**Resources:**
- `tasks://all` - View all tasks
- `tasks://pending` - View pending tasks
- `tasks://completed` - View completed tasks

**Use Cases:**
- Learning CRUD patterns
- File-based persistence
- State management across sessions
- Building productivity tools

**Quick Start:**
```bash
cd task-manager-mcp
npm install
npm start
```

**Documentation:** See [task-manager-mcp/README.md](task-manager-mcp/README.md)

---

## Remote MCP Servers (Azure)

### 3. Knowledge Base MCP

**Directory:** `knowledge-base-mcp/`

**Purpose:** Demonstrates remote MCP server with document management and Azure deployment.

**Features:**
- Document CRUD operations
- Full-text search across documents
- Tag-based organization
- HTTP/SSE transport for remote access
- API key authentication
- Azure Container Apps deployment
- Dockerized with multi-stage builds
- Bicep infrastructure templates

**Tools:**
- `add_document` - Add a new document
- `get_document` - Retrieve a document by ID
- `search_documents` - Search documents by content or tags
- `update_document` - Update an existing document
- `delete_document` - Delete a document
- `list_documents` - List all documents with optional filtering

**Resources:**
- `kb://documents` - View all documents
- `kb://tags` - View all unique tags
- `kb://stats` - View knowledge base statistics

**Use Cases:**
- Centralized knowledge management
- Remote MCP server patterns
- Azure deployment learning
- Production MCP architecture
- Team collaboration with AI

**Quick Start (Local):**
```bash
cd knowledge-base-mcp
npm install
npm run dev
```

**Azure Deployment:**
```bash
cd knowledge-base-mcp
chmod +x deploy/deploy.sh
./deploy/deploy.sh
```

**Documentation:** See [knowledge-base-mcp/README.md](knowledge-base-mcp/README.md)

---

### 4. Analytics MCP

**Directory:** `analytics-mcp/`

**Purpose:** Demonstrates analytics, metrics tracking, and statistical reporting with Azure deployment.

**Features:**
- Event tracking with categories and values
- Time-series metrics aggregation (hour, day, week, month)
- Statistical analysis (mean, median, percentiles, std dev)
- Advanced queries with filters
- Comprehensive reporting
- HTTP/SSE transport for remote access
- API key authentication
- Azure Container Apps deployment

**Tools:**
- `track_event` - Record an analytics event
- `get_metrics` - Get aggregated metrics for a time range
- `get_report` - Generate comprehensive analytics report
- `query_events` - Query raw events with filters
- `get_stats` - Get statistical summaries

**Resources:**
- `analytics://events/recent` - View recent events
- `analytics://metrics/summary` - View metrics summary
- `analytics://dashboard` - View dashboard data

**Use Cases:**
- Application analytics and monitoring
- User behavior tracking
- Statistical analysis and reporting
- Time-series data patterns
- AI-powered insights

**Quick Start (Local):**
```bash
cd analytics-mcp
npm install
npm run dev
```

**Azure Deployment:**
```bash
cd analytics-mcp
chmod +x deploy/deploy.sh
./deploy/deploy.sh
```

**Documentation:** See [analytics-mcp/README.md](analytics-mcp/README.md)

---

## Comparison Matrix

| Feature | Weather API | Task Manager | Knowledge Base | Analytics |
|---------|------------|-------------|---------------|-----------|
| **Transport** | stdio (local) | stdio (local) | HTTP/SSE (remote) | HTTP/SSE (remote) |
| **Deployment** | Local | Local | Azure | Azure |
| **Persistence** | Cache (temp) | JSON file | JSON file | JSON file |
| **Authentication** | None | None | API Key | API Key |
| **Docker** | ❌ | ❌ | ✅ | ✅ |
| **Azure Bicep** | ❌ | ❌ | ✅ | ✅ |
| **Tools** | 3 | 6 | 6 | 5 |
| **Resources** | 1 | 3 | 3 | 3 |
| **Complexity** | ⭐⭐ Medium | ⭐⭐ Medium | ⭐⭐⭐ High | ⭐⭐⭐ High |

---

## Architecture Patterns

### Local Servers (stdio)

**Weather API MCP & Task Manager MCP**

- **Transport:** stdio (Standard Input/Output)
- **Communication:** Process-based, launched by MCP client
- **Authentication:** Not required (local trust)
- **Deployment:** NPM package or direct execution
- **Use Case:** Personal use, development, local tooling

**Architecture:**
```
MCP Client (Claude Desktop, Cline)
    ↓ spawns process
MCP Server (Node.js process)
    ↓ stdio communication
Tools & Resources
```

### Remote Servers (HTTP/SSE)

**Knowledge Base MCP & Analytics MCP**

- **Transport:** HTTP with Server-Sent Events
- **Communication:** Network-based, always running
- **Authentication:** API key required
- **Deployment:** Docker container on Azure Container Apps
- **Use Case:** Team collaboration, production systems, public APIs

**Architecture:**
```
MCP Client (Claude Desktop, Cline)
    ↓ HTTP requests + SSE
Load Balancer / API Gateway
    ↓
Container App (auto-scaled)
    ↓
MCP Server (Node.js + Express)
    ↓
Tools & Resources
```

---

## Technology Stack

### Common Dependencies

- **MCP SDK:** `@modelcontextprotocol/sdk` (v1.0.4+)
- **Node.js:** 20.0.0+
- **Package Manager:** npm

### Local Servers

- **Runtime:** Node.js with ES modules
- **Storage:** File system (fs/promises)
- **External APIs:** HTTPS module (weather-api-mcp)

### Remote Servers

- **HTTP Framework:** Express.js 4.18+
- **CORS:** cors 2.8+
- **Container:** Docker with multi-stage builds
- **Cloud:** Azure Container Apps
- **IaC:** Azure Bicep
- **Monitoring:** Azure Log Analytics + Application Insights

---

## Learning Path

### Beginner

1. **Start with:** `task-manager-mcp`
   - Simple CRUD operations
   - File-based storage
   - Clear separation of concerns
   - 6 tools to understand

2. **Then:** `weather-api-mcp`
   - External API integration
   - Caching patterns
   - Error handling
   - Real-world data fetching

### Intermediate

3. **Move to:** `knowledge-base-mcp`
   - Remote MCP server setup
   - HTTP/SSE transport
   - Authentication patterns
   - Basic Azure deployment
   - Dockerization

### Advanced

4. **Master:** `analytics-mcp`
   - Statistical computing
   - Time-series aggregation
   - Advanced querying
   - Production deployment
   - Complete Azure infrastructure

---

## Deployment Comparison

### Local Deployment

**Weather API MCP & Task Manager MCP**

```bash
# Install
npm install

# Configure (optional)
export OPENWEATHER_API_KEY=your-key  # weather-api-mcp only

# Run
npm start

# Add to Claude Desktop config
{
  "mcpServers": {
    "server-name": {
      "command": "node",
      "args": ["/absolute/path/to/src/index.js"]
    }
  }
}
```

### Azure Deployment

**Knowledge Base MCP & Analytics MCP**

```bash
# Prerequisites
- Azure CLI installed
- Docker installed
- Azure subscription

# Deploy
cd examples/{knowledge-base-mcp|analytics-mcp}
export RESOURCE_GROUP="mcp-rg"
export API_KEY="$(openssl rand -base64 32)"
./deploy/deploy.sh

# Add to Claude Desktop config
{
  "mcpServers": {
    "server-name": {
      "url": "https://your-app.azurecontainerapps.io/sse",
      "transport": "sse",
      "headers": {
        "Authorization": "Bearer your-api-key"
      }
    }
  }
}
```

---

## Cost Considerations

### Local Servers

- **Cost:** $0 (runs on your machine)
- **Resources:** Minimal (< 100MB RAM per server)
- **Scaling:** Limited to single machine

### Remote Servers (Azure)

**Monthly Estimates:**

| Component | Dev | Production |
|-----------|-----|-----------|
| Container Apps | $5-10 | $20-50 |
| Log Analytics | $2-5 | $10-20 |
| Container Registry | $5 | $5-10 |
| **Total** | **$12-20** | **$35-80** |

**Cost Optimization:**
- Scale to zero in dev (default in templates)
- Use free tier Log Analytics (5GB/month)
- Share Container Registry across projects
- Set up billing alerts

---

## Security Best Practices

### Local Servers

- ✅ Workspace sandboxing (implicit via process isolation)
- ✅ Input validation
- ✅ No network exposure
- ⚠️ API keys in environment variables only

### Remote Servers

- ✅ API key authentication
- ✅ CORS configuration
- ✅ Non-root Docker user
- ✅ HTTPS/TLS (via Azure)
- ✅ Environment variables for secrets
- ✅ Health check endpoints
- ⚠️ Consider Azure Key Vault for production
- ⚠️ Implement rate limiting for public APIs

---

## Extending the Examples

### Upgrade JSON Storage to Database

All examples use JSON file storage for simplicity. For production:

**Option 1: Azure Cosmos DB**
```javascript
import { CosmosClient } from '@azure/cosmos';

const client = new CosmosClient({
  endpoint: process.env.COSMOS_ENDPOINT,
  key: process.env.COSMOS_KEY
});

const container = client.database('mcp-db').container('documents');

async function loadDocuments() {
  const { resources } = await container.items.readAll().fetchAll();
  return resources;
}
```

**Option 2: PostgreSQL**
```javascript
import pg from 'pg';
const { Pool } = pg;

const pool = new Pool({
  connectionString: process.env.DATABASE_URL
});

async function loadDocuments() {
  const { rows } = await pool.query('SELECT * FROM documents');
  return rows;
}
```

### Add Vector Search

For semantic search in knowledge base:

```bash
npm install @azure/search-documents
```

```javascript
import { SearchClient, AzureKeyCredential } from '@azure/search-documents';

const client = new SearchClient(
  process.env.SEARCH_ENDPOINT,
  'documents',
  new AzureKeyCredential(process.env.SEARCH_KEY)
);

async function semanticSearch(query) {
  const results = await client.search(query, {
    select: ['id', 'title', 'content'],
    top: 10
  });
  return results.results;
}
```

---

## Troubleshooting

### Common Issues

**1. Module not found errors**
```bash
# Solution: Install dependencies
npm install
```

**2. Port already in use**
```bash
# Solution: Change port
PORT=3002 npm start
```

**3. API key errors (remote servers)**
```bash
# Solution: Set API key
export API_KEY="your-key-here"
npm start
```

**4. Azure deployment fails**
```bash
# Solution: Check Azure CLI login
az login
az account show
```

### Getting Help

- Main course documentation: [../../README.md](../../README.md)
- Troubleshooting guide: [../../TROUBLESHOOTING_FAQ.md](../../TROUBLESHOOTING_FAQ.md)
- Setup guide: [../../STUDENT_SETUP_GUIDE.md](../../STUDENT_SETUP_GUIDE.md)
- Implementation guide: [../../IMPLEMENTATION_GUIDE.md](../../IMPLEMENTATION_GUIDE.md)

---

## Contributing

Found a bug or have an improvement? These examples are part of the "MCP in Practice" training course. Contributions are welcome:

1. Test your changes thoroughly
2. Update documentation
3. Follow existing code style
4. Submit issues or pull requests

---

## License

MIT License - See LICENSE file for details

---

**Last Updated:** January 2025

**Maintained by:** MCP in Practice Training Course

**Related Resources:**
- [MCP Tutorials](../../MCP_TUTORIALS.md)
- [Popular Remote MCP Servers](../../POPULAR_REMOTE_MCP_SERVERS.md)
- [Post-Course Resources](../../POST_COURSE_RESOURCES.md)
