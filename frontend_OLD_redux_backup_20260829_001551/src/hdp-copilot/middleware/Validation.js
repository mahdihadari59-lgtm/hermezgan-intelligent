class Validation {
  constructor({ minLength = 1, maxLength = 500 } = {}) {
    this.minLength = minLength;
    this.maxLength = maxLength;
  }

  validate(query, context = {}) {
    if (typeof query !== 'string') return { ok: false, error: 'query_must_be_string' };
    const sanitized = String(query).replace(/[\u0000-\u001f\u007f]/g, ' ').replace(/\s+/g, ' ').trim();
    if (!sanitized) return { ok: false, error: 'empty_query' };
    if (sanitized.length < this.minLength) return { ok: false, error: 'query_too_short' };
    if (sanitized.length > this.maxLength) return { ok: false, error: 'query_too_long' };
    if (context != null && typeof context !== 'object') return { ok: false, error: 'invalid_context' };
    return { ok: true, query: sanitized };
  }
}
module.exports = Validation;
