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
