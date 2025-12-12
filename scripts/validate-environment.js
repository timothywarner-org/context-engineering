#!/usr/bin/env node

/**
 * Environment Validation Script for MCP in Practice Course
 *
 * This script verifies that your development environment is properly
 * configured for the training session.
 *
 * Usage: node validate-environment.js
 */

const { execSync, spawn } = require('child_process');
const fs = require('fs');
const path = require('path');
const os = require('os');

// ANSI color codes for pretty output
const colors = {
  reset: '\x1b[0m',
  bright: '\x1b[1m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  cyan: '\x1b[36m',
};

function log(message, color = 'reset') {
  console.log(`${colors[color]}${message}${colors.reset}`);
}

function header(message) {
  log('\n' + '='.repeat(60), 'cyan');
  log(`  ${message}`, 'bright');
  log('='.repeat(60), 'cyan');
}

function pass(message) {
  log(`✅ ${message}`, 'green');
}

function fail(message) {
  log(`❌ ${message}`, 'red');
}

function warn(message) {
  log(`⚠️  ${message}`, 'yellow');
}

function info(message) {
  log(`ℹ️  ${message}`, 'blue');
}

// Track overall validation status
let hasErrors = false;
let hasWarnings = false;
const results = {
  passed: [],
  failed: [],
  warnings: []
};

// Helper to run shell commands safely
function runCommand(command, options = {}) {
  try {
    const output = execSync(command, {
      encoding: 'utf8',
      stdio: options.silent ? 'pipe' : 'pipe',
      ...options
    });
    return { success: true, output: output.trim() };
  } catch (error) {
    return { success: false, error: error.message, output: error.stdout?.trim() || '' };
  }
}

// Check Node.js version
function checkNodeVersion() {
  header('Checking Node.js Installation');

  const result = runCommand('node --version');
  if (!result.success) {
    fail('Node.js is not installed or not in PATH');
    results.failed.push('Node.js not found');
    hasErrors = true;
    return;
  }

  const version = result.output.replace('v', '');
  const major = parseInt(version.split('.')[0]);

  if (major >= 20) {
    pass(`Node.js version: ${result.output} (required: >=20.x)`);
    results.passed.push('Node.js version');
  } else {
    fail(`Node.js version too old: ${result.output} (required: >=20.x)`);
    info('Download from: https://nodejs.org/');
    results.failed.push('Node.js version');
    hasErrors = true;
  }
}

// Check npm
function checkNpm() {
  header('Checking npm Installation');

  const result = runCommand('npm --version');
  if (!result.success) {
    fail('npm is not installed or not in PATH');
    results.failed.push('npm not found');
    hasErrors = true;
    return;
  }

  const version = result.output;
  const major = parseInt(version.split('.')[0]);

  if (major >= 9) {
    pass(`npm version: ${version} (recommended: >=9.x)`);
    results.passed.push('npm version');
  } else {
    warn(`npm version is old: ${version} (recommended: >=9.x)`);
    info('Update with: npm install -g npm@latest');
    results.warnings.push('npm version');
    hasWarnings = true;
  }
}

// Check Python (optional)
function checkPython() {
  header('Checking Python Installation (Optional)');

  // Try python3 first, then python
  let result = runCommand('python3 --version', { silent: true });
  if (!result.success) {
    result = runCommand('python --version', { silent: true });
  }

  if (!result.success) {
    warn('Python not found (optional - only needed for Python MCP examples)');
    info('If you want to run Python examples, install from: https://www.python.org/');
    results.warnings.push('Python not installed');
    hasWarnings = true;
    return;
  }

  // Parse version (format: "Python 3.x.x")
  const versionMatch = result.output.match(/Python (\d+)\.(\d+)/);
  if (!versionMatch) {
    warn('Could not parse Python version');
    results.warnings.push('Python version check');
    hasWarnings = true;
    return;
  }

  const major = parseInt(versionMatch[1]);
  const minor = parseInt(versionMatch[2]);

  if (major === 3 && minor >= 9) {
    pass(`Python version: ${result.output} (required: >=3.9)`);
    results.passed.push('Python version');
  } else {
    warn(`Python version may be too old: ${result.output} (required: >=3.9)`);
    results.warnings.push('Python version');
    hasWarnings = true;
  }
}

// Check Docker
function checkDocker() {
  header('Checking Docker Installation (Optional)');

  const result = runCommand('docker --version', { silent: true });
  if (!result.success) {
    warn('Docker not found (optional - needed for containerized deployments)');
    info('Install from: https://www.docker.com/products/docker-desktop');
    results.warnings.push('Docker not installed');
    hasWarnings = true;
    return;
  }

  pass(`Docker installed: ${result.output}`);
  results.passed.push('Docker installed');

  // Check if Docker daemon is running
  const psResult = runCommand('docker ps', { silent: true });
  if (!psResult.success) {
    warn('Docker is installed but daemon is not running');
    info('Start Docker Desktop to enable Docker functionality');
    results.warnings.push('Docker daemon not running');
    hasWarnings = true;
  } else {
    pass('Docker daemon is running');
    results.passed.push('Docker daemon');
  }
}

// Check Git
function checkGit() {
  header('Checking Git Installation');

  const result = runCommand('git --version');
  if (!result.success) {
    fail('Git is not installed');
    info('Install from: https://git-scm.com/downloads');
    results.failed.push('Git not found');
    hasErrors = true;
    return;
  }

  pass(`Git installed: ${result.output}`);
  results.passed.push('Git installed');
}

// Check repository structure
function checkRepositoryStructure() {
  header('Checking Repository Structure');

  const requiredDirs = [
    { path: 'coretext-mcp', name: 'CoreText MCP Server' },
    { path: 'stoic-mcp', name: 'Stoic MCP Server' },
    { path: 'context_journal_mcp_local', name: 'Context Journal MCP (Local)' }
  ];

  const requiredFiles = [
    { path: 'README.md', name: 'Main README' },
    { path: 'DEMO_SCRIPT.md', name: 'Demo Script' },
    { path: 'course-plan.md', name: 'Course Plan' }
  ];

  for (const dir of requiredDirs) {
    if (fs.existsSync(dir.path) && fs.statSync(dir.path).isDirectory()) {
      pass(`Found: ${dir.name} (${dir.path}/)`);
      results.passed.push(dir.name);
    } else {
      fail(`Missing: ${dir.name} (${dir.path}/)`);
      results.failed.push(dir.name);
      hasErrors = true;
    }
  }

  for (const file of requiredFiles) {
    if (fs.existsSync(file.path) && fs.statSync(file.path).isFile()) {
      pass(`Found: ${file.name}`);
      results.passed.push(file.name);
    } else {
      warn(`Missing: ${file.name} (${file.path})`);
      results.warnings.push(file.name);
      hasWarnings = true;
    }
  }
}

// Check CoreText MCP dependencies
function checkCoreTextDependencies() {
  header('Checking CoreText MCP Dependencies');

  const coreTextPath = path.join(process.cwd(), 'coretext-mcp');
  if (!fs.existsSync(coreTextPath)) {
    warn('CoreText MCP directory not found, skipping dependency check');
    return;
  }

  const packageJsonPath = path.join(coreTextPath, 'package.json');
  if (!fs.existsSync(packageJsonPath)) {
    fail('coretext-mcp/package.json not found');
    results.failed.push('CoreText package.json');
    hasErrors = true;
    return;
  }

  pass('Found coretext-mcp/package.json');

  // Check if node_modules exists
  const nodeModulesPath = path.join(coreTextPath, 'node_modules');
  if (!fs.existsSync(nodeModulesPath)) {
    fail('coretext-mcp/node_modules not found');
    info('Run: cd coretext-mcp && npm install');
    results.failed.push('CoreText dependencies');
    hasErrors = true;
    return;
  }

  pass('Found coretext-mcp/node_modules');

  // Check for MCP SDK
  const sdkPath = path.join(nodeModulesPath, '@modelcontextprotocol', 'sdk');
  if (fs.existsSync(sdkPath)) {
    pass('MCP SDK installed in coretext-mcp');
    results.passed.push('CoreText MCP SDK');

    // Try to get version
    const sdkPackageJson = path.join(sdkPath, 'package.json');
    if (fs.existsSync(sdkPackageJson)) {
      try {
        const sdkPkg = JSON.parse(fs.readFileSync(sdkPackageJson, 'utf8'));
        info(`  MCP SDK version: ${sdkPkg.version}`);
      } catch (e) {
        // Ignore version read errors
      }
    }
  } else {
    fail('MCP SDK not installed in coretext-mcp');
    info('Run: cd coretext-mcp && npm install');
    results.failed.push('CoreText MCP SDK');
    hasErrors = true;
  }

  // Check for .env file
  const envPath = path.join(coreTextPath, '.env');
  const envExamplePath = path.join(coreTextPath, '.env.example');

  if (fs.existsSync(envPath)) {
    pass('Found coretext-mcp/.env file');
    results.passed.push('CoreText .env');
  } else if (fs.existsSync(envExamplePath)) {
    warn('.env file not created yet (optional)');
    info('Copy: cp coretext-mcp/.env.example coretext-mcp/.env');
    results.warnings.push('CoreText .env');
    hasWarnings = true;
  } else {
    warn('.env.example file not found');
    results.warnings.push('CoreText .env.example');
    hasWarnings = true;
  }
}

// Check Stoic MCP dependencies
function checkStoicDependencies() {
  header('Checking Stoic MCP Dependencies');

  const stoicPath = path.join(process.cwd(), 'stoic-mcp', 'local');
  if (!fs.existsSync(stoicPath)) {
    warn('Stoic MCP local directory not found, skipping dependency check');
    return;
  }

  const packageJsonPath = path.join(stoicPath, 'package.json');
  if (!fs.existsSync(packageJsonPath)) {
    fail('stoic-mcp/local/package.json not found');
    results.failed.push('Stoic package.json');
    hasErrors = true;
    return;
  }

  pass('Found stoic-mcp/local/package.json');

  // Check if node_modules exists
  const nodeModulesPath = path.join(stoicPath, 'node_modules');
  if (!fs.existsSync(nodeModulesPath)) {
    fail('stoic-mcp/local/node_modules not found');
    info('Run: cd stoic-mcp/local && npm install');
    results.failed.push('Stoic dependencies');
    hasErrors = true;
    return;
  }

  pass('Found stoic-mcp/local/node_modules');

  // Check for build output
  const distPath = path.join(stoicPath, 'dist');
  if (fs.existsSync(distPath)) {
    const indexPath = path.join(distPath, 'index.js');
    if (fs.existsSync(indexPath)) {
      pass('Stoic MCP has been built (dist/index.js exists)');
      results.passed.push('Stoic build');
    } else {
      warn('dist/ directory exists but dist/index.js not found');
      info('Run: cd stoic-mcp/local && npm run build');
      results.warnings.push('Stoic build incomplete');
      hasWarnings = true;
    }
  } else {
    warn('Stoic MCP not built yet (dist/ directory missing)');
    info('Run: cd stoic-mcp/local && npm run build');
    results.warnings.push('Stoic not built');
    hasWarnings = true;
  }
}

// Check Python dependencies (optional)
function checkPythonDependencies() {
  header('Checking Python MCP Dependencies (Optional)');

  const contextJournalPath = path.join(process.cwd(), 'context_journal_mcp_local');
  if (!fs.existsSync(contextJournalPath)) {
    warn('Context Journal MCP directory not found, skipping Python dependency check');
    return;
  }

  const requirementsPath = path.join(contextJournalPath, 'requirements.txt');
  if (!fs.existsSync(requirementsPath)) {
    warn('context_journal_mcp_local/requirements.txt not found');
    results.warnings.push('Python requirements.txt');
    hasWarnings = true;
    return;
  }

  pass('Found context_journal_mcp_local/requirements.txt');

  // Try to check if packages are installed
  const pipResult = runCommand('pip3 list', { silent: true });
  if (!pipResult.success) {
    warn('Could not check Python packages (pip3 not available)');
    return;
  }

  // Check for mcp package
  if (pipResult.output.includes('mcp')) {
    pass('Python MCP SDK appears to be installed');
    results.passed.push('Python MCP SDK');
  } else {
    warn('Python MCP SDK may not be installed');
    info('Run: cd context_journal_mcp_local && pip install -r requirements.txt');
    results.warnings.push('Python MCP SDK');
    hasWarnings = true;
  }
}

// Test CoreText MCP server startup
function testCoreTextStartup() {
  header('Testing CoreText MCP Server Startup');

  const serverPath = path.join(process.cwd(), 'coretext-mcp', 'src', 'index.js');
  if (!fs.existsSync(serverPath)) {
    fail('CoreText server file not found (coretext-mcp/src/index.js)');
    results.failed.push('CoreText server file');
    hasErrors = true;
    return;
  }

  info('Attempting to start CoreText MCP server for 3 seconds...');

  return new Promise((resolve) => {
    const serverProcess = spawn('node', [serverPath], {
      cwd: path.join(process.cwd(), 'coretext-mcp'),
      stdio: ['ignore', 'pipe', 'pipe']
    });

    let output = '';
    let errorOutput = '';

    serverProcess.stdout.on('data', (data) => {
      output += data.toString();
    });

    serverProcess.stderr.on('data', (data) => {
      errorOutput += data.toString();
    });

    // Give server 3 seconds to start
    setTimeout(() => {
      if (!serverProcess.killed) {
        serverProcess.kill();

        // Check for errors in stderr
        if (errorOutput.includes('Error') || errorOutput.includes('error')) {
          fail('CoreText MCP server started but reported errors');
          info('Error output:');
          console.log(errorOutput.slice(0, 500)); // First 500 chars
          results.failed.push('CoreText server startup');
          hasErrors = true;
        } else {
          pass('CoreText MCP server started successfully');
          results.passed.push('CoreText server startup');
        }
        resolve();
      }
    }, 3000);

    serverProcess.on('error', (error) => {
      fail(`CoreText MCP server failed to start: ${error.message}`);
      results.failed.push('CoreText server startup');
      hasErrors = true;
      resolve();
    });

    serverProcess.on('exit', (code) => {
      if (code !== null && code !== 0) {
        fail(`CoreText MCP server exited with code ${code}`);
        if (errorOutput) {
          info('Error output:');
          console.log(errorOutput.slice(0, 500));
        }
        results.failed.push('CoreText server startup');
        hasErrors = true;
      }
      resolve();
    });
  });
}

// Check disk space
function checkDiskSpace() {
  header('Checking Disk Space');

  try {
    // This is a basic check - just verify we can write to the filesystem
    const testFile = path.join(os.tmpdir(), 'mcp-test-' + Date.now() + '.txt');
    fs.writeFileSync(testFile, 'test');
    fs.unlinkSync(testFile);

    pass('Filesystem is writable');
    results.passed.push('Filesystem writable');

    // Get disk usage on Unix-like systems
    if (process.platform !== 'win32') {
      const dfResult = runCommand('df -h .', { silent: true });
      if (dfResult.success) {
        const lines = dfResult.output.split('\n');
        if (lines.length > 1) {
          info('Disk usage:');
          console.log('  ' + lines[1]);
        }
      }
    }
  } catch (error) {
    warn('Could not verify filesystem write access');
    results.warnings.push('Filesystem check');
    hasWarnings = true;
  }
}

// Print summary
function printSummary() {
  header('Validation Summary');

  log(`\nTotal Checks: ${results.passed.length + results.failed.length + results.warnings.length}`, 'bright');
  log(`✅ Passed: ${results.passed.length}`, 'green');
  log(`❌ Failed: ${results.failed.length}`, 'red');
  log(`⚠️  Warnings: ${results.warnings.length}`, 'yellow');

  if (results.failed.length > 0) {
    log('\n❌ FAILED CHECKS:', 'red');
    results.failed.forEach(item => log(`  - ${item}`, 'red'));
  }

  if (results.warnings.length > 0) {
    log('\n⚠️  WARNINGS:', 'yellow');
    results.warnings.forEach(item => log(`  - ${item}`, 'yellow'));
  }

  log(''); // Empty line

  if (hasErrors) {
    fail('❌ VALIDATION FAILED - Please fix the errors above before the training');
    info('Refer to STUDENT_SETUP_GUIDE.md for detailed setup instructions');
    info('Check TROUBLESHOOTING_FAQ.md if you need help');
    process.exit(1);
  } else if (hasWarnings) {
    warn('⚠️  VALIDATION PASSED WITH WARNINGS - Review warnings above');
    info('Optional components are not configured, but you can proceed with the training');
    info('You may want to address warnings for the complete experience');
    process.exit(0);
  } else {
    pass('✅ ALL CHECKS PASSED - Your environment is ready for the training!');
    info('See you in the course! 🚀');
    process.exit(0);
  }
}

// Main execution
async function main() {
  log(`
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║   MCP in Practice: Environment Validation Script             ║
║                                                               ║
║   This script will verify your setup before the training     ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
`, 'cyan');

  // Run all validation checks
  checkNodeVersion();
  checkNpm();
  checkGit();
  checkPython();
  checkDocker();
  checkDiskSpace();
  checkRepositoryStructure();
  checkCoreTextDependencies();
  checkStoicDependencies();
  checkPythonDependencies();

  // Test server startup (async)
  await testCoreTextStartup();

  // Print final summary
  printSummary();
}

// Run validation
main().catch(error => {
  fail(`Unexpected error during validation: ${error.message}`);
  console.error(error);
  process.exit(1);
});
