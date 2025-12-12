#!/usr/bin/env node
/**
 * ============================================================================
 * CORETEXT MCP SERVER - COMPLETE TEACHING EDITION
 * ============================================================================
 * Author: Tim Warner - TechTrainerTim.com
 * Purpose: O'Reilly Live Training - Context Engineering with MCP
 * Date: October 31, 2024
 *
 * TEACHING FLOW:
 * 1. Start with "AI Amnesia" - show ChatGPT forgetting
 * 2. Deploy this server - show persistence across sessions
 * 3. Demo CRUD operations - create, read, update, delete memories
 * 4. Show enrichment - Deepseek API integration
 * 5. Explore resources - context stream and knowledge graph
 * 6. Deploy to Azure - production patterns
 * ============================================================================
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListResourcesRequestSchema,
  ReadResourceRequestSchema,
  ListToolsRequestSchema
} from '@modelcontextprotocol/sdk/types.js';
import fs from 'fs/promises';
import path from 'path';
import { fileURLToPath } from 'url';
import { v4 as uuidv4 } from 'uuid';
import dotenv from 'dotenv';
import https from 'https';
import http from 'http';
import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

dotenv.config();

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const DATA_PATH = path.join(__dirname, '..', 'data', 'memory.json');

/**
 * UTILITY: Force kill any process using a given port
 * Needed because health server may not clean up properly on crashes
 */
async function killPort(port) {
  try {
    console.error(`🔍 Checking for processes on port ${port}...`);

    // Windows: Use netstat to find PID, then taskkill
    const { stdout } = await execAsync(`netstat -ano | findstr :${port}`);

    if (stdout.trim()) {
      const lines = stdout.trim().split('\n');
      const pids = new Set();

      for (const line of lines) {
        // Extract PID from the last column of netstat output
        const parts = line.trim().split(/\s+/);
        const pid = parts[parts.length - 1];
        if (pid && !isNaN(pid)) {
          pids.add(pid);
        }
      }

      for (const pid of pids) {
        try {
          await execAsync(`taskkill /F /PID ${pid}`);
          console.error(`   ✅ Killed process ${pid} on port ${port}`);
        } catch (killError) {
          console.error(`   ⚠️  Could not kill PID ${pid}: ${killError.message}`);
        }
      }
    } else {
      console.error(`   ✅ Port ${port} is available`);
    }
  } catch (error) {
    // If netstat fails (no processes found), that's good - port is free
    console.error(`   ✅ Port ${port} is available`);
  }
}

/**
 * MEMORY ENTRY CLASS
 * TEACHING POINT: Episodic vs Semantic memory
 * - Episodic: "I met with the client at 2pm on Tuesday"
 * - Semantic: "The client prefers email over phone calls"
 */
class MemoryEntry {
  constructor(content, type = 'semantic', metadata = {}) {
    this.id = uuidv4();
    this.content = content;
    this.type = type; // 'episodic' or 'semantic'
    this.metadata = {
      ...metadata,
      created: new Date().toISOString(),
      updated: new Date().toISOString(),
      accessCount: 0,
      enriched: false,
      lastAccessed: null
    };
    this.embeddings = null;
    this.tags = metadata.tags || [];
    this.enrichment = null;
  }
}

/**
 * MEMORY MANAGER CLASS
 * TEACHING POINT: CRUD operations fundamental to any data system
 */
class MemoryManager {
  constructor() {
    this.memories = new Map();
    this.initialized = false;
  }

  async initialize() {
    try {
      await fs.mkdir(path.dirname(DATA_PATH), { recursive: true });

      try {
        const data = await fs.readFile(DATA_PATH, 'utf-8');
        const parsed = JSON.parse(data);
        for (const [id, memory] of Object.entries(parsed)) {
          this.memories.set(id, memory);
        }
        console.error(`📚 Loaded ${this.memories.size} memories from disk`);
      } catch {
        console.error('📝 Starting with empty memory store');
        await this.createDemoMemories();
      }

      this.initialized = true;
    } catch (error) {
      console.error('❌ Failed to initialize:', error);
      throw error;
    }
  }

  async createDemoMemories() {
    const demos = [
      {
        content: "MCP (Model Context Protocol) enables persistent AI memory across sessions",
        type: "semantic",
        tags: ["mcp", "context", "ai", "protocol", "demo"]
      },
      {
        content: "O'Reilly Live Training: Context Engineering with MCP - October 31, 2024, 11am-3pm CDT",
        type: "episodic",
        tags: ["training", "event", "oreilly", "demo"]
      },
      {
        content: "Azure Container Apps provides serverless containers with automatic scaling",
        type: "semantic",
        tags: ["azure", "containers", "serverless", "demo"]
      }
    ];

    for (const demo of demos) {
      await this.create(demo.content, demo.type, { tags: demo.tags });
    }
    console.error('🎭 Created demo memories for teaching');
  }

  async persist() {
    const data = Object.fromEntries(this.memories);
    await fs.writeFile(DATA_PATH, JSON.stringify(data, null, 2));
  }

  async create(content, type = 'semantic', metadata = {}) {
    const entry = new MemoryEntry(content, type, metadata);
    this.memories.set(entry.id, entry);
    await this.persist();
    console.error(`💾 Created ${type} memory: ${entry.id}`);
    return entry;
  }

  async read(id) {
    const memory = this.memories.get(id);
    if (memory) {
      memory.metadata.accessCount++;
      memory.metadata.lastAccessed = new Date().toISOString();
      await this.persist();
      console.error(`📖 Read memory: ${id} (access #${memory.metadata.accessCount})`);
    }
    return memory;
  }

  async update(id, updates) {
    const memory = this.memories.get(id);
    if (!memory) return null;

    Object.assign(memory, updates);
    memory.metadata.updated = new Date().toISOString();
    await this.persist();
    console.error(`✏️ Updated memory: ${id}`);
    return memory;
  }

  async delete(id) {
    const result = this.memories.delete(id);
    if (result) {
      await this.persist();
      console.error(`🗑️ Deleted memory: ${id}`);
    }
    return result;
  }

  async search(query) {
    console.error(`🔍 Searching for: "${query}"`);
    const results = [];
    for (const memory of this.memories.values()) {
      if (memory.content.toLowerCase().includes(query.toLowerCase()) ||
          memory.tags.some(tag => tag.toLowerCase().includes(query.toLowerCase()))) {
        results.push(memory);
      }
    }
    console.error(`   Found ${results.length} matches`);
    return results;
  }

  async list(type = null) {
    const memories = Array.from(this.memories.values());
    if (type) {
      return memories.filter(m => m.type === type);
    }
    return memories;
  }

  findCommonElements(nodeIds, field) {
    const elements = {};
    nodeIds.forEach(id => {
      const memory = this.memories.get(id);
      if (memory && memory[field]) {
        (Array.isArray(memory[field]) ? memory[field] : [memory[field]]).forEach(element => {
          elements[element] = (elements[element] || 0) + 1;
        });
      }
    });
    return Object.entries(elements)
      .filter(([_, count]) => count > 1)
      .sort((a, b) => b[1] - a[1])
      .map(([element]) => element);
  }

  identifyClusterTheme(nodeIds) {
    const clusterMemories = nodeIds.map(id => this.memories.get(id)).filter(Boolean);

    const episodicCount = clusterMemories.filter(m => m.type === 'episodic').length;
    const semanticCount = clusterMemories.filter(m => m.type === 'semantic').length;

    if (episodicCount > semanticCount * 2) return 'Timeline/Events';
    if (semanticCount > episodicCount * 2) return 'Knowledge/Facts';

    const categories = {};
    clusterMemories.forEach(m => {
      if (m.enrichment && m.enrichment.category) {
        categories[m.enrichment.category] = (categories[m.enrichment.category] || 0) + 1;
      }
    });

    const topCategory = Object.entries(categories)
      .sort((a, b) => b[1] - a[1])[0];

    return topCategory ? topCategory[0] : 'Mixed';
  }
}

/**
 * DEEPSEEK ENRICHMENT SERVICE
 * TEACHING POINTS:
 * 1. Authentication hierarchy
 * 2. Graceful degradation
 * 3. Production patterns
 */
class DeepseekEnrichmentService {
  constructor() {
    this.apiKey = process.env.DEEPSEEK_API_KEY ||
                  process.env.DEEPSEEK_KEY ||
                  null;

    this.baseUrl = 'api.deepseek.com';
    this.model = 'deepseek-chat';

    if (this.apiKey) {
      console.error(`🔑 Deepseek API configured (key ending in: ...${this.apiKey.slice(-4)})`);
    } else {
      console.error('⚠️  No Deepseek API key found - using fallback mode');
    }
  }

  async enrich(memory) {
    console.error(`🧪 Enriching memory: ${memory.id.substring(0, 8)}...`);

    if (!this.apiKey) {
      return this.fallbackEnrich(memory);
    }

    try {
      const startTime = Date.now();

      const enrichmentPrompt = `Analyze this memory entry and provide:
1. A concise summary (max 50 words)
2. Top 5 keywords
3. Sentiment (positive/neutral/negative)
4. Category (technical/communication/education/business/personal)
5. Suggested related topics (2-3)

Memory: "${memory.content}"

Respond with valid JSON only, no markdown.`;

      const requestBody = JSON.stringify({
        model: this.model,
        messages: [
          {
            role: "system",
            content: "You are a memory enrichment system. Provide structured analysis in JSON format."
          },
          {
            role: "user",
            content: enrichmentPrompt
          }
        ],
        temperature: 0.3,
        max_tokens: 500,
        response_format: { type: "json_object" }
      });

      const response = await this.makeAPICall(requestBody);
      const analysis = JSON.parse(response.choices[0].message.content);

      memory.metadata.enriched = true;
      memory.metadata.enrichedAt = new Date().toISOString();
      memory.metadata.enrichmentMethod = 'deepseek-api';
      memory.enrichment = {
        ...analysis,
        apiVersion: 'deepseek-chat-v1',
        processingTime: `${Date.now() - startTime}ms`
      };

      console.error(`   ✅ Enriched via Deepseek API (${memory.enrichment.processingTime})`);
      return memory;

    } catch (error) {
      console.error(`   ⚠️ API enrichment failed: ${error.message}`);
      return this.fallbackEnrich(memory);
    }
  }

  makeAPICall(requestBody) {
    return new Promise((resolve, reject) => {
      const options = {
        hostname: this.baseUrl,
        path: '/v1/chat/completions',
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.apiKey}`,
          'Content-Length': Buffer.byteLength(requestBody)
        }
      };

      const req = https.request(options, (res) => {
        let data = '';
        res.on('data', chunk => data += chunk);
        res.on('end', () => {
          if (res.statusCode === 200) {
            resolve(JSON.parse(data));
          } else {
            reject(new Error(`API returned ${res.statusCode}: ${data}`));
          }
        });
      });

      req.on('error', reject);
      req.write(requestBody);
      req.end();
    });
  }

  fallbackEnrich(memory) {
    console.error('   📝 Using local enrichment (no API)');

    const text = memory.content.toLowerCase();

    const stopWords = new Set(['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'was', 'are', 'were']);
    const words = text.split(/\W+/).filter(w => w.length > 3 && !stopWords.has(w));
    const wordFreq = {};
    words.forEach(w => wordFreq[w] = (wordFreq[w] || 0) + 1);
    const keywords = Object.entries(wordFreq)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 5)
      .map(([word]) => word);

    const positiveWords = ['good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic', 'success', 'achieved'];
    const negativeWords = ['bad', 'poor', 'terrible', 'awful', 'failed', 'error', 'problem', 'issue'];

    let sentiment = 'neutral';
    const posCount = positiveWords.filter(w => text.includes(w)).length;
    const negCount = negativeWords.filter(w => text.includes(w)).length;
    if (posCount > negCount) sentiment = 'positive';
    else if (negCount > posCount) sentiment = 'negative';

    let category = 'general';
    if (/\b(code|programming|function|api|server|database)\b/i.test(text)) category = 'technical';
    else if (/\b(meeting|discuss|team|client|presentation)\b/i.test(text)) category = 'communication';
    else if (/\b(learn|study|course|training|teach)\b/i.test(text)) category = 'education';
    else if (/\b(business|revenue|customer|market|sales)\b/i.test(text)) category = 'business';

    memory.metadata.enriched = true;
    memory.metadata.enrichedAt = new Date().toISOString();
    memory.metadata.enrichmentMethod = 'local-fallback';
    memory.enrichment = {
      summary: memory.content.substring(0, 100) + (memory.content.length > 100 ? '...' : ''),
      keywords: keywords,
      sentiment: sentiment,
      category: category,
      confidence: 0.7,
      method: 'local'
    };

    console.error(`   ✅ Enriched locally (fallback mode)`);
    return memory;
  }
}

/**
 * MAIN MCP SERVER CLASS
 * TEACHING POINTS:
 * 1. Tools = Actions the AI can perform
 * 2. Resources = Information the AI can access
 * 3. Handlers = How we process requests
 */
class CoreTextServer {
  constructor() {
    this.server = new Server(
      {
        name: 'coretext-mcp',
        version: '1.0.0'
      },
      {
        capabilities: {
          resources: {},
          tools: {}
        }
      }
    );

    this.memoryManager = new MemoryManager();
    this.enrichmentService = new DeepseekEnrichmentService();

    this.setupHandlers();
  }

  setupHandlers() {
    // ==================== TOOLS HANDLER ====================
    this.server.setRequestHandler(ListToolsRequestSchema, async () => ({
      tools: [
        {
          name: 'memory_create',
          description: '📝 Create a new memory entry with optional type and metadata',
          inputSchema: {
            type: 'object',
            properties: {
              content: {
                type: 'string',
                description: 'The content to remember (fact, event, or information)'
              },
              type: {
                type: 'string',
                enum: ['episodic', 'semantic'],
                description: 'Memory type - episodic for events, semantic for facts',
                default: 'semantic'
              },
              tags: {
                type: 'array',
                items: { type: 'string' },
                description: 'Tags for categorization and search'
              },
              enrich: {
                type: 'boolean',
                description: 'Whether to enrich with AI analysis (requires API key)',
                default: false
              }
            },
            required: ['content']
          }
        },
        {
          name: 'memory_read',
          description: '📖 Retrieve a specific memory by ID',
          inputSchema: {
            type: 'object',
            properties: {
              id: { type: 'string', description: 'Memory ID to retrieve' }
            },
            required: ['id']
          }
        },
        {
          name: 'memory_update',
          description: '✏️ Update an existing memory',
          inputSchema: {
            type: 'object',
            properties: {
              id: { type: 'string', description: 'Memory ID to update' },
              content: { type: 'string', description: 'New content (optional)' },
              tags: {
                type: 'array',
                items: { type: 'string' },
                description: 'New tags (optional)'
              }
            },
            required: ['id']
          }
        },
        {
          name: 'memory_delete',
          description: '🗑️ Delete a memory permanently',
          inputSchema: {
            type: 'object',
            properties: {
              id: { type: 'string', description: 'Memory ID to delete' }
            },
            required: ['id']
          }
        },
        {
          name: 'memory_search',
          description: '🔍 Search memories by content or tags',
          inputSchema: {
            type: 'object',
            properties: {
              query: { type: 'string', description: 'Search query (searches content and tags)' },
              limit: {
                type: 'number',
                description: 'Max results to return',
                default: 10
              }
            },
            required: ['query']
          }
        },
        {
          name: 'memory_list',
          description: '📋 List all memories with optional type filter',
          inputSchema: {
            type: 'object',
            properties: {
              type: {
                type: 'string',
                enum: ['episodic', 'semantic', 'all'],
                description: 'Filter by memory type',
                default: 'all'
              },
              limit: {
                type: 'number',
                description: 'Max results to return',
                default: 20
              }
            }
          }
        },
        {
          name: 'memory_stats',
          description: '📊 Get memory system statistics and usage patterns',
          inputSchema: {
            type: 'object',
            properties: {}
          }
        },
        {
          name: 'memory_enrich',
          description: '✨ Enrich an existing memory with AI analysis',
          inputSchema: {
            type: 'object',
            properties: {
              id: { type: 'string', description: 'Memory ID to enrich' }
            },
            required: ['id']
          }
        }
      ]
    }));

    // ==================== TOOL CALLS HANDLER ====================
    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      const { name, arguments: args } = request.params;
      console.error(`\n🔧 Tool called: ${name}`);

      try {
        switch (name) {
          case 'memory_create': {
            let memory = await this.memoryManager.create(
              args.content,
              args.type || 'semantic',
              { tags: args.tags || [] }
            );

            if (args.enrich) {
              memory = await this.enrichmentService.enrich(memory);
              await this.memoryManager.update(memory.id, memory);
            }

            return {
              content: [
                {
                  type: 'text',
                  text: JSON.stringify({
                    success: true,
                    memory: memory,
                    message: `✅ Memory created with ID: ${memory.id}`
                  }, null, 2)
                }
              ]
            };
          }

          case 'memory_read': {
            const memory = await this.memoryManager.read(args.id);
            if (!memory) {
              return {
                content: [{
                  type: 'text',
                  text: JSON.stringify({
                    success: false,
                    error: `Memory not found: ${args.id}`
                  })
                }]
              };
            }

            return {
              content: [{
                type: 'text',
                text: JSON.stringify({
                  success: true,
                  memory: memory
                }, null, 2)
              }]
            };
          }

          case 'memory_update': {
            const updates = {};
            if (args.content) updates.content = args.content;
            if (args.tags) updates.tags = args.tags;

            const memory = await this.memoryManager.update(args.id, updates);
            if (!memory) {
              return {
                content: [{
                  type: 'text',
                  text: JSON.stringify({
                    success: false,
                    error: `Memory not found: ${args.id}`
                  })
                }]
              };
            }

            return {
              content: [{
                type: 'text',
                text: JSON.stringify({
                  success: true,
                  memory: memory,
                  message: `✅ Memory updated: ${args.id}`
                }, null, 2)
              }]
            };
          }

          case 'memory_delete': {
            const result = await this.memoryManager.delete(args.id);
            return {
              content: [{
                type: 'text',
                text: JSON.stringify({
                  success: result,
                  message: result ? `✅ Memory deleted: ${args.id}` : `❌ Memory not found: ${args.id}`
                })
              }]
            };
          }

          case 'memory_search': {
            const results = await this.memoryManager.search(args.query);
            const limited = results.slice(0, args.limit || 10);

            return {
              content: [{
                type: 'text',
                text: JSON.stringify({
                  success: true,
                  query: args.query,
                  count: limited.length,
                  total: results.length,
                  memories: limited
                }, null, 2)
              }]
            };
          }

          case 'memory_list': {
            const typeFilter = args.type === 'all' ? null : args.type;
            const memories = await this.memoryManager.list(typeFilter);
            const limited = memories.slice(0, args.limit || 20);

            return {
              content: [{
                type: 'text',
                text: JSON.stringify({
                  success: true,
                  type: args.type || 'all',
                  count: limited.length,
                  total: memories.length,
                  memories: limited
                }, null, 2)
              }]
            };
          }

          case 'memory_stats': {
            const memories = await this.memoryManager.list();
            const episodic = memories.filter(m => m.type === 'episodic').length;
            const semantic = memories.filter(m => m.type === 'semantic').length;
            const enriched = memories.filter(m => m.metadata.enriched).length;

            const stats = {
              total: memories.length,
              episodic: episodic,
              semantic: semantic,
              enriched: enriched,
              enrichmentRate: memories.length > 0 ?
                `${(enriched / memories.length * 100).toFixed(1)}%` : '0%',
              tags: [...new Set(memories.flatMap(m => m.tags))],
              mostAccessed: memories.sort((a, b) =>
                (b.metadata.accessCount || 0) - (a.metadata.accessCount || 0)
              ).slice(0, 5).map(m => ({
                id: m.id,
                content: m.content.substring(0, 50) + '...',
                accessCount: m.metadata.accessCount
              }))
            };

            return {
              content: [{
                type: 'text',
                text: JSON.stringify({
                  success: true,
                  stats: stats
                }, null, 2)
              }]
            };
          }

          case 'memory_enrich': {
            let memory = await this.memoryManager.read(args.id);
            if (!memory) {
              return {
                content: [{
                  type: 'text',
                  text: JSON.stringify({
                    success: false,
                    error: `Memory not found: ${args.id}`
                  })
                }]
              };
            }

            memory = await this.enrichmentService.enrich(memory);
            await this.memoryManager.update(memory.id, memory);

            return {
              content: [{
                type: 'text',
                text: JSON.stringify({
                  success: true,
                  memory: memory,
                  message: `✨ Memory enriched: ${args.id}`
                }, null, 2)
              }]
            };
          }

          default:
            throw new Error(`Unknown tool: ${name}`);
        }
      } catch (error) {
        console.error(`❌ Tool error: ${error.message}`);
        return {
          content: [{
            type: 'text',
            text: JSON.stringify({
              success: false,
              error: error.message
            })
          }]
        };
      }
    });

    // ==================== RESOURCES HANDLER ====================
    this.server.setRequestHandler(ListResourcesRequestSchema, async () => ({
      resources: [
        {
          uri: 'memory://overview',
          name: '📊 Memory System Overview',
          description: 'Current state, statistics, and capabilities of the CoreText memory system',
          mimeType: 'text/markdown'
        },
        {
          uri: 'memory://context-stream',
          name: '🌊 Active Context Stream',
          description: 'Real-time view of recent memories and access patterns - maintains conversation continuity',
          mimeType: 'application/json'
        },
        {
          uri: 'memory://knowledge-graph',
          name: '🕸️ Knowledge Graph',
          description: 'Semantic relationships between memories - shows how concepts connect',
          mimeType: 'application/json'
        }
      ]
    }));

    // ==================== RESOURCE READER ====================
    this.server.setRequestHandler(ReadResourceRequestSchema, async (request) => {
      const { uri } = request.params;
      console.error(`\n📄 Resource accessed: ${uri}`);

      // ========== MEMORY OVERVIEW RESOURCE ==========
      if (uri === 'memory://overview') {
        const memories = await this.memoryManager.list();
        const stats = {
          total: memories.length,
          episodic: memories.filter(m => m.type === 'episodic').length,
          semantic: memories.filter(m => m.type === 'semantic').length,
          enriched: memories.filter(m => m.metadata.enriched).length
        };

        const recentMemories = memories
          .sort((a, b) => new Date(b.metadata.updated) - new Date(a.metadata.updated))
          .slice(0, 5);

        const mostAccessed = memories
          .sort((a, b) => (b.metadata.accessCount || 0) - (a.metadata.accessCount || 0))
          .slice(0, 5);

        const tagFreq = {};
        memories.forEach(m => {
          (m.tags || []).forEach(tag => {
            tagFreq[tag] = (tagFreq[tag] || 0) + 1;
          });
        });

        return {
          contents: [
            {
              uri: uri,
              mimeType: 'text/markdown',
              text: `# 🧠 CoreText Memory System Overview

## 📊 Current Statistics
- **Total Memories**: ${stats.total}
- **Episodic**: ${stats.episodic} (event-based memories)
- **Semantic**: ${stats.semantic} (fact-based memories)
- **AI-Enriched**: ${stats.enriched}
- **Enrichment Coverage**: ${stats.total > 0 ? (stats.enriched / stats.total * 100).toFixed(1) : 0}%

## 🕐 Recent Activity (Last 5 Updates)
${recentMemories.map(m => `- **${new Date(m.metadata.updated).toLocaleString()}**: ${m.content.substring(0, 60)}...`).join('\n') || '- No memories yet'}

## 🔥 Most Accessed Memories
${mostAccessed.filter(m => m.metadata.accessCount > 0).map(m => `- **${m.metadata.accessCount} accesses**: ${m.content.substring(0, 60)}...`).join('\n') || '- No accessed memories yet'}

## 🏷️ Knowledge Tags (Top 10)
${Object.entries(tagFreq)
  .sort((a, b) => b[1] - a[1])
  .slice(0, 10)
  .map(([tag, count]) => `\`${tag}\` (${count})`)
  .join(' • ') || 'No tags yet'}

## 💡 Teaching Examples

### Example 1: Store a Fact (Semantic Memory)
\`\`\`
User: "Remember that our client prefers email over phone calls"
→ Creates semantic memory tagged ['client', 'communication', 'preferences']
\`\`\`

### Example 2: Store an Event (Episodic Memory)
\`\`\`
User: "Remember we discussed the Azure migration at 2pm today"
→ Creates episodic memory tagged ['meeting', 'azure', 'migration']
\`\`\`

## 🔐 System Configuration
- **Storage Backend**: ${memories.length > 0 ? '✅ Active (JSON file)' : '🔄 Ready'}
- **Enrichment API**: ${process.env.DEEPSEEK_API_KEY ? '✅ Deepseek Connected' : '⚠️ Fallback Mode'}
- **Memory Persistence**: ✅ Enabled (survives restarts)

---
*System Time: ${new Date().toISOString()}*
*Server Version: 1.0.0*`
            }
          ]
        };
      }

      // ========== CONTEXT STREAM RESOURCE ==========
      if (uri === 'memory://context-stream') {
        // TEACHING POINT: This shows "working memory" - what's currently relevant
        const memories = await this.memoryManager.list();

        const contextStream = memories
          .map(m => ({
            ...m,
            lastRelevantTime: Math.max(
              new Date(m.metadata.updated).getTime(),
              m.metadata.lastAccessed ? new Date(m.metadata.lastAccessed).getTime() : 0
            )
          }))
          .sort((a, b) => b.lastRelevantTime - a.lastRelevantTime)
          .slice(0, 20);

        const now = Date.now();
        const hour = 60 * 60 * 1000;
        const day = 24 * hour;

        const grouped = {
          recent: contextStream.filter(m => now - m.lastRelevantTime < hour),
          today: contextStream.filter(m => {
            const age = now - m.lastRelevantTime;
            return age >= hour && age < day;
          }),
          earlier: contextStream.filter(m => now - m.lastRelevantTime >= day)
        };

        const contextSummary = {
          timestamp: new Date().toISOString(),
          teaching_note: "This resource maintains conversation continuity by showing recent context",
          activeTopics: [...new Set(contextStream.flatMap(m => m.tags || []))].slice(0, 10),
          dominantType: contextStream.filter(m => m.type === 'episodic').length >
                         contextStream.filter(m => m.type === 'semantic').length
                         ? 'episodic' : 'semantic',
          recentContext: grouped.recent.map(m => ({
            id: m.id,
            type: m.type,
            content: m.content,
            tags: m.tags,
            enrichment: m.enrichment ? {
              summary: m.enrichment.summary,
              sentiment: m.enrichment.sentiment,
              category: m.enrichment.category
            } : null,
            metadata: {
              created: m.metadata.created,
              accessCount: m.metadata.accessCount,
              enriched: m.metadata.enriched
            }
          })),
          todayContext: grouped.today.map(m => ({
            id: m.id,
            snippet: m.content.substring(0, 100) + '...',
            tags: m.tags,
            type: m.type
          })),
          earlierContext: grouped.earlier.length,
          statistics: {
            totalMemories: memories.length,
            inContextStream: contextStream.length,
            recentlyActive: grouped.recent.length,
            enrichmentRate: memories.length > 0 ?
              `${(memories.filter(m => m.metadata.enriched).length / memories.length * 100).toFixed(1)}%` : '0%',
            avgAccessCount: memories.length > 0 ?
              (memories.reduce((sum, m) => sum + (m.metadata.accessCount || 0), 0) / memories.length).toFixed(1) : '0'
          },
          demo_tip: "Show how this maintains context across conversation turns!"
        };

        return {
          contents: [
            {
              uri: uri,
              mimeType: 'application/json',
              text: JSON.stringify(contextSummary, null, 2)
            }
          ]
        };
      }

      // ========== KNOWLEDGE GRAPH RESOURCE ==========
      if (uri === 'memory://knowledge-graph') {
        // TEACHING POINT: This shows how memories interconnect (semantic network)
        const memories = await this.memoryManager.list();

        // Build nodes
        const nodes = memories.map(m => ({
          id: m.id,
          label: m.content.substring(0, 30) + '...',
          type: m.type,
          enriched: m.metadata.enriched,
          accessCount: m.metadata.accessCount || 0,
          tags: m.tags || []
        }));

        // Build edges based on shared tags and keywords
        const edges = [];
        for (let i = 0; i < memories.length; i++) {
          for (let j = i + 1; j < memories.length; j++) {
            const m1 = memories[i];
            const m2 = memories[j];

            const sharedTags = (m1.tags || []).filter(t => (m2.tags || []).includes(t));

            const sharedKeywords = m1.enrichment && m2.enrichment ?
              (m1.enrichment.keywords || []).filter(k =>
                (m2.enrichment.keywords || []).includes(k)) : [];

            const strength = sharedTags.length + sharedKeywords.length;

            if (strength > 0) {
              edges.push({
                source: m1.id,
                target: m2.id,
                weight: strength,
                sharedTags: sharedTags,
                sharedKeywords: sharedKeywords
              });
            }
          }
        }

        // Find clusters
        const clusters = [];
        const visited = new Set();

        nodes.forEach(node => {
          if (!visited.has(node.id)) {
            const cluster = [];
            const queue = [node.id];

            while (queue.length > 0) {
              const current = queue.shift();
              if (!visited.has(current)) {
                visited.add(current);
                cluster.push(current);

                edges.forEach(edge => {
                  if (edge.source === current && !visited.has(edge.target)) {
                    queue.push(edge.target);
                  } else if (edge.target === current && !visited.has(edge.source)) {
                    queue.push(edge.source);
                  }
                });
              }
            }

            if (cluster.length > 1) {
              clusters.push(cluster);
            }
          }
        });

        const knowledgeGraph = {
          metadata: {
            generated: new Date().toISOString(),
            teaching_note: "This shows how memories form semantic networks",
            totalNodes: nodes.length,
            totalEdges: edges.length,
            clusters: clusters.length,
            graphDensity: nodes.length > 1 ?
              (2 * edges.length / (nodes.length * (nodes.length - 1))).toFixed(3) : '0'
          },
          nodes: nodes,
          edges: edges.sort((a, b) => b.weight - a.weight),
          clusters: clusters.map(c => ({
            size: c.length,
            nodeIds: c,
            commonTags: this.memoryManager.findCommonElements(c, 'tags'),
            theme: this.memoryManager.identifyClusterTheme(c)
          })),
          insights: {
            mostConnected: nodes.sort((a, b) => {
              const aEdges = edges.filter(e => e.source === a.id || e.target === a.id).length;
              const bEdges = edges.filter(e => e.source === b.id || e.target === b.id).length;
              return bEdges - aEdges;
            }).slice(0, 3).map(n => ({
              id: n.id,
              label: n.label,
              connections: edges.filter(e => e.source === n.id || e.target === n.id).length
            })),
            strongestConnections: edges.slice(0, 5).map(e => ({
              source: nodes.find(n => n.id === e.source)?.label || 'Unknown',
              target: nodes.find(n => n.id === e.target)?.label || 'Unknown',
              strength: e.weight,
              basis: [...e.sharedTags, ...e.sharedKeywords]
            })),
            orphanedMemories: nodes.filter(n =>
              !edges.some(e => e.source === n.id || e.target === n.id)
            ).length
          },
          demo_tip: "Create related memories and watch clusters form!"
        };

        return {
          contents: [
            {
              uri: uri,
              mimeType: 'application/json',
              text: JSON.stringify(knowledgeGraph, null, 2)
            }
          ]
        };
      }

      throw new Error(`Resource not found: ${uri}`);
    });
  }

  async start() {
    console.error('============================================');
    console.error('🚀 CoreText MCP Server - Teaching Edition');
    console.error('============================================');
    console.error('📚 Initializing memory system...');

    await this.memoryManager.initialize();

    // Start health check endpoint for Azure Container Apps
    // Note: Port killing is handled by npm run inspector (via kill-ports script)
    // This keeps the server lightweight and doesn't interfere with stdio transport
    this.startHealthServer();

    const transport = new StdioServerTransport();
    await this.server.connect(transport);

    console.error('✅ Server ready for connections');
    console.error('🔑 Deepseek enrichment:', process.env.DEEPSEEK_API_KEY ? 'CONFIGURED' : 'FALLBACK MODE');
    console.error('📁 Data location:', DATA_PATH);
    console.error('============================================');
    console.error('');
    console.error('TEACHING TIPS:');
    console.error('1. Start MCP Inspector: npm run inspector');
    console.error('2. Show tool list to demonstrate capabilities');
    console.error('3. Create both episodic and semantic memories');
    console.error('4. Access resources to show persistent state');
    console.error('5. Restart server to prove persistence');
    console.error('============================================');
  }

  startHealthServer() {
    // Use port 3001 to avoid conflict with MCP Inspector (which uses 3000)
    const port = process.env.HEALTH_PORT || 3001;

    const healthServer = http.createServer((req, res) => {
      if (req.url === '/health' && req.method === 'GET') {
        // Return health status
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({
          status: 'healthy',
          timestamp: new Date().toISOString(),
          memoryCount: this.memoryManager.memories.size,
          enrichmentConfigured: !!process.env.DEEPSEEK_API_KEY,
          uptime: process.uptime()
        }));
      } else {
        res.writeHead(404, { 'Content-Type': 'text/plain' });
        res.end('Not Found');
      }
    });

    healthServer.listen(port, () => {
      console.error(`❤️  Health endpoint running on http://localhost:${port}/health`);
    });

    // Store reference for cleanup
    this.healthServer = healthServer;
  }
}

// ============================================================================
// SERVER STARTUP
// ============================================================================
const server = new CoreTextServer();
server.start().catch(error => {
  console.error('❌ Failed to start server:', error);
  process.exit(1);
});

// Handle graceful shutdown
process.on('SIGINT', () => {
  console.error('\n👋 Shutting down gracefully...');
  process.exit(0);
});

process.on('SIGTERM', () => {
  console.error('\n👋 Shutting down gracefully...');
  process.exit(0);
});
