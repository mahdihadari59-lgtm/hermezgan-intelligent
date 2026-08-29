#!/usr/bin/env node
/**
 * Fix Remaining ESLint Warnings
 * Fixes: unused vars, missing useEffect dependencies
 */

const fs = require('fs');
const path = require('path');

const PROJECT_ROOT = process.cwd();

const FIXES = [
  {
    file: 'src/pages/ChatPage.js',
    changes: [
      {
        // Fix 1: Remove unused useState import
        find: /import\s+React,\s*\{\s*useState,\s*useEffect\s*\}\s+from\s+['"]react['"];?/,
        replace: "import React, { useEffect } from 'react';"
      },
      {
        // Fix 2: Add sessionId to useEffect dependency array
        // Pattern: useEffect(() => { ... }, []);  -> add sessionId
        find: /(useEffect\(\(\)\s*=>\s*\{[\s\S]*?\}\s*,\s*)\[\]\s*\);?/,
        replace: "$1[sessionId]);"
      }
    ]
  },
  {
    file: 'src/pages/MapPage.js',
    changes: [
      {
        // Fix 3-4: Remove unused showDetailPanel, setShowDetailPanel from destructuring
        // Try common patterns
        find: /(,?\s*showDetailPanel\s*,?\s*setShowDetailPanel,?)/,
        replace: ""
      },
      {
        // Fix 5: Remove unused userLocation from destructuring  
        find: /(,?\s*userLocation\s*,?)/,
        replace: ""
      }
    ]
  }
];

function applyFixes(filePath, changes) {
  const fullPath = path.join(PROJECT_ROOT, filePath);
  if (!fs.existsSync(fullPath)) {
    console.log(`❌ Not found: ${filePath}`);
    return;
  }

  let content = fs.readFileSync(fullPath, 'utf-8');
  let modified = false;

  for (const change of changes) {
    if (change.find.test(content)) {
      content = content.replace(change.find, change.replace);
      modified = true;
      console.log(`  ✓ Applied fix: ${change.replace.substring(0, 60)}...`);
    } else {
      console.log(`  ⚠ Pattern not matched, may need manual fix`);
    }
  }

  if (modified) {
    fs.writeFileSync(fullPath, content);
    console.log(`✅ Fixed warnings in: ${filePath}\n`);
  } else {
    console.log(`ℹ️ No changes: ${filePath}\n`);
  }
}

console.log('╔══════════════════════════════════════════════════╗');
console.log('║     Fix Remaining ESLint Warnings               ║');
console.log('╚══════════════════════════════════════════════════╝\n');

for (const fix of FIXES) {
  console.log(`📄 ${fix.file}`);
  applyFixes(fix.file, fix.changes);
}

console.log('Done! Run ESLint again to verify:');
console.log('  npx eslint src/pages/ChatPage.js src/pages/MapPage.js');
