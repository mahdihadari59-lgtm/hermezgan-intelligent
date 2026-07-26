/**
 * لایه ۷: دانش‌نامه RAG (نسخه سبک، بدون وابستگی به وکتور دیتابیس خارجی)
 */
class RAGEngine {
  constructor() {
    this.knowledge = new Map();
    this.loadSamples();
  }

  loadSamples() {
    const samples = [
      { query: 'دلم گرفته', response: 'ناراحت نباش. همه چی درست میشه.' },
      { query: 'خسته‌ام', response: 'خسته نباشی. یه استراحت کن.' },
      { query: 'واویلا', response: 'واویلا یعنی وای خدای من! (تعجب)' },
      { query: 'اَبی چِش', response: 'اَبی چِش یعنی حالت چطوره؟' },
      { query: 'دِلِمی', response: 'دِلِمی یعنی عزیز دلم.' },
      { query: 'چِطوری مِردُم', response: 'چِطوری مِردُم یعنی چطوری مردم؟' },
      { query: 'سَلام خَری', response: 'سَلام خَری یعنی سلام رفیق.' },
      { query: 'خُبَه رَه', response: 'خُبَه رَه یعنی خوبی رفیق؟' }
    ];
    for (const s of samples) this.knowledge.set(s.query, s.response);
  }

  search(query) {
    if (this.knowledge.has(query)) {
      return { found: true, response: this.knowledge.get(query), confidence: 0.95 };
    }
    for (const [key, value] of this.knowledge) {
      if (query.includes(key) || key.includes(query)) {
        return { found: true, response: value, confidence: 0.7 };
      }
    }
    return { found: false, response: null, confidence: 0 };
  }

  addSample(query, response) {
    this.knowledge.set(query, response);
    return { added: true, total: this.knowledge.size };
  }

  getStats() {
    return { totalSamples: this.knowledge.size };
  }
}

module.exports = RAGEngine;
