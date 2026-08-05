const fs = require('fs');
const path = require('path');
const logger = require('../utils/logger');

const DIALECT_CODES = ['ban', 'min', 'qes', 'jas', 'lan', 'bas', 'kha', 'rud', 'sir'];
const DIALECT_NAMES = {
  ban: 'بندری', min: 'مینابی', qes: 'قشمی', jas: 'جاسکی',
  lan: 'لنگه‌ای', bas: 'بستکی', kha: 'خمیری', rud: 'رودانی', sir: 'سیریکی'
};

class MultilingualDictionary {
  constructor() {
    this.entries = [];
    this.meta = {};
    this.byId = new Map();
    // ایندکس معکوس: هر واژه گویشی (هر زبانی) -> فهرست entryId هایی که توش هست
    this.reverseIndex = new Map();
    this.loaded = false;
    this.load();
  }

  load() {
    try {
      const raw = fs.readFileSync(
        path.join(__dirname, 'multilingual_words.json'),
        'utf8'
      );
      const data = JSON.parse(raw);
      this.meta = data.meta || {};
      this.entries = data.entries || [];

      for (const entry of this.entries) {
        this.byId.set(entry.id, entry);
        this._indexEntry(entry);
      }

      this.loaded = true;
      logger.success(
        `Multilingual dictionary loaded: ${this.entries.length} entries (${this.meta.verified_entries} verified, ${this.meta.sourced_entries} sourced)`
      );
    } catch (e) {
      logger.error('خطا در بارگذاری دیکشنری چندزبانه:', e.message);
      this.entries = [];
      this.loaded = false;
    }
  }

  _indexEntry(entry) {
    const addTerm = (term) => {
      if (!term) return;
      if (!this.reverseIndex.has(term)) this.reverseIndex.set(term, []);
      this.reverseIndex.get(term).push(entry.id);
    };
    addTerm(entry.word_standard);
    if (entry.dialects) {
      for (const code of DIALECT_CODES) addTerm(entry.dialects[code]);
    }
  }

  isValidDialect(code) {
    return code === 'persian' || DIALECT_CODES.includes(code);
  }

  dialectName(code) {
    return code === 'persian' ? 'فارسی' : DIALECT_NAMES[code] || code;
  }

  /**
   * پیدا کردن entryهایی که یک واژه در یک گویش/فارسی مشخص بهشون اشاره داره
   */
  findEntriesByTerm(term, dialectCode) {
    const ids = this.reverseIndex.get(term) || [];
    return ids
      .map((id) => this.byId.get(id))
      .filter((e) => {
        if (dialectCode === 'persian') return e.word_standard === term;
        return e.dialects && e.dialects[dialectCode] === term;
      });
  }

  /**
   * ترجمه یک واژه از یک گویش/فارسی به گویش/فارسی دیگر
   */
  translate(word, sourceDialect, targetDialect) {
    if (!this.isValidDialect(sourceDialect) || !this.isValidDialect(targetDialect)) {
      return { found: false, reason: 'invalid_dialect' };
    }
    const matches = this.findEntriesByTerm(word, sourceDialect);
    if (matches.length === 0) {
      return { found: false, reason: 'not_found' };
    }
    const entry = matches[0];
    const translated = targetDialect === 'persian' ? entry.word_standard : entry.dialects[targetDialect];
    if (!translated) {
      return {
        found: false,
        reason: 'no_data_for_target_dialect',
        entry_definition: entry.definition,
        data_quality: entry.data_quality
      };
    }
    return {
      found: true,
      original: word,
      translated,
      source_dialect: this.dialectName(sourceDialect),
      target_dialect: this.dialectName(targetDialect),
      definition: entry.definition,
      example: entry.examples ? entry.examples[targetDialect] || entry.examples.ban : undefined,
      confidence: (entry.confidence_score || 70) / 100,
      data_quality: entry.data_quality,
      category: entry.category
    };
  }

  translateAllDialects(word, sourceDialect = 'persian') {
    const matches = this.findEntriesByTerm(word, sourceDialect);
    if (matches.length === 0) return { found: false, reason: 'not_found' };
    const entry = matches[0];
    const result = { persian: entry.word_standard };
    for (const code of DIALECT_CODES) {
      if (entry.dialects && entry.dialects[code]) {
        result[this.dialectName(code)] = entry.dialects[code];
      }
    }
    return { found: true, definition: entry.definition, translations: result, data_quality: entry.data_quality };
  }

  searchAcrossDialects(query, limit = 20) {
    const results = [];
    const q = query.trim();
    if (!q) return results;
    for (const entry of this.entries) {
      let matched = false;
      const hitDialects = [];
      if (entry.word_standard && entry.word_standard.includes(q)) matched = true;
      if (entry.dialects) {
        for (const code of DIALECT_CODES) {
          if (entry.dialects[code] && entry.dialects[code].includes(q)) {
            matched = true;
            hitDialects.push(code);
          }
        }
      }
      if (matched) {
        results.push({
          id: entry.id,
          word_standard: entry.word_standard,
          definition: entry.definition,
          category: entry.category,
          subcategory: entry.subcategory,
          matched_dialects: hitDialects,
          dialects: entry.dialects,
          data_quality: entry.data_quality
        });
      }
      if (results.length >= limit) break;
    }
    return results;
  }

  searchByCategory(category, dialectCode = 'ban', limit = 50) {
    return this.entries
      .filter((e) => e.category === category && e.dialects && e.dialects[dialectCode])
      .slice(0, limit)
      .map((e) => ({
        word_standard: e.word_standard,
        translation: e.dialects[dialectCode],
        definition: e.definition,
        example: e.examples ? e.examples[dialectCode] : undefined,
        subcategory: e.subcategory
      }));
  }

  getDialectInfo(dialectCode) {
    if (!DIALECT_CODES.includes(dialectCode)) return null;
    const withWord = this.entries.filter((e) => e.dialects && e.dialects[dialectCode]);
    return {
      code: dialectCode,
      name: this.dialectName(dialectCode),
      total_words: withWord.length,
      sample_words: withWord.slice(0, 5).map((e) => ({
        persian: e.word_standard,
        dialect: e.dialects[dialectCode],
        definition: e.definition
      }))
    };
  }

  listDialects() {
    return DIALECT_CODES.map((code) => this.getDialectInfo(code));
  }

  getStats() {
    return {
      totalEntries: this.entries.length,
      verified: this.meta.verified_entries || 0,
      sourced: this.meta.sourced_entries || 0,
      dialectWordCounts: this.meta.dialect_word_counts || {},
      loaded: this.loaded
    };
  }
}

module.exports = MultilingualDictionary;
module.exports.DIALECT_CODES = DIALECT_CODES;
module.exports.DIALECT_NAMES = DIALECT_NAMES;
