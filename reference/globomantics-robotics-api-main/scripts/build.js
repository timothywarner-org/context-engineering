/**
 * Build script for Globomantics Robotics API
 * Creates a distribution package with version info
 */

const fs = require('fs');
const path = require('path');

const packageJson = require('../package.json');

const buildDir = path.join(__dirname, '..', 'dist');
const buildInfo = {
  name: packageJson.name,
  version: packageJson.version,
  buildTime: new Date().toISOString(),
  nodeVersion: process.version,
  platform: process.platform,
  arch: process.arch
};

// Create dist directory
if (!fs.existsSync(buildDir)) {
  fs.mkdirSync(buildDir, { recursive: true });
}

// Write build info
fs.writeFileSync(
  path.join(buildDir, 'build-info.json'),
  JSON.stringify(buildInfo, null, 2)
);

// Copy source files
const srcDir = path.join(__dirname, '..', 'src');
const distSrcDir = path.join(buildDir, 'src');

if (!fs.existsSync(distSrcDir)) {
  fs.mkdirSync(distSrcDir, { recursive: true });
}

const sourceFiles = fs.readdirSync(srcDir);
sourceFiles.forEach(file => {
  fs.copyFileSync(
    path.join(srcDir, file),
    path.join(distSrcDir, file)
  );
});

// Copy package.json
fs.copyFileSync(
  path.join(__dirname, '..', 'package.json'),
  path.join(buildDir, 'package.json')
);

console.log('Build completed successfully!');
console.log(`Output directory: ${buildDir}`);
console.log(`Build info:`, buildInfo);
