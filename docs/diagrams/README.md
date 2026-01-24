# WARNERCO Schematica Architecture Diagrams

High-quality Mermaid diagrams documenting the WARNERCO Robotics Schematica system architecture.

## Available Diagrams

| Diagram | Description | Key Elements |
|---------|-------------|--------------|
| **[system-overview.md](system-overview.md)** | Full system architecture | Client layer, MCP primitives, LangGraph, 3-tier memory |
| **[langgraph-flow.md](langgraph-flow.md)** | RAG pipeline details | 5-node flow, intent classification, state management |
| **[azure-deploy.md](azure-deploy.md)** | Azure deployment | Container Apps, AI Search, OpenAI, security |
| **[mcp-primitives.md](mcp-primitives.md)** | MCP capabilities | 11 tools, 10 resources, 5 prompts, elicitations |

## Diagram Features

### Theme Configuration
All diagrams use custom Mermaid themes for consistency:
```mermaid
%%{init: {'theme': 'base', 'themeVariables': {
    'primaryColor': '#...',
    'primaryTextColor': '#fff',
    'fontFamily': 'Inter, system-ui, sans-serif'
}}}%%
```

### Color Coding
| Color | Meaning |
|-------|---------|
| Blue (#0078d4) | Clients, Azure services |
| Green (#059669) | Tools, compute |
| Purple (#7c3aed) | Prompts, MCP protocol |
| Orange (#d83b01) | AI services |
| Teal (#008272) | Data services |
| Gray (#475569) | Security, infrastructure |

### Typography
- **Bold headers** using `<b>` tags
- Multi-line labels with `<br/>`
- Monospace for code/URIs

## Viewing Options

### VS Code (Recommended)
1. Install [Mermaid Preview extension](https://marketplace.visualstudio.com/items?itemName=vstirbu.vscode-mermaid-preview)
2. Open any `.md` file
3. Use preview pane (Ctrl+Shift+V)

### GitHub
Diagrams render automatically in GitHub's markdown viewer.

### Mermaid Live Editor
Copy the Mermaid code block and paste into [mermaid.live](https://mermaid.live/) for interactive editing.

### Export to PNG/SVG
```bash
# Install Mermaid CLI
npm install -g @mermaid-js/mermaid-cli

# Generate images
mmdc -i system-overview.md -o system-overview.svg -t dark
mmdc -i langgraph-flow.md -o langgraph-flow.svg -t dark
mmdc -i azure-deploy.md -o azure-deploy.svg -t dark
mmdc -i mcp-primitives.md -o mcp-primitives.svg -t dark
```

## SVG Files

Pre-rendered SVGs are available in this directory:
- `system-overview.svg`
- `langgraph-flow.svg`
- `azure-deploy.svg`

To regenerate after updates:
```bash
for f in *.md; do
    [[ "$f" != "README.md" ]] && mmdc -i "$f" -o "${f%.md}.svg" -t dark -b transparent
done
```

## Diagram Architecture Consistency

All diagrams follow these conventions:

1. **Top-to-bottom flow** for vertical hierarchy
2. **Left-to-right flow** for pipelines
3. **Subgraph nesting** for logical grouping
4. **Consistent arrow styles**:
   - `-->` solid: data flow
   - `-.->` dashed: security/config
   - `==>` thick: main path

## Updates

When updating diagrams:
1. Maintain color consistency
2. Test in VS Code preview
3. Verify text doesn't overlap
4. Regenerate SVGs if needed
5. Update this README if adding new diagrams

---

*Diagrams maintained for Context Engineering with MCP course.*
*Last updated: January 2025*
