#!/usr/bin/env node
/**
 * SEGMENT 2 DEMO: BUILDING YOUR CONTEXT STACK
 * Duration: 55 minutes
 * Focus: Memory types, enrichment, resources
 */

import { Client } from '@modelcontextprotocol/sdk/client/index.js';
import { StdioClientTransport } from '@modelcontextprotocol/sdk/client/stdio.js';

console.log('\n' + '='.repeat(60));
console.log('🏗️  SEGMENT 2: BUILDING YOUR CONTEXT STACK');
console.log('='.repeat(60) + '\n');

const demos = [
  {
    title: 'Demo 5: The Two Memory Types',
    description: 'Creating related episodic and semantic memories',
    async run(client) {
      console.log('Creating EPISODIC memory (event)...');
      const episodic = await client.callTool({
        name: 'memory_create',
        arguments: {
          content: "Had breakthrough discussion about MCP authentication at 2:15pm with the team",
          type: "episodic",
          tags: ["meeting", "mcp", "authentication", "team"],
          enrich: false
        }
      });

      const ep = JSON.parse(episodic.content[0].text);
      console.log(`✅ Episodic: ${ep.memory.content.substring(0, 50)}...`);

      console.log('\nCreating SEMANTIC memory (fact)...');
      const semantic = await client.callTool({
        name: 'memory_create',
        arguments: {
          content: "MCP authentication uses API keys stored in environment variables for security",
          type: "semantic",
          tags: ["mcp", "authentication", "security", "api"],
          enrich: false
        }
      });

      const sem = JSON.parse(semantic.content[0].text);
      console.log(`✅ Semantic: ${sem.memory.content.substring(0, 50)}...`);

      console.log('\nNotice: Same topic, different memory types!');
      console.log('   📅 Episodic = WHEN it happened (timeline)');
      console.log('   💡 Semantic = WHAT we learned (knowledge)');

      return [ep.memory.id, sem.memory.id];
    }
  },
  {
    title: 'Demo 5: Check Statistics',
    description: 'View breakdown by memory type',
    async run(client) {
      console.log('Getting memory statistics...');
      const result = await client.callTool({
        name: 'memory_stats',
        arguments: {}
      });

      const stats = JSON.parse(result.content[0].text);
      console.log('\n📊 Memory System Stats:');
      console.log(`   Total: ${stats.stats.total}`);
      console.log(`   📅 Episodic (events): ${stats.stats.episodic}`);
      console.log(`   💡 Semantic (facts): ${stats.stats.semantic}`);
      console.log(`   ✨ Enriched: ${stats.stats.enriched}`);
      console.log(`   🏷️  Tags: ${stats.stats.tags.length} unique`);

      if (stats.stats.mostAccessed.length > 0) {
        console.log('\n🔥 Most Accessed:');
        stats.stats.mostAccessed.slice(0, 3).forEach((m, i) => {
          console.log(`   ${i + 1}. [${m.accessCount}x] ${m.content}`);
        });
      }
    }
  },
  {
    title: 'Demo 6: Search and Discovery',
    description: 'Finding memories by tag and content',
    async run(client) {
      console.log('Searching for "authentication"...');
      const result = await client.callTool({
        name: 'memory_search',
        arguments: {
          query: 'authentication',
          limit: 10
        }
      });

      const response = JSON.parse(result.content[0].text);
      console.log(`\n✅ Found ${response.count} memories`);
      console.log('\nResults:');
      response.memories.forEach((m, i) => {
        const typeEmoji = m.type === 'episodic' ? '📅' : '💡';
        console.log(`   ${i + 1}. ${typeEmoji} ${m.content.substring(0, 55)}...`);
        console.log(`      Tags: ${m.tags.join(', ')}`);
      });

      console.log('\n💡 Notice: Both types returned because they share tags!');
    }
  },
  {
    title: 'Demo 7: Enrichment with AI',
    description: 'Adding AI analysis to memories',
    async run(client) {
      console.log('Creating memory WITH enrichment...');
      const result = await client.callTool({
        name: 'memory_create',
        arguments: {
          content: "Azure Container Apps provides serverless containers with automatic scaling and built-in KEDA support",
          type: "semantic",
          tags: ["azure", "containers", "serverless"],
          enrich: true  // Enable enrichment!
        }
      });

      const response = JSON.parse(result.content[0].text);
      console.log('\n✅ Memory created AND enriched!');
      console.log(`   Method: ${response.memory.metadata.enrichmentMethod}`);

      if (response.memory.enrichment) {
        console.log('\n🧪 Enrichment Analysis:');
        console.log(`   Summary: ${response.memory.enrichment.summary || 'N/A'}`);
        console.log(`   Category: ${response.memory.enrichment.category}`);
        console.log(`   Sentiment: ${response.memory.enrichment.sentiment}`);
        if (response.memory.enrichment.keywords) {
          console.log(`   Keywords: ${response.memory.enrichment.keywords.join(', ')}`);
        }
        if (response.memory.enrichment.processingTime) {
          console.log(`   Processing: ${response.memory.enrichment.processingTime}`);
        }
      }

      console.log('\n💡 Enrichment works WITH Deepseek API or WITHOUT (fallback)');
      return response.memory.id;
    }
  },
  {
    title: 'Demo 8: Resource Access - Overview',
    description: 'Reading the markdown dashboard',
    async run(client) {
      console.log('Reading memory://overview resource...');
      const result = await client.readResource({
        uri: 'memory://overview'
      });

      const content = result.contents[0].text;
      console.log('\n📊 Overview Resource (first 500 chars):');
      console.log('-'.repeat(60));
      console.log(content.substring(0, 500) + '...');
      console.log('-'.repeat(60));
      console.log('\n💡 This resource is ALWAYS available (no tool call needed)');
      console.log('   AI can access it automatically for context!');
    }
  },
  {
    title: 'Demo 8: Resource Access - Context Stream',
    description: 'Viewing real-time context',
    async run(client) {
      console.log('Reading memory://context-stream resource...');
      const result = await client.readResource({
        uri: 'memory://context-stream'
      });

      const content = JSON.parse(result.contents[0].text);
      console.log('\n🌊 Context Stream:');
      console.log(`   Active Topics: ${content.activeTopics.slice(0, 8).join(', ')}`);
      console.log(`   Dominant Type: ${content.dominantType}`);
      console.log(`   Recent Items: ${content.recentContext.length}`);
      console.log(`   Today Items: ${content.todayContext.length}`);

      if (content.recentContext.length > 0) {
        console.log('\n🔥 Most Recent:');
        content.recentContext.slice(0, 3).forEach((m, i) => {
          const typeEmoji = m.type === 'episodic' ? '📅' : '💡';
          console.log(`   ${typeEmoji} ${m.content.substring(0, 50)}...`);
        });
      }

      console.log('\n💡 This maintains conversation continuity!');
      console.log('   Perfect for multi-turn AI interactions');
    }
  }
];

async function runSegment2() {
  const transport = new StdioClientTransport({
    command: 'node',
    args: ['src/index.js'],
    stderr: 'pipe'
  });

  const client = new Client(
    {
      name: 'demo-segment2',
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
    console.log('✅ SEGMENT 2 COMPLETE!');
    console.log('='.repeat(60));
    console.log('\n📊 Key Takeaways:');
    console.log('   ✓ Understood episodic vs semantic memory');
    console.log('   ✓ Used AI enrichment (with fallback)');
    console.log('   ✓ Accessed resources for context');
    console.log('   ✓ Saw tag-based memory connections');
    console.log('\n🎓 Student Exercise Ideas:');
    console.log('   1. Create 3 related memories (same topic, different types)');
    console.log('   2. Enrich one with AI analysis');
    console.log('   3. Search to find the connections');
    console.log('   4. View context-stream to see them grouped');
    console.log('\n📖 Next: npm run demo:segment3');
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

runSegment2();
