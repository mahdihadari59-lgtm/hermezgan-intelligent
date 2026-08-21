class BaseExpert {
  constructor(name, deps = {}) {
    this.name = name;
    this.deps = deps;
  }

  async handle() {
    throw new Error('handle() must be implemented');
  }

  async getCached(namespace, key, fetchFn, ttl) {
    const cache = this.deps.cacheManager;
    if (!cache) return fetchFn();

    const cached = await cache.get(namespace, key);
    if (cached) return cached;

    const data = await fetchFn();
    if (data !== undefined && data !== null) {
      await cache.set(namespace, key, data, ttl);
    }
    return data;
  }
}
module.exports = BaseExpert;
