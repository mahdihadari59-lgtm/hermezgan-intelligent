// vosk_native.js
// بایندینگ مستقیم به libvosk.so با استفاده از koffi (بدون واسطه‌ی vosk-koffi).

const fs = require("fs");
const koffi = require("koffi");

const LIBVOSK_PATH =
  process.env.LIBVOSK_PATH || `${process.env.HOME}/ai-system/lib/libvosk.so`;

if (!fs.existsSync(LIBVOSK_PATH)) {
  throw new Error(
    `libvosk.so پیدا نشد: ${LIBVOSK_PATH}\n` +
      `اول اسکریپت get_libvosk.sh رو اجرا کن تا این فایل ساخته بشه.`
  );
}

const lib = koffi.load(LIBVOSK_PATH);

const vosk_set_log_level = lib.func("void vosk_set_log_level(int log_level)");
const vosk_model_new = lib.func("void *vosk_model_new(const char *model_path)");
const vosk_model_free = lib.func("void vosk_model_free(void *model)");
const vosk_recognizer_new = lib.func(
  "void *vosk_recognizer_new(void *model, float sample_rate)"
);
const vosk_recognizer_free = lib.func("void vosk_recognizer_free(void *recognizer)");
const vosk_recognizer_accept_waveform = lib.func(
  "int vosk_recognizer_accept_waveform(void *recognizer, const uint8_t *data, int length)"
);
const vosk_recognizer_result = lib.func("const char *vosk_recognizer_result(void *recognizer)");
const vosk_recognizer_final_result = lib.func(
  "const char *vosk_recognizer_final_result(void *recognizer)"
);
const vosk_recognizer_partial_result = lib.func(
  "const char *vosk_recognizer_partial_result(void *recognizer)"
);

class VoskModel {
  constructor(modelPath) {
    if (!fs.existsSync(modelPath)) {
      throw new Error(`مسیر مدل پیدا نشد: ${modelPath}`);
    }
    this.handle = vosk_model_new(modelPath);
    if (!this.handle) {
      throw new Error("vosk_model_new مقدار null برگردوند — مدل لود نشد.");
    }
  }

  free() {
    if (this.handle) {
      vosk_model_free(this.handle);
      this.handle = null;
    }
  }
}

class VoskRecognizer {
  constructor(model, sampleRate = 16000) {
    this.handle = vosk_recognizer_new(model.handle, sampleRate);
    if (!this.handle) {
      throw new Error("vosk_recognizer_new مقدار null برگردوند.");
    }
  }

  acceptWaveform(data) {
    return vosk_recognizer_accept_waveform(this.handle, data, data.length) === 1;
  }

  result() {
    return JSON.parse(vosk_recognizer_result(this.handle));
  }

  finalResult() {
    return JSON.parse(vosk_recognizer_final_result(this.handle));
  }

  partialResult() {
    return JSON.parse(vosk_recognizer_partial_result(this.handle));
  }

  free() {
    if (this.handle) {
      vosk_recognizer_free(this.handle);
      this.handle = null;
    }
  }
}

function setLogLevel(level) {
  vosk_set_log_level(level);
}

module.exports = { VoskModel, VoskRecognizer, setLogLevel, LIBVOSK_PATH };
