class ContextManager {
  constructor(store = null) {
    this.store = store;
    this.ttl = 3600;
  }

  _key(conversationId) { return `hdp:v1:ctx:${conversationId}`; }

  _safeParse(value, fallback) {
    if (!value) return fallback;
    try { return JSON.parse(value); } catch (_) { return fallback; }
  }

  async load(conversationId, fallback = {}) {
    if (!this.store || !conversationId) return fallback;
    const key = this._key(conversationId);
    if (typeof this.store.get === 'function') {
      const raw = await this.store.get(key);
      return this._safeParse(raw, fallback);
    }
    return fallback;
  }

  async save(conversationId, context) {
    if (!this.store || !conversationId) return;
    const key = this._key(conversationId);
    const value = JSON.stringify(context);
    if (typeof this.store.setEx === 'function') return this.store.setEx(key, this.ttl, value);
    if (typeof this.store.setex === 'function') return this.store.setex(key, this.ttl, value);
    if (typeof this.store.set === 'function') return this.store.set(key, value);
  }
}
module.exports = ContextManager;
