#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const https = require('https');
const http = require('http');

// Find all markdown files
function findMarkdownFiles(dir, files = []) {
  const items = fs.readdirSync(dir);
  
  for (const item of items) {
    const fullPath = path.join(dir, item);
    const stat = fs.statSync(fullPath);
    
    if (stat.isDirectory()) {
      if (!item.startsWith('.') && item !== 'node_modules') {
        findMarkdownFiles(fullPath, files);
      }
    } else if (item.endsWith('.md')) {
      files.push(fullPath);
    }
  }
  
  return files;
}

// Extract links from markdown content
function extractLinks(content) {
  const linkRegex = /\[([^\]]+)\]\(([^)]+)\)/g;
  const links = [];
  let match;
  
  while ((match = linkRegex.exec(content)) !== null) {
    links.push({
      text: match[1],
      url: match[2]
    });
  }
  
  return links;
}

// Check if URL is external (http/https)
function isExternalUrl(url) {
  return url.startsWith('http://') || url.startsWith('https://');
}

// Validate URL (HEAD request)
function validateUrl(url) {
  return new Promise((resolve) => {
    const protocol = url.startsWith('https://') ? https : http;
    const options = {
      method: 'HEAD',
      timeout: 10000,
      headers: {
        'User-Agent': 'Mozilla/5.0 (compatible; LinkChecker/1.0)'
      }
    };
    
    try {
      const req = protocol.request(url, options, (res) => {
        resolve({
          url,
          status: res.statusCode,
          valid: res.statusCode >= 200 && res.statusCode < 400
        });
      });
      
      req.on('error', (error) => {
        resolve({
          url,
          status: 0,
          valid: false,
          error: error.message
        });
      });
      
      req.on('timeout', () => {
        req.destroy();
        resolve({
          url,
          status: 0,
          valid: false,
          error: 'Timeout'
        });
      });
      
      req.end();
    } catch (error) {
      resolve({
        url,
        status: 0,
        valid: false,
        error: error.message
      });
    }
  });
}

// Main execution
async function main() {
  console.log('🔍 Finding markdown files...\n');
  const markdownFiles = findMarkdownFiles('.');
  console.log(`Found ${markdownFiles.length} markdown files\n`);
  
  const allLinks = [];
  const uniqueUrls = new Set();
  
  // Extract all links
  for (const file of markdownFiles) {
    const content = fs.readFileSync(file, 'utf8');
    const links = extractLinks(content);
    const externalLinks = links.filter(link => isExternalUrl(link.url));
    
    if (externalLinks.length > 0) {
      allLinks.push({ file, links: externalLinks });
      externalLinks.forEach(link => uniqueUrls.add(link.url));
    }
  }
  
  console.log(`📊 Statistics:`);
  console.log(`- Total external links: ${Array.from(uniqueUrls).length}\n`);
  
  // Validate unique URLs (sample for speed)
  console.log('🌐 Validating sample of external URLs...\n');
  const urlsToValidate = Array.from(uniqueUrls).slice(0, 20);
  const results = await Promise.all(urlsToValidate.map(validateUrl));
  
  const failed = results.filter(r => !r.valid);
  
  if (failed.length > 0) {
    console.log('❌ Failed URLs:\n');
    failed.forEach(result => {
      console.log(`  ${result.url}`);
      console.log(`    Status: ${result.status} ${result.error || ''}\n`);
    });
  } else {
    console.log('✅ All sampled URLs are valid!\n');
  }
  
  console.log(`\n📝 Summary:`);
  console.log(`- Validated: ${results.length} URLs (sample)`);
  console.log(`- Valid: ${results.filter(r => r.valid).length}`);
  console.log(`- Failed: ${failed.length}`);
}

main().catch(console.error);
