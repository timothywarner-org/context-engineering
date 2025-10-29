#!/usr/bin/env node
/**
 * SEGMENT 1 DEMO: FROM PROMPTS TO PERSISTENT CONTEXT
 * Duration: 55 minutes
 * Focus: Basic CRUD, persistence across restarts
 */

import { Client } from '@modelcontextprotocol/sdk/client/index.js';
import { StdioClientTransport } from '@modelcontextprotocol/sdk/client/stdio.js';

console.log('\n' + '='.repeat(60));
console.log('📚 SEGMENT 1: FROM PROMPTS TO PERSISTENT CONTEXT');
console.log('='.repeat(60) + '\n');

const demos = [
  {
    title: 'Demo 3: Create Your First Memory',
    description: 'Creating a semantic memory (fact-based)',
    async run(client) {
      console.log('Creating semantic memory about preferences...');
      const result = await client.callTool({
        name: 'memory_create',
        arguments: {
          content: "Tim prefers dark themes and uses VS Code with Monokai Pro",
          type: "semantic",
          tags: ["preferences", "tim", "vscode"],
          enrich: false
        }
      });

      const response = JSON.parse(result.content[0].text);
      console.log('\n✅ Memory Created!');
      console.log(`   ID: ${response.memory.id}`);
      console.log(`   Type: ${response.memory.type}`);
      console.log(`   Created: ${response.memory.metadata.created}`);
      console.log(`   Tags: ${response.memory.tags.join(', ')}`);
      return response.memory.id;
    }
  },
  {
    title: 'Demo 4: Prove Persistence',
    description: 'Listing memories to show persistence',
    async run(client) {
      console.log('Listing all memories...');
      const result = await client.callTool({
        name: 'memory_list',
        arguments: {
          type: 'all',
          limit: 20
        }
      });

      const response = JSON.parse(result.content[0].text);
      console.log(`\n✅ Found ${response.count} memories in the system`);
      console.log('\nRecent memories:');
      response.memories.slice(0, 3).forEach((m, i) => {
        const typeEmoji = m.type === 'episodic' ? '📅' : '💡';
        console.log(`   ${i + 1}. ${typeEmoji} ${m.content.substring(0, 50)}...`);
      });
    }
  },
  {
    title: 'Exercise 1: Student Practice - Create Semantic Memory',
    description: 'Students create a fact about themselves',
    async run(client) {
      console.log('Example: Creating a semantic memory about yourself...');
      const result = await client.callTool({
        name: 'memory_create',
        arguments: {
          content: "I am learning MCP to build context-aware AI applications",
          type: "semantic",
          tags: ["learning", "mcp", "ai", "student"],
          enrich: false
        }
      });

      const response = JSON.parse(result.content[0].text);
      console.log('\n✅ Student memory created!');
      console.log(`   Content: ${response.memory.content}`);
      console.log(`   Type: ${response.memory.type}`);
      return response.memory.id;
    }
  },
  {
    title: 'Exercise 1: Student Practice - Create Episodic Memory',
    description: 'Students create an event memory',
    async run(client) {
      console.log('Example: Creating an episodic memory about today...');
      const result = await client.callTool({
        name: 'memory_create',
        arguments: {
          content: "Started O'Reilly Context Engineering course on Oct 29, 2025",
          type: "episodic",
          tags: ["training", "oreilly", "event", "student"],
          enrich: false
        }
      });

      const response = JSON.parse(result.content[0].text);
      console.log('\n✅ Student event created!');
      console.log(`   Content: ${response.memory.content}`);
      console.log(`   Type: ${response.memory.type}`);
      return response.memory.id;
    }
  },
  {
    title: 'Exercise 1: Search Your Memories',
    description: 'Finding memories by keyword',
    async run(client) {
      console.log('Searching for "student" memories...');
      const result = await client.callTool({
        name: 'memory_search',
        arguments: {
          query: 'student',
          limit: 10
        }
      });

      const response = JSON.parse(result.content[0].text);
      console.log(`\n✅ Found ${response.count} matching memories`);
      if (response.count > 0) {
        console.log('\nMatches:');
        response.memories.forEach((m, i) => {
          console.log(`   ${i + 1}. ${m.content.substring(0, 60)}...`);
        });
      }
    }
  }
];

async function runSegment1() {
  const transport = new StdioClientTransport({
    command: 'node',
    args: ['src/index.js'],
    stderr: 'pipe'
  });

  const client = new Client(
    {
      name: 'demo-segment1',
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
    console.log('✅ SEGMENT 1 COMPLETE!');
    console.log('='.repeat(60));
    console.log('\n📊 Key Takeaways:');
    console.log('   ✓ Created semantic memories (facts)');
    console.log('   ✓ Created episodic memories (events)');
    console.log('   ✓ Searched and retrieved memories');
    console.log('   ✓ Saw persistence in action');
    console.log('\n🎓 Now try:');
    console.log('   1. Stop the server (Ctrl+C)');
    console.log('   2. Restart it: npm run dev');
    console.log('   3. Run: npm run demo:segment1 again');
    console.log('   4. Notice: All memories are still there!');
    console.log('\n📖 Next: npm run demo:segment2');
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

runSegment1();
