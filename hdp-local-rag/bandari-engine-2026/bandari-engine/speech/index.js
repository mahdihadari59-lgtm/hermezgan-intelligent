'use strict';

const vosk = require('./vosk');
const { ElevenLabsTTS } = require('./elevenlabs');

let ttsInstance = null;

function getTTS(options = {}) {
  if (!ttsInstance) {
    ttsInstance = new ElevenLabsTTS(options);
  }
  return ttsInstance;
}

async function transcribe(audioFile, options = {}) {
  const stt = vosk.getInstance(options.modelPath);
  return stt.transcribeFile(audioFile);
}

module.exports = {
  vosk,
  transcribe,
  getTTS,
  ElevenLabsTTS
};
