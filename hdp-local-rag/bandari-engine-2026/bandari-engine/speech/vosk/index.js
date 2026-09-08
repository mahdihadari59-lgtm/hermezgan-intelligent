// index.js — نقطه ورود ماژول vosk (STT)
const { SpeechToText, DEFAULT_MODEL_PATH, SAMPLE_RATE } = require("./speech_to_text");
const { checkModel, assertModelValid } = require("./model_checker");
const { VoskModel, VoskRecognizer, setLogLevel } = require("./vosk_native");
const audioUtils = require("./audio_utils");

let _instance = null;
function getInstance(modelPath) {
  if (!_instance) _instance = new SpeechToText(modelPath);
  return _instance;
}

module.exports = {
  SpeechToText,
  getInstance,
  DEFAULT_MODEL_PATH,
  SAMPLE_RATE,
  checkModel,
  assertModelValid,
  VoskModel,
  VoskRecognizer,
  setLogLevel,
  audioUtils,
};
