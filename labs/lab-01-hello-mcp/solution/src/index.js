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

// McpServer is the high-level class that exposes .tool(). The low-level Server
// (from server/index.js) has no .tool() method, so importing that and calling
// server.tool() throws "server.tool is not a function" at startup.
import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';

// .tool() expects a Zod "raw shape" for the input schema (not a hand-written
// JSON Schema object). The SDK converts the shape to JSON Schema for the client
// and validates/coerces arguments before your handler runs.
import { z } from 'zod';

async function main() {
  // Create server instance
  const server = new McpServer(
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
      a: z.number().describe('First number'),
      b: z.number().describe('Second number')
    },
    async ({ a, b }) => {
      // Zod guarantees a and b are numbers; guard the non-finite edge cases
      // (z.number() admits NaN/Infinity).
      if (!Number.isFinite(a) || !Number.isFinite(b)) {
        throw new Error('Both parameters must be finite numbers');
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
