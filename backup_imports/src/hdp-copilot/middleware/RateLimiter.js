class RateLimiter {
  constructor({ windowMs = 60_000, maxRequests = 30 } = {}) {
    this.windowMs = windowMs;
    this.maxRequests = maxRequests;
    this.buckets = new Map();
  }

  _key(context = {}) {
    return context.userId || context.apiKey || context.ip || context.conversationId || 'anon';
  }

  check(context = {}) {
    const key = this._key(context);
    const now = Date.now();
    let bucket = this.buckets.get(key);
    if (!bucket || now >= bucket.resetAt) bucket = { count: 0, resetAt: now + this.windowMs };

    bucket.count += 1;
    this.buckets.set(key, bucket);

    if (bucket.count > this.maxRequests) {
      return { allowed: false, retryAfterMs: Math.max(0, bucket.resetAt - now) };
    }
    return { allowed: true, remaining: Math.max(0, this.maxRequests - bucket.count), resetAt: bucket.resetAt };
  }
}
module.exports = RateLimiter;
