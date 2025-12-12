#!/usr/bin/env node

import { readFile, writeFile } from 'fs/promises';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';
import type { Quote, QuotesData } from './types.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const QUOTES_FILE = join(__dirname, '..', 'quotes.json');
const QUOTES_SOURCE_DIR = join(__dirname, '..', 'quotes-source');

// Theme keyword mapping for auto-detection
const THEME_KEYWORDS: Record<string, string[]> = {
  anxiety: ['anxiety', 'anxious', 'worry', 'fear', 'stress'],
  courage: ['courage', 'courageous', 'brave', 'bravery', 'bold'],
  control: ['control', 'power', 'influence', 'agency'],
  mindset: ['mind', 'thought', 'thinking', 'perspective', 'view'],
  discipline: ['discipline', 'practice', 'habit', 'training'],
  wisdom: ['wisdom', 'wise', 'knowledge', 'understanding'],
  adversity: ['adversity', 'difficulty', 'challenge', 'obstacle', 'hardship'],
  resilience: ['resilience', 'strength', 'endurance', 'perseverance'],
  virtue: ['virtue', 'virtuous', 'good', 'moral', 'character'],
  presence: ['present', 'now', 'moment', 'time'],
  gratitude: ['gratitude', 'grateful', 'thankful', 'appreciate'],
  action: ['action', 'do', 'doing', 'act'],
  integrity: ['integrity', 'truth', 'honest', 'honor'],
  contentment: ['contentment', 'content', 'satisfaction', 'enough'],
  preparation: ['preparation', 'prepare', 'ready'],
  opportunity: ['opportunity', 'chance', 'luck'],
  purpose: ['purpose', 'goal', 'aim', 'direction'],
  response: ['response', 'react', 'reaction', 'happen']
};

function detectTheme(text: string): string {
  const lowerText = text.toLowerCase();

  for (const [theme, keywords] of Object.entries(THEME_KEYWORDS)) {
    if (keywords.some(keyword => lowerText.includes(keyword))) {
      return theme;
    }
  }

  // Default theme if no keywords match
  return 'wisdom';
}

function parseQuoteLine(line: string): Omit<Quote, 'id' | 'favorite' | 'notes' | 'createdAt' | 'addedBy'> | null {
  // Expected format: "Quote text" - Author, Source
  const match = line.match(/^"([^"]+)"\s*-\s*([^,]+),\s*(.+)$/);

  if (!match) {
    console.warn(`Warning: Could not parse line: ${line}`);
    return null;
  }

  const [, text, author, source] = match;
  const theme = detectTheme(text);

  return {
    text: text.trim(),
    author: author.trim(),
    source: source.trim(),
    theme
  };
}

async function readQuotesData(): Promise<QuotesData> {
  try {
    const data = await readFile(QUOTES_FILE, 'utf-8');
    return JSON.parse(data);
  } catch (error) {
    console.error('Error reading quotes file:', error);
    throw error;
  }
}

async function writeQuotesData(data: QuotesData): Promise<void> {
  try {
    await writeFile(QUOTES_FILE, JSON.stringify(data, null, 2), 'utf-8');
  } catch (error) {
    console.error('Error writing quotes file:', error);
    throw error;
  }
}

async function importQuotes(filePath: string): Promise<void> {
  try {
    // Read input file
    const fileContent = await readFile(filePath, 'utf-8');
    const lines = fileContent
      .split('\n')
      .map(line => line.trim())
      .filter(line => line.length > 0 && !line.startsWith('#')); // Skip empty lines and comments

    console.log(`Found ${lines.length} lines to process...`);

    // Parse quotes
    const parsedQuotes = lines
      .map(parseQuoteLine)
      .filter((q): q is NonNullable<typeof q> => q !== null);

    if (parsedQuotes.length === 0) {
      console.error('No valid quotes found in file');
      process.exit(1);
    }

    console.log(`Successfully parsed ${parsedQuotes.length} quotes`);

    // Read existing quotes data
    const quotesData = await readQuotesData();

    // Generate new quotes with IDs
    const now = new Date().toISOString();
    let nextId = quotesData.metadata.lastId + 1;

    const newQuotes: Quote[] = parsedQuotes.map(parsed => ({
      ...parsed,
      id: nextId++,
      favorite: false,
      notes: null,
      createdAt: now,
      addedBy: 'manual'
    }));

    // Append to existing quotes
    quotesData.quotes.push(...newQuotes);

    // Update metadata
    quotesData.metadata.lastId = nextId - 1;
    quotesData.metadata.lastModified = now;

    // Write atomically
    await writeQuotesData(quotesData);

    console.log(`✓ Successfully imported ${newQuotes.length} quotes`);
    console.log(`  New quote IDs: ${newQuotes[0].id} - ${newQuotes[newQuotes.length - 1].id}`);
    console.log(`  Total quotes: ${quotesData.quotes.length}`);

  } catch (error) {
    if (error instanceof Error) {
      console.error(`Error: ${error.message}`);
    } else {
      console.error('Unknown error occurred');
    }
    process.exit(1);
  }
}

// CLI entry point
const args = process.argv.slice(2);

if (args.length === 0) {
  console.error('Usage: npm run import <filename>');
  console.error('');
  console.error('Files should be placed in: local/quotes-source/');
  console.error('');
  console.error('Expected file format (one quote per line):');
  console.error('"Quote text here" - Author Name, Source Book');
  console.error('');
  console.error('Example:');
  console.error('"The best time to plant a tree was 20 years ago. The second best time is now." - Chinese Proverb, Traditional Wisdom');
  console.error('');
  console.error('Example usage:');
  console.error('  npm run import my-quotes.txt');
  process.exit(1);
}

// Resolve file path from quotes-source directory
const fileName = args[0];
const filePath = join(QUOTES_SOURCE_DIR, fileName);

console.log(`Reading from: ${filePath}`);
importQuotes(filePath);
