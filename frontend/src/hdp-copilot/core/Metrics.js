class Metrics {
  constructor() {
    this.counters = new Map();
    this.timings = new Map();
  }
  increment(name, by = 1) { this.counters.set(name, (this.counters.get(name) || 0) + by); }
  observe(name, value) {
    if (!this.timings.has(name)) this.timings.set(name, { count: 0, sum: 0, min: Number.POSITIVE_INFINITY, max: 0 });
    const b = this.timings.get(name);
    b.count += 1; b.sum += value; b.min = Math.min(b.min, value); b.max = Math.max(b.max, value);
  }
  recordIntent(intentType) { this.increment(`intent.${intentType || 'unknown'}`); }
  recordCacheHit(namespace) { this.increment(`cache.hit.${namespace}`); }
  recordCacheMiss(namespace) { this.increment(`cache.miss.${namespace}`); }
  snapshot() {
    const counters = {};
    const timings = {};
    for (const [k, v] of this.counters.entries()) counters[k] = v;
    for (const [k, v] of this.timings.entries()) timings[k] = { count: v.count, avg: v.count ? v.sum / v.count : 0, min: v.min === Number.POSITIVE_INFINITY ? 0 : v.min, max: v.max };
    return { counters, timings };
  }
}
module.exports = Metrics;
