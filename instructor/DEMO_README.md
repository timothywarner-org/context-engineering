# MCP Demo Documentation

**Complete demonstration materials for O'Reilly Live Training: Context Engineering with MCP**

---

## 📚 What's Included

This directory contains comprehensive demonstration materials for presenting both MCP servers (CoreText and Stoic) in local development and Azure production environments.

> **Note**: The coretext-mcp and stoic-mcp servers are conceptual teaching examples designed to illustrate MCP patterns and best practices. They serve as valuable reference implementations for understanding MCP architecture, tool design, and Azure deployment strategies.

### Documentation Files

| File | Lines | Size | Purpose |
|------|-------|------|---------|
| **[DEMO_SCRIPT.md](DEMO_SCRIPT.md)** | 2,168 | 52 KB | Complete 3-4 hour demo script with detailed walkthroughs |
| **[DEMO_QUICK_REFERENCE.md](DEMO_QUICK_REFERENCE.md)** | 447 | 8.9 KB | Printable quick reference card for live presentations |

### Total Documentation
- **2,615 lines** of demonstration guidance
- **~61 KB** of comprehensive materials
- **4 major parts** covering full stack (local → Azure)
- **85+ code examples** ready to copy-paste
- **Complete troubleshooting guide** for common issues

---

## 🎯 Demo Structure

### Part 1: CoreText MCP Local (60 minutes)
**Focus**: Memory server with CRUD operations

**What You'll Demo**:
- ✅ Code walkthrough (MemoryEntry, MemoryManager, DeepSeek enrichment)
- ✅ MCP Inspector testing (8 tools, 3 resources)
- ✅ Memory lifecycle (create → read → update → delete)
- ✅ Episodic vs Semantic memory types
- ✅ Context persistence across sessions
- ✅ AI enrichment with fallback mode

**Key Commands**:
```bash
cd coretext-mcp
npm run inspector
# Test tools in browser at http://localhost:5173
cat data/memory.json
```

### Part 2: Stoic MCP Local (60 minutes)
**Focus**: TypeScript quote management with AI features

**What You'll Demo**:
- ✅ TypeScript code structure (types, storage, AI service)
- ✅ Build process (tsc compilation)
- ✅ MCP Inspector testing (9 tools)
- ✅ Personal features (favorites, notes)
- ✅ AI explanations for developers
- ✅ Quote generation on demand
- ✅ Bulk import with theme detection

**Key Commands**:
```bash
cd stoic-mcp/local
npm run build
npx @modelcontextprotocol/inspector node dist/index.js
npm run import demo-quotes.txt
```

### Part 3: Client Configuration (30 minutes)
**Focus**: Integrating MCP servers with AI clients

**What You'll Demo**:
- ✅ Claude Desktop configuration (Windows/Mac/Linux)
- ✅ VS Code GitHub Copilot configuration
- ✅ Testing in Claude Desktop (both servers)
- ✅ Context persistence across conversations
- ✅ Tool discovery and automatic invocation

**Key Files**:
- Claude Desktop: `%APPDATA%\Claude\claude_desktop_config.json`
- VS Code: `.vscode/mcp.json`

### Part 4: Azure Deployment (60 minutes)
**Focus**: Production deployment on Azure

**What You'll Demo**:
- ✅ Resource group and managed identity creation
- ✅ Docker multi-stage build
- ✅ Azure Container Registry push
- ✅ Bicep Infrastructure as Code deployment
- ✅ Cosmos DB Free Tier setup (2 containers)
- ✅ Key Vault secrets management
- ✅ Container Apps scaling (0-3 replicas)
- ✅ Log Analytics monitoring
- ✅ Cost analysis (~$3-10/month)

**Key Commands**:
```bash
az group create --name stoic-rg-demo --location eastus
az identity create --name stoic-msi-demo --resource-group stoic-rg-demo
docker build -t stoic-mcp:demo -f Dockerfile .
az deployment group create --resource-group stoic-rg-demo --template-file azure/main.bicep
```

---

## 🚀 Quick Start for Presenters

### 1. Print the Quick Reference Card

```bash
# Open in browser and print
code DEMO_QUICK_REFERENCE.md
# File → Print → Save as PDF or print to paper
```

Keep this card visible during the live demo for quick command lookup.

### 2. Review the Full Demo Script

```bash
code DEMO_SCRIPT.md
```

Read through once before the demo to familiarize yourself with:
- Timing for each section
- Code sections to highlight
- Expected outputs
- Talking points

### 3. Complete Pre-Demo Checklist

From DEMO_SCRIPT.md:
- [ ] 5 terminals open and positioned
- [ ] Azure CLI authenticated (`az account show`)
- [ ] Environment variables set (`$DEEPSEEK_API_KEY`)
- [ ] Git repos clean (`git status`)
- [ ] Browser tabs ready (Azure Portal, MCP spec, diagrams)
- [ ] Claude Desktop config backed up
- [ ] Screen sharing tested

### 4. Test Run (Optional but Recommended)

Do a quick 15-minute test run:

```bash
# Part 1 test: CoreText Inspector
cd coretext-mcp && npm run inspector
# Create 1 memory, verify in UI

# Part 2 test: Stoic Inspector
cd stoic-mcp/local && npm run build
npx @modelcontextprotocol/inspector node dist/index.js
# Get 1 random quote, verify in UI

# Part 3 test: Claude Desktop
# Open Claude Desktop, verify 2 servers connected

# Part 4 test: Azure CLI
az account show
# Verify authenticated and correct subscription
```

---

## 🎓 For Course Students

### Using These Materials

**During the Course**:
1. Follow along with [DEMO_QUICK_REFERENCE.md](DEMO_QUICK_REFERENCE.md)
2. Copy-paste commands as instructor demonstrates
3. Take notes on talking points and explanations

**After the Course**:
1. Use [DEMO_SCRIPT.md](DEMO_SCRIPT.md) as implementation guide
2. Follow step-by-step to recreate the demo
3. Reference troubleshooting section for issues
4. Experiment with modifications

**For Your Own Projects**:
- Use as template for building MCP servers
- Adapt Azure deployment for your use cases
- Follow security patterns (Managed Identity, Key Vault)
- Reference cost optimization strategies

### Prerequisites Knowledge

To follow along effectively:
- ✅ Basic JavaScript/TypeScript syntax
- ✅ Command line comfort (bash/PowerShell)
- ✅ Git basics (clone, commit, push)
- ✅ Azure fundamentals (resource groups, basics)
- ✅ Docker basics (build, run, push)
- ✅ JSON file format

No prior MCP experience required - that's what this course teaches!

---

## 📊 Demo Timing Guide

**Total Duration**: 3-4 hours (including Q&A and breaks)

| Segment | Duration | Key Activities |
|---------|----------|----------------|
| **Introduction** | 10 min | Course overview, prerequisites check |
| **Part 1: CoreText Local** | 60 min | Code + MCP Inspector demo |
| *Break* | 10 min | |
| **Part 2: Stoic Local** | 60 min | TypeScript + features demo |
| *Break* | 10 min | |
| **Part 3: Client Config** | 30 min | Claude Desktop + VS Code |
| *Break* | 10 min | |
| **Part 4: Azure Deployment** | 60 min | Full cloud deployment |
| **Q&A** | 20-30 min | Audience questions |
| **Total** | ~3h 50min | (adjust breaks as needed) |

**Flexibility**: Each part can be shortened or expanded based on:
- Audience questions and engagement
- Technical issues requiring troubleshooting
- Depth of code explanation desired
- Time constraints

---

## 🎬 Presentation Tips

### Before Starting

**Set Expectations**:
> "Today we'll build two complete MCP servers from scratch, test them locally, configure them in Claude Desktop, and deploy one to Azure. You'll leave with working code, architecture diagrams, and production deployment templates."

**Share Repository**:
> "All code and documentation is in this GitHub repo. You can clone it now or wait until after the demo. Everything we do today is reproducible on your machines."

### During the Demo

**Be Verbal About What You're Doing**:
- "Now I'm switching to terminal 2..."
- "I'm going to scroll to line 150 where the enrichment happens..."
- "Watch the Inspector UI on the right as I call this tool..."

**Explain Waiting Periods**:
- Docker build: "This takes 2-3 minutes, let me explain what's happening..."
- Azure deployment: "While this provisions, let's look at the Bicep template..."
- API calls: "DeepSeek is thinking... this typically takes 1-2 seconds..."

**Use the Diagrams**:
- Switch to diagram when explaining architecture
- Point out specific components: "This box here is the MemoryManager..."
- Use diagrams during deployment waiting periods

**Handle Errors Gracefully**:
- "Ah, port already in use - let me kill that process..."
- "This is a good teaching moment about..."
- Use DEMO_QUICK_REFERENCE.md troubleshooting section

### Common Pitfalls to Avoid

1. **Don't assume everything is installed**
   - Verify Node.js version at start
   - Check Azure CLI authentication early
   - Test screen sharing before starting

2. **Don't skip the 'why'**
   - Explain WHY we use MCP (context persistence)
   - Explain WHY managed identity (no credentials in code)
   - Explain WHY scale-to-zero (cost optimization)

3. **Don't rush through code**
   - Students need time to understand
   - Highlight key lines slowly
   - Pause for questions after each section

4. **Don't forget to demo the "win"**
   - Show context persisting across Claude restarts
   - Show auto-scaling in Azure
   - Show cost being low

---

## 🐛 Troubleshooting During Live Demo

### If Something Breaks...

**Keep Calm and Use Backups**:

1. **MCP Inspector won't start**
   → Use test-client.js instead
   → Or skip Inspector, show Claude Desktop directly

2. **Docker build fails**
   → Use pre-built image from Docker Hub
   → Or skip Docker, focus on Bicep template walkthrough

3. **Azure deployment takes forever**
   → Show already-deployed instance in different resource group
   → Explain what would happen while showing portal

4. **Network/internet fails**
   → Switch to local-only demos (Parts 1-3)
   → Show pre-recorded video of Azure deployment
   → Share deployment script for students to try later

5. **Forgot a command**
   → Check DEMO_QUICK_REFERENCE.md (print it!)
   → Or check DEMO_SCRIPT.md on second monitor

**Remember**: Technical difficulties happen. How you handle them teaches professionalism!

---

## 📚 Related Materials

### In This Repository

- **[README.md](README.md)** - Main course overview and resources
- **[CLAUDE.md](CLAUDE.md)** - Project-level AI guidance
- **[diagrams/](diagrams/)** - Architecture visualizations
  - [coretext-mcp-local.md](diagrams/coretext-mcp-local.md)
  - [coretext-mcp-azure.md](diagrams/coretext-mcp-azure.md)
  - [stoic-mcp-local.md](diagrams/stoic-mcp-local.md)
  - [stoic-mcp-azure.md](diagrams/stoic-mcp-azure.md)
- **[coretext-mcp/](coretext-mcp/)** - Memory server implementation
- **[stoic-mcp/](stoic-mcp/)** - Quote server implementation

### External Resources

- **MCP Specification**: https://spec.modelcontextprotocol.io/
- **MCP TypeScript SDK**: https://github.com/modelcontextprotocol/typescript-sdk
- **MCP Inspector**: https://github.com/modelcontextprotocol/inspector
- **Azure Container Apps**: https://learn.microsoft.com/azure/container-apps/
- **Azure Cosmos DB**: https://learn.microsoft.com/azure/cosmos-db/
- **Bicep**: https://learn.microsoft.com/azure/azure-resource-manager/bicep/

---

## ✅ Post-Demo Checklist

### Immediately After Demo

- [ ] Share GitHub repository link with students
- [ ] Share DEMO_SCRIPT.md direct link
- [ ] Remind students about architecture diagrams
- [ ] Answer any remaining questions in chat
- [ ] Save chat transcript (if available)

### Within 24 Hours

- [ ] Review recording (if recorded)
- [ ] Note any sections that could be improved
- [ ] Update demo script if issues discovered
- [ ] Respond to student emails/questions

### Optional Cleanup

- [ ] Delete demo resource group: `az group delete --name stoic-rg-demo`
- [ ] Remove test data from local repos
- [ ] Restore original Claude Desktop config
- [ ] Clear browser cache/history if sharing screen recording

---

## 🎯 Success Metrics

**Students should leave able to**:
1. ✅ Explain what MCP is and why it matters
2. ✅ Implement basic MCP server with tools
3. ✅ Configure MCP in Claude Desktop
4. ✅ Deploy MCP server to Azure
5. ✅ Estimate Azure costs for MCP workloads
6. ✅ Troubleshoot common MCP issues

**Evidence of success**:
- Students ask advanced questions (not just setup help)
- Students share what they'll build with MCP
- Students successfully recreate demo on their machines
- Positive feedback about clarity and pacing

---

## 📞 Support

### For Instructors

**Questions about demo materials?**
- Review [DEMO_SCRIPT.md](DEMO_SCRIPT.md) Q&A section
- Check troubleshooting guide
- Test locally before presenting

**Want to customize the demo?**
- Modify code examples for your use case
- Adjust timing based on audience level
- Add/remove sections as needed

### For Students

**Having trouble following along?**
- Clone the repo: `git clone <repo-url>`
- Check prerequisites in main README
- Use DEMO_QUICK_REFERENCE.md as checklist

**Need help after the course?**
- Review DEMO_SCRIPT.md step-by-step
- Check troubleshooting section first
- Open GitHub issue for specific problems
- Contact instructor (see main README)

---

## 📝 License & Usage

**Course Materials**: © 2026 Timothy Warner

**Usage Rights**:
- ✅ Use for learning and education
- ✅ Modify for personal projects
- ✅ Share with attribution
- ✅ Use code examples in your applications

**Attribution**:
When sharing or building on these materials, please attribute:
> Based on "MCP in Practice: Context Engineering" by Tim Warner (O'Reilly Live Training)

---

## 🙏 Acknowledgments

**Technologies**:
- Model Context Protocol by Anthropic
- Azure by Microsoft
- Node.js and TypeScript communities

**Inspiration**:
- Students who ask great questions
- Developers pushing MCP boundaries
- Open source contributors

---

## 📅 Version History

- **v1.1** (January 2026) - Updated documentation and conceptual notes
  - Updated dates and version references
  - Clarified coretext-mcp and stoic-mcp as conceptual teaching examples
- **v1.0** (October 2025) - Initial comprehensive demo materials
  - Complete 4-part demo script (2,168 lines)
  - Printable quick reference card (447 lines)
  - This README for navigation

**Future Enhancements**:
- [ ] Add video recordings of demo sections
- [ ] Create slide deck to accompany demo
- [ ] Add advanced topics (multi-agent, vector search)
- [ ] Create automated testing scripts

---

## 🚀 Ready to Present?

1. **Print** [DEMO_QUICK_REFERENCE.md](DEMO_QUICK_REFERENCE.md)
2. **Open** [DEMO_SCRIPT.md](DEMO_SCRIPT.md) on second monitor
3. **Review** [Pre-Demo Checklist](#quick-start-for-presenters)
4. **Test** screen sharing and audio
5. **Take a deep breath** - you've got this! 🎯

**Remember**: The goal is not perfection, but learning. Your enthusiasm and clear explanations matter more than flawless execution.

**Good luck with your demo!** 🌟

---

**Questions?** Review [DEMO_SCRIPT.md](DEMO_SCRIPT.md) Q&A section or contact Tim Warner via [techtrainertim.com](https://techtrainertim.com)
