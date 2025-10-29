// contextDemo.js
// ------------------------------------------------------------
// DeepSeek Context Window Utilization Demo
// Author: Tim Warner classroom edition
// ------------------------------------------------------------
// This script demonstrates how token usage grows as conversation
// history expands. It visualizes context window consumption
// using a progress bar and color-coded output in the terminal.
// ------------------------------------------------------------

import axios from "axios";
import * as dotenv from "dotenv";
import { encode } from "gpt-tokenizer";
import chalk from "chalk";
import cliProgress from "cli-progress";

dotenv.config(); // Load .env variables (e.g., DeepSeek API key)

// ------------------------------------------------------------
// Configuration
// ------------------------------------------------------------
const API_KEY = process.env.DEEPSEEK_API_KEY;   // Your DeepSeek API key
const MODEL = "deepseek-chat";                   // Model name (or deepseek-v3)
const MAX_CONTEXT_TOKENS = 128000;               // Typical DeepSeek V3 context size

// ------------------------------------------------------------
// Seed conversation messages
// ------------------------------------------------------------
const baseMessages = [
  { role: "system", content: "You are a clear, concise teaching assistant for AI concepts." },
  { role: "user", content: "Explain what a context window is in plain English." },
  { role: "assistant", content: "A context window is the model's working memory: the space used for input and output tokens together." }
];

// ------------------------------------------------------------
// Count tokens in conversation using GPT-style tokenizer
// ------------------------------------------------------------
function countTokens(messages) {
  const joined = messages.map(m => `${m.role}: ${m.content}`).join("\n");
  return encode(joined).length;
}

// ------------------------------------------------------------
// Display a progress bar for visual effect
// ------------------------------------------------------------
function showMeter(used, total) {
  const bar = new cliProgress.SingleBar({
    format: chalk.cyanBright("Context Window") + " |" + chalk.magenta("{bar}") + `| {percentage}%  ({value}/{total})`,
    barCompleteChar: "█",
    barIncompleteChar: "░",
    hideCursor: true
  });
  bar.start(total, used);
  bar.update(used);
  bar.stop();
}

// ------------------------------------------------------------
// Main loop: simulate a growing conversation
// ------------------------------------------------------------
async function runDemo() {
  let messages = [...baseMessages];
  console.clear();
  console.log(chalk.yellow.bold("🎓 DeepSeek Context Window Demonstration"));
  console.log(chalk.gray("Each turn expands the conversation and shows current token usage.\n"));

  for (let i = 1; i <= 10; i++) {
    // Add a fake message to expand context
    messages.push({ role: "user", content: `This is simulated message number ${i}. Please summarize everything so far.` });

    const usedTokens = countTokens(messages);
    const percent = ((usedTokens / MAX_CONTEXT_TOKENS) * 100).toFixed(2);

    // Print current state
    console.log(chalk.whiteBright(`\n🗨️  Turn ${i}: ${usedTokens} tokens used (${percent}% of window)\n`));
    showMeter(usedTokens, MAX_CONTEXT_TOKENS);

    // Warn when near or over limit
    if (usedTokens >= MAX_CONTEXT_TOKENS) {
      console.log(chalk.red("\n⚠️  Context window exceeded. Older messages would now be truncated.\n"));
      break;
    }

    // Delay between iterations for animation pacing
    await new Promise(r => setTimeout(r, 700));
  }

  console.log(chalk.greenBright("\n✅ Simulation complete. Sending final sample request...\n"));
  await callAPI(messages);
}

// ------------------------------------------------------------
// Call DeepSeek API once to demonstrate real completion usage
// ------------------------------------------------------------
async function callAPI(messages) {
  try {
    const res = await axios.post(
      "https://api.deepseek.com/v1/chat/completions",
      {
        model: MODEL,
        messages,
        max_tokens: 100
      },
      {
        headers: {
          Authorization: `Bearer ${API_KEY}`,
          "Content-Type": "application/json"
        }
      }
    );

    console.log(chalk.cyan("Model response:\n"));
    console.log(chalk.white(res.data.choices[0].message.content));

    // Print usage stats if API returns them
    if (res.data.usage) {
      const u = res.data.usage;
      console.log(chalk.gray(`\nAPI usage → prompt: ${u.prompt_tokens}, completion: ${u.completion_tokens}, total: ${u.total_tokens}`));
    }
  } catch (err) {
    console.error(chalk.red("API error:"), err.response?.data || err.message);
  }
}

// ------------------------------------------------------------
// Execute demo
// ------------------------------------------------------------
runDemo();
