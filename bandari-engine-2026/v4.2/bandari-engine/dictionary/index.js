const { loadBaseWords, loadLearnedWords, persistLearnedWord } = require('./loader');
const logger = require('../utils/logger');

class Dictionary {
  constructor() {
    this.words = new Map();
    this.learned = {};
    this.wordCategory = new Map();
    this.categoryMeta = {};
    this.proverbs = {};
    this.loaded = false;
    this.totalWords = 0;
    this.loadAll();
  }

  loadAll() {
    try {
      const { words, phrases, proverbs, wordCategory, categoryMeta } = loadBaseWords();
      this._ingest(words);
      this._ingest(phrases);

      this.categoryMeta = categoryMeta;
      for (const [word, catKey] of Object.entries(wordCategory)) {
        this.wordCategory.set(word, catKey);
      }
      this.proverbs = proverbs;

      this.learned = loadLearnedWords();
      this._ingest(this.learned);

      this.loaded = true;
      logger.success(`Dictionary loaded: ${this.totalWords} entries across ${Object.keys(this.categoryMeta).length} categories (incl. ${Object.keys(this.learned).length} learned)`);
    } catch (e) {
      logger.error('خطا در بارگذاری دیکشنری:', e.message);
      this.loadFallback();
    }
  }

  getCategories() {
    return Object.entries(this.categoryMeta).map(([key, label]) => ({ key, label }));
  }

  getByCategory(catKey) {
    const result = {};
    for (const [word, cat] of this.wordCategory) {
      if (cat === catKey && this.words.has(word)) {
        result[word] = this.words.get(word);
      }
    }
    return result;
  }

  getProverbs() {
    return this.proverbs;
  }

  _ingest(pairs) {
    for (const [a, b] of Object.entries(pairs)) {
      if (!this.words.has(a)) this.totalWords++;
      this.words.set(a, b);
      this.words.set(b, a);
    }
  }

  loadFallback() {
    const fallback = {
      'سلام': 'سَلام',
      'خوب': 'خُب',
      'چطوری': 'چِطوری',
      'ممنون': 'مَمنون',
      'خداحافظ': 'خُدا نِگَهدار'
    };
    this._ingest(fallback);
    this.loaded = true;
  }

  translate(word) {
    const exact = this.words.get(word);
    if (exact) {
      return { found: true, translation: exact, confidence: 0.95, matchType: 'exact' };
    }

    // تطبیق تقریبی فقط برای کلمات با طول معنادار، برای جلوگیری از تطابق کاذب کلمات کوتاه
    if (word.length >= 3) {
      for (const [key, value] of this.words) {
        if (key.length >= 3 && (key.includes(word) || word.includes(key))) {
          return { found: true, translation: value, confidence: 0.6, matchType: 'fuzzy' };
        }
      }
    }
    return { found: false, translation: word, confidence: 0.1, matchType: 'none' };
  }

  addWord(word, translation) {
    if (!word || !translation) {
      return { added: false, reason: 'کلمه یا ترجمه خالی است' };
    }
    const isNew = !this.words.has(word);
    this.words.set(word, translation);
    this.words.set(translation, word);
    if (isNew) this.totalWords++;

    const persisted = persistLearnedWord(word, translation, this.learned);
    return { added: true, persisted, total: this.totalWords };
  }

  getStats() {
    return {
      totalWords: this.totalWords,
      loaded: this.loaded,
      learnedCount: Object.keys(this.learned).length,
      categories: Object.keys(this.categoryMeta).length,
      proverbs: Object.keys(this.proverbs).length
    };
  }
}

module.exports = Dictionary;
