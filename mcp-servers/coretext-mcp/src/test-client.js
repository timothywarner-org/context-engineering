#!/usr/bin/env node
/**
 * ============================================================================
 * CORETEXT MCP SERVER - TEST CLIENT
 * ============================================================================
 * Purpose: Validates all 8 tools work correctly before teaching session
 * Usage: npm test
 * ============================================================================
 */

import { Client } from '@modelcontextprotocol/sdk/client/index.js';
import { StdioClientTransport } from '@modelcontextprotocol/sdk/client/stdio.js';
import { spawn } from 'child_process';

console.log('============================================');
console.log('🧪 CoreText MCP Server - Test Suite');
console.log('============================================\n');

let testsPassed = 0;
let testsFailed = 0;
const createdMemoryIds = [];

async function runTests() {
  // Start the server
  console.log('📡 Starting MCP server...');
  const serverProcess = spawn('node', ['src/index.js'], {
    stdio: ['pipe', 'pipe', 'pipe']
  });

  // Suppress server logs during testing
  serverProcess.stderr.on('data', () => {});

  const transport = new StdioClientTransport({
    command: 'node',
    args: ['src/index.js'],
    stderr: 'pipe'
  });

  const client = new Client(
    {
      name: 'test-client',
      version: '1.0.0'
    },
    {
      capabilities: {}
    }
  );

  try {
    await client.connect(transport);
    console.log('✅ Connected to server\n');

    // Test 1: List Tools
    await test('List Tools', async () => {
      const result = await client.listTools();
      if (result.tools.length !== 8) {
        throw new Error(`Expected 8 tools, got ${result.tools.length}`);
      }
      const toolNames = result.tools.map(t => t.name);
      const expectedTools = [
        'memory_create', 'memory_read', 'memory_update',
        'memory_delete', 'memory_search', 'memory_list',
        'memory_stats', 'memory_enrich'
      ];
      for (const expected of expectedTools) {
        if (!toolNames.includes(expected)) {
          throw new Error(`Missing tool: ${expected}`);
        }
      }
      console.log(`   Found all 8 tools: ${toolNames.join(', ')}`);
    });

    // Test 2: List Resources
    await test('List Resources', async () => {
      const result = await client.listResources();
      if (result.resources.length !== 3) {
        throw new Error(`Expected 3 resources, got ${result.resources.length}`);
      }
      const uris = result.resources.map(r => r.uri);
      console.log(`   Found all 3 resources: ${uris.join(', ')}`);
    });

    // Test 3: Create Semantic Memory (without enrichment)
    await test('Create Semantic Memory', async () => {
      const result = await client.callTool({
        name: 'memory_create',
        arguments: {
          content: 'Test semantic memory - MCP enables persistent context',
          type: 'semantic',
          tags: ['test', 'mcp', 'semantic'],
          enrich: false
        }
      });

      const response = JSON.parse(result.content[0].text);
      if (!response.success) {
        throw new Error('Failed to create memory');
      }
      createdMemoryIds.push(response.memory.id);
      console.log(`   Created memory with ID: ${response.memory.id.substring(0, 8)}...`);
    });

    // Test 4: Create Episodic Memory (without enrichment)
    await test('Create Episodic Memory', async () => {
      const result = await client.callTool({
        name: 'memory_create',
        arguments: {
          content: 'Test episodic memory - Meeting on Oct 29, 2025 at 2pm',
          type: 'episodic',
          tags: ['test', 'meeting', 'episodic'],
          enrich: false
        }
      });

      const response = JSON.parse(result.content[0].text);
      if (!response.success) {
        throw new Error('Failed to create memory');
      }
      createdMemoryIds.push(response.memory.id);
      console.log(`   Created memory with ID: ${response.memory.id.substring(0, 8)}...`);
    });

    // Test 5: Read Memory
    await test('Read Memory', async () => {
      const memoryId = createdMemoryIds[0];
      const result = await client.callTool({
        name: 'memory_read',
        arguments: {
          id: memoryId
        }
      });

      const response = JSON.parse(result.content[0].text);
      if (!response.success) {
        throw new Error('Failed to read memory');
      }
      console.log(`   Read memory: ${response.memory.content.substring(0, 40)}...`);
      console.log(`   Access count: ${response.memory.metadata.accessCount}`);
    });

    // Test 6: Update Memory
    await test('Update Memory', async () => {
      const memoryId = createdMemoryIds[0];
      const result = await client.callTool({
        name: 'memory_update',
        arguments: {
          id: memoryId,
          content: 'Updated test memory - MCP enables persistent AI context',
          tags: ['test', 'mcp', 'updated']
        }
      });

      const response = JSON.parse(result.content[0].text);
      if (!response.success) {
        throw new Error('Failed to update memory');
      }
      console.log(`   Updated memory successfully`);
    });

    // Test 7: Search Memories
    await test('Search Memories', async () => {
      const result = await client.callTool({
        name: 'memory_search',
        arguments: {
          query: 'test',
          limit: 10
        }
      });

      const response = JSON.parse(result.content[0].text);
      if (!response.success) {
        throw new Error('Failed to search memories');
      }
      console.log(`   Found ${response.count} memories matching "test"`);
    });

    // Test 8: List Memories
    await test('List Memories', async () => {
      const result = await client.callTool({
        name: 'memory_list',
        arguments: {
          type: 'all',
          limit: 20
        }
      });

      const response = JSON.parse(result.content[0].text);
      if (!response.success) {
        throw new Error('Failed to list memories');
      }
      console.log(`   Listed ${response.count} memories`);
    });

    // Test 9: Get Statistics
    await test('Get Statistics', async () => {
      const result = await client.callTool({
        name: 'memory_stats',
        arguments: {}
      });

      const response = JSON.parse(result.content[0].text);
      if (!response.success) {
        throw new Error('Failed to get stats');
      }
      console.log(`   Total memories: ${response.stats.total}`);
      console.log(`   Episodic: ${response.stats.episodic}, Semantic: ${response.stats.semantic}`);
      console.log(`   Enrichment rate: ${response.stats.enrichmentRate}`);
    });

    // Test 10: Enrich Memory (will use fallback if no API key)
    await test('Enrich Memory', async () => {
      const memoryId = createdMemoryIds[1];
      const result = await client.callTool({
        name: 'memory_enrich',
        arguments: {
          id: memoryId
        }
      });

      const response = JSON.parse(result.content[0].text);
      if (!response.success) {
        throw new Error('Failed to enrich memory');
      }
      console.log(`   Enriched via: ${response.memory.metadata.enrichmentMethod}`);
      if (response.memory.enrichment) {
        console.log(`   Category: ${response.memory.enrichment.category}`);
        console.log(`   Sentiment: ${response.memory.enrichment.sentiment}`);
      }
    });

    // Test 11: Read Resource - Overview
    await test('Read Resource: Overview', async () => {
      const result = await client.readResource({
        uri: 'memory://overview'
      });

      if (!result.contents || result.contents.length === 0) {
        throw new Error('No content returned');
      }
      const content = result.contents[0].text;
      if (!content.includes('CoreText Memory System Overview')) {
        throw new Error('Overview content missing expected header');
      }
      console.log(`   Overview length: ${content.length} characters`);
    });

    // Test 12: Read Resource - Context Stream
    await test('Read Resource: Context Stream', async () => {
      const result = await client.readResource({
        uri: 'memory://context-stream'
      });

      if (!result.contents || result.contents.length === 0) {
        throw new Error('No content returned');
      }
      const content = JSON.parse(result.contents[0].text);
      if (!content.activeTopics) {
        throw new Error('Context stream missing activeTopics');
      }
      console.log(`   Active topics: ${content.activeTopics.slice(0, 5).join(', ')}`);
      console.log(`   Recent context items: ${content.recentContext.length}`);
    });

    // Test 13: Read Resource - Knowledge Graph
    await test('Read Resource: Knowledge Graph', async () => {
      const result = await client.readResource({
        uri: 'memory://knowledge-graph'
      });

      if (!result.contents || result.contents.length === 0) {
        throw new Error('No content returned');
      }
      const content = JSON.parse(result.contents[0].text);
      if (!content.nodes) {
        throw new Error('Knowledge graph missing nodes');
      }
      console.log(`   Nodes: ${content.metadata.totalNodes}`);
      console.log(`   Edges: ${content.metadata.totalEdges}`);
      console.log(`   Clusters: ${content.metadata.clusters}`);
    });

    // Test 14: Delete Memory (cleanup test memories)
    await test('Delete Test Memories', async () => {
      for (const memoryId of createdMemoryIds) {
        const result = await client.callTool({
          name: 'memory_delete',
          arguments: {
            id: memoryId
          }
        });

        const response = JSON.parse(result.content[0].text);
        if (!response.success) {
          throw new Error(`Failed to delete memory ${memoryId}`);
        }
      }
      console.log(`   Deleted ${createdMemoryIds.length} test memories`);
    });

    // Summary
    console.log('\n============================================');
    console.log('📊 Test Results');
    console.log('============================================');
    console.log(`✅ Passed: ${testsPassed}`);
    console.log(`❌ Failed: ${testsFailed}`);
    console.log(`📈 Success Rate: ${((testsPassed / (testsPassed + testsFailed)) * 100).toFixed(1)}%`);
    console.log('============================================\n');

    if (testsFailed === 0) {
      console.log('🎉 All tests passed! Server is ready for teaching.');
      console.log('\nNext steps:');
      console.log('1. Run: npm run inspector');
      console.log('2. Open: http://localhost:5173');
      console.log('3. Test tools manually in the Inspector UI\n');
    } else {
      console.log('⚠️  Some tests failed. Please review errors above.\n');
      process.exit(1);
    }

  } catch (error) {
    console.error('\n❌ Test suite error:', error.message);
    process.exit(1);
  } finally {
    await client.close();
    serverProcess.kill();
  }
}

async function test(name, fn) {
  process.stdout.write(`🧪 ${name}... `);
  try {
    await fn();
    console.log('✅ PASS');
    testsPassed++;
  } catch (error) {
    console.log('❌ FAIL');
    console.log(`   Error: ${error.message}`);
    testsFailed++;
  }
}

runTests().catch(error => {
  console.error('Fatal error:', error);
  process.exit(1);
});
