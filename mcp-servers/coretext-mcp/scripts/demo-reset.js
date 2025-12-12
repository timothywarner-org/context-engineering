#!/usr/bin/env node
/**
 * Demo Reset Script
 * Wipes all memories and starts fresh with demo data
 */

import fs from 'fs/promises';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const DATA_PATH = path.join(__dirname, '..', 'data', 'memory.json');

console.log('\n🔄 DEMO RESET - Starting Fresh\n');
console.log('============================================\n');

try {
  // Check if file exists
  try {
    await fs.access(DATA_PATH);
    await fs.unlink(DATA_PATH);
    console.log('✅ Deleted existing memory.json');
  } catch {
    console.log('ℹ️  No existing memory.json found');
  }

  console.log('✅ Memory system reset complete');
  console.log('\n============================================');
  console.log('Next steps:');
  console.log('1. npm run dev        - Start server (auto-reloads)');
  console.log('2. npm run inspector  - Open MCP Inspector');
  console.log('3. npm run demo:populate - Add example memories');
  console.log('============================================\n');

} catch (error) {
  console.error('❌ Reset failed:', error.message);
  process.exit(1);
}
