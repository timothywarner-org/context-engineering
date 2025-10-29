#!/usr/bin/env node
/**
 * Demo Populate Script
 * Creates example memories for teaching demonstrations
 */

import { Client } from '@modelcontextprotocol/sdk/client/index.js';
import { StdioClientTransport } from '@modelcontextprotocol/sdk/client/stdio.js';

console.log('\n📚 DEMO POPULATE - Creating Example Memories\n');
console.log('============================================\n');

const examples = [
  {
    content: "Tim Warner teaches Context Engineering with MCP at O'Reilly",
    type: "semantic",
    tags: ["instructor", "oreilly", "mcp", "teaching"]
  },
  {
    content: "Had breakthrough discussion about persistent AI memory on Oct 29, 2025 at 2pm",
    type: "episodic",
    tags: ["meeting", "memory", "ai", "breakthrough"]
  },
  {
    content: "MCP (Model Context Protocol) solves the AI amnesia problem by providing persistent context",
    type: "semantic",
    tags: ["mcp", "context", "ai", "protocol"]
  },
  {
    content: "Azure Container Apps provides serverless containers with automatic scaling and KEDA support",
    type: "semantic",
    tags: ["azure", "containers", "serverless", "cloud"]
  },
  {
    content: "Student asked excellent question about RAG vs MCP during live training session",
    type: "episodic",
    tags: ["training", "question", "rag", "mcp"]
  },
  {
    content: "Deepseek API provides cost-effective AI enrichment for memory analysis",
    type: "semantic",
    tags: ["deepseek", "api", "enrichment", "ai"]
  },
  {
    content: "Deployed first MCP server to Azure successfully on Oct 28, 2025",
    type: "episodic",
    tags: ["deployment", "azure", "mcp", "success"]
  },
  {
    content: "Cosmos DB replaces JSON file storage for production-scale MCP servers",
    type: "semantic",
    tags: ["cosmosdb", "storage", "production", "azure"]
  },
  {
    content: "VS Code and Claude Desktop both support MCP natively",
    type: "semantic",
    tags: ["vscode", "claude", "mcp", "integration"]
  },
  {
    content: "Class feedback session revealed students want more hands-on Azure deployment practice",
    type: "episodic",
    tags: ["feedback", "students", "azure", "training"]
  }
];

async function populate() {
  const transport = new StdioClientTransport({
    command: 'node',
    args: ['src/index.js'],
    stderr: 'pipe'
  });

  const client = new Client(
    {
      name: 'demo-populate',
      version: '1.0.0'
    },
    {
      capabilities: {}
    }
  );

  try {
    await client.connect(transport);
    console.log('✅ Connected to server\n');

    let created = 0;
    for (const example of examples) {
      try {
        const result = await client.callTool({
          name: 'memory_create',
          arguments: example
        });

        const response = JSON.parse(result.content[0].text);
        if (response.success) {
          created++;
          const typeEmoji = example.type === 'episodic' ? '📅' : '💡';
          console.log(`${typeEmoji} Created ${example.type}: ${example.content.substring(0, 50)}...`);
        }
      } catch (error) {
        console.error(`❌ Failed to create: ${example.content.substring(0, 40)}...`);
      }
    }

    console.log('\n============================================');
    console.log(`✅ Created ${created}/${examples.length} example memories`);
    console.log('============================================\n');

    // Show stats
    const statsResult = await client.callTool({
      name: 'memory_stats',
      arguments: {}
    });

    const stats = JSON.parse(statsResult.content[0].text);
    if (stats.success) {
      console.log('📊 Memory System Statistics:');
      console.log(`   Total: ${stats.stats.total}`);
      console.log(`   Episodic: ${stats.stats.episodic}`);
      console.log(`   Semantic: ${stats.stats.semantic}`);
      console.log(`   Tags: ${stats.stats.tags.length} unique`);
    }

    console.log('\n============================================');
    console.log('Next steps:');
    console.log('1. npm run inspector    - View memories in Inspector');
    console.log('2. npm run demo:segment1 - Run Segment 1 demos');
    console.log('3. npm run demo:segment2 - Run Segment 2 demos');
    console.log('============================================\n');

  } catch (error) {
    console.error('\n❌ Population failed:', error.message);
    process.exit(1);
  } finally {
    await client.close();
  }
}

populate();
