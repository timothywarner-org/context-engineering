#!/usr/bin/env node

/**
 * Knowledge Base MCP Server (Remote - Azure Deployment)
 *
 * A remote MCP server demonstrating document storage, retrieval, and search.
 * Designed for Azure Container Apps deployment with SSE (Server-Sent Events) transport.
 *
 * Features:
 * - Document CRUD operations
 * - Full-text search across documents
 * - Tag-based organization
 * - HTTP/SSE transport for remote access
 * - Azure-ready with environment configuration
 * - API key authentication
 * - CORS support for web clients
 *
 * Tools:
 * - add_document: Add a new document to the knowledge base
 * - get_document: Retrieve a document by ID
 * - search_documents: Search documents by content or tags
 * - update_document: Update an existing document
 * - delete_document: Delete a document
 * - list_documents: List all documents with optional filtering
 *
 * Resources:
 * - kb://documents: View all documents
 * - kb://tags: View all unique tags
 * - kb://stats: View knowledge base statistics
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
const PORT = process.env.PORT || 3000;
const API_KEY = process.env.API_KEY || 'dev-key-change-in-production';
const DATA_DIR = process.env.DATA_DIR || path.join(__dirname, '..', 'data');
const DOCUMENTS_FILE = path.join(DATA_DIR, 'documents.json');

// In-memory cache
let documentsCache = null;
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
 * Load documents from file with caching
 */
async function loadDocuments() {
  const now = Date.now();

  // Return cache if valid
  if (documentsCache && cacheTimestamp && (now - cacheTimestamp < CACHE_TTL)) {
    return documentsCache;
  }

  try {
    await ensureDataDirectory();
    const data = await fs.readFile(DOCUMENTS_FILE, 'utf-8');
    documentsCache = JSON.parse(data);
    cacheTimestamp = now;
    return documentsCache;
  } catch (error) {
    if (error.code === 'ENOENT') {
      // File doesn't exist yet, return empty array
      documentsCache = [];
      cacheTimestamp = now;
      return documentsCache;
    }
    console.error('[Error] Failed to load documents:', error.message);
    throw error;
  }
}

/**
 * Save documents to file and invalidate cache
 */
async function saveDocuments(documents) {
  try {
    await ensureDataDirectory();
    await fs.writeFile(DOCUMENTS_FILE, JSON.stringify(documents, null, 2), 'utf-8');
    documentsCache = documents;
    cacheTimestamp = Date.now();
  } catch (error) {
    console.error('[Error] Failed to save documents:', error.message);
    throw error;
  }
}

/**
 * Generate a unique document ID
 */
function generateId() {
  return `doc_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}

/**
 * Perform full-text search across documents
 */
function searchDocuments(documents, query, tags) {
  let results = documents;

  // Filter by tags if provided
  if (tags && tags.length > 0) {
    results = results.filter(doc =>
      tags.some(tag => doc.tags.includes(tag))
    );
  }

  // Search in title and content if query provided
  if (query && query.trim().length > 0) {
    const lowerQuery = query.toLowerCase();
    results = results.filter(doc =>
      doc.title.toLowerCase().includes(lowerQuery) ||
      doc.content.toLowerCase().includes(lowerQuery)
    );
  }

  return results;
}

/**
 * Format a document for display
 */
function formatDocument(doc, includeContent = true) {
  let formatted = `📄 **${doc.title}** (${doc.id})\n`;

  if (doc.tags && doc.tags.length > 0) {
    formatted += `   Tags: ${doc.tags.map(t => `#${t}`).join(', ')}\n`;
  }

  if (includeContent) {
    formatted += `\n${doc.content}\n`;
  }

  formatted += `\n   Created: ${new Date(doc.createdAt).toLocaleString()}`;

  if (doc.updatedAt && doc.updatedAt !== doc.createdAt) {
    formatted += `\n   Updated: ${new Date(doc.updatedAt).toLocaleString()}`;
  }

  return formatted;
}

/**
 * Format multiple documents for display
 */
function formatDocumentList(documents, title = 'Documents') {
  if (documents.length === 0) {
    return `**${title}**\n\nNo documents found.`;
  }

  let output = `**${title}** (${documents.length} total)\n\n`;

  documents.forEach(doc => {
    output += formatDocument(doc, false) + '\n\n';
  });

  return output;
}

/**
 * Create and configure MCP server
 */
function createMCPServer() {
  const server = new Server(
    {
      name: 'knowledge-base-mcp',
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
  // TOOL: add_document
  // ==========================================================================

  server.tool(
    'add_document',
    'Add a new document to the knowledge base',
    {
      type: 'object',
      properties: {
        title: {
          type: 'string',
          description: 'Document title (required)'
        },
        content: {
          type: 'string',
          description: 'Document content (required)'
        },
        tags: {
          type: 'array',
          items: { type: 'string' },
          description: 'Document tags (optional)'
        }
      },
      required: ['title', 'content']
    },
    async ({ title, content, tags }) => {
      try {
        console.log(`[Tool] add_document: ${title}`);

        if (!title || title.trim().length === 0) {
          throw new Error('Document title cannot be empty');
        }

        if (!content || content.trim().length === 0) {
          throw new Error('Document content cannot be empty');
        }

        const now = new Date().toISOString();
        const doc = {
          id: generateId(),
          title: title.trim(),
          content: content.trim(),
          tags: tags ? tags.map(t => t.trim().toLowerCase()) : [],
          createdAt: now,
          updatedAt: now
        };

        const documents = await loadDocuments();
        documents.push(doc);
        await saveDocuments(documents);

        console.log(`[Success] Added document: ${doc.id}`);

        return {
          content: [{
            type: 'text',
            text: `✅ **Document Added**\n\n${formatDocument(doc)}`
          }]
        };
      } catch (error) {
        console.error(`[Error] add_document: ${error.message}`);
        return {
          content: [{
            type: 'text',
            text: `❌ Failed to add document: ${error.message}`
          }],
          isError: true
        };
      }
    }
  );

  // ==========================================================================
  // TOOL: get_document
  // ==========================================================================

  server.tool(
    'get_document',
    'Retrieve a document by ID',
    {
      type: 'object',
      properties: {
        id: {
          type: 'string',
          description: 'Document ID'
        }
      },
      required: ['id']
    },
    async ({ id }) => {
      try {
        console.log(`[Tool] get_document: ${id}`);

        const documents = await loadDocuments();
        const doc = documents.find(d => d.id === id);

        if (!doc) {
          throw new Error(`Document not found: ${id}`);
        }

        return {
          content: [{
            type: 'text',
            text: formatDocument(doc)
          }]
        };
      } catch (error) {
        console.error(`[Error] get_document: ${error.message}`);
        return {
          content: [{
            type: 'text',
            text: `❌ Failed to get document: ${error.message}`
          }],
          isError: true
        };
      }
    }
  );

  // ==========================================================================
  // TOOL: search_documents
  // ==========================================================================

  server.tool(
    'search_documents',
    'Search documents by content or tags',
    {
      type: 'object',
      properties: {
        query: {
          type: 'string',
          description: 'Search query (searches title and content)'
        },
        tags: {
          type: 'array',
          items: { type: 'string' },
          description: 'Filter by tags'
        }
      }
    },
    async ({ query, tags }) => {
      try {
        console.log(`[Tool] search_documents: query="${query || ''}", tags=${tags ? tags.join(',') : 'none'}`);

        const documents = await loadDocuments();
        const results = searchDocuments(documents, query, tags);

        const searchDesc = [];
        if (query) searchDesc.push(`query: "${query}"`);
        if (tags && tags.length > 0) searchDesc.push(`tags: ${tags.join(', ')}`);

        const title = searchDesc.length > 0
          ? `Search Results (${searchDesc.join(', ')})`
          : 'All Documents';

        return {
          content: [{
            type: 'text',
            text: formatDocumentList(results, title)
          }]
        };
      } catch (error) {
        console.error(`[Error] search_documents: ${error.message}`);
        return {
          content: [{
            type: 'text',
            text: `❌ Failed to search documents: ${error.message}`
          }],
          isError: true
        };
      }
    }
  );

  // ==========================================================================
  // TOOL: update_document
  // ==========================================================================

  server.tool(
    'update_document',
    'Update an existing document',
    {
      type: 'object',
      properties: {
        id: {
          type: 'string',
          description: 'Document ID'
        },
        title: {
          type: 'string',
          description: 'New title (optional)'
        },
        content: {
          type: 'string',
          description: 'New content (optional)'
        },
        tags: {
          type: 'array',
          items: { type: 'string' },
          description: 'New tags (optional)'
        }
      },
      required: ['id']
    },
    async ({ id, title, content, tags }) => {
      try {
        console.log(`[Tool] update_document: ${id}`);

        const documents = await loadDocuments();
        const docIndex = documents.findIndex(d => d.id === id);

        if (docIndex === -1) {
          throw new Error(`Document not found: ${id}`);
        }

        const doc = documents[docIndex];

        if (title !== undefined) doc.title = title.trim();
        if (content !== undefined) doc.content = content.trim();
        if (tags !== undefined) doc.tags = tags.map(t => t.trim().toLowerCase());

        doc.updatedAt = new Date().toISOString();

        await saveDocuments(documents);

        console.log(`[Success] Updated document: ${id}`);

        return {
          content: [{
            type: 'text',
            text: `✅ **Document Updated**\n\n${formatDocument(doc)}`
          }]
        };
      } catch (error) {
        console.error(`[Error] update_document: ${error.message}`);
        return {
          content: [{
            type: 'text',
            text: `❌ Failed to update document: ${error.message}`
          }],
          isError: true
        };
      }
    }
  );

  // ==========================================================================
  // TOOL: delete_document
  // ==========================================================================

  server.tool(
    'delete_document',
    'Delete a document',
    {
      type: 'object',
      properties: {
        id: {
          type: 'string',
          description: 'Document ID'
        }
      },
      required: ['id']
    },
    async ({ id }) => {
      try {
        console.log(`[Tool] delete_document: ${id}`);

        const documents = await loadDocuments();
        const docIndex = documents.findIndex(d => d.id === id);

        if (docIndex === -1) {
          throw new Error(`Document not found: ${id}`);
        }

        const deletedDoc = documents[docIndex];
        documents.splice(docIndex, 1);

        await saveDocuments(documents);

        console.log(`[Success] Deleted document: ${id}`);

        return {
          content: [{
            type: 'text',
            text: `✅ **Document Deleted**\n\n${deletedDoc.title} (${id})`
          }]
        };
      } catch (error) {
        console.error(`[Error] delete_document: ${error.message}`);
        return {
          content: [{
            type: 'text',
            text: `❌ Failed to delete document: ${error.message}`
          }],
          isError: true
        };
      }
    }
  );

  // ==========================================================================
  // TOOL: list_documents
  // ==========================================================================

  server.tool(
    'list_documents',
    'List all documents with optional tag filter',
    {
      type: 'object',
      properties: {
        tags: {
          type: 'array',
          items: { type: 'string' },
          description: 'Filter by tags (optional)'
        }
      }
    },
    async ({ tags }) => {
      try {
        console.log(`[Tool] list_documents: tags=${tags ? tags.join(',') : 'none'}`);

        const documents = await loadDocuments();
        const results = tags && tags.length > 0
          ? searchDocuments(documents, null, tags)
          : documents;

        const title = tags && tags.length > 0
          ? `Documents (filtered by tags: ${tags.join(', ')})`
          : 'All Documents';

        return {
          content: [{
            type: 'text',
            text: formatDocumentList(results, title)
          }]
        };
      } catch (error) {
        console.error(`[Error] list_documents: ${error.message}`);
        return {
          content: [{
            type: 'text',
            text: `❌ Failed to list documents: ${error.message}`
          }],
          isError: true
        };
      }
    }
  );

  // ==========================================================================
  // RESOURCE: kb://documents
  // ==========================================================================

  server.resource(
    'kb://documents',
    'View all documents',
    async () => {
      console.log('[Resource] kb://documents');

      const documents = await loadDocuments();

      return {
        contents: [{
          uri: 'kb://documents',
          mimeType: 'text/plain',
          text: formatDocumentList(documents, 'All Documents')
        }]
      };
    }
  );

  // ==========================================================================
  // RESOURCE: kb://tags
  // ==========================================================================

  server.resource(
    'kb://tags',
    'View all unique tags',
    async () => {
      console.log('[Resource] kb://tags');

      const documents = await loadDocuments();
      const allTags = new Set();

      documents.forEach(doc => {
        doc.tags.forEach(tag => allTags.add(tag));
      });

      const tags = Array.from(allTags).sort();

      let text = `**Knowledge Base Tags**\n\n`;
      if (tags.length === 0) {
        text += 'No tags found.';
      } else {
        text += tags.map(tag => `#${tag}`).join(', ');
      }

      return {
        contents: [{
          uri: 'kb://tags',
          mimeType: 'text/plain',
          text
        }]
      };
    }
  );

  // ==========================================================================
  // RESOURCE: kb://stats
  // ==========================================================================

  server.resource(
    'kb://stats',
    'View knowledge base statistics',
    async () => {
      console.log('[Resource] kb://stats');

      const documents = await loadDocuments();
      const allTags = new Set();
      let totalContent = 0;

      documents.forEach(doc => {
        doc.tags.forEach(tag => allTags.add(tag));
        totalContent += doc.content.length;
      });

      const avgContentLength = documents.length > 0
        ? Math.round(totalContent / documents.length)
        : 0;

      const text = `**Knowledge Base Statistics**

📊 **Document Count**: ${documents.length}
🏷️  **Unique Tags**: ${allTags.size}
📝 **Total Content**: ${totalContent.toLocaleString()} characters
📏 **Average Length**: ${avgContentLength} characters per document

**Recent Activity**:
${documents.length > 0
  ? documents
      .sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt))
      .slice(0, 5)
      .map(d => `- ${d.title} (${new Date(d.createdAt).toLocaleDateString()})`)
      .join('\n')
  : 'No documents yet'}
`;

      return {
        contents: [{
          uri: 'kb://stats',
          mimeType: 'text/plain',
          text
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
  console.log('📚 Starting Knowledge Base MCP Server (Remote/Azure)...');
  console.log(`📡 Transport: HTTP/SSE`);
  console.log(`🔑 API Key: ${API_KEY === 'dev-key-change-in-production' ? '⚠️  Using default dev key' : '✅ Custom key set'}`);

  // Ensure data directory exists
  await ensureDataDirectory();

  // Create Express app
  const app = express();

  // CORS configuration
  app.use(cors({
    origin: '*', // Configure appropriately for production
    methods: ['GET', 'POST', 'OPTIONS'],
    allowedHeaders: ['Content-Type', 'Authorization']
  }));

  app.use(express.json());

  // API key authentication middleware
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

  // Health check endpoint (no auth required)
  app.get('/health', (req, res) => {
    res.json({
      status: 'healthy',
      service: 'knowledge-base-mcp',
      version: '1.0.0',
      timestamp: new Date().toISOString()
    });
  });

  // MCP SSE endpoint
  app.post('/sse', authenticateAPIKey, async (req, res) => {
    console.log('[SSE] New connection request');

    const mcpServer = createMCPServer();
    const transport = new SSEServerTransport('/message', res);

    await mcpServer.connect(transport);

    console.log('[SSE] Client connected');
  });

  // Message endpoint for SSE transport
  app.post('/message', authenticateAPIKey, async (req, res) => {
    // This is handled by the SSE transport
    res.status(200).send();
  });

  // Start server
  app.listen(PORT, () => {
    console.log(`✅ Knowledge Base MCP Server ready`);
    console.log(`🌐 Listening on http://0.0.0.0:${PORT}`);
    console.log(`📍 SSE endpoint: POST /sse`);
    console.log(`💚 Health check: GET /health`);
    console.log(`📍 Registered tools: add_document, get_document, search_documents, update_document, delete_document, list_documents`);
    console.log(`📍 Registered resources: kb://documents, kb://tags, kb://stats`);
  });
}

main().catch((error) => {
  console.error('❌ Fatal error:', error);
  process.exit(1);
});
