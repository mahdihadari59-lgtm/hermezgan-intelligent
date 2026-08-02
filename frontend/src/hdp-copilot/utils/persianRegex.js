class PersianRegex {
  static normalize(text) {
    return String(text ?? '')
      .replace(/\u064A/g, 'ی')
      .replace(/\u0643/g, 'ک')
      .replace(/\u200c+/g, '‌')
      .replace(/\s+/g, ' ')
      .trim();
  }

  static extractDestination(text) {
    const t = this.normalize(text);
    const m = t.match(/(?:به|تا|از|مسیر|راه|هوای|آب و هوای|جاذبه‌های|دیدنی‌های)\s+([^\s،.]+(?:\s+[^\s،.]+){0,2})/);
    return m?.[1]?.trim() || null;
  }

  static extractCategory(text) {
    const t = this.normalize(text);
    const patterns = [
      /(تعمیرگاه|پمپ بنزین|بیمارستان|داروخانه|هتل|رستوران|مسجد|بندر|اسکله|فرودگاه|مرکز خرید|بازار|اتوبوس|تاکسی|شناور|لندی)/,
    ];
    for (const p of patterns) {
      const m = t.match(p);
      if (m?.[1]) return m[1].trim();
    }
    return null;
  }

  static extractFeeling(text) {
    const t = this.normalize(text);
    const feelings = ['گرمه', 'سرده', 'شرجیه', 'طوفانیه', 'بارونیه', 'آفتابیه'];
    return feelings.find(f => t.includes(f)) || null;
  }
}
module.exports = PersianRegex;
