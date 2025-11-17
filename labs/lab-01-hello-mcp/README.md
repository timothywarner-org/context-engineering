# Lab 01: Hello MCP - Your First MCP Server

**Duration**: 30 minutes
**Difficulty**: Beginner
**Prerequisites**: Node.js 20+, completed STUDENT_SETUP_GUIDE.md

## 🎯 Learning Objectives

By the end of this lab, you will:

1. Understand the basic structure of an MCP server
2. Register your first MCP tool
3. Implement a simple tool handler
4. Test your server with MCP Inspector
5. Debug MCP communication using console logging

## 📚 Concepts Covered

- MCP server initialization
- Tool registration and JSON Schema
- stdio transport for local communication
- Tool handler functions and response format
- Testing with MCP Inspector

## 🏗️ What You'll Build

A simple "calculator" MCP server with a single tool that adds two numbers.

**Server Name**: `hello-mcp`
**Tool**: `add` - Adds two numbers and returns the result

### Example Usage

```
User: "Add 5 and 3"
AI: [Calls add tool with {"a": 5, "b": 3}]
Tool Response: "The sum of 5 and 3 is 8"
```

---

## 📝 Instructions

### Step 1: Understand the Starter Code

Navigate to the starter directory:

```bash
cd labs/lab-01-hello-mcp/starter
```

Examine the files:
- `src/index.js` - Main server file (has TODO sections)
- `package.json` - Dependencies and scripts
- `.env.example` - Environment configuration template

### Step 2: Install Dependencies

```bash
npm install
```

This installs:
- `@modelcontextprotocol/sdk` - Core MCP library
- `dotenv` - Environment variable management

### Step 3: Implement the Server (Fill in TODOs)

Open `src/index.js` and complete the following sections:

#### TODO 1: Import Required MCP Components

```javascript
import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
```

**Why?**
- `Server` - Main MCP server class
- `StdioServerTransport` - Enables stdin/stdout communication (for local connections)

#### TODO 2: Create Server Instance

```javascript
const server = new Server(
  {
    name: 'hello-mcp',
    version: '1.0.0'
  },
  {
    capabilities: {
      tools: {}  // Declares this server provides tools
    }
  }
);
```

**Why?**
- `name` and `version` identify your server
- `capabilities.tools` tells clients this server can execute tools

#### TODO 3: Register the "add" Tool

```javascript
server.tool(
  'add',                           // Tool name
  'Adds two numbers together',     // Description for AI
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
    // Tool handler implementation goes here
  }
);
```

**Schema Explained**:
- Uses JSON Schema to define expected parameters
- `properties` defines parameter types and descriptions
- `required` lists mandatory parameters
- AI uses this schema to understand how to call the tool

#### TODO 4: Implement Tool Handler Logic

Inside the tool handler, add:

```javascript
async ({ a, b }) => {
  // Validate inputs
  if (typeof a !== 'number' || typeof b !== 'number') {
    throw new Error('Both parameters must be numbers');
  }

  // Perform calculation
  const sum = a + b;

  // Log to stderr (for debugging - won't interfere with MCP protocol)
  console.error(`[add] ${a} + ${b} = ${sum}`);

  // Return in MCP format
  return {
    content: [{
      type: 'text',
      text: `The sum of ${a} and ${b} is ${sum}`
    }]
  };
}
```

**Response Format**:
- MCP tools MUST return `{ content: [...] }`
- Content items have a `type` (usually `'text'`)
- The `text` field contains the result

**Debugging Tip**: Use `console.error()` instead of `console.log()` for debug messages. stdout is used for MCP protocol communication.

#### TODO 5: Start the Server

```javascript
const transport = new StdioServerTransport();
await server.connect(transport);

console.error('Hello MCP Server started successfully');
console.error('Waiting for MCP client connection...');
```

**Why stdio?**
- Simple and secure for local tools
- No network ports to manage
- Direct process communication

### Step 4: Run Your Server

Start the server:

```bash
node src/index.js
```

You should see:
```
Hello MCP Server started successfully
Waiting for MCP client connection...
```

The server is now running and waiting for connections. **Keep this terminal open**.

### Step 5: Test with MCP Inspector

Open a **new terminal** and start MCP Inspector:

```bash
npx @modelcontextprotocol/inspector
```

This will:
1. Start a local web server
2. Open your browser to `http://localhost:6274`

In the MCP Inspector web interface:

1. **Connect to your server**:
   - Transport: Select "Command"
   - Command: `node`
   - Args: Full path to your `src/index.js` file
     - Example: `/Users/yourname/context-engineering/labs/lab-01-hello-mcp/starter/src/index.js`
   - Click "Connect"

2. **Verify connection**:
   - You should see "Connected" status
   - The "Tools" tab should show your `add` tool

3. **Test the tool**:
   - Click the "Tools" tab
   - Click on "add"
   - Fill in the parameters:
     ```json
     {
       "a": 5,
       "b": 3
     }
     ```
   - Click "Run Tool"

4. **Check the result**:
   - You should see: `"The sum of 5 and 3 is 8"`
   - Check your server terminal - you should see the debug log:
     ```
     [add] 5 + 3 = 8
     ```

### Step 6: Test Error Handling

In MCP Inspector, try invalid inputs:

```json
{
  "a": "hello",
  "b": 3
}
```

Expected result: An error message about invalid input types.

**Questions to consider**:
- What happens if you omit a required parameter?
- What if you add extra parameters not in the schema?

---

## ✅ Success Criteria

Your lab is complete when:

- [ ] Server starts without errors
- [ ] MCP Inspector can connect to your server
- [ ] The `add` tool appears in the tools list
- [ ] Tool returns correct sum: `add(5, 3)` returns 8
- [ ] Tool handles invalid inputs gracefully
- [ ] Debug logs appear in the server terminal

---

## 🧪 Testing

Run the included test to validate your implementation:

```bash
npm test
```

Or manually test with the test client:

```bash
node test-client.js
```

Expected output:
```
✅ Server connection: OK
✅ Tool list: Found 'add'
✅ add(5, 3) = 8
✅ Error handling: OK
All tests passed!
```

---

## 🐛 Troubleshooting

### Issue: "Cannot find module '@modelcontextprotocol/sdk'"

**Solution**:
```bash
rm -rf node_modules package-lock.json
npm install
```

### Issue: "Server starts but MCP Inspector can't connect"

**Checklist**:
1. Did you use the **full absolute path** to `src/index.js`?
2. Is the server still running in the other terminal?
3. Did you select "Command" transport (not HTTP)?
4. Try restarting the Inspector

### Issue: "Tool returns undefined or null"

**Check**:
- Are you returning `{ content: [...] }` format?
- Is the handler async?
- Are you using `return` (not just logging)?

### Issue: No debug logs appearing

**Remember**: Use `console.error()` not `console.log()` for debug output.

---

## 📖 Key Takeaways

1. **MCP servers follow a standard structure**:
   - Initialize server
   - Register tools/resources
   - Connect transport
   - Handle requests

2. **Tool schema uses JSON Schema**:
   - Defines parameter types
   - Provides descriptions for AI
   - Validates input automatically

3. **Response format is standardized**:
   ```javascript
   return {
     content: [{
       type: 'text',
       text: 'Your result here'
     }]
   };
   ```

4. **Debugging with console.error()** - stdout is reserved for MCP protocol

---

## 🚀 Going Further (Optional)

If you finish early, try these challenges:

### Challenge 1: Add a Subtraction Tool

Add a `subtract` tool that subtracts b from a.

### Challenge 2: Add a Multiply Tool

Add a `multiply` tool with the same pattern.

### Challenge 3: Add Input Validation

Enhance error messages to be more descriptive:
- "Parameter 'a' must be a number, received: string"
- "Parameter 'b' is required but was not provided"

### Challenge 4: Return Metadata

Include additional metadata in the response:
```javascript
return {
  content: [{
    type: 'text',
    text: `Result: ${sum}\nOperation: addition\nInputs: ${a}, ${b}`
  }]
};
```

### Challenge 5: Test with Claude Desktop

If you have Claude Desktop configured, add this server to your config and test with natural language:

```json
{
  "mcpServers": {
    "hello-mcp": {
      "command": "node",
      "args": ["/absolute/path/to/labs/lab-01-hello-mcp/starter/src/index.js"]
    }
  }
}
```

Then ask Claude: "Can you add 42 and 58 for me?"

---

## 📚 Additional Resources

- **MCP Specification**: <https://spec.modelcontextprotocol.io/>
- **JSON Schema**: <https://json-schema.org/understanding-json-schema/>
- **MCP Server Examples**: <https://github.com/modelcontextprotocol/servers>

---

## Next Lab

Once you've completed this lab, move on to:

**[Lab 02: Tool Calling Patterns](../lab-02-tool-calling/)** - Build a multi-tool server with complex schemas

---

**Time to build!** 🔨

Start with the starter code, complete the TODOs, and test your implementation. Check the solution if you get stuck, but try solving it yourself first!
