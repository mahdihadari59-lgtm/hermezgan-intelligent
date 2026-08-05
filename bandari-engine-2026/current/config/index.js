const path = require('path');
require('dotenv').config();

module.exports = {
  PORT: process.env.PORT || 5200,
  DATA_DIR: path.join(__dirname, '..', 'data'),
  LEARNED_WORDS_FILE: path.join(__dirname, '..', 'data', 'learned_words.json'),
  CONTEXT_TTL_MS: 30 * 60 * 1000,
  LLM: {
    enabled: process.env.BANDARI_LLM_ENABLED === '1' || !!process.env.LLM_API_URL,
    provider: process.env.LLM_PROVIDER || 'llama.cpp',
    apiUrl: process.env.LLM_API_URL || 'http://127.0.0.1:8080/v1/chat/completions',
    model: process.env.LLM_MODEL || 'Qwen2.5-1.5B-Instruct-Q4_K_M',
    apiKey: process.env.LLM_API_KEY || '',
    timeout: parseInt(process.env.LLM_TIMEOUT || '30000', 10),
    temperature: parseFloat(process.env.LLM_TEMPERATURE || '0.3'),
    maxTokens: parseInt(process.env.LLM_MAX_TOKENS || '256', 10)
  }
};
