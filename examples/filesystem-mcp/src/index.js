#!/usr/bin/env node

/**
 * Filesystem MCP Server
 *
 * Provides safe filesystem access tools for AI agents with path sandboxing.
 *
 * Tools:
 * - read_file: Read file contents
 * - write_file: Write or update file
 * - list_directory: List directory contents with metadata
 * - search_files: Search for files by glob pattern
 * - delete_file: Delete a file safely
 *
 * Resources:
 * - fs://tree: Directory tree visualization
 * - fs://stats: Filesystem statistics
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import fs from 'fs/promises';
import fsSync from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { glob } from 'glob';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Configuration
const WORKSPACE_ROOT = process.env.WORKSPACE_ROOT || process.cwd();
const DEBUG = process.env.DEBUG === 'true';

// Logging helper
function log(message) {
  if (DEBUG) {
    console.error(`[filesystem-mcp] ${message}`);
  }
}

/**
 * Validate and resolve path to ensure it's within workspace
 */
function validatePath(requestedPath) {
  const resolved = path.resolve(WORKSPACE_ROOT, requestedPath);

  // Security check: Ensure path is within workspace
  if (!resolved.startsWith(WORKSPACE_ROOT)) {
    throw new Error(
      `Access denied: Path '${requestedPath}' is outside workspace. ` +
      `Workspace root: ${WORKSPACE_ROOT}`
    );
  }

  return resolved;
}

/**
 * Format file size in human-readable format
 */
function formatFileSize(bytes) {
  const units = ['B', 'KB', 'MB', 'GB'];
  let size = bytes;
  let unitIndex = 0;

  while (size >= 1024 && unitIndex < units.length - 1) {
    size /= 1024;
    unitIndex++;
  }

  return `${size.toFixed(2)} ${units[unitIndex]}`;
}

/**
 * Get directory tree as formatted string
 */
async function getDirectoryTree(dirPath, prefix = '', maxDepth = 3, currentDepth = 0) {
  if (currentDepth >= maxDepth) {
    return `${prefix}[...]\n`;
  }

  let tree = '';
  try {
    const entries = await fs.readdir(dirPath, { withFileTypes: true });
    const sortedEntries = entries.sort((a, b) => {
      // Directories first
      if (a.isDirectory() && !b.isDirectory()) return -1;
      if (!a.isDirectory() && b.isDirectory()) return 1;
      return a.name.localeCompare(b.name);
    });

    for (let i = 0; i < sortedEntries.length; i++) {
      const entry = sortedEntries[i];
      const isLast = i === sortedEntries.length - 1;
      const connector = isLast ? '└── ' : '├── ';
      const newPrefix = prefix + (isLast ? '    ' : '│   ');

      if (entry.name.startsWith('.')) continue; // Skip hidden files

      tree += `${prefix}${connector}${entry.name}`;

      if (entry.isDirectory()) {
        tree += '/\n';
        const subPath = path.join(dirPath, entry.name);
        tree += await getDirectoryTree(subPath, newPrefix, maxDepth, currentDepth + 1);
      } else {
        tree += '\n';
      }
    }
  } catch (error) {
    tree += `${prefix}[Error: ${error.message}]\n`;
  }

  return tree;
}

/**
 * Get filesystem statistics
 */
async function getFilesystemStats(dirPath) {
  let fileCount = 0;
  let dirCount = 0;
  let totalSize = 0;

  async function walk(currentPath) {
    try {
      const entries = await fs.readdir(currentPath, { withFileTypes: true });

      for (const entry of entries) {
        if (entry.name.startsWith('.')) continue;

        const fullPath = path.join(currentPath, entry.name);

        if (entry.isDirectory()) {
          dirCount++;
          await walk(fullPath);
        } else {
          fileCount++;
          try {
            const stats = await fs.stat(fullPath);
            totalSize += stats.size;
          } catch (error) {
            // Skip files we can't stat
          }
        }
      }
    } catch (error) {
      // Skip directories we can't read
    }
  }

  await walk(dirPath);

  return {
    files: fileCount,
    directories: dirCount,
    totalSize: formatFileSize(totalSize),
    totalSizeBytes: totalSize
  };
}

async function main() {
  log(`Starting Filesystem MCP Server`);
  log(`Workspace root: ${WORKSPACE_ROOT}`);

  // Verify workspace exists
  try {
    await fs.access(WORKSPACE_ROOT);
  } catch (error) {
    console.error(`Error: Workspace root does not exist: ${WORKSPACE_ROOT}`);
    process.exit(1);
  }

  // Create server
  const server = new Server(
    {
      name: 'filesystem-mcp',
      version: '1.0.0'
    },
    {
      capabilities: {
        tools: {},
        resources: {}
      }
    }
  );

  // ============================================================================
  // TOOLS
  // ============================================================================

  /**
   * Tool: read_file
   * Read contents of a file
   */
  server.tool(
    'read_file',
    'Read the contents of a file from the workspace',
    {
      type: 'object',
      properties: {
        path: {
          type: 'string',
          description: 'Path to the file relative to workspace root'
        }
      },
      required: ['path']
    },
    async ({ path: filePath }) => {
      try {
        const validatedPath = validatePath(filePath);
        log(`Reading file: ${filePath}`);

        const content = await fs.readFile(validatedPath, 'utf-8');

        return {
          content: [{
            type: 'text',
            text: content
          }]
        };
      } catch (error) {
        if (error.code === 'ENOENT') {
          throw new Error(`File not found: ${filePath}`);
        } else if (error.code === 'EACCES') {
          throw new Error(`Permission denied: ${filePath}`);
        } else {
          throw error;
        }
      }
    }
  );

  /**
   * Tool: write_file
   * Write or update a file
   */
  server.tool(
    'write_file',
    'Write content to a file in the workspace (creates parent directories if needed)',
    {
      type: 'object',
      properties: {
        path: {
          type: 'string',
          description: 'Path to the file relative to workspace root'
        },
        content: {
          type: 'string',
          description: 'Content to write to the file'
        }
      },
      required: ['path', 'content']
    },
    async ({ path: filePath, content }) => {
      try {
        const validatedPath = validatePath(filePath);
        log(`Writing file: ${filePath}`);

        // Ensure parent directory exists
        const dir = path.dirname(validatedPath);
        await fs.mkdir(dir, { recursive: true });

        // Write file
        await fs.writeFile(validatedPath, content, 'utf-8');

        return {
          content: [{
            type: 'text',
            text: `Successfully wrote to ${filePath} (${content.length} bytes)`
          }]
        };
      } catch (error) {
        if (error.code === 'EACCES') {
          throw new Error(`Permission denied: ${filePath}`);
        } else {
          throw error;
        }
      }
    }
  );

  /**
   * Tool: list_directory
   * List contents of a directory with metadata
   */
  server.tool(
    'list_directory',
    'List files and directories with metadata (size, type, modified time)',
    {
      type: 'object',
      properties: {
        path: {
          type: 'string',
          description: 'Path to directory (relative to workspace root, defaults to root)',
          default: '.'
        }
      }
    },
    async ({ path: dirPath = '.' }) => {
      try {
        const validatedPath = validatePath(dirPath);
        log(`Listing directory: ${dirPath}`);

        const entries = await fs.readdir(validatedPath, { withFileTypes: true });
        const items = [];

        for (const entry of entries) {
          const fullPath = path.join(validatedPath, entry.name);
          let stats;

          try {
            stats = await fs.stat(fullPath);
          } catch (error) {
            continue; // Skip entries we can't stat
          }

          items.push({
            name: entry.name,
            type: entry.isDirectory() ? 'directory' : 'file',
            size: entry.isDirectory() ? null : formatFileSize(stats.size),
            sizeBytes: entry.isDirectory() ? null : stats.size,
            modified: stats.mtime.toISOString()
          });
        }

        // Sort: directories first, then alphabetically
        items.sort((a, b) => {
          if (a.type === 'directory' && b.type !== 'directory') return -1;
          if (a.type !== 'directory' && b.type === 'directory') return 1;
          return a.name.localeCompare(b.name);
        });

        // Format as readable text
        let text = `Directory: ${dirPath}\n`;
        text += `Total items: ${items.length}\n\n`;

        for (const item of items) {
          const icon = item.type === 'directory' ? '📁' : '📄';
          const size = item.size || '';
          text += `${icon} ${item.name.padEnd(40)} ${size.padEnd(12)} ${item.modified}\n`;
        }

        return {
          content: [{
            type: 'text',
            text
          }]
        };
      } catch (error) {
        if (error.code === 'ENOENT') {
          throw new Error(`Directory not found: ${dirPath}`);
        } else if (error.code === 'ENOTDIR') {
          throw new Error(`Not a directory: ${dirPath}`);
        } else {
          throw error;
        }
      }
    }
  );

  /**
   * Tool: search_files
   * Search for files matching a glob pattern
   */
  server.tool(
    'search_files',
    'Search for files matching a glob pattern (e.g., "**/*.js" for all JavaScript files)',
    {
      type: 'object',
      properties: {
        pattern: {
          type: 'string',
          description: 'Glob pattern to match files (e.g., "**/*.js", "src/**/*.ts")'
        },
        directory: {
          type: 'string',
          description: 'Directory to search in (relative to workspace root, defaults to root)',
          default: '.'
        }
      },
      required: ['pattern']
    },
    async ({ pattern, directory = '.' }) => {
      try {
        const validatedPath = validatePath(directory);
        log(`Searching for: ${pattern} in ${directory}`);

        const matches = await glob(pattern, {
          cwd: validatedPath,
          nodir: true, // Files only
          dot: false   // Exclude hidden files
        });

        let text = `Found ${matches.length} file(s) matching "${pattern}" in ${directory}\n\n`;

        for (const match of matches) {
          text += `📄 ${match}\n`;
        }

        return {
          content: [{
            type: 'text',
            text
          }]
        };
      } catch (error) {
        throw new Error(`Search failed: ${error.message}`);
      }
    }
  );

  /**
   * Tool: delete_file
   * Delete a file
   */
  server.tool(
    'delete_file',
    'Delete a file from the workspace',
    {
      type: 'object',
      properties: {
        path: {
          type: 'string',
          description: 'Path to the file to delete (relative to workspace root)'
        }
      },
      required: ['path']
    },
    async ({ path: filePath }) => {
      try {
        const validatedPath = validatePath(filePath);
        log(`Deleting file: ${filePath}`);

        // Verify it's a file, not a directory
        const stats = await fs.stat(validatedPath);
        if (stats.isDirectory()) {
          throw new Error('Cannot delete directories (only files)');
        }

        await fs.unlink(validatedPath);

        return {
          content: [{
            type: 'text',
            text: `Successfully deleted: ${filePath}`
          }]
        };
      } catch (error) {
        if (error.code === 'ENOENT') {
          throw new Error(`File not found: ${filePath}`);
        } else if (error.code === 'EACCES') {
          throw new Error(`Permission denied: ${filePath}`);
        } else {
          throw error;
        }
      }
    }
  );

  // ============================================================================
  // RESOURCES
  // ============================================================================

  /**
   * Resource: fs://tree
   * Directory tree visualization
   */
  server.resource(
    'fs://tree',
    'Visualize the workspace directory structure as a tree',
    async () => {
      log('Generating directory tree');

      const tree = await getDirectoryTree(WORKSPACE_ROOT);

      return {
        contents: [{
          uri: 'fs://tree',
          mimeType: 'text/plain',
          text: `Workspace Directory Tree\n` +
                `Root: ${WORKSPACE_ROOT}\n\n` +
                tree
        }]
      };
    }
  );

  /**
   * Resource: fs://stats
   * Filesystem statistics
   */
  server.resource(
    'fs://stats',
    'Get filesystem statistics (file count, total size, etc.)',
    async () => {
      log('Calculating filesystem stats');

      const stats = await getFilesystemStats(WORKSPACE_ROOT);

      return {
        contents: [{
          uri: 'fs://stats',
          mimeType: 'text/plain',
          text: `Workspace Statistics\n` +
                `Root: ${WORKSPACE_ROOT}\n\n` +
                `Files: ${stats.files}\n` +
                `Directories: ${stats.directories}\n` +
                `Total Size: ${stats.totalSize}\n`
        }]
      };
    }
  );

  // ============================================================================
  // START SERVER
  // ============================================================================

  const transport = new StdioServerTransport();
  await server.connect(transport);

  log('Filesystem MCP Server running');
  log(`Ready to accept connections`);
}

// Run server
main().catch((error) => {
  console.error('Fatal error:', error);
  process.exit(1);
});
