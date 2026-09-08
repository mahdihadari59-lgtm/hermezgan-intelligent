class IntentAnalyzer {
  constructor() {
    this.intents = {
      greeting: { keywords: ['سلام', 'چطوری', 'خوبی', 'چه خبر', 'اَبی چِش', 'سَلام'], response: 'سلام! چطور می‌توانم کمک کنم؟' },
      farewell: { keywords: ['خداحافظ', 'خدا نگهدار', 'بای'], response: 'خدا نگهدار! به سلامت.' },
      translate: { keywords: ['ترجمه', 'معنی', 'یعنی چی', 'چی میشه'], response: 'در حال ترجمه...' },
      emotion: { keywords: ['دلم گرفته', 'ناراحت', 'خسته', 'واویلا'], response: 'ناراحت نباش. من کنارتم.' },
      traffic: { keywords: ['ترافیک', 'راهبندان', 'تصادف'], response: 'وضعیت ترافیک را بررسی می‌کنم.' }
    };
  }

  analyze(text) {
    let maxScore = 0;
    let bestIntent = 'general';
    for (const [intent, data] of Object.entries(this.intents)) {
      let score = 0;
      for (const keyword of data.keywords) {
        if (text.includes(keyword)) score += 1;
      }
      if (score > maxScore) { maxScore = score; bestIntent = intent; }
    }
    const confidence = maxScore > 0 ? Math.min(0.95, maxScore / 3) : 0.3;
    return { intent: bestIntent, confidence, response: this.intents[bestIntent]?.response || 'چطور می‌توانم کمک کنم؟' };
  }
}

module.exports = IntentAnalyzer;
