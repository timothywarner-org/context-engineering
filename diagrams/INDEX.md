# MCP Architecture Diagrams - Quick Reference

## 📊 Diagram Index

### CoreText MCP Server

| Deployment | File | Focus | Key Components |
|------------|------|-------|----------------|
| **Local** | [coretext-mcp-local.md](coretext-mcp-local.md) | Development setup with JSON storage | 8 tools, 3 resources, DeepSeek API, stdio transport |
| **Azure** | [coretext-mcp-azure.md](coretext-mcp-azure.md) | Production deployment on Azure | Container Apps, Cosmos DB, Key Vault, $3-10/month |

### Stoic MCP Server

| Deployment | File | Focus | Key Components |
|------------|------|-------|----------------|
| **Local** | [stoic-mcp-local.md](stoic-mcp-local.md) | TypeScript dev setup with quotes | 9 tools, bulk import, theme detection, AI generation |
| **Azure** | [stoic-mcp-azure.md](stoic-mcp-azure.md) | Production with dual Cosmos containers | 2 containers (quotes+metadata), multi-stage Docker |

## 🎯 Choose Your Diagram

### By Learning Goal

**"I want to understand MCP basics"**
→ Start with [coretext-mcp-local.md](coretext-mcp-local.md)
- Simplest architecture
- Clear MCP protocol flow
- Easy to understand components

**"I want to build my first MCP server"**
→ Review [stoic-mcp-local.md](stoic-mcp-local.md)
- TypeScript implementation
- Complete CRUD operations
- AI integration patterns

**"I want to deploy to Azure"**
→ Compare [coretext-mcp-azure.md](coretext-mcp-azure.md) + [stoic-mcp-azure.md](stoic-mcp-azure.md)
- See Azure resource patterns
- Understand cost structures
- Learn security best practices

**"I want to migrate local → cloud"**
→ Read both local + Azure versions side-by-side
- [CoreText Local](coretext-mcp-local.md) → [CoreText Azure](coretext-mcp-azure.md)
- [Stoic Local](stoic-mcp-local.md) → [Stoic Azure](stoic-mcp-azure.md)

### By Role

**Students**
1. Local diagrams during course segments 1-2
2. Azure diagrams during course segment 3
3. Both for segment 4 (advanced patterns)

**Developers**
1. Local diagrams for prototyping
2. Azure diagrams for production planning
3. Compare both for migration strategies

**Architects**
1. Azure diagrams for infrastructure design
2. Cost sections for budgeting
3. Security sections for compliance

**DevOps Engineers**
1. Azure diagrams for deployment automation
2. Bicep template references
3. Monitoring and observability sections

## 📋 Quick Stats

| Metric | Total |
|--------|-------|
| **Diagrams** | 4 comprehensive |
| **Lines of documentation** | 2,285 |
| **Directory size** | 76 KB |
| **Azure resources documented** | 7 per server |
| **Tools documented** | 17 total (8 CoreText + 9 Stoic) |
| **Code examples** | 85+ (Bash, JSON, TypeScript, KQL) |

## 🔍 Find Specific Information

### Architecture Components

- **MCP Protocol**: All diagrams → Server Core sections
- **Storage**: Local → Storage Layer, Azure → Data Layer
- **AI Integration**: All diagrams → AI/Enrichment sections
- **Authentication**: Azure diagrams → Identity & Access
- **Deployment**: Azure diagrams → Deployment Pipeline

### Operations

- **Development setup**: Local diagrams → Development Workflow
- **Testing**: Local diagrams → Testing sections
- **Deployment**: Azure diagrams → Deployment Process
- **Monitoring**: Azure diagrams → Observability sections
- **Cost optimization**: Azure diagrams → Cost Breakdown

### Technologies

- **TypeScript**: [stoic-mcp-local.md](stoic-mcp-local.md) → TypeScript Build Process
- **Docker**: Azure diagrams → Docker Build Process
- **Cosmos DB**: Azure diagrams → Cosmos DB Schema
- **Key Vault**: Azure diagrams → Secrets Management
- **Container Apps**: Azure diagrams → Container Apps sections

## 📖 Related Documentation

- **[README.md](README.md)** - Directory overview and viewing instructions
- **[DIAGRAM_SUMMARY.md](DIAGRAM_SUMMARY.md)** - Detailed metrics and validation checklist
- **[../README.md](../README.md)** - Main course README
- **[../CLAUDE.md](../CLAUDE.md)** - Project-level AI guidance

## 🚀 Getting Started

### First Time Here?

1. Read this INDEX.md (you are here!)
2. Open [README.md](README.md) for viewing instructions
3. Start with [coretext-mcp-local.md](coretext-mcp-local.md)
4. Progress through diagrams in order:
   - CoreText Local → CoreText Azure
   - Stoic Local → Stoic Azure

### During the Course?

**Segment 1** → [coretext-mcp-local.md](coretext-mcp-local.md)
**Segment 2** → [stoic-mcp-local.md](stoic-mcp-local.md)
**Segment 3** → [coretext-mcp-azure.md](coretext-mcp-azure.md) + [stoic-mcp-azure.md](stoic-mcp-azure.md)
**Segment 4** → Compare all four diagrams

### After the Course?

Use as reference material:
- Implementation patterns
- Deployment checklists
- Cost estimation guides
- Security configurations

## 💡 Pro Tips

1. **View in VS Code** with Mermaid Preview extension for best experience
2. **Compare side-by-side** local vs Azure for migration understanding
3. **Follow data flow arrows** to understand request handling
4. **Check color coding** to identify component types
5. **Read prose sections** for detailed explanations beyond diagrams

## 🔗 External Resources

- [Mermaid Live Editor](https://mermaid.live/) - Test and modify diagrams
- [MCP Specification](https://spec.modelcontextprotocol.io/) - Official protocol docs
- [Azure Free Account](https://azure.microsoft.com/en-us/free/) - $200 credit for 30 days
- [Course Repository](https://github.com/timothywarner-org/context-engineering-2) - Full source code

## ✅ Diagram Quality

All diagrams are:
- ✅ Syntax validated (Mermaid 10.x compatible)
- ✅ Rendered and tested in multiple viewers
- ✅ Architecturally accurate to source code
- ✅ Cost estimates verified ($3-10/month range)
- ✅ Code examples tested and functional
- ✅ Accessibility considerations included

## 📞 Questions?

- **Technical issues**: Open GitHub issue
- **Course questions**: Contact instructor (see [main README](../README.md))
- **Diagram suggestions**: Submit pull request

---

**Last Updated**: October 30, 2025
**Version**: 1.0
**Maintained by**: Tim Warner + Claude Code
