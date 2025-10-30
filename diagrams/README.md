# MCP Architecture Diagrams

This directory contains comprehensive Mermaid architecture diagrams for both MCP servers in the Context Engineering course.

## Available Diagrams

### CoreText MCP
1. **[coretext-mcp-local.md](coretext-mcp-local.md)** - Local development architecture
   - stdio transport communication
   - JSON file storage
   - DeepSeek API integration with fallback
   - 8 tools for memory CRUD operations
   - 3 resources for context visualization

2. **[coretext-mcp-azure.md](coretext-mcp-azure.md)** - Azure production architecture
   - Azure Container Apps deployment
   - Cosmos DB Free Tier storage
   - Key Vault secrets management
   - Managed Identity authentication
   - Auto-scaling (0-3 replicas)
   - Estimated cost: $3-10/month

### Stoic MCP
3. **[stoic-mcp-local.md](stoic-mcp-local.md)** - Local development architecture
   - TypeScript implementation
   - JSON file storage with metadata
   - 9 tools for quote management
   - AI-powered explanations and generation
   - Bulk import utility

4. **[stoic-mcp-azure.md](stoic-mcp-azure.md)** - Azure production architecture
   - Azure Container Apps deployment
   - Cosmos DB with 2 containers (quotes + metadata)
   - Multi-stage Docker build
   - TypeScript compilation in container
   - Production monitoring and scaling
   - Estimated cost: $3-10/month

## Viewing the Diagrams

### Option 1: VS Code
Install the [Mermaid Preview extension](https://marketplace.visualstudio.com/items?itemName=vstirbu.vscode-mermaid-preview):
```bash
code --install-extension vstirbu.vscode-mermaid-preview
```

Then open any `.md` file and use the preview button.

### Option 2: GitHub
View directly on GitHub - Mermaid diagrams render automatically in markdown files.

### Option 3: Mermaid Live Editor
Copy the Mermaid code blocks and paste into [Mermaid Live Editor](https://mermaid.live/).

### Option 4: Command Line
Install Mermaid CLI:
```bash
npm install -g @mermaid-js/mermaid-cli

# Generate PNG images
mmdc -i coretext-mcp-local.md -o coretext-mcp-local.png
mmdc -i coretext-mcp-azure.md -o coretext-mcp-azure.png
mmdc -i stoic-mcp-local.md -o stoic-mcp-local.png
mmdc -i stoic-mcp-azure.md -o stoic-mcp-azure.png
```

## Diagram Features

### Visual Elements

**Color Coding**:
- Light blue: Client applications (Claude Desktop, VS Code)
- Yellow/amber: Secrets and configuration (Key Vault, environment vars)
- Light green: Free Azure resources (Cosmos DB Free Tier, Managed Identity)
- Light orange: Paid Azure resources (Container Apps, Log Analytics)
- Purple: MCP server components
- Blue: Container/Docker infrastructure
- Teal: Build and deployment tools

**Node Types**:
- Rectangles: Services and components
- Rounded rectangles: Processes and handlers
- Cylinders: Data storage (databases, files)
- Parallelograms: External services (APIs)

**Edge Types**:
- Solid arrows: Data flow and communication
- Dashed arrows: Scaling, monitoring, and containment relationships

### Diagram Validation

All diagrams have been validated for:
- ✅ Mermaid syntax correctness
- ✅ Proper subgraph nesting
- ✅ Valid style classes and definitions
- ✅ Accurate component relationships
- ✅ Complete data flow paths

## Architecture Comparison

| Feature | Local | Azure |
|---------|-------|-------|
| **Storage** | JSON files | Cosmos DB |
| **Compute** | Local Node.js | Container Apps |
| **Scaling** | Single process | Auto-scale 0-3 |
| **Cost** | $0 | $3-10/month |
| **Availability** | Developer machine | 99.95% SLA |
| **Security** | .env files | Key Vault + RBAC |
| **Monitoring** | Console logs | Log Analytics |
| **Backup** | Git commits | Cosmos DB auto-backup |

## Common Patterns

### Both Architectures Share

1. **MCP Protocol**
   - JSON-RPC 2.0 communication
   - Tool-based operations
   - Resource-based context

2. **AI Integration**
   - DeepSeek API for enrichment/explanations
   - Graceful fallback when API unavailable
   - Structured prompts for consistent results

3. **CRUD Operations**
   - Create, Read, Update, Delete
   - Search and filtering
   - Statistics and metadata tracking

4. **Memory Types** (CoreText)
   - Episodic: Time-based events
   - Semantic: Facts and knowledge

5. **Quote Management** (Stoic)
   - Author and theme categorization
   - Favorites and personal notes
   - AI-powered explanations

### Migration Path

The diagrams illustrate the migration path from local development to Azure production:

**Phase 1: Local Development**
- Rapid iteration on developer machine
- JSON file storage for simplicity
- No infrastructure costs
- Full feature development

**Phase 2: Azure Production**
- Same code with storage adapter changes
- Infrastructure as Code (Bicep templates)
- Auto-scaling and high availability
- Production monitoring and observability

## Educational Use

These diagrams are designed for the O'Reilly Live Training course "Context Engineering with MCP". They serve multiple purposes:

1. **Visual Learning**: Complex architecture made accessible
2. **Reference Material**: Students can review after class
3. **Implementation Guide**: Shows what to build and how components connect
4. **Deployment Roadmap**: Clear path from local to production

## Diagram Structure

Each diagram follows a consistent structure:

1. **Client Layer**: Applications that consume the MCP server
2. **MCP Server Layer**: Core protocol implementation
3. **Business Logic**: Application-specific services
4. **Storage Layer**: Data persistence
5. **External Services**: APIs and third-party integrations
6. **Deployment Tools**: Build, deploy, and infrastructure

For Azure diagrams, additional sections:

7. **Azure Resource Group**: Cloud infrastructure
8. **Identity & Access**: Authentication and authorization
9. **Observability**: Monitoring and logging

## Updates and Maintenance

These diagrams are maintained alongside the codebase. When architecture changes:

1. Update the relevant `.md` file(s)
2. Verify Mermaid syntax with the Mermaid Live Editor
3. Test rendering in VS Code or GitHub preview
4. Update this README if new diagrams are added

## Questions or Issues?

For questions about the diagrams or suggestions for improvements:
- Open an issue in the [GitHub repository](https://github.com/timothywarner-org/context-engineering-2)
- Contact Tim Warner: [techtrainertim.com](https://techtrainertim.com)

## License

These diagrams are part of the Context Engineering with MCP course materials.
© 2025 Timothy Warner. For educational use.
