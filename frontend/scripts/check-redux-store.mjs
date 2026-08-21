#!/usr/bin/env node
/**
 * check-redux-store.mjs
 *
 * Usage:
 *   node scripts/check-redux-store.mjs [project-root]            # report only
 *   node scripts/check-redux-store.mjs [project-root] --fix      # report + safe fixes
 *
 * Example:
 *   node scripts/check-redux-store.mjs . --fix
 */

import fs from "fs";
import path from "path";

const args = process.argv.slice(2);
const rootArg = args.find((a) => a !== "--fix") || ".";
const FIX = args.includes("--fix");
const ROOT = path.resolve(rootArg);

const exts = new Set([".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs"]);

function exists(p) {
  try {
    fs.accessSync(p);
    return true;
  } catch {
    return false;
  }
}

function readFile(p) {
  return fs.readFileSync(p, "utf8");
}

function walk(dir, out = []) {
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      if (entry.name === "node_modules" || entry.name === ".git" || entry.name === "dist" || entry.name === "build") continue;
      walk(full, out);
    } else if (entry.isFile()) {
      if (exts.has(path.extname(entry.name))) out.push(full);
    }
  }
  return out;
}

function findFirst(paths) {
  for (const p of paths) {
    if (exists(p)) return p;
  }
  return null;
}

function splitTopLevelCSV(text) {
  return text
    .split(",")
    .map((s) => s.trim())
    .filter(Boolean);
}

function parseExportList(listText) {
  const out = new Set();
  for (const part of splitTopLevelCSV(listText)) {
    // "a as b" -> exported name is b
    const m = part.match(/^([\w$]+)\s+as\s+([\w$]+)$/);
    if (m) {
      out.add(m[2]);
    } else {
      out.add(part);
    }
  }
  return out;
}

function extractExports(fileContent) {
  const names = new Set();

  // export { a, b as c } from './x';
  for (const m of fileContent.matchAll(/export\s*\{\s*([^}]+)\s*\}\s*(?:from\s*['"][^'"]+['"])?\s*;/g)) {
    for (const n of parseExportList(m[1])) names.add(n);
  }

  // export const foo = ...
  for (const m of fileContent.matchAll(/export\s+(?:const|let|var|function|class)\s+([\w$]+)/g)) {
    names.add(m[1]);
  }

  // export const { a, b as c } = slice.actions;
  // (RTK pattern)
  for (const m of fileContent.matchAll(/export\s+const\s*\{\s*([^}]+)\s*\}\s*=\s*[^;]+;/g)) {
    for (const n of parseExportList(m[1])) names.add(n);
  }

  return names;
}

function extractImportsFromStore(fileContent) {
  const imported = new Set();

  // import { a, b as c } from '../store'
  for (const m of fileContent.matchAll(/import\s*\{\s*([^}]+)\s*\}\s*from\s*['"]([^'"]+)['"]/g)) {
    const spec = m[2];
    if (!/\/store(?:\/index)?$|^\.{1,2}\/store(?:\/index)?$/.test(spec) && !/\/store(?:\/index)?/.test(spec)) continue;
    for (const n of parseExportList(m[1])) imported.add(n);
  }

  return imported;
}

function getFileRel(p) {
  return path.relative(ROOT, p).replaceAll(path.sep, "/");
}

function findSliceFile(baseName) {
  const candidates = walk(ROOT).filter((f) => path.basename(f).toLowerCase() === `${baseName.toLowerCase()}.js`);
  return candidates[0] || null;
}

function findStoreEntry() {
  const candidates = [
    path.join(ROOT, "src", "store", "index.js"),
    path.join(ROOT, "src", "store.js"),
    path.join(ROOT, "store", "index.js"),
    path.join(ROOT, "store.js"),
    path.join(ROOT, "src", "app", "store", "index.js"),
  ];
  return findFirst(candidates);
}

function safeAppendAliases(storeFile, aliases) {
  const content = readFile(storeFile);

  const linesToAdd = [];
  for (const alias of aliases) {
    if (alias === "addNotification") {
      if (/export\s*\{\s*addToast\s+as\s+addNotification\s*\}/.test(content)) continue;
      if (/\baddToast\b/.test(content)) {
        linesToAdd.push(`export { addToast as addNotification } from "./uiSlice";`);
      }
    }

    if (alias === "setSessionId") {
      if (/export\s*\{\s*setSessionId\s*\}/.test(content) || /export\s*\{\s*setSessionId\s+as\s+setSessionId\s*\}/.test(content)) continue;
      if (/\bsetSessionId\b/.test(content)) continue; // already present somewhere
      linesToAdd.push(`export { setSessionId } from "./chatSlice";`);
    }

    if (alias === "setError") {
      if (/export\s*\{\s*setError\s*\}/.test(content)) continue;
      if (/\bsetError\b/.test(content)) continue;
      // only safe if uiSlice exports it
      const uiSlice = findSliceFile("uiSlice");
      if (uiSlice) {
        const uiExports = extractExports(readFile(uiSlice));
        if (uiExports.has("setError")) {
          linesToAdd.push(`export { setError } from "./uiSlice";`);
        }
      }
    }

    if (alias === "clearError") {
      if (/export\s*\{\s*clearError\s*\}/.test(content)) continue;
      if (/\bclearError\b/.test(content)) continue;
      const uiSlice = findSliceFile("uiSlice");
      if (uiSlice) {
        const uiExports = extractExports(readFile(uiSlice));
        if (uiExports.has("clearError")) {
          linesToAdd.push(`export { clearError } from "./uiSlice";`);
        }
      }
    }
  }

  if (!linesToAdd.length) return false;

  const backup = `${storeFile}.bak_${Date.now()}`;
  fs.copyFileSync(storeFile, backup);

  const appendBlock = `\n\n// --- auto-added compatibility exports ---\n${linesToAdd.join("\n")}\n`;
  fs.writeFileSync(storeFile, content.replace(/\s*$/, "") + appendBlock, "utf8");

  console.log(`\n[FIX] updated: ${getFileRel(storeFile)}`);
  console.log(`[FIX] backup : ${getFileRel(backup)}`);
  console.log(`[FIX] added   :\n  - ${linesToAdd.join("\n  - ")}`);
  return true;
}

const storeFile = findStoreEntry();
if (!storeFile) {
  console.error("[ERROR] Store entry not found.");
  console.error("Searched for:");
  console.error("  - src/store/index.js");
  console.error("  - src/store.js");
  console.error("  - store/index.js");
  console.error("  - store.js");
  process.exit(1);
}

const allFiles = walk(ROOT);
const storeDir = path.dirname(storeFile);
const storeExports = extractExports(readFile(storeFile));

const sliceFiles = allFiles.filter((f) => /[\\/](uiSlice|chatSlice|mapSlice|cameraSlice|hotspotSlice|authSlice|dashboardSlice)\.(js|jsx|ts|tsx)$/i.test(f));
const sliceExports = new Map();

for (const f of sliceFiles) {
  sliceExports.set(path.basename(f, path.extname(f)), extractExports(readFile(f)));
}

const importReport = [];
const missingSummary = new Map();

for (const file of allFiles) {
  if (path.resolve(file) === path.resolve(storeFile)) continue;

  const content = readFile(file);
  const imported = extractImportsFromStore(content);
  if (!imported.size) continue;

  const missing = [...imported].filter((name) => !storeExports.has(name));
  if (missing.length) {
    importReport.push({
      file,
      missing,
    });

    for (const name of missing) {
      missingSummary.set(name, (missingSummary.get(name) || 0) + 1);
    }
  }
}

console.log(`\n[STORE] ${getFileRel(storeFile)}`);
console.log(`[EXPORTS] ${[...storeExports].sort().join(", ") || "(none)"}`);

if (!importReport.length) {
  console.log("\n[OK] No missing named exports detected for imports from store.");
  process.exit(0);
}

console.log("\n[ISSUES]");
for (const item of importReport) {
  console.log(`- ${getFileRel(item.file)}`);
  console.log(`  missing: ${item.missing.join(", ")}`);
}

console.log("\n[SUMMARY]");
for (const [name, count] of [...missingSummary.entries()].sort((a, b) => b[1] - a[1])) {
  console.log(`- ${name}: referenced in ${count} file(s) but not exported from store`);
}

console.log("\n[LIKELY FIXES]");
if (missingSummary.has("addNotification")) {
  if (storeExports.has("addToast")) {
    console.log("- addNotification -> addToast (safe alias)");
  } else {
    console.log("- addNotification: no addToast export found; inspect uiSlice");
  }
}
if (missingSummary.has("setSessionId")) {
  if ([...sliceExports.values()].some((s) => s.has("setSessionId"))) {
    console.log("- setSessionId exists in a slice; re-export from store");
  } else {
    console.log("- setSessionId: not found in slices; add it to chatSlice or remove the import");
  }
}
if (missingSummary.has("setError") || missingSummary.has("clearError")) {
  const uiSlice = sliceExports.get("uiSlice");
  if (uiSlice?.has("setError") || uiSlice?.has("clearError")) {
    console.log("- setError / clearError exist in uiSlice; re-export them from store");
  } else {
    console.log("- setError / clearError: not found in uiSlice; use slice-specific errors or add shared ui error actions");
  }
}

if (FIX) {
  const aliasesToTry = [...missingSummary.keys()];
  const changed = safeAppendAliases(storeFile, aliasesToTry);
  if (!changed) {
    console.log("\n[FIX] No safe automatic alias was applied.");
  }
}
