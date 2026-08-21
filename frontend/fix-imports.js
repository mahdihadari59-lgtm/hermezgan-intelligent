#!/usr/bin/env node
/**
 * Auto-Fix ESLint Import Errors
 * ================================
 * This script automatically adds missing imports for ChatPage.js and MapPage.js
 * based on a configurable mapping dictionary.
 * 
 * Usage:
 *   node fix-imports.js
 * 
 * It will:
 *   1. Scan the target files
 *   2. Detect used but undefined identifiers
 *   3. Add missing import statements at the top of each file
 *   4. Create backups before modifying (optional)
 */

const fs = require('fs');
const path = require('path');

// ===================== CONFIGURATION =====================
// Map undefined identifiers to their import sources
const IMPORT_MAP = {
  // --- ChatPage & MapPage shared store actions ---
  clearMessages:    { source: "../stores/chatStore", named: true },
  setSessionId:     { source: "../stores/chatStore", named: true },
  addMessage:       { source: "../stores/chatStore", named: true },
  addNotification:  { source: "../stores/appStore", named: true },
  setLoading:       { source: "../stores/appStore", named: true },
  setTyping:        { source: "../stores/chatStore", named: true },
  addToast:         { source: "../stores/appStore", named: true },
  setError:         { source: "../stores/appStore", named: true },
  clearError:       { source: "../stores/appStore", named: true },

  // --- MapPage store actions ---
  setMarkers:          { source: "../stores/mapStore", named: true },
  setGeolocating:      { source: "../stores/mapStore", named: true },
  setUserLocation:     { source: "../stores/mapStore", named: true },
  setMapCenter:        { source: "../stores/mapStore", named: true },
  setZoom:             { source: "../stores/mapStore", named: true },
  setMapMode:          { source: "../stores/mapStore", named: true },
  setSearchQuery:      { source: "../stores/mapStore", named: true },
  setServiceTypeFilter:{ source: "../stores/mapStore", named: true },
  selectMarker:        { source: "../stores/mapStore", named: true },

  // --- Services ---
  mapService:     { source: "../services/mapService", named: true },
  hotspotService: { source: "../services/hotspotService", named: true },
  cameraService:  { source: "../services/cameraService", named: true },

  // --- React-Leaflet ---
  useMap:         { source: "react-leaflet", named: true },

  // --- ChatPage Components ---
  ChatBox:        { source: "../components/ChatBox", default: true },

  // --- MapPage Components ---
  MapSearch:            { source: "../components/map", named: true },
  HotspotFilter:        { source: "../components/map", named: true },
  HotspotList:          { source: "../components/map", named: true },
  CameraFilter:         { source: "../components/map", named: true },
  CameraList:           { source: "../components/map", named: true },
  LeafletMapContainer:  { source: "../components/map/LeafletMapContainer", default: true },
  TileLayer:            { source: "react-leaflet", named: true },
  MapMarkers:           { source: "../components/map", named: true },
  HotspotMarkers:       { source: "../components/map", named: true },
  CameraMarkers:        { source: "../components/map", named: true },
  MapPopup:             { source: "../components/map", named: true },
  HotspotInfo:          { source: "../components/map", named: true },
  CameraInfo:           { source: "../components/map", named: true },
};

// Files to process
const FILES = [
  "src/pages/ChatPage.js",
  "src/pages/MapPage.js"
];

// ===================== HELPERS =====================

function escapeRegExp(string) {
  return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

function extractExistingImports(content) {
  const imports = new Set();
  const importRegex = /import\s+(?:(\{[^}]*\})|(\w+)|\*\s+as\s+(\w+))\s+from\s+['"]([^'"]+)['"];?/g;
  let match;
  while ((match = importRegex.exec(content)) !== null) {
    if (match[1]) {
      // Named imports: import { a, b } from '...'
      match[1].replace(/[{}\s]/g, '').split(',').forEach(name => {
        if (name) imports.add(name);
      });
    } else if (match[2]) {
      // Default import: import X from '...'
      imports.add(match[2]);
    } else if (match[3]) {
      // Namespace import: import * as X from '...'
      imports.add(match[3]);
    }
  }
  return imports;
}

function findUsedUndefined(content, existingImports) {
  const undefinedIds = new Set();

  // Remove strings, comments, and JSX tags to avoid false positives
  let cleanContent = content
    .replace(/'[^']*'/g, "''")
    .replace(/"[^"]*"/g, '""')
    .replace(/`[^`]*`/g, "``")
    .replace(/\/\/.*/g, '')
    .replace(/\/\*[\s\S]*?\*\//g, '');

  // Find all potential identifiers (words that could be variables/functions)
  const wordRegex = /\b([A-Za-z_]\w*)\b/g;
  let match;

  while ((match = wordRegex.exec(cleanContent)) !== null) {
    const word = match[1];

    // Skip JavaScript reserved words and common globals
    const reserved = new Set([
      'import', 'from', 'export', 'default', 'return', 'const', 'let', 'var',
      'function', 'class', 'if', 'else', 'for', 'while', 'switch', 'case',
      'break', 'continue', 'try', 'catch', 'finally', 'throw', 'new', 'this',
      'true', 'false', 'null', 'undefined', 'async', 'await', 'yield',
      'typeof', 'instanceof', 'in', 'of', 'console', 'window', 'document',
      'React', 'useState', 'useEffect', 'useCallback', 'useMemo', 'useRef',
      'useContext', 'useReducer', 'Promise', 'Set', 'Map', 'Array', 'Object',
      'String', 'Number', 'Boolean', 'Date', 'Math', 'JSON', 'Error',
      'handle', 'onClick', 'onChange', 'onSubmit', 'onClose', 'onOpen',
      'data', 'error', 'response', 'result', 'item', 'index', 'key', 'id',
      'name', 'value', 'label', 'type', 'props', 'state', 'event', 'e',
      'params', 'options', 'config', 'url', 'path', 'method', 'body',
      'headers', 'status', 'message', 'text', 'html', 'style', 'className',
      'children', 'ref', 'forwardRef', 'createElement', 'Fragment',
      'use', 'to', 'as', 'is', 'it', 'be', 'or', 'and', 'not', 'no',
      'get', 'set', 'has', 'can', 'will', 'should', 'do', 'done',
      'go', 'going', 'went', 'come', 'came', 'take', 'took', 'make', 'made',
      'see', 'saw', 'know', 'knew', 'think', 'thought', 'say', 'said',
      'tell', 'told', 'ask', 'asked', 'work', 'worked', 'try', 'tried',
      'feel', 'felt', 'become', 'became', 'leave', 'left', 'put', 'mean',
      'meant', 'keep', 'kept', 'let', 'begin', 'began', 'seem', 'seemed',
      'help', 'helped', 'show', 'showed', 'hear', 'heard', 'play', 'played',
      'run', 'ran', 'move', 'moved', 'live', 'lived', 'believe', 'believed',
      'bring', 'brought', 'happen', 'happened', 'write', 'wrote', 'provide',
      'provided', 'sit', 'sat', 'stand', 'stood', 'lose', 'lost', 'pay',
      'paid', 'meet', 'met', 'include', 'included', 'continue', 'continued',
      'set', 'learn', 'learned', 'change', 'changed', 'lead', 'led',
      'understand', 'understood', 'watch', 'watched', 'follow', 'followed',
      'stop', 'stopped', 'create', 'created', 'speak', 'spoke', 'read',
      'allow', 'allowed', 'add', 'added', 'spend', 'spent', 'grow', 'grew',
      'open', 'opened', 'walk', 'walked', 'win', 'won', 'offer', 'offered',
      'remember', 'remembered', 'love', 'loved', 'consider', 'considered',
      'appear', 'appeared', 'buy', 'bought', 'wait', 'waited', 'serve',
      'served', 'die', 'died', 'send', 'sent', 'expect', 'expected', 'build',
      'built', 'stay', 'stayed', 'fall', 'fell', 'cut', 'reach', 'reached',
      'kill', 'killed', 'remain', 'remained', 'suggest', 'suggested', 'raise',
      'raised', 'pass', 'passed', 'sell', 'sold', 'require', 'required',
      'report', 'reported', 'decide', 'decided', 'pull', 'pulled', 'far',
      'good', 'new', 'first', 'last', 'long', 'great', 'little', 'own',
      'other', 'old', 'right', 'big', 'high', 'different', 'small', 'large',
      'next', 'early', 'young', 'important', 'few', 'public', 'bad', 'same',
      'able', 'module', 'exports', 'require', 'process', 'Buffer', 'global',
      '__dirname', '__filename', 'setTimeout', 'setInterval', 'clearTimeout',
      'clearInterval', 'fetch', 'alert', 'confirm', 'prompt', 'localStorage',
      'sessionStorage', 'location', 'history', 'navigator'
    ]);

    if (reserved.has(word)) continue;
    if (existingImports.has(word)) continue;
    if (!IMPORT_MAP[word]) continue; // Only care about ones we know how to fix

    // Check if it's actually used as a value/function call, not just a property
    const before = cleanContent.substring(Math.max(0, match.index - 20), match.index);
    const after = cleanContent.substring(match.index + word.length, match.index + word.length + 20);

    // Skip if it's a property access (e.g., obj.something)
    if (before.endsWith('.')) continue;

    // Skip if it's inside JSX tag name but already imported
    // We already checked existingImports

    undefinedIds.add(word);
  }

  return undefinedIds;
}

function generateImportStatements(undefinedIds) {
  const sourceGroups = {};

  undefinedIds.forEach(id => {
    const config = IMPORT_MAP[id];
    if (!config) return;

    if (!sourceGroups[config.source]) {
      sourceGroups[config.source] = { named: new Set(), defaults: new Set() };
    }

    if (config.default) {
      sourceGroups[config.source].defaults.add(id);
    } else {
      sourceGroups[config.source].named.add(id);
    }
  });

  const statements = [];
  for (const [source, { named, defaults }] of Object.entries(sourceGroups)) {
    // Default imports (usually one per source)
    defaults.forEach(def => {
      statements.push(`import ${def} from '${source}';`);
    });

    // Named imports
    if (named.size > 0) {
      const sorted = Array.from(named).sort();
      statements.push(`import { ${sorted.join(', ')} } from '${source}';`);
    }
  }

  return statements;
}

function fixFile(filePath) {
  const fullPath = path.resolve(filePath);

  if (!fs.existsSync(fullPath)) {
    console.error(`❌ File not found: ${fullPath}`);
    return false;
  }

  let content = fs.readFileSync(fullPath, 'utf-8');
  const originalContent = content;

  // Extract existing imports
  const existingImports = extractExistingImports(content);

  // Find undefined identifiers that we can fix
  const undefinedIds = findUsedUndefined(content, existingImports);

  if (undefinedIds.size === 0) {
    console.log(`✅ ${filePath} — No missing imports detected.`);
    return true;
  }

  console.log(`🔧 ${filePath} — Found ${undefinedIds.size} missing imports:`);
  console.log(`   ${Array.from(undefinedIds).join(', ')}`);

  // Generate import statements
  const newImports = generateImportStatements(undefinedIds);

  // Insert after the last import, or at the top if no imports exist
  const lastImportIndex = content.lastIndexOf('import ');
  if (lastImportIndex !== -1) {
    const lineEnd = content.indexOf('\n', lastImportIndex);
    const insertPos = lineEnd !== -1 ? lineEnd + 1 : content.length;
    content = content.slice(0, insertPos) + '\n' + newImports.join('\n') + '\n' + content.slice(insertPos);
  } else {
    // No imports exist, add at very top
    content = newImports.join('\n') + '\n\n' + content;
  }

  // Backup original
  const backupPath = fullPath + '.backup';
  fs.writeFileSync(backupPath, originalContent);

  // Write fixed content
  fs.writeFileSync(fullPath, content);

  console.log(`✅ Fixed! Backup saved to: ${backupPath}`);
  console.log(`   Added imports:\n   ${newImports.join('\n   ')}`);

  return true;
}

// ===================== MAIN =====================

console.log('╔══════════════════════════════════════════════════╗');
console.log('║     Auto ESLint Import Fixer v1.0               ║');
console.log('╚══════════════════════════════════════════════════╝\n');

let successCount = 0;
FILES.forEach(file => {
  if (fixFile(file)) successCount++;
  console.log('');
});

console.log(`Done! Processed ${successCount}/${FILES.length} files.`);
console.log('\n⚠️  IMPORTANT: Review the changes before committing!');
console.log('   The mapping dictionary may need adjustment based on your project structure.');
console.log('\n📝 To customize imports, edit IMPORT_MAP at the top of this script.');
