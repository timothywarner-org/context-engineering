#!/usr/bin/env node

/**
 * Lab 01: Hello MCP - Your First MCP Server
 *
 * A minimal calculator MCP server that demonstrates:
 * - Server setup (high-level McpServer)
 * - Tool registration with a typed input schema
 * - Parameter validation
 * - MCP-formatted responses
 * - stdio transport (how Claude Desktop / Inspector launch local servers)
 */

// Why McpServer (not the low-level Server): McpServer exposes the .tool()
// convenience method this lab uses. The low-level Server has no .tool(), which
// is what made the starter throw on launch.
import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';

// Why zod: SDK 1.x's .tool() expects a Zod "raw shape" for the input schema,
// not a hand-written JSON Schema object. The SDK converts the shape to JSON
// Schema for the client AND validates/coerces args before your handler runs.
import { z } from 'zod';

async function main() {
  // Server identity. Capabilities are inferred from what you register, but we
  // declare tools explicitly so the handshake advertises the capability.
  const server = new McpServer(
    { name: 'hello-mcp', version: '1.0.0' },
    { capabilities: { tools: {} } }
  );

  // Register the 'add' tool.
  // Signature in use: tool(name, description, zodShape, handler)
  server.tool(
    'add',
    'Adds two numbers together and returns the sum.',
    {
      a: z.number().describe('The first addend'),
      b: z.number().describe('The second addend')
    },
    async ({ a, b }) => {
      // Zod already guaranteed a and b are numbers, so a defensive typeof check
      // is redundant here. We keep a runtime guard only for the finite case,
      // since z.number() admits NaN/Infinity.
      if (!Number.isFinite(a) || !Number.isFinite(b)) {
        throw new Error('Both parameters must be finite numbers');
      }

      const sum = a + b;

      // stdout is reserved for the MCP protocol. All human/debug output must go
      // to stderr or it corrupts the JSON-RPC stream.
      console.error(`[add] ${a} + ${b} = ${sum}`);

      // MCP tool results are always { content: [...] }.
      return {
        content: [
          {
            type: 'text',
            text: `The sum of ${a} and ${b} is ${sum}`
          }
        ]
      };
    }
  );

  // stdio transport: the client (Inspector, Claude Desktop) spawns this process
  // and talks JSON-RPC over stdin/stdout.
  const transport = new StdioServerTransport();
  await server.connect(transport);

  console.error('Hello MCP Server started successfully');
  console.error('Waiting for MCP client connection...');
}

main().catch((error) => {
  console.error('Fatal error:', error);
  process.exit(1);
});
