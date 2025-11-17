# Filesystem MCP Server Example

A complete MCP server that provides safe filesystem access tools for AI agents.

## Overview

This example demonstrates:
- ✅ Filesystem operations (read, write, list, search)
- ✅ Path validation and sandboxing
- ✅ Error handling for file operations
- ✅ Resource exposure for directory listings
- ✅ Security best practices

## Features

### Tools

1. **`read_file`** - Read file contents
   - Parameters: `path` (string)
   - Returns: File contents as text
   - Security: Validates path is within allowed directory

2. **`write_file`** - Write or update file
   - Parameters: `path` (string), `content` (string)
   - Returns: Success confirmation
   - Security: Creates directories if needed, validates path

3. **`list_directory`** - List directory contents
   - Parameters: `path` (string, optional, defaults to workspace root)
   - Returns: Array of files and directories with metadata
   - Includes: Name, type (file/directory), size, modified time

4. **`search_files`** - Search for files by name pattern
   - Parameters: `pattern` (string), `directory` (string, optional)
   - Returns: Array of matching file paths
   - Uses: Glob pattern matching

5. **`delete_file`** - Delete a file
   - Parameters: `path` (string)
   - Returns: Success confirmation
   - Security: Requires confirmation, validates path

### Resources

1. **`fs://tree`** - Directory tree visualization
   - URI: `fs://tree`
   - Returns: Formatted directory tree of workspace
   - Useful for giving AI context about project structure

2. **`fs://stats`** - Filesystem statistics
   - URI: `fs://stats`
   - Returns: File count, total size, recent changes
   - Helps AI understand workspace scope

## Security Features

### Path Sandboxing

All file operations are restricted to the configured workspace directory:

```javascript
function validatePath(requestedPath) {
  const resolved = path.resolve(workspaceRoot, requestedPath);
  if (!resolved.startsWith(workspaceRoot)) {
    throw new Error('Access denied: Path outside workspace');
  }
  return resolved;
}
```

### Safe Operations

- **Read**: Checks file exists and is readable
- **Write**: Creates parent directories, handles existing files
- **Delete**: Validates file exists before deletion
- **List**: Handles permission errors gracefully

## Installation

```bash
cd examples/filesystem-mcp
npm install
```

## Configuration

Create `.env` file:

```bash
# Workspace root - all file operations are restricted to this directory
WORKSPACE_ROOT=/path/to/your/workspace

# Optional: Enable verbose logging
DEBUG=true
```

## Usage

### Running the Server

```bash
npm start
```

### Testing with MCP Inspector

```bash
npx @modelcontextprotocol/inspector
```

Connect using:
- **Command**: `node`
- **Args**: `/full/path/to/examples/filesystem-mcp/src/index.js`

### Claude Desktop Integration

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "node",
      "args": ["/full/path/to/examples/filesystem-mcp/src/index.js"],
      "env": {
        "WORKSPACE_ROOT": "/path/to/your/workspace"
      }
    }
  }
}
```

## Example Interactions

### Read a File

```
User: "What's in the README.md file?"
AI: [Calls read_file with path: "README.md"]
Tool: Returns file contents
AI: "Here's what's in README.md: ..."
```

### Create a File

```
User: "Create a new file called notes.txt with 'Hello World'"
AI: [Calls write_file with path: "notes.txt", content: "Hello World"]
Tool: Returns success message
AI: "I've created notes.txt with your content"
```

### Search Files

```
User: "Find all JavaScript files in the src directory"
AI: [Calls search_files with pattern: "src/**/*.js"]
Tool: Returns array of matching files
AI: "I found 5 JavaScript files: ..."
```

### List Directory

```
User: "What files are in the current directory?"
AI: [Calls list_directory]
Tool: Returns directory listing
AI: "The directory contains: ..."
```

## Use Cases

1. **Code Analysis**: AI can read source files to understand codebases
2. **File Generation**: AI can create files (configs, documentation, code)
3. **Project Navigation**: AI can explore directory structure
4. **File Management**: AI can organize and manage files
5. **Search & Discovery**: AI can find files matching patterns

## Architecture

```
filesystem-mcp/
├── src/
│   ├── index.js          # Main server implementation
│   ├── validator.js      # Path validation and security
│   └── operations.js     # Filesystem operation wrappers
├── package.json
├── .env.example
└── README.md
```

## Security Considerations

### ⚠️ Important Security Notes

1. **Workspace Restriction**: Always set `WORKSPACE_ROOT` to limit access
2. **No System Access**: Never allow access to system directories
3. **Path Traversal**: Validates against `../` attacks
4. **File Size Limits**: Consider adding max file size limits
5. **Rate Limiting**: Consider adding rate limits for writes

### Production Recommendations

For production deployments:

```javascript
// Add file size limits
const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB

// Add allowed extensions
const ALLOWED_EXTENSIONS = ['.txt', '.md', '.json', '.js', '.ts'];

// Add rate limiting
const rateLimit = new Map(); // Track operations per minute
```

## Error Handling

The server handles common errors gracefully:

- **File not found**: Returns clear error message
- **Permission denied**: Indicates access issue
- **Path outside workspace**: Security error
- **Disk full**: Write operation error
- **Invalid path**: Validation error

## Testing

Run the test suite:

```bash
npm test
```

Tests cover:
- ✅ Path validation
- ✅ Read operations
- ✅ Write operations
- ✅ Delete operations
- ✅ Directory listing
- ✅ File search
- ✅ Error handling
- ✅ Security boundaries

## Performance

- **Async operations**: All file I/O is non-blocking
- **Streaming**: Large files use streaming where applicable
- **Caching**: Directory listings cached briefly
- **Efficient search**: Uses optimized glob matching

## Extending

### Add New Tools

```javascript
server.tool(
  'create_directory',
  'Creates a new directory',
  {
    type: 'object',
    properties: {
      path: { type: 'string', description: 'Directory path' }
    },
    required: ['path']
  },
  async ({ path }) => {
    const validatedPath = validatePath(path);
    await fs.promises.mkdir(validatedPath, { recursive: true });
    return {
      content: [{
        type: 'text',
        text: `Directory created: ${path}`
      }]
    };
  }
);
```

### Add File Watching

```javascript
import { watch } from 'fs';

const watcher = watch(workspaceRoot, { recursive: true }, (eventType, filename) => {
  console.error(`File ${eventType}: ${filename}`);
  // Emit notification to connected clients
});
```

## Limitations

- **Binary files**: Currently text-only (add base64 encoding for binary)
- **Large files**: No streaming for very large files (add pagination)
- **Concurrent writes**: No locking mechanism (add file locking if needed)
- **Cross-platform**: Path handling differs between OS (normalize paths)

## Contributing

Improvements welcome:
- Add binary file support (base64 encoding)
- Implement file watching/notifications
- Add file locking for concurrent access
- Support archive operations (zip/unzip)
- Add diff/patch operations

## License

MIT

## Related Examples

- **database-mcp**: Database query operations
- **api-mcp**: External API integration
- **coretext-mcp**: Memory and context management

---

**Learn More**: See the implementation in `src/index.js` for detailed comments and patterns.
