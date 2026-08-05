/**
 * لایه ۴: قواعد دستوری
 */
class GrammarEngine {
  constructor() {
    this.rules = [
      { name: 'حذف ن آخر فعل سوم شخص جمع', pattern: /می‌رَوَن/g, replacement: 'می‌رُن' },
      { name: 'حذف ن آخر فعل سوم شخص جمع (دار)', pattern: /دارَن/g, replacement: 'دارُن' },
      { name: 'تبدیل ست به س', pattern: /هَست/g, replacement: 'هَس' },
      { name: 'کوتاه‌سازی می‌خواهم', pattern: /می‌خواهَم/g, replacement: 'می‌خوام' },
      { name: 'کوتاه‌سازی نمی‌دانم', pattern: /نمی‌دانَم/g, replacement: 'نمی‌دونَم' }
    ];

    this.featureMarkers = {
      'کشیدگی مصوت': /(اا|وو|یی|هه)/,
      'حذف ن پایانی فعل جمع': /[^ن]رُن$/,
      'تبدیل ست به س': /هَس/,
      'ادات تعجب بندری': /واویلا/
    };
  }

  apply(text) {
    let result = text;
    for (const rule of this.rules) {
      result = result.replace(rule.pattern, rule.replacement);
    }
    return result;
  }

  detectFeatures(text) {
    const features = [];
    for (const [name, pattern] of Object.entries(this.featureMarkers)) {
      if (pattern.test(text)) features.push(name);
    }
    return features;
  }
}

module.exports = GrammarEngine;
