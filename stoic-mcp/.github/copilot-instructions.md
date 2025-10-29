# Copilot Instructions for Stoic MCP

This guide enables AI coding agents to work productively in the Stoic MCP codebase. It covers architecture, workflows, conventions, and integration points specific to this project.

## Big Picture Architecture

- **Monorepo Structure:**
  - `local/`: Node.js MCP server using JSON file storage. Production-ready, implements full Model Context Protocol (MCP) spec.
  - `azure/`: Planned Azure implementation (Cosmos DB, serverless hosting).
- **Core Components (Local):**
  - `src/index.ts`: MCP server entry, tool registration, StdioServerTransport for Claude Desktop.
  - `src/storage.ts`: File-based CRUD storage for quotes.
  - `src/deepseek.ts`: DeepSeek API integration for AI explanations/generation.
  - `src/types.ts`: TypeScript interfaces for schema/type safety.
- **Data Flow:**
  - Quotes stored in `local/quotes.json` with metadata and auto-incrementing IDs.
  - Bulk import via text files in `local/quotes-source/` (see `IMPORT_GUIDE.md`).
  - Tool requests handled via MCP protocol (StdioServerTransport).

## Developer Workflows

- **Install & Run (Local):**
  - `cd local && npm install`
  - Create `.env` with `DEEPSEEK_API_KEY`
  - `npm run build && npm start` (production)
  - `npm run dev` (development)
  - `npm run watch` (auto-rebuild)
  - Bulk import: `npm run import <filename.txt>`
- **Claude Desktop Integration:**
  - Register server in `claude_desktop_config.json` (see local README for config example).
  - Use double backslashes for Windows paths.
- **Troubleshooting:**
  - API key issues: check `.env` or system env vars.
  - File permissions: ensure `quotes.json` is writable.
  - Server visibility: verify build, config path, restart Claude Desktop.

## Project-Specific Conventions

- **Quote Schema:**
  - Metadata: `lastId`, `version`, `lastModified`.
  - Quote: `id`, `text`, `author`, `source`, `theme`, `favorite`, `notes`, `createdAt`, `addedBy`.
- **Bulk Import Format:**
  - Each line: `"Quote text" - Author, Source`
  - Comments: lines starting with `#`
  - Theme auto-detected from text
- **Tool Naming:**
  - 9 tools: get_random_quote, search_quotes, add_quote, get_quote_explanation, toggle_favorite, get_favorites, update_quote_notes, delete_quote, generate_quote

## Integration Points

- **DeepSeek API:**
  - Used for AI-powered explanations and quote generation.
  - Requires API key in `.env` or system environment.
- **Claude Desktop:**
  - Communicates via StdioServerTransport, MCP protocol.

## Key Files & Directories

- `local/README.md`: Local implementation details, developer workflow, tool documentation.
- `local/IMPORT_GUIDE.md`: Bulk import instructions and format.
- `local/quotes.json`: Main data store for quotes.
- `src/`: Core server, storage, and AI integration code.
- `local/quotes-source/`: Bulk import source files.

---

For Azure implementation, see `azure/README.md` (currently a stub).

_Update this file as project conventions evolve._
