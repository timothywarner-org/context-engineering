# Student Setup Guide - MCP in Practice

Welcome! This guide will help you prepare your environment **before** the training session begins.

## 🎯 Setup Goals

By the end of this guide, you'll have:

- ✅ Node.js 20+ installed and verified
- ✅ Python 3.9+ installed (optional, for Python examples)
- ✅ Docker Desktop running
- ✅ Claude Desktop or compatible MCP client configured
- ✅ Repository cloned and dependencies installed
- ✅ Environment validated with test script

## ⏱️ Time Required

- **Basic Setup**: 30-45 minutes
- **Full Setup** (with Docker): 60 minutes

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

## Step 2: Install Python 3.9+ (Optional)

**Note**: Only needed if you want to explore the Python-based MCP servers.

### Windows

```powershell

# Download from python.org or use winget

winget install Python.Python.3.12

# Verify

python --version
pip --version

```

### macOS/Linux

```bash

# macOS

brew install python@3.12

# Ubuntu/Debian

sudo apt update && sudo apt install python3.12 python3-pip

# Verify

python3 --version
pip3 --version

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

# You should see: coretext-mcp/, stoic-mcp/, README.md, etc.


```

---

## Step 6: Install Dependencies

### CoreText MCP (JavaScript - Primary Example)

```bash
cd coretext-mcp
npm install

# Verify installation

npm list @modelcontextprotocol/sdk

# Should show version 1.x.x


```

### Stoic MCP (TypeScript - Advanced Example)

```bash
cd ../stoic-mcp
npm install

cd local
npm install
npm run build

# Verify build

ls dist/

# Should see index.js


```

### Context Journal MCP (Python - Optional)

```bash
cd ../context_journal_mcp_local
pip install -r requirements.txt

# Or using virtual environment (recommended)

python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

```

---

## Step 7: Configure Environment Variables

### CoreText MCP

```bash
cd coretext-mcp
cp .env.example .env

# Edit .env with your preferred editor
# Add your Deepseek API key (optional - server works without it)


```

**Get Deepseek API Key** (Optional):

1. Visit <https://platform.deepseek.com/>

2. Sign up for free account

3. Generate API key

4. Add to `.env`: `DEEPSEEK_API_KEY=your_key_here`

**Note**: The servers work in **fallback mode** without an API key.

### Stoic MCP

```bash
cd stoic-mcp/local
cp .env.example .env

# Add Deepseek key if desired (optional)


```

---

## Step 8: Configure Claude Desktop (Optional)

**Note**: We'll do this together during the training, but you can prepare the file:

### Windows

```powershell

# Configuration file location:
# %APPDATA%\Claude\claude_desktop_config.json

# Example content (update paths to match your system):


```

### macOS/Linux

```bash

# Configuration file location:
# ~/Library/Application Support/Claude/claude_desktop_config.json


```

### Sample Configuration

Create a backup of the provided sample:

```bash
cp claude_desktop_config.json ~/Documents/claude_desktop_config_backup.json

```

---

## Step 9: Run Validation Script

We'll create a validation script together during the course, but you can test manually:

### Test CoreText MCP

```bash
cd coretext-mcp
node src/index.js &

# Server should start without errors

# In another terminal:

node src/test-client.js

# Should show successful tool calls

# Kill the server

pkill -f "node src/index.js"

```

### Test Stoic MCP

```bash
cd stoic-mcp/local
node dist/index.js &

# Should start without errors
# Kill with Ctrl+C


```

---

## ✅ Pre-Course Checklist

Complete this checklist **before** the training:

- [ ] Node.js 20+ installed (`node --version`)
- [ ] npm working (`npm --version`)
- [ ] Python 3.9+ installed (optional, `python3 --version`)
- [ ] Docker Desktop running (`docker ps`)
- [ ] Repository cloned (`cd context-engineering`)
- [ ] CoreText dependencies installed (`cd coretext-mcp && npm list`)
- [ ] Stoic MCP built (`cd stoic-mcp/local && ls dist/index.js`)
- [ ] .env files created from examples
- [ ] Claude Desktop or MCP client installed
- [ ] Can manually start and stop MCP servers

---

## 🆘 Troubleshooting Before the Course

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

## 📚 Optional Pre-Reading

If you want to get a head start:

1. **MCP Specification**: <https://spec.modelcontextprotocol.io/>

2. **Protocol Overview**: <https://modelcontextprotocol.io/docs/concepts/overview>

3. **Quick Browse**:

   - `README.md` - Project overview
   - `DEMO_QUICK_REFERENCE.md` - Quick reference
   - `coretext-mcp/README.md` - CoreText server overview

---

## 💡 What to Expect During Training

During the 4-hour course, we'll:

1. **Segment 1** (60 min): MCP fundamentals, tool calling, your first MCP server

2. **Segment 2** (60 min): Memory patterns, resources, context engineering

3. **Segment 3** (60 min): Production deployment, Azure Container Apps, monitoring

4. **Segment 4** (60 min): Advanced patterns, multi-agent orchestration, real-world use cases

You'll be running code, testing MCP servers, and deploying to Azure (optional).

---

## 🎓 Day-of-Training Quick Start

On training day, verify everything works:

```bash

# Quick validation (run these in separate terminals)

# Terminal 1: Start CoreText MCP

cd context-engineering/coretext-mcp
node src/index.js

# Terminal 2: Test it

cd context-engineering/coretext-mcp
node src/test-client.js

# Success? You're ready! 🚀


```

---

## 🤝 Getting Help

- **Before Training**: Check the troubleshooting section above
- **During Training**: Ask questions in the live session
- **After Training**: Refer to `POST_COURSE_RESOURCES.md`

---

## Next Steps

Once you've completed this setup:

1. ✅ Mark all checklist items as complete

2. 📧 If you encounter issues, note them to ask during the session

3. 🧘 Relax - you're prepared!

See you in the training! 🎯


