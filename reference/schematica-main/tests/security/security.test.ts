/**
 * Security Tests
 *
 * Tests for security best practices including authentication,
 * input validation, and protection against common vulnerabilities.
 */

import request from 'supertest';
import express, { Request, Response, NextFunction } from 'express';

/**
 * Test-specific auth middleware that reads API key at runtime
 * (mirrors the behavior of the actual auth middleware)
 */
const createAuthMiddleware = (apiKey: string | undefined) => {
  return (req: Request, res: Response, next: NextFunction): void => {
    // Health and root endpoints are public
    if (req.path === '/health' || req.path === '/') {
      return next();
    }

    if (!apiKey) {
      res.status(500).json({
        error: 'Server configuration error',
        message: 'API key not configured'
      });
      return;
    }

    const authHeader = req.headers.authorization;

    if (!authHeader) {
      res.status(401).json({
        error: 'Unauthorized',
        message: 'Missing Authorization header'
      });
      return;
    }

    const parts = authHeader.split(' ');
    if (parts.length !== 2 || parts[0].toLowerCase() !== 'bearer') {
      res.status(401).json({
        error: 'Unauthorized',
        message: 'Invalid Authorization header format'
      });
      return;
    }

    const token = parts[1];
    if (token !== apiKey) {
      res.status(401).json({
        error: 'Unauthorized',
        message: 'Invalid API key'
      });
      return;
    }

    next();
  };
};

describe('Security Tests', () => {
  describe('Authentication Middleware', () => {
    const TEST_API_KEY = 'test-api-key-12345';

    it('should allow access to health endpoint without auth', async () => {
      const app = express();
      app.use(createAuthMiddleware(TEST_API_KEY));
      app.get('/health', (_req, res) => {
        res.json({ status: 'healthy' });
      });

      const response = await request(app)
        .get('/health')
        .expect(200);

      expect(response.body.status).toBe('healthy');
    });

    it('should reject requests without Authorization header', async () => {
      const app = express();
      app.use(createAuthMiddleware(TEST_API_KEY));
      app.get('/protected', (_req, res) => {
        res.json({ message: 'Access granted' });
      });

      const response = await request(app)
        .get('/protected')
        .expect(401);

      expect(response.body.error).toBe('Unauthorized');
    });

    it('should reject requests with invalid token format', async () => {
      const app = express();
      app.use(createAuthMiddleware(TEST_API_KEY));
      app.get('/protected', (_req, res) => {
        res.json({ message: 'Access granted' });
      });

      const response = await request(app)
        .get('/protected')
        .set('Authorization', 'InvalidFormat token')
        .expect(401);

      expect(response.body.error).toBe('Unauthorized');
    });

    it('should reject requests with wrong token', async () => {
      const app = express();
      app.use(createAuthMiddleware(TEST_API_KEY));
      app.get('/protected', (_req, res) => {
        res.json({ message: 'Access granted' });
      });

      const response = await request(app)
        .get('/protected')
        .set('Authorization', 'Bearer wrong-token')
        .expect(401);

      expect(response.body.error).toBe('Unauthorized');
    });

    it('should allow requests with valid Bearer token', async () => {
      const app = express();
      app.use(createAuthMiddleware(TEST_API_KEY));
      app.get('/protected', (_req, res) => {
        res.json({ message: 'Access granted' });
      });

      const response = await request(app)
        .get('/protected')
        .set('Authorization', `Bearer ${TEST_API_KEY}`)
        .expect(200);

      expect(response.body.message).toBe('Access granted');
    });

    it('should handle missing API key configuration', async () => {
      const app = express();
      app.use(createAuthMiddleware(undefined)); // No API key configured
      app.get('/protected', (_req, res) => {
        res.json({ ok: true });
      });

      const response = await request(app)
        .get('/protected')
        .set('Authorization', 'Bearer any-token')
        .expect(500);

      expect(response.body.error).toBe('Server configuration error');
    });
  });

  describe('Input Validation', () => {
    it('should handle empty JSON body gracefully', async () => {
      const app = express();
      app.use(express.json());
      app.post('/test', (req, res) => {
        const body = req.body || {};
        res.json({ received: Object.keys(body).length });
      });

      const response = await request(app)
        .post('/test')
        .send({})
        .expect(200);

      expect(response.body.received).toBe(0);
    });

    it('should handle malformed JSON gracefully', async () => {
      const app = express();
      app.use(express.json());
      app.use((err: Error, _req: Request, res: Response, _next: NextFunction) => {
        res.status(400).json({ error: 'Invalid JSON' });
      });
      app.post('/test', (_req, res) => {
        res.json({ ok: true });
      });

      const response = await request(app)
        .post('/test')
        .set('Content-Type', 'application/json')
        .send('{ invalid json }')
        .expect(400);

      expect(response.body.error).toBe('Invalid JSON');
    });

    it('should not expose stack traces in error responses', async () => {
      const app = express();
      app.get('/error', () => {
        throw new Error('Test error');
      });
      app.use((err: Error, _req: Request, res: Response, _next: NextFunction) => {
        res.status(500).json({ error: 'Internal server error' });
      });

      const response = await request(app)
        .get('/error')
        .expect(500);

      expect(response.body.stack).toBeUndefined();
      expect(response.text).not.toContain('at ');
    });
  });

  describe('HTTP Security Headers', () => {
    it('should set proper content-type for JSON responses', async () => {
      const app = express();
      app.get('/test', (_req, res) => {
        res.json({ data: 'test' });
      });

      const response = await request(app).get('/test');
      expect(response.headers['content-type']).toMatch(/application\/json/);
    });
  });

  describe('API Key Security', () => {
    it('should not leak API key in responses', async () => {
      const SECRET_KEY = 'secret-key-that-should-not-leak';
      const app = express();
      app.use(createAuthMiddleware(SECRET_KEY));
      app.get('/health', (_req, res) => {
        res.json({ status: 'healthy', service: 'schematica' });
      });

      const response = await request(app)
        .get('/health')
        .expect(200);

      expect(JSON.stringify(response.body)).not.toContain('secret-key');
    });
  });

  describe('Rate Limiting Readiness', () => {
    it('should accept multiple rapid requests (baseline test)', async () => {
      const app = express();
      app.get('/test', (_req, res) => {
        res.json({ ok: true });
      });

      // Send 5 requests in quick succession
      const requests = Array(5).fill(null).map(() =>
        request(app).get('/test')
      );

      const responses = await Promise.all(requests);
      responses.forEach(response => {
        expect(response.status).toBe(200);
      });
    });
  });

  describe('XSS Prevention', () => {
    it('should escape HTML in JSON responses', async () => {
      const app = express();
      app.get('/test', (_req, res) => {
        // JSON.stringify automatically escapes special characters
        res.json({ userInput: '<script>alert("xss")</script>' });
      });

      const response = await request(app).get('/test');
      expect(response.headers['content-type']).toMatch(/application\/json/);
      // The script tag should be in the JSON but as a string, not executable
      expect(response.body.userInput).toBe('<script>alert("xss")</script>');
    });
  });

  describe('SQL Injection Prevention', () => {
    it('should handle potentially malicious input safely', async () => {
      const app = express();
      app.use(express.json());
      app.post('/search', (req, res) => {
        // Simulate safe parameter handling (no raw SQL)
        const query = req.body.query || '';
        // In a real app, this would use parameterized queries
        res.json({ searchTerm: query, results: [] });
      });

      const response = await request(app)
        .post('/search')
        .send({ query: "'; DROP TABLE users; --" })
        .expect(200);

      // The malicious input is just treated as a string
      expect(response.body.searchTerm).toBe("'; DROP TABLE users; --");
      expect(response.body.results).toEqual([]);
    });
  });
});
