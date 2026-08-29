class CacheManager {
  constructor(redisClient = null, options = {}) {
    this.redis = redisClient;
    this.localCache = new Map();
    this.maxEntries = options.maxEntries || 5000;
    this.ttls = {
      weather: 600,
      traffic: 60,
      transport: 300,
      tourism: 86400,
      nearby: 180,
      route: 300,
      search: 600,
      default: 300
    };
  }

  _key(namespace, key) { return `hdp:v1:${namespace}:${key}`; }
  _now() { return Date.now(); }

  _evictIfNeeded() {
    if (this.localCache.size <= this.maxEntries) return;
    const items = [...this.localCache.entries()].sort((a, b) => (a[1].lastAccess || 0) - (b[1].lastAccess || 0));
    const removeCount = this.localCache.size - this.maxEntries;
    for (let i = 0; i < removeCount; i++) this.localCache.delete(items[i][0]);
  }

  async get(namespace, key) {
    const fullKey = this._key(namespace, key);
    if (this.redis) {
      const val = await this.redis.get(fullKey);
      if (!val) return null;
      try { return JSON.parse(val); } catch (_) { return val; }
    }

    const item = this.localCache.get(fullKey);
    if (!item) return null;
    if (this._now() > item.expiry) {
      this.localCache.delete(fullKey);
      return null;
    }
    item.lastAccess = this._now();
    return item.value;
  }

  async set(namespace, key, value, customTtl) {
    const ttl = customTtl || this.ttls[namespace] || this.ttls.default;
    const fullKey = this._key(namespace, key);
    if (this.redis) {
      await this.redis.setEx(fullKey, ttl, JSON.stringify(value));
      return;
    }
    this.localCache.set(fullKey, {
      value,
      expiry: this._now() + (ttl * 1000),
      lastAccess: this._now()
    });
    this._evictIfNeeded();
  }

  async invalidate(namespace, pattern = '*') {
    if (this.redis) {
      const prefix = `hdp:v1:${namespace}:`;
      if (typeof this.redis.scanIterator === 'function') {
        for await (const key of this.redis.scanIterator({ MATCH: `${prefix}${pattern}`, COUNT: 100 })) {
          await this.redis.del(key);
        }
        return;
      }
      if (typeof this.redis.scan === 'function') {
        let cursor = 0;
        do {
          const [nextCursor, keys] = await this.redis.scan(cursor, 'MATCH', `${prefix}${pattern}`, 'COUNT', 100);
          cursor = Number(nextCursor);
          if (keys?.length) await this.redis.del(...keys);
        } while (cursor !== 0);
      }
      return;
    }

    const prefix = `hdp:v1:${namespace}:`;
    for (const key of [...this.localCache.keys()]) {
      if (key.startsWith(prefix)) this.localCache.delete(key);
    }
  }

  size() { return this.localCache.size; }
}
module.exports = CacheManager;
