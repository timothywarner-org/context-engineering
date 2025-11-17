#!/usr/bin/env node

/**
 * Analytics MCP Server (Remote - Azure Deployment)
 *
 * A remote MCP server demonstrating analytics, metrics tracking, and reporting.
 * Designed for Azure Container Apps deployment with SSE (Server-Sent Events) transport.
 *
 * Features:
 * - Event tracking and logging
 * - Time-series metrics aggregation
 * - Statistical analysis and reporting
 * - HTTP/SSE transport for remote access
 * - Azure-ready with environment configuration
 * - API key authentication
 * - Real-time analytics queries
 *
 * Tools:
 * - track_event: Record an analytics event
 * - get_metrics: Get aggregated metrics for a time range
 * - get_report: Generate analytics report
 * - query_events: Query raw events with filters
 * - get_stats: Get statistical summaries
 *
 * Resources:
 * - analytics://events/recent: View recent events
 * - analytics://metrics/summary: View metrics summary
 * - analytics://dashboard: View dashboard data
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { SSEServerTransport } from '@modelcontextprotocol/sdk/server/sse.js';
import express from 'express';
import cors from 'cors';
import { promises as fs } from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Configuration
const PORT = process.env.PORT || 3001;
const API_KEY = process.env.API_KEY || 'dev-key-change-in-production';
const DATA_DIR = process.env.DATA_DIR || path.join(__dirname, '..', 'data');
const EVENTS_FILE = path.join(DATA_DIR, 'events.json');

// In-memory cache
let eventsCache = null;
let cacheTimestamp = null;
const CACHE_TTL = 5000; // 5 seconds

/**
 * Ensure data directory exists
 */
async function ensureDataDirectory() {
  try {
    await fs.mkdir(DATA_DIR, { recursive: true });
  } catch (error) {
    console.error('[Error] Failed to create data directory:', error.message);
    throw error;
  }
}

/**
 * Load events from file with caching
 */
async function loadEvents() {
  const now = Date.now();

  if (eventsCache && cacheTimestamp && (now - cacheTimestamp < CACHE_TTL)) {
    return eventsCache;
  }

  try {
    await ensureDataDirectory();
    const data = await fs.readFile(EVENTS_FILE, 'utf-8');
    eventsCache = JSON.parse(data);
    cacheTimestamp = now;
    return eventsCache;
  } catch (error) {
    if (error.code === 'ENOENT') {
      eventsCache = [];
      cacheTimestamp = now;
      return eventsCache;
    }
    console.error('[Error] Failed to load events:', error.message);
    throw error;
  }
}

/**
 * Save events to file and invalidate cache
 */
async function saveEvents(events) {
  try {
    await ensureDataDirectory();
    await fs.writeFile(EVENTS_FILE, JSON.stringify(events, null, 2), 'utf-8');
    eventsCache = events;
    cacheTimestamp = Date.now();
  } catch (error) {
    console.error('[Error] Failed to save events:', error.message);
    throw error;
  }
}

/**
 * Generate event ID
 */
function generateId() {
  return `evt_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}

/**
 * Filter events by date range and criteria
 */
function filterEvents(events, filters = {}) {
  let filtered = events;

  if (filters.startDate) {
    const start = new Date(filters.startDate);
    filtered = filtered.filter(e => new Date(e.timestamp) >= start);
  }

  if (filters.endDate) {
    const end = new Date(filters.endDate);
    filtered = filtered.filter(e => new Date(e.timestamp) <= end);
  }

  if (filters.eventType) {
    filtered = filtered.filter(e => e.type === filters.eventType);
  }

  if (filters.category) {
    filtered = filtered.filter(e => e.category === filters.category);
  }

  return filtered;
}

/**
 * Aggregate metrics from events
 */
function aggregateMetrics(events, groupBy = 'day') {
  const metrics = {};

  events.forEach(event => {
    const date = new Date(event.timestamp);
    let key;

    switch (groupBy) {
      case 'hour':
        key = date.toISOString().substring(0, 13) + ':00:00.000Z';
        break;
      case 'day':
        key = date.toISOString().substring(0, 10);
        break;
      case 'week':
        const weekStart = new Date(date);
        weekStart.setDate(date.getDate() - date.getDay());
        key = weekStart.toISOString().substring(0, 10);
        break;
      case 'month':
        key = date.toISOString().substring(0, 7);
        break;
      default:
        key = date.toISOString().substring(0, 10);
    }

    if (!metrics[key]) {
      metrics[key] = {
        period: key,
        count: 0,
        byType: {},
        byCategory: {},
        values: []
      };
    }

    metrics[key].count++;

    // Count by type
    if (!metrics[key].byType[event.type]) {
      metrics[key].byType[event.type] = 0;
    }
    metrics[key].byType[event.type]++;

    // Count by category
    if (event.category) {
      if (!metrics[key].byCategory[event.category]) {
        metrics[key].byCategory[event.category] = 0;
      }
      metrics[key].byCategory[event.category]++;
    }

    // Collect numeric values
    if (event.value !== undefined && typeof event.value === 'number') {
      metrics[key].values.push(event.value);
    }
  });

  // Calculate statistics for each period
  Object.values(metrics).forEach(metric => {
    if (metric.values.length > 0) {
      metric.statistics = calculateStatistics(metric.values);
    }
    delete metric.values; // Remove raw values from output
  });

  return metrics;
}

/**
 * Calculate statistical summary
 */
function calculateStatistics(values) {
  if (values.length === 0) return null;

  const sorted = [...values].sort((a, b) => a - b);
  const sum = values.reduce((a, b) => a + b, 0);
  const mean = sum / values.length;

  // Calculate variance and standard deviation
  const variance = values.reduce((acc, val) => acc + Math.pow(val - mean, 2), 0) / values.length;
  const stdDev = Math.sqrt(variance);

  return {
    count: values.length,
    sum: sum,
    mean: mean,
    min: sorted[0],
    max: sorted[sorted.length - 1],
    median: sorted[Math.floor(sorted.length / 2)],
    stdDev: stdDev,
    p25: sorted[Math.floor(sorted.length * 0.25)],
    p75: sorted[Math.floor(sorted.length * 0.75)],
    p95: sorted[Math.floor(sorted.length * 0.95)],
    p99: sorted[Math.floor(sorted.length * 0.99)]
  };
}

/**
 * Format metrics for display
 */
function formatMetrics(metrics) {
  let output = '**📊 Metrics Summary**\n\n';

  const periods = Object.keys(metrics).sort();

  periods.forEach(period => {
    const metric = metrics[period];
    output += `**${period}**\n`;
    output += `  Total Events: ${metric.count}\n`;

    if (Object.keys(metric.byType).length > 0) {
      output += `  By Type:\n`;
      Object.entries(metric.byType)
        .sort((a, b) => b[1] - a[1])
        .forEach(([type, count]) => {
          output += `    - ${type}: ${count}\n`;
        });
    }

    if (metric.statistics) {
      output += `  Statistics:\n`;
      output += `    - Mean: ${metric.statistics.mean.toFixed(2)}\n`;
      output += `    - Median: ${metric.statistics.median.toFixed(2)}\n`;
      output += `    - Min/Max: ${metric.statistics.min.toFixed(2)} / ${metric.statistics.max.toFixed(2)}\n`;
      output += `    - Std Dev: ${metric.statistics.stdDev.toFixed(2)}\n`;
    }

    output += '\n';
  });

  return output;
}

/**
 * Format events list
 */
function formatEvents(events, limit = 50) {
  if (events.length === 0) {
    return 'No events found.';
  }

  let output = `**Recent Events** (showing ${Math.min(limit, events.length)} of ${events.length})\n\n`;

  events.slice(0, limit).forEach(event => {
    const date = new Date(event.timestamp);
    output += `📌 **${event.type}** (${event.id})\n`;
    output += `   Time: ${date.toLocaleString()}\n`;

    if (event.category) {
      output += `   Category: ${event.category}\n`;
    }

    if (event.value !== undefined) {
      output += `   Value: ${event.value}\n`;
    }

    if (event.metadata && Object.keys(event.metadata).length > 0) {
      output += `   Metadata: ${JSON.stringify(event.metadata)}\n`;
    }

    output += '\n';
  });

  return output;
}

/**
 * Create and configure MCP server
 */
function createMCPServer() {
  const server = new Server(
    {
      name: 'analytics-mcp',
      version: '1.0.0'
    },
    {
      capabilities: {
        tools: {},
        resources: {}
      }
    }
  );

  // ==========================================================================
  // TOOL: track_event
  // ==========================================================================

  server.tool(
    'track_event',
    'Record an analytics event',
    {
      type: 'object',
      properties: {
        type: {
          type: 'string',
          description: 'Event type (e.g., page_view, click, conversion)'
        },
        category: {
          type: 'string',
          description: 'Event category (optional)'
        },
        value: {
          type: 'number',
          description: 'Numeric value associated with event (optional)'
        },
        metadata: {
          type: 'object',
          description: 'Additional metadata (optional)'
        }
      },
      required: ['type']
    },
    async ({ type, category, value, metadata }) => {
      try {
        console.log(`[Tool] track_event: ${type}`);

        const event = {
          id: generateId(),
          type: type,
          category: category || null,
          value: value !== undefined ? value : null,
          metadata: metadata || {},
          timestamp: new Date().toISOString()
        };

        const events = await loadEvents();
        events.push(event);
        await saveEvents(events);

        console.log(`[Success] Event tracked: ${event.id}`);

        return {
          content: [{
            type: 'text',
            text: `✅ **Event Tracked**\n\nID: ${event.id}\nType: ${event.type}\nTimestamp: ${new Date(event.timestamp).toLocaleString()}`
          }]
        };
      } catch (error) {
        console.error(`[Error] track_event: ${error.message}`);
        return {
          content: [{
            type: 'text',
            text: `❌ Failed to track event: ${error.message}`
          }],
          isError: true
        };
      }
    }
  );

  // ==========================================================================
  // TOOL: get_metrics
  // ==========================================================================

  server.tool(
    'get_metrics',
    'Get aggregated metrics for a time range',
    {
      type: 'object',
      properties: {
        startDate: {
          type: 'string',
          description: 'Start date (ISO 8601 format)'
        },
        endDate: {
          type: 'string',
          description: 'End date (ISO 8601 format)'
        },
        groupBy: {
          type: 'string',
          enum: ['hour', 'day', 'week', 'month'],
          description: 'Aggregation period (default: day)'
        },
        eventType: {
          type: 'string',
          description: 'Filter by event type (optional)'
        }
      }
    },
    async ({ startDate, endDate, groupBy, eventType }) => {
      try {
        console.log(`[Tool] get_metrics: ${startDate || 'all'} to ${endDate || 'now'}`);

        const events = await loadEvents();
        const filtered = filterEvents(events, { startDate, endDate, eventType });
        const metrics = aggregateMetrics(filtered, groupBy || 'day');

        return {
          content: [{
            type: 'text',
            text: formatMetrics(metrics)
          }]
        };
      } catch (error) {
        console.error(`[Error] get_metrics: ${error.message}`);
        return {
          content: [{
            type: 'text',
            text: `❌ Failed to get metrics: ${error.message}`
          }],
          isError: true
        };
      }
    }
  );

  // ==========================================================================
  // TOOL: get_report
  // ==========================================================================

  server.tool(
    'get_report',
    'Generate comprehensive analytics report',
    {
      type: 'object',
      properties: {
        startDate: {
          type: 'string',
          description: 'Start date (ISO 8601 format)'
        },
        endDate: {
          type: 'string',
          description: 'End date (ISO 8601 format)'
        }
      }
    },
    async ({ startDate, endDate }) => {
      try {
        console.log(`[Tool] get_report: ${startDate || 'all'} to ${endDate || 'now'}`);

        const events = await loadEvents();
        const filtered = filterEvents(events, { startDate, endDate });

        // Calculate overall statistics
        const numericEvents = filtered.filter(e => e.value !== undefined);
        const values = numericEvents.map(e => e.value);
        const stats = values.length > 0 ? calculateStatistics(values) : null;

        // Count by type and category
        const byType = {};
        const byCategory = {};

        filtered.forEach(event => {
          byType[event.type] = (byType[event.type] || 0) + 1;
          if (event.category) {
            byCategory[event.category] = (byCategory[event.category] || 0) + 1;
          }
        });

        let report = `**📈 Analytics Report**\n\n`;
        report += `**Period**: ${startDate || 'All time'} to ${endDate || 'Now'}\n`;
        report += `**Total Events**: ${filtered.length}\n\n`;

        report += `**By Event Type**:\n`;
        Object.entries(byType)
          .sort((a, b) => b[1] - a[1])
          .forEach(([type, count]) => {
            report += `  - ${type}: ${count} (${((count / filtered.length) * 100).toFixed(1)}%)\n`;
          });

        if (Object.keys(byCategory).length > 0) {
          report += `\n**By Category**:\n`;
          Object.entries(byCategory)
            .sort((a, b) => b[1] - a[1])
            .forEach(([category, count]) => {
              report += `  - ${category}: ${count}\n`;
            });
        }

        if (stats) {
          report += `\n**Value Statistics** (${stats.count} events with values):\n`;
          report += `  - Mean: ${stats.mean.toFixed(2)}\n`;
          report += `  - Median: ${stats.median.toFixed(2)}\n`;
          report += `  - Range: ${stats.min.toFixed(2)} - ${stats.max.toFixed(2)}\n`;
          report += `  - Std Dev: ${stats.stdDev.toFixed(2)}\n`;
          report += `  - 95th percentile: ${stats.p95.toFixed(2)}\n`;
        }

        return {
          content: [{
            type: 'text',
            text: report
          }]
        };
      } catch (error) {
        console.error(`[Error] get_report: ${error.message}`);
        return {
          content: [{
            type: 'text',
            text: `❌ Failed to generate report: ${error.message}`
          }],
          isError: true
        };
      }
    }
  );

  // ==========================================================================
  // TOOL: query_events
  // ==========================================================================

  server.tool(
    'query_events',
    'Query raw events with filters',
    {
      type: 'object',
      properties: {
        startDate: {
          type: 'string',
          description: 'Start date (ISO 8601 format)'
        },
        endDate: {
          type: 'string',
          description: 'End date (ISO 8601 format)'
        },
        eventType: {
          type: 'string',
          description: 'Filter by event type'
        },
        category: {
          type: 'string',
          description: 'Filter by category'
        },
        limit: {
          type: 'number',
          description: 'Maximum number of events to return (default: 50)'
        }
      }
    },
    async ({ startDate, endDate, eventType, category, limit }) => {
      try {
        console.log(`[Tool] query_events`);

        const events = await loadEvents();
        const filtered = filterEvents(events, { startDate, endDate, eventType, category });

        // Sort by timestamp descending (most recent first)
        filtered.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));

        return {
          content: [{
            type: 'text',
            text: formatEvents(filtered, limit || 50)
          }]
        };
      } catch (error) {
        console.error(`[Error] query_events: ${error.message}`);
        return {
          content: [{
            type: 'text',
            text: `❌ Failed to query events: ${error.message}`
          }],
          isError: true
        };
      }
    }
  );

  // ==========================================================================
  // TOOL: get_stats
  // ==========================================================================

  server.tool(
    'get_stats',
    'Get statistical summary of events',
    {
      type: 'object',
      properties: {
        eventType: {
          type: 'string',
          description: 'Filter by event type (optional)'
        }
      }
    },
    async ({ eventType }) => {
      try {
        console.log(`[Tool] get_stats: type=${eventType || 'all'}`);

        const events = await loadEvents();
        const filtered = eventType ? events.filter(e => e.type === eventType) : events;

        const numericEvents = filtered.filter(e => e.value !== undefined);
        const values = numericEvents.map(e => e.value);
        const stats = values.length > 0 ? calculateStatistics(values) : null;

        let output = `**📊 Statistical Summary**\n\n`;
        output += `Total Events: ${filtered.length}\n`;
        output += `Events with Values: ${numericEvents.length}\n\n`;

        if (stats) {
          output += `**Descriptive Statistics**:\n`;
          output += `  Count: ${stats.count}\n`;
          output += `  Sum: ${stats.sum.toFixed(2)}\n`;
          output += `  Mean: ${stats.mean.toFixed(2)}\n`;
          output += `  Median: ${stats.median.toFixed(2)}\n`;
          output += `  Min: ${stats.min.toFixed(2)}\n`;
          output += `  Max: ${stats.max.toFixed(2)}\n`;
          output += `  Std Dev: ${stats.stdDev.toFixed(2)}\n\n`;

          output += `**Percentiles**:\n`;
          output += `  25th: ${stats.p25.toFixed(2)}\n`;
          output += `  50th (median): ${stats.median.toFixed(2)}\n`;
          output += `  75th: ${stats.p75.toFixed(2)}\n`;
          output += `  95th: ${stats.p95.toFixed(2)}\n`;
          output += `  99th: ${stats.p99.toFixed(2)}\n`;
        } else {
          output += 'No numeric values found in events.';
        }

        return {
          content: [{
            type: 'text',
            text: output
          }]
        };
      } catch (error) {
        console.error(`[Error] get_stats: ${error.message}`);
        return {
          content: [{
            type: 'text',
            text: `❌ Failed to get statistics: ${error.message}`
          }],
          isError: true
        };
      }
    }
  );

  // ==========================================================================
  // RESOURCE: analytics://events/recent
  // ==========================================================================

  server.resource(
    'analytics://events/recent',
    'View recent events',
    async () => {
      console.log('[Resource] analytics://events/recent');

      const events = await loadEvents();
      const recent = events.slice(-100).reverse(); // Last 100 events, most recent first

      return {
        contents: [{
          uri: 'analytics://events/recent',
          mimeType: 'text/plain',
          text: formatEvents(recent, 100)
        }]
      };
    }
  );

  // ==========================================================================
  // RESOURCE: analytics://metrics/summary
  // ==========================================================================

  server.resource(
    'analytics://metrics/summary',
    'View metrics summary',
    async () => {
      console.log('[Resource] analytics://metrics/summary');

      const events = await loadEvents();
      const last30Days = new Date();
      last30Days.setDate(last30Days.getDate() - 30);

      const filtered = filterEvents(events, {
        startDate: last30Days.toISOString()
      });

      const metrics = aggregateMetrics(filtered, 'day');

      return {
        contents: [{
          uri: 'analytics://metrics/summary',
          mimeType: 'text/plain',
          text: formatMetrics(metrics)
        }]
      };
    }
  );

  // ==========================================================================
  // RESOURCE: analytics://dashboard
  // ==========================================================================

  server.resource(
    'analytics://dashboard',
    'View analytics dashboard',
    async () => {
      console.log('[Resource] analytics://dashboard');

      const events = await loadEvents();

      const today = new Date();
      const last7Days = new Date(today);
      last7Days.setDate(today.getDate() - 7);
      const last30Days = new Date(today);
      last30Days.setDate(today.getDate() - 30);

      const todayEvents = filterEvents(events, {
        startDate: today.toISOString().substring(0, 10)
      });

      const weekEvents = filterEvents(events, {
        startDate: last7Days.toISOString()
      });

      const monthEvents = filterEvents(events, {
        startDate: last30Days.toISOString()
      });

      let dashboard = `**📊 Analytics Dashboard**\n\n`;
      dashboard += `**Event Counts**:\n`;
      dashboard += `  Today: ${todayEvents.length}\n`;
      dashboard += `  Last 7 days: ${weekEvents.length}\n`;
      dashboard += `  Last 30 days: ${monthEvents.length}\n`;
      dashboard += `  All time: ${events.length}\n\n`;

      // Top event types
      const byType = {};
      events.forEach(e => {
        byType[e.type] = (byType[e.type] || 0) + 1;
      });

      const topTypes = Object.entries(byType)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 5);

      dashboard += `**Top Event Types** (all time):\n`;
      topTypes.forEach(([type, count]) => {
        dashboard += `  ${type}: ${count}\n`;
      });

      return {
        contents: [{
          uri: 'analytics://dashboard',
          mimeType: 'text/plain',
          text: dashboard
        }]
      };
    }
  );

  return server;
}

/**
 * Start HTTP server with SSE transport
 */
async function main() {
  console.log('📈 Starting Analytics MCP Server (Remote/Azure)...');
  console.log(`📡 Transport: HTTP/SSE`);
  console.log(`🔑 API Key: ${API_KEY === 'dev-key-change-in-production' ? '⚠️  Using default dev key' : '✅ Custom key set'}`);

  await ensureDataDirectory();

  const app = express();

  app.use(cors({
    origin: '*',
    methods: ['GET', 'POST', 'OPTIONS'],
    allowedHeaders: ['Content-Type', 'Authorization']
  }));

  app.use(express.json());

  const authenticateAPIKey = (req, res, next) => {
    const authHeader = req.headers.authorization;

    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return res.status(401).json({ error: 'Missing or invalid authorization header' });
    }

    const token = authHeader.substring(7);

    if (token !== API_KEY) {
      return res.status(403).json({ error: 'Invalid API key' });
    }

    next();
  };

  app.get('/health', (req, res) => {
    res.json({
      status: 'healthy',
      service: 'analytics-mcp',
      version: '1.0.0',
      timestamp: new Date().toISOString()
    });
  });

  app.post('/sse', authenticateAPIKey, async (req, res) => {
    console.log('[SSE] New connection request');

    const mcpServer = createMCPServer();
    const transport = new SSEServerTransport('/message', res);

    await mcpServer.connect(transport);

    console.log('[SSE] Client connected');
  });

  app.post('/message', authenticateAPIKey, async (req, res) => {
    res.status(200).send();
  });

  app.listen(PORT, () => {
    console.log(`✅ Analytics MCP Server ready`);
    console.log(`🌐 Listening on http://0.0.0.0:${PORT}`);
    console.log(`📍 SSE endpoint: POST /sse`);
    console.log(`💚 Health check: GET /health`);
    console.log(`📍 Registered tools: track_event, get_metrics, get_report, query_events, get_stats`);
    console.log(`📍 Registered resources: analytics://events/recent, analytics://metrics/summary, analytics://dashboard`);
  });
}

main().catch((error) => {
  console.error('❌ Fatal error:', error);
  process.exit(1);
});
