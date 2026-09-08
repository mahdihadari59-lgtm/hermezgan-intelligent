const fs = require('fs');
const path = require('path');
const logger = require('../utils/logger');

class RAGEngine {
  constructor() {
    this.samples = new Map();
    this.knowledge = new Map();
    this._loadKnowledge();
    logger.debug(`RAG: ${this.samples.size} نمونه بارگذاری شد`);
  }

  _loadKnowledge() {
    try {
      const knowledgePath = path.join(__dirname, '..', 'knowledge', 'local_knowledge.json');
      if (fs.existsSync(knowledgePath)) {
        const data = JSON.parse(fs.readFileSync(knowledgePath, 'utf8'));
        for (const entry of data.entries || []) {
          this.addSample(entry.title, entry.content);
          if (!this.knowledge.has(entry.category)) this.knowledge.set(entry.category, []);
          this.knowledge.get(entry.category).push(entry);
        }
        logger.debug(`RAG: ${data.entries?.length || 0} مدخل دانش محلی بارگذاری شد`);
      }
    } catch (e) { logger.debug('هیچ دانش محلی بارگذاری نشد'); }
  }

  addSample(query, response) {
    const key = query.trim().toLowerCase();
    if (key.length > 0) this.samples.set(key, response);
  }

  search(query) {
    const key = query.trim().toLowerCase();
    if (this.samples.has(key)) return { found: true, response: this.samples.get(key), confidence: 0.95 };
    for (const [sampleKey, response] of this.samples) {
      if (sampleKey.includes(key) || key.includes(sampleKey)) {
        return { found: true, response, confidence: 0.8, fuzzy: true };
      }
    }
    return { found: false, confidence: 0 };
  }

  searchKnowledge(query, category = null) {
    const key = query.trim().toLowerCase();
    const results = [];
    const entries = category ? (this.knowledge.get(category) || []) : Array.from(this.knowledge.values()).flat();
    for (const entry of entries) {
      if (entry.title.toLowerCase().includes(key) || entry.content.toLowerCase().includes(key)) {
        results.push(entry);
      }
    }
    return results.slice(0, 10);
  }

  getStats() {
    return { samples: this.samples.size, knowledgeCategories: this.knowledge.size, totalKnowledgeEntries: Array.from(this.knowledge.values()).reduce((sum, arr) => sum + arr.length, 0) };
  }
}

module.exports = RAGEngine;
