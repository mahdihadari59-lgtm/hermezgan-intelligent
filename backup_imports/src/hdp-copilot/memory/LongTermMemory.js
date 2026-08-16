class LongTermMemory {
  constructor({ store = null, ttl = 86400 } = {}) {
    this.store = store;
    this.ttl = ttl;
    this.local = new Map();
  }

  _key(conversationId) { return `hdp:v1:ltm:${conversationId}`; }

  async get(conversationId) {
    if (!conversationId) return null;
    const key = this._key(conversationId);
    if (this.store?.get) {
      const raw = await this.store.get(key);
      try { return raw ? JSON.parse(raw) : null; } catch { return null; }
    }
    const item = this.local.get(key);
    if (!item) return null;
    if (Date.now() > item.expiry) { this.local.delete(key); return null; }
    return item.value;
  }

  async set(conversationId, value) {
    if (!conversationId) return;
    const key = this._key(conversationId);
    if (this.store?.setEx) return this.store.setEx(key, this.ttl, JSON.stringify(value));
    if (this.store?.setex) return this.store.setex(key, this.ttl, JSON.stringify(value));
    if (this.store?.set) return this.store.set(key, JSON.stringify(value));
    this.local.set(key, { value, expiry: Date.now() + (this.ttl * 1000) });
  }
}
module.exports = LongTermMemory;
