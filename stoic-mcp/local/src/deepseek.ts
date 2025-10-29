import type { Quote } from './types.js';

const DEEPSEEK_API_URL = 'https://api.deepseek.com/v1/chat/completions';

export class DeepSeekService {
  private apiKey: string;

  constructor() {
    this.apiKey = process.env.DEEPSEEK_API_KEY || '';
    if (!this.apiKey) {
      console.warn('DEEPSEEK_API_KEY not set. AI explanations will be disabled.');
    }
  }

  async explainQuote(quote: Quote): Promise<string> {
    if (!this.apiKey) {
      return 'DeepSeek API key not configured. Set DEEPSEEK_API_KEY environment variable to enable AI explanations.';
    }

    const prompt = `You are a Stoic philosophy expert. Explain this quote in practical terms for a modern software developer dealing with work stress and technical challenges.

Quote: "${quote.text}"
Author: ${quote.author}
Source: ${quote.source}

Provide a concise, actionable explanation (2-3 paragraphs) that helps a developer apply this wisdom to their daily work. Focus on practical application rather than philosophical theory.`;

    try {
      const response = await fetch(DEEPSEEK_API_URL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.apiKey}`
        },
        body: JSON.stringify({
          model: 'deepseek-chat',
          messages: [
            {
              role: 'user',
              content: prompt
            }
          ],
          temperature: 0.7,
          max_tokens: 500
        })
      });

      if (!response.ok) {
        const error = await response.text();
        console.error('DeepSeek API error:', error);
        return `Failed to get explanation: ${response.status} ${response.statusText}`;
      }

      const data = await response.json() as {
        choices: Array<{
          message: {
            content: string;
          };
        }>;
      };
      return data.choices[0].message.content;
    } catch (error) {
      console.error('Error calling DeepSeek API:', error);
      return `Error getting explanation: ${error instanceof Error ? error.message : 'Unknown error'}`;
    }
  }

  async generateQuote(theme: string): Promise<string> {
    if (!this.apiKey) {
      return 'DeepSeek API key not configured. Set DEEPSEEK_API_KEY environment variable to enable AI quote generation.';
    }

    const prompt = `Generate a Stoic-style quote about "${theme}" that would be helpful for a software developer. Make it sound authentic to ancient Stoic philosophers like Marcus Aurelius, Seneca, or Epictetus. Return only the quote itself, without attribution or extra commentary.`;

    try {
      const response = await fetch(DEEPSEEK_API_URL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.apiKey}`
        },
        body: JSON.stringify({
          model: 'deepseek-chat',
          messages: [
            {
              role: 'user',
              content: prompt
            }
          ],
          temperature: 0.8,
          max_tokens: 150
        })
      });

      if (!response.ok) {
        const error = await response.text();
        console.error('DeepSeek API error:', error);
        return `Failed to generate quote: ${response.status} ${response.statusText}`;
      }

      const data = await response.json() as {
        choices: Array<{
          message: {
            content: string;
          };
        }>;
      };
      return data.choices[0].message.content.trim().replace(/^["']|["']$/g, '');
    } catch (error) {
      console.error('Error calling DeepSeek API:', error);
      return `Error generating quote: ${error instanceof Error ? error.message : 'Unknown error'}`;
    }
  }
}
