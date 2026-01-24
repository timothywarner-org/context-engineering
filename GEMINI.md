# Gemini Code Assistant Guide

This document provides guidance for using Gemini Code Assistant with the `context-engineering` repository. This repository is the central hub for the O'Reilly Live Learning course, "Context Engineering with MCP".

## Project Overview

This repository contains all the course materials, including slides, labs, and the flagship teaching application for the "Context Engineering with Model Context Protocol (MCP)" course. It's designed to be a hands-on learning environment for understanding and implementing persistent memory and tool-calling capabilities for AI models.

The primary technologies used are:

- **Python**: FastAPI, FastMCP, LangGraph, Pydantic
- **Node.js**: MCP TypeScript SDK for Lab 01
- **Model Context Protocol (MCP)**: The core protocol for communication between AI models and external tools/memory
- **Vector Databases**: ChromaDB (local), Azure AI Search (production)
- **Graph Database**: SQLite + NetworkX for knowledge graph

## Course Structure

The course is divided into four 50-minute segments:

1. **Understanding Context**: Covers the fundamentals of AI memory and context windows
2. **MCP Server Development**: Hands-on labs building MCP servers with FastMCP
3. **Semantic Memory Stores**: JSON, ChromaDB, Azure AI Search, Graph Memory implementations
4. **MCP in Production**: Claude Desktop, Claude Code, VS Code, GitHub Copilot integration

## Key Projects and Learning Resources

- `src/warnerco/backend/` - **WARNERCO Schematica**: The flagship FastAPI + FastMCP + LangGraph teaching application demonstrating hybrid RAG with vector and graph memory
- `labs/lab-01-hello-mcp/` - Hands-on lab for students to build their first MCP server (Node.js)
- `docs/` - Student-facing documentation, including setup guides, tutorials, and API reference
- `instructor/` - Course plan, demo scripts, and teaching materials

## Building and Running

### WARNERCO Schematica (Primary Teaching App)

```bash
cd src/warnerco/backend
uv sync                                    # Install dependencies
uv run uvicorn app.main:app --reload       # Start FastAPI server (http://localhost:8000)
uv run warnerco-mcp                        # MCP stdio server (for Claude Desktop)
```

**Memory Backends** (set `MEMORY_BACKEND` in `.env`):
- `json` - Fastest startup, keyword search (default)
- `chroma` - Local semantic search (recommended for dev)
- `azure_search` - Enterprise deployment

### Lab 01 - Hello MCP (Beginner Entry Point)

```bash
cd labs/lab-01-hello-mcp/starter
npm install
npm start
npx @modelcontextprotocol/inspector node src/index.js  # Test with Inspector
```

## Development Conventions

- **Coding Style**:
  - JavaScript/TypeScript: 2-space indentation, ES modules
  - Python: 4-space indentation, snake_case filenames
- **Naming Conventions**:
  - Follow existing patterns: `main.py`, `mcp_tools.py`, `flow.py`
  - Documentation files in `UPPER_SNAKE.md` format
- **Logging**: Use `console.error()` for logging in MCP servers, as `stdout` is reserved for the MCP protocol
- **Testing**:
  - WARNERCO Schematica: `uv run pytest` in `src/warnerco/backend`
  - MCP servers: Test with MCP Inspector (`npx @modelcontextprotocol/inspector`)
- **Commits**: Use short, imperative, sentence-case commit messages
- **Security**: Do not commit secrets. Use `.env.example` files as templates

---
*This file provides context for Gemini Code Assistant interactions with this repository.*
