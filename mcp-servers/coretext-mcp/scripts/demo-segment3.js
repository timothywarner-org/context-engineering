#!/usr/bin/env node
/**
 * SEGMENT 3 DEMO: ADVANCED PATTERNS - MULTI-AGENT MEMORY
 * Duration: 55 minutes
 * Focus: Knowledge graphs, context streams, CRUD deep dive
 */

import { Client } from '@modelcontextprotocol/sdk/client/index.js';
import { StdioClientTransport } from '@modelcontextprotocol/sdk/client/stdio.js';

console.log('\n' + '='.repeat(60));
console.log('🕸️  SEGMENT 3: ADVANCED PATTERNS - MULTI-AGENT MEMORY');
console.log('='.repeat(60) + '\n');

const demos = [
  {
    title: 'Demo 9: Building the Knowledge Graph',
    description: 'Creating interconnected memories',
    async run(client) {
      console.log('Creating interconnected memories about MCP...\n');

      const memories = [
        {
          content: "MCP enables persistent context for AI assistants",
          tags: ["mcp", "context", "ai"]
        },
        {
          content: "Context persistence solves the token window limitation",
          tags: ["context", "tokens", "limitation"]
        },
        {
          content: "AI assistants like Claude and ChatGPT benefit from MCP",
          tags: ["ai", "claude", "chatgpt", "mcp"]
        }
      ];

      for (const mem of memories) {
        await client.callTool({
          name: 'memory_create',
          arguments: {
            content: mem.content,
            type: 'semantic',
            tags: mem.tags,
            enrich: false
          }
        });
        console.log(`✅ Created: ${mem.content.substring(0, 45)}...`);
      }

      console.log('\n💡 Notice: These memories share tags:');
      console.log('   "mcp" appears in memories 1 & 3');
      console.log('   "context" appears in memories 1 & 2');
      console.log('   "ai" appears in memories 1 & 3');
      console.log('\n   This creates automatic connections!');
    }
  },
  {
    title: 'Demo 9: View Knowledge Graph',
    description: 'Seeing memory connections',
    async run(client) {
      console.log('Reading memory://knowledge-graph resource...\n');
      const result = await client.readResource({
        uri: 'memory://knowledge-graph'
      });

      const graph = JSON.parse(result.contents[0].text);
      console.log('🕸️  Knowledge Graph:');
      console.log(`   Nodes (memories): ${graph.metadata.totalNodes}`);
      console.log(`   Edges (connections): ${graph.metadata.totalEdges}`);
      console.log(`   Clusters: ${graph.metadata.clusters}`);
      console.log(`   Graph Density: ${graph.metadata.graphDensity}`);

      if (graph.insights.strongestConnections.length > 0) {
        console.log('\n🔗 Strongest Connections:');
        graph.insights.strongestConnections.slice(0, 5).forEach((conn, i) => {
          console.log(`   ${i + 1}. [${conn.strength}] ${conn.source} ↔ ${conn.target}`);
          console.log(`      Via: ${conn.basis.join(', ')}`);
        });
      }

      if (graph.clusters.length > 0) {
        console.log('\n🎯 Knowledge Clusters:');
        graph.clusters.forEach((cluster, i) => {
          console.log(`   Cluster ${i + 1}: ${cluster.size} memories`);
          console.log(`      Theme: ${cluster.theme}`);
          console.log(`      Common tags: ${cluster.commonTags.join(', ')}`);
        });
      }

      console.log('\n💡 Memories form semantic networks naturally!');
      console.log('   This is how human knowledge works too.');
    }
  },
  {
    title: 'Demo 10: Context Stream in Action',
    description: 'Watching memory flow through time windows',
    async run(client) {
      console.log('Creating memories at "different times"...\n');

      // Create some new memories
      for (let i = 1; i <= 3; i++) {
        await client.callTool({
          name: 'memory_create',
          arguments: {
            content: `Context stream test memory #${i} - created just now`,
            type: 'episodic',
            tags: ['test', 'stream', 'demo'],
            enrich: false
          }
        });
        console.log(`✅ Created test memory #${i}`);
      }

      console.log('\nReading context stream...\n');
      const result = await client.readResource({
        uri: 'memory://context-stream'
      });

      const stream = JSON.parse(result.contents[0].text);
      console.log('🌊 Context Stream Analysis:');
      console.log(`   Active Topics: ${stream.activeTopics.slice(0, 8).join(', ')}`);
      console.log(`   Dominant Type: ${stream.dominantType}`);

      console.log('\n⏰ Time Windows:');
      console.log(`   Recent (<1 hour): ${stream.recentContext.length} memories`);
      console.log(`   Today (<24 hours): ${stream.todayContext.length} memories`);
      console.log(`   Earlier (older): ${stream.earlierContext} memories`);

      if (stream.recentContext.length > 0) {
        console.log('\n🔥 Recent Context:');
        stream.recentContext.slice(0, 5).forEach((m, i) => {
          console.log(`   ${i + 1}. ${m.content.substring(0, 50)}...`);
        });
      }

      console.log('\n💡 This is "working memory" for AI!');
      console.log('   Recent = high priority, Earlier = archived');
    }
  },
  {
    title: 'Demo 11: Full CRUD Cycle',
    description: 'Complete lifecycle of a memory',
    async run(client) {
      console.log('Demonstrating full CRUD cycle...\n');

      // CREATE
      console.log('1️⃣  CREATE a memory');
      const createResult = await client.callTool({
        name: 'memory_create',
        arguments: {
          content: "CRUD demo: This memory will go through create, read, update, delete",
          type: 'semantic',
          tags: ['demo', 'crud', 'lifecycle'],
          enrich: false
        }
      });
      const created = JSON.parse(createResult.content[0].text);
      const memoryId = created.memory.id;
      console.log(`   ✅ Created with ID: ${memoryId.substring(0, 8)}...`);
      console.log(`   Created at: ${created.memory.metadata.created}`);

      // READ
      console.log('\n2️⃣  READ the memory');
      const readResult = await client.callTool({
        name: 'memory_read',
        arguments: { id: memoryId }
      });
      const read = JSON.parse(readResult.content[0].text);
      console.log(`   ✅ Read successfully`);
      console.log(`   Access count: ${read.memory.metadata.accessCount}`);
      console.log(`   Last accessed: ${read.memory.metadata.lastAccessed}`);

      // UPDATE
      console.log('\n3️⃣  UPDATE the memory');
      const updateResult = await client.callTool({
        name: 'memory_update',
        arguments: {
          id: memoryId,
          content: "CRUD demo: This memory was UPDATED to show modification capability",
          tags: ['demo', 'crud', 'updated', 'modified']
        }
      });
      const updated = JSON.parse(updateResult.content[0].text);
      console.log(`   ✅ Updated successfully`);
      console.log(`   Updated at: ${updated.memory.metadata.updated}`);
      console.log(`   New tags: ${updated.memory.tags.join(', ')}`);

      // DELETE
      console.log('\n4️⃣  DELETE the memory');
      const deleteResult = await client.callTool({
        name: 'memory_delete',
        arguments: { id: memoryId }
      });
      const deleted = JSON.parse(deleteResult.content[0].text);
      console.log(`   ✅ Deleted successfully`);

      console.log('\n💡 Complete CRUD cycle demonstrated!');
      console.log('   Every operation tracked in metadata');
    }
  },
  {
    title: 'Demo 12: Multi-Agent Scenario',
    description: 'Customer service + technical support sharing memory',
    async run(client) {
      console.log('Simulating multi-agent memory sharing...\n');

      console.log('👥 Agent 1: Customer Service');
      const cs = await client.callTool({
        name: 'memory_create',
        arguments: {
          content: "Customer reported login issues with error code 403",
          type: 'episodic',
          tags: ['customer', 'login', 'error', 'support'],
          enrich: false
        }
      });
      const csMemory = JSON.parse(cs.content[0].text);
      console.log(`   ✅ Created: ${csMemory.memory.content}`);

      console.log('\n🔍 Agent 2: Technical Support searches');
      const search = await client.callTool({
        name: 'memory_search',
        arguments: {
          query: 'error',
          limit: 5
        }
      });
      const searchResult = JSON.parse(search.content[0].text);
      console.log(`   ✅ Found ${searchResult.count} error-related memories`);

      console.log('\n🛠️  Agent 2: Creates solution');
      const tech = await client.callTool({
        name: 'memory_create',
        arguments: {
          content: "Error 403 is caused by expired authentication tokens - solution is to refresh credentials",
          type: 'semantic',
          tags: ['error', 'authentication', 'solution', 'technical'],
          enrich: false
        }
      });
      const techMemory = JSON.parse(tech.content[0].text);
      console.log(`   ✅ Created: ${techMemory.memory.content.substring(0, 60)}...`);

      console.log('\n🕸️  Checking knowledge graph connection...');
      const graph = await client.readResource({
        uri: 'memory://knowledge-graph'
      });
      const graphData = JSON.parse(graph.contents[0].text);

      console.log('\n💡 Both agents now share context!');
      console.log('   Customer Service memory: episodic (the incident)');
      console.log('   Technical Support memory: semantic (the solution)');
      console.log('   Connected via: "error" tag');
      console.log(`   Total connections: ${graphData.metadata.totalEdges} edges`);
    }
  }
];

async function runSegment3() {
  const transport = new StdioClientTransport({
    command: 'node',
    args: ['src/index.js'],
    stderr: 'pipe'
  });

  const client = new Client(
    {
      name: 'demo-segment3',
      version: '1.0.0'
    },
    {
      capabilities: {}
    }
  );

  try {
    await client.connect(transport);
    console.log('🔌 Connected to MCP server\n');

    for (const demo of demos) {
      console.log('\n' + '-'.repeat(60));
      console.log(`🎯 ${demo.title}`);
      console.log(`   ${demo.description}`);
      console.log('-'.repeat(60) + '\n');

      await demo.run(client);

      console.log('\n⏸️  Press Enter to continue to next demo...');
      await new Promise(resolve => {
        process.stdin.once('data', resolve);
      });
    }

    console.log('\n' + '='.repeat(60));
    console.log('✅ SEGMENT 3 COMPLETE!');
    console.log('='.repeat(60));
    console.log('\n📊 Key Takeaways:');
    console.log('   ✓ Saw memories connect into knowledge graphs');
    console.log('   ✓ Understood context streams and time windows');
    console.log('   ✓ Mastered complete CRUD lifecycle');
    console.log('   ✓ Experienced multi-agent memory sharing');
    console.log('\n🎓 Student Exercise Ideas:');
    console.log('   1. Create a cluster of 5+ related memories');
    console.log('   2. Use consistent tags to strengthen connections');
    console.log('   3. View knowledge graph to see the cluster');
    console.log('   4. Simulate two agents working together');
    console.log('\n📖 This completes the technical segments!');
    console.log('   Segment 4 (Production Reality) uses Azure Portal/CLI');
    console.log('='.repeat(60) + '\n');

  } catch (error) {
    console.error('\n❌ Demo failed:', error.message);
    process.exit(1);
  } finally {
    await client.close();
  }
}

// Non-interactive mode if --auto flag
if (process.argv.includes('--auto')) {
  console.log('🤖 Running in automatic mode (no pauses)\n');
  const originalStdin = process.stdin.once;
  process.stdin.once = (event, callback) => {
    if (event === 'data') {
      setTimeout(callback, 100);
    }
  };
}

runSegment3();
