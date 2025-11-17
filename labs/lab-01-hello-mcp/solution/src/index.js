#!/usr/bin/env node

/**
 * Lab 01: Hello MCP - Solution
 *
 * A simple calculator MCP server that demonstrates:
 * - Basic server setup
 * - Tool registration
 * - Parameter validation
 * - Response formatting
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';

async function main() {
  // Create server instance
  const server = new Server(
    {
      name: 'hello-mcp',
      version: '1.0.0'
    },
    {
      capabilities: {
        tools: {}  // This server provides tools
      }
    }
  );

  // Register the 'add' tool
  server.tool(
    'add',
    'Adds two numbers together',
    {
      type: 'object',
      properties: {
        a: {
          type: 'number',
          description: 'First number'
        },
        b: {
          type: 'number',
          description: 'Second number'
        }
      },
      required: ['a', 'b']
    },
    async ({ a, b }) => {
      // Validate inputs
      if (typeof a !== 'number' || typeof b !== 'number') {
        throw new Error('Both parameters must be numbers');
      }

      // Perform calculation
      const sum = a + b;

      // Log to stderr for debugging
      console.error(`[add] ${a} + ${b} = ${sum}`);

      // Return result in MCP format
      return {
        content: [{
          type: 'text',
          text: `The sum of ${a} and ${b} is ${sum}`
        }]
      };
    }
  );

  // Create stdio transport and connect
  const transport = new StdioServerTransport();
  await server.connect(transport);

  console.error('Hello MCP Server started successfully');
  console.error('Waiting for MCP client connection...');
}

// Run the server
main().catch((error) => {
  console.error('Fatal error:', error);
  process.exit(1);
});
