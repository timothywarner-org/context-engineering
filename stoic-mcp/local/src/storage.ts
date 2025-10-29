import { readFile, writeFile } from 'fs/promises';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';
import type { Quote, QuotesData, SearchParams } from './types.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const QUOTES_FILE = join(__dirname, '..', 'quotes.json');

export class QuoteStorage {
  private async readQuotes(): Promise<QuotesData> {
    try {
      const data = await readFile(QUOTES_FILE, 'utf-8');
      return JSON.parse(data);
    } catch (error) {
      console.error('Error reading quotes file:', error);
      return {
        metadata: {
          lastId: 0,
          version: '1.0.0',
          lastModified: new Date().toISOString()
        },
        quotes: []
      };
    }
  }

  private async writeQuotes(data: QuotesData): Promise<void> {
    try {
      // Update lastModified timestamp
      data.metadata.lastModified = new Date().toISOString();
      await writeFile(QUOTES_FILE, JSON.stringify(data, null, 2), 'utf-8');
    } catch (error) {
      console.error('Error writing quotes file:', error);
      throw new Error('Failed to write quotes');
    }
  }

  async getRandomQuote(): Promise<Quote | null> {
    const data = await this.readQuotes();
    if (data.quotes.length === 0) return null;
    
    const randomIndex = Math.floor(Math.random() * data.quotes.length);
    return data.quotes[randomIndex];
  }

  async searchQuotes(params: SearchParams): Promise<Quote[]> {
    const data = await this.readQuotes();
    let results = data.quotes;

    if (params.author) {
      results = results.filter(q => 
        q.author.toLowerCase().includes(params.author!.toLowerCase())
      );
    }

    if (params.theme) {
      results = results.filter(q => 
        q.theme.toLowerCase() === params.theme!.toLowerCase()
      );
    }

    if (params.query) {
      const searchLower = params.query.toLowerCase();
      results = results.filter(q =>
        q.text.toLowerCase().includes(searchLower) ||
        q.author.toLowerCase().includes(searchLower) ||
        q.theme.toLowerCase().includes(searchLower)
      );
    }

    return results;
  }

  async addQuote(quote: Omit<Quote, 'id'>): Promise<Quote> {
    const data = await this.readQuotes();

    // Generate new ID from metadata
    const newId = data.metadata.lastId + 1;

    const newQuote: Quote = {
      ...quote,
      id: newId
    };

    data.quotes.push(newQuote);
    data.metadata.lastId = newId;
    await this.writeQuotes(data);

    return newQuote;
  }

  async updateQuote(id: number, updates: Partial<Quote>): Promise<Quote | null> {
    const data = await this.readQuotes();
    const index = data.quotes.findIndex(q => q.id === id);

    if (index === -1) return null;

    data.quotes[index] = { ...data.quotes[index], ...updates };
    await this.writeQuotes(data);

    return data.quotes[index];
  }

  async deleteQuote(id: number): Promise<boolean> {
    const data = await this.readQuotes();
    const initialLength = data.quotes.length;

    data.quotes = data.quotes.filter(q => q.id !== id);

    if (data.quotes.length === initialLength) {
      return false; // Quote not found
    }

    await this.writeQuotes(data);
    return true;
  }

  async getFavorites(): Promise<Quote[]> {
    const data = await this.readQuotes();
    return data.quotes.filter(q => q.favorite);
  }

  async toggleFavorite(id: number): Promise<Quote | null> {
    const data = await this.readQuotes();
    const quote = data.quotes.find(q => q.id === id);

    if (!quote) return null;

    quote.favorite = !quote.favorite;
    await this.writeQuotes(data);

    return quote;
  }
}
