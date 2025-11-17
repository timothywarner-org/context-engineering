#!/usr/bin/env node

/**
 * Lab 01: Hello MCP - Your First MCP Server
 *
 * This is a simple calculator MCP server that demonstrates:
 * - Basic server setup
 * - Tool registration
 * - Parameter validation
 * - Response formatting
 *
 * Complete the TODO sections to build your first MCP server!
 */

// TODO 1: Import required MCP components
// Hint: You need Server from '@modelcontextprotocol/sdk/server/index.js'
// and StdioServerTransport from '@modelcontextprotocol/sdk/server/stdio.js'

import {} from '@modelcontextprotocol/sdk/server/index.js';
import {} from '@modelcontextprotocol/sdk/server/stdio.js';

// Main function to set up and run the MCP server
async function main() {
  // TODO 2: Create a new Server instance
  // Provide a name ('hello-mcp') and version ('1.0.0')
  // Declare capabilities: { tools: {} }

  const server = null; // Replace this with your Server instance

  // TODO 3: Register the 'add' tool
  // Tool name: 'add'
  // Description: 'Adds two numbers together'
  // Schema: Define parameters 'a' and 'b' as numbers (both required)
  // Handler: Implement the addition logic

  server.tool(
    // Tool name
    'add',

    // Tool description (helps AI understand when to use this tool)
    'YOUR DESCRIPTION HERE',

    // Input schema (JSON Schema format)
    {
      type: 'object',
      properties: {
        // TODO: Define parameter 'a' as a number
        a: {
          // Your schema here
        },
        // TODO: Define parameter 'b' as a number
        b: {
          // Your schema here
        }
      },
      required: ['a', 'b']  // Both parameters are required
    },

    // Tool handler - this function runs when the tool is called
    async ({ a, b }) => {
      // TODO 4: Implement the tool handler

      // 1. Validate that both inputs are actually numbers
      // Hint: Use typeof to check
      if (/* your validation here */) {
        throw new Error('Both parameters must be numbers');
      }

      // 2. Calculate the sum
      const sum = 0; // Replace with actual calculation

      // 3. Log to stderr for debugging (won't interfere with MCP protocol)
      console.error(`[add] ${a} + ${b} = ${sum}`);

      // 4. Return the result in MCP format
      // MUST return { content: [{ type: 'text', text: '...' }] }
      return {
        content: [{
          type: 'text',
          text: `YOUR RESULT MESSAGE HERE`  // Replace with meaningful message
        }]
      };
    }
  );

  // TODO 5: Start the server with stdio transport
  // Create a StdioServerTransport and connect it to the server

  const transport = null; // Create StdioServerTransport here

  // Connect the server to the transport
  await server.connect(/* your transport here */);

  // Log success (use console.error for debug messages)
  console.error('Hello MCP Server started successfully');
  console.error('Waiting for MCP client connection...');
}

// Run the main function and handle any errors
main().catch((error) => {
  console.error('Fatal error:', error);
  process.exit(1);
});
