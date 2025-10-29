#!/usr/bin/env node

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';
import { QuoteStorage } from './storage.js';
import { DeepSeekService } from './deepseek.js';

const storage = new QuoteStorage();
const deepseek = new DeepSeekService();

const server = new Server(
  {
    name: 'stoic-mcp-local',
    version: '1.0.0',
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// List available tools
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: 'get_random_quote',
        description: 'Get a random Stoic quote for inspiration',
        inputSchema: {
          type: 'object',
          properties: {},
        },
      },
      {
        name: 'search_quotes',
        description: 'Search for quotes by author, theme, or keyword',
        inputSchema: {
          type: 'object',
          properties: {
            query: {
              type: 'string',
              description: 'Keyword to search in quote text, author, or theme',
            },
            author: {
              type: 'string',
              description: 'Filter by author name (e.g., "Marcus Aurelius", "Seneca", "Epictetus")',
            },
            theme: {
              type: 'string',
              description: 'Filter by theme (e.g., "control", "mindset", "courage")',
            },
          },
        },
      },
      {
        name: 'add_quote',
        description: 'Add a new Stoic quote to the collection',
        inputSchema: {
          type: 'object',
          properties: {
            text: {
              type: 'string',
              description: 'The quote text',
            },
            author: {
              type: 'string',
              description: 'The author of the quote',
            },
            source: {
              type: 'string',
              description: 'The source book or work',
            },
            theme: {
              type: 'string',
              description: 'The main theme (e.g., "courage", "wisdom", "discipline")',
            },
          },
          required: ['text', 'author', 'source', 'theme'],
        },
      },
      {
        name: 'get_quote_explanation',
        description: 'Get an AI-powered explanation of how to apply a quote to modern developer challenges',
        inputSchema: {
          type: 'object',
          properties: {
            quote_id: {
              type: 'string',
              description: 'The ID of the quote to explain',
            },
          },
          required: ['quote_id'],
        },
      },
      {
        name: 'toggle_favorite',
        description: 'Mark or unmark a quote as favorite',
        inputSchema: {
          type: 'object',
          properties: {
            quote_id: {
              type: 'string',
              description: 'The ID of the quote',
            },
          },
          required: ['quote_id'],
        },
      },
      {
        name: 'get_favorites',
        description: 'Get all quotes marked as favorites',
        inputSchema: {
          type: 'object',
          properties: {},
        },
      },
      {
        name: 'update_quote_notes',
        description: 'Add or update personal notes on a quote',
        inputSchema: {
          type: 'object',
          properties: {
            quote_id: {
              type: 'string',
              description: 'The ID of the quote',
            },
            notes: {
              type: 'string',
              description: 'Your personal notes or reflections',
            },
          },
          required: ['quote_id', 'notes'],
        },
      },
      {
        name: 'delete_quote',
        description: 'Delete a quote from the collection',
        inputSchema: {
          type: 'object',
          properties: {
            quote_id: {
              type: 'string',
              description: 'The ID of the quote to delete',
            },
          },
          required: ['quote_id'],
        },
      },
      {
        name: 'generate_quote',
        description: 'Use AI to generate a new Stoic-style quote on a specific theme',
        inputSchema: {
          type: 'object',
          properties: {
            theme: {
              type: 'string',
              description: 'The theme for the quote (e.g., "debugging", "code review", "imposter syndrome")',
            },
          },
          required: ['theme'],
        },
      },
    ],
  };
});

// Handle tool calls
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  try {
    switch (name) {
      case 'get_random_quote': {
        const quote = await storage.getRandomQuote();
        if (!quote) {
          return {
            content: [{ type: 'text', text: 'No quotes available' }],
          };
        }
        return {
          content: [
            {
              type: 'text',
              text: `"${quote.text}"\n\n— ${quote.author}, ${quote.source}\n\nTheme: ${quote.theme}\nID: ${quote.id}${quote.favorite ? ' ⭐' : ''}${quote.notes !== null ? `\n\nYour notes: ${quote.notes}` : ''}`,
            },
          ],
        };
      }

      case 'search_quotes': {
        const quotes = await storage.searchQuotes(args as any);
        if (quotes.length === 0) {
          return {
            content: [{ type: 'text', text: 'No quotes found matching your criteria' }],
          };
        }
        const formatted = quotes
          .map(
            (q) =>
              `[${q.id}${q.favorite ? ' ⭐' : ''}] "${q.text}"\n— ${q.author}, ${q.source} (Theme: ${q.theme})`
          )
          .join('\n\n');
        return {
          content: [{ type: 'text', text: `Found ${quotes.length} quote(s):\n\n${formatted}` }],
        };
      }

      case 'add_quote': {
        if (!args) {
          return {
            content: [{ type: 'text', text: 'Missing required arguments' }],
            isError: true,
          };
        }
        const newQuote = await storage.addQuote({
          text: args.text as string,
          author: args.author as string,
          source: args.source as string,
          theme: args.theme as string,
          favorite: false,
          notes: null,
          createdAt: new Date().toISOString(),
          addedBy: 'user',
        });
        return {
          content: [
            {
              type: 'text',
              text: `Quote added successfully!\n\nID: ${newQuote.id}\n"${newQuote.text}"\n— ${newQuote.author}`,
            },
          ],
        };
      }

      case 'get_quote_explanation': {
        if (!args) {
          return {
            content: [{ type: 'text', text: 'Missing required arguments' }],
            isError: true,
          };
        }
        const quotes = await storage.searchQuotes({});
        const quote = quotes.find((q) => q.id === Number(args.quote_id));
        if (!quote) {
          return {
            content: [{ type: 'text', text: `Quote with ID ${args.quote_id} not found` }],
          };
        }
        const explanation = await deepseek.explainQuote(quote);
        return {
          content: [
            {
              type: 'text',
              text: `"${quote.text}"\n— ${quote.author}, ${quote.source}\n\n${explanation}`,
            },
          ],
        };
      }

      case 'toggle_favorite': {
        if (!args) {
          return {
            content: [{ type: 'text', text: 'Missing required arguments' }],
            isError: true,
          };
        }
        const updated = await storage.toggleFavorite(Number(args.quote_id));
        if (!updated) {
          return {
            content: [{ type: 'text', text: `Quote with ID ${args.quote_id} not found` }],
          };
        }
        return {
          content: [
            {
              type: 'text',
              text: `Quote ${updated.favorite ? 'marked as favorite ⭐' : 'removed from favorites'}\n\n"${updated.text}"\n— ${updated.author}`,
            },
          ],
        };
      }

      case 'get_favorites': {
        const favorites = await storage.getFavorites();
        if (favorites.length === 0) {
          return {
            content: [{ type: 'text', text: 'No favorite quotes yet' }],
          };
        }
        const formatted = favorites
          .map((q) => `[${q.id}] "${q.text}"\n— ${q.author}, ${q.source}`)
          .join('\n\n');
        return {
          content: [{ type: 'text', text: `Your ${favorites.length} favorite quote(s):\n\n${formatted}` }],
        };
      }

      case 'update_quote_notes': {
        if (!args) {
          return {
            content: [{ type: 'text', text: 'Missing required arguments' }],
            isError: true,
          };
        }
        const updated = await storage.updateQuote(Number(args.quote_id), {
          notes: args.notes as string,
        });
        if (!updated) {
          return {
            content: [{ type: 'text', text: `Quote with ID ${args.quote_id} not found` }],
          };
        }
        return {
          content: [
            {
              type: 'text',
              text: `Notes updated for:\n\n"${updated.text}"\n— ${updated.author}\n\nYour notes: ${updated.notes}`,
            },
          ],
        };
      }

      case 'delete_quote': {
        if (!args) {
          return {
            content: [{ type: 'text', text: 'Missing required arguments' }],
            isError: true,
          };
        }
        const deleted = await storage.deleteQuote(Number(args.quote_id));
        if (!deleted) {
          return {
            content: [{ type: 'text', text: `Quote with ID ${args.quote_id} not found` }],
          };
        }
        return {
          content: [{ type: 'text', text: `Quote ${args.quote_id} deleted successfully` }],
        };
      }

      case 'generate_quote': {
        if (!args) {
          return {
            content: [{ type: 'text', text: 'Missing required arguments' }],
            isError: true,
          };
        }
        const generatedText = await deepseek.generateQuote(args.theme as string);
        return {
          content: [
            {
              type: 'text',
              text: `Generated quote on "${args.theme}":\n\n"${generatedText}"\n\nWould you like to add this to your collection? Use add_quote if so.`,
            },
          ],
        };
      }

      default:
        return {
          content: [{ type: 'text', text: `Unknown tool: ${name}` }],
          isError: true,
        };
    }
  } catch (error) {
    return {
      content: [
        {
          type: 'text',
          text: `Error: ${error instanceof Error ? error.message : 'Unknown error'}`,
        },
      ],
      isError: true,
    };
  }
});

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error('Stoic MCP Local Server running on stdio');
}

main().catch((error) => {
  console.error('Fatal error:', error);
  process.exit(1);
});
