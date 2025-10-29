# Stoic MCP - Local Implementation

Local Node.js MCP server using JSON file storage for Stoic philosophy quotes. This implementation demonstrates the Model Context Protocol (MCP) specification with a complete, production-ready server.

## Features

- ✅ **CRUD Operations**: Full create, read, update, delete support
- 📝 **JSON Storage**: File-based persistence with metadata tracking
- 🤖 **AI Integration**: DeepSeek-powered quote explanations and generation
- ⭐ **Favorites**: Mark quotes that resonate
- 🔍 **Search**: Filter by author, theme, or keywords
- 📝 **Personal Notes**: Add personal reflections to quotes
- 📥 **Bulk Import**: Import quotes from text files with automatic theme detection

## Prerequisites

- Node.js 18+ and npm
- DeepSeek API key from [platform.deepseek.com](https://platform.deepseek.com)

## Quick Start

### 1. Install Dependencies

```bash
cd local
npm install
```

### 2. Configure API Key

The server reads `DEEPSEEK_API_KEY` from your system environment variables. You have two options:

**Option A: System Environment Variable (Recommended for production/teaching)**
- Set `DEEPSEEK_API_KEY` in your system environment variables
- The MCP server will automatically inherit this value
- No secrets in config files

**Option B: Local .env file (Development only)**
- Create a `.env` file in the `local/` directory:
  ```bash
  DEEPSEEK_API_KEY=your_key_here
  ```
- Useful for local development
- **DO NOT** commit `.env` to version control

### 3. Build and Run

```bash
npm run build
npm start
```

### 4. Configure in Claude Desktop

Add to your Claude Desktop config:
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "stoic-mcp": {
      "command": "node",
      "args": [
        "C:\\github\\stoic-mcp\\local\\dist\\index.js"
      ]
    }
  }
}
```

**Important Notes:**
- Update the path to match your installation location
- Use double backslashes on Windows (e.g., `C:\\github\\...`)
- **API Key Security**: The server automatically reads `DEEPSEEK_API_KEY` from your system environment variables - do NOT add it to this config file
- The MCP server inherits all environment variables from your system
- Restart Claude Desktop after changing the config file

## Available Tools

### `get_random_quote`
Get a random Stoic quote for inspiration.

**Example:** "I need some motivation"

### `search_quotes`
Search by author, theme, or keyword.

**Parameters:**
- `query` (optional): Keyword search
- `author` (optional): Filter by author
- `theme` (optional): Filter by theme

**Example:** "Find quotes about courage by Marcus Aurelius"

### `add_quote`
Add a new quote to the collection.

**Parameters:**
- `text`: The quote text
- `author`: Quote author
- `source`: Source book/work
- `theme`: Main theme

### `get_quote_explanation`
Get AI-powered practical explanation.

**Parameters:**
- `quote_id`: ID of the quote

**Example:** "Explain quote 5 in terms of handling production incidents"

### `toggle_favorite`
Mark or unmark as favorite.

**Parameters:**
- `quote_id`: ID of the quote

### `get_favorites`
Retrieve all favorite quotes.

### `update_quote_notes`
Add personal notes to a quote.

**Parameters:**
- `quote_id`: ID of the quote
- `notes`: Your reflection

### `delete_quote`
Remove a quote from the collection.

**Parameters:**
- `quote_id`: ID of the quote

### `generate_quote`
Use AI to generate new Stoic-style quote.

**Parameters:**
- `theme`: Theme for generation (e.g., "debugging", "code review")

## Data Structure

Quotes are stored in `quotes.json` with metadata tracking:

```json
{
  "metadata": {
    "lastId": 25,
    "version": "1.0.0",
    "lastModified": "2025-10-23T19:58:03.584Z"
  },
  "quotes": [
    {
      "id": 1,
      "text": "You have power over your mind - not outside events.",
      "author": "Marcus Aurelius",
      "source": "Meditations",
      "theme": "control",
      "favorite": false,
      "notes": null,
      "createdAt": "2025-10-23T19:44:31.298Z",
      "addedBy": "seed"
    }
  ]
}
```

### Schema Details

**Metadata:**
- `lastId`: Auto-incrementing ID counter for new quotes
- `version`: Schema version (currently "1.0.0")
- `lastModified`: ISO timestamp of last modification

**Quote Properties:**
- `id`: Numeric ID (auto-generated from metadata.lastId)
- `text`: Quote text
- `author`: Author name
- `source`: Source book or work
- `theme`: Theme category
- `favorite`: Boolean favorite flag
- `notes`: Personal notes (string | null)
- `createdAt`: ISO timestamp when quote was added
- `addedBy`: Source ("seed", "user", "manual")

## Bulk Import

Import multiple quotes from a text file:

```bash
npm run import <filename.txt>
```

**Format:** Place your import file in `local/quotes-source/` directory:

```
"Quote text here" - Author Name, Source Book
"Another quote" - Author Name, Source Book
```

**Features:**
- Automatic theme detection from 18 predefined categories
- Atomic file operations (all or nothing)
- Metadata auto-updates (lastId and lastModified)

See `local/IMPORT_GUIDE.md` for complete documentation.

## Development

```bash
# Watch mode for development
npm run watch

# Development mode (build + run)
npm run dev

# Clean build artifacts
npm run clean
```

## Architecture

This implementation follows the official MCP specification:

**Core Components:**
- `src/index.ts` - MCP server entry point with tool registration
- `src/storage.ts` - File-based storage layer with CRUD operations
- `src/deepseek.ts` - AI integration for explanations and generation
- `src/types.ts` - TypeScript interfaces for type safety

**Communication:**
- Uses `StdioServerTransport` for Claude Desktop integration
- Handles `ListToolsRequestSchema` for tool discovery
- Handles `CallToolRequestSchema` for tool execution

**9 Available Tools:** get_random_quote, search_quotes, add_quote, get_quote_explanation, toggle_favorite, get_favorites, update_quote_notes, delete_quote, generate_quote

## Troubleshooting

**Issue:** "DEEPSEEK_API_KEY not set" warning

**Solution:** Ensure your `.env` file exists and contains your API key, or set it as a system environment variable.

**Issue:** Quotes not persisting

**Solution:** Check file permissions on `quotes.json` and ensure the path is correct.

**Issue:** Server not appearing in Claude Desktop

**Solution:**
- Verify the path in `claude_desktop_config.json` points to `dist/index.js`
- Ensure you've run `npm run build` first
- Restart Claude Desktop after config changes
- Check Claude Desktop logs for error messages

## Next Steps

Ready to scale to Azure? Check out the [Azure implementation](../azure/README.md) using Cosmos DB.

## License

MIT - See root LICENSE file
