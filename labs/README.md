# Context Engineering with MCP - Hands-On Labs

These progressive labs will take you from building your first MCP server to deploying production-ready AI memory systems.

**Note**: This course is a work-in-progress. Additional labs are planned and will be released over time.

**Primary Teaching Example**: WARNERCO Robotics Schematica at `src/warnerco/backend/` demonstrates all advanced concepts (FastMCP, LangGraph, Graph Memory, etc.).

## Lab Structure

Each lab includes:
- **README.md** - Lab objectives and instructions
- **starter/** - Starting code template
- **solution/** - Reference solution
- **tests/** - Validation scripts (where applicable)

## Available Labs

### Lab 01: Hello MCP (30 minutes)
**Objective**: Create your first MCP server with a single tool

**What you'll learn**:
- MCP server basics and structure
- Tool registration and schema definition
- stdio transport communication
- Testing with MCP Inspector

**Start**: [lab-01-hello-mcp/](./lab-01-hello-mcp/)

---

## Coming Soon

The following labs are planned for future releases:

### Beginner Track

**Lab 02: Tool Calling Patterns** (45 minutes)
- Multiple tool registration
- Input schema validation with JSON Schema
- Error handling in tool handlers
- Returning structured data

**Lab 03: Resources and Context** (45 minutes)
- Resource registration and URI schemes
- Dynamic resource generation
- Combining tools and resources
- Resource templating

### Intermediate Track

**Lab 04: Memory Patterns** (60 minutes)
- Memory architecture patterns
- Persistent storage with JSON files
- Memory retrieval and search
- Context window optimization

**Lab 05: Production Deployment** (60 minutes)
- Docker containerization
- Azure Container Apps deployment
- Environment configuration
- Health checks and monitoring

### Advanced Track

**Lab 06: Advanced Patterns** (90 minutes)
- Vector database integration
- Semantic search with embeddings
- Multi-agent coordination
- MCP sampling (AI completions within context)

---

## Quick Start

### Running Lab 01

```bash
# Navigate to the lab
cd labs/lab-01-hello-mcp

# Read the instructions
cat README.md

# Start with the starter code
cd starter
npm install

# Follow the lab instructions...

# When you're done, check your work against the solution
cd ../solution
```

### Testing Your Solution

```bash
# In the lab's starter/ directory
npm test

# Or test with MCP Inspector
npx @modelcontextprotocol/inspector node src/index.js
```

---

## Lab Completion Checklist

Track your progress:

- [ ] **Lab 01**: Hello MCP - Build your first MCP server

*More labs coming soon!*

---

## Getting Help

### During Labs

1. **Check the README**: Each lab has detailed step-by-step instructions
2. **Review the solution**: Solutions are provided for reference
3. **Use MCP Inspector**: Debug your server interactively
4. **Check docs/TROUBLESHOOTING_FAQ.md**: Common issues and solutions

### Common Issues

#### "Server won't start"
```bash
# Check for syntax errors
node --check src/index.js

# Look for port conflicts
lsof -ti:3000 | xargs kill -9  # macOS/Linux
```

#### "Tool not appearing in Inspector"
- Ensure tool is registered BEFORE `server.connect()`
- Check tool schema for syntax errors
- Restart MCP Inspector

#### "Dependencies not found"
```bash
# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install
```

---

## Lab Tips

### Best Practices

1. **Read the entire lab README first** - understand the objectives
2. **Start with the starter code** - don't jump to the solution
3. **Test incrementally** - validate each step as you go
4. **Use console.error()** - for debugging (goes to stderr, not MCP)
5. **Check the solution if stuck** - but try on your own first

### Time Management

- **Each lab has an estimated time** - don't rush
- **Skip optional sections** if you're behind schedule
- **Focus on understanding over completion** - quality over speed

### Code Quality

- **Add comments** to explain your thinking
- **Handle errors gracefully** - return useful error messages
- **Validate inputs** - use JSON Schema effectively
- **Keep it simple** - solve the problem, then refactor

---

## Beyond the Labs

### Next Steps After Completing Lab 01

While waiting for additional labs, you can:

1. **Explore WARNERCO Schematica** - Study `src/warnerco/backend/` for a production-grade MCP implementation
2. **Read the MCP specification** - Deepen your understanding of the protocol
3. **Experiment with tools and resources** - Extend your Lab 01 server with additional features
4. **Try the dashboards** - Run WARNERCO Schematica and explore `http://localhost:8000/dash/`
5. **Study the Graph Memory tutorial** - See `docs/tutorials/graph-memory-tutorial.md`

### Resources

- **MCP Specification**: <https://spec.modelcontextprotocol.io/>
- **MCP SDK Docs**: <https://github.com/modelcontextprotocol/typescript-sdk>
- **Example Servers**: <https://github.com/modelcontextprotocol/servers>
- **Community Discord**: <https://discord.gg/modelcontextprotocol>

---

## Contributing to Labs

Found an issue or have an improvement?

1. Note the problem or enhancement idea
2. Test your proposed fix
3. Share as course feedback

---

**Happy Learning!**

*Remember: The goal is not just to complete the labs, but to understand the patterns so you can apply them in real-world scenarios.*
