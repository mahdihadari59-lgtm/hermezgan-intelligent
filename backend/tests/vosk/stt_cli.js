#!/usr/bin/env node
// stt_cli.js — نسخه‌ی production-friendly test_vosk.js.
// ورودی: مسیر فایل wav. خروجی: فقط یک خط JSON روی stdout.

const { SpeechToText, DEFAULT_MODEL_PATH } = require("./speech_to_text");

function main() {
  const wavPath = process.argv[2];

  if (!wavPath) {
    process.stdout.write(JSON.stringify({ success: false, error: "مسیر فایل wav داده نشده." }) + "\n");
    process.exit(1);
  }

  try {
    const modelPath = process.env.VOSK_MODEL_PATH || DEFAULT_MODEL_PATH;
    const stt = new SpeechToText(modelPath);
    stt.load();
    const text = stt.transcribeFile(wavPath);
    stt.free();
    process.stdout.write(JSON.stringify({ success: true, text }) + "\n");
  } catch (err) {
    process.stdout.write(JSON.stringify({ success: false, error: err.message }) + "\n");
    process.exit(1);
  }
}

main();
