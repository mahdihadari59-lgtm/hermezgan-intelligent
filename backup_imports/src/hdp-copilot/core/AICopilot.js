const path = require('path');
const PersianRegex = require('../utils/persianRegex');

const Security = require('./Security');
const Validation = require('../middleware/Validation');
const Authentication = require('../middleware/Authentication');
const RateLimiter = require('../middleware/RateLimiter');
const IntentDetector = require('./IntentDetector');
const EntityParser = require('./EntityParser');
const ContextManager = require('./ContextManager');
const SearchPipeline = require('./SearchPipeline');
const PluginManager = require('./PluginManager');
const CacheManager = require('./CacheManager');
const Logger = require('./Logger');
const Metrics = require('./Metrics');
const ShortTermMemory = require('../memory/ShortTermMemory');
const LongTermMemory = require('../memory/LongTermMemory');
const ConversationSummary = require('../memory/ConversationSummary');
const CircuitBreaker = require('./CircuitBreaker');

const RouteExpert = require('../experts/RouteExpert');
const TrafficExpert = require('../experts/TrafficExpert');
const WeatherExpert = require('../experts/WeatherExpert');
const NearbyExpert = require('../experts/NearbyExpert');
const TouristExpert = require('../experts/TouristExpert');
const EmergencyExpert = require('../experts/EmergencyExpert');
const TransportExpert = require('../experts/TransportExpert');

class AICopilot {
  constructor(deps = {}) {
    this.deps = {
      knowledgeBase: deps.knowledgeBase,
      fuzzySearch: deps.fuzzySearch,
      embeddingSearch: deps.embeddingSearch,
      emergencyService: deps.emergencyService,
      redis: deps.redis,
      contextStore: deps.contextStore
    };

    this.logger = new Logger(deps.logDir);
    this.metrics = new Metrics();
    this.cache = new CacheManager(deps.redis, { maxEntries: deps.maxCacheEntries || 5000 });
    this.security = new Security();
    this.validation = new Validation({ minLength: 1, maxLength: deps.maxQueryLength || 500 });
    this.auth = new Authentication({ required: Boolean(deps.requireAuth), allowedKeys: deps.allowedKeys || [] });
    this.rateLimiter = new RateLimiter({ windowMs: deps.rateLimitWindowMs || 60_000, maxRequests: deps.rateLimitMaxRequests || 30 });

    this.intentDetector = new IntentDetector();
    this.entityParser = new EntityParser();
    this.contextManager = new ContextManager(deps.contextStore || deps.redis);
    this.shortMemory = new ShortTermMemory({ limit: deps.shortMemoryLimit || 10, store: deps.contextStore || deps.redis });
    this.longMemory = new LongTermMemory({ store: deps.contextStore || deps.redis, ttl: deps.longMemoryTtl || 86400 });
    this.summaryBuilder = new ConversationSummary();

    this.searchPipeline = new SearchPipeline({
      knowledgeBase: deps.knowledgeBase,
      embeddingSearch: deps.embeddingSearch,
      fuzzySearch: deps.fuzzySearch,
      cacheManager: this.cache,
      logger: this.logger,
      metrics: this.metrics,
      breaker: new CircuitBreaker({ failureThreshold: 3, cooldownMs: 30000 })
    });

    this.pluginManager = new PluginManager({
      knowledgeBase: deps.knowledgeBase,
      emergencyService: deps.emergencyService,
      cacheManager: this.cache,
      logger: this.logger,
      searchPipeline: this.searchPipeline,
      metrics: this.metrics
    });

    this.defaultResponses = {
      greeting: 'سلام! چطور می‌توانم کمکتان کنم؟',
      unknown: 'متوجه نشدم. لطفاً واضح‌تر بگویید.',
      error: 'متأسفانه خطایی رخ داد. دوباره تلاش کنید.',
      blocked: 'این درخواست از نظر امنیتی قابل پردازش نیست.'
    };

    this.maxHistory = 10;
    this._registerBuiltins();

    const expertsDir = deps.expertsDir || path.join(__dirname, '..', 'experts');
    const pluginsDir = deps.pluginsDir || path.join(__dirname, '..', 'plugins');
    this.pluginManager.autoLoad({ expertsDir, pluginsDir, manifestMap: deps.intentMap || {} });
  }

  _registerBuiltins() {
    const expertDeps = {
      knowledgeBase: this.deps.knowledgeBase,
      emergencyService: this.deps.emergencyService,
      cacheManager: this.cache,
      logger: this.logger,
      searchPipeline: this.searchPipeline,
      metrics: this.metrics
    };

    this.pluginManager.register('route', new RouteExpert(expertDeps));
    this.pluginManager.register('traffic', new TrafficExpert(expertDeps));
    this.pluginManager.register('weather', new WeatherExpert(expertDeps));
    this.pluginManager.register('nearby', new NearbyExpert(expertDeps));
    this.pluginManager.register('tourist', new TouristExpert(expertDeps));
    this.pluginManager.register('emergency', new EmergencyExpert(expertDeps));
    this.pluginManager.register('transport', new TransportExpert(expertDeps));
  }

  async ask(query, context = {}) {
    const startTime = Date.now();
    const convId = context.conversationId || 'anon';
    const userId = context.userId || 'anon';
    this.metrics.increment('requests.total');

    if (!query?.trim()) {
      this.metrics.increment('requests.empty');
      return this._buildResponse(this.defaultResponses.greeting, 'greeting', 1.0, context, startTime);
    }

    try {
      const validation = this.validation.validate(query, context);
      if (!validation.ok) {
        this.metrics.increment(`validation.${validation.error}`);
        return this._buildResponse(this.defaultResponses.unknown, 'validation_error', 0, context, startTime);
      }

      const sanitizedQuery = this.security.sanitizeQuery(validation.query);
      const security = this.security.detectInjection(sanitizedQuery);
      if (security.blocked) {
        this.logger.warn({ event: 'prompt_injection_blocked', conversationId: convId, userId, reasons: security.reasons });
        this.metrics.increment('security.blocked');
        return this._buildResponse(this.defaultResponses.blocked, 'blocked', 0, context, startTime);
      }

      const auth = await this.auth.authenticate(context);
      if (!auth.ok) {
        this.metrics.increment(`auth.${auth.error}`);
        return this._buildResponse('دسترسی شما معتبر نیست.', 'auth_error', 0, context, startTime);
      }

      const limit = this.rateLimiter.check(context);
      if (!limit.allowed) {
        this.metrics.increment('ratelimit.blocked');
        return this._buildResponse(`تعداد درخواست‌ها زیاد است. لطفاً ${Math.ceil(limit.retryAfterMs / 1000)} ثانیه بعد دوباره تلاش کنید.`, 'rate_limited', 0, context, startTime);
      }

      const ctx = await this.contextManager.load(convId, {
        lastDestination: null,
        lastCategory: null,
        lastIntent: null,
        entities: {},
        history: [],
        summary: null
      });

      const shortHistory = await this.shortMemory.get(convId);
      const normalized = PersianRegex.normalize(sanitizedQuery);
      const entities = this.entityParser.parse(normalized);
      const resolvedQuery = this._resolveContext(normalized, { ...ctx, summary: ctx.summary, recent: shortHistory });

      const intents = this.intentDetector.detect(resolvedQuery, entities);
      const primary = intents[0] || { type: 'general', confidence: 0.5, score: 0 };

      const nextCtx = {
        ...ctx,
        lastDestination: entities.destination || ctx.lastDestination,
        lastCategory: entities.category || ctx.lastCategory,
        lastIntent: primary.type,
        entities: { ...(ctx.entities || {}), ...entities }
      };

      const userTurn = { role: 'user', text: sanitizedQuery, intent: primary.type, destination: entities.destination || null, category: entities.category || null, ts: Date.now() };
      await this.shortMemory.append(convId, userTurn);
      nextCtx.history = Array.isArray(nextCtx.history) ? nextCtx.history : [];
      nextCtx.history.push(userTurn);
      nextCtx.history = nextCtx.history.slice(-this.maxHistory);

      const depsForRun = { knowledgeBase: this.deps.knowledgeBase, emergencyService: this.deps.emergencyService, cacheManager: this.cache, searchPipeline: this.searchPipeline, logger: this.logger, metrics: this.metrics, defaultResponses: this.defaultResponses };

      const isMulti = intents.length > 1 && (intents[0].score - intents[1].score) < 0.15;
      let response = isMulti
        ? await this.pluginManager.routeMulti(intents, resolvedQuery, { ...context, ...nextCtx }, depsForRun)
        : await this.pluginManager.route(primary, resolvedQuery, { ...context, ...nextCtx }, depsForRun);

      if (!response) response = this.defaultResponses.unknown;

      const assistantTurn = { role: 'assistant', text: response, intent: primary.type, ts: Date.now() };
      await this.shortMemory.append(convId, assistantTurn);

      nextCtx.history.push(assistantTurn);
      nextCtx.history = nextCtx.history.slice(-this.maxHistory);

      const summary = this.summaryBuilder.build(nextCtx.history, ctx.summary || {});
      nextCtx.summary = summary;
      await this.longMemory.set(convId, summary);
      await this.contextManager.save(convId, nextCtx);

      this.metrics.recordIntent(primary.type);
      this.metrics.observe('response.ms', Date.now() - startTime);
      this.logger.info({ userId, conversationId: convId, query: sanitizedQuery, intent: primary.type, confidence: primary.confidence, responseTime: Date.now() - startTime, multiIntent: isMulti, entities });

      return this._buildResponse(response, primary.type, primary.confidence, { ...context, ...nextCtx }, startTime);
    } catch (err) {
      this.metrics.increment('requests.error');
      this.logger.error({ userId, query, error: err.message, stack: err.stack });
      return this._buildResponse(this.defaultResponses.error, 'error', 0, context, startTime);
    }
  }

  _resolveContext(text, ctx) {
    const lastDestination = ctx?.lastDestination || ctx?.summary?.lastDestination;
    if (!lastDestination) return text;
    const refs = [
      { r: /هواش|آب و هواش|دماش|آب‌وهواش/g, rep: `آب و هوای ${lastDestination}` },
      { r: /مسیرش|راهش|ترافیکش|جاده‌ش|جادش/g, rep: `مسیر ${lastDestination}` },
      { r: /جاذبه‌هاش|دیدنی‌هاش|تفریحاتش|جاهاش/g, rep: `جاذبه‌های ${lastDestination}` },
      { r: /خدماتش|امکاناتش|جاهای خدماتی‌اش/g, rep: `خدمات ${lastDestination}` }
    ];
    let resolved = text;
    for (const { r, rep } of refs) resolved = resolved.replace(r, rep);
    const vague = /(?:^|\s)(آن|این|آنجا|اینجا|همانجا|همونجا)(?:\s|$)/;
    if (vague.test(resolved) && !resolved.includes(lastDestination)) resolved = `${lastDestination} ${resolved}`;
    return resolved;
  }

  _buildResponse(text, intentType, confidence, context, startTime) {
    return {
      text,
      intent: intentType,
      confidence,
      responseTime: startTime ? Date.now() - startTime : undefined,
      conversationId: context.conversationId,
      context: { lastDestination: context.lastDestination, lastCategory: context.lastCategory, summary: context.summary || null },
      metrics: this.metrics.snapshot()
    };
  }

  getHelp() {
    return 'HDP Copilot is ready.';
  }

  getDiagnostics() {
    return {
      metrics: this.metrics.snapshot(),
      cacheSize: this.cache.size?.() || 0,
      plugins: this.pluginManager.list()
    };
  }
}

module.exports = AICopilot;
