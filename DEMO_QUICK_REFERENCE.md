# MCP Demo - Quick Reference Card

**Quick Commands for Live Demo** | Print this page for easy reference during presentation

---

## 🚀 Pre-Demo Setup (5 minutes before start)

```bash
# Set environment
export DEEPSEEK_API_KEY="sk-xxxxxxxxxxxxx"

# Verify Azure
az account show

# Check repo status
cd /c/github/context-engineering-2
git status

# Open terminals (5 windows)
# T1: deepseek-context-demo
# T2: coretext-mcp
# T3: stoic-mcp/local
# T4: Azure CLI
# T5: MCP Inspector
```

---

## 🧠 Part 0: DeepSeek Context Demo (15 min)

**Purpose**: Demonstrate the AI amnesia problem before introducing MCP as the solution

### Setup
```bash
cd deepseek-context-demo
npm install
```

### Run Demo
```bash
npm start
```

### What to Show

**Script demonstrates**:
- Token counting in real-time with visual progress bar
- Growing conversation consuming context window (128K tokens)
- 10 simulated conversation turns
- Warning when context limit exceeded
- Actual DeepSeek API call at the end

**Key Teaching Points**:
- Context window limits cause AI to "forget" earlier conversation
- Token usage grows as conversation history expands
- This is the **AI amnesia problem** MCP solves
- Visual progress bar shows consumption (green → yellow → red)

### Demo Flow
1. Show the code (`contextDemo.js`) briefly
2. Run `npm start` and let it execute
3. Point out the progress bar filling up
4. Highlight when warnings appear (if context exceeded)
5. Show final API response
6. **Transition**: "This is why we need persistent memory... enter MCP!"

---

## 📦 Part 1: CoreText MCP Local (60 min)

### Start Inspector
```bash
cd coretext-mcp
npm run inspector
# Opens http://localhost:5173
```

### Test Tools in Inspector

**Create Memory**:
```json
{"content": "MCP enables persistent AI memory", "type": "semantic", "tags": ["mcp", "demo"]}
```

**Read Memory** (use returned UUID):
```json
{"id": "uuid-here"}
```

**Search**:
```json
{"query": "mcp"}
```

**Stats** (no args)

**Enrich** (if API key):
```json
{"id": "uuid-here"}
```

### View File
```bash
cat data/memory.json | jq
```

---

## 🏛️ Part 2: Stoic MCP Local (60 min)

### Build TypeScript
```bash
cd stoic-mcp/local
npm run build
ls dist/
```

### Start Inspector
```bash
npx @modelcontextprotocol/inspector node dist/index.js
```

### Test Tools in Inspector

**Random Quote** (no args)

**Search by Author**:
```json
{"author": "Marcus Aurelius"}
```

**Search by Theme**:
```json
{"theme": "courage"}
```

**Add Quote**:
```json
{
  "text": "The best revenge is not to be like your enemy.",
  "author": "Marcus Aurelius",
  "source": "Meditations",
  "theme": "mindset"
}
```

**Toggle Favorite** (use quote ID):
```json
{"quote_id": "15"}
```

**Get Favorites** (no args)

**Update Notes**:
```json
{"quote_id": "15", "notes": "Remember during debugging!"}
```

**Get Explanation** (if API key):
```json
{"quote_id": "15"}
```

**Generate Quote**:
```json
{"theme": "debugging"}
```

### Bulk Import
```bash
cat > quotes-source/demo.txt << 'EOF'
"First, say to yourself what you would be; then do what you have to do." - Epictetus, Discourses
EOF

npm run import demo.txt
```

---

## 🔧 Part 3: Client Configuration (30 min)

### Claude Desktop Config

**Location**:
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`
- Mac: `~/Library/Application Support/Claude/claude_desktop_config.json`

**Config**:
```json
{
  "mcpServers": {
    "coretext": {
      "command": "node",
      "args": ["C:\\github\\context-engineering-2\\coretext-mcp\\src\\index.js"],
      "env": {"DEEPSEEK_API_KEY": "sk-xxxxx"}
    },
    "stoic": {
      "command": "node",
      "args": ["C:\\github\\context-engineering-2\\stoic-mcp\\local\\dist\\index.js"],
      "env": {"DEEPSEEK_API_KEY": "sk-xxxxx"}
    }
  }
}
```

**Restart Claude**:
```bash
# Windows
taskkill /IM "Claude.exe" /F

# Mac
killall Claude
```

### Test in Claude Desktop

**CoreText**:
```
Create a semantic memory: "MCP revolutionizes AI context management"
```

**Stoic**:
```
Give me a Stoic quote about courage
```

### VS Code Config

**Location**: `.vscode/mcp.json` in workspace

```json
{
  "mcpServers": {
    "coretext": {
      "command": "node",
      "args": ["${workspaceFolder}/coretext-mcp/src/index.js"]
    },
    "stoic": {
      "command": "node",
      "args": ["${workspaceFolder}/stoic-mcp/local/dist/index.js"]
    }
  }
}
```

---

## ☁️ Part 4: Azure Deployment (60 min)

### Create Resource Group
```bash
az group create --name stoic-rg-demo --location eastus
```

### Create Managed Identity
```bash
az identity create --name stoic-msi-demo --resource-group stoic-rg-demo

MSI_PRINCIPAL_ID=$(az identity show --name stoic-msi-demo --resource-group stoic-rg-demo --query principalId -o tsv)
echo $MSI_PRINCIPAL_ID
```

### Build Docker Image
```bash
cd stoic-mcp
docker build -t stoic-mcp:demo -f Dockerfile .
docker images | grep stoic
```

### Push to ACR
```bash
# Create ACR
az acr create --name timwarneracr --resource-group stoic-rg-demo --sku Basic

# Login
az acr login --name timwarneracr

# Tag and push
docker tag stoic-mcp:demo timwarneracr.azurecr.io/stoic-mcp:v1
docker push timwarneracr.azurecr.io/stoic-mcp:v1
```

### Deploy Bicep
```bash
az deployment group create \
  --resource-group stoic-rg-demo \
  --template-file azure/main.bicep \
  --parameters \
    managedIdentityName=stoic-msi-demo \
    containerImage=timwarneracr.azurecr.io/stoic-mcp:v1 \
    deepseekApiKey=$DEEPSEEK_API_KEY
```

**Watch in Portal**: Navigate to `stoic-rg-demo` resource group

### Get Container App URL
```bash
STOIC_URL=$(az containerapp show \
  --name stoic-app-* \
  --resource-group stoic-rg-demo \
  --query properties.configuration.ingress.fqdn -o tsv)

echo "https://$STOIC_URL"

# Test health
curl https://$STOIC_URL/health
```

### View Logs
```bash
az containerapp logs show \
  --name stoic-app-* \
  --resource-group stoic-rg-demo \
  --follow
```

### KQL Query in Portal

Navigate to Log Analytics → Logs:

```kql
ContainerAppConsoleLogs_CL
| where ContainerAppName_s contains "stoic"
| project TimeGenerated, Log_s
| order by TimeGenerated desc
| take 100
```

---

## 🧹 Cleanup

### Delete Azure Resources
```bash
az group delete --name stoic-rg-demo --yes --no-wait
```

### Reset Local Data
```bash
# CoreText
cd coretext-mcp
rm data/memory.json

# Stoic
cd stoic-mcp/local
cp quotes.json quotes-backup.json
```

---

## 🐛 Quick Troubleshooting

### Inspector Won't Start
```bash
lsof -ti:5173 | xargs kill -9
```

### Claude Desktop Not Loading Servers
1. Check config file location
2. Validate JSON: `jq . config.json`
3. Use absolute paths with `\\` on Windows
4. Check Claude Desktop logs: `%APPDATA%\Claude\logs\`
5. Completely restart Claude (kill process)

### TypeScript Build Errors
```bash
npm install --save-dev @types/node
npm run build
```

### Azure Deployment Fails (Free Tier)
- Only 1 Cosmos DB free tier per subscription
- Change `enableFreeTier: false` in Bicep
- Or use existing free tier account

### Container App Not Starting
```bash
# Check logs
az containerapp logs show --name stoic-app-* --resource-group stoic-rg-demo --tail 100

# Test image locally
docker run -p 3000:3000 timwarneracr.azurecr.io/stoic-mcp:v1
curl http://localhost:3000/health
```

---

## 📊 Key Stats to Mention

**CoreText MCP**:
- 8 tools (memory CRUD)
- 3 resources (overview, context-stream, knowledge-graph)
- 2 memory types (episodic, semantic)
- JSON storage (~100MB limit)

**Stoic MCP**:
- 9 tools (quote management + AI)
- TypeScript compiled to JavaScript
- 18 theme categories
- Bulk import with auto-detection

**Azure Costs**:
- Cosmos DB Free Tier: $0 (1000 RU/s, 25GB)
- Container Apps: $1-5/month (scale-to-zero)
- Key Vault: $0.03/month
- Log Analytics: $2-5/month
- **Total: $3-10/month**

**Scaling**:
- Min replicas: 0 (scale-to-zero)
- Max replicas: 3
- CPU: 0.25 cores per replica
- Memory: 0.5 GiB per replica
- Cold start: ~5-10 seconds

---

## 🎤 Demo Checklist

**Before Starting**:
- [ ] 5 terminals open
- [ ] Azure CLI authenticated
- [ ] Environment variables set
- [ ] Claude Desktop config backed up
- [ ] Browser tabs ready (Portal, MCP spec, diagrams)
- [ ] Screen sharing tested

**Part 1** (60 min):
- [ ] CoreText code walkthrough (15 min)
- [ ] MCP Inspector demo (25 min)
- [ ] Key takeaways (5 min)

**Part 2** (60 min):
- [ ] Stoic code walkthrough (20 min)
- [ ] TypeScript build (5 min)
- [ ] MCP Inspector demo (15 min)
- [ ] Bulk import (5 min)
- [ ] Key takeaways (5 min)

**Part 3** (30 min):
- [ ] Claude Desktop config (15 min)
- [ ] Test in Claude (5 min)
- [ ] VS Code config (10 min)

**Part 4** (60 min):
- [ ] Azure prerequisites (5 min)
- [ ] Docker build (10 min)
- [ ] Bicep deployment (15 min)
- [ ] Verify and test (10 min)
- [ ] Monitoring (5 min)
- [ ] Cost analysis (5 min)
- [ ] Key takeaways (5 min)

**After Demo**:
- [ ] Q&A session
- [ ] Share repo link
- [ ] Show diagrams for reference
- [ ] Cleanup (optional)

---

## 📞 Emergency Contacts

**If something breaks during live demo**:

1. **Network fails**: Use pre-recorded video clips
2. **Azure portal slow**: Use Azure CLI commands
3. **MCP Inspector crashes**: Use test-client.js instead
4. **Docker build fails**: Use pre-built image from Docker Hub
5. **Forget a command**: This quick reference card!

---

## 🔗 Quick Links

- Full Demo Script: [DEMO_SCRIPT.md](DEMO_SCRIPT.md)
- Architecture Diagrams: [diagrams/](diagrams/)
- Main README: [README.md](README.md)
- MCP Specification: https://spec.modelcontextprotocol.io/
- Azure Portal: https://portal.azure.com

---

**Print this page and keep it handy during the demo!** 🎯

**Version**: 1.0 | **Updated**: October 30, 2025
