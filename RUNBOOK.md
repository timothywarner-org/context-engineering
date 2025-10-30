# Context Engineering Demo Runbook

> **Tim's Quick Start Guide** - Get all three demos running without errors

## Prerequisites

- Node.js 18+ installed
- Git Bash or similar terminal (Windows)
- DeepSeek API key (stored in repo-root `.env`)

## Project Overview

This repository contains three demos for the "MCP in Practice" course:

1. **deepseek-context-demo** - Visual demonstration of context window token usage
2. **coretext-mcp** - MCP server with persistent memory and CRUD operations
3. **stoic-mcp** - MCP server for Stoic philosophy quotes

---

## Demo 1: DeepSeek Context Demo

**Purpose**: Demonstrates how token usage grows as conversation history expands with visual progress bars.

### Setup

```bash
# Navigate to the demo directory
cd context-engineering-2/deepseek-context-demo

# Install dependencies (first time only)
npm install

# Verify .env file has the API key from repo root
cat .env
# Should show: DEEPSEEK_API_KEY=sk-de6516ce261e43bfa6d199aeb1bf6ece
```

### Run the Demo

```bash
npm start
```

### Expected Output

```
🎓 DeepSeek Context Window Demonstration
Each turn expands the conversation and shows current token usage.

🗨️  Turn 1: 64 tokens used (0.05% of window)
🗨️  Turn 2: 80 tokens used (0.06% of window)
...
🗨️  Turn 10: 208 tokens used (0.16% of window)
```

### What It Does

- Shows 10 simulated conversation turns
- Displays token count growth with each turn
- Uses `gpt-tokenizer` to estimate token usage
- Demonstrates context window consumption visually

### Troubleshooting

**Issue**: `Authentication Fails, Your api key is invalid`

- **Fix**: The demo works for token counting even with invalid API key
- The final API call may fail but the demo still demonstrates the concept
- To fix API errors: Get a valid DeepSeek API key from <https://platform.deepseek.com/>

**Issue**: `DEEPSEEK_API_KEY not found`

- **Fix**: Create `.env` file with `DEEPSEEK_API_KEY=your_key_here`

---

## Demo 2: CoreText MCP Server with Inspector

**Purpose**: Production-ready MCP server demonstrating persistent AI memory with CRUD operations, enrichment, and knowledge graphs.

### Setup

```bash
# Navigate to the coretext-mcp directory
cd ../coretext-mcp

# Install dependencies (first time only)
npm install

# Configure environment (optional - works without API key)
cp .env.example .env
# Edit .env and add your DEEPSEEK_API_KEY if you want AI enrichment
# The server works in fallback mode without the API key
```

### Run with MCP Inspector

```bash
npm run inspector
```

### Expected Output

```
Starting MCP inspector...

🔍 MCP Inspector is up and running at http://localhost:5173 🚀
```

### Using the Inspector

1. **Open in browser**: Navigate to <http://localhost:5173>
2. **View Tools**: You'll see 8 available tools:
   - `memory_create` - Create new memory entries
   - `memory_read` - Read a specific memory by ID
   - `memory_update` - Update existing memory
   - `memory_delete` - Delete a memory
   - `memory_search` - Search memories by keyword
   - `memory_list` - List all memories
   - `memory_stats` - Get memory statistics
   - `memory_enrich` - AI-enrich a memory (requires API key)

3. **View Resources**: Three resources available:
   - `memory://overview` - Dashboard with stats and tag cloud
   - `memory://context-stream` - Time-windowed memory view
   - `memory://knowledge-graph` - Semantic connections between memories

### Test Basic Operations

**Create a memory:**

```json
{
  "content": "MCP enables persistent AI context across conversations",
  "type": "semantic",
  "tags": ["mcp", "context", "ai"]
}
```

**List all memories:**

- Call `memory_list` tool (no parameters needed)

**Search memories:**

```json
{
  "query": "MCP"
}
```

### Alternative: Run Test Suite

```bash
npm test
```

This runs automated tests for all 8 tools and 3 resources.

### Troubleshooting

**Issue**: `npm run inspector` fails to start

- **Fix**: Check Node.js version with `node --version` (need 18+)
- **Fix**: Delete `node_modules` and run `npm install` again

**Issue**: Port 5173 already in use

- **Fix**: Kill existing process on port 5173
- **Fix**: Or use `npm start` to run without inspector

**Issue**: Enrichment fails

- **Expected**: Server uses fallback enrichment without API key
- **Fix**: Add valid `DEEPSEEK_API_KEY` to `.env` for AI enrichment

**Issue**: Memory not persisting

- **Fix**: Check that `data/` folder exists and is writable
- **Fix**: Server auto-creates `data/memory.json` on first run

---

## Demo 3: Stoic MCP Local Server

**Purpose**: Simple MCP server demonstrating JSON-based storage with Stoic philosophy quotes.

### Setup

```bash
# Navigate to the stoic-mcp root directory
cd ../stoic-mcp

# Install dependencies for all workspaces (first time only)
npm install

# Navigate to the local implementation
cd local

# Build TypeScript to JavaScript
npm run build
```

### Run the Server

```bash
npm start
```

### Expected Output

```
Stoic MCP Local Server running on stdio
```

The server is now running and listening for MCP protocol messages via stdio.

### Available Tools

The server provides 9 tools for quote management:

1. `get_random_quote` - Get a random Stoic quote
2. `search_quotes` - Search by author, theme, or keyword
3. `add_quote` - Add a new quote manually
4. `get_quote_explanation` - Get AI explanation (requires DEEPSEEK_API_KEY)
5. `toggle_favorite` - Mark/unmark quote as favorite
6. `get_favorites` - List all favorited quotes
7. `update_quote_notes` - Add personal notes to a quote
8. `delete_quote` - Remove a quote
9. `generate_quote` - Generate new Stoic-style quote (requires API key)

### Data Storage

Quotes are stored in: `local/quotes.json`

### Testing with MCP Inspector

You can use the MCP Inspector to test this server:

```bash
# From the stoic-mcp/local directory
npx @modelcontextprotocol/inspector node dist/index.js
```

Then open <http://localhost:5173> to interact with the server.

### Development Mode

```bash
# Auto-rebuild on file changes
npm run watch

# In another terminal, run the server
npm start
```

### Troubleshooting

**Issue**: `npm install` fails with "Cannot read properties of null"

- **Fix**: Run `npm install` from `stoic-mcp` root, not from `local/`
- This is a workspace repo, install from parent first

**Issue**: `tsc: command not found`

- **Fix**: Install TypeScript: `npm install -g typescript`
- **Or**: Use `npm run build` which uses local TypeScript

**Issue**: `quotes.json not found`

- **Fix**: Server auto-creates `quotes.json` on first run
- **Fix**: Check that `local/quotes-source/` directory exists

**Issue**: AI features not working

- **Expected**: Tools work without API key (return fallback messages)
- **Fix**: Add `DEEPSEEK_API_KEY` environment variable for AI features

---

## Quick Reference

### Start All Three Demos

```bash
# Terminal 1: DeepSeek Context Demo
cd context-engineering-2/deepseek-context-demo
npm start

# Terminal 2: CoreText MCP Inspector
cd context-engineering-2/coretext-mcp
npm run inspector
# Open http://localhost:5173

# Terminal 3: Stoic MCP Server (via Inspector)
cd context-engineering-2/stoic-mcp/local
npx @modelcontextprotocol/inspector node dist/index.js
# Open http://localhost:5174 (different port)
```

### Environment Variables

All demos use `DEEPSEEK_API_KEY` from:

1. Repo root `.env` (currently set)
2. Project-specific `.env` files
3. System environment variables

### Common Issues Across All Demos

**npm install fails**

```bash
# Clear npm cache
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

**Port conflicts**

```bash
# Find process on port
netstat -ano | findstr :5173

# Kill process (Windows)
taskkill /PID <process_id> /F
```

**API key issues**

- Check `.env` file exists: `cat .env`
- Check format: `DEEPSEEK_API_KEY=sk-...`
- No quotes needed around the key
- No spaces around the `=` sign

---

## Next Steps

### Integrate with Claude Desktop

Add to `%APPDATA%\Claude\claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "coretext": {
      "command": "node",
      "args": ["C:/github/context-engineering-2/coretext-mcp/src/index.js"],
      "env": {
        "DEEPSEEK_API_KEY": "sk-de6516ce261e43bfa6d199aeb1bf6ece"
      }
    },
    "stoic": {
      "command": "node",
      "args": ["C:/github/context-engineering-2/stoic-mcp/local/dist/index.js"],
      "env": {
        "DEEPSEEK_API_KEY": "sk-de6516ce261e43bfa6d199aeb1bf6ece"
      }
    }
  }
}
```

**Note**: Restart Claude Desktop after making config changes.

### Learn More

- **MCP Specification**: <https://spec.modelcontextprotocol.io/>
- **MCP Documentation**: <https://modelcontextprotocol.io/docs>
- **DeepSeek Platform**: <https://platform.deepseek.com/>

---

## Bonus: Deploy MCP Servers to Azure

**Production-ready deployment (~$8-15/month)**

Both CoreText MCP and Stoic MCP servers can be deployed to Azure using cost-optimized infrastructure.

### Deploy CoreText MCP to Azure

**Features**: Persistent AI memory with CRUD operations, enrichment, and knowledge graphs.

```bash
cd context-engineering-2/coretext-mcp/azure
./deploy.sh
```

The script will:

1. Verify prerequisites (Azure CLI, Docker)
2. Create Azure Container Registry
3. Build and push Docker image
4. Deploy infrastructure (Cosmos DB Free Tier, Container Apps, Key Vault)
5. Configure secrets via Managed Identity

**Documentation**:

- **Full Guide**: `coretext-mcp/azure/README.md`
- **Quick Start**: `coretext-mcp/azure/QUICKSTART.md`
- **MCP Inspector Tour**: `coretext-mcp/MCP_INSPECTOR_TOUR.md`

### Deploy Stoic MCP to Azure

**Features**: Stoic philosophy quotes with AI-powered explanations.

```bash
cd context-engineering-2/stoic-mcp/azure
./deploy.sh
```

The script will:

1. Verify prerequisites (Azure CLI, Docker)
2. Create Azure Container Registry (or reuse existing)
3. Build TypeScript server and push Docker image
4. Deploy infrastructure (Cosmos DB with 2 containers, Container Apps, Key Vault)
5. Configure secrets via Managed Identity

**Documentation**:

- **Full Guide**: `stoic-mcp/azure/README.md`
- **Quick Start**: `stoic-mcp/azure/QUICKSTART.md`
- **Validation Report**: `stoic-mcp/azure/VALIDATION_REPORT.md`

### What Gets Deployed (Both Servers)

- **Cosmos DB**: Free Tier (1000 RU/s, 25GB storage) - **$0/month**
  - **Note**: Only ONE free tier per subscription - choose which server to use it for
- **Container Apps**: Consumption plan, scales to zero - **~$1-5/month per app**
- **Key Vault**: Secure secret storage - **~$0.03/month**
- **Log Analytics**: 30-day retention - **~$2-5/month**
- **Container Registry**: Basic tier (shared by both) - **~$5/month**
- **Total**: **~$8-15/month** per server

### Requirements

- Azure subscription (see `azure-details.md`)
- Resource group: `context-engineering-rg`
- Managed Identity: `context-msi`
- Azure CLI installed and logged in
- Docker installed

### Cosmos DB Schema Differences

**CoreText MCP** (Single container):

- Container: `memory`
- Partition Key: `/id`
- Schema: `{id, content, type, tags, createdAt, updatedAt, enrichment, connections}`

**Stoic MCP** (Two containers):

- Container 1: `quotes` (Partition Key: `/id`)
  - Schema: `{id, text, author, source, theme, favorite, notes, createdAt, addedBy}`
- Container 2: `metadata` (Partition Key: `/type`)
  - Schema: `{id, type, lastId, version, quoteCount, lastUpdated}`

### Test Deployment

```bash
# Health check (replace with your app URL)
curl https://your-app-url.eastus.azurecontainerapps.io/health

# View logs
az containerapp logs show -n YOUR_APP_NAME -g context-engineering-rg --follow

# List deployments
az deployment group list -g context-engineering-rg -o table
```

### CI/CD with GitHub Actions

Both servers include GitHub Actions workflows for automated deployment:

**CoreText MCP**: `.github/workflows/deploy-coretext-mcp.yml`

- Setup Guide: `.github/GITHUB_ACTIONS_SETUP.md`

**Stoic MCP**: `.github/workflows/deploy-stoic-mcp.yml`

- Setup Guide: `.github/GITHUB_ACTIONS_SETUP_STOIC.md`

**Setup Steps**:

1. Create Azure service principal
2. Add GitHub secrets (`AZURE_CREDENTIALS`, `AZURE_SUBSCRIPTION_ID`, `DEEPSEEK_API_KEY`)
3. Push to `main` branch triggers deployment

---

## Tim's Pro Tips

1. **Always run `npm install` from the correct directory**
   - `deepseek-context-demo/` for Demo 1
   - `coretext-mcp/` for Demo 2
   - `stoic-mcp/` (root) then `stoic-mcp/local/` for Demo 3

2. **MCP Inspector is your friend**
   - Use it to debug tool calls
   - View resources in real-time
   - Test without connecting to Claude Desktop

3. **Fallback modes work**
   - All demos function without API keys (with limitations)
   - API keys unlock AI features (enrichment, generation, explanations)

4. **Check the logs**
   - MCP servers log to stderr (visible in terminal)
   - Look for emoji indicators (🚀 ✅ ❌ 📝)

5. **Git status is your friend**
   - Check which files changed: `git status`
   - Don't commit `.env` files (they're .gitignored)

---

**Last Updated**: 2025-10-29
**Tested On**: Windows 11, Node.js 20+, Git Bash
