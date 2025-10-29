# Stoic MCP

**Model Context Protocol server delivering Stoic philosophy quotes with AI-powered explanations via DeepSeek API.**

This monorepo demonstrates the architectural progression from local JSON storage to Azure Cosmos DB, perfect for live training sessions on MCP server development.

## Project Structure

```
stoic-mcp/
├── local/          # Local implementation with JSON file storage
└── azure/          # Azure implementation with Cosmos DB
```

## Features

- **CRUD Operations**: Create, read, update, and delete Stoic quotes
- **Random Quote Delivery**: Get inspiration when you need it
- **AI-Powered Explanations**: DeepSeek integration for deeper understanding
- **Search & Filter**: Find quotes by author, theme, or keywords
- **Favorites Management**: Track quotes that resonate with you

## Why Stoicism for Developers?

Developer wellness matters. Stoic philosophy offers practical wisdom for handling:
- High-pressure deployments
- Difficult technical decisions  
- Imposter syndrome and self-doubt
- Work-life balance challenges

## Getting Started

Choose your implementation:

- **[Local Setup](./local/README.md)** - Start here for learning MCP basics
- **[Azure Setup](./azure/README.md)** - Deploy to production with Cosmos DB

## Learning Objectives

This project teaches:
- MCP server architecture per Anthropic specification
- Tool implementation patterns in Node.js/TypeScript
- External API integration (DeepSeek)
- Storage abstraction layers
- Local → Cloud migration strategies

## Prerequisites

- Node.js 18+ and npm
- DeepSeek API key (get one at [platform.deepseek.com](https://platform.deepseek.com))
- For Azure deployment: Azure subscription

## Contributing

This is an educational project built for live training. Feel free to fork and adapt for your own teaching needs.

## License

MIT

---

*Built with ❤️ by Tim Warner*
