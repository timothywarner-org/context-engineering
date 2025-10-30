# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This repository contains training materials and code examples for "MCP in Practice: Engineering AI Memory from Prompt to Persistence" - a 4-hour live online course teaching how to deploy production MCP (Model Context Protocol) servers that enable AI agents to access tools, APIs, and databases with persistent memory.

## MCP (Model Context Protocol) Resources

### Official Specification & Documentation

- **MCP Specification**: <https://spec.modelcontextprotocol.io/>
- **MCP Documentation**: <https://modelcontextprotocol.io/docs>
- **Protocol Overview**: <https://modelcontextprotocol.io/docs/concepts/overview>
- **Architecture Guide**: <https://modelcontextprotocol.io/docs/concepts/architecture>

### Official SDKs

- **TypeScript/JavaScript SDK**: <https://github.com/modelcontextprotocol/typescript-sdk>
  - npm: `@modelcontextprotocol/sdk`
  - Full async/await support with TypeScript types
- **Python SDK**: <https://github.com/modelcontextprotocol/python-sdk>
  - pip: `mcp-sdk`
  - Async Python implementation with type hints
- **MCP Inspector**: <https://github.com/modelcontextprotocol/inspector>
  - Browser-based debugging tool for MCP servers

### MCP Core Concepts

1. **Tools**: Functions that AI can discover and invoke (database queries, API calls, file operations)
2. **Resources**: Data sources AI can access (files, URLs, dynamic content)
3. **Prompts**: Reusable prompt templates with variables
4. **Sampling**: LLM completion requests within MCP context

## Context Engineering Principles

### Context Window Optimization

- **Token budgeting**: Allocate context space strategically between system prompts, conversation history, and retrieved data
- **Dynamic pruning**: Remove redundant information while preserving semantic coherence
- **Hierarchical summarization**: Compress older context into increasingly abstract summaries
- **Relevance scoring**: Use embedding similarity to prioritize context inclusion

### Memory Architecture Patterns

1. **Episodic Memory**: Sequential conversation storage with temporal indexing
2. **Semantic Memory**: Vector-indexed knowledge base for similarity retrieval
3. **Working Memory**: Active context for current task execution
4. **Procedural Memory**: Cached tool usage patterns and successful workflows

### Context Persistence Strategies

```javascript
// Example: Implementing context layers with MCP
const contextLayers = {
  immediate: { maxTokens: 4000, ttl: '5m' },      // Current conversation
  recent: { maxTokens: 2000, ttl: '1h' },         // Recent interactions
  background: { maxTokens: 1000, ttl: '24h' },    // Historical context
  persistent: { maxTokens: 500, ttl: 'infinite' }  // Core memories
};
```

## Prompt Engineering for MCP

### MCP-Aware Prompt Design

1. **Tool Discovery Prompts**: Help AI understand available capabilities

   ```
   You have access to the following tools via MCP:
   - database_query: Execute SQL queries on the user's database
   - api_call: Make HTTP requests to external APIs
   - file_read: Read contents of local files
   
   When the user asks for data, determine which tool(s) to use.
   ```

2. **Stateful Conversation Prompts**: Maintain context across tool calls

   ```
   Previous context from MCP memory:
   {retrieved_context}
   
   Current user request: {user_input}
   
   Use the context to provide a coherent response that builds on prior interactions.
   ```

3. **Multi-Agent Coordination**: Orchestrate between different MCP servers

   ```
   You are coordinating between multiple MCP servers:
   - Memory Server: Stores and retrieves conversation context
   - Tool Server: Executes external operations
   - Analytics Server: Tracks usage patterns
   
   Route requests appropriately and maintain state consistency.
   ```

### Prompt Chaining with MCP

```javascript
// Example: Progressive enhancement pattern
const promptChain = [
  { role: 'analyzer', prompt: 'Understand user intent and required tools' },
  { role: 'planner', prompt: 'Create execution plan using available MCP tools' },
  { role: 'executor', prompt: 'Execute plan and handle tool responses' },
  { role: 'synthesizer', prompt: 'Combine results into coherent response' }
];
```

### Dynamic Prompt Construction

- **Variable injection**: Use MCP resources to populate prompt templates
- **Conditional sections**: Include/exclude prompt parts based on available tools
- **Feedback loops**: Adjust prompts based on tool execution results

## Development Commands

### Setup

```bash
# Install dependencies (when package.json exists)
npm install

# Install MCP SDK
npm install @modelcontextprotocol/sdk

# Test Docker setup (optional)
docker run hello-world
```

### Development

```bash
# Run MCP server (once implemented)
npm start

# Run specific MCP server examples
node examples/[server-name]/index.js

# Test MCP server with Inspector
# Open MCP Inspector in browser and connect to local server
```

## Architecture

### Expected Project Structure

```
context-engineering/
├── examples/              # MCP server implementation examples
│   ├── filesystem/       # File system access server
│   ├── database/         # Database query server
│   ├── api/             # API integration server
│   └── memory/          # Memory storage patterns
├── src/                  # Core MCP utilities and patterns
│   ├── servers/         # Base server implementations
│   ├── memory/          # Memory persistence patterns
│   └── utils/           # Shared utilities
├── labs/                # Hands-on lab exercises
└── docker/              # Docker configurations for deployment
```

### Key Technologies

- **MCP (Model Context Protocol)**: Core protocol for AI tool-calling and memory
- **Node.js 20+**: Primary runtime for MCP servers
- **Docker**: For containerized deployments
- **Vector Databases**: For semantic memory storage
- **AI Platforms**: Integration with ChatGPT, Claude, and GitHub Copilot

## MCP Server Development Patterns

When implementing MCP servers in this repository:

1. **Server Structure**: Each MCP server should expose tools, resources, and prompts
2. **Memory Patterns**: Implement episodic, semantic, and working memory architectures
3. **Tool Discovery**: Ensure servers support automatic capability discovery
4. **State Management**: Focus on persistent context across sessions

## Testing Approach

- Use MCP Inspector for manual testing of server endpoints
- Test with actual AI platforms (ChatGPT, Claude) for integration verification
- Validate memory persistence across sessions
- Test multi-agent orchestration scenarios

## Security Considerations

- Never expose API keys or credentials in code
- Implement proper authentication for production MCP servers
- Use environment variables for sensitive configuration
- Follow context isolation patterns for multi-tenant scenarios

## Advanced MCP Implementation Patterns

### Server Connection Strategies

1. **Direct stdio**: Fast, secure, ideal for local tools
2. **HTTP/SSE**: Network-accessible, supports remote deployment
3. **WebSocket**: Bidirectional, real-time updates
4. **Named pipes**: OS-level IPC for high-performance scenarios

### State Management in MCP

```typescript
// Example: Implementing stateful MCP server
class StatefulMCPServer {
  private conversationState: Map<string, ConversationContext>;
  private vectorStore: VectorDatabase;
  
  async handleToolCall(name: string, args: any, conversationId: string) {
    // Retrieve relevant context
    const context = await this.retrieveContext(conversationId);
    
    // Execute tool with context awareness
    const result = await this.executeTool(name, args, context);
    
    // Update conversation state
    await this.updateContext(conversationId, result);
    
    return result;
  }
}
```

### MCP Security Best Practices

1. **Authentication**: Implement bearer tokens or API keys for server access
2. **Authorization**: Use capability-based security for tool permissions
3. **Input validation**: Sanitize all tool arguments against injection attacks
4. **Rate limiting**: Prevent resource exhaustion from excessive calls
5. **Audit logging**: Track all tool invocations for compliance

### Performance Optimization

- **Connection pooling**: Reuse MCP connections across requests
- **Response streaming**: Use SSE for large responses
- **Caching strategies**: Cache tool results based on input parameters
- **Batch operations**: Group related tool calls for efficiency

## Context Engineering Advanced Topics

### Semantic Context Compression

```javascript
// Example: Intelligent context compression
async function compressContext(messages, targetTokens) {
  // 1. Extract key entities and relationships
  const entities = await extractEntities(messages);
  
  // 2. Generate semantic summary
  const summary = await generateSummary(messages, entities);
  
  // 3. Identify critical information
  const critical = await identifyCriticalInfo(messages);
  
  // 4. Reconstruct compressed context
  return {
    summary,
    entities,
    critical,
    recentMessages: messages.slice(-3)
  };
}
```

### Multi-Modal Context Handling

- **Text**: Traditional conversation and document context
- **Code**: Syntax-aware context for programming tasks
- **Structured data**: JSON, CSV, database schemas
- **Embeddings**: Vector representations for semantic search

### Context Conflict Resolution

1. **Temporal priority**: Recent context overrides older information
2. **Source authority**: Rank context sources by reliability
3. **Semantic coherence**: Ensure context consistency
4. **User preference**: Apply user-defined context rules

## Production Deployment Considerations

### Scaling MCP Servers

- **Horizontal scaling**: Deploy multiple server instances with load balancing
- **Vertical scaling**: Optimize single-instance performance
- **Edge deployment**: Run MCP servers close to users
- **Serverless**: Use functions-as-a-service for stateless tools

### Monitoring and Observability

```javascript
// Example: OpenTelemetry integration
const { trace } = require('@opentelemetry/api');

async function instrumentedToolCall(name, args) {
  const span = trace.getTracer('mcp-server').startSpan(`tool.${name}`);
  
  try {
    span.setAttributes({
      'tool.name': name,
      'tool.args': JSON.stringify(args),
      'conversation.id': getCurrentConversationId()
    });
    
    const result = await executeTool(name, args);
    span.setStatus({ code: SpanStatusCode.OK });
    return result;
  } catch (error) {
    span.recordException(error);
    span.setStatus({ code: SpanStatusCode.ERROR });
    throw error;
  } finally {
    span.end();
  }
}
```

### Integration Patterns

1. **AI Platform Integration**
   - Claude Desktop: Native MCP support
   - ChatGPT: Via custom GPTs and actions
   - Copilot: Through extensions
   - LangChain: MCP tool wrapper

2. **Enterprise Systems**
   - API gateways for MCP exposure
   - Service mesh integration
   - Identity provider connections
   - Data governance compliance

## Course-Specific Notes

This repository serves as both teaching material and reference implementation. Code should be:

- Clear and well-commented for educational purposes
- Production-ready to demonstrate real-world patterns
- Modular to allow students to experiment with individual components
- Progressive in complexity from basic to advanced examples

### Learning Path

1. **Basic**: Simple MCP server with single tool
2. **Intermediate**: Stateful server with memory persistence
3. **Advanced**: Multi-agent orchestration with vector stores
4. **Expert**: Production deployment with full observability

## Cutting-Edge Prompt Engineering Techniques

### Chain-of-Thought (CoT) with MCP Tools

```javascript
// Example: Structured reasoning with tool access
const cotPrompt = `
Let's approach this step-by-step:

1. First, I'll check what tools are available via MCP
2. Then, I'll analyze which tools are needed for this task
3. I'll create a plan for using these tools in sequence
4. Finally, I'll execute the plan and synthesize the results

Available MCP tools: {available_tools}
User request: {user_request}

My reasoning:
`;
```

### Few-Shot Learning with MCP Examples

```javascript
// Example: Teaching AI how to use MCP tools effectively
const fewShotExamples = [
  {
    user: "What's the weather in Tokyo?",
    assistant_thought: "I need to use the weather_api tool",
    tool_call: { name: "weather_api", args: { city: "Tokyo" } },
    result: "72°F, partly cloudy"
  },
  {
    user: "Save that information for later",
    assistant_thought: "I should store this in memory using the memory_store tool",
    tool_call: { name: "memory_store", args: { key: "tokyo_weather", value: "72°F, partly cloudy" } },
    result: "Stored successfully"
  }
];
```

### Self-Reflection and Error Correction

```javascript
// Example: AI self-evaluation pattern
const reflectionPrompt = `
After executing the MCP tool, evaluate:
1. Did the tool return the expected type of result?
2. Does the result fully answer the user's question?
3. Are there follow-up tools that should be called?
4. Should I retry with different parameters?

Tool result: {tool_result}
Expected outcome: {expected_outcome}
`;
```

### Adaptive Prompting Based on Tool Availability

```javascript
// Example: Dynamic prompt adjustment
async function generateAdaptivePrompt(availableTools, userIntent) {
  const toolCategories = categorizeTools(availableTools);
  
  let prompt = "You are an AI assistant with access to the following capabilities:\n";
  
  if (toolCategories.includes('database')) {
    prompt += "- Query and analyze structured data\n";
  }
  if (toolCategories.includes('filesystem')) {
    prompt += "- Read and write files on the local system\n";
  }
  if (toolCategories.includes('api')) {
    prompt += "- Access external services and APIs\n";
  }
  
  prompt += "\nAdapt your response strategy based on available tools.";
  return prompt;
}
```

## Future Directions and Research Areas

### Emerging MCP Capabilities

1. **Multi-modal tools**: Image generation, audio processing, video analysis
2. **Recursive tool calling**: Tools that can invoke other tools
3. **Conditional execution**: Tool calls based on previous results
4. **Parallel execution**: Concurrent tool invocations for performance

### Advanced Context Engineering Research

- **Neuromorphic memory**: Brain-inspired storage patterns
- **Quantum context**: Superposition of multiple context states
- **Federated context**: Distributed memory across multiple servers
- **Causal context graphs**: Understanding cause-effect relationships

### Next-Generation Prompt Techniques

1. **Constitutional prompting**: Self-governing AI behavior through principles
2. **Recursive prompt optimization**: Prompts that improve themselves
3. **Emergent tool discovery**: AI learning new tool combinations
4. **Semantic prompt compilation**: High-level intents to low-level operations

### Integration with Emerging AI Standards

- **OpenAI Assistants API**: MCP adapter patterns
- **Google Vertex AI**: MCP compatibility layer
- **AWS Bedrock**: MCP deployment templates
- **Azure AI Studio**: MCP orchestration patterns

## Resources for Continued Learning

### MCP Community

- **Discord**: <https://discord.gg/modelcontextprotocol>
- **GitHub Discussions**: <https://github.com/modelcontextprotocol/discussions>
- **Stack Overflow**: Tag `model-context-protocol`

### Related Specifications

- **JSON-RPC 2.0**: <https://www.jsonrpc.org/specification> (MCP transport layer)
- **OpenAPI/Swagger**: For documenting MCP tool interfaces
- **AsyncAPI**: For event-driven MCP patterns
- **GraphQL**: For complex data querying via MCP

### Academic Papers and Research

- "Augmenting Language Models with Tools" (Schick et al., 2023)
- "Constitutional AI: Harmlessness from AI Feedback" (Anthropic, 2022)
- "Toolformer: Language Models Can Teach Themselves to Use Tools" (Meta, 2023)
- "ReAct: Synergizing Reasoning and Acting in Language Models" (Yao et al., 2023)
