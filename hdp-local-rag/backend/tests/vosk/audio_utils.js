// audio_utils.js
// ابزارهای صوتی سبک، بدون هیچ وابستگی npm — فقط fs/child_process از stdlib.

const fs = require("fs");
const { spawnSync } = require("child_process");

function readWavHeader(filePath) {
  const fd = fs.openSync(filePath, "r");
  const buffer = Buffer.alloc(44);
  fs.readSync(fd, buffer, 0, 44, 0);
  fs.closeSync(fd);

  if (buffer.toString("ascii", 0, 4) !== "RIFF" || buffer.toString("ascii", 8, 12) !== "WAVE") {
    throw new Error("فایل یک WAV معتبر (RIFF/WAVE) نیست.");
  }

  return {
    audioFormat: buffer.readUInt16LE(20),
    channels: buffer.readUInt16LE(22),
    sampleRate: buffer.readUInt32LE(24),
    byteRate: buffer.readUInt32LE(28),
    bitsPerSample: buffer.readUInt16LE(34),
  };
}

function isVoskCompatible(filePath, expectedSampleRate = 16000) {
  const header = readWavHeader(filePath);
  return (
    header.audioFormat === 1 &&
    header.channels === 1 &&
    header.bitsPerSample === 16 &&
    header.sampleRate === expectedSampleRate
  );
}

function convertToVoskWav(inputPath, outputPath, sampleRate = 16000) {
  const result = spawnSync(
    "ffmpeg",
    ["-y", "-i", inputPath, "-ar", String(sampleRate), "-ac", "1", "-sample_fmt", "s16", outputPath],
    { encoding: "utf-8" }
  );

  if (result.status !== 0) {
    throw new Error(
      `تبدیل با ffmpeg شکست خورد (کد ${result.status}):\n${result.stderr}\n` +
        `اگه ffmpeg نصب نیست: pkg install ffmpeg`
    );
  }

  return outputPath;
}

function readPcmData(wavFilePath) {
  const full = fs.readFileSync(wavFilePath);
  return full.subarray(44);
}

module.exports = { readWavHeader, isVoskCompatible, convertToVoskWav, readPcmData };
