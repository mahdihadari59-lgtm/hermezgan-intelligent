const fs = require('fs');
const path = require('path');
const logger = require('../utils/logger');
const config = require('../config');

class Dictionary {
  constructor() {
    this.words = new Map();
    this.categories = new Map();
    this.phrases = new Map();
    this.proverbs = new Map();
    this.learnedWords = new Map();
    this._loadWords();
    this._loadLearned();
  }

  _loadWords() {
    try {
      const data = JSON.parse(fs.readFileSync(path.join(__dirname, 'words.json'), 'utf8'));
      for (const [categoryKey, categoryData] of Object.entries(data.categories || {})) {
        this.categories.set(categoryKey, categoryData.label);
        for (const [persian, bandari] of Object.entries(categoryData.words || {})) {
          this.words.set(persian, { translation: bandari, category: categoryKey });
        }
      }
      for (const [bandari, persian] of Object.entries(data.phrases || {})) {
        this.phrases.set(bandari, persian);
        this.words.set(persian, { translation: bandari, category: 'phrases' });
      }
      for (const [saying, meaning] of Object.entries(data.proverbs || {})) {
        this.proverbs.set(saying, meaning);
      }
      logger.success(`دیکشنری: ${this.words.size} واژه در ${this.categories.size} دسته بارگذاری شد`);
    } catch (e) {
      logger.error('خطا در بارگذاری دیکشنری:', e.message);
    }
  }

  _loadLearned() {
    try {
      if (fs.existsSync(config.LEARNED_WORDS_FILE)) {
        const data = JSON.parse(fs.readFileSync(config.LEARNED_WORDS_FILE, 'utf8'));
        for (const [persian, bandari] of Object.entries(data.learned || {})) {
          this.learnedWords.set(persian, bandari);
          this.words.set(persian, { translation: bandari, category: 'learned' });
        }
      }
    } catch (e) { logger.warn('خطا در بارگذاری واژه‌های یادگرفته‌شده:', e.message); }
  }

  _saveLearned() {
    try {
      const data = { learned: Object.fromEntries(this.learnedWords) };
      const dir = path.dirname(config.LEARNED_WORDS_FILE);
      if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
      fs.writeFileSync(config.LEARNED_WORDS_FILE, JSON.stringify(data, null, 2), 'utf8');
      return true;
    } catch (e) { logger.error('خطا در ذخیره واژه‌های یادگرفته‌شده:', e.message); return false; }
  }

  translate(word) {
    if (this.words.has(word)) {
      const result = this.words.get(word);
      return { translation: result.translation, found: true, category: result.category };
    }
    if (word.length >= 3) {
      const lower = word.toLowerCase();
      for (const [key, value] of this.words) {
        if (key.toLowerCase().includes(lower) || lower.includes(key.toLowerCase())) {
          return { translation: value.translation, found: true, category: value.category, fuzzy: true };
        }
      }
    }
    if (this.phrases.has(word)) return { translation: this.phrases.get(word), found: true, category: 'phrase' };
    return { translation: word, found: false };
  }

  addWord(persian, bandari) {
    if (this.words.has(persian)) return { added: false, persisted: true, message: 'واژه از قبل وجود دارد' };
    this.learnedWords.set(persian, bandari);
    this.words.set(persian, { translation: bandari, category: 'learned' });
    const persisted = this._saveLearned();
    return { added: true, persisted, message: 'واژه جدید اضافه شد' };
  }

  getCategories() {
    const result = {};
    for (const [key, label] of this.categories) {
      result[key] = { key, label, count: this._countCategory(key) };
    }
    return result;
  }

  _countCategory(categoryKey) {
    let count = 0;
    for (const [_, value] of this.words) {
      if (value.category === categoryKey) count++;
    }
    return count;
  }

  getByCategory(categoryKey) {
    const result = {};
    for (const [word, value] of this.words) {
      if (value.category === categoryKey) result[word] = value.translation;
    }
    return result;
  }

  getProverbs() { return Object.fromEntries(this.proverbs); }

  getStats() {
    let categoryStats = {};
    for (const [key] of this.categories) categoryStats[key] = this._countCategory(key);
    categoryStats.learned = this.learnedWords.size;
    categoryStats.phrases = this.phrases.size;
    categoryStats.proverbs = this.proverbs.size;
    return { totalWords: this.words.size, categories: categoryStats, learnedCount: this.learnedWords.size };
  }
}

module.exports = Dictionary;
