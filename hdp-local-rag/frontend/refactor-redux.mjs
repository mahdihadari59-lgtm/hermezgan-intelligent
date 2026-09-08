#!/usr/bin/env node
import fs from "fs";
import path from "path";

const ROOT = path.resolve(process.argv[2] || ".");
const FEATURES_DIR = path.join(ROOT, "src", "features");
const FEATURES_INDEX = path.join(FEATURES_DIR, "index.js");

function exists(p){ try { fs.accessSync(p); return true; } catch { return false; } }
function read(p){ return fs.readFileSync(p, "utf8"); }
function writeBackup(file, content){
  const old = read(file);
  if (old === content) return false;
  const backup = `${file}.bak_${Date.now()}`;
  fs.copyFileSync(file, backup);
  fs.writeFileSync(file, content, "utf8");
  console.log(`updated: ${path.relative(ROOT, file)}`);
  console.log(`backup : ${path.relative(ROOT, backup)}`);
  return true;
}
function walk(dir, out=[]){
  if (!exists(dir)) return out;
  for (const entry of fs.readdirSync(dir, {withFileTypes:true})) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      if (["node_modules",".git","dist","build","coverage",".next"].includes(entry.name)) continue;
      walk(full, out);
    } else if (entry.isFile()) out.push(full);
  }
  return out;
}
function isSliceFile(f){ return /Slice\.(js|jsx|ts|tsx|mjs|cjs)$/i.test(f) && !/index\./i.test(f); }
function sliceNameFromPath(f){ return path.relative(FEATURES_DIR, f).split(path.sep)[0]; }
function cap(s){ return s.charAt(0).toUpperCase() + s.slice(1); }

function parseExports(content){
  const set = new Set();
  for (const m of content.matchAll(/export\s+const\s*\{\s*([\s\S]*?)\s*\}\s*=\s*[^;]+;/g)) {
    m[1].split(",").map(s=>s.trim()).filter(Boolean).forEach(part=>{
      const mm = part.match(/^([\w$]+)\s+as\s+([\w$]+)$/);
      set.add(mm ? mm[2] : part);
    });
  }
  for (const m of content.matchAll(/export\s+(?:const|let|var|function|class)\s+([\w$]+)/g)) set.add(m[1]);
  return set;
}

function inferContext(file, content){
  const base = path.basename(file).toLowerCase();
  const checks = [
    ["chat", /chatpage|state\.chat\b|chatService|sendMessage|getChatHistory/i],
    ["map", /mappage|state\.map\b|mapService|setMapCenter|setZoom|setMarkers/i],
    ["camera", /camerapage|state\.camera\b|cameraService|setCameras|selectCamera/i],
    ["hotspot", /hotspot|state\.hotspot\b|hotspotService|setHotspots|selectHotspot/i],
    ["dashboard", /dashboard|state\.dashboard\b|setStats/i],
    ["auth", /login|logout|state\.auth\b|authService|setUser/i],
    ["ui", /state\.ui\b|toggleSidebar|setTheme|addToast|setNotification/i],
  ];
  for (const [ctx, rx] of checks) if (rx.test(base) || rx.test(content)) return ctx;
  return null;
}

function buildRename(context){
  const P = cap(context);
  return {
    setLoading: `set${P}Loading`,
    setError: `set${P}Error`,
    clearError: `clear${P}Error`,
    addNotification: "addToast",
  };
}

function rewriteStoreImportBlock(raw, renameMap){
  const m = raw.match(/import\s*\{\s*([\s\S]*?)\s*\}\s*from\s*(['"][^'"]+['"])\s*;?/);
  if (!m) return raw;
  const names = m[1].split(",").map(s=>s.trim()).filter(Boolean).map(p=>{
    const mm = p.match(/^([\w$]+)\s+as\s+([\w$]+)$/);
    return mm ? {imported:mm[1], local:mm[2]} : {imported:p, local:p};
  });
  const out = [];
  const seen = new Set();
  for (const item of names) {
    const newImported = renameMap[item.imported] || item.imported;
    const local = renameMap[item.imported] ? newImported : item.local;
    const key = `${newImported}::${local}`;
    if (seen.has(key)) continue;
    seen.add(key);
    out.push(local === newImported ? newImported : `${newImported} as ${local}`);
  }
  return `import {\n  ${out.join(",\n  ")}\n} from ${m[2]};`;
}

function parseStoreImports(content){
  const blocks = [];
  const re = /import\s*\{\s*([\s\S]*?)\s*\}\s*from\s*['"]([^'"]*\/store(?:\/index)?|\.{1,2}\/store(?:\/index)?)['"]\s*;?/g;
  let m;
  while ((m = re.exec(content)) !== null) {
    blocks.push({ raw: m[0] });
  }
  return blocks;
}

if (!exists(FEATURES_DIR)) {
  console.error(`[ERROR] Not found: ${FEATURES_DIR}`);
  process.exit(1);
}

const srcFiles = walk(path.join(ROOT, "src"));
const sliceFiles = srcFiles.filter(f => /src[\\/]+features[\\/]+.*Slice\./.test(f.replace(/\\/g, "/")) && isSliceFile(f));

if (!sliceFiles.length) {
  console.error("[ERROR] No slice files found.");
  process.exit(1);
}

const slices = sliceFiles.map(file => ({
  file,
  name: sliceNameFromPath(file),
  exports: parseExports(read(file)),
}));

const byName = new Map();
for (const s of slices) {
  for (const e of s.exports) {
    if (!byName.has(e)) byName.set(e, []);
    byName.get(e).push(s.name);
  }
}

let index = `// Auto-generated barrel. Do not edit by hand.\n`;
for (const s of slices) index += `export { default as ${s.name}Slice } from './${s.name}/${s.name}Slice';\n`;
index += `\n// Actions\n`;
for (const s of slices) {
  const pref = cap(s.name);
  const names = [...s.exports].sort();
  const lines = [];
  for (const n of names) {
    const conflict = (byName.get(n) || []).length > 1 || ["setLoading","setError","clearError"].includes(n);
    if (!conflict) {
      lines.push(`  ${n},`);
    } else {
      let alias = n;
      if (n === "setLoading") alias = `set${pref}Loading`;
      else if (n === "setError") alias = `set${pref}Error`;
      else if (n === "clearError") alias = `clear${pref}Error`;
      else if (n === "addNotification" && s.name === "ui") alias = "addNotification";
      else if (/^set[A-Z]/.test(n)) alias = `${n}${pref}`;
      lines.push(`  ${n} as ${alias},`);
    }
  }
  if (s.name === "ui" && s.exports.has("addToast")) lines.push(`  addToast as addNotification,`);
  if (lines.length) index += `export {\n${lines.join("\n")}\n} from './${s.name}/${s.name}Slice';\n\n`;
}

fs.writeFileSync(FEATURES_INDEX, index, "utf8");
console.log(`updated: ${path.relative(ROOT, FEATURES_INDEX)}`);

for (const file of srcFiles) {
  if (!file.startsWith(path.join(ROOT, "src"))) continue;
  const content = read(file);
  const blocks = parseStoreImports(content);
  if (!blocks.length) continue;
  const context = inferContext(file, content);
  const renameMap = buildRename(context || "ui");
  let out = content;
  let changed = false;

  for (const block of blocks) {
    const newBlock = rewriteStoreImportBlock(block.raw, renameMap);
    if (newBlock !== block.raw) {
      out = out.replace(block.raw, newBlock);
      changed = true;
    }
  }

  if (changed) {
    const backup = `${file}.bak_${Date.now()}`;
    fs.copyFileSync(file, backup);
    fs.writeFileSync(file, out, "utf8");
    console.log(`updated: ${path.relative(ROOT, file)}`);
  }
}
