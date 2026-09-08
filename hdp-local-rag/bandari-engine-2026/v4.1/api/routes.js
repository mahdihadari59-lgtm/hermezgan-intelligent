const express = require('express');
const logger = require('../utils/logger');

function createRoutes(engines) {
  const { dictionary, multilingual, rag, grammar, intent, dialect, morphology, context, llm } = engines;
  const router = express.Router();

  function requireText(req, res) {
    const { text } = req.body || {};
    if (!text || typeof text !== 'string' || !text.trim()) {
      res.status(400).json({ error: 'متن را وارد کنید' });
      return null;
    }
    return text.trim();
  }

  // خط‌لولهٔ اصلی ترجمه: RAG -> LLM (اختیاری) -> دیکشنری واژه‌به‌واژه + گرامر
  async function runTranslationPipeline(text, sessionId) {
    const dialectResult = dialect.detect(text);
    const intentResult = intent.analyze(text);
    const history = context.getHistory(sessionId);

    const ragResult = rag.search(text);
    if (ragResult.found) {
      context.addTurn(sessionId, { text, translation: ragResult.response, source: 'rag' });
      return {
        success: true,
        translation: ragResult.response,
        intent: intentResult.intent,
        dialect: dialectResult.dialect,
        confidence: ragResult.confidence,
        source: 'rag'
      };
    }

    const llmResult = await llm.translate(text, history);
    if (llmResult.used) {
      context.addTurn(sessionId, { text, translation: llmResult.translation, source: 'llm' });
      return {
        success: true,
        translation: llmResult.translation,
        intent: intentResult.intent,
        dialect: dialectResult.dialect,
        confidence: llmResult.confidence,
        source: 'llm'
      };
    }

    const words = text.split(/\s+/).filter(Boolean);
    const translatedWords = [];
    let matched = 0;
    for (const word of words) {
      const result = dictionary.translate(word);
      translatedWords.push(result.translation);
      if (result.found) matched++;
    }

    let translation = grammar.apply(translatedWords.join(' '));
    const confidence = matched > 0 ? Math.min(0.95, matched / words.length) : 0.3;

    context.addTurn(sessionId, { text, translation, source: 'dictionary' });

    return {
      success: true,
      translation,
      original: text,
      intent: intentResult.intent,
      dialect: dialectResult.dialect,
      confidence,
      matchedWords: matched,
      totalWords: words.length,
      source: 'dictionary'
    };
  }

  // =====================================================
  // اندپوینت‌های v4.2 — دیکشنری ۹-گویشی (multilingual)
  // کدهای گویش: ban, min, qes, jas, lan, bas, kha, rud, sir + 'persian'
  // =====================================================

  router.post('/multilingual/translate', (req, res) => {
    const { word, source, target } = req.body || {};
    if (!word || !source || !target) {
      return res.status(400).json({ error: 'word، source و target را وارد کنید' });
    }
    const result = multilingual.translate(word, source, target);
    if (!result.found) return res.status(404).json(result);
    res.json(result);
  });

  router.post('/multilingual/translate-all', (req, res) => {
    const { word, source } = req.body || {};
    if (!word) return res.status(400).json({ error: 'word را وارد کنید' });
    const result = multilingual.translateAllDialects(word, source || 'persian');
    if (!result.found) return res.status(404).json(result);
    res.json(result);
  });

  router.get('/multilingual/search', (req, res) => {
    const q = req.query.q;
    if (!q) return res.status(400).json({ error: 'پارامتر q را وارد کنید' });
    const limit = req.query.limit ? parseInt(req.query.limit, 10) : 20;
    res.json({ results: multilingual.searchAcrossDialects(q, limit) });
  });

  router.get('/multilingual/category/:category', (req, res) => {
    const dialectCode = req.query.dialect || 'ban';
    const results = multilingual.searchByCategory(req.params.category, dialectCode);
    res.json({ category: req.params.category, dialect: dialectCode, results });
  });

  router.get('/multilingual/dialects', (req, res) => {
    res.json({ dialects: multilingual.listDialects() });
  });

  router.get('/multilingual/dialects/:code', (req, res) => {
    const info = multilingual.getDialectInfo(req.params.code);
    if (!info) return res.status(404).json({ error: 'کد گویش نامعتبر است' });
    res.json(info);
  });

  router.get('/multilingual/stats', (req, res) => {
    res.json(multilingual.getStats());
  });

  router.post('/translate', async (req, res) => {
    const text = requireText(req, res);
    if (!text) return;
    const sessionId = req.body.sessionId || null;
    try {
      const result = await runTranslationPipeline(text, sessionId);
      res.json(result);
    } catch (e) {
      logger.error('خطا در ترجمه:', e.message);
      res.status(500).json({ error: 'خطای داخلی سرور' });
    }
  });

  router.post('/detect', (req, res) => {
    const text = requireText(req, res);
    if (!text) return;
    const features = grammar.detectFeatures(text);
    const dialectResult = dialect.detect(text);
    res.json({
      dialect: dialectResult.dialect,
      dialectLabel: dialectResult.label,
      confidence: dialectResult.confidence,
      scores: dialectResult.scores,
      grammarFeatures: features
    });
  });

  router.post('/morphology', (req, res) => {
    const text = requireText(req, res);
    if (!text) return;
    res.json({ analysis: morphology.analyzeText(text) });
  });

  router.post('/intent', (req, res) => {
    const text = requireText(req, res);
    if (!text) return;
    res.json(intent.analyze(text));
  });

  router.post('/learn', (req, res) => {
    const { word, translation } = req.body || {};
    if (!word || !translation) {
      return res.status(400).json({ error: 'کلمه و ترجمه را وارد کنید' });
    }
    const dictResult = dictionary.addWord(word, translation);
    rag.addSample(word, translation);
    res.json({ success: dictResult.added, persisted: dictResult.persisted, message: 'واژه جدید اضافه شد' });
  });

  router.get('/dictionary/categories', (req, res) => {
    res.json({ categories: dictionary.getCategories() });
  });

  router.get('/dictionary/category/:key', (req, res) => {
    const words = dictionary.getByCategory(req.params.key);
    if (Object.keys(words).length === 0) {
      return res.status(404).json({ error: 'دسته‌ای با این کلید پیدا نشد' });
    }
    res.json({ category: req.params.key, words });
  });

  router.get('/context/:sessionId', (req, res) => {
    res.json({ history: context.getHistory(req.params.sessionId, 20) });
  });

  router.get('/stats', (req, res) => {
    res.json({
      dictionary: dictionary.getStats(),
      multilingual: multilingual.getStats(),
      rag: rag.getStats(),
      context: context.getStats(),
      llmEnabled: llm.enabled,
      version: '4.2.0'
    });
  });

  router.get('/health', (req, res) => {
    res.json({ status: 'online', version: '4.2.0' });
  });

  return router;
}

module.exports = createRoutes;
