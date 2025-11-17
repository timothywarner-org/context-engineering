#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

function checkMarkdownFile(filePath) {
  const content = fs.readFileSync(filePath, 'utf8');
  const lines = content.split('\n');
  const issues = [];
  
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    const prevLine = i > 0 ? lines[i - 1] : '';
    const nextLine = i < lines.length - 1 ? lines[i + 1] : '';
    
    // MD022: Headings should be surrounded by blank lines
    if (line.match(/^#{1,6}\s+/)) {
      if (i > 0 && prevLine.trim() !== '' && !prevLine.match(/^#{1,6}\s+/) && !prevLine.match(/^---+$/)) {
        issues.push({
          line: i + 1,
          rule: 'MD022',
          message: 'Heading should have blank line before it'
        });
      }
      if (i < lines.length - 1 && nextLine.trim() !== '' && !nextLine.match(/^#{1,6}\s+/) && !nextLine.match(/^---+$/)) {
        issues.push({
          line: i + 1,
          rule: 'MD022',
          message: 'Heading should have blank line after it'
        });
      }
    }
    
    // MD031: Fenced code blocks should be surrounded by blank lines
    if (line.match(/^```/)) {
      const isOpening = !line.match(/^```$/);
      if (i > 0 && prevLine.trim() !== '' && !isOpening) {
        issues.push({
          line: i + 1,
          rule: 'MD031',
          message: 'Code block should have blank line before it'
        });
      }
    }
    
    // MD032: Lists should be surrounded by blank lines
    if (line.match(/^[\s]*[-*+]\s+/) || line.match(/^[\s]*\d+\.\s+/)) {
      if (i > 0 && prevLine.trim() !== '' && !prevLine.match(/^[\s]*[-*+\d.]\s+/)) {
        issues.push({
          line: i + 1,
          rule: 'MD032',
          message: 'List should have blank line before it'
        });
      }
    }
    
    // Check for tabs (should use spaces)
    if (line.includes('\t')) {
      issues.push({
        line: i + 1,
        rule: 'NO-TABS',
        message: 'Use spaces instead of tabs'
      });
    }
    
    // Check trailing spaces
    if (line.match(/\s+$/)) {
      issues.push({
        line: i + 1,
        rule: 'NO-TRAILING-SPACES',
        message: 'Remove trailing spaces'
      });
    }
  }
  
  return issues;
}

function main() {
  const filesToCheck = [
    './MCP_TUTORIALS.md',
    './POPULAR_REMOTE_MCP_SERVERS.md',
    './STUDENT_SETUP_GUIDE.md',
    './TROUBLESHOOTING_FAQ.md',
    './IMPLEMENTATION_GUIDE.md',
    './POST_COURSE_RESOURCES.md',
    './README.md'
  ];
  
  console.log('📝 Checking markdown files for formatting issues...\n');
  
  let totalIssues = 0;
  
  for (const file of filesToCheck) {
    if (!fs.existsSync(file)) {
      console.log(`⚠️  Skipping ${file} (not found)\n`);
      continue;
    }
    
    const issues = checkMarkdownFile(file);
    
    if (issues.length > 0) {
      console.log(`❌ ${file}:`);
      issues.forEach(issue => {
        console.log(`  Line ${issue.line}: [${issue.rule}] ${issue.message}`);
      });
      console.log();
      totalIssues += issues.length;
    } else {
      console.log(`✅ ${file}: No issues found`);
    }
  }
  
  console.log(`\n📊 Total issues found: ${totalIssues}`);
  
  if (totalIssues === 0) {
    console.log('✨ All markdown files are properly formatted!');
  }
}

main();
