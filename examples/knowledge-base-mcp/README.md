# Knowledge Base MCP Server (Remote - Azure)

A remote MCP (Model Context Protocol) server for knowledge base management with document storage, search, and Azure Container Apps deployment support.

## Overview

This MCP server provides AI assistants with the ability to store, retrieve, and search documents through a remote HTTP/SSE interface. It's designed for production deployment on Azure Container Apps with built-in authentication, CORS support, and containerization.

### Use Cases

- Centralized knowledge management for teams
- Document storage accessible from multiple AI clients
- Production-ready remote MCP server reference
- Learning remote MCP deployment patterns
- Azure Container Apps deployment example

## Features

### Document Management

- ✅ **CRUD Operations**: Create, read, update, delete documents
- 🔍 **Full-text Search**: Search across document titles and content
- 🏷️  **Tag-based Organization**: Organize and filter by tags
- 💾 **Persistent Storage**: JSON file-based storage (upgradeable to database)
- 📊 **Statistics**: View knowledge base metrics and recent activity
- 🌐 **Remote Access**: HTTP/SSE transport for network accessibility

### Production Features

- 🔐 **API Key Authentication**: Secure access with bearer tokens
- 🌍 **CORS Support**: Configurable for web clients
- 🐳 **Dockerized**: Multi-stage builds for optimization
- ☁️  **Azure-ready**: Bicep templates for Container Apps
- 💚 **Health Checks**: Built-in health monitoring
- 📝 **Logging**: Structured logging with Azure integration
- 📈 **Auto-scaling**: Scale to zero or high based on demand

### MCP Capabilities

- **6 Tools**: add_document, get_document, search_documents, update_document, delete_document, list_documents
- **3 Resources**: kb://documents, kb://tags, kb://stats
- **SSE Transport**: Server-Sent Events for remote communication
- **Caching**: In-memory document caching with TTL

## Installation

### Prerequisites

- Node.js 20 or higher
- Docker (for containerization)
- Azure CLI (for Azure deployment)
- Azure subscription (for cloud deployment)

### Local Development Setup

```bash
# Navigate to the knowledge base directory
cd examples/knowledge-base-mcp

# Install dependencies
npm install

# Run locally
npm run dev
```

The server will start on `http://localhost:3000`

### Test Health Endpoint

```bash
curl http://localhost:3000/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "knowledge-base-mcp",
  "version": "1.0.0",
  "timestamp": "2025-01-15T10:30:00.000Z"
}
```

## Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `PORT` | HTTP server port | `3000` | No |
| `API_KEY` | Authentication key | `dev-key-change-in-production` | Yes (production) |
| `DATA_DIR` | Document storage path | `./data` | No |
| `NODE_ENV` | Environment mode | `development` | No |

### Local Development

Create a `.env` file:

```env
PORT=3000
API_KEY=your-secret-api-key-here
DATA_DIR=./data
NODE_ENV=development
```

## Azure Deployment

### Quick Deploy

```bash
# Set environment variables
export RESOURCE_GROUP="kb-mcp-rg"
export LOCATION="eastus"
export ENVIRONMENT="dev"
export API_KEY="$(openssl rand -base64 32)"

# Run deployment script
chmod +x deploy/deploy.sh
./deploy/deploy.sh
```

### Manual Deployment Steps

#### 1. Build Docker Image

```bash
docker build -t knowledge-base-mcp:latest .
```

#### 2. Create Azure Container Registry

```bash
az acr create \
  --resource-group kb-mcp-rg \
  --name kbmcpacr \
  --sku Basic
```

#### 3. Push Image to ACR

```bash
az acr login --name kbmcpacr

docker tag knowledge-base-mcp:latest kbmcpacr.azurecr.io/knowledge-base-mcp:latest
docker push kbmcpacr.azurecr.io/knowledge-base-mcp:latest
```

#### 4. Deploy with Bicep

```bash
az deployment group create \
  --resource-group kb-mcp-rg \
  --template-file deploy/main.bicep \
  --parameters \
      environmentName=dev \
      apiKey="your-api-key" \
      containerRegistryName=kbmcpacr
```

#### 5. Get Service URL

```bash
az deployment group show \
  --resource-group kb-mcp-rg \
  --name main \
  --query properties.outputs.containerAppUrl.value -o tsv
```

## Usage

### Connecting from MCP Clients

#### Claude Desktop (Remote Server)

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "knowledge-base": {
      "url": "https://your-app.eastus.azurecontainerapps.io/sse",
      "transport": "sse",
      "headers": {
        "Authorization": "Bearer your-api-key-here"
      }
    }
  }
}
```

#### Cline (VS Code)

Add to your Cline MCP settings:

```json
{
  "knowledge-base": {
    "url": "https://your-app.eastus.azurecontainerapps.io/sse",
    "apiKey": "your-api-key-here"
  }
}
```

### Example Conversations

#### Adding a Document

```
User: Add a document about MCP best practices
AI: [Calls add_document tool]

✅ Document Added

📄 **MCP Best Practices** (doc_1234567890_abc123def)
   Tags: #mcp, #best-practices

Model Context Protocol (MCP) best practices include:
1. Use semantic versioning for tools
2. Implement proper error handling
3. Cache frequently accessed data
...

   Created: 1/15/2025, 10:30:00 AM
```

#### Searching Documents

```
User: Search for documents about Azure
AI: [Calls search_documents with query="Azure"]

**Search Results (query: "Azure")** (3 total)

📄 **Azure Deployment Guide** (doc_1234567891_xyz789abc)
   Tags: #azure, #deployment

📄 **MCP on Azure Container Apps** (doc_1234567892_def456ghi)
   Tags: #azure, #mcp

📄 **Azure Cost Optimization** (doc_1234567893_ghi789jkl)
   Tags: #azure, #costs
```

#### Viewing Statistics

```
User: Show me knowledge base statistics
AI: [Accesses kb://stats resource]

**Knowledge Base Statistics**

📊 Document Count: 47
🏷️  Unique Tags: 15
📝 Total Content: 125,430 characters
📏 Average Length: 2,669 characters per document

**Recent Activity**:
- Azure Deployment Guide (1/15/2025)
- MCP Best Practices (1/14/2025)
- TypeScript Patterns (1/13/2025)
```

## API Reference

### Tools

#### add_document

Add a new document to the knowledge base.

**Parameters:**
```typescript
{
  title: string;        // Required
  content: string;      // Required
  tags?: string[];      // Optional
}
```

**Example:**
```json
{
  "title": "Azure MCP Deployment",
  "content": "Step-by-step guide for deploying MCP servers to Azure...",
  "tags": ["azure", "deployment", "mcp"]
}
```

#### get_document

Retrieve a document by ID.

**Parameters:**
```typescript
{
  id: string;  // Required
}
```

#### search_documents

Search documents by content or tags.

**Parameters:**
```typescript
{
  query?: string;    // Search in title and content
  tags?: string[];   // Filter by tags
}
```

#### update_document

Update an existing document.

**Parameters:**
```typescript
{
  id: string;           // Required
  title?: string;       // Optional
  content?: string;     // Optional
  tags?: string[];      // Optional
}
```

#### delete_document

Delete a document.

**Parameters:**
```typescript
{
  id: string;  // Required
}
```

#### list_documents

List all documents with optional tag filter.

**Parameters:**
```typescript
{
  tags?: string[];  // Optional tag filter
}
```

### Resources

#### kb://documents

View all documents in the knowledge base.

#### kb://tags

View all unique tags across all documents.

#### kb://stats

View knowledge base statistics including document count, tags, and recent activity.

## Architecture

### Transport: HTTP/SSE

This server uses Server-Sent Events (SSE) for real-time communication:

- **Client → Server**: HTTP POST requests
- **Server → Client**: Server-Sent Events stream
- **Authentication**: Bearer token in Authorization header
- **CORS**: Configurable for cross-origin requests

### Storage

Documents are stored in a JSON file with in-memory caching:

- **Location**: `data/documents.json`
- **Cache TTL**: 5 seconds
- **Format**: Pretty-printed JSON
- **Upgradeable**: Replace with database for production scale

### Security

- ✅ API key authentication on all endpoints (except /health)
- ✅ Non-root user in Docker container
- ✅ Environment variables for secrets
- ✅ CORS configuration for web clients
- ✅ Health checks for monitoring

## Monitoring

### View Logs (Azure)

```bash
az containerapp logs show \
  --resource-group kb-mcp-rg \
  --name kb-mcp-dev-app \
  --follow
```

### View Metrics (Azure)

```bash
az monitor metrics list \
  --resource kb-mcp-dev-app \
  --resource-group kb-mcp-rg \
  --resource-type Microsoft.App/containerApps \
  --metric Requests
```

### Application Insights

The Bicep template includes Application Insights integration. View in Azure Portal:

1. Navigate to your Container App
2. Click "Application Insights"
3. View requests, failures, and performance

## Scaling

### Auto-scaling Configuration

The deployment includes auto-scaling rules:

- **Min Replicas**: 0 (dev), 1 (prod) - scale to zero when idle
- **Max Replicas**: 3 (dev), 10 (prod)
- **Trigger**: HTTP concurrent requests > 10

### Manual Scaling

```bash
az containerapp update \
  --resource-group kb-mcp-rg \
  --name kb-mcp-dev-app \
  --min-replicas 2 \
  --max-replicas 5
```

## Troubleshooting

### Connection Refused

**Error:** Cannot connect to server

**Solutions:**
```bash
# Check if server is running
curl https://your-app.azurecontainerapps.io/health

# Check Container App status
az containerapp show \
  --resource-group kb-mcp-rg \
  --name kb-mcp-dev-app \
  --query properties.runningStatus
```

### Authentication Failed

**Error:** 401 Unauthorized or 403 Forbidden

**Solution:** Verify API key is correct:
```bash
curl -H "Authorization: Bearer your-api-key" \
  https://your-app.azurecontainerapps.io/health
```

### Data Not Persisting

**Problem:** Documents disappear after restart

**Cause:** Container storage is ephemeral by default

**Solution:** Add persistent volume in Bicep template or migrate to Azure Cosmos DB

### High Latency

**Problem:** Slow response times

**Solutions:**
1. Check if scaling is needed
2. Review Application Insights for bottlenecks
3. Consider adding Cosmos DB for better performance
4. Enable caching at CDN/API Gateway level

## Cost Optimization

### Azure Costs (Monthly Estimates)

| Component | Free Tier | Light Use | Medium Use |
|-----------|-----------|-----------|------------|
| Container Apps | Yes (180K vCPU-s) | $5-10 | $20-40 |
| Log Analytics | 5GB free | $2-5 | $10-20 |
| Container Registry | $5 (Basic) | $5 | $5 |
| **Total** | ~$5 | ~$12-20 | ~$35-65 |

### Cost Reduction Tips

1. **Scale to Zero**: Enable in dev/staging (default in this template)
2. **Use Free Tiers**: Log Analytics has 5GB/month free
3. **Optimize Images**: Multi-stage builds reduce storage costs
4. **Monitor Usage**: Set up billing alerts

## Upgrading to Production

### Database Migration

Replace JSON file storage with Azure Cosmos DB:

1. Add Cosmos DB to Bicep template
2. Replace `loadDocuments()` and `saveDocuments()` with Cosmos SDK calls
3. Use partition keys for scalability
4. Update environment variables

### Add Redis Cache

For high-traffic scenarios:

1. Add Azure Cache for Redis
2. Implement caching layer before database
3. Set appropriate TTLs

### CDN Integration

For global distribution:

1. Add Azure Front Door or CDN
2. Configure caching rules
3. Set up custom domains

## Learning Objectives

This MCP server demonstrates:

1. **Remote MCP Architecture**: HTTP/SSE transport vs stdio
2. **Azure Deployment**: Container Apps with Bicep
3. **Authentication**: API key-based security
4. **Production Patterns**: Health checks, logging, scaling
5. **Containerization**: Multi-stage Docker builds
6. **Infrastructure as Code**: Bicep templates
7. **CI/CD Ready**: Suitable for GitHub Actions or Azure DevOps

## Related Examples

- **weather-api-mcp**: Local server with external API integration
- **task-manager-mcp**: Local server with file-based persistence
- **analytics-mcp**: Remote server with advanced querying
- **coretext-mcp**: Memory pattern implementation

## Next Steps

### Enhancements

- [ ] Add vector search for semantic document retrieval
- [ ] Implement document versioning
- [ ] Add collaborative editing capabilities
- [ ] Support document attachments
- [ ] Add export/import functionality
- [ ] Implement access control lists (ACLs)
- [ ] Add audit logging

### Production Checklist

- [ ] Replace default API key with secure secret
- [ ] Configure CORS for specific origins
- [ ] Set up Azure Key Vault for secrets
- [ ] Enable managed identity for ACR access
- [ ] Configure custom domain and SSL
- [ ] Set up monitoring alerts
- [ ] Implement backup strategy
- [ ] Add rate limiting
- [ ] Create disaster recovery plan

## Support

For issues or questions:

- Main course: [TROUBLESHOOTING_FAQ.md](../../TROUBLESHOOTING_FAQ.md)
- Setup guide: [STUDENT_SETUP_GUIDE.md](../../STUDENT_SETUP_GUIDE.md)
- Implementation guide: [IMPLEMENTATION_GUIDE.md](../../IMPLEMENTATION_GUIDE.md)
- MCP tutorials: [MCP_TUTORIALS.md](../../MCP_TUTORIALS.md)

## License

MIT License - See LICENSE file for details
