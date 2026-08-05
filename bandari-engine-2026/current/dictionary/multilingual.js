const fs = require('fs');
const path = require('path');
const logger = require('../utils/logger');

class MultilingualDictionary {
  constructor() {
    this.entries = [];
    this.dialects = {};
    this.dialectMeta = {};
    this._loadData();
  }

  _loadData() {
    try {
      const data = JSON.parse(fs.readFileSync(path.join(__dirname, 'multilingual_words.json'), 'utf8'));
      this.dialects = data.dialects || [];
      this.dialectMeta = data.dialect_meta || {};
      if (data.meta && data.entries) {
        this.entries = data.entries;
        logger.success(`دیکشنری چندگویشی: ${this.entries.length} ورودی بارگذاری شد`);
        return;
      }
      this.entries = data.entries || [];
      logger.success(`دیکشنری چندگویشی: ${this.entries.length} ورودی بارگذاری شد`);
    } catch (e) {
      logger.error('خطا در بارگذاری دیکشنری چندگویشی:', e.message);
      this.entries = [];
    }
  }

  translate(word, sourceDialect, targetDialect) {
    const src = this._normalizeDialect(sourceDialect);
    const tgt = this._normalizeDialect(targetDialect);
    for (const entry of this.entries) {
      if (entry.word_standard === word) return this._buildTranslationResult(entry, src, tgt);
      if (entry.dialects && entry.dialects[src] === word) return this._buildTranslationResult(entry, src, tgt);
    }
    return { found: false, word, source: sourceDialect, target: targetDialect };
  }

  _normalizeDialect(dialect) {
    const map = { 'persian': 'persian', 'ban': 'ban', 'min': 'min', 'qes': 'qes', 'jas': 'jas', 'lan': 'lan', 'bas': 'bas', 'kha': 'kha', 'rud': 'rud', 'sir': 'sir', 'bandari': 'ban', 'minabi': 'min', 'qeshm': 'qes', 'jaski': 'jas', 'langari': 'lan', 'bastaki': 'bas', 'khamiri': 'kha', 'rudani': 'rud', 'siriki': 'sir' };
    return map[dialect] || dialect;
  }

  _buildTranslationResult(entry, source, target) {
    const sourceText = source === 'persian' ? entry.word_standard : (entry.dialects?.[source] || null);
    const targetText = target === 'persian' ? entry.word_standard : (entry.dialects?.[target] || null);
    if (target !== 'persian' && !entry.dialects?.[target]) {
      return { found: true, word: sourceText, source, target, translation: null, data_quality: entry.data_quality, error: 'no_data_for_target_dialect' };
    }
    return { found: true, word: sourceText, source, target, translation: targetText, category: entry.category, subcategory: entry.subcategory, data_quality: entry.data_quality || 'unknown', confidence_score: entry.confidence_score || 70, examples: entry.examples, ipa: entry.ipa, region_usage: entry.region_usage, cultural_note: entry.cultural_note };
  }

  translateAllDialects(word, sourceDialect = 'persian') {
    const src = this._normalizeDialect(sourceDialect);
    const results = {};
    for (const entry of this.entries) {
      if (entry.word_standard === word) {
        for (const [dialect, value] of Object.entries(entry.dialects || {})) results[dialect] = value;
        if (Object.keys(results).length === 1 && results.ban) { results.persian = entry.word_standard; results[src] = results.ban; }
        return { found: true, word, source: src, translations: results, data_quality: entry.data_quality, confidence_score: entry.confidence_score, category: entry.category };
      }
      if (entry.dialects && entry.dialects[src] === word) {
        for (const [dialect, value] of Object.entries(entry.dialects || {})) results[dialect] = value;
        return { found: true, word, source: src, translations: results, data_quality: entry.data_quality, confidence_score: entry.confidence_score, category: entry.category };
      }
    }
    return { found: false, word, source: src };
  }

  searchAcrossDialects(query, limit = 20) {
    const results = [];
    const q = query.toLowerCase();
    for (const entry of this.entries) {
      if (entry.word_standard.toLowerCase().includes(q)) {
        results.push({ word: entry.word_standard, category: entry.category, dialects: entry.dialects, data_quality: entry.data_quality });
        if (results.length >= limit) break;
        continue;
      }
      if (entry.dialects) {
        let found = false;
        for (const [dialect, value] of Object.entries(entry.dialects)) {
          if (value && value.toLowerCase().includes(q)) {
            results.push({ word: entry.word_standard, dialect, translation: value, category: entry.category, data_quality: entry.data_quality });
            found = true;
            break;
          }
        }
        if (found && results.length >= limit) break;
      }
    }
    return results;
  }

  searchByCategory(category, dialectCode = 'ban') {
    const dialect = this._normalizeDialect(dialectCode);
    const results = {};
    for (const entry of this.entries) {
      if (entry.category === category) {
        const word = entry.word_standard;
        const translation = entry.dialects?.[dialect] || entry.dialects?.ban || word;
        results[word] = translation;
      }
    }
    return results;
  }

  listDialects() {
    const result = [];
    for (const [code, meta] of Object.entries(this.dialectMeta)) {
      const count = this.entries.filter(e => e.dialects && e.dialects[code]).length;
      result.push({ code, label: meta.label, region: meta.region, population: meta.population, wordCount: count });
    }
    return result;
  }

  getDialectInfo(code) {
    const dialect = this._normalizeDialect(code);
    const meta = this.dialectMeta[dialect];
    if (!meta) return null;
    const count = this.entries.filter(e => e.dialects && e.dialects[dialect]).length;
    return { ...meta, code: dialect, wordCount: count, verifiedCount: this.entries.filter(e => e.dialects && e.dialects[dialect] && e.data_quality === 'verified').length };
  }

  getStats() {
    const dialectStats = {};
    for (const [code] of Object.entries(this.dialectMeta)) {
      dialectStats[code] = this.entries.filter(e => e.dialects && e.dialects[code]).length;
    }
    return { totalEntries: this.entries.length, verifiedEntries: this.entries.filter(e => e.data_quality === 'verified').length, sourcedEntries: this.entries.filter(e => e.data_quality === 'sourced').length, dialects: dialectStats, categories: this._getCategoryStats() };
  }

  _getCategoryStats() {
    const stats = {};
    for (const entry of this.entries) stats[entry.category] = (stats[entry.category] || 0) + 1;
    return stats;
  }
}

module.exports = MultilingualDictionary;
