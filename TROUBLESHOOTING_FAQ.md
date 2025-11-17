# Troubleshooting FAQ - MCP in Practice

This FAQ addresses the most common issues students encounter during the course. Bookmark this page!

## 🔍 Quick Diagnosis

**Start here if you're stuck:**

```bash
# Run this diagnostic command in the problematic directory
node --version && npm --version && npm list @modelcontextprotocol/sdk
```

Expected output:
- Node: v20.x.x or higher
- npm: 9.x.x or higher
- MCP SDK: 1.x.x

---

## 📂 Table of Contents

1. [Installation & Setup Issues](#installation--setup-issues)
2. [MCP Server Won't Start](#mcp-server-wont-start)
3. [Connection & Communication Issues](#connection--communication-issues)
4. [Tool Call Failures](#tool-call-failures)
5. [Claude Desktop Integration](#claude-desktop-integration)
6. [Docker & Container Issues](#docker--container-issues)
7. [Azure Deployment Problems](#azure-deployment-problems)
8. [Performance & Memory Issues](#performance--memory-issues)
9. [API Key & Authentication](#api-key--authentication)
10. [Development Workflow](#development-workflow)

---

## Installation & Setup Issues

### Q: "npm install" fails with EACCES permission error

**Problem**: Permission denied when installing global packages.

**Solution**:
```bash
# DON'T use sudo! Instead, reconfigure npm:
mkdir ~/.npm-global
npm config set prefix ~/.npm-global

# Add to your shell profile (~/.bashrc, ~/.zshrc, etc.)
echo 'export PATH=~/.npm-global/bin:$PATH' >> ~/.bashrc
source ~/.bashrc

# Now retry
npm install
```

### Q: "Python not found" error on Windows

**Problem**: Python installed but not in PATH.

**Solution**:
```powershell
# Option 1: Reinstall Python with "Add to PATH" checked

# Option 2: Add manually
# 1. Find Python: where python
# 2. Add to PATH in System Environment Variables
# 3. Restart terminal

# Verify
python --version
```

### Q: Package installation hangs or times out

**Problem**: Network issues or npm registry problems.

**Solution**:
```bash
# Clear npm cache
npm cache clean --force

# Try with verbose logging
npm install --verbose

# Alternative: Use a different registry
npm config set registry https://registry.npmjs.org/

# Retry
npm install
```

### Q: "node-gyp" build failures on Windows

**Problem**: Missing build tools for native dependencies.

**Solution**:
```powershell
# Install Windows Build Tools (run as Administrator)
npm install -g windows-build-tools

# Or use Visual Studio Build Tools
# Download from: https://visualstudio.microsoft.com/downloads/
# Select "Desktop development with C++"

# Retry installation
npm install
```

---

## MCP Server Won't Start

### Q: Server crashes immediately with "MODULE_NOT_FOUND"

**Problem**: Missing dependencies or incorrect import paths.

**Diagnosis**:
```bash
# Check if dependencies are installed
npm list @modelcontextprotocol/sdk

# Look for broken symlinks
ls -la node_modules/.bin/
```

**Solution**:
```bash
# Clean install
rm -rf node_modules package-lock.json
npm install

# For TypeScript projects, rebuild
npm run build
```

### Q: "Address already in use" error (EADDRINUSE)

**Problem**: Port already occupied by another process.

**Solution**:

**macOS/Linux:**
```bash
# Find process using port 3000
lsof -ti:3000

# Kill it
lsof -ti:3000 | xargs kill -9

# Or use the provided script
node scripts/kill-ports.js
```

**Windows:**
```powershell
# Find process on port 3000
netstat -ano | findstr :3000

# Kill by PID
taskkill /PID <PID> /F

# Or use PowerShell script
.\scripts\kill-ports.ps1
```

### Q: Server starts but immediately exits with no error

**Problem**: Server process isn't staying alive (common with stdio transport).

**Diagnosis**:
```bash
# Run with debug output
NODE_ENV=development node src/index.js

# Check for syntax errors
node --check src/index.js
```

**Solution**:
- Ensure the server isn't exiting prematurely
- Check for unhandled promise rejections
- Verify stdio transport is configured correctly
- Look at `src/index.js` - it should have `server.connect(transport)`

### Q: "Cannot find module" error for local files

**Problem**: Incorrect relative path or file extension.

**Solution**:
```javascript
// ❌ Wrong - missing .js extension for ESM
import { foo } from './utils';

// ✅ Correct
import { foo } from './utils.js';

// For CommonJS (require), .js is optional
const { foo } = require('./utils');  // Works
```

---

## Connection & Communication Issues

### Q: MCP Inspector can't connect to server

**Problem**: Server not exposing the right transport or Inspector misconfigured.

**Solution**:

1. **Verify server is running:**
```bash
# Check process
ps aux | grep "node.*index.js"
```

2. **Check transport type:**
   - CoreText/Stoic use **stdio** (not HTTP)
   - Inspector needs to connect via command, not URL

3. **Correct Inspector setup:**
```bash
# Start Inspector
npx @modelcontextprotocol/inspector

# In Inspector UI, use "Command" mode:
# Command: node
# Args: /absolute/path/to/context-engineering/coretext-mcp/src/index.js
```

### Q: Claude Desktop shows "Server disconnected"

**Problem**: Server crashed or configuration incorrect.

**Diagnosis**:
```bash
# Check Claude Desktop logs

# macOS:
tail -f ~/Library/Logs/Claude/mcp*.log

# Windows:
# %APPDATA%\Claude\logs\mcp*.log

# Linux:
tail -f ~/.config/Claude/logs/mcp*.log
```

**Solution**:

1. **Verify config file syntax:**
```json
{
  "mcpServers": {
    "coretext": {
      "command": "node",
      "args": ["/absolute/path/to/coretext-mcp/src/index.js"],
      "env": {
        "DEEPSEEK_API_KEY": "optional-key-here"
      }
    }
  }
}
```

2. **Common config mistakes:**
   - ❌ Relative paths instead of absolute
   - ❌ Backslashes not escaped on Windows: `C:\Users\...` → `C:\\Users\\...`
   - ❌ Trailing commas in JSON
   - ❌ Missing `node` command (just providing the .js file)

3. **Test server manually:**
```bash
# Run the exact command from config
node /absolute/path/to/coretext-mcp/src/index.js

# Should start without errors
```

### Q: Tools not appearing in Claude Desktop

**Problem**: Server connected but tools not registered.

**Solution**:

1. **Check server logs** - look for `server.tool()` registrations
2. **Restart Claude Desktop** - sometimes needed after config changes
3. **Verify tool schema:**
```javascript
// Ensure tools are registered BEFORE server.connect()
server.tool("tool_name", "description", { /* schema */ }, handler);
server.connect(transport);  // Must be last
```

---

## Tool Call Failures

### Q: Tool returns "Internal error" with no details

**Problem**: Unhandled exception in tool handler.

**Solution**:

**Add error handling:**
```javascript
server.tool("my_tool", "Description", schema, async (params) => {
  try {
    const result = await doSomething(params);
    return { content: [{ type: "text", text: JSON.stringify(result) }] };
  } catch (error) {
    console.error("Tool error:", error);
    return {
      content: [{
        type: "text",
        text: `Error: ${error.message}\n\nStack: ${error.stack}`
      }],
      isError: true
    };
  }
});
```

### Q: Tool receives undefined/null parameters

**Problem**: Schema mismatch or client sending different format.

**Diagnosis**:
```javascript
server.tool("debug_tool", "Test", { /* schema */ }, async (params) => {
  console.error("Received params:", JSON.stringify(params, null, 2));
  // Check what you're actually receiving
  return { content: [{ type: "text", text: "Check console" }] };
});
```

**Solution**:
- Verify schema matches expected input
- Check for required vs. optional properties
- Add parameter validation

### Q: JSON parse errors when tool returns data

**Problem**: Returning invalid JSON structure.

**Solution**:
```javascript
// ❌ Wrong - returning raw string
return JSON.stringify(result);

// ✅ Correct - MCP response format
return {
  content: [{
    type: "text",
    text: JSON.stringify(result, null, 2)  // Pretty-print for readability
  }]
};
```

### Q: File operations fail with permission errors

**Problem**: Insufficient permissions or path issues.

**Solution**:
```javascript
// Always use absolute paths
const path = require('path');
const dataPath = path.join(process.cwd(), 'data', 'memory.json');

// Check directory exists
const fs = require('fs');
const dir = path.dirname(dataPath);
if (!fs.existsSync(dir)) {
  fs.mkdirSync(dir, { recursive: true });
}

// Wrap file operations
try {
  const data = fs.readFileSync(dataPath, 'utf-8');
  // ...
} catch (error) {
  if (error.code === 'ENOENT') {
    // File doesn't exist, create it
    fs.writeFileSync(dataPath, JSON.stringify([], null, 2));
  } else {
    throw error;  // Re-throw other errors
  }
}
```

---

## Claude Desktop Integration

### Q: Config file location - where is it?

**Answer**:

- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

**Create if missing:**
```bash
# macOS/Linux
mkdir -p ~/Library/Application\ Support/Claude
touch ~/Library/Application\ Support/Claude/claude_desktop_config.json

# Windows (PowerShell)
New-Item -Path "$env:APPDATA\Claude\claude_desktop_config.json" -ItemType File -Force
```

### Q: Changes to config not taking effect

**Solution**:
1. **Fully quit Claude Desktop** (not just close window)
   - macOS: Cmd+Q or right-click dock icon → Quit
   - Windows: Right-click system tray icon → Exit
2. **Wait 5 seconds**
3. **Restart Claude Desktop**
4. **Check for typos** in config (use JSON validator)

### Q: How to verify server is working in Claude Desktop?

**Test Method**:

1. Open Claude Desktop
2. Start a new conversation
3. Type: "What MCP tools do you have access to?"
4. Claude should list your registered tools

**If tools don't appear:**
```bash
# Check logs for errors
tail -f ~/Library/Logs/Claude/mcp*.log  # macOS
```

### Q: Multiple MCP servers - which one is being used?

**Answer**: All configured servers are loaded simultaneously.

**Configuration example:**
```json
{
  "mcpServers": {
    "coretext": {
      "command": "node",
      "args": ["/path/to/coretext-mcp/src/index.js"]
    },
    "stoic": {
      "command": "node",
      "args": ["/path/to/stoic-mcp/local/dist/index.js"]
    }
  }
}
```

Claude has access to tools from **both** servers.

---

## Docker & Container Issues

### Q: Docker Desktop won't start on Windows

**Problem**: Virtualization not enabled or WSL2 not configured.

**Solution**:

1. **Enable WSL2:**
```powershell
# Run as Administrator
wsl --install
wsl --set-default-version 2
```

2. **Install WSL2 kernel update:**
   - Download: <https://aka.ms/wsl2kernel>
   - Install and restart

3. **Enable virtualization in BIOS:**
   - Restart PC
   - Enter BIOS (usually F2, F10, or Del during boot)
   - Enable Intel VT-x or AMD-V
   - Save and exit

4. **Restart Docker Desktop**

### Q: "docker: command not found" after installation

**Problem**: Docker not in PATH or daemon not running.

**Solution**:
```bash
# Verify Docker Desktop is running
# Check system tray (Windows) or menu bar (macOS)

# macOS - add to PATH if needed
echo 'export PATH="/usr/local/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc

# Linux - ensure daemon is running
sudo systemctl start docker
sudo systemctl enable docker

# Verify
docker --version
docker ps
```

### Q: Container exits immediately with exit code 1

**Diagnosis**:
```bash
# Check container logs
docker logs <container_name>

# Run interactively to see errors
docker run -it <image_name> /bin/sh
```

**Common causes:**
- Missing environment variables
- Incorrect entrypoint/command
- Dependencies not installed in image

### Q: "docker build" fails with network timeout

**Solution**:
```bash
# Increase timeout
docker build --network=host -t myimage .

# Or use build args for proxy
docker build --build-arg HTTP_PROXY=http://proxy:port -t myimage .

# Clear build cache if needed
docker builder prune
```

---

## Azure Deployment Problems

### Q: "az: command not found"

**Problem**: Azure CLI not installed.

**Solution**:
```bash
# macOS
brew install azure-cli

# Windows
winget install Microsoft.AzureCLI

# Linux
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Verify
az --version
```

### Q: Authentication fails with "az login"

**Solution**:
```bash
# Clear cached credentials
az account clear

# Re-login with device code (works in any environment)
az login --use-device-code

# Verify logged in
az account show
```

### Q: Bicep deployment fails with "resource provider not registered"

**Problem**: Required Azure resource providers not enabled.

**Solution**:
```bash
# Register required providers
az provider register --namespace Microsoft.App
az provider register --namespace Microsoft.OperationalInsights
az provider register --namespace Microsoft.DocumentDB

# Check registration status
az provider show --namespace Microsoft.App --query "registrationState"

# Wait for "Registered" (can take 5-10 minutes)
```

### Q: Container App deployment succeeds but app doesn't work

**Diagnosis**:
```bash
# Check container app logs
az containerapp logs show \
  --name <app_name> \
  --resource-group <rg_name> \
  --follow

# Check replica status
az containerapp replica list \
  --name <app_name> \
  --resource-group <rg_name>
```

**Common issues:**
- Environment variables not set (DEEPSEEK_API_KEY, etc.)
- Port mismatch (ensure EXPOSE in Dockerfile matches Container App ingress)
- Secrets not properly referenced

### Q: Cosmos DB connection fails from Container App

**Problem**: Managed identity or connection string misconfigured.

**Solution**:

1. **Verify Managed Identity is assigned:**
```bash
az containerapp identity show \
  --name <app_name> \
  --resource-group <rg_name>
```

2. **Check RBAC role assignment:**
```bash
az cosmosdb sql role assignment list \
  --account-name <cosmos_account> \
  --resource-group <rg_name>
```

3. **Test connection string** (if using key-based auth):
```bash
# Get connection string
az cosmosdb keys list \
  --name <cosmos_account> \
  --resource-group <rg_name> \
  --type connection-strings

# Verify in Container App environment variables
az containerapp show \
  --name <app_name> \
  --resource-group <rg_name> \
  --query "properties.template.containers[0].env"
```

---

## Performance & Memory Issues

### Q: Server becomes slow after many tool calls

**Problem**: Memory leak or inefficient data structures.

**Diagnosis**:
```bash
# Monitor Node.js memory
node --expose-gc --trace-gc src/index.js

# Or use built-in profiling
node --prof src/index.js
# Process the log
node --prof-process isolate-*-v8.log > processed.txt
```

**Solution**:

1. **Implement pagination for large datasets:**
```javascript
// ❌ Loading entire database
const allMemories = JSON.parse(fs.readFileSync('memory.json'));

// ✅ Load only what's needed
function getMemories(limit = 100, offset = 0) {
  const all = JSON.parse(fs.readFileSync('memory.json'));
  return all.slice(offset, offset + limit);
}
```

2. **Clear old data:**
```javascript
// Implement retention policy
function cleanOldMemories() {
  const memories = JSON.parse(fs.readFileSync('memory.json'));
  const cutoff = Date.now() - (30 * 24 * 60 * 60 * 1000); // 30 days
  const recent = memories.filter(m => new Date(m.timestamp) > cutoff);
  fs.writeFileSync('memory.json', JSON.stringify(recent, null, 2));
}
```

### Q: High CPU usage when idle

**Problem**: Polling loop or inefficient event listeners.

**Solution**:
- Use event-driven patterns instead of polling
- Implement debouncing for frequent operations
- Check for runaway intervals/timeouts

---

## API Key & Authentication

### Q: Deepseek API returns 401 Unauthorized

**Problem**: Invalid or missing API key.

**Verification**:
```bash
# Test API key directly
curl https://api.deepseek.com/v1/chat/completions \
  -H "Authorization: Bearer YOUR_KEY_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "deepseek-chat",
    "messages": [{"role": "user", "content": "Hello"}]
  }'

# Should return JSON response, not 401
```

**Solution**:
1. **Verify key is correct** - regenerate if needed
2. **Check .env file** is loaded:
```javascript
require('dotenv').config();
console.log('API Key loaded:', process.env.DEEPSEEK_API_KEY ? 'YES' : 'NO');
```

3. **Ensure key is passed to API client:**
```javascript
const apiKey = process.env.DEEPSEEK_API_KEY || 'not-configured';
if (apiKey === 'not-configured') {
  console.warn('Running in fallback mode without AI enrichment');
}
```

### Q: API key exposed in logs or error messages

**Problem**: Security risk - API keys should never be logged.

**Solution**:
```javascript
// ❌ Never do this
console.log('Using API key:', process.env.DEEPSEEK_API_KEY);

// ✅ Log sanitized version
const key = process.env.DEEPSEEK_API_KEY || '';
console.log('API key configured:', key ? `${key.slice(0, 10)}...` : 'NO');

// ✅ Sanitize errors
catch (error) {
  const sanitized = error.message.replace(/sk-[a-zA-Z0-9]+/g, 'sk-***');
  console.error('Error:', sanitized);
}
```

---

## Development Workflow

### Q: How to restart server quickly during development?

**Solution**:

**Use nodemon for auto-restart:**
```bash
# Install nodemon
npm install -g nodemon

# Run with auto-restart
nodemon src/index.js

# Or add to package.json scripts:
{
  "scripts": {
    "dev": "nodemon src/index.js",
    "start": "node src/index.js"
  }
}

# Then use:
npm run dev
```

### Q: How to debug MCP tool handlers?

**Technique**:

1. **Add verbose logging:**
```javascript
server.tool("my_tool", "...", schema, async (params) => {
  console.error("=== TOOL CALL START ===");
  console.error("Params:", JSON.stringify(params, null, 2));

  const result = await processParams(params);
  console.error("Result:", JSON.stringify(result, null, 2));
  console.error("=== TOOL CALL END ===");

  return { content: [{ type: "text", text: JSON.stringify(result) }] };
});
```

2. **Use debugger:**
```bash
# Start with Node inspector
node --inspect src/index.js

# Open Chrome DevTools:
# chrome://inspect
```

3. **VS Code debugging:**
Create `.vscode/launch.json`:
```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "type": "node",
      "request": "launch",
      "name": "Debug MCP Server",
      "program": "${workspaceFolder}/src/index.js",
      "envFile": "${workspaceFolder}/.env"
    }
  ]
}
```

### Q: How to test changes without Claude Desktop?

**Solution** - Use MCP Inspector or test client:

**Option 1: MCP Inspector**
```bash
npx @modelcontextprotocol/inspector
# Connect to your server
# Test tools interactively
```

**Option 2: Test client script**
```bash
# Use the provided test client
node src/test-client.js

# Or create custom test
node -e "
const { Client } = require('@modelcontextprotocol/sdk/client/index.js');
const { StdioClientTransport } = require('@modelcontextprotocol/sdk/client/stdio.js');

async function test() {
  const transport = new StdioClientTransport({
    command: 'node',
    args: ['src/index.js']
  });
  const client = new Client({ name: 'test-client', version: '1.0.0' }, {});
  await client.connect(transport);

  const result = await client.callTool('your_tool', { /* params */ });
  console.log('Result:', result);

  await client.close();
}
test();
"
```

---

## 🆘 Still Stuck?

If your issue isn't covered here:

1. **Check server logs** - most issues show up there
2. **Review DEMO_SCRIPT.md** - see working examples
3. **Check coretext-mcp/PORT_FIXES.md** - port-related issues
4. **Search GitHub issues** - may already be solved
5. **Ask during training** - that's what we're here for!

---

## 📝 Contributing to This FAQ

Found a solution to a problem not listed here? Please:

1. Document the problem clearly
2. Include diagnostic steps
3. Provide working solution
4. Submit as course feedback

---

**Last Updated**: Pre-course preparation
**Maintainer**: Course instructor
**Version**: 1.0
