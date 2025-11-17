# Popular Remote MCP Servers Directory

A comprehensive directory of the most popular and widely-used Model Context Protocol (MCP) servers, including both official implementations and community favorites.

**Last Updated:** January 2025

---

## Table of Contents

- [Official Anthropic Servers](#official-anthropic-servers)
- [MCP Server Registries](#mcp-server-registries)
- [Top 10 Most Popular Servers](#top-10-most-popular-servers)
- [Servers by Category](#servers-by-category)
- [Installation & Configuration](#installation--configuration)
- [Cloud Hosting Platforms](#cloud-hosting-platforms)

---

## Official Anthropic Servers

Anthropic maintains official pre-built MCP servers for enterprise systems. These are production-ready and officially supported.

### Repository

- **[modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers)** - Official reference implementations

### Official Pre-Built Servers

1. **GitHub MCP Server**

   - **Repository:** [modelcontextprotocol/server-github](https://github.com/modelcontextprotocol/servers/tree/main/src/github)
   - **Purpose:** Repository management, file operations, API integration
   - **Status:** Public preview (April 2025 updates)
   - **Installation:** `npx -y @modelcontextprotocol/server-github`
   - **Configuration:** Requires `GITHUB_PERSONAL_ACCESS_TOKEN`
   - **Features:**
     - Repository file reading
     - Commit history access
     - Issue and PR management
     - Code search

2. **Slack MCP Server**

   - **Repository:** [modelcontextprotocol/server-slack](https://github.com/modelcontextprotocol/servers/tree/main/src/slack)
   - **Purpose:** Team communication and workflow automation
   - **Installation:** `npx -y @modelcontextprotocol/server-slack`
   - **Features:**
     - Read messages
     - Send notifications
     - Search conversations
     - Channel management
     - Workspace history access

3. **PostgreSQL MCP Server**

   - **Repository:** [modelcontextprotocol/server-postgres](https://github.com/modelcontextprotocol/servers/tree/main/src/postgres)
   - **Purpose:** Database operations and analysis
   - **Installation:** `npx -y @modelcontextprotocol/server-postgres postgresql://localhost/mydb`
   - **Features:**
     - Read-only queries (security)
     - Schema introspection
     - Query execution
     - Database analysis

4. **Google Drive MCP Server**

   - **Repository:** [modelcontextprotocol/server-gdrive](https://github.com/modelcontextprotocol/servers/tree/main/src/gdrive)
   - **Purpose:** Document access and management
   - **Features:**
     - Document reading
     - File search
     - Content analysis
     - Drive integration

5. **Git MCP Server**

   - **Repository:** [modelcontextprotocol/server-git](https://github.com/modelcontextprotocol/servers/tree/main/src/git)
   - **Purpose:** Local Git repository operations
   - **Features:**
     - Repository status
     - Commit operations
     - Branch management
     - Diff viewing

6. **Puppeteer MCP Server**

   - **Repository:** [modelcontextprotocol/server-puppeteer](https://github.com/modelcontextprotocol/servers/tree/main/src/puppeteer)
   - **Purpose:** Browser automation and web scraping
   - **Features:**
     - Page navigation
     - Element interaction
     - Screenshot capture
     - Web scraping

7. **Filesystem MCP Server**

   - **Repository:** [modelcontextprotocol/server-filesystem](https://github.com/modelcontextprotocol/servers/tree/main/src/filesystem)
   - **Purpose:** Secure local file operations
   - **Features:**
     - Read/write files
     - Directory management
     - Path sandboxing
     - Secure operations

8. **Fetch MCP Server**

   - **Repository:** [modelcontextprotocol/server-fetch](https://github.com/modelcontextprotocol/servers/tree/main/src/fetch)
   - **Purpose:** Web content fetching
   - **Features:**
     - HTTP requests
     - Content parsing
     - URL validation
     - Response handling

9. **Memory MCP Server**

   - **Repository:** [modelcontextprotocol/server-memory](https://github.com/modelcontextprotocol/servers/tree/main/src/memory)
   - **Purpose:** Knowledge graph-based memory system
   - **Features:**
     - Entity storage
     - Relationship management
     - Knowledge graph
     - Persistent memory

10. **Sequential Thinking MCP Server**

    - **Repository:** [modelcontextprotocol/server-sequential-thinking](https://github.com/modelcontextprotocol/servers/tree/main/src/sequential-thinking)
    - **Purpose:** Structured reasoning and thinking
    - **Features:**
      - Step-by-step reasoning
      - Thought organization
      - Logic tracking

11. **Everything MCP Server**

    - **Repository:** [modelcontextprotocol/server-everything](https://github.com/modelcontextprotocol/servers/tree/main/src/everything)
    - **Purpose:** Reference and test server
    - **Features:**
      - All MCP features demonstrated
      - Testing capabilities
      - Reference implementation

---

## MCP Server Registries

### Primary Registries

1. **[Glama](https://glama.ai/mcp/servers)**

   - **Description:** Production-ready MCP server directory
   - **Features:**
     - Sort by usage (last 30 days)
     - Natural language search
     - API access
     - Installation guides
   - **API:** MCP registry API available
   - **Popular for:** Server discovery and metrics

2. **[Smithery](https://smithery.mintlify.dev/)**

   - **Repository:** [smithery-ai/cli](https://github.com/smithery-ai/cli)
   - **Description:** Registry and management platform
   - **CLI Tool:** `@smithery/cli`
   - **Features:**
     - Server installation
     - Server management
     - Client-agnostic
     - Configuration support
   - **Installation:**
     ```bash
     npx @smithery/cli install <server-name> --client claude
     ```

3. **[MCP Server Finder](https://www.mcpserverfinder.com/)**

   - **Description:** Searchable server directory
   - **Features:**
     - Category filtering
     - Search functionality
     - Server details
     - Installation instructions

4. **[MCP Hub](https://mcphub.tools/)**

   - **Description:** MCP servers and clients explorer
   - **Features:**
     - Server browsing
     - Client information
     - Integration guides
     - Community submissions

5. **[PulseMCP](https://www.pulsemcp.com/)**

   - **Description:** MCP server documentation
   - **Features:**
     - Detailed server pages
     - Configuration examples
     - Usage guides
     - Official server listings

6. **[MCP List AI](https://www.mcplist.ai/)**

   - **Description:** AI-powered server directory
   - **Blog:** [Top 10 Essential MCP Servers](https://www.mcplist.ai/blog/top-10-essential-mcp-servers/)
   - **Features:**
     - Curated recommendations
     - Usage statistics
     - Integration guides

7. **[LobeHub MCP Servers](https://lobehub.com/mcp/)**

   - **Description:** Community server directory
   - **Features:**
     - Server templates
     - Usage examples
     - Integration patterns

---

## Top 10 Most Popular Servers

Based on usage metrics, community adoption, and feature completeness:

### 1. GitHub MCP Server

- **Provider:** Anthropic (official)
- **Use Case:** Repository management and code access
- **Popularity:** One of the most popular MCP servers
- **Documentation:** [PulseMCP GitHub Server](https://www.pulsemcp.com/servers/modelcontextprotocol-github)
- **Key Features:**
  - File operations
  - Commit history
  - PR and issue management
  - Code search

### 2. Filesystem MCP Server

- **Provider:** Anthropic (official)
- **Use Case:** Local file operations
- **Popularity:** Essential for most implementations
- **Key Features:**
  - Read/write files
  - Directory listing
  - Path sandboxing
  - Secure operations

### 3. PostgreSQL MCP Server

- **Provider:** Anthropic (official)
- **Use Case:** Database queries and analysis
- **Documentation:** [PulseMCP Postgres Server](https://www.pulsemcp.com/servers/modelcontextprotocol-postgres)
- **Key Features:**
  - Read-only queries
  - Schema introspection
  - Natural language to SQL
  - Data analysis

### 4. Slack MCP Server

- **Provider:** Anthropic (official)
- **Use Case:** Team communication automation
- **Documentation:** [PulseMCP Slack Server](https://www.pulsemcp.com/servers/slack)
- **Key Features:**
  - Message reading
  - Message sending
  - Channel management
  - Search functionality

### 5. Google Drive MCP Server

- **Provider:** Anthropic (official)
- **Use Case:** Document access and management
- **Key Features:**
  - Document reading
  - File search
  - Content analysis
  - Drive integration

### 6. Brave Search MCP Server

- **Use Case:** Privacy-focused web search
- **Key Features:**
  - Web search
  - Privacy-focused
  - Search results
  - No tracking

### 7. YouTube MCP Server

- **Repository:** [anaisbetts/mcp-youtube](https://github.com/anaisbetts/mcp-youtube)
- **Alternative:** [ZubeidHendricks/youtube-mcp-server](https://github.com/ZubeidHendricks/youtube-mcp-server)
- **Use Case:** YouTube video management and analysis
- **Documentation:** [LobeHub YouTube Server](https://lobehub.com/mcp/dannysubsense-youtube-mcp-server)
- **Key Features:**
  - Video management
  - Shorts creation
  - Analytics access
  - Subtitle extraction
  - Metadata access

### 8. Puppeteer MCP Server

- **Provider:** Anthropic (official)
- **Use Case:** Browser automation
- **Key Features:**
  - Web scraping
  - Screenshot capture
  - Page interaction
  - Navigation automation

### 9. SQLite MCP Server

- **Use Case:** Lightweight database operations
- **Key Features:**
  - Local database access
  - Query execution
  - Schema management
  - Embedded database

### 10. Memory MCP Server

- **Provider:** Anthropic (official)
- **Use Case:** Knowledge graph and persistent memory
- **Key Features:**
  - Entity storage
  - Relationship tracking
  - Knowledge graph
  - Persistent context

---

## Servers by Category

### Development Tools

#### Version Control

- **GitHub MCP Server** (official) - Repository management
- **Git MCP Server** (official) - Local Git operations
- **GitLab MCP Server** (community) - GitLab integration

#### Code & Files

- **Filesystem MCP Server** (official) - File operations
- **Blender MCP** - 3D modeling integration
- **File Server** - Advanced file management

### Databases

#### SQL Databases

- **PostgreSQL MCP Server** (official) - Postgres operations
- **SQLite MCP Server** - Lightweight database
- **MySQL MCP Server** - MySQL integration
- **SQL Server MCP** - Microsoft SQL Server

#### NoSQL & Vector Databases

- **Vector Search MCP** - Meaning-based retrieval
- **MongoDB MCP** - Document database
- **Redis MCP** - Key-value store

### Communication & Collaboration

- **Slack MCP Server** (official) - Team messaging
- **Discord MCP** - Discord integration
- **Microsoft Teams MCP** - Teams integration
- **Email MCP** - Email operations

### Cloud Storage

- **Google Drive MCP Server** (official) - Drive integration
- **Dropbox MCP** - Dropbox files
- **OneDrive MCP** - Microsoft OneDrive
- **S3 MCP** - AWS S3 storage

### Web & Automation

- **Puppeteer MCP Server** (official) - Browser automation
- **Fetch MCP Server** (official) - Web content fetching
- **Brave Search MCP** - Web search
- **Playwright MCP** - Browser testing

### AI & Data

- **OpenAI MCP** - OpenAI integration
- **Anthropic MCP** - Claude integration
- **Data Analysis MCP** - Data processing
- **Vector Embeddings MCP** - Embedding generation

### System & Operations

- **Windows Command Line MCP** - Windows CLI operations
- **Linux Shell MCP** - Linux commands
- **Docker MCP** - Container management
- **Kubernetes MCP** - K8s operations

---

## Installation & Configuration

### Using Smithery CLI

```bash

# Install Smithery CLI

npm install -g @smithery/cli

# Search for servers

smithery search "web search"

# Install a server for Claude

npx @smithery/cli install <server-name> --client claude

# Install with configuration

npx @smithery/cli install mcp-obsidian --client claude --config '{"vaultPath":"path/to/vault"}'

# List installed servers

npx @smithery/cli list servers --client claude

# Inspect a server

npx @smithery/cli inspect <server-name>

```

### Using NPX (Official Servers)

```bash

# GitHub

npx -y @modelcontextprotocol/server-github

# Slack

npx -y @modelcontextprotocol/server-slack

# PostgreSQL

npx -y @modelcontextprotocol/server-postgres postgresql://localhost/mydb

# Filesystem

npx -y @modelcontextprotocol/server-filesystem /path/to/workspace

```

### Claude Desktop Configuration

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "your_token_here"
      }
    },
    "postgres": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-postgres",
        "postgresql://localhost/mydb"
      ]
    },
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "/path/to/workspace"
      ]
    }
  }
}

```

**Config Location:**

- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux:** `~/.config/Claude/claude_desktop_config.json`

---

## Cloud Hosting Platforms

### Major Cloud Providers

1. **[Cloudflare Workers](https://blog.cloudflare.com/remote-model-context-protocol-servers-mcp/)**

   - **Transport:** SSE / Streamable HTTP
   - **Features:**
     - Global edge deployment
     - OAuth support built-in
     - Durable Objects for persistent connections
     - Python support

2. **[Google Cloud Run](https://cloud.google.com/run/docs/host-mcp-servers)**

   - **Transport:** HTTP/SSE
   - **Features:**
     - Container deployment
     - Node.js and Python support
     - Automatic scaling
     - Pay-per-use pricing

3. **[Azure Container Apps](https://techcommunity.microsoft.com/blog/appsonazureblog/host-remote-mcp-servers-in-azure-container-apps/4403550)**

   - **Transport:** SSE
   - **Features:**
     - Container-based deployment
     - API key authentication
     - Azure integration
     - Managed infrastructure

### Hosting Tools

- **[Apache APISIX](https://apisix.apache.org/blog/2025/04/21/host-mcp-server-with-api-gateway/)** - API Gateway integration
- **Docker** - Container deployment
- **Kubernetes** - Orchestrated deployment

---

## Community Lists & Resources

### Curated Lists

1. **[awesome-mcp-servers (punkpeye)](https://github.com/punkpeye/awesome-mcp-servers)**

   - Comprehensive collection
   - Production and experimental servers
   - Regular updates

2. **[awesome-mcp-servers (wong2)](https://github.com/wong2/awesome-mcp-servers)**

   - Alternative curated list
   - Categorized servers
   - Installation guides

3. **[awesome-mcp-servers (appcypher)](https://github.com/appcypher/awesome-mcp-servers)**

   - Another comprehensive list
   - Detailed descriptions
   - Use case examples

### Articles & Rankings

1. **[🚀Top 10 MCP Servers for 2025 (Yes, GitHub's Included!)](https://dev.to/fallon_jimmy/top-10-mcp-servers-for-2025-yes-githubs-included-15jg)**

   - DEV Community article
   - 2025 rankings
   - Feature comparisons

2. **[15 Best MCP Servers You Can Add to Cursor For 10x Productivity](https://www.firecrawl.dev/blog/best-mcp-servers-for-cursor)**

   - Cursor integration focus
   - Productivity enhancement
   - Configuration examples

3. **[Top 10 MCP Servers You Can Try in 2025](https://apidog.com/blog/top-10-mcp-servers/)**

   - Apidog rankings
   - Use case analysis
   - Implementation guides

4. **[10 Awesome MCP Servers](https://www.kdnuggets.com/10-awesome-mcp-servers)**

   - KDnuggets article
   - Data science focus
   - Practical examples

5. **[Best MCP Servers You Should Know](https://medium.com/data-science-in-your-pocket/best-mcp-servers-you-should-know-019226d01bca)**

   - Medium article by Mehul Gupta
   - Blender-MCP, GitHub-MCP, File servers
   - Integration examples

6. **[Top 9 MCP Servers for Git Tools in 2025](https://apidog.com/blog/top-10-mcp-servers-for-git-tools/)**

   - Git-focused servers
   - Version control workflows
   - Development tools

7. **[17+ Top MCP Registries, Directories & Marketplaces](https://medium.com/demohub-tutorials/17-top-mcp-registries-and-directories-explore-the-best-sources-for-server-discovery-integration-0f748c72c34a)**

   - Comprehensive registry list
   - Discovery platforms
   - Integration marketplaces

---

## Security Considerations

### Using Third-Party Servers

**Important:** Anthropic has not verified the correctness or security of all community servers. Use third-party MCP servers at your own risk.

### Best Practices

1. **Review source code** before installing community servers

2. **Use official servers** when available

3. **Validate credentials** and API keys

4. **Monitor server activity** in production

5. **Implement rate limiting** for public servers

6. **Use environment variables** for secrets

7. **Sandbox server access** to specific directories/resources

8. **Audit logs** for security events

---

## Contributing

### Add Your Server

- Submit to registries (Glama, Smithery, etc.)
- Create pull requests to awesome-mcp-servers lists
- Share on community forums
- Document thoroughly

### Report Issues

- Use GitHub issues for official servers
- Contact maintainers for community servers
- Share security concerns responsibly

---

**Last Updated:** January 2025

**Maintained by:** MCP in Practice Training Course

**Related:** See [MCP_TUTORIALS.md](MCP_TUTORIALS.md) for learning resources and tutorials.


