#!/usr/bin/env node
import fs from "fs";
import path from "path";

const root = path.resolve(process.argv[2] || ".");
const featuresDir = path.join(root, "src", "features");
const indexFile = path.join(featuresDir, "index.js");

function exists(p) {
  try {
    fs.accessSync(p);
    return true;
  } catch {
    return false;
  }
}

function walkFiles(dir) {
  const out = [];
  if (!exists(dir)) return out;

  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      if (entry.name === "node_modules" || entry.name === ".git" || entry.name === "build" || entry.name === "dist") continue;
      out.push(...walkFiles(full));
    } else if (entry.isFile()) {
      out.push(full);
    }
  }
  return out;
}

function isSliceFile(file) {
  const base = path.basename(file);
  if (base === "index.js" || base === "rootReducer.js" || base === "store.js") return false;
  return /\.(js|jsx|ts|tsx|mjs|cjs)$/.test(base) && /slice/i.test(base);
}

if (!exists(featuresDir)) {
  console.error(`[ERROR] features dir not found: ${featuresDir}`);
  process.exit(1);
}

const files = walkFiles(featuresDir).filter(isSliceFile);
if (!files.length) {
  console.error(`[ERROR] no slice files found inside: ${featuresDir}`);
  process.exit(1);
}

const exportsBlock = files
  .map((file) => {
    const rel = "./" + path.relative(featuresDir, file).replace(/\\/g, "/").replace(/\.(js|jsx|ts|tsx|mjs|cjs)$/, "");
    return `export * from "${rel}";`;
  })
  .join("\n");

const content =
`// Auto-generated barrel for feature slices.
// Re-export named actions/selectors from every slice.
// Do not add default exports here unless strictly required.

${exportsBlock}
`;

if (exists(indexFile)) {
  const backup = `${indexFile}.bak_${Date.now()}`;
  fs.copyFileSync(indexFile, backup);
  fs.writeFileSync(indexFile, content, "utf8");
  console.log(`[OK] updated: ${path.relative(root, indexFile)}`);
  console.log(`[OK] backup : ${path.relative(root, backup)}`);
} else {
  fs.writeFileSync(indexFile, content, "utf8");
  console.log(`[OK] created: ${path.relative(root, indexFile)}`);
}

console.log("\n[EXPORTS]");
for (const file of files) {
  console.log(`- ${path.relative(root, file)}`);
}
