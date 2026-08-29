class Security {
  constructor() {
    this.injectionPatterns = [
      /ignore (all|previous) (instructions|prompts)/i,
      /system prompt/i,
      /developer message/i,
      /bypass/i,
      /override/i,
      /do anything now/i,
      /reveal.*prompt/i,
      /prompt injection/i,
      /ignore.*policy/i,
      /فیلترها را نادیده بگیر/i,
      /دستورهای قبلی را نادیده بگیر/i,
      /پرامپت را نشان بده/i
    ];
  }

  sanitizeQuery(query) {
    return String(query ?? '')
      .replace(/[\u0000-\u001f\u007f]/g, ' ')
      .replace(/\u200c+/g, '‌')
      .replace(/\s+/g, ' ')
      .trim();
  }

  detectInjection(query) {
    const text = this.sanitizeQuery(query);
    const reasons = [];
    for (const pattern of this.injectionPatterns) {
      if (pattern.test(text)) reasons.push(pattern.toString());
    }
    return { blocked: reasons.length > 0, reasons };
  }

  validateContext(context = {}) {
    if (context == null || typeof context !== 'object' || Array.isArray(context)) {
      return { ok: false, error: 'invalid_context' };
    }
    const convId = context.conversationId;
    if (convId != null && (typeof convId !== 'string' || convId.length > 128)) {
      return { ok: false, error: 'invalid_conversation_id' };
    }
    const userId = context.userId;
    if (userId != null && (typeof userId !== 'string' || userId.length > 128)) {
      return { ok: false, error: 'invalid_user_id' };
    }
    const location = context.location || context.userLocation;
    if (location) {
      const lat = Number(location.latitude);
      const lng = Number(location.longitude);
      if (!Number.isFinite(lat) || !Number.isFinite(lng)) {
        return { ok: false, error: 'invalid_location' };
      }
    }
    return { ok: true };
  }
}
module.exports = Security;
