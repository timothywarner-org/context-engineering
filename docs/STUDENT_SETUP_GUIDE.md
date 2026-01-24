# Student Setup Guide - Context Engineering with MCP

Welcome! This guide will help you prepare your environment **before** the training session begins.

## Setup Goals

By the end of this guide, you'll have:

- Node.js 20+ installed and verified
- Python 3.11+ with uv package manager installed
- Docker Desktop running (optional, for Azure deployment labs)
- Claude Desktop or VS Code with GitHub Copilot configured
- Repository cloned and WARNERCO Schematica running
- Environment validated with test commands

## Time Required

- **Basic Setup**: 30-45 minutes
- **Full Setup** (with Docker and Azure): 60 minutes

---

## Step 1: Install Node.js 20+

### Windows

```powershell

# Download from nodejs.org or use winget

winget install OpenJS.NodeJS.LTS

# Verify installation

node --version  # Should show v20.x.x or higher
npm --version

```

### macOS

```bash

# Using Homebrew

brew install node@20

# Verify installation

node --version
npm --version

```

### Linux

```bash

# Using nvm (recommended)

curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm install 20
nvm use 20

# Verify

node --version
npm --version

```

---

## Step 2: Install Python 3.11+ with uv Package Manager

**Note**: Python with uv is required for the WARNERCO Schematica server (the primary teaching example).

### Windows

```powershell
# Download from python.org or use winget
winget install Python.Python.3.12

# Verify Python
python --version  # Should show 3.11 or higher

# Install uv package manager
irm https://astral.sh/uv/install.ps1 | iex

# Restart your terminal, then verify uv
uv --version
```

### macOS/Linux

```bash
# macOS
brew install python@3.12

# Ubuntu/Debian
sudo apt update && sudo apt install python3.12 python3-pip

# Verify Python
python3 --version

# Install uv package manager
curl -LsSf https://astral.sh/uv/install.sh | sh

# Restart your terminal, then verify uv
uv --version
```

---

## Step 3: Install Docker Desktop (Recommended)

Docker enables containerized deployments and Azure testing.

### Download & Install

1. Visit <https://www.docker.com/products/docker-desktop>

2. Download for your OS (Windows/macOS/Linux)

3. Install and start Docker Desktop

4. Verify installation:

```bash
docker --version
docker run hello-world

```

### Troubleshooting

- **Windows**: Ensure WSL2 is enabled
- **macOS**: Grant permissions in System Preferences > Security
- **Linux**: Add your user to the docker group:
  ```bash
  sudo usermod -aG docker $USER
  # Log out and back in
  ```

---

## Step 4: Install MCP Client

You need an MCP-compatible client to interact with MCP servers.

### Option A: Claude Desktop (Recommended)

1. Download from <https://claude.ai/download>

2. Install and create/sign in to your account

3. We'll configure it in Step 6

### Option B: VS Code with GitHub Copilot

1. Install VS Code: <https://code.visualstudio.com/>

2. Install GitHub Copilot extension

3. Configure MCP in settings (covered in training)

### Option C: MCP Inspector (Development/Testing)

```bash

# We'll use this during the course for debugging

npx @modelcontextprotocol/inspector

```

---

## Step 5: Clone Repository

```bash
# Clone the course repository
git clone https://github.com/timothywarner-org/context-engineering.git
cd context-engineering

# Verify structure
ls -la

# You should see:
# - src/warnerco/     # WARNERCO Schematica (primary teaching example)
# - labs/             # Hands-on labs
# - docs/             # Student documentation
# - config/           # Sample MCP client configurations
# - .claude/          # Claude Code agents and skills
```

---

## Step 6: Install Dependencies

### WARNERCO Schematica (Python/FastMCP - Primary Teaching Example)

```bash
cd src/warnerco/backend
uv sync

# This installs all dependencies including:
# - FastMCP (Python MCP framework)
# - FastAPI (REST API server)
# - LangGraph (RAG orchestration)
# - ChromaDB (local vector search)
```

### Lab 01: Hello MCP (JavaScript)

```bash
cd labs/lab-01-hello-mcp/starter
npm install

# Verify installation
npm list @modelcontextprotocol/sdk
# Should show version 1.x.x
```

---

## Step 7: Configure Environment Variables

### WARNERCO Schematica

```bash
cd src/warnerco/backend
cp .env.example .env

# Edit .env with your preferred editor
# Default settings work for local development
```

**Key Environment Variables** (all optional for local development):

| Variable | Default | Description |
|----------|---------|-------------|
| `MEMORY_BACKEND` | `json` | Memory backend: `json`, `chroma`, or `azure_search` |
| `DEBUG` | `true` | Enable debug logging |

**For Azure deployment** (covered in advanced labs):
- `AZURE_OPENAI_ENDPOINT` - Azure OpenAI service URL
- `AZURE_OPENAI_API_KEY` - Azure OpenAI API key
- `AZURE_SEARCH_ENDPOINT` - Azure AI Search URL
- `AZURE_SEARCH_KEY` - Azure AI Search key

**Note**: The server works fully without any API keys using the JSON backend.

---

## Step 8: Configure MCP Client (Optional)

**Note**: We will do this together during the training, but you can prepare the file.

### Option A: Claude Desktop

**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

Example configuration for WARNERCO Schematica:

```json
{
  "mcpServers": {
    "warnerco-schematica": {
      "command": "uv",
      "args": ["run", "warnerco-mcp"],
      "cwd": "C:/github/context-engineering/src/warnerco/backend",
      "env": {
        "MEMORY_BACKEND": "json"
      }
    }
  }
}
```

### Option B: VS Code with GitHub Copilot

The repository includes a pre-configured `.vscode/mcp.json` file. Simply open the repo in VS Code and the MCP server will be available to GitHub Copilot.

See [docs/TUTORIAL_GITHUB_COPILOT.md](TUTORIAL_GITHUB_COPILOT.md) for detailed instructions.

---

## Step 9: Verify Installation

Test that everything is working before the training session.

### Test WARNERCO Schematica HTTP Server

```bash
cd src/warnerco/backend

# Start the FastAPI server
uv run uvicorn app.main:app --reload

# Server should start on http://localhost:8000
# Open http://localhost:8000/docs in your browser to see the API documentation
# Press Ctrl+C to stop
```

### Test WARNERCO Schematica MCP Server

```bash
cd src/warnerco/backend

# Start with MCP Inspector (opens browser at http://localhost:5173)
npx @modelcontextprotocol/inspector uv run warnerco-mcp

# You should see 4+ tools listed: warn_list_robots, warn_get_robot, etc.
# Press Ctrl+C to stop
```

### Test Lab 01 (JavaScript MCP)

```bash
cd labs/lab-01-hello-mcp/starter
npm install
npx @modelcontextprotocol/inspector node src/index.js

# You should see basic MCP tools listed
# Press Ctrl+C to stop
```

---

## Pre-Course Checklist

Complete this checklist **before** the training:

- [ ] Node.js 20+ installed (`node --version`)
- [ ] npm working (`npm --version`)
- [ ] Python 3.11+ installed (`python --version` or `python3 --version`)
- [ ] uv package manager installed (`uv --version`)
- [ ] Docker Desktop running (optional, `docker ps`)
- [ ] Repository cloned (`cd context-engineering`)
- [ ] WARNERCO Schematica dependencies installed (`cd src/warnerco/backend && uv sync`)
- [ ] WARNERCO server starts (`uv run uvicorn app.main:app --reload`)
- [ ] API docs accessible at http://localhost:8000/docs
- [ ] MCP Inspector works (`npx @modelcontextprotocol/inspector uv run warnerco-mcp`)
- [ ] Claude Desktop or VS Code with GitHub Copilot installed

---

## Troubleshooting Before the Course

### Issue: "npm install" fails with permission errors

**Solution**:

```bash

# Don't use sudo! Instead, configure npm properly:

npm config set prefix ~/.npm-global
echo 'export PATH=~/.npm-global/bin:$PATH' >> ~/.bashrc
source ~/.bashrc

```

### Issue: "Command not found: node"

**Solution**: Restart your terminal after installing Node.js, or verify installation path is in PATH.

### Issue: Docker Desktop won't start (Windows)

**Solution**:

1. Enable WSL2: `wsl --install`

2. Enable virtualization in BIOS

3. Install WSL2 kernel update

### Issue: "MODULE_NOT_FOUND" errors

**Solution**:

```bash

# Clear npm cache and reinstall

rm -rf node_modules package-lock.json
npm cache clean --force
npm install

```

### Issue: Port already in use

**Solution**:

```bash

# Find and kill processes on port 3000 (or relevant port)
# macOS/Linux:

lsof -ti:3000 | xargs kill -9

# Windows:

netstat -ano | findstr :3000
taskkill /PID <PID> /F

```

---

## Optional Pre-Reading

If you want to get a head start:

1. **MCP Specification**: <https://spec.modelcontextprotocol.io/>

2. **Protocol Overview**: <https://modelcontextprotocol.io/docs/concepts/overview>

3. **Quick Browse**:
   - `README.md` - Project overview
   - `CLAUDE.md` - Comprehensive development guide
   - `docs/TUTORIAL_DASHBOARDS.md` - Dashboard walkthrough

---

## What to Expect During Training

During the 4-hour course, we will:

1. **Segment 1** (60 min): MCP fundamentals, tool calling, your first MCP server with Lab 01

2. **Segment 2** (60 min): Memory patterns, resources, context engineering with WARNERCO Schematica

3. **Segment 3** (60 min): Production deployment, Azure Container Apps, semantic search with ChromaDB

4. **Segment 4** (60 min): Advanced patterns, Graph Memory, hybrid RAG, LangGraph orchestration

You will be running code, testing MCP tools, and exploring the dashboards throughout.

---

## Day-of-Training Quick Start

On training day, verify everything works:

```bash
# Terminal 1: Start WARNERCO Schematica HTTP server
cd context-engineering/src/warnerco/backend
uv run uvicorn app.main:app --reload

# Terminal 2 (optional): Open browser
# Visit http://localhost:8000/docs to see API documentation
# Visit http://localhost:8000/dash/ to see dashboards

# Success? You are ready!
```

---

## Getting Help

- **Before Training**: Check the troubleshooting section above or [TROUBLESHOOTING_FAQ.md](TROUBLESHOOTING_FAQ.md)
- **During Training**: Ask questions in the live session
- **After Training**: Refer to [POST_COURSE_RESOURCES.md](POST_COURSE_RESOURCES.md)

---

## Next Steps

Once you have completed this setup:

1. Mark all checklist items as complete

2. If you encounter issues, note them to ask during the session

3. Explore the OpenAPI docs at http://localhost:8000/docs to familiarize yourself with the API

See you in the training!


