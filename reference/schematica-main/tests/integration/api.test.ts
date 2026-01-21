/**
 * Integration Tests - API Endpoints
 *
 * Tests for the Express API endpoints, verifying HTTP responses,
 * content types, and proper error handling.
 */

import request from 'supertest';
import express from 'express';
import { SchematicService } from '../../src/schematic-service';

// Create a minimal test app without starting the server
const createTestApp = () => {
  const app = express();
  const schematicService = new SchematicService();

  app.use(express.json());

  // Health endpoint
  app.get('/health', (_req, res) => {
    res.json({
      status: 'healthy',
      service: 'schematica',
      version: '1.0.0',
      schematics_count: schematicService.getCount()
    });
  });

  // Root endpoint - JSON response for API clients
  app.get('/', (req, res) => {
    const acceptsHtml = req.headers.accept?.includes('text/html');
    if (acceptsHtml) {
      res.send('<html><body>Schematica</body></html>');
    } else {
      res.json({
        name: 'Schematica',
        description: 'Globomantics Robotics MCP Server',
        version: '1.0.0'
      });
    }
  });

  // MCP endpoint (simplified for testing)
  app.post('/api/mcp', (req, res) => {
    const { method, params } = req.body;

    if (method === 'tools/list') {
      res.json({ tools: ['fetchSchematic', 'listSchematics'] });
    } else if (method === 'tools/call') {
      const { name } = params || {};
      if (name === 'listSchematics') {
        const results = schematicService.listSchematics({ limit: 5 });
        res.json({ content: [{ type: 'text', text: JSON.stringify(results) }] });
      } else {
        res.status(400).json({ error: 'Unknown tool' });
      }
    } else {
      res.status(400).json({ error: 'Invalid method' });
    }
  });

  return app;
};

describe('API Endpoints', () => {
  const app = createTestApp();

  describe('GET /health', () => {
    it('should return healthy status', async () => {
      const response = await request(app)
        .get('/health')
        .expect('Content-Type', /json/)
        .expect(200);

      expect(response.body.status).toBe('healthy');
      expect(response.body.service).toBe('schematica');
      expect(response.body.version).toBe('1.0.0');
    });

    it('should include schematics count', async () => {
      const response = await request(app)
        .get('/health')
        .expect(200);

      expect(response.body.schematics_count).toBeGreaterThan(0);
    });
  });

  describe('GET /', () => {
    it('should return JSON for API clients', async () => {
      const response = await request(app)
        .get('/')
        .set('Accept', 'application/json')
        .expect('Content-Type', /json/)
        .expect(200);

      expect(response.body.name).toBe('Schematica');
      expect(response.body.version).toBe('1.0.0');
    });

    it('should return HTML for browsers', async () => {
      const response = await request(app)
        .get('/')
        .set('Accept', 'text/html')
        .expect('Content-Type', /html/)
        .expect(200);

      expect(response.text).toContain('Schematica');
    });
  });

  describe('POST /api/mcp', () => {
    it('should list available tools', async () => {
      const response = await request(app)
        .post('/api/mcp')
        .send({ method: 'tools/list' })
        .expect('Content-Type', /json/)
        .expect(200);

      expect(response.body.tools).toBeDefined();
      expect(response.body.tools.length).toBeGreaterThan(0);
    });

    it('should call listSchematics tool', async () => {
      const response = await request(app)
        .post('/api/mcp')
        .send({
          method: 'tools/call',
          params: { name: 'listSchematics', arguments: {} }
        })
        .expect(200);

      expect(response.body.content).toBeDefined();
      expect(response.body.content[0].type).toBe('text');
    });

    it('should return error for invalid method', async () => {
      const response = await request(app)
        .post('/api/mcp')
        .send({ method: 'invalid/method' })
        .expect(400);

      expect(response.body.error).toBeDefined();
    });

    it('should return error for unknown tool', async () => {
      const response = await request(app)
        .post('/api/mcp')
        .send({
          method: 'tools/call',
          params: { name: 'unknownTool' }
        })
        .expect(400);

      expect(response.body.error).toBeDefined();
    });
  });

  describe('response headers', () => {
    it('should return proper content-type for JSON', async () => {
      const response = await request(app).get('/health');
      expect(response.headers['content-type']).toMatch(/application\/json/);
    });
  });
});
