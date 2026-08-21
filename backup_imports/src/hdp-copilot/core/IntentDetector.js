class IntentDetector {
  constructor() {
    this.patterns = {
      emergency: { keywords: ['امداد','تصادف','پنچری','خرابی','کمک','اورژانس','آتش','پلیس','115','110','125','حریق'], regex: [/(?:تصادف|پنچر|خراب|اورژانس|آتش‌نشانی|پلیس|امداد|حریق)/, /(?:شماره|تماس)\s+(?:اورژانس|پلیس|آتش|امداد)/], weight: 1.2, priority: 1, priorityWeight: 1.0 },
      route: { keywords: ['راه','مسیر','چطور برم','چگونه بروم','فاصله','چند کیلومتر','چطوری برم','میخوام برم','می‌خوام برم','بریم','برسیم','کجاست'], regex: [/(?:راه|مسیر)\s+(?:به\s+)?(.+?)(?:\s+چطور|چگونه|کجاست|$)/, /(?:چطور|چگونه|چطوری)\s+(?:برم|بروم|برسیم)\s+(?:به\s+)?(.+)/, /(?:فاصله|مسافت)\s+(?:تا|به|از)\s+(.+)/], weight: 1.0, priority: 2, priorityWeight: 0.95 },
      traffic: { keywords: ['ترافیک','شلوغ','بسته','راه بسته','بحرانی','قفل','ترافیکی','ازدحام'], regex: [/(?:ترافیک|وضعیت راه|شلوغی)\s+(.+)/, /(.+?)\s+(?:ترافیک|شلوغ|بسته|قفل)/], weight: 1.0, priority: 2, priorityWeight: 0.9 },
      nearby: { keywords: ['نزدیک','اطراف','نزدیکم','پیدا کن','بگیر','کجاست'], regex: [/(?:نزدیک|اطراف|در نزدیکی|نزدیکم)\s+(.+)/, /(.+?)\s+(?:نزدیک|اطراف|نزدیکم)/], weight: 0.9, priority: 3, priorityWeight: 0.85 },
      weather: { keywords: ['هوا','آب و هوا','گرم','سرد','بارون','باران','شرجی','طوفان','هواش','دمای'], regex: [/(?:آب و هوا|آب‌وهوا|هوا|هوای|دمای)\s+(.+)/, /(.+?)\s+(?:هوا|آب و هوا|آب‌وهوا|هواش)/, /(?:گرمه|سرده|بارونی|طوفانی|شرجیه)/], weight: 0.9, priority: 3, priorityWeight: 0.85 },
      tourist: { keywords: ['گردشگری','تفریح','جاهای دیدنی','جاذبه','سفر','دیدن','بازدید','توریستی'], regex: [/(?:جاذبه|جاهای دیدنی|مکان‌های دیدنی|دیدنی‌های)\s+(.+)/, /(.+?)\s+(?:چی داره|جاذبه|دیدنی|تفریح)/], weight: 0.85, priority: 3, priorityWeight: 0.8 },
      transport: { keywords: ['اتوبوس','تاکسی','شناور','لندی','فرودگاه','پرواز','بندر','اسکله','حمل و نقل','ترمینال'], regex: [/(?:اتوبوس|تاکسی|شناور|لندی|پرواز|اسکله|فرودگاه)\s+(.+)/, /(.+?)\s+(?:دارید|هست|کجاست|چنده|چه موقع)/], weight: 0.9, priority: 3, priorityWeight: 0.85 },
      greeting: { keywords: ['سلام','درود','صبح بخیر','شب بخیر','هی','سلامتی','علیکم'], regex: [/^(سلام|درود|صبح بخیر|شب بخیر|هی|سلامتی|سلام علیکم)\b/], weight: 0.8, priority: 4, priorityWeight: 0.7 }
    };
  }

  detect(text, entities = {}) {
    const scored = [];
    for (const [type, cfg] of Object.entries(this.patterns)) {
      let rawScore = 0;
      let matchedKeywords = 0;
      let extractedDest = null;

      for (const kw of cfg.keywords) {
        if (text.includes(kw)) { matchedKeywords += 1; rawScore += cfg.weight * 0.35; }
      }

      if (cfg.regex) {
        for (const p of cfg.regex) {
          const m = text.match(p);
          if (m) { rawScore += cfg.weight * 0.55; if (m[1]) extractedDest = m[1].trim(); break; }
        }
      }

      const wordCount = text.split(/\s+/).filter(Boolean).length;
      const normalizedScore = Math.min(rawScore / Math.max(wordCount * 0.08, 0.5), 1.0);
      const finalScore = (normalizedScore * 0.8) + (cfg.priorityWeight * 0.2);

      if (finalScore > 0.15) {
        scored.push({
          type,
          score: parseFloat(finalScore.toFixed(3)),
          confidence: parseFloat(normalizedScore.toFixed(2)),
          priority: cfg.priority,
          matchedKeywords,
          destination: extractedDest || entities.destination || null,
          category: entities.category || null,
          feeling: entities.feeling || null,
          origin: entities.origin || null,
          text
        });
      }
    }
    scored.sort((a, b) => b.score - a.score);
    return scored;
  }
}
module.exports = IntentDetector;
