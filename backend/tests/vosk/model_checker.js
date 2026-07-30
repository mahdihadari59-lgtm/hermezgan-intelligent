// model_checker.js
const fs = require("fs");
const path = require("path");

const REQUIRED_FILES = ["am/final.mdl", "conf/model.conf", "graph/Gr.fst"];
const OPTIONAL_FILES = ["ivector/final.ie", "rescore/G.carpa", "rnnlm/final.raw"];

function checkModel(modelPath) {
  if (!fs.existsSync(modelPath)) {
    return {
      ok: false,
      missing: REQUIRED_FILES,
      optionalMissing: OPTIONAL_FILES,
      sizeBytes: 0,
      error: `مسیر مدل اصلاً وجود نداره: ${modelPath}`,
    };
  }

  const missing = REQUIRED_FILES.filter((f) => !fs.existsSync(path.join(modelPath, f)));
  const optionalMissing = OPTIONAL_FILES.filter((f) => !fs.existsSync(path.join(modelPath, f)));

  let sizeBytes = 0;
  try {
    sizeBytes = getDirSize(modelPath);
  } catch (e) {}

  return {
    ok: missing.length === 0,
    missing,
    optionalMissing,
    sizeBytes,
    error: missing.length ? `فایل‌های ضروری موجود نیستن: ${missing.join(", ")}` : null,
  };
}

function getDirSize(dirPath) {
  let total = 0;
  const entries = fs.readdirSync(dirPath, { withFileTypes: true });
  for (const entry of entries) {
    const fullPath = path.join(dirPath, entry.name);
    if (entry.isDirectory()) {
      total += getDirSize(fullPath);
    } else {
      total += fs.statSync(fullPath).size;
    }
  }
  return total;
}

function formatBytes(bytes) {
  if (bytes === 0) return "0 B";
  const units = ["B", "KB", "MB", "GB"];
  const i = Math.floor(Math.log(bytes) / Math.log(1024));
  return `${(bytes / Math.pow(1024, i)).toFixed(2)} ${units[i]}`;
}

function assertModelValid(modelPath) {
  const result = checkModel(modelPath);
  if (!result.ok) {
    throw new Error(`مدل Vosk نامعتبره (${modelPath}): ${result.error}`);
  }
  console.log(
    `✅ مدل معتبره — حجم: ${formatBytes(result.sizeBytes)}` +
      (result.optionalMissing.length ? ` (بدون: ${result.optionalMissing.join(", ")})` : "")
  );
  return result;
}

module.exports = { checkModel, assertModelValid, formatBytes, REQUIRED_FILES, OPTIONAL_FILES };
