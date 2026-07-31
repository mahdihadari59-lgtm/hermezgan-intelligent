// test_vosk.js
// استفاده: node test_vosk.js [sample.wav]

const path = require("path");
const { SpeechToText, DEFAULT_MODEL_PATH } = require("./speech_to_text");
const { assertModelValid } = require("./model_checker");

function main() {
  const wavArg = process.argv[2];

  console.log("== ۱. اعتبارسنجی مدل ==");
  assertModelValid(DEFAULT_MODEL_PATH);

  console.log("\n== ۲. لود مدل ==");
  const stt = new SpeechToText();
  stt.load();

  if (!wavArg) {
    console.log("\nهیچ فایل WAV داده نشده. فقط تست لود مدل انجام شد. ✅");
    console.log("برای تست کامل: node test_vosk.js /path/to/sample.wav");
    return;
  }

  console.log(`\n== ۳. تبدیل فایل به متن: ${wavArg} ==`);
  const start = Date.now();
  const text = stt.transcribeFile(wavArg);
  const elapsed = ((Date.now() - start) / 1000).toFixed(2);

  console.log("\n--- نتیجه ---");
  console.log(text || "(متنی تشخیص داده نشد)");
  console.log(`--- زمان پردازش: ${elapsed} ثانیه ---`);

  stt.free();
}

try {
  main();
} catch (err) {
  console.error("❌ خطا:", err.message);
  process.exit(1);
}
