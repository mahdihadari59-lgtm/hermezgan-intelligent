class Authentication {
  constructor({ required = false, allowedKeys = [] } = {}) {
    this.required = required;
    this.allowedKeys = new Set(allowedKeys);
  }

  async authenticate(context = {}) {
    if (!this.required) return { ok: true, principal: { userId: context.userId || 'anon', role: 'guest' } };
    const key = context.apiKey || context.token;
    if (!key) return { ok: false, error: 'missing_credentials' };
    if (this.allowedKeys.size && !this.allowedKeys.has(key)) return { ok: false, error: 'unauthorized' };
    return { ok: true, principal: { userId: context.userId || 'authed-user', role: 'user' } };
  }
}
module.exports = Authentication;
