#!/usr/bin/env node
/**
 * Kill processes on ports used by MCP Inspector and CoreText server
 * Run this before starting the inspector to ensure clean port state
 */

import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

async function killPort(port) {
  try {
    console.log(`🔍 Checking port ${port}...`);

    const { stdout } = await execAsync(`netstat -ano | findstr :${port}`);

    if (stdout.trim()) {
      const lines = stdout.trim().split('\n');
      const pids = new Set();

      for (const line of lines) {
        const parts = line.trim().split(/\s+/);
        const pid = parts[parts.length - 1];
        if (pid && !isNaN(pid)) {
          pids.add(pid);
        }
      }

      for (const pid of pids) {
        try {
          await execAsync(`taskkill /F /PID ${pid}`);
          console.log(`   ✅ Killed PID ${pid} on port ${port}`);
        } catch (killError) {
          console.log(`   ⚠️  Could not kill PID ${pid}`);
        }
      }
    } else {
      console.log(`   ✅ Port ${port} is free`);
    }
  } catch (error) {
    console.log(`   ✅ Port ${port} is free`);
  }
}

async function main() {
  console.log('============================================');
  console.log('🧹 Cleaning ports for MCP Inspector');
  console.log('============================================\n');

  // Kill ports used by MCP Inspector and CoreText
  await killPort(3000);  // Inspector server backend
  await killPort(5173);  // Inspector Vite UI frontend
  await killPort(3001);  // CoreText health server

  console.log('\n✅ All ports cleaned!\n');
  console.log('You can now run: npm run inspector');
  console.log('============================================');
}

main().catch(console.error);
