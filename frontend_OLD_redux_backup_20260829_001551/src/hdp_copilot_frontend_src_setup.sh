#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

PROJECT_ROOT="${HOME}/hermezgan-intelligent/frontend/src/hdp-copilot"

mkdir -p "$PROJECT_ROOT"/{core,experts,config,utils,middleware,memory,plugins/weather,logs}

cat > "$PROJECT_ROOT/package.json" <<'EOF'
{
  "name": "hdp-copilot",
  "version": "4.0.0",
  "private": true,
  "main": "index.js",
  "type": "commonjs"
}
EOF

cat > "$PROJECT_ROOT/index.js" <<'EOF'
module.exports = require('./core/AICopilot');
EOF

cat > "$PROJECT_ROOT/utils/persianRegex.js" <<'EOF'
class PersianRegex {
  static normalize(text) {
    return String(text ?? '')
      .replace(/\u064A/g, 'ی')
      .replace(/\u0643/g, 'ک')
      .replace(/\u200c+/g, '‌')
      .replace(/\s+/g, ' ')
      .trim();
  }

  static extractDestination(text) {
    const t = this.normalize(text);
    const m = t.match(/(?:به|تا|از|مسیر|راه|هوای|آب و هوای|جاذبه‌های|دیدنی‌های)\s+([^\s،.]+(?:\s+[^\s،.]+){0,2})/);
    return m?.[1]?.trim() || null;
  }

  static extractCategory(text) {
    const t = this.normalize(text);
    const patterns = [
      /(تعمیرگاه|پمپ بنزین|بیمارستان|داروخانه|هتل|رستوران|مسجد|بندر|اسکله|فرودگاه|مرکز خرید|بازار|اتوبوس|تاکسی|شناور|لندی)/,
    ];
    for (const p of patterns) {
      const m = t.match(p);
      if (m?.[1]) return m[1].trim();
    }
    return null;
  }

  static extractFeeling(text) {
    const t = this.normalize(text);
    const feelings = ['گرمه', 'سرده', 'شرجیه', 'طوفانیه', 'بارونیه', 'آفتابیه'];
    return feelings.find(f => t.includes(f)) || null;
  }
}
module.exports = PersianRegex;
EOF

cat > "$PROJECT_ROOT/core/Logger.js" <<'EOF'
const fs = require('fs');
const path = require('path');
const { once } = require('events');

class Logger {
  constructor(logDir = './logs') {
    this.logDir = logDir;
    this.currentDate = null;
    this.stream = null;
    if (!fs.existsSync(logDir)) fs.mkdirSync(logDir, { recursive: true });
  }

  _getFilePath() {
    const day = new Date().toISOString().slice(0, 10);
    return { day, file: path.join(this.logDir, `${day}.ndjson`) };
  }

  _ensureStream() {
    const { day, file } = this._getFilePath();
    if (this.currentDate !== day || !this.stream) {
      if (this.stream) {
        try { this.stream.end(); } catch (_) {}
      }
      this.currentDate = day;
      this.stream = fs.createWriteStream(file, { flags: 'a' });
      this.stream.on('error', (err) => console.error('[LOGGER_STREAM_ERROR]', err));
    }
  }

  async _write(level, data) {
    try {
      this._ensureStream();
      const line = JSON.stringify({ timestamp: new Date().toISOString(), level, ...data }) + '\n';
      if (this.stream && !this.stream.write(line)) await once(this.stream, 'drain');
      if (process.env.NODE_ENV !== 'production') {
        const fn = level === 'error' ? 'error' : level === 'warn' ? 'warn' : 'log';
        console[fn](`[${level.toUpperCase()}]`, data);
      }
    } catch (err) {
      console.error('[LOGGER_WRITE_ERROR]', err);
    }
  }

  info(data) { return this._write('info', data); }
  warn(data) { return this._write('warn', data); }
  error(data) { return this._write('error', data); }
}
module.exports = Logger;
EOF

cat > "$PROJECT_ROOT/core/CacheManager.js" <<'EOF'
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
EOF

cat > "$PROJECT_ROOT/core/ContextManager.js" <<'EOF'
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
EOF

cat > "$PROJECT_ROOT/core/CircuitBreaker.js" <<'EOF'
class CircuitBreaker {
  constructor({ failureThreshold = 3, cooldownMs = 30000 } = {}) {
    this.failureThreshold = failureThreshold;
    this.cooldownMs = cooldownMs;
    this.state = new Map();
  }

  _get(key) {
    if (!this.state.has(key)) {
      this.state.set(key, { failures: 0, openedAt: 0, halfOpenTrial: false });
    }
    return this.state.get(key);
  }

  _isOpen(entry) {
    if (!entry.openedAt) return false;
    return (Date.now() - entry.openedAt) < this.cooldownMs;
  }

  async execute(key, fn) {
    const entry = this._get(key);
    if (this._isOpen(entry)) return null;
    try {
      const result = await fn();
      entry.failures = 0;
      entry.openedAt = 0;
      entry.halfOpenTrial = false;
      return result;
    } catch (err) {
      entry.failures += 1;
      if (entry.failures >= this.failureThreshold) {
        entry.openedAt = Date.now();
        entry.halfOpenTrial = false;
      }
      throw err;
    }
  }
}
module.exports = CircuitBreaker;
EOF

cat > "$PROJECT_ROOT/core/Security.js" <<'EOF'
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
EOF

cat > "$PROJECT_ROOT/core/Metrics.js" <<'EOF'
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
EOF

cat > "$PROJECT_ROOT/middleware/Validation.js" <<'EOF'
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
EOF

cat > "$PROJECT_ROOT/middleware/Authentication.js" <<'EOF'
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
EOF

cat > "$PROJECT_ROOT/middleware/RateLimiter.js" <<'EOF'
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
EOF

cat > "$PROJECT_ROOT/memory/ShortTermMemory.js" <<'EOF'
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
EOF

cat > "$PROJECT_ROOT/memory/LongTermMemory.js" <<'EOF'
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
EOF

cat > "$PROJECT_ROOT/memory/ConversationSummary.js" <<'EOF'
class ConversationSummary {
  build(messages = [], previous = {}) {
    const recent = Array.isArray(messages) ? messages.slice(-8) : [];
    const userTurns = recent.filter(m => m.role === 'user');
    const assistantTurns = recent.filter(m => m.role === 'assistant');
    const intents = [...new Set(userTurns.map(m => m.intent).filter(Boolean))];
    const lastDestination = [...userTurns].reverse().find(m => m.destination)?.destination || previous.lastDestination || null;
    const lastCategory = [...userTurns].reverse().find(m => m.category)?.category || previous.lastCategory || null;
    const lastQuery = userTurns.length ? userTurns[userTurns.length - 1].text : null;

    const textParts = [];
    if (lastDestination) textParts.push(`مقصد: ${lastDestination}`);
    if (lastCategory) textParts.push(`دسته: ${lastCategory}`);
    if (intents.length) textParts.push(`نیت‌ها: ${intents.join('، ')}`);
    if (lastQuery) textParts.push(`آخرین پرسش: ${lastQuery}`);

    return {
      text: textParts.join(' | '),
      lastDestination,
      lastCategory,
      intents,
      updatedAt: new Date().toISOString(),
      recentTurns: { user: userTurns.length, assistant: assistantTurns.length }
    };
  }
}
module.exports = ConversationSummary;
EOF

cat > "$PROJECT_ROOT/core/EntityParser.js" <<'EOF'
class EntityParser {
  constructor() {
    this.destinationAliases = [
      { pattern: /^(بندر\s?عباس|بندرعباس|bandar\s*abbas)$/i, value: 'بندرعباس' },
      { pattern: /^(قشم|جزیره\s*قشم|qeshm)$/i, value: 'قشم' },
      { pattern: /^(کیش|kish)$/i, value: 'کیش' },
      { pattern: /^(میناب|minab)$/i, value: 'میناب' },
      { pattern: /^(هرمز|hormuz)$/i, value: 'هرمز' },
      { pattern: /^(جاسک|jask)$/i, value: 'جاسک' },
      { pattern: /^(بستک|bastak)$/i, value: 'بستک' },
      { pattern: /^(رودان|rudan)$/i, value: 'رودان' },
      { pattern: /^(پارسیان|parsian)$/i, value: 'پارسیان' },
      { pattern: /^(حاجی\s?آباد|حاجی‌آباد|hajiabad)$/i, value: 'حاجی‌آباد' }
    ];

    this.categoryAliases = [
      { pattern: /(تعمیرگاه|مکانیک|صافکاری|پنچرگیری)/, value: 'تعمیرگاه' },
      { pattern: /(پمپ\s?بنزین|جایگاه\s?سوخت|cng)/i, value: 'پمپ بنزین' },
      { pattern: /(بیمارستان|درمانگاه|اورژانس|کلینیک)/, value: 'بیمارستان' },
      { pattern: /(داروخانه)/, value: 'داروخانه' },
      { pattern: /(هتل|اقامتگاه|مهمانپذیر)/, value: 'هتل' },
      { pattern: /(رستوران|غذاخوری|کافه)/, value: 'رستوران' },
      { pattern: /(مسجد|حسینیه|امامزاده)/, value: 'مسجد' },
      { pattern: /(بندر|اسکله|ترمینال|فرودگاه)/, value: 'حمل و نقل' },
      { pattern: /(مرکز\s?خرید|بازار|مال)/, value: 'مرکز خرید' },
      { pattern: /(اتوبوس|تاکسی|شناور|لندی|پرواز)/, value: 'حمل و نقل' }
    ];

    this.destinationPatterns = [
      /(?:راه|مسیر|به|تا|برم|برسیم|بریم|فاصله|آب و هوای|هوای|جاذبه‌های|دیدنی‌های|دیدنی های|جاذبه های)\s+([^\s،.]+(?:\s+[^\s،.]+){0,2})/,
      /([^\s]+(?:\s+[^\s]+){0,2})\s+(?:کجاست|چطوره|چگونه است|چند کیلومتر|چقدر دوره|هواش|آب و هواش)/,
      /(?:می‌خوام|میخوام|می خوام|برویم|بریم|برم)\s+(?:به\s+)?([^\s،.]+(?:\s+[^\s،.]+){0,2})/,
      /(?:یه\s+)?(?:مسیر|راه)\s+(?:تا|به|از\s+[^\s]+\s+تا|از\s+[^\s]+\s+به)?\s*([^\s،.]+(?:\s+[^\s،.]+){0,2})/
    ];

    this.radiusPatterns = [
      /(?:شعاع|در|تا|تا\s+حدود)\s*(\d+)\s*(?:کیلومتر|کیلومتری|km|متر|متری|m)/i,
      /(\d+)\s*(?:کیلومتر|کیلومتری|km|متر|متری|m)\s*(?:شعاع|اطراف|نزدیک)/i
    ];

    this.feelingPatterns = ['گرمه', 'سرده', 'شرجیه', 'طوفانیه', 'بارونیه', 'آفتابیه'];
  }

  parse(text) {
    const categoryPatterns = this.categoryAliases.map(item => item.pattern);
    const entities = {
      destination: this._canonicalDestination(this._extract(text, this.destinationPatterns)),
      radius: this._extractRadius(text),
      category: this._canonicalCategory(this._extract(text, categoryPatterns)),
      feeling: this._extractFeeling(text),
      origin: null
    };

    const routeMatch = text.match(/از\s+([^\s،.]+(?:\s+[^\s،.]+){0,2})\s+تا\s+([^\s،.]+(?:\s+[^\s،.]+){0,2})/);
    if (routeMatch) {
      entities.origin = this._canonicalDestination(routeMatch[1].trim());
      entities.destination = this._canonicalDestination(routeMatch[2].trim());
    }
    return entities;
  }

  _extract(text, patterns) {
    for (const pattern of patterns) {
      const m = text.match(pattern);
      if (m && m[1]) return m[1].trim();
    }
    return null;
  }

  _extractRadius(text) {
    const m = text.match(this.radiusPatterns[0]) || text.match(this.radiusPatterns[1]);
    if (m) {
      let val = parseInt(m[1], 10);
      if (text.includes('متر') || text.includes('m')) val = val / 1000;
      return val;
    }
    if (/(نزدیک|اطراف|نزدیکم|اطرافم)/.test(text)) return 5;
    return null;
  }

  _extractFeeling(text) {
    for (const feeling of this.feelingPatterns) {
      if (text.includes(feeling)) return feeling;
    }
    return null;
  }

  _canonicalDestination(value) {
    if (!value) return null;
    const cleaned = value.trim();
    for (const item of this.destinationAliases) {
      if (item.pattern.test(cleaned)) return item.value;
    }
    return cleaned;
  }

  _canonicalCategory(value) {
    if (!value) return null;
    const cleaned = value.trim();
    for (const item of this.categoryAliases) {
      if (item.pattern.test(cleaned)) return item.value;
    }
    return cleaned;
  }
}
module.exports = EntityParser;
EOF

cat > "$PROJECT_ROOT/core/IntentDetector.js" <<'EOF'
class IntentDetector {
  constructor() {
    this.patterns = {
      emergency: { keywords: ['امداد','تصادف','پنچری','خرابی','کمک','اورژانس','آتش','پلیس','115','110','125','حریق'], regex: [/(?:تصادف|پنچر|خراب|اورژانس|آتش‌نشانی|پلیس|امداد|حریق)/, /(?:شماره|تماس)\s+(?:اورژانس|پلیس|آتش|امداد)/], weight: 1.2, priority: 1, priorityWeight: 1.0 },
      route: { keywords: ['راه','مسیر','چطور برم','چگونه بروم','فاصله','چند کیلومتر','چطوری برم','میخوام برم','می‌خوام برم','بریم','برسیم','کجاست'], regex: [/(?:راه|مسیر)\s+(?:به\s+)?(.+?)(?:\s+چطور|چگونه|کجاست|$)/, /(?:چطور|چگونه|چطوری)\s+(?:برم|بروم|برسیم)\s+(?:به\s+)?(.+)/, /(?:فاصله|مسافت)\s+(?:تا|به|از)\s+(.+)/], weight: 1.0, priority: 2, priorityWeight: 0.95 },
      traffic: { keywords: ['ترافیک','شلوغ','بسته','راه بسته','بحرانی','قفل','ترافیکی','ازدحام'], regex: [/(?:ترافیک|وضعیت راه|شلوغی)\s+(.+)/, /(.+?)\s+(?:ترافیک|شلوغ|بسته|قفل)/], weight: 1.0, priority: 2, priorityWeight: 0.9 },
      nearby: { keywords: ['نزدیک','اطراف','نزدیکم','پیدا کن','بگیر','کجاست'], regex: [/(?:نزدیک|اطراف|در نزدیکی|نزدیکم)\s+(.+)/, /(.+?)\s+(?:نزدیک|اطراف|نزدیکم)/], weight: 0.9, priority: 3, priorityWeight: 0.85 },
      weather: { keywords: ['هوا','آب و هوا','گرم','سرد','بارون','باران','شرجی','طوفان','هواش','دمای'], regex: [/(?:آب و هوا|آب‌وهوا|هوا|هوای|دمای)\s+(.+)/, /(.+?)\s+(?:هوا|آب و هوا|آب‌وهوا|هواش)/, /(?:گرمه|سرده|بارونی|طوفانی|شرجیه)/], weight: 0.9, priority: 3, priorityWeight: 0.85 },
      tourist: { keywords: ['گردشگری','تفریح','جاهای دیدنی','جاذبه','سفر','دیدن','بازدید','توریستی'], regex: [/(?:جاذبه|جاهای دیدنی|مکان‌های دیدنی|دیدنی‌های)\s+(.+)/, /(.+?)\s+(?:چی داره|جاذبه|دیدنی|تفریح)/], weight: 0.85, priority: 3, priorityWeight: 0.8 },
      transport: { keywords: ['اتوبوس','تاکسی','شناور','لندی','فرودگاه','پرواز','بندر','اسکله','حمل و نقل','ترمینال'], regex: [/(?:اتوبوس|تاکسی|شناور|لندی|پرواز|اسکله|فرودگاه)\s+(.+)/, /(.+?)\s+(?:دارید|هست|کجاست|چنده|چه موقع)/], weight: 0.9, priority: 3, priorityWeight: 0.85 },
      greeting: { keywords: ['سلام','درود','صبح بخیر','شب بخیر','هی','سلامتی','علیکم'], regex: [/^(سلام|درود|صبح بخیر|شب بخیر|هی|سلامتی|سلام علیکم)\b/], weight: 0.8, priority: 4, priorityWeight: 0.7 }
    };
  }

  detect(text, entities = {}) {
    const scored = [];
    for (const [type, cfg] of Object.entries(this.patterns)) {
      let rawScore = 0;
      let matchedKeywords = 0;
      let extractedDest = null;

      for (const kw of cfg.keywords) {
        if (text.includes(kw)) { matchedKeywords += 1; rawScore += cfg.weight * 0.35; }
      }

      if (cfg.regex) {
        for (const p of cfg.regex) {
          const m = text.match(p);
          if (m) { rawScore += cfg.weight * 0.55; if (m[1]) extractedDest = m[1].trim(); break; }
        }
      }

      const wordCount = text.split(/\s+/).filter(Boolean).length;
      const normalizedScore = Math.min(rawScore / Math.max(wordCount * 0.08, 0.5), 1.0);
      const finalScore = (normalizedScore * 0.8) + (cfg.priorityWeight * 0.2);

      if (finalScore > 0.15) {
        scored.push({
          type,
          score: parseFloat(finalScore.toFixed(3)),
          confidence: parseFloat(normalizedScore.toFixed(2)),
          priority: cfg.priority,
          matchedKeywords,
          destination: extractedDest || entities.destination || null,
          category: entities.category || null,
          feeling: entities.feeling || null,
          origin: entities.origin || null,
          text
        });
      }
    }
    scored.sort((a, b) => b.score - a.score);
    return scored;
  }
}
module.exports = IntentDetector;
EOF

cat > "$PROJECT_ROOT/core/PluginManager.js" <<'EOF'
const fs = require('fs');
const path = require('path');

class PluginManager {
  constructor(deps = {}) {
    this.deps = deps;
    this.registry = new Map();
    this.sources = new Map();
  }

  register(intentType, instance, meta = {}) {
    if (!intentType || !instance) return;
    this.registry.set(intentType, instance);
    this.sources.set(intentType, meta);
  }

  get(intentType) { return this.registry.get(intentType) || null; }

  autoLoad({ pluginsDir = null, expertsDir = null, manifestMap = {} } = {}) {
    if (pluginsDir && fs.existsSync(pluginsDir)) {
      const subdirs = fs.readdirSync(pluginsDir, { withFileTypes: true }).filter(d => d.isDirectory());
      for (const dirent of subdirs) {
        const pluginDir = path.join(pluginsDir, dirent.name);
        const manifestPath = path.join(pluginDir, 'manifest.json');
        if (!fs.existsSync(manifestPath)) continue;

        try {
          const manifest = JSON.parse(fs.readFileSync(manifestPath, 'utf8'));
          if (manifest.enabled === false) continue;
          const entry = path.resolve(pluginDir, manifest.entry);
          const mod = require(entry);
          const PluginClass = mod?.default || mod;
          const instance = new PluginClass(this.deps, manifest.configPath || undefined);
          const intents = Array.isArray(manifest.intents) ? manifest.intents : [manifest.intent || dirent.name.toLowerCase()];
          for (const intentType of intents) {
            this.register(intentType, instance, { plugin: manifest.name || dirent.name, entry: manifest.entry, dir: pluginDir });
          }
        } catch (err) {
          this.deps.logger?.error({ event: 'plugin_load_failed', dir: pluginDir, error: err.message });
        }
      }
    }

    if (expertsDir && fs.existsSync(expertsDir)) {
      const files = fs.readdirSync(expertsDir).filter(f => f.endsWith('Expert.js') && f !== 'BaseExpert.js');
      for (const file of files) {
        const fullPath = path.join(expertsDir, file);
        try {
          const mod = require(fullPath);
          const ExpertClass = mod?.default || mod;
          const intentType = manifestMap[file] || file.replace('Expert.js', '').toLowerCase();
          if (this.registry.has(intentType)) continue;
          const instance = new ExpertClass(this.deps);
          this.register(intentType, instance, { source: 'experts', file });
        } catch (err) {
          this.deps.logger?.error({ event: 'expert_load_failed', file, error: err.message });
        }
      }
    }

    return this.list();
  }

  list() { return [...this.registry.keys()]; }

  async route(intent, query, context, deps) {
    const expert = this.get(intent.type);
    if (!expert) {
      const result = await deps.searchPipeline?.search(query, deps.searchOptions || {});
      return result || deps.defaultResponses?.unknown || null;
    }
    return expert.handle(intent, query, context, deps);
  }

  async routeMulti(intents, query, context, deps) {
    const out = [];
    for (const intent of intents.slice(0, 2)) {
      const res = await this.route(intent, query, context, deps);
      if (res) out.push(res);
    }
    return out.join('\n\n───\n\n');
  }
}

module.exports = PluginManager;
EOF

cat > "$PROJECT_ROOT/core/SearchPipeline.js" <<'EOF'
const CircuitBreaker = require('./CircuitBreaker');

class SearchPipeline {
  constructor({ knowledgeBase, embeddingSearch, fuzzySearch, cacheManager, logger, metrics, breaker }) {
    this.kb = knowledgeBase;
    this.embed = embeddingSearch;
    this.fuzzy = fuzzySearch;
    this.cache = cacheManager;
    this.logger = logger;
    this.metrics = metrics;
    this.breaker = breaker || new CircuitBreaker({ failureThreshold: 3, cooldownMs: 30000 });
    this.layerTimeoutMs = 1500;
  }

  async _timeout(promiseFactory, ms, label) {
    let timer;
    const timeout = new Promise((_, reject) => {
      timer = setTimeout(() => reject(new Error(`TIMEOUT:${label}:${ms}`)), ms);
    });
    try {
      return await Promise.race([Promise.resolve().then(promiseFactory), timeout]);
    } finally {
      clearTimeout(timer);
    }
  }

  _safeArray(value) { return !value ? [] : Array.isArray(value) ? value : [value]; }

  _normalizeStageValue(value, stageName) {
    if (!value) return [];
    if (typeof value === 'string') {
      return [{ title: value, content: '', score: stageName === 'fts5' || stageName === 'kg' || stageName === 'bm25' ? 0.95 : 0.75, _layer: stageName }];
    }
    const items = this._safeArray(value);
    return items.map(item => ({
      ...item,
      title: item?.title ?? '',
      content: item?.content ?? item?.text ?? '',
      score: Number(item?.score ?? item?._score ?? item?.relevance ?? 0.5),
      _layer: stageName
    }));
  }

  _dedupe(items) {
    const map = new Map();
    for (const item of items) {
      const key = `${String(item.title ?? '')}::${String(item.content ?? '')}`.toLowerCase().trim();
      if (!map.has(key)) map.set(key, item);
    }
    return [...map.values()];
  }

  _rerank(candidates, query) {
    const queryWords = [...new Set(String(query).toLowerCase().split(/\s+/).filter(Boolean))];
    return candidates.map(c => {
      const text = `${c.title ?? ''} ${c.content ?? ''}`.toLowerCase();
      const overlap = queryWords.length ? queryWords.filter(w => text.includes(w)).length / queryWords.length : 0;
      const lengthBonus = Math.min(text.length / 5000, 0.1);
      const base = Number(c.score ?? 0.5);
      const finalScore = (base * 0.6) + (overlap * 0.35) + lengthBonus;
      return { ...c, _finalScore: finalScore };
    }).sort((a, b) => b._finalScore - a._finalScore);
  }

  async _runStage(stage, query, timeoutMs) {
    const raw = await this.breaker.execute(stage.name, () => this._timeout(stage.fn, timeoutMs, stage.name));
    return this._normalizeStageValue(raw, stage.name);
  }

  async search(query, options = {}) {
    const normalizedQuery = String(query ?? '').trim();
    if (!normalizedQuery) return null;

    const cacheKey = `gen:${Buffer.from(normalizedQuery).toString('base64').slice(0, 32)}`;
    const cached = await this.cache?.get('search', cacheKey);
    if (cached) {
      this.metrics?.recordCacheHit('search');
      return cached;
    }
    this.metrics?.recordCacheMiss('search');

    const timeoutMs = options.timeoutMs || this.layerTimeoutMs;
    const stages = [
      { name: 'fts5', fn: () => this.kb?.searchFTS5?.(normalizedQuery), stopAt: 0.92 },
      { name: 'kg', fn: () => this.kb?.searchKnowledgeGraph?.(normalizedQuery), stopAt: 0.90 },
      { name: 'bm25', fn: () => this.kb?.searchBM25?.(normalizedQuery), stopAt: 0.88 },
      { name: 'embedding', fn: () => this.embed?.search(normalizedQuery, { limit: 5, threshold: 0.6 }), stopAt: 0.82 },
      { name: 'fuzzy', fn: () => this.fuzzy?.search(normalizedQuery), stopAt: 0.78 }
    ];

    const candidates = [];

    for (const stage of stages) {
      const started = Date.now();
      let items = [];
      try {
        items = await this._runStage(stage, normalizedQuery, timeoutMs);
      } catch (err) {
        this.logger?.warn?.({ event: 'search_stage_failed', stage: stage.name, query: normalizedQuery, error: err.message });
        this.metrics?.increment(`search.stage.error.${stage.name}`);
        continue;
      }

      const elapsed = Date.now() - started;
      this.metrics?.observe(`search.stage.ms.${stage.name}`, elapsed);

      if (items.length) {
        this.metrics?.increment(`search.stage.hit.${stage.name}`);
        candidates.push(...items);
        const bestStageItem = this._rerank(items, normalizedQuery)[0];
        if (bestStageItem && Number(bestStageItem._finalScore ?? 0) >= stage.stopAt) {
          const answer = bestStageItem.content || bestStageItem.title || bestStageItem.text || null;
          if (answer) {
            await this.cache?.set('search', cacheKey, answer, 600);
            this.logger?.info?.({ event: 'search_pipeline_fast_path', query: normalizedQuery, stage: stage.name });
            return answer;
          }
        }
      } else {
        this.metrics?.increment(`search.stage.miss.${stage.name}`);
      }
    }

    if (!candidates.length) return null;

    const reranked = this._rerank(this._dedupe(candidates), normalizedQuery);
    const best = reranked[0];
    const answer = best?.content || best?.title || best?.text || null;
    if (answer) await this.cache?.set('search', cacheKey, answer, 600);

    this.logger?.info?.({ event: 'search_pipeline', query: normalizedQuery, layers: [...new Set(candidates.map(c => c._layer))], bestLayer: best?._layer || null });
    return answer;
  }
}
module.exports = SearchPipeline;
EOF

cat > "$PROJECT_ROOT/experts/BaseExpert.js" <<'EOF'
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
EOF

cat > "$PROJECT_ROOT/experts/RouteExpert.js" <<'EOF'
const BaseExpert = require('./BaseExpert');

class RouteExpert extends BaseExpert {
  constructor(deps = {}) { super('RouteExpert', deps); }
  async handle(intent, query, context, deps) {
    const dest = intent.destination;
    if (!dest) return 'مقصد را مشخص کنید. مثال: "راه قشم چطوره؟"';
    const cacheKey = `${intent.origin || 'unknown'}:${dest}`;
    const route = await this.getCached('route', cacheKey, () => deps.knowledgeBase?.getRoute?.(dest, intent.origin), 300);
    if (!route) return `مسیر ${dest} در پایگاه داده موجود نیست.`;
    let res = `🚗 مسیر ${intent.origin ? `${intent.origin} → ` : ''}${dest}: ${route.distance} کیلومتر، حدود ${route.duration} دقیقه.`;
    if (route.traffic) res += `\n📊 وضعیت ترافیک: ${route.traffic}`;
    if (route.tip) res += `\n💡 ${route.tip}`;
    if (route.alternative) res += `\n🛣️ مسیر جایگزین: ${route.alternative}`;
    return res;
  }
}
module.exports = RouteExpert;
EOF

cat > "$PROJECT_ROOT/experts/TrafficExpert.js" <<'EOF'
const BaseExpert = require('./BaseExpert');

class TrafficExpert extends BaseExpert {
  constructor(deps = {}) { super('TrafficExpert', deps); }
  async handle(intent, query, context, deps) {
    const area = intent.destination || context.location?.city || 'بندرعباس';
    const traffic = await this.getCached('traffic', area, () => deps.knowledgeBase?.getTrafficInfo?.(area), 60);
    if (!traffic || !Object.keys(traffic).length) return `اطلاعات ترافیکی ${area} در دسترس نیست.`;
    let res = `🚦 وضعیت ترافیک ${area}:\n`;
    for (const [road, status] of Object.entries(traffic)) {
      const emoji = status === 'سنگین' ? '🔴' : status === 'نیمه سنگین' ? '🟡' : status === 'بسته' ? '⛔' : '🟢';
      res += `${emoji} ${road}: ${status}\n`;
    }
    return res.trim();
  }
}
module.exports = TrafficExpert;
EOF

cat > "$PROJECT_ROOT/experts/WeatherExpert.js" <<'EOF'
const BaseExpert = require('./BaseExpert');

class WeatherExpert extends BaseExpert {
  constructor(deps = {}) { super('WeatherExpert', deps); }
  async handle(intent, query, context, deps) {
    const city = intent.destination || context.lastDestination || 'بندرعباس';
    const weather = await this.getCached('weather', city, () => deps.knowledgeBase?.getWeatherInfo?.(city), 600);
    if (!weather) return `اطلاعات آب و هوای ${city} در دسترس نیست.`;
    return `🌡️ ${weather.city || city}: ${weather.temp}°C، رطوبت ${weather.humidity}%\n🌬️ باد: ${weather.wind || 'نامشخص'}\n☀️ وضعیت: ${weather.condition || 'آفتابی'}\n💡 ${weather.tip || 'کولر فراموش نشود'}`;
  }
}
module.exports = WeatherExpert;
EOF

cat > "$PROJECT_ROOT/experts/NearbyExpert.js" <<'EOF'
const BaseExpert = require('./BaseExpert');

class NearbyExpert extends BaseExpert {
  constructor(deps = {}) { super('NearbyExpert', deps); }
  async handle(intent, query, context, deps) {
    const category = intent.category;
    if (!category) return 'نوع خدمات را مشخص کنید. مثال: "تعمیرگاه نزدیک"';
    const loc = context.location || context.userLocation;
    if (!loc?.latitude || !loc?.longitude) return 'برای یافتن خدمات نزدیک، لطفاً موقعیت GPS خود را فعال کنید. 📍';

    const radius = intent.radius || 5;
    const cacheKey = `${category}:${loc.latitude.toFixed(3)}:${loc.longitude.toFixed(3)}:${radius}`;
    const services = await this.getCached('nearby', cacheKey, () => deps.knowledgeBase?.getNearbyServices?.(category, { latitude: loc.latitude, longitude: loc.longitude, radius: radius * 1000 }), 180);

    if (!services?.length) return `${category} در شعاع ${radius} کیلومتری پیدا نشد.`;

    let res = `📍 نزدیک‌ترین ${category} (شعاع ${radius}km):\n`;
    services.slice(0, 3).forEach((s, i) => {
      res += `\n${i + 1}. 🏢 ${s.name} | 📏 ${s.distance}m`;
      if (s.phone) res += ` | 📞 ${s.phone}`;
      if (s.isOpen !== undefined) res += s.isOpen ? ' | ✅ باز' : ' | ❌ بسته';
    });
    if (services.length > 3) res += `\n\n... و ${services.length - 3} مورد دیگر`;
    return res;
  }
}
module.exports = NearbyExpert;
EOF

cat > "$PROJECT_ROOT/experts/TouristExpert.js" <<'EOF'
const BaseExpert = require('./BaseExpert');

class TouristExpert extends BaseExpert {
  constructor(deps = {}) { super('TouristExpert', deps); }
  async handle(intent, query, context, deps) {
    const destination = intent.destination;
    if (!destination) return 'مقصد گردشگری را مشخص کنید. مثال: "جاذبه‌های قشم" یا "دیدنی‌های هرمز"';

    const places = await this.getCached('tourism', destination, () => deps.knowledgeBase?.getTouristPlaces?.(destination), 86400);
    if (!places?.length) return `جاذبه‌ای برای ${destination} یافت نشد.`;

    let response = `🏝️ جاذبه‌های گردشگری ${destination}:\n`;
    for (let i = 0; i < Math.min(5, places.length); i++) {
      const place = places[i];
      response += `\n${i + 1}. ${place.name}`;
      if (place.description) response += ` - ${place.description}`;
      if (place.rating) response += ` ⭐${place.rating}`;
    }
    if (places.length > 5) response += `\n\n... و ${places.length - 5} مکان دیگر`;
    return response;
  }
}
module.exports = TouristExpert;
EOF

cat > "$PROJECT_ROOT/experts/EmergencyExpert.js" <<'EOF'
const BaseExpert = require('./BaseExpert');
const fs = require('fs');
const path = require('path');

class EmergencyExpert extends BaseExpert {
  constructor(deps = {}, configPath = './config/emergency.json') {
    super('EmergencyExpert', deps);
    const raw = fs.readFileSync(path.resolve(configPath), 'utf8');
    this.contacts = JSON.parse(raw);
  }

  _normalizeCity(city) {
    return String(city || 'default').trim().toLowerCase().replace(/\s+/g, '');
  }

  detectType(text) {
    const t = String(text || '').toLowerCase();
    if (t.includes('تصادف')) return 'accident';
    if (t.includes('پنچر')) return 'flat_tire';
    if (t.includes('خراب') || t.includes('استارت')) return 'breakdown';
    if (t.includes('آتش') || t.includes('حریق')) return 'fire';
    if (t.includes('پلیس') || t.includes('سرقت')) return 'police';
    return 'general';
  }

  async handle(intent, query, context, deps) {
    const type = this.detectType(intent.text || query);
    const loc = context.location || context.userLocation;
    const cityKey = this._normalizeCity(context.location?.city || 'default');
    const contacts = this.contacts[cityKey] || this.contacts.default;

    let res = `🚨 درخواست امداد ثبت شد\n\n`;
    switch (type) {
      case 'accident': res += `📞 اورژانس: ${contacts.emergency}\n🚔 پلیس راهور: ${contacts.police}\n`; break;
      case 'flat_tire':
      case 'breakdown': res += `🔧 در حال جستجوی امداد خودرو...\n📞 امداد خودرو: ${contacts.roadside}\n`; break;
      case 'fire': res += `📞 آتش‌نشانی: ${contacts.fire}\n`; break;
      case 'police': res += `📞 پلیس: ${contacts.police}\n`; break;
      default: res += `📞 شماره‌های اضطراری:\n`;
    }

    res += `• اورژانس: ${contacts.emergency}\n`;
    res += `• پلیس: ${contacts.police}\n`;
    res += `• آتش‌نشانی: ${contacts.fire}\n`;
    res += `• هلال احمر: ${contacts.redcrescent}\n`;
    res += `• مدیریت بحران: ${contacts.crisis || contacts.emergency}\n`;

    if (loc?.latitude && loc?.longitude) {
      res += `\n📍 موقعیت: ${loc.latitude}, ${loc.longitude}\n`;
      if (deps.emergencyService?.sendAlert) {
        try {
          await deps.emergencyService.sendAlert({ type, location: { lat: loc.latitude, lng: loc.longitude }, timestamp: new Date().toISOString(), userId: context.userId });
          res += `✅ موقعیت برای مرکز امداد ارسال شد.`;
        } catch (e) {
          res += `⚠️ خطا در ارسال. لطفاً با ${contacts.emergency} تماس بگیرید.`;
        }
      }
    } else {
      res += `\n⚠️ لطفاً GPS را فعال کنید.`;
    }
    return res;
  }
}
module.exports = EmergencyExpert;
EOF

cat > "$PROJECT_ROOT/experts/TransportExpert.js" <<'EOF'
const BaseExpert = require('./BaseExpert');

class TransportExpert extends BaseExpert {
  constructor(deps = {}) { super('TransportExpert', deps); }

  detectType(text) {
    const t = String(text || '').toLowerCase();
    if (t.includes('پرواز') || t.includes('فرودگاه')) return 'flight';
    if (t.includes('شناور') || t.includes('لندی') || t.includes('کشتی')) return 'ship';
    if (t.includes('اتوبوس')) return 'bus';
    if (t.includes('تاکسی')) return 'taxi';
    return 'transport';
  }

  async handle(intent, query, context, deps) {
    const type = this.detectType(query);
    const destination = intent.destination || null;
    const origin = context.location?.city || 'بندرعباس';
    const info = await deps.knowledgeBase?.getTransportInfo?.(type, destination, origin);
    if (!info) return `اطلاعات ${type} ${destination || ''} در دسترس نیست.`;

    let icon = '🚏';
    if (type === 'flight') icon = '✈️';
    else if (type === 'ship') icon = '🚢';
    else if (type === 'bus') icon = '🚌';
    else if (type === 'taxi') icon = '🚖';

    let response = `${icon} اطلاعات ${type}${destination ? ` برای ${destination}` : ''}:\n`;
    if (info.schedule) response += `⏰ برنامه سفر: ${info.schedule}\n`;
    if (info.price) response += `💰 هزینه: ${info.price} تومان\n`;
    if (info.duration) response += `⏱️ مدت سفر: ${info.duration}\n`;
    if (info.phone) response += `📞 رزرو/استعلام: ${info.phone}\n`;
    if (info.note) response += `💡 ${info.note}`;
    return response.trim();
  }
}
module.exports = TransportExpert;
EOF

cat > "$PROJECT_ROOT/config/emergency.json" <<'EOF'
{
  "default": {
    "emergency": "115",
    "police": "110",
    "fire": "125",
    "redcrescent": "112",
    "roadside": "076-3255-6666",
    "crisis": "076-3212-0000"
  },
  "bandarabbas": {
    "emergency": "115",
    "police": "110",
    "fire": "125",
    "redcrescent": "112",
    "roadside": "076-3255-6666",
    "crisis": "076-3212-1111"
  },
  "qeshm": {
    "emergency": "115",
    "police": "110",
    "fire": "125",
    "redcrescent": "112",
    "roadside": "076-3525-4444",
    "crisis": "076-3523-2222"
  }
}
EOF

cat > "$PROJECT_ROOT/plugins/weather/manifest.json" <<'EOF'
{
  "name": "Weather Plugin",
  "intent": "weather",
  "version": "1.0.0",
  "entry": "../../experts/WeatherExpert.js",
  "enabled": true
}
EOF

cat > "$PROJECT_ROOT/README.md" <<'EOF'
# HDP Copilot in frontend/src

Install path:

`/data/data/com.termux/files/home/hermezgan-intelligent/frontend/src/hdp-copilot`

Use from React by importing:

```javascript
const AICopilot = require('./hdp-copilot');
```
EOF

echo "Created project at: $PROJECT_ROOT"
echo "Main path: ${HOME}/hermezgan-intelligent/frontend/src/hdp-copilot"
