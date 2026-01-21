/**
 * Schematica - Globomantics Robotics MCP Server
 *
 * A Model Context Protocol server that provides schematic lookup capabilities
 * for robotic components and assemblies.
 */

import express, { Request, Response } from 'express';
import { SchematicService } from './schematic-service';
import { authMiddleware } from './auth';
import { FetchSchematicParams, ListSchematicsParams } from './types';

const app = express();
const PORT = process.env.PORT || 3000;

// Initialize schematic service
const schematicService = new SchematicService();

// Middleware
app.use(express.json());
app.use(authMiddleware);

// Health check endpoint (public)
app.get('/health', (_req: Request, res: Response) => {
  res.json({
    status: 'healthy',
    service: 'schematica',
    version: '1.0.0',
    schematics_count: schematicService.getCount()
  });
});

// Root endpoint (public) - serves HTML for browsers, JSON for API clients
app.get('/', (req: Request, res: Response) => {
  const acceptsHtml = req.headers.accept?.includes('text/html');

  if (acceptsHtml) {
    const schematicsCount = schematicService.getCount();
    const categories = schematicService.getCategories();

    res.send(`
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Schematica | Globomantics Robotics MCP Server</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
      background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
      color: #ffffff;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
    }
    .container {
      max-width: 900px;
      margin: 0 auto;
      padding: 2rem;
      flex: 1;
    }
    header {
      text-align: center;
      padding: 3rem 0;
      border-bottom: 1px solid rgba(255,255,255,0.1);
      margin-bottom: 2rem;
    }
    .logo {
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 1rem;
      margin-bottom: 1rem;
    }
    .robot-icon {
      width: 80px;
      height: 80px;
      background: linear-gradient(180deg, #4ade80 0%, #22c55e 100%);
      border-radius: 12px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 2.5rem;
    }
    h1 {
      font-size: 2.5rem;
      font-weight: 700;
      margin-bottom: 0.5rem;
    }
    .subtitle {
      color: #9ca3af;
      font-size: 1.1rem;
    }
    .badge {
      display: inline-block;
      background: linear-gradient(90deg, #0f3460, #e94560);
      padding: 0.25rem 0.75rem;
      border-radius: 20px;
      font-size: 0.8rem;
      margin-top: 1rem;
    }
    .stats {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 1.5rem;
      margin: 2rem 0;
    }
    .stat-card {
      background: rgba(255,255,255,0.05);
      border: 1px solid rgba(255,255,255,0.1);
      border-radius: 12px;
      padding: 1.5rem;
      text-align: center;
    }
    .stat-value {
      font-size: 2.5rem;
      font-weight: 700;
      color: #4ade80;
    }
    .stat-label {
      color: #9ca3af;
      margin-top: 0.5rem;
    }
    .section {
      background: rgba(255,255,255,0.03);
      border: 1px solid rgba(255,255,255,0.1);
      border-radius: 12px;
      padding: 1.5rem;
      margin: 1.5rem 0;
    }
    .section h2 {
      font-size: 1.2rem;
      margin-bottom: 1rem;
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }
    .endpoint {
      background: rgba(0,0,0,0.3);
      border-radius: 8px;
      padding: 1rem;
      margin: 0.75rem 0;
      font-family: 'Monaco', 'Menlo', monospace;
      font-size: 0.9rem;
    }
    .method {
      display: inline-block;
      padding: 0.2rem 0.5rem;
      border-radius: 4px;
      font-size: 0.75rem;
      font-weight: 600;
      margin-right: 0.5rem;
    }
    .method-get { background: #22c55e; color: #000; }
    .method-post { background: #3b82f6; color: #fff; }
    .categories {
      display: flex;
      flex-wrap: wrap;
      gap: 0.5rem;
      margin-top: 0.5rem;
    }
    .category-tag {
      background: rgba(74, 222, 128, 0.2);
      border: 1px solid rgba(74, 222, 128, 0.3);
      color: #4ade80;
      padding: 0.25rem 0.75rem;
      border-radius: 20px;
      font-size: 0.85rem;
    }
    .tools-grid {
      display: grid;
      gap: 1rem;
      margin-top: 1rem;
    }
    .tool-card {
      background: rgba(0,0,0,0.2);
      border-radius: 8px;
      padding: 1rem;
    }
    .tool-name {
      color: #4ade80;
      font-family: 'Monaco', 'Menlo', monospace;
      font-weight: 600;
    }
    .tool-desc {
      color: #9ca3af;
      font-size: 0.9rem;
      margin-top: 0.5rem;
    }
    footer {
      text-align: center;
      padding: 2rem;
      border-top: 1px solid rgba(255,255,255,0.1);
      color: #6b7280;
      font-size: 0.9rem;
    }
    footer a {
      color: #4ade80;
      text-decoration: none;
    }
    footer a:hover {
      text-decoration: underline;
    }
    .status-indicator {
      display: inline-flex;
      align-items: center;
      gap: 0.5rem;
      background: rgba(34, 197, 94, 0.2);
      border: 1px solid rgba(34, 197, 94, 0.3);
      padding: 0.5rem 1rem;
      border-radius: 20px;
      font-size: 0.9rem;
    }
    .status-dot {
      width: 8px;
      height: 8px;
      background: #22c55e;
      border-radius: 50%;
      animation: pulse 2s infinite;
    }
    @keyframes pulse {
      0%, 100% { opacity: 1; }
      50% { opacity: 0.5; }
    }
  </style>
</head>
<body>
  <div class="container">
    <header>
      <div class="logo">
        <div class="robot-icon">&#129302;</div>
        <div>
          <h1>Schematica</h1>
          <div class="subtitle">Globomantics Robotics MCP Server</div>
        </div>
      </div>
      <div class="badge">Model Context Protocol v1.0</div>
      <div style="margin-top: 1.5rem;">
        <span class="status-indicator">
          <span class="status-dot"></span>
          Server Online
        </span>
      </div>
    </header>

    <div class="stats">
      <div class="stat-card">
        <div class="stat-value">${schematicsCount}</div>
        <div class="stat-label">Schematics Available</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">${categories.length}</div>
        <div class="stat-label">Component Categories</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">14</div>
        <div class="stat-label">Robot Model Series</div>
      </div>
    </div>

    <div class="section">
      <h2>&#128268; API Endpoints</h2>
      <div class="endpoint">
        <span class="method method-get">GET</span>
        <span>/health</span>
        <span style="color: #6b7280; margin-left: 1rem;">Health check (no auth required)</span>
      </div>
      <div class="endpoint">
        <span class="method method-post">POST</span>
        <span>/api/mcp</span>
        <span style="color: #6b7280; margin-left: 1rem;">MCP endpoint (Bearer token required)</span>
      </div>
    </div>

    <div class="section">
      <h2>&#128295; Available MCP Tools</h2>
      <div class="tools-grid">
        <div class="tool-card">
          <div class="tool-name">fetchSchematic</div>
          <div class="tool-desc">Fetch detailed schematic information using natural language queries like "cooling manifold for XR-18"</div>
        </div>
        <div class="tool-card">
          <div class="tool-name">listSchematics</div>
          <div class="tool-desc">List and filter schematics by category, model series, or status</div>
        </div>
      </div>
    </div>

    <div class="section">
      <h2>&#128193; Component Categories</h2>
      <div class="categories">
        ${categories.map(cat => '<span class="category-tag">' + cat + '</span>').join('')}
      </div>
    </div>

    <div class="section">
      <h2>&#128214; Quick Start</h2>
      <p style="color: #9ca3af; margin-bottom: 1rem;">Configure Schematica in your MCP client (e.g., Claude Desktop):</p>
      <div class="endpoint" style="white-space: pre; overflow-x: auto;">
{
  "mcpServers": {
    "schematica": {
      "url": "${req.protocol}://${req.get('host')}/api/mcp",
      "auth": {
        "type": "bearer",
        "token": "YOUR_API_KEY"
      }
    }
  }
}</div>
    </div>
  </div>

  <footer>
    <p><strong>Globomantics Robotics</strong> | Powering the future of intelligent automation</p>
    <p style="margin-top: 0.5rem;">
      <a href="/health">Health Check</a> &bull;
      <a href="https://github.com/timothywarner-org/schematica">GitHub</a> &bull;
      <a href="https://modelcontextprotocol.io">MCP Documentation</a>
    </p>
  </footer>
</body>
</html>
    `);
  } else {
    res.json({
      name: 'Schematica',
      description: 'Globomantics Robotics MCP Server - Schematic lookup service',
      version: '1.0.0',
      endpoints: {
        health: '/health',
        mcp: '/api/mcp'
      }
    });
  }
});

/**
 * MCP Tool Definitions
 */
const toolDefinitions = {
  fetchSchematic: {
    name: 'fetchSchematic',
    description: 'Fetch schematic information for a Globomantics robot component. Accepts natural language queries like "show me the cooling manifold schematic for XR-18" or explicit model/component parameters.',
    inputSchema: {
      type: 'object',
      properties: {
        query: {
          type: 'string',
          description: 'Natural language query describing the schematic you need (e.g., "cooling manifold for XR-18")'
        },
        model: {
          type: 'string',
          description: 'Optional: Explicit model number (e.g., "XR-18", "MK-9")'
        },
        component: {
          type: 'string',
          description: 'Optional: Explicit component name (e.g., "cooling manifold", "servo assembly")'
        }
      },
      required: ['query']
    }
  },
  listSchematics: {
    name: 'listSchematics',
    description: 'List available schematics in the Globomantics database. Can filter by category, model, or status.',
    inputSchema: {
      type: 'object',
      properties: {
        category: {
          type: 'string',
          description: 'Filter by category (thermal, motion, sensors, power, control, structural, manipulation)',
          enum: ['thermal', 'motion', 'sensors', 'power', 'control', 'structural', 'manipulation']
        },
        model: {
          type: 'string',
          description: 'Filter by model prefix or number (e.g., "XR", "XR-18")'
        },
        status: {
          type: 'string',
          description: 'Filter by status',
          enum: ['active', 'deprecated', 'draft']
        },
        limit: {
          type: 'number',
          description: 'Maximum number of results to return (default: 50, max: 100)',
          minimum: 1,
          maximum: 100
        }
      }
    }
  }
};

/**
 * MCP API Endpoint
 * Handles tool discovery and execution
 */
app.post('/api/mcp', (req: Request, res: Response) => {
  const { method, params } = req.body;

  switch (method) {
    case 'tools/list': {
      // Return available tools
      res.json({
        tools: Object.values(toolDefinitions)
      });
      break;
    }

    case 'tools/call': {
      const { name, arguments: args } = params || {};

      if (name === 'fetchSchematic') {
        const schematicParams: FetchSchematicParams = {
          query: args?.query || '',
          model: args?.model,
          component: args?.component
        };

        const result = schematicService.fetchSchematic(schematicParams);

        if (result) {
          res.json({
            content: [
              {
                type: 'text',
                text: JSON.stringify(result, null, 2)
              }
            ]
          });
        } else {
          res.json({
            content: [
              {
                type: 'text',
                text: 'No matching schematic found for the given query. Try specifying a model number (e.g., XR-18) or component name (e.g., cooling manifold).'
              }
            ],
            isError: true
          });
        }
        break;
      }

      if (name === 'listSchematics') {
        const listParams: ListSchematicsParams = {
          category: args?.category,
          model: args?.model,
          status: args?.status,
          limit: args?.limit
        };

        const results = schematicService.listSchematics(listParams);
        const categories = schematicService.getCategories();

        res.json({
          content: [
            {
              type: 'text',
              text: JSON.stringify({
                total_available: schematicService.getCount(),
                categories_available: categories,
                results_count: results.length,
                results
              }, null, 2)
            }
          ]
        });
        break;
      }

      // Unknown tool
      res.status(400).json({
        error: 'Unknown tool',
        message: `Tool "${name}" not found. Available tools: fetchSchematic, listSchematics`
      });
      break;
    }

    default:
      res.status(400).json({
        error: 'Invalid method',
        message: `Method "${method}" not supported. Use "tools/list" or "tools/call".`
      });
  }
});

// Error handling middleware
app.use((err: Error, _req: Request, res: Response, _next: express.NextFunction) => {
  console.error('Server error:', err);
  res.status(500).json({
    error: 'Internal server error',
    message: err.message
  });
});

// Start server
app.listen(PORT, () => {
  console.log(`
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   🤖 Schematica - Globomantics Robotics MCP Server          ║
║                                                              ║
║   Server running on port ${PORT}                              ║
║   Schematics loaded: ${schematicService.getCount()}                              ║
║   Categories: ${schematicService.getCategories().join(', ')}
║                                                              ║
║   Endpoints:                                                 ║
║   - Health: http://localhost:${PORT}/health                   ║
║   - MCP API: http://localhost:${PORT}/api/mcp                 ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
  `);
});

export default app;
