# Lab 01: Hello MCP - Your First MCP Server

**Duration**: 30 minutes
**Difficulty**: Beginner
**Prerequisites**: Node.js 20+, completed [STUDENT_SETUP_GUIDE.md](../../docs/STUDENT_SETUP_GUIDE.md)

## Learning Objectives

By the end of this lab, you will:

1. Understand the basic structure of an MCP server
2. Register your first MCP tool
3. Implement a simple tool handler
4. Test your server with MCP Inspector
5. Debug MCP communication using console logging

## Concepts Covered

- MCP server initialization
- Tool registration and JSON Schema
- stdio transport for local communication
- Tool handler functions and response format
- Testing with MCP Inspector

## What You Will Build

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

## Instructions

### Step 1: Understand the Starter Code

Navigate to the starter directory:

```bash
cd labs/lab-01-hello-mcp/starter
```

Examine the files:
- `src/index.js` - Main server file (has TODO sections)
- `package.json` - Dependencies and scripts

### Step 2: Install Dependencies

```bash
npm install
```

This installs:
- `@modelcontextprotocol/sdk` - Core MCP library
- `zod` - Schema library the SDK uses to define and validate tool inputs

### Step 3: Implement the Server (Fill in TODOs)

Open `src/index.js` and complete the following sections:

#### TODO 1: Import Required MCP Components

```javascript
import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { z } from 'zod';
```

**Why?**
- `McpServer` - The high-level server class. It is the one that exposes the `.tool()` helper used below. The low-level `Server` (from `server/index.js`) has no `.tool()` method, so importing that instead throws `server.tool is not a function` at startup.
- `StdioServerTransport` - Enables stdin/stdout communication (for local connections)
- `z` (Zod) - Defines the tool's input schema. The SDK 1.x `.tool()` method expects a Zod shape, converts it to JSON Schema for the client, and validates arguments for you.

#### TODO 2: Create Server Instance

```javascript
const server = new McpServer(
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
    // A Zod shape: one entry per parameter. .describe() text is surfaced to the AI.
    a: z.number().describe('First number'),
    b: z.number().describe('Second number')
  },
  async ({ a, b }) => {
    // Tool handler implementation goes here
  }
);
```

**Schema Explained**:
- The third argument is a **Zod shape**, not a hand-written JSON Schema object. The SDK converts it to JSON Schema (with `a` and `b` as required numbers) for the client.
- `.describe()` adds a human/AI-readable hint for each parameter
- Because the shape is typed, the SDK validates incoming arguments **before** your handler runs

#### TODO 4: Implement Tool Handler Logic

Inside the tool handler, add:

```javascript
async ({ a, b }) => {
  // Zod already guaranteed a and b are numbers. Guard only the non-finite
  // edge cases (z.number() still admits NaN / Infinity).
  if (!Number.isFinite(a) || !Number.isFinite(b)) {
    throw new Error('Both parameters must be finite numbers');
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

From the `starter` directory, run:

```bash
npm run inspect
```

This launches MCP Inspector **with the server already wired up** (`node src/index.js`), opens your browser to `http://localhost:6274`, and connects. Because `npm run` always sets the working directory to this package, the relative path `src/index.js` resolves every time, regardless of where you started.

> **Why not type the path into the Inspector GUI?** A relative path like `.\src\index.js` is resolved against whatever directory you launched Inspector in. Launch from the wrong place and `node` cannot find the file, the child process exits instantly, and Inspector reports **"HTTP 404: Session not found"**. The `npm run inspect` script removes that failure mode. If you must use the GUI, supply the **full absolute path** to `src/index.js`.

In the MCP Inspector web interface:

1. **Verify connection**:
   - You should see "Connected" status
   - The "Tools" tab should show your `add` tool

2. **Test the tool**:
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

3. **Check the result**:
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

## Success Criteria

Your lab is complete when:

- [ ] Server starts without errors
- [ ] MCP Inspector can connect to your server
- [ ] The `add` tool appears in the tools list
- [ ] Tool returns correct sum: `add(5, 3)` returns 8
- [ ] Tool handles invalid inputs gracefully
- [ ] Debug logs appear in the server terminal

---

## Testing

Validate your implementation with the MCP Inspector — it connects to your server, lists tools, and lets you call `add` interactively. Run from the `starter` directory:

```bash
npm run inspect
```

In the Inspector UI (default <http://localhost:6274>):
1. Confirm the server connects and the **Tools** tab lists `add`.
2. Call `add` with `{ "a": 5, "b": 3 }` and confirm the response text reads `The sum of 5 and 3 is 8`.
3. Call `add` with a non-number (e.g. `"a": "x"`) and confirm you get a clean validation error, not a crash.

---

## Troubleshooting

### Issue: "Cannot find module '@modelcontextprotocol/sdk'"

**Solution**:
```bash
rm -rf node_modules package-lock.json
npm install
```

### Issue: "HTTP 404: Session not found" / "Connection Error" on Connect

This means the stdio child process exited immediately — almost always because `node` could not find `src/index.js`. The relative path you typed in the GUI was resolved against the wrong working directory.

**Fix**: use `npm run inspect` from the `starter` directory. `npm run` forces the working directory to this package, so `src/index.js` always resolves. If you insist on the GUI, set Args to the **full absolute path** to `src/index.js`.

### Issue: "Server starts but MCP Inspector can't connect"

**Checklist**:

1. Are you launching with `npm run inspect` from the `starter` directory? (Or, in the GUI, using the **full absolute path** to `src/index.js`?)
2. Is the server still running in the other terminal?
3. Did you select "STDIO" transport (not HTTP)?
4. Try restarting the Inspector

### Issue: "Tool returns undefined or null"

**Check**:
- Are you returning `{ content: [...] }` format?
- Is the handler async?
- Are you using `return` (not just logging)?

### Issue: No debug logs appearing

**Remember**: Use `console.error()` not `console.log()` for debug output.

---

## Key Takeaways

1. **MCP servers follow a standard structure**:
   - Initialize server
   - Register tools/resources
   - Connect transport
   - Handle requests

2. **Tool schema is defined with a Zod shape**:
   - Defines parameter types
   - Provides descriptions for AI (via `.describe()`)
   - The SDK converts it to JSON Schema for the client and validates input automatically

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

## Going Further (Optional)

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

## Additional Resources

- **MCP Specification**: <https://spec.modelcontextprotocol.io/>
- **JSON Schema**: <https://json-schema.org/understanding-json-schema/>
- **MCP Server Examples**: <https://github.com/modelcontextprotocol/servers>

---

## Next Steps

Once you have completed this lab, continue up the four-lab ladder:

1. **Lab 02 - MCP Chat CLI** (Python) - See [`../lab-02-mcp-chat/README.md`](../lab-02-mcp-chat/README.md) for a complete MCP client plus stdio server plus REPL.
2. **Lab 03 - MCP Apps** (JS/TS) - See [`../lab-03-mcp-apps/README.md`](../lab-03-mcp-apps/README.md) for interactive `ui://` surfaces in Claude Desktop (SEP-1865).
3. **Lab 04 - Remote MCP + OAuth on Azure** - See [`../../remote-mcp-apim-functions-python/QUICKSTART.md`](../../remote-mcp-apim-functions-python/QUICKSTART.md) for a remote MCP server secured by Entra ID OAuth via APIM.
4. **Explore WARNERCO Schematica** - See `src/warnerco/backend/` for a production-grade Python MCP implementation using FastMCP. Run it and visit http://localhost:8000/dash/, then study `docs/tutorials/graph-memory-tutorial.md`.

---

**Time to build!**

Start with the starter code, complete the TODOs, and test your implementation. Check the solution if you get stuck, but try solving it yourself first!
