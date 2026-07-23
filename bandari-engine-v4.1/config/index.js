const path = require('path');

module.exports = {
  PORT: process.env.PORT || 5200,
  DATA_DIR: path.join(__dirname, '..', 'data'),
  LEARNED_WORDS_FILE: path.join(__dirname, '..', 'data', 'learned_words.json'),
  CONTEXT_TTL_MS: 30 * 60 * 1000, // 30 دقیقه انقضای حافظه مکالمه
  LLM: {
    enabled: process.env.BANDARI_LLM_ENABLED === '1',
    // آداپتور LLM جدا تعریف شده تا وابستگی سخت به یک provider خاص نباشد
    provider: process.env.BANDARI_LLM_PROVIDER || 'none'
  }
};
