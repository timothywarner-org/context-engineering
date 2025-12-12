# Context Engineering with MCP: From Prompts to Persistent AI Memory

<img src="images/cover.png" alt="Context Engineering with MCP Course Cover" width="700"/>

Welcome to the training hub for mastering **Context Engineering with Model Context Protocol (MCP)**. Whether you're building AI applications or deepening your understanding of persistent AI memory, this guide provides everything you need to implement production-ready context systems.

---

## Quick Start for Students

**New to this course?** Start here:

1. **[Student Setup Guide](student/STUDENT_SETUP_GUIDE.md)** - Prepare your environment before class (30-60 min)
2. **[Validate Environment](scripts/validate-environment.js)** - Run `node scripts/validate-environment.js` to check your setup
3. **[Troubleshooting FAQ](student/TROUBLESHOOTING_FAQ.md)** - Quick fixes for common issues
4. **[Hands-On Labs](labs/)** - Progressive exercises from beginner to advanced
5. **[Post-Course Resources](student/POST_COURSE_RESOURCES.md)** - Continue learning after the training

**During class:** Keep the [Troubleshooting FAQ](student/TROUBLESHOOTING_FAQ.md) open for quick reference.

---

## Repository Structure

```
context-engineering/
│
├── instructor/              # Instructor materials
│   ├── course-plan.md           # Full course plan
│   ├── DEMO_SCRIPT.md           # Complete demo walkthrough
│   ├── RUNBOOK.md               # Execution procedures
│   └── *.pptx                   # Presentation deck
│
├── student/                 # Student materials
│   ├── STUDENT_SETUP_GUIDE.md   # Pre-course setup
│   ├── TROUBLESHOOTING_FAQ.md   # Common issues & fixes
│   └── POST_COURSE_RESOURCES.md # After-class learning
│
├── reference/               # Reference documentation
│   ├── IMPLEMENTATION_GUIDE.md  # Choose the right pattern
│   ├── MCP_TUTORIALS.md         # MCP tutorials & guides
│   ├── CONFIG_GUIDE.md          # Configuration reference
│   └── POPULAR_REMOTE_MCP_SERVERS.md
│
├── mcp-servers/             # MCP server implementations
│   ├── coretext-mcp/            # Main teaching example (JavaScript)
│   ├── stoic-mcp/               # TypeScript production example
│   ├── context_journal_mcp_local/   # Python implementation
│   ├── context_journal_mcp_azure/   # Azure deployment
│   └── deepseek-context-demo/       # DeepSeek integration
│
├── labs/                    # Hands-on exercises
│   └── lab-01-hello-mcp/        # Your first MCP server
│
├── examples/                # Reference implementations
│   └── filesystem-mcp/          # File operations server
│
├── diagrams/                # Architecture diagrams
├── images/                  # Course images
├── scripts/                 # Utility scripts
├── config/                  # Sample configuration files
└── docs/                    # Internal documentation
```

---

## Course Overview

**Level:** Intermediate
**Duration:** 2-4 hours (flexible format)
**Format:** Hands-on live training

### What You'll Build

You mastered prompting—now stop your AI from forgetting everything. This hands-on course teaches you **Context Engineering** using MCP—the production-ready protocol adopted by Microsoft and Anthropic.

**By the end of this course, you will have:**

- Built a working MCP server that gives AI access to your GitHub repositories
- Deployed production MCP infrastructure to Azure with authentication and monitoring
- Implemented multi-agent memory systems that persist across sessions
- Configured Claude Desktop, VS Code Copilot, and ChatGPT with persistent context

---

## First-Party Reference Docs

- **[MCP Specification](https://spec.modelcontextprotocol.io/)** - Official protocol specification
- **[MCP Documentation](https://modelcontextprotocol.io/docs)** - Protocol overview
- **[MCP TypeScript SDK](https://github.com/modelcontextprotocol/typescript-sdk)** - Official SDK
- **[Official MCP Servers](https://github.com/modelcontextprotocol/servers)** - Production-ready servers
- **[Claude MCP Documentation](https://docs.claude.com/en/docs/mcp)** - Claude integration guide

---

## Required Setup

**AI Platform Access**
- [Claude Desktop](https://claude.ai/download) (Windows/Mac) - Native MCP support
- [VS Code](https://code.visualstudio.com/) with [GitHub Copilot](https://marketplace.visualstudio.com/items?itemName=GitHub.copilot)

**Development Environment**
- [Node.js 20 LTS](https://nodejs.org/) or [Python 3.10+](https://www.python.org/downloads/)
- [Git](https://git-scm.com/downloads)
- [Azure CLI](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli) (for deployment labs)

**MCP Development Tools**
```bash
# Install MCP Inspector globally
npm install -g @modelcontextprotocol/inspector

# Install TypeScript SDK
npm install @modelcontextprotocol/sdk
```

---

## Your Instructor

### Tim Warner

**Microsoft MVP** - Azure AI and Cloud/Datacenter Management (6+ years)
**Microsoft Certified Trainer** (25+ years)

- Website: [techtrainertim.com](https://techtrainertim.com)
- LinkedIn: [linkedin.com/in/timothywarner](https://www.linkedin.com/in/timothywarner/)
- YouTube: [youtube.com/timothywarner](https://www.youtube.com/channel/UCim7PFtynyPuzMHtbNyYOXA)
- Bluesky: [@techtrainertim.bsky.social](https://bsky.app/profile/techtrainertim.bsky.social)

---

## License & Usage

© 2025 Timothy Warner. Course materials provided for educational purposes.

Model Context Protocol is an open standard - free to implement in commercial and open-source projects.

---

## Contributing

Found an issue or have a suggestion? [Open an issue](https://github.com/timothywarner-org/context-engineering/issues) or submit a pull request.
