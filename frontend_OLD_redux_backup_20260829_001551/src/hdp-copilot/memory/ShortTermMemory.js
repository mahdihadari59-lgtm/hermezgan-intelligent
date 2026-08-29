class ShortTermMemory {
  constructor({ limit = 10, store = null } = {}) {
    this.limit = limit;
    this.store = store;
    this.local = new Map();
  }

  _key(conversationId) { return `hdp:v1:stm:${conversationId}`; }

  async get(conversationId) {
    if (!conversationId) return [];
    const key = this._key(conversationId);
    if (this.store?.get) {
      const raw = await this.store.get(key);
      try { return raw ? JSON.parse(raw) : []; } catch { return []; }
    }
    return this.local.get(key) || [];
  }

  async append(conversationId, message) {
    if (!conversationId || !message) return [];
    const key = this._key(conversationId);
    const current = await this.get(conversationId);
    current.push(message);
    const trimmed = current.slice(-this.limit);

    if (this.store?.setEx) await this.store.setEx(key, 3600, JSON.stringify(trimmed));
    else if (this.store?.setex) await this.store.setex(key, 3600, JSON.stringify(trimmed));
    else if (this.store?.set) await this.store.set(key, JSON.stringify(trimmed));
    else this.local.set(key, trimmed);

    return trimmed;
  }

  async clear(conversationId) {
    if (!conversationId) return;
    const key = this._key(conversationId);
    if (this.store?.del) await this.store.del(key);
    else this.local.delete(key);
  }
}
module.exports = ShortTermMemory;
