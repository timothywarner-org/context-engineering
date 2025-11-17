# Task Manager MCP Server

A local MCP (Model Context Protocol) server for task management with persistent JSON storage. Demonstrates CRUD operations, status tracking, and file-based persistence patterns.

## Overview

This MCP server provides AI assistants with the ability to create, read, update, and delete tasks with full persistence. It's an ideal example of how to implement stateful MCP servers with local file storage.

### Use Cases

- Personal task management through AI conversations
- Project planning with AI assistance
- Todo list management across AI sessions
- Task tracking with status and priority management
- Learning MCP server development patterns

## Features

### Task Management

- ✅ **CRUD Operations**: Create, read, update, and delete tasks
- 📊 **Status Tracking**: todo, in-progress, done
- 🎯 **Priority Levels**: low, medium, high
- 📅 **Due Dates**: ISO 8601 date tracking with overdue detection
- 💾 **Persistent Storage**: JSON file-based storage
- 🔍 **Filtering**: Filter tasks by status and priority
- 📋 **Multiple Views**: All tasks, pending tasks, completed tasks

### MCP Capabilities

- **6 Tools**: create_task, get_task, update_task, delete_task, list_tasks, complete_task
- **3 Resources**: tasks://all, tasks://pending, tasks://completed
- **stdio Transport**: Local process-based communication
- **Input Validation**: Comprehensive validation of all inputs
- **Error Handling**: Graceful error messages for all operations

## Installation

### Prerequisites

- Node.js 20 or higher
- npm or yarn

### Setup

```bash
# Navigate to the task manager directory
cd examples/task-manager-mcp

# Install dependencies
npm install

# Test the server
npm start
```

## Configuration

### Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "task-manager": {
      "command": "node",
      "args": ["/absolute/path/to/context-engineering/examples/task-manager-mcp/src/index.js"]
    }
  }
}
```

**Windows Example:**
```json
{
  "mcpServers": {
    "task-manager": {
      "command": "node",
      "args": ["C:\\Users\\YourName\\context-engineering\\examples\\task-manager-mcp\\src\\index.js"]
    }
  }
}
```

**macOS/Linux Example:**
```json
{
  "mcpServers": {
    "task-manager": {
      "command": "node",
      "args": ["/Users/yourname/context-engineering/examples/task-manager-mcp/src/index.js"]
    }
  }
}
```

### VS Code with Cline

Add to your Cline MCP settings:

```json
{
  "task-manager": {
    "command": "node",
    "args": ["/absolute/path/to/examples/task-manager-mcp/src/index.js"]
  }
}
```

### Testing with MCP Inspector

```bash
# Start MCP Inspector
npx @modelcontextprotocol/inspector node src/index.js

# Open the URL shown in your browser
# Test tools and resources interactively
```

## Usage

### Basic Task Creation

```
User: Create a task to review the quarterly report
AI: [Calls create_task tool]
✅ Task Created

📋 **Review the quarterly report** (task_1234567890_abc123def)
   Priority: 🟡 medium
   Status: todo
   Created: 1/15/2025, 10:30:00 AM
```

### Task with Priority and Due Date

```
User: Create a high priority task to submit expense report by Friday
AI: [Calls create_task with priority="high" and dueDate="2025-01-19T17:00:00Z"]
✅ Task Created

📋 **Submit expense report** (task_1234567891_xyz789abc)
   Priority: 🔴 high
   Status: todo
   Due: 1/19/2025, 5:00:00 PM
   Created: 1/15/2025, 10:35:00 AM
```

### Listing Tasks

```
User: Show me all my tasks
AI: [Calls list_tasks tool]

**All Tasks** (5 total)

**TODO** (2)
📋 **Submit expense report** (task_1234567891_xyz789abc)
   Priority: 🔴 high
   Status: todo
   Due: 1/19/2025, 5:00:00 PM
   Created: 1/15/2025, 10:35:00 AM

📋 **Review the quarterly report** (task_1234567890_abc123def)
   Priority: 🟡 medium
   Status: todo
   Created: 1/15/2025, 10:30:00 AM

**IN-PROGRESS** (2)
🔄 **Write documentation** (task_1234567892_def456ghi)
   Priority: 🟡 medium
   Status: in-progress
   Created: 1/14/2025, 9:00:00 AM

**DONE** (1)
✅ **Setup development environment** (task_1234567893_ghi789jkl)
   Priority: 🟢 low
   Status: done
   Created: 1/13/2025, 2:00:00 PM
```

### Updating Task Status

```
User: Mark the expense report task as in-progress
AI: [Calls update_task with status="in-progress"]
✅ Task Updated

🔄 **Submit expense report** (task_1234567891_xyz789abc)
   Priority: 🔴 high
   Status: in-progress
   Due: 1/19/2025, 5:00:00 PM ⚠️ OVERDUE
   Created: 1/15/2025, 10:35:00 AM
   Updated: 1/20/2025, 11:00:00 AM
```

### Completing Tasks

```
User: Complete the expense report task
AI: [Calls complete_task]
✅ Task Completed

✅ **Submit expense report** (task_1234567891_xyz789abc)
   Priority: 🔴 high
   Status: done
   Due: 1/19/2025, 5:00:00 PM
   Created: 1/15/2025, 10:35:00 AM
   Updated: 1/20/2025, 3:30:00 PM
```

### Filtering Tasks

```
User: Show me only high priority tasks
AI: [Calls list_tasks with priority="high"]

**Tasks (filtered by priority: high)** (1 total)

**DONE** (1)
✅ **Submit expense report** (task_1234567891_xyz789abc)
   Priority: 🔴 high
   Status: done
   Created: 1/15/2025, 10:35:00 AM
```

## Tool Reference

### create_task

Create a new task.

**Parameters:**
- `title` (string, required): Task title
- `description` (string, optional): Task description
- `priority` (string, optional): Priority level (low, medium, high). Default: medium
- `dueDate` (string, optional): Due date in ISO 8601 format

**Example:**
```javascript
{
  "title": "Write documentation",
  "description": "Complete the API documentation for the new features",
  "priority": "high",
  "dueDate": "2025-01-25T17:00:00Z"
}
```

### get_task

Get a task by ID.

**Parameters:**
- `id` (string, required): Task ID

**Example:**
```javascript
{
  "id": "task_1234567890_abc123def"
}
```

### update_task

Update an existing task.

**Parameters:**
- `id` (string, required): Task ID
- `title` (string, optional): New title
- `description` (string, optional): New description
- `status` (string, optional): New status (todo, in-progress, done)
- `priority` (string, optional): New priority (low, medium, high)
- `dueDate` (string, optional): New due date in ISO 8601 format

**Example:**
```javascript
{
  "id": "task_1234567890_abc123def",
  "status": "in-progress",
  "priority": "high"
}
```

### delete_task

Delete a task.

**Parameters:**
- `id` (string, required): Task ID

**Example:**
```javascript
{
  "id": "task_1234567890_abc123def"
}
```

### list_tasks

List all tasks with optional filters.

**Parameters:**
- `status` (string, optional): Filter by status (todo, in-progress, done, all). Default: all
- `priority` (string, optional): Filter by priority (low, medium, high, all). Default: all

**Example:**
```javascript
{
  "status": "todo",
  "priority": "high"
}
```

### complete_task

Mark a task as complete (shortcut for updating status to 'done').

**Parameters:**
- `id` (string, required): Task ID

**Example:**
```javascript
{
  "id": "task_1234567890_abc123def"
}
```

## Resource Reference

### tasks://all

View all tasks in the system.

**Returns:** Formatted list of all tasks grouped by status

### tasks://pending

View all pending tasks (status: todo or in-progress).

**Returns:** Formatted list of pending tasks

### tasks://completed

View all completed tasks (status: done).

**Returns:** Formatted list of completed tasks

## Data Storage

Tasks are stored in `examples/task-manager-mcp/data/tasks.json`.

### Task Schema

```json
{
  "id": "task_1234567890_abc123def",
  "title": "Task title",
  "description": "Optional description",
  "status": "todo",
  "priority": "medium",
  "dueDate": "2025-01-25T17:00:00Z",
  "createdAt": "2025-01-15T10:30:00.000Z",
  "updatedAt": "2025-01-15T10:30:00.000Z"
}
```

### Storage Location

- **Default:** `examples/task-manager-mcp/data/tasks.json`
- **Auto-created:** Directory and file are created automatically on first use
- **Format:** Pretty-printed JSON with 2-space indentation

## Architecture

### Key Design Patterns

1. **File-based Persistence**: Simple JSON file storage for reliability
2. **Validation Layer**: Comprehensive input validation for all operations
3. **Error Handling**: Graceful error messages with detailed context
4. **Formatted Output**: Human-readable task display with emojis
5. **Smart Sorting**: Tasks sorted by priority, due date, and creation time

### Code Structure

```
task-manager-mcp/
├── src/
│   └── index.js          # Main server implementation
├── data/
│   └── tasks.json        # Task storage (auto-created)
├── package.json          # Dependencies and scripts
└── README.md            # This file
```

## Troubleshooting

### Server won't start

**Error:** `Cannot find module '@modelcontextprotocol/sdk'`

**Solution:**
```bash
cd examples/task-manager-mcp
npm install
```

### Tasks not persisting

**Error:** Tasks disappear after restart

**Cause:** File write permissions or path issues

**Solution:**
```bash
# Check data directory exists
ls -la data/

# Verify file permissions
chmod 644 data/tasks.json

# Check file contents
cat data/tasks.json
```

### Invalid due date error

**Error:** `Invalid due date: 2025-01-25`

**Cause:** Due date must be in full ISO 8601 format

**Solution:** Use complete ISO 8601 format with time:
```
✅ Correct: "2025-01-25T17:00:00Z"
❌ Wrong:   "2025-01-25"
❌ Wrong:   "01/25/2025"
```

### Task not found error

**Error:** `Task not found: task_xyz123`

**Cause:** Invalid task ID or task was deleted

**Solution:** Use `list_tasks` to get valid task IDs:
```
User: Show me all my tasks
[Gets list with valid IDs]
```

## Advanced Usage

### Batch Operations

```
User: Create three tasks:
1. Review pull request (high priority)
2. Update documentation (medium priority)
3. Refactor logging (low priority)

AI: [Creates three tasks with appropriate priorities]
```

### Task Dependencies

```
User: I can't work on task X until task Y is done. Update task X to note this.

AI: [Updates task X description to include dependency note]
```

### Recurring Tasks

```
User: Create a weekly task to review analytics every Monday

AI: [Creates task with due date next Monday and notes it's weekly in description]
```

## Learning Objectives

This MCP server demonstrates:

1. **State Management**: How to persist data across sessions
2. **CRUD Patterns**: Complete implementation of create/read/update/delete
3. **Input Validation**: Proper validation of all user inputs
4. **Error Handling**: Graceful error messages and recovery
5. **Resource Exposure**: Multiple views of the same data (all/pending/completed)
6. **File I/O**: Safe file operations with Node.js fs module
7. **Data Formatting**: Human-readable output formatting
8. **Schema Design**: Task data structure with proper types

## Next Steps

### Enhancements

- Add task search by keywords
- Implement task tags/categories
- Add task notes/comments
- Support subtasks
- Add task attachments
- Implement recurring tasks
- Add task history/audit log
- Support multiple projects

### Migration to Database

When you outgrow file-based storage:

1. Replace `loadTasks()` and `saveTasks()` with database queries
2. Add database connection pooling
3. Use transactions for multi-step operations
4. Add indexes for performance
5. Consider using examples/database-mcp as reference

## Related Examples

- **filesystem-mcp**: File operations with sandboxing
- **weather-api-mcp**: External API integration with caching
- **knowledge-base-mcp**: Remote MCP server with Azure deployment
- **analytics-mcp**: Remote MCP server with advanced querying

## Support

For issues or questions:

- Check the main course [TROUBLESHOOTING_FAQ.md](../../TROUBLESHOOTING_FAQ.md)
- Review [STUDENT_SETUP_GUIDE.md](../../STUDENT_SETUP_GUIDE.md)
- Refer to [IMPLEMENTATION_GUIDE.md](../../IMPLEMENTATION_GUIDE.md)

## License

MIT License - See LICENSE file for details
