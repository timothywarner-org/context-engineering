# MCP in Practice - Hands-On Labs

These progressive labs will take you from building your first MCP server to deploying production-ready AI memory systems.

## Lab Structure

Each lab includes:
- 📝 **README.md** - Lab objectives and instructions
- 🏗️ **starter/** - Starting code template
- ✅ **solution/** - Reference solution
- 🧪 **tests/** - Validation scripts (where applicable)

## Learning Path

### Beginner Track

#### Lab 01: Hello MCP (30 minutes)
**Objective**: Create your first MCP server with a single tool

**What you'll learn**:
- MCP server basics and structure
- Tool registration and schema definition
- stdio transport communication
- Testing with MCP Inspector

**Start**: [lab-01-hello-mcp/](./lab-01-hello-mcp/)

---

#### Lab 02: Tool Calling Patterns (45 minutes)
**Objective**: Build a multi-tool MCP server with parameter validation

**What you'll learn**:
- Multiple tool registration
- Input schema validation with JSON Schema
- Error handling in tool handlers
- Returning structured data

**Prerequisites**: Lab 01

**Start**: [lab-02-tool-calling/](./lab-02-tool-calling/)

---

#### Lab 03: Resources and Context (45 minutes)
**Objective**: Add MCP resources to expose dynamic data

**What you'll learn**:
- Resource registration and URI schemes
- Dynamic resource generation
- Combining tools and resources
- Resource templating

**Prerequisites**: Lab 02

**Start**: [lab-03-resources/](./lab-03-resources/)

---

### Intermediate Track

#### Lab 04: Memory Patterns (60 minutes)
**Objective**: Implement episodic and semantic memory storage

**What you'll learn**:
- Memory architecture patterns
- Persistent storage with JSON files
- Memory retrieval and search
- Context window optimization

**Prerequisites**: Lab 03

**Start**: [lab-04-memory-patterns/](./lab-04-memory-patterns/)

---

#### Lab 05: Production Deployment (60 minutes)
**Objective**: Containerize and deploy your MCP server to Azure

**What you'll learn**:
- Docker containerization
- Azure Container Apps deployment
- Environment configuration
- Health checks and monitoring

**Prerequisites**: Lab 04, Azure account

**Start**: [lab-05-production-deployment/](./lab-05-production-deployment/)

---

### Advanced Track

#### Lab 06: Advanced Patterns (90 minutes)
**Objective**: Implement vector search and multi-agent orchestration

**What you'll learn**:
- Vector database integration
- Semantic search with embeddings
- Multi-agent coordination
- MCP sampling (AI completions within context)

**Prerequisites**: Lab 05

**Start**: [lab-06-advanced-patterns/](./lab-06-advanced-patterns/)

---

## Quick Start

### Setup All Labs

```bash
# From the repository root
cd labs

# Install dependencies for all labs
for dir in lab-*/; do
  if [ -f "$dir/starter/package.json" ]; then
    echo "Installing dependencies for $dir..."
    (cd "$dir/starter" && npm install)
  fi
done
```

### Running a Lab

```bash
# Navigate to the lab
cd lab-01-hello-mcp

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

Most labs include validation tests:

```bash
# In the lab's starter/ directory
npm test

# Or run the validation script
node test-solution.js
```

---

## Lab Completion Checklist

Track your progress:

- [ ] **Lab 01**: Hello MCP - Build your first MCP server
- [ ] **Lab 02**: Tool Calling - Multi-tool server with validation
- [ ] **Lab 03**: Resources - Dynamic data exposure
- [ ] **Lab 04**: Memory Patterns - Persistent AI memory
- [ ] **Lab 05**: Production Deployment - Azure Container Apps
- [ ] **Lab 06**: Advanced Patterns - Vector search & orchestration

---

## Getting Help

### During Labs

1. **Check the README**: Each lab has detailed step-by-step instructions
2. **Review the solution**: Solutions are provided for reference
3. **Use MCP Inspector**: Debug your server interactively
4. **Check TROUBLESHOOTING_FAQ.md**: Common issues and solutions

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

### Next Steps After Completing All Labs

1. **Combine patterns** - build a server with multiple advanced features
2. **Explore integrations** - connect to real databases or APIs
3. **Deploy to production** - use the patterns in real projects
4. **Share your work** - contribute examples to the community

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

**Happy Learning!** 🚀

*Remember: The goal is not just to complete the labs, but to understand the patterns so you can apply them in real-world scenarios.*
