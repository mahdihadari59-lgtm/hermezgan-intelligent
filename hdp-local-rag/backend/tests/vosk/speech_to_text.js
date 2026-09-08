// speech_to_text.js
const path = require("path");
const os = require("os");
const fs = require("fs");

const { VoskModel, VoskRecognizer, setLogLevel } = require("./vosk_native");
const { assertModelValid } = require("./model_checker");
const { isVoskCompatible, convertToVoskWav, readPcmData } = require("./audio_utils");

const DEFAULT_MODEL_PATH =
  process.env.VOSK_MODEL_PATH ||
  "/data/data/com.termux/files/home/hormozgan-driver-pro121-backup/backend/vosk-model-fa";

const SAMPLE_RATE = 16000;

class SpeechToText {
  constructor(modelPath = DEFAULT_MODEL_PATH) {
    this.modelPath = modelPath;
    this.model = null;
  }

  load() {
    if (this.model) return this;
    assertModelValid(this.modelPath);
    setLogLevel(0);
    this.model = new VoskModel(this.modelPath);
    console.log("✅ Vosk model loaded successfully");
    console.log(`   مسیر: ${this.modelPath}`);
    return this;
  }

  transcribeFile(wavPath) {
    if (!this.model) this.load();

    let inputPath = wavPath;
    let tempFile = null;

    if (!isVoskCompatible(wavPath, SAMPLE_RATE)) {
      tempFile = path.join(os.tmpdir(), `vosk_tmp_${Date.now()}.wav`);
      convertToVoskWav(wavPath, tempFile, SAMPLE_RATE);
      inputPath = tempFile;
    }

    const recognizer = new VoskRecognizer(this.model, SAMPLE_RATE);
    try {
      const pcmData = readPcmData(inputPath);
      const CHUNK_SIZE = 4000;
      let fullText = [];

      for (let offset = 0; offset < pcmData.length; offset += CHUNK_SIZE) {
        const chunk = pcmData.subarray(offset, offset + CHUNK_SIZE);
        if (recognizer.acceptWaveform(chunk)) {
          const partial = recognizer.result();
          if (partial.text) fullText.push(partial.text);
        }
      }

      const final = recognizer.finalResult();
      if (final.text) fullText.push(final.text);

      return fullText.join(" ").trim();
    } finally {
      recognizer.free();
      if (tempFile && fs.existsSync(tempFile)) fs.unlinkSync(tempFile);
    }
  }

  createStreamRecognizer() {
    if (!this.model) this.load();
    return new VoskRecognizer(this.model, SAMPLE_RATE);
  }

  free() {
    if (this.model) {
      this.model.free();
      this.model = null;
    }
  }
}

module.exports = { SpeechToText, DEFAULT_MODEL_PATH, SAMPLE_RATE };
