#!/usr/bin/env node
/**
 * Smart Store Import Fixer
 * Auto-detects if stores export hooks or direct actions, then fixes accordingly.
 */

const fs = require('fs');
const path = require('path');

const PROJECT_ROOT = process.cwd();

// Store file paths (relative to project root)
const STORE_FILES = {
  chatStore: 'src/stores/chatStore.js',
  appStore:  'src/stores/appStore.js',
  mapStore:  'src/stores/mapStore.js',
};

// Which actions belong to which store
const STORE_ACTIONS = {
  chatStore: ['clearMessages', 'setSessionId', 'addMessage', 'setTyping'],
  appStore:  ['addNotification', 'setLoading', 'addToast', 'setError', 'clearError'],
  mapStore:  ['setMarkers', 'setGeolocating', 'setUserLocation', 'setMapCenter',
             'setZoom', 'setMapMode', 'setSearchQuery', 'setServiceTypeFilter', 'selectMarker'],
};

const TARGET_FILES = [
  'src/pages/ChatPage.js',
  'src/pages/MapPage.js'
];

// ===================== DETECT STORE PATTERN =====================

function detectStorePattern(storePath) {
  const fullPath = path.join(PROJECT_ROOT, storePath);
  if (!fs.existsSync(fullPath)) {
    console.log(`⚠️  Store not found: ${storePath}`);
    return null;
  }

  const content = fs.readFileSync(fullPath, 'utf-8');

  // Check if it exports a hook (useXxxStore)
  const hookExportMatch = content.match(/export\s+(?:const|function)\s+(use\w+Store)/);
  if (hookExportMatch) {
    return { type: 'hook', hookName: hookExportMatch[1] };
  }

  // Check if it exports direct actions
  const actionExportMatch = content.match(/export\s+(?:const|function)\s+(\w+)/);
  if (actionExportMatch) {
    // Check if any of our known actions are exported directly
    for (const action of Object.values(STORE_ACTIONS).flat()) {
      if (content.includes(`export const ${action}`) || content.includes(`export function ${action}`)) {
        return { type: 'direct' };
      }
    }
  }

  // Check for default export or create pattern (Zustand)
  if (content.includes('create(') || content.includes('createStore')) {
    const hookMatch = content.match(/const\s+(use\w+Store)/);
    if (hookMatch) {
      return { type: 'hook', hookName: hookMatch[1] };
    }
  }

  return { type: 'unknown' };
}

// ===================== FIX FILE =====================

function fixFile(filePath, storePatterns) {
  const fullPath = path.join(PROJECT_ROOT, filePath);
  if (!fs.existsSync(fullPath)) {
    console.log(`❌ File not found: ${filePath}`);
    return;
  }

  let content = fs.readFileSync(fullPath, 'utf-8');
  const originalContent = content;
  let modified = false;

  // Process each store
  for (const [storeName, pattern] of Object.entries(storePatterns)) {
    if (!pattern || !STORE_ACTIONS[storeName]) continue;

    const actions = STORE_ACTIONS[storeName];
    const sourcePath = `../stores/${storeName}`;

    // Find direct import line for this store
    const directImportRegex = new RegExp(
      `import\\s+\\{([^}]*)\\}\\s+from\\s+['"]${sourcePath.replace(/\//g, '\\/')}['"];?\\n?`,
      'g'
    );

    const match = directImportRegex.exec(content);
    if (!match) continue;

    const importedActions = match[1].split(',').map(s => s.trim()).filter(Boolean);
    const relevantActions = importedActions.filter(a => actions.includes(a));

    if (relevantActions.length === 0) continue;

    if (pattern.type === 'hook') {
      // ===== HOOK PATTERN =====
      console.log(`  🔧 ${storeName} uses hook pattern: ${pattern.hookName}`);

      // Remove direct action import
      content = content.replace(match[0], '');

      // Add hook import if not exists
      const hookImportRegex = new RegExp(
        `import\\s+\\{?\\s*${pattern.hookName}\\s*\\}?\\s+from\\s+['"]${sourcePath.replace(/\//g, '\\/')}['"];?`
      );

      if (!hookImportRegex.test(content)) {
        const hookImport = `import { ${pattern.hookName} } from '${sourcePath}';\n`;
        const lastImportIdx = content.lastIndexOf('import ');
        if (lastImportIdx !== -1) {
          const lineEnd = content.indexOf('\n', lastImportIdx);
          const insertPos = lineEnd !== -1 ? lineEnd + 1 : content.length;
          content = content.slice(0, insertPos) + hookImport + content.slice(insertPos);
        } else {
          content = hookImport + content;
        }
      }

      // Add destructuring inside component function
      const componentMatch = content.match(/(const\s+\w+\s*=\s*\(\)\s*=>\s*\{)/);
      if (componentMatch) {
        const hookLine = `  const { ${relevantActions.join(', ')} } = ${pattern.hookName}();`;
        const insertAfter = componentMatch.index + componentMatch[1].length;

        // Check if already added
        if (!content.includes(hookLine)) {
          content = content.slice(0, insertAfter) + '\n' + hookLine + '\n' + content.slice(insertAfter);
        }
      }

      modified = true;
      console.log(`     → Converted to hook + added destructuring`);

    } else if (pattern.type === 'direct') {
      // ===== DIRECT PATTERN =====
      console.log(`  ✅ ${storeName} uses direct exports — no change needed`);
    }
  }

  // Clean up extra blank lines
  content = content.replace(/\n{3,}/g, '\n\n');

  if (modified) {
    fs.writeFileSync(fullPath, content);
    console.log(`✅ Fixed: ${filePath}\n`);
  } else {
    console.log(`ℹ️  No changes needed: ${filePath}\n`);
  }
}

// ===================== MAIN =====================

console.log('╔══════════════════════════════════════════════════╗');
console.log('║     Smart Store Import Fixer v2.0               ║');
console.log('╚══════════════════════════════════════════════════╝\n');

console.log('🔍 Detecting store patterns...\n');

const storePatterns = {};
for (const [name, filePath] of Object.entries(STORE_FILES)) {
  const pattern = detectStorePattern(filePath);
  storePatterns[name] = pattern;

  if (pattern) {
    console.log(`  ${name}: ${pattern.type === 'hook' ? 'HOOK (' + pattern.hookName + ')' : pattern.type.toUpperCase()}`);
  }
}

console.log('\n🔧 Fixing files...\n');

for (const file of TARGET_FILES) {
  console.log(`📄 ${file}`);
  fixFile(file, storePatterns);
}

console.log('Done! Run ESLint again to verify:\n  npx eslint src/pages/ChatPage.js src/pages/MapPage.js');
