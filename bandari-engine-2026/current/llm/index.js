```javascript
/**
 * services/llm_translator.js
 * HDP LLM Translator Service
 * 
 * Translates between Persian and Bandari (Hormozgan dialect)
 * Supports multiple providers: llama.cpp, OpenAI, Ollama
 */

const config = require('../config');
const logger = require('../utils/logger');

class LLMTranslator {
  constructor() {
    // Configuration
    this.enabled = config.LLM?.enabled ?? (process.env.BANDARI_LLM_ENABLED === '1');
    this.provider = config.LLM?.provider || process.env.LLM_PROVIDER || 'llama.cpp';
    this.model = config.LLM?.model || process.env.LLM_MODEL || 'Qwen2.5-1.5B-Instruct-Q4_K_M';
    this.apiUrl = config.LLM?.apiUrl || process.env.LLM_API_URL || 'http://127.0.0.1:8080/v1/chat/completions';
    this.apiKey = config.LLM?.apiKey || process.env.LLM_API_KEY || '';
    this.temperature = Number(config.LLM?.temperature || process.env.LLM_TEMPERATURE || 0.3);
    this.maxTokens = Number(config.LLM?.maxTokens || process.env.LLM_MAX_TOKENS || 256);
    this.timeout = Number(config.LLM?.timeout || process.env.LLM_TIMEOUT || 30000);

    // Statistics
    this.stats = {
      totalRequests: 0,
      successfulRequests: 0,
      failedRequests: 0,
      avgResponseTime: 0,
      lastRequestTime: null
    };

    this._logConfiguration();

    if (this.enabled) {
      logger.success('✅ LLM Translator enabled');
    } else {
      logger.warn('⚠️ LLM Translator disabled');
    }
  }

  _logConfiguration() {
    logger.info('┌─────────────────────────────────────────────');
    logger.info('│ LLM Configuration');
    logger.info(`│ Provider    : ${this.provider}`);
    logger.info(`│ Model       : ${this.model}`);
    logger.info(`│ API URL     : ${this.apiUrl}`);
    logger.info(`│ API Key     : ${this.apiKey ? 'SET' : 'NONE'}`);
    logger.info(`│ Temperature : ${this.temperature}`);
    logger.info(`│ Max Tokens  : ${this.maxTokens}`);
    logger.info(`│ Timeout     : ${this.timeout}ms`);
    logger.info(`│ Enabled     : ${this.enabled}`);
    logger.info('└─────────────────────────────────────────────');
  }

  _headers() {
    const headers = {
      'Content-Type': 'application/json'
    };

    if (this.apiKey) {
      headers.Authorization = `Bearer ${this.apiKey}`;
    }

    return headers;
  }

  /**
   * Translate text from Persian to Bandari dialect
   * 
   * @param {string} text - Text to translate
   * @param {Array} contextHistory - Previous translations for context
   * @returns {Promise<Object>} Translation result
   */
  async translate(text, contextHistory = []) {
    if (!this.enabled) {
      return {
        used: false,
        reason: 'llm_disabled'
      };
    }

    if (!text || typeof text !== 'string') {
      return {
        used: false,
        success: false,
        reason: 'invalid_text',
        error: 'Text must be a non-empty string'
      };
    }

    const startTime = Date.now();
    this.stats.totalRequests++;

    try {
      const translation = await this._callProvider(text, contextHistory);
      const responseTime = Date.now() - startTime;

      this.stats.successfulRequests++;
      this.stats.avgResponseTime = (
        (this.stats.avgResponseTime * (this.stats.successfulRequests - 1) + responseTime) /
        this.stats.successfulRequests
      );
      this.stats.lastRequestTime = new Date().toISOString();

      return {
        used: true,
        success: true,
        provider: this.provider,
        model: this.model,
        translation,
        confidence: 0.85,
        responseTime
      };

    } catch (err) {
      this.stats.failedRequests++;
      logger.error('❌ LLM Error:', err.message);

      return {
        used: false,
        success: false,
        fallback: true,
        reason: 'provider_error',
        error: err.message,
        responseTime: Date.now() - startTime
      };
    }
  }

  /**
   * Health check for LLM service
   * 
   * @returns {Promise<boolean>} True if healthy
   */
  async healthCheck() {
    try {
      // Build health check URL
      let url = this.apiUrl;
      if (url.endsWith('/v1/chat/completions')) {
        url = url.replace('/v1/chat/completions', '/health');
      } else if (url.endsWith('/api/generate')) {
        // Ollama health check
        url = url.replace('/api/generate', '/api/tags');
      }

      const response = await fetch(url, {
        method: 'GET',
        headers: this._headers(),
        signal: AbortSignal.timeout(5000)
      });

      return response.ok;
    } catch (err) {
      logger.warn(`Health Check Failed: ${err.message}`);
      return false;
    }
  }

  /**
   * Get system prompt for translation
   * 
   * @returns {string} System prompt
   */
  _systemPrompt() {
    return `شما مترجم حرفه‌ای گویش بندری هرمزگان هستید.

قوانین:
1- فقط ترجمه را برگردان.
2- توضیح اضافه ننویس.
3- واژه‌های محلی بندری استفاده کن.
4- اگر معادل وجود نداشت همان فارسی را نگه دار.
5- خروجی فقط یک جمله باشد.

نمونه ترجمه‌ها:
- "سلام چطوری؟" → "سَلَام، چِطُری؟"
- "به بیمارستان می‌روم" → "دَارُم مِری بِیمارِستون"
- "کجا هستی؟" → "کُجا هِستی؟"
- "خسته نباشی" → "خَستِه نَباشی"
- "مرسی" → "مَرسی"`;
  }

  /**
   * Call LLM provider
   * 
   * @param {string} text - Text to translate
   * @param {Array} contextHistory - Context history
   * @returns {Promise<string>} Translated text
   */
  async _callProvider(text, contextHistory = []) {
    const messages = [
      {
        role: 'system',
        content: this._systemPrompt()
      }
    ];

    // Add context history (last 6 exchanges)
    if (Array.isArray(contextHistory) && contextHistory.length > 0) {
      const recent = contextHistory.slice(-6);
      for (const item of recent) {
        if (item.text) {
          messages.push({
            role: 'user',
            content: item.text
          });
        }
        if (item.translation) {
          messages.push({
            role: 'assistant',
            content: item.translation
          });
        }
      }
    }

    messages.push({
      role: 'user',
      content: text
    });

    const body = {
      model: this.model,
      messages,
      temperature: this.temperature,
      max_tokens: this.maxTokens,
      stream: false
    };

    logger.debug(`➡ POST ${this.apiUrl}`);

    const controller = new AbortController();
    const timeout = setTimeout(() => {
      controller.abort();
    }, this.timeout);

    try {
      const response = await fetch(this.apiUrl, {
        method: 'POST',
        headers: this._headers(),
        body: JSON.stringify(body),
        signal: controller.signal
      });

      clearTimeout(timeout);

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`HTTP ${response.status}: ${errorText}`);
      }

      const data = await response.json();
      return this._extractResponse(data);

    } catch (err) {
      clearTimeout(timeout);
      throw err;
    }
  }

  /**
   * Extract translation from provider response
   * 
   * @param {Object} data - Provider response
   * @returns {string} Extracted translation
   */
  _extractResponse(data) {
    // OpenAI / llama.cpp / vLLM
    if (data.choices && data.choices.length > 0) {
      const choice = data.choices[0];
      if (choice.message && choice.message.content) {
        return choice.message.content.trim();
      }
      if (choice.text) {
        return choice.text.trim();
      }
    }

    // Ollama
    if (data.message && data.message.content) {
      return data.message.content.trim();
    }

    // llama.cpp completion endpoint
    if (data.content) {
      return data.content.trim();
    }

    // Generic fallback
    if (data.response) {
      return data.response.trim();
    }

    // Try to find any string in response
    if (typeof data === 'string') {
      return data.trim();
    }

    throw new Error(
      `Invalid LLM response: ${JSON.stringify(data).substring(0, 200)}`
    );
  }

  /**
   * Get statistics
   * 
   * @returns {Object} Statistics
   */
  getStats() {
    return {
      ...this.stats,
      successRate: this.stats.totalRequests > 0
        ? (this.stats.successfulRequests / this.stats.totalRequests * 100).toFixed(2) + '%'
        : '0%'
    };
  }

  /**
   * Reset statistics
   */
  resetStats() {
    this.stats = {
      totalRequests: 0,
      successfulRequests: 0,
      failedRequests: 0,
      avgResponseTime: 0,
      lastRequestTime: null
    };
  }
}

// Export singleton
module.exports = new LLMTranslator();
```
