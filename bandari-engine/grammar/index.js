class GrammarEngine {
  constructor() {
    this.rules = [
      { name: 'حذف تکراری‌ها', pattern: (text) => text.replace(/\s+/g, ' ').trim() },
      { name: 'تصحیح حرف اضافه', pattern: (text) => text.replace(/در (خونه|بازار|مسجد)/g, 'تو $1') },
      { name: 'راست‌چین کردن فعل', pattern: (text) => text.replace(/می‌(\w+) (من|تو|او|ما|شما|آنها)/g, '$2 می‌$1') }
    ];
  }

  apply(text) {
    let result = text;
    for (const rule of this.rules) {
      result = rule.pattern(result);
    }
    return result;
  }

  detectFeatures(text) {
    const features = [];
    if (text.includes('می‌')) features.push('present_tense');
    if (text.match(/[ا]?[دت]؟[ن]؟$/) && text.length > 3) features.push('verbal_ending');
    if (text.includes('هو') || text.includes('او')) features.push('dialectal_water');
    if (text.match(/[آا]و$/)) features.push('dialectal_vowel');
    return { features, wordCount: text.split(/\s+/).filter(Boolean).length };
  }
}

module.exports = GrammarEngine;
