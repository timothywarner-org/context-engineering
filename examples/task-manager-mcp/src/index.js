#!/usr/bin/env node

/**
 * Task Manager MCP Server
 *
 * A local MCP server demonstrating task management with persistent storage.
 * Provides CRUD operations for tasks with status tracking, priorities, and due dates.
 *
 * Features:
 * - Create, read, update, delete tasks
 * - Status management (todo, in-progress, done)
 * - Priority levels (low, medium, high)
 * - Due date tracking
 * - JSON file persistence
 * - Task filtering and search
 *
 * Tools:
 * - create_task: Create a new task
 * - get_task: Get a task by ID
 * - update_task: Update an existing task
 * - delete_task: Delete a task
 * - list_tasks: List all tasks with optional filters
 * - complete_task: Mark a task as complete
 *
 * Resources:
 * - tasks://all: View all tasks
 * - tasks://pending: View pending tasks (todo + in-progress)
 * - tasks://completed: View completed tasks
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { promises as fs } from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Data file path
const DATA_DIR = path.join(__dirname, '..', 'data');
const TASKS_FILE = path.join(DATA_DIR, 'tasks.json');

// Valid values
const VALID_STATUSES = ['todo', 'in-progress', 'done'];
const VALID_PRIORITIES = ['low', 'medium', 'high'];

/**
 * Ensure data directory exists
 */
async function ensureDataDirectory() {
  try {
    await fs.mkdir(DATA_DIR, { recursive: true });
  } catch (error) {
    console.error('[Error] Failed to create data directory:', error.message);
    throw error;
  }
}

/**
 * Load tasks from file
 */
async function loadTasks() {
  try {
    await ensureDataDirectory();
    const data = await fs.readFile(TASKS_FILE, 'utf-8');
    return JSON.parse(data);
  } catch (error) {
    if (error.code === 'ENOENT') {
      // File doesn't exist yet, return empty array
      return [];
    }
    console.error('[Error] Failed to load tasks:', error.message);
    throw error;
  }
}

/**
 * Save tasks to file
 */
async function saveTasks(tasks) {
  try {
    await ensureDataDirectory();
    await fs.writeFile(TASKS_FILE, JSON.stringify(tasks, null, 2), 'utf-8');
  } catch (error) {
    console.error('[Error] Failed to save tasks:', error.message);
    throw error;
  }
}

/**
 * Generate a unique task ID
 */
function generateId() {
  return `task_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}

/**
 * Validate task status
 */
function validateStatus(status) {
  if (!VALID_STATUSES.includes(status)) {
    throw new Error(`Invalid status: ${status}. Must be one of: ${VALID_STATUSES.join(', ')}`);
  }
}

/**
 * Validate task priority
 */
function validatePriority(priority) {
  if (!VALID_PRIORITIES.includes(priority)) {
    throw new Error(`Invalid priority: ${priority}. Must be one of: ${VALID_PRIORITIES.join(', ')}`);
  }
}

/**
 * Validate due date format (ISO 8601)
 */
function validateDueDate(dueDate) {
  if (!dueDate) return;

  const date = new Date(dueDate);
  if (isNaN(date.getTime())) {
    throw new Error(`Invalid due date: ${dueDate}. Must be ISO 8601 format (e.g., 2025-01-15T10:00:00Z)`);
  }
}

/**
 * Format a task for display
 */
function formatTask(task) {
  const statusEmoji = {
    'todo': '📋',
    'in-progress': '🔄',
    'done': '✅'
  };

  const priorityEmoji = {
    'low': '🟢',
    'medium': '🟡',
    'high': '🔴'
  };

  let formatted = `${statusEmoji[task.status]} **${task.title}** (${task.id})\n`;
  formatted += `   Priority: ${priorityEmoji[task.priority]} ${task.priority}\n`;
  formatted += `   Status: ${task.status}\n`;

  if (task.description) {
    formatted += `   Description: ${task.description}\n`;
  }

  if (task.dueDate) {
    const dueDate = new Date(task.dueDate);
    const isOverdue = dueDate < new Date() && task.status !== 'done';
    formatted += `   Due: ${dueDate.toLocaleString()} ${isOverdue ? '⚠️ OVERDUE' : ''}\n`;
  }

  formatted += `   Created: ${new Date(task.createdAt).toLocaleString()}\n`;

  if (task.updatedAt && task.updatedAt !== task.createdAt) {
    formatted += `   Updated: ${new Date(task.updatedAt).toLocaleString()}\n`;
  }

  return formatted;
}

/**
 * Format multiple tasks for display
 */
function formatTaskList(tasks, title = 'Tasks') {
  if (tasks.length === 0) {
    return `**${title}**\n\nNo tasks found.`;
  }

  let output = `**${title}** (${tasks.length} total)\n\n`;

  // Group by status
  const byStatus = {
    'todo': tasks.filter(t => t.status === 'todo'),
    'in-progress': tasks.filter(t => t.status === 'in-progress'),
    'done': tasks.filter(t => t.status === 'done')
  };

  for (const [status, statusTasks] of Object.entries(byStatus)) {
    if (statusTasks.length > 0) {
      output += `\n**${status.toUpperCase()}** (${statusTasks.length})\n`;
      statusTasks.forEach(task => {
        output += formatTask(task) + '\n';
      });
    }
  }

  return output;
}

async function main() {
  console.error('📋 Starting Task Manager MCP Server...');

  // Ensure data directory exists
  await ensureDataDirectory();

  const server = new Server(
    {
      name: 'task-manager-mcp',
      version: '1.0.0'
    },
    {
      capabilities: {
        tools: {},
        resources: {}
      }
    }
  );

  // ==========================================================================
  // TOOL: create_task
  // ==========================================================================

  server.tool(
    'create_task',
    'Create a new task',
    {
      type: 'object',
      properties: {
        title: {
          type: 'string',
          description: 'Task title (required)'
        },
        description: {
          type: 'string',
          description: 'Task description (optional)'
        },
        priority: {
          type: 'string',
          enum: VALID_PRIORITIES,
          description: 'Task priority (default: medium)'
        },
        dueDate: {
          type: 'string',
          description: 'Due date in ISO 8601 format (optional, e.g., 2025-01-15T10:00:00Z)'
        }
      },
      required: ['title']
    },
    async ({ title, description, priority, dueDate }) => {
      try {
        console.error(`[Tool] create_task: ${title}`);

        // Validate inputs
        if (!title || title.trim().length === 0) {
          throw new Error('Task title cannot be empty');
        }

        const taskPriority = priority || 'medium';
        validatePriority(taskPriority);

        if (dueDate) {
          validateDueDate(dueDate);
        }

        // Create new task
        const now = new Date().toISOString();
        const task = {
          id: generateId(),
          title: title.trim(),
          description: description ? description.trim() : '',
          status: 'todo',
          priority: taskPriority,
          dueDate: dueDate || null,
          createdAt: now,
          updatedAt: now
        };

        // Load existing tasks and add new one
        const tasks = await loadTasks();
        tasks.push(task);
        await saveTasks(tasks);

        console.error(`[Success] Created task: ${task.id}`);

        return {
          content: [{
            type: 'text',
            text: `✅ **Task Created**\n\n${formatTask(task)}`
          }]
        };
      } catch (error) {
        console.error(`[Error] create_task: ${error.message}`);
        return {
          content: [{
            type: 'text',
            text: `❌ Failed to create task: ${error.message}`
          }],
          isError: true
        };
      }
    }
  );

  // ==========================================================================
  // TOOL: get_task
  // ==========================================================================

  server.tool(
    'get_task',
    'Get a task by ID',
    {
      type: 'object',
      properties: {
        id: {
          type: 'string',
          description: 'Task ID'
        }
      },
      required: ['id']
    },
    async ({ id }) => {
      try {
        console.error(`[Tool] get_task: ${id}`);

        const tasks = await loadTasks();
        const task = tasks.find(t => t.id === id);

        if (!task) {
          throw new Error(`Task not found: ${id}`);
        }

        return {
          content: [{
            type: 'text',
            text: formatTask(task)
          }]
        };
      } catch (error) {
        console.error(`[Error] get_task: ${error.message}`);
        return {
          content: [{
            type: 'text',
            text: `❌ Failed to get task: ${error.message}`
          }],
          isError: true
        };
      }
    }
  );

  // ==========================================================================
  // TOOL: update_task
  // ==========================================================================

  server.tool(
    'update_task',
    'Update an existing task',
    {
      type: 'object',
      properties: {
        id: {
          type: 'string',
          description: 'Task ID'
        },
        title: {
          type: 'string',
          description: 'New task title (optional)'
        },
        description: {
          type: 'string',
          description: 'New task description (optional)'
        },
        status: {
          type: 'string',
          enum: VALID_STATUSES,
          description: 'New task status (optional)'
        },
        priority: {
          type: 'string',
          enum: VALID_PRIORITIES,
          description: 'New task priority (optional)'
        },
        dueDate: {
          type: 'string',
          description: 'New due date in ISO 8601 format (optional)'
        }
      },
      required: ['id']
    },
    async ({ id, title, description, status, priority, dueDate }) => {
      try {
        console.error(`[Tool] update_task: ${id}`);

        const tasks = await loadTasks();
        const taskIndex = tasks.findIndex(t => t.id === id);

        if (taskIndex === -1) {
          throw new Error(`Task not found: ${id}`);
        }

        // Validate inputs
        if (status) {
          validateStatus(status);
        }
        if (priority) {
          validatePriority(priority);
        }
        if (dueDate) {
          validateDueDate(dueDate);
        }

        // Update task fields
        const task = tasks[taskIndex];

        if (title !== undefined) task.title = title.trim();
        if (description !== undefined) task.description = description.trim();
        if (status !== undefined) task.status = status;
        if (priority !== undefined) task.priority = priority;
        if (dueDate !== undefined) task.dueDate = dueDate;

        task.updatedAt = new Date().toISOString();

        // Save updated tasks
        await saveTasks(tasks);

        console.error(`[Success] Updated task: ${id}`);

        return {
          content: [{
            type: 'text',
            text: `✅ **Task Updated**\n\n${formatTask(task)}`
          }]
        };
      } catch (error) {
        console.error(`[Error] update_task: ${error.message}`);
        return {
          content: [{
            type: 'text',
            text: `❌ Failed to update task: ${error.message}`
          }],
          isError: true
        };
      }
    }
  );

  // ==========================================================================
  // TOOL: delete_task
  // ==========================================================================

  server.tool(
    'delete_task',
    'Delete a task',
    {
      type: 'object',
      properties: {
        id: {
          type: 'string',
          description: 'Task ID'
        }
      },
      required: ['id']
    },
    async ({ id }) => {
      try {
        console.error(`[Tool] delete_task: ${id}`);

        const tasks = await loadTasks();
        const taskIndex = tasks.findIndex(t => t.id === id);

        if (taskIndex === -1) {
          throw new Error(`Task not found: ${id}`);
        }

        const deletedTask = tasks[taskIndex];
        tasks.splice(taskIndex, 1);

        await saveTasks(tasks);

        console.error(`[Success] Deleted task: ${id}`);

        return {
          content: [{
            type: 'text',
            text: `✅ **Task Deleted**\n\n${deletedTask.title} (${id})`
          }]
        };
      } catch (error) {
        console.error(`[Error] delete_task: ${error.message}`);
        return {
          content: [{
            type: 'text',
            text: `❌ Failed to delete task: ${error.message}`
          }],
          isError: true
        };
      }
    }
  );

  // ==========================================================================
  // TOOL: list_tasks
  // ==========================================================================

  server.tool(
    'list_tasks',
    'List all tasks with optional filters',
    {
      type: 'object',
      properties: {
        status: {
          type: 'string',
          enum: [...VALID_STATUSES, 'all'],
          description: 'Filter by status (default: all)'
        },
        priority: {
          type: 'string',
          enum: [...VALID_PRIORITIES, 'all'],
          description: 'Filter by priority (default: all)'
        }
      }
    },
    async ({ status, priority }) => {
      try {
        console.error(`[Tool] list_tasks: status=${status || 'all'}, priority=${priority || 'all'}`);

        let tasks = await loadTasks();

        // Apply filters
        if (status && status !== 'all') {
          validateStatus(status);
          tasks = tasks.filter(t => t.status === status);
        }

        if (priority && priority !== 'all') {
          validatePriority(priority);
          tasks = tasks.filter(t => t.priority === priority);
        }

        // Sort by priority (high > medium > low), then by due date
        const priorityOrder = { 'high': 0, 'medium': 1, 'low': 2 };
        tasks.sort((a, b) => {
          // First by priority
          const priorityDiff = priorityOrder[a.priority] - priorityOrder[b.priority];
          if (priorityDiff !== 0) return priorityDiff;

          // Then by due date (tasks with due dates first, then by date)
          if (a.dueDate && !b.dueDate) return -1;
          if (!a.dueDate && b.dueDate) return 1;
          if (a.dueDate && b.dueDate) {
            return new Date(a.dueDate) - new Date(b.dueDate);
          }

          // Finally by creation date
          return new Date(b.createdAt) - new Date(a.createdAt);
        });

        const filterText = [];
        if (status && status !== 'all') filterText.push(`status: ${status}`);
        if (priority && priority !== 'all') filterText.push(`priority: ${priority}`);

        const title = filterText.length > 0
          ? `Tasks (filtered by ${filterText.join(', ')})`
          : 'All Tasks';

        return {
          content: [{
            type: 'text',
            text: formatTaskList(tasks, title)
          }]
        };
      } catch (error) {
        console.error(`[Error] list_tasks: ${error.message}`);
        return {
          content: [{
            type: 'text',
            text: `❌ Failed to list tasks: ${error.message}`
          }],
          isError: true
        };
      }
    }
  );

  // ==========================================================================
  // TOOL: complete_task
  // ==========================================================================

  server.tool(
    'complete_task',
    'Mark a task as complete',
    {
      type: 'object',
      properties: {
        id: {
          type: 'string',
          description: 'Task ID'
        }
      },
      required: ['id']
    },
    async ({ id }) => {
      try {
        console.error(`[Tool] complete_task: ${id}`);

        const tasks = await loadTasks();
        const taskIndex = tasks.findIndex(t => t.id === id);

        if (taskIndex === -1) {
          throw new Error(`Task not found: ${id}`);
        }

        const task = tasks[taskIndex];
        task.status = 'done';
        task.updatedAt = new Date().toISOString();

        await saveTasks(tasks);

        console.error(`[Success] Completed task: ${id}`);

        return {
          content: [{
            type: 'text',
            text: `✅ **Task Completed**\n\n${formatTask(task)}`
          }]
        };
      } catch (error) {
        console.error(`[Error] complete_task: ${error.message}`);
        return {
          content: [{
            type: 'text',
            text: `❌ Failed to complete task: ${error.message}`
          }],
          isError: true
        };
      }
    }
  );

  // ==========================================================================
  // RESOURCE: tasks://all
  // ==========================================================================

  server.resource(
    'tasks://all',
    'View all tasks',
    async () => {
      console.error('[Resource] tasks://all');

      const tasks = await loadTasks();

      return {
        contents: [{
          uri: 'tasks://all',
          mimeType: 'text/plain',
          text: formatTaskList(tasks, 'All Tasks')
        }]
      };
    }
  );

  // ==========================================================================
  // RESOURCE: tasks://pending
  // ==========================================================================

  server.resource(
    'tasks://pending',
    'View pending tasks (todo + in-progress)',
    async () => {
      console.error('[Resource] tasks://pending');

      const tasks = await loadTasks();
      const pending = tasks.filter(t => t.status === 'todo' || t.status === 'in-progress');

      return {
        contents: [{
          uri: 'tasks://pending',
          mimeType: 'text/plain',
          text: formatTaskList(pending, 'Pending Tasks')
        }]
      };
    }
  );

  // ==========================================================================
  // RESOURCE: tasks://completed
  // ==========================================================================

  server.resource(
    'tasks://completed',
    'View completed tasks',
    async () => {
      console.error('[Resource] tasks://completed');

      const tasks = await loadTasks();
      const completed = tasks.filter(t => t.status === 'done');

      return {
        contents: [{
          uri: 'tasks://completed',
          mimeType: 'text/plain',
          text: formatTaskList(completed, 'Completed Tasks')
        }]
      };
    }
  );

  // ==========================================================================
  // START SERVER
  // ==========================================================================

  const transport = new StdioServerTransport();
  await server.connect(transport);

  console.error('✅ Task Manager MCP Server ready');
  console.error('📍 Registered tools: create_task, get_task, update_task, delete_task, list_tasks, complete_task');
  console.error('📍 Registered resources: tasks://all, tasks://pending, tasks://completed');
}

main().catch((error) => {
  console.error('❌ Fatal error:', error);
  process.exit(1);
});
