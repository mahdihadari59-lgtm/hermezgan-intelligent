const config = require('../config');
const logger = require('../utils/logger');

/**
 * لایه ۸: مترجم هوشمند (LLM Translator)
 * این لایه فقط زمانی فعال می‌شود که دیکشنری/RAG جواب مطمئنی نداشته باشند.
 * به‌صورت پیش‌فرض غیرفعال است (config.LLM.enabled=false) تا سرویس بدون
 * کلید API یا اتصال شبکه هم کار کند. آداپتور واقعی (مثلاً تماس با Claude API)
 * را می‌توان بعداً در متد `_callProvider` پیاده‌سازی کرد.
 */
class LLMTranslator {
  constructor() {
    this.enabled = config.LLM.enabled;
    this.provider = config.LLM.provider;
    if (this.enabled) {
      logger.info(`LLM Translator فعال است (provider: ${this.provider})`);
    } else {
      logger.info('LLM Translator غیرفعال است (fallback به دیکشنری/RAG)');
    }
  }

  async translate(text, contextHistory = []) {
    if (!this.enabled) {
      return { used: false, reason: 'llm_disabled' };
    }
    try {
      const result = await this._callProvider(text, contextHistory);
      return { used: true, translation: result, confidence: 0.85 };
    } catch (e) {
      logger.warn('LLM Translator خطا داد، fallback به دیکشنری:', e.message);
      return { used: false, reason: 'provider_error', error: e.message };
    }
  }

  async _callProvider(text, contextHistory) {
    // TODO: اتصال واقعی به provider (مثلا Anthropic API) اینجا پیاده‌سازی شود.
    // عمداً هنوز پیاده‌سازی نشده تا سرویس بدون کلید/شبکه هم قابل اجرا بماند.
    throw new Error('provider not configured');
  }
}

module.exports = LLMTranslator;
