# Live Online Training Proposal: MCP in Practice: Engineering AI Memory from Prompt to Persistence

## Course Metadata

**Title:** MCP in Practice: Engineering AI Memory from Prompt to Persistence

**One-line Sell:** Deploy production MCP servers that give AI agents real-time access to tools, APIs, and databases - exactly like Anthropic and Microsoft do

**Content Level:** Intermediate to Advanced

**Previous Title:** N/A

**Instructor name:** Tim Warner

**Publisher**: Pearson

**Editorial contact:** [To be completed by Pearson Editor]

**Price**: [To be completed by Pearson Editor]

**Course Duration:** 4 hours

**Preferred First Event Dates and Start Time:** [To be coordinated from available dates and times]

**Katacoda-Based Labs:** N/A

## Description

### Three Key Differentiators

- **Deploy real MCP servers live**: Wire up tool-calling that lets ChatGPT query databases, Claude access APIs, and Copilot manipulate files - no custom code required

- **Master the protocol powering AI's future**: MCP is already in Claude, coming to Windows, and spreading fast - learn it before everyone else does

- **Build what enterprises actually need**: Multi-agent orchestration, persistent memory, and dynamic tool discovery - the missing pieces for production AI

### Course Summary

**MCP (Model Context Protocol) is the game-changing standard that transforms AI from chat toys into production tools. While others teach prompting, you'll learn the protocol that lets AI agents discover and invoke external capabilities dynamically - databases, APIs, file systems, anything. This is the technology behind Claude's computer use, Microsoft's Copilot extensions, and the next wave of enterprise AI systems.**

**In this hands-on course, you'll deploy real MCP servers, connect them to ChatGPT, Claude, and Copilot, then architect multi-agent workflows with persistent memory. No more context loss. No more copy-paste. Just AI that actually *does things*. You'll implement the same patterns used at Anthropic, Microsoft, and leading AI companies - giving you skills that are desperately needed but barely taught. By course end, you'll have working MCP servers, production patterns, and the confidence to build AI systems that remember, reason, and take action.**

### What you'll learn and how you can apply it

By the end of this live online course, you'll be able to:

- **Engineer persistent AI memory systems** using MCP servers to store, retrieve, and chain context across ChatGPT, Claude, and Copilot sessions

- **Build stateful conversation architectures** where MCP enables tool discovery AND maintains context between interactions - no more AI amnesia

- **Design context-aware workflows** that use MCP to access vector databases, preserve conversation history, and implement memory patterns like episodic and semantic storage

- **Deploy production context systems** combining MCP's tool-calling with advanced patterns like context pruning, memory hierarchies, and cross-agent state sharing

### This live event is for you because...

- **You're exhausted by AI amnesia** - tired of re-explaining context every conversation and want your AI to remember what matters across sessions

- **You need stateful AI workflows** - not just better prompts, but agents with persistent memory that can query databases, call APIs, and maintain context

- **You see MCP as the missing link** - you understand context engineering principles but need the protocol that makes persistent memory actually work

- **You want production-ready solutions** - while others theorize about AI memory, you'll build real systems using MCP servers, vector stores, and conversation chains

### Prerequisites

**These prerequisites ensure you're ready to build stateful AI systems with MCP:**

- **Context engineering fundamentals** - Experience with prompt chaining, conversation design, or fighting AI amnesia (you know the pain!)

- **One AI platform minimum** - Active use of ChatGPT, Claude, or Copilot (you understand context windows and their limits)

- **Basic technical comfort** - Command line basics, JSON understanding, and willingness to deploy servers (we'll guide you through it)

- **API/webhook awareness** - You don't need to code, but should understand how systems talk to each other

- **Problem-driven mindset** - Come with a real context persistence challenge you want to solve

### Course Set-up

**AI Platform Access (Required)**
- Active accounts with tool/plugin access: ChatGPT Plus/Team, Claude Pro, or GitHub Copilot
- Enable beta features where available (especially Claude's MCP support)

**Development Environment**
- **Node.js 20+ or Python 3.11+** - for running MCP servers (installers provided in repo)
- **Docker Desktop** - for containerized MCP deployments (optional but recommended)
- **VS Code or similar editor** - with JSON syntax highlighting

**GitHub Repository**
- Clone before class: **github.com/timothywarner-org/mcp-context-engineering**
- Contains: MCP server templates, vector DB configs, memory pattern examples, API connectors
- Pre-configured servers for: filesystem access, database queries, API calls, memory storage

**MCP Toolchain**
- **MCP SDK**: Will install during class via `npm install @modelcontextprotocol/sdk`
- **MCP Inspector**: Browser-based tool for testing MCP servers (link in repo)
- **API Testing Tool**: Postman, Bruno, or similar for debugging MCP endpoints

**Required Browser Extensions**
- **Claude Desktop** (if available) or browser access to claude.ai
- **JSON Viewer** for inspecting MCP protocol messages

**Network Requirements**
- Stable internet for API calls and tool discovery
- Ability to run local servers on ports 3000-3100 (check firewall settings)
- Access to GitHub, npm registry, and AI platform endpoints

**Pre-class Checklist**
1. Run `npm install` in the cloned repo to verify Node.js setup
2. Test Docker with `docker run hello-world` (optional)
3. Ensure you can access your AI platforms with tool/plugin features
4. Review the `/examples` folder for MCP server patterns we'll implement

### Recommended Preparation

- **Attend**: *The Elements of Prompt Engineering* by Tim Warner: https://www.oreilly.com/live-events/the-elements-of-prompt-engineering/0790145064170/
- **Read**: *Quick Start Guide to Large Language Models: Strategies and Best Practices for Using ChatGPT and Other LLMs* by Sinan Ozdemir https://www.oreilly.com/library/view/quick-start-guide/9780138199425/
- **Watch**: *How LLMs Understand & Generate Human Language* by Kate Harwood https://www.oreilly.com/videos/how-llms-understand/9780135414309/

### Recommended Follow-up

- **Watch**: *Generative AI Toolbox* by Shaun Wassell https://www.oreilly.com/library/view/generative-ai-toolbox/9780135421246/
- **Read**: *AI for Everyone: A Beginner's Handbook for Artificial Intelligence (AI)* by Pearson https://www.oreilly.com/library/view/ai-for-everyone/9789361590832/
- **Attend**: *LangChain for Generative AI Pipelines* by Bruno Gonçalves: https://www.oreilly.com/live-events/langchain-for-generative-ai-pipelines/0642572002267/
- **Watch**: *Securing Generative AI* by Omar Santos https://www.oreilly.com/library/view/securing-generative-ai/9780135401804/

### Schedule

**[Keep for registration page:] Time for breaks and Q&A will be included throughout the course.**

**Segment 1: Context Crisis Meets MCP Solution (55 minutes)**
- Why prompts fail: the stateless AI problem demonstrated live
- Introduction to MCP: the protocol enabling persistent memory and tool discovery
- Live demo: Same workflow with and without MCP - watch AI gain memory and capabilities
- Anatomy of an MCP server: tools, resources, and prompts working together
- Exercise: Map your context persistence challenge to MCP capabilities (5 min)
- Q&A (5 min)

Break (10 minutes)

**Segment 2: Deploy Your First Stateful AI System (55 minutes)**
- Live coding: Deploy a basic MCP server with memory capabilities
- Connect MCP to ChatGPT and Claude - watch them discover tools automatically
- Implement conversation memory: store, retrieve, and chain context
- Build a multi-turn workflow that remembers across sessions
- Exercise: Modify the MCP server to solve your specific context problem (5 min)
- Q&A (5 min)

Break (10 minutes)

**Segment 3: Advanced Context Engineering with MCP (55 minutes)**
- Vector database integration for semantic memory via MCP
- Multi-agent orchestration: agents sharing context through MCP servers
- Memory patterns: episodic, semantic, and working memory architectures
- Tool composition: chaining MCP servers for complex workflows
- Exercise: Design a multi-agent context flow for your use case (5 min)
- Q&A (5 min)

Break (10 minutes)

**Segment 4: Production Context Systems (45 minutes)**
- Enterprise MCP patterns: authentication, rate limiting, audit trails
- Context optimization: smart pruning, caching, and cost management
- Security considerations: context isolation and data governance
- Future-proofing: MCP in Windows, expanding platform support
- Lab exercise: Deploy a production-ready MCP memory system
- Course wrap-up and next steps (10 minutes)
