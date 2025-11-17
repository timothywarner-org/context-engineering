#!/usr/bin/env node

const fs = require('fs');

function fixMarkdownFile(filePath) {
  const content = fs.readFileSync(filePath, 'utf8');
  const lines = content.split('\n');
  const fixed = [];
  
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    const prevLine = i > 0 ? lines[i - 1] : '';
    const nextLine = i < lines.length - 1 ? lines[i + 1] : '';
    
    // MD022: Add blank line before heading if needed
    if (line.match(/^#{1,6}\s+/) && i > 0) {
      if (prevLine.trim() !== '' && !prevLine.match(/^#{1,6}\s+/) && !prevLine.match(/^---+$/)) {
        fixed.push('');
      }
    }
    
    // MD031: Add blank line before code block if needed
    if (line.match(/^```/) && i > 0) {
      if (prevLine.trim() !== '') {
        fixed.push('');
      }
    }
    
    // MD032: Add blank line before list if needed
    if ((line.match(/^[\s]*[-*+]\s+/) || line.match(/^[\s]*\d+\.\s+/)) && i > 0) {
      if (prevLine.trim() !== '' && !prevLine.match(/^[\s]*[-*+\d.]\s+/)) {
        fixed.push('');
      }
    }
    
    fixed.push(line);
    
    // MD022: Add blank line after heading if needed
    if (line.match(/^#{1,6}\s+/) && i < lines.length - 1) {
      if (nextLine.trim() !== '' && !nextLine.match(/^#{1,6}\s+/) && !nextLine.match(/^---+$/)) {
        fixed.push('');
      }
    }
  }
  
  // Remove trailing spaces
  const cleaned = fixed.map(line => line.trimEnd());
  
  // Ensure file ends with newline
  return cleaned.join('\n') + '\n';
}

const filesToFix = [
  './MCP_TUTORIALS.md',
  './POPULAR_REMOTE_MCP_SERVERS.md',
  './STUDENT_SETUP_GUIDE.md',
  './TROUBLESHOOTING_FAQ.md',
  './IMPLEMENTATION_GUIDE.md',
  './POST_COURSE_RESOURCES.md'
];

console.log('🔧 Fixing markdown files...\n');

for (const file of filesToFix) {
  if (fs.existsSync(file)) {
    const fixed = fixMarkdownFile(file);
    fs.writeFileSync(file, fixed, 'utf8');
    console.log(`✅ Fixed: ${file}`);
  } else {
    console.log(`⚠️  Skipped: ${file} (not found)`);
  }
}

console.log('\n✨ Markdown formatting complete!');
