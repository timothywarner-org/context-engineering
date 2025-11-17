# Analytics MCP Server (Remote - Azure)

A remote MCP (Model Context Protocol) server for analytics, metrics tracking, and statistical reporting with Azure Container Apps deployment support.

## Overview

This MCP server provides AI assistants with the ability to track events, aggregate metrics, and generate statistical reports through a remote HTTP/SSE interface. It demonstrates production-ready analytics patterns with Azure deployment capabilities.

### Use Cases

- Event tracking for applications and user interactions
- Real-time metrics aggregation and reporting
- Statistical analysis of time-series data
- AI-powered analytics queries and insights
- Learning remote MCP server patterns
- Production analytics infrastructure reference

## Features

### Analytics Capabilities

- ✅ **Event Tracking**: Record events with types, categories, and values
- 📊 **Metrics Aggregation**: Group by hour, day, week, or month
- 📈 **Statistical Analysis**: Mean, median, percentiles, standard deviation
- 🔍 **Advanced Queries**: Filter by date range, event type, category
- 📝 **Comprehensive Reports**: Generate detailed analytics summaries
- ⏱️  **Time-series Data**: Track trends over time

### Production Features

- 🌐 **Remote Access**: HTTP/SSE transport for network accessibility
- 🔐 **API Key Authentication**: Secure access with bearer tokens
- 🌍 **CORS Support**: Configurable for web clients
- 🐳 **Dockerized**: Multi-stage builds for optimization
- ☁️  **Azure-ready**: Bicep templates for Container Apps
- 💚 **Health Checks**: Built-in health monitoring
- 📝 **Logging**: Structured logging with Azure integration
- 📈 **Auto-scaling**: Scale based on demand

### MCP Capabilities

- **5 Tools**: track_event, get_metrics, get_report, query_events, get_stats
- **3 Resources**: analytics://events/recent, analytics://metrics/summary, analytics://dashboard
- **SSE Transport**: Server-Sent Events for remote communication
- **In-memory Caching**: 5-second TTL for performance

## Installation

### Prerequisites

- Node.js 20 or higher
- Docker (for containerization)
- Azure CLI (for Azure deployment)
- Azure subscription (for cloud deployment)

### Local Development Setup

```bash
# Navigate to the analytics directory
cd examples/analytics-mcp

# Install dependencies
npm install

# Run locally
npm run dev
```

The server will start on `http://localhost:3001`

### Test Health Endpoint

```bash
curl http://localhost:3001/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "analytics-mcp",
  "version": "1.0.0",
  "timestamp": "2025-01-15T10:30:00.000Z"
}
```

## Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `PORT` | HTTP server port | `3001` | No |
| `API_KEY` | Authentication key | `dev-key-change-in-production` | Yes (production) |
| `DATA_DIR` | Event storage path | `./data` | No |
| `NODE_ENV` | Environment mode | `development` | No |

### Local Development

Create a `.env` file:

```env
PORT=3001
API_KEY=your-secret-api-key-here
DATA_DIR=./data
NODE_ENV=development
```

## Azure Deployment

### Quick Deploy

```bash
# Set environment variables
export RESOURCE_GROUP="analytics-mcp-rg"
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
docker build -t analytics-mcp:latest .
```

#### 2. Create Azure Container Registry

```bash
az acr create \
  --resource-group analytics-mcp-rg \
  --name analyticsmcpacr \
  --sku Basic
```

#### 3. Push Image to ACR

```bash
az acr login --name analyticsmcpacr

docker tag analytics-mcp:latest analyticsmcpacr.azurecr.io/analytics-mcp:latest
docker push analyticsmcpacr.azurecr.io/analytics-mcp:latest
```

#### 4. Deploy with Bicep

```bash
az deployment group create \
  --resource-group analytics-mcp-rg \
  --template-file deploy/main.bicep \
  --parameters \
      environmentName=dev \
      apiKey="your-api-key" \
      containerRegistryName=analyticsmcpacr
```

#### 5. Get Service URL

```bash
az deployment group show \
  --resource-group analytics-mcp-rg \
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
    "analytics": {
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
  "analytics": {
    "url": "https://your-app.eastus.azurecontainerapps.io/sse",
    "apiKey": "your-api-key-here"
  }
}
```

### Example Conversations

#### Tracking Events

```
User: Track a page view event for the homepage
AI: [Calls track_event tool]

✅ Event Tracked

ID: evt_1234567890_abc123def
Type: page_view
Timestamp: 1/15/2025, 10:30:00 AM
```

#### Getting Metrics

```
User: Show me metrics for the last 7 days grouped by day
AI: [Calls get_metrics with startDate and groupBy="day"]

**📊 Metrics Summary**

**2025-01-09**
  Total Events: 142
  By Type:
    - page_view: 89
    - button_click: 35
    - form_submit: 18
  Statistics:
    - Mean: 23.50
    - Median: 20.00
    - Min/Max: 5.00 / 85.00
    - Std Dev: 15.23

**2025-01-10**
  Total Events: 198
  By Type:
    - page_view: 124
    - button_click: 52
    - form_submit: 22
  Statistics:
    - Mean: 28.75
    - Median: 25.00
    - Min/Max: 8.00 / 95.00
    - Std Dev: 18.42

[continues...]
```

#### Generating Reports

```
User: Generate an analytics report for January
AI: [Calls get_report with date range]

**📈 Analytics Report**

**Period**: 2025-01-01 to 2025-01-31
**Total Events**: 4,523

**By Event Type**:
  - page_view: 2,845 (62.9%)
  - button_click: 1,123 (24.8%)
  - form_submit: 445 (9.8%)
  - download: 110 (2.4%)

**By Category**:
  - user-interaction: 3,201
  - conversion: 445
  - engagement: 877

**Value Statistics** (1,234 events with values):
  - Mean: 45.23
  - Median: 38.50
  - Range: 0.00 - 500.00
  - Std Dev: 32.15
  - 95th percentile: 125.00
```

#### Viewing Dashboard

```
User: Show me the analytics dashboard
AI: [Accesses analytics://dashboard resource]

**📊 Analytics Dashboard**

**Event Counts**:
  Today: 47
  Last 7 days: 892
  Last 30 days: 4,523
  All time: 12,847

**Top Event Types** (all time):
  page_view: 7,845
  button_click: 3,123
  form_submit: 1,445
  download: 434
  search: 890
```

## API Reference

### Tools

#### track_event

Record an analytics event.

**Parameters:**
```typescript
{
  type: string;         // Required (e.g., "page_view", "click", "conversion")
  category?: string;    // Optional (e.g., "user-interaction", "conversion")
  value?: number;       // Optional numeric value
  metadata?: object;    // Optional additional data
}
```

**Example:**
```json
{
  "type": "purchase",
  "category": "conversion",
  "value": 99.99,
  "metadata": {
    "product_id": "prod_123",
    "currency": "USD"
  }
}
```

#### get_metrics

Get aggregated metrics for a time range.

**Parameters:**
```typescript
{
  startDate?: string;    // ISO 8601 format
  endDate?: string;      // ISO 8601 format
  groupBy?: string;      // "hour" | "day" | "week" | "month"
  eventType?: string;    // Filter by event type
}
```

**Example:**
```json
{
  "startDate": "2025-01-01T00:00:00Z",
  "endDate": "2025-01-31T23:59:59Z",
  "groupBy": "day",
  "eventType": "page_view"
}
```

#### get_report

Generate comprehensive analytics report.

**Parameters:**
```typescript
{
  startDate?: string;    // ISO 8601 format
  endDate?: string;      // ISO 8601 format
}
```

#### query_events

Query raw events with filters.

**Parameters:**
```typescript
{
  startDate?: string;
  endDate?: string;
  eventType?: string;
  category?: string;
  limit?: number;        // Default: 50
}
```

#### get_stats

Get statistical summary of events.

**Parameters:**
```typescript
{
  eventType?: string;    // Filter by event type (optional)
}
```

### Resources

#### analytics://events/recent

View recent events (last 100).

#### analytics://metrics/summary

View metrics summary for the last 30 days grouped by day.

#### analytics://dashboard

View analytics dashboard with key metrics and top event types.

## Data Storage

Events are stored in `examples/analytics-mcp/data/events.json`.

### Event Schema

```json
{
  "id": "evt_1234567890_abc123def",
  "type": "page_view",
  "category": "user-interaction",
  "value": 1,
  "metadata": {
    "page": "/home",
    "user_agent": "Mozilla/5.0"
  },
  "timestamp": "2025-01-15T10:30:00.000Z"
}
```

## Architecture

### Statistical Analysis

The server implements comprehensive statistical calculations:

- **Descriptive Statistics**: count, sum, mean, median, min, max
- **Variability**: standard deviation, variance
- **Percentiles**: 25th, 50th (median), 75th, 95th, 99th
- **Aggregations**: Group by hour, day, week, or month
- **Filtering**: By date range, event type, category

### Performance

- **Caching**: 5-second TTL for event data
- **Memory Efficiency**: Streaming aggregations
- **Scalability**: Auto-scaling in Azure
- **Response Time**: <100ms for typical queries

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
  --resource-group analytics-mcp-rg \
  --name analytics-mcp-dev-app \
  --follow
```

### View Metrics (Azure)

```bash
az monitor metrics list \
  --resource analytics-mcp-dev-app \
  --resource-group analytics-mcp-rg \
  --resource-type Microsoft.App/containerApps \
  --metric Requests
```

### Application Insights

The Bicep template includes Application Insights integration for:

- Request tracking
- Failure analysis
- Performance monitoring
- Custom metrics

## Scaling

### Auto-scaling Configuration

- **Min Replicas**: 0 (dev), 1 (prod) - scale to zero when idle
- **Max Replicas**: 3 (dev), 10 (prod)
- **Trigger**: HTTP concurrent requests > 10

### Manual Scaling

```bash
az containerapp update \
  --resource-group analytics-mcp-rg \
  --name analytics-mcp-dev-app \
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
  --resource-group analytics-mcp-rg \
  --name analytics-mcp-dev-app \
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

**Problem:** Events disappear after restart

**Cause:** Container storage is ephemeral by default

**Solution:** Add persistent volume in Bicep template or migrate to Azure Cosmos DB

### Slow Aggregations

**Problem:** Slow metric calculations with many events

**Solutions:**
1. Migrate to time-series database (Azure Data Explorer, InfluxDB)
2. Implement pre-aggregation for common queries
3. Add caching layer with Redis
4. Use pagination for large result sets

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
5. **Data Retention**: Limit event retention period

## Upgrading to Production

### Database Migration

Replace JSON file storage with time-series database:

**Option 1: Azure Cosmos DB**
- Good for flexible schema
- Built-in partitioning and scaling
- TTL support for automatic cleanup

**Option 2: Azure Data Explorer (Kusto)**
- Optimized for time-series analytics
- Built-in aggregation functions
- Powerful query language (KQL)

**Option 3: InfluxDB on Azure**
- Purpose-built for time-series data
- High write throughput
- Built-in downsampling

### Add Redis Cache

For high-traffic scenarios:

1. Add Azure Cache for Redis
2. Cache aggregated metrics
3. Set appropriate TTLs (5-15 minutes)
4. Invalidate on new events

### Real-time Processing

For real-time analytics:

1. Add Azure Event Hubs or Service Bus
2. Implement event streaming
3. Use Azure Stream Analytics for aggregations
4. Store results in Cosmos DB or Redis

## Learning Objectives

This MCP server demonstrates:

1. **Remote MCP Architecture**: HTTP/SSE transport for remote access
2. **Statistical Computing**: Comprehensive statistical analysis
3. **Time-series Data**: Aggregation and trend analysis
4. **Azure Deployment**: Container Apps with full infrastructure
5. **Production Patterns**: Caching, monitoring, scaling
6. **Containerization**: Multi-stage Docker builds
7. **Infrastructure as Code**: Bicep templates for Azure

## Related Examples

- **weather-api-mcp**: Local server with external API integration
- **task-manager-mcp**: Local server with CRUD operations
- **knowledge-base-mcp**: Remote server with document management
- **coretext-mcp**: Memory pattern implementation

## Next Steps

### Enhancements

- [ ] Add real-time event streaming with WebSockets
- [ ] Implement custom dashboards and visualizations
- [ ] Add alerting for threshold breaches
- [ ] Support multiple data sources
- [ ] Add A/B test analysis capabilities
- [ ] Implement funnel analysis
- [ ] Add cohort analysis features
- [ ] Support custom metric definitions

### Production Checklist

- [ ] Replace default API key with secure secret
- [ ] Migrate to time-series database
- [ ] Configure CORS for specific origins
- [ ] Set up Azure Key Vault for secrets
- [ ] Enable managed identity for ACR access
- [ ] Configure custom domain and SSL
- [ ] Set up monitoring alerts
- [ ] Implement data retention policies
- [ ] Add rate limiting
- [ ] Create disaster recovery plan
- [ ] Implement backup strategy

## Support

For issues or questions:

- Main course: [TROUBLESHOOTING_FAQ.md](../../TROUBLESHOOTING_FAQ.md)
- Setup guide: [STUDENT_SETUP_GUIDE.md](../../STUDENT_SETUP_GUIDE.md)
- Implementation guide: [IMPLEMENTATION_GUIDE.md](../../IMPLEMENTATION_GUIDE.md)
- MCP tutorials: [MCP_TUTORIALS.md](../../MCP_TUTORIALS.md)

## License

MIT License - See LICENSE file for details
