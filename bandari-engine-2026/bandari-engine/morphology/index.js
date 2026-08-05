/**
 * لایه ۳: ریخت‌شناسی (Morphology)
 * تشخیص سادهٔ ریشه فعل، زمان دستوری و پسوند صرفی بر اساس الگوهای رایج بندری.
 * این یک تحلیل‌گر قاعده‌محور سبک است، نه یک مدل کامل صرفی.
 */
class MorphologyAnalyzer {
  constructor() {
    // پسوندهای رایج زمان/صرف در گویش بندری، به ترتیب طول (بلندتر اول)
    this.suffixPatterns = [
      { suffix: 'یدَن', tense: 'infinitive' },
      { suffix: 'دَن', tense: 'infinitive' },
      { suffix: 'َن', tense: 'present_plural' }, // مثل: دارَن، می‌رَوَن (فتحه + ن)
      { suffix: 'ُن', tense: 'present_plural_short' }, // مثل: دارُن، می‌رُن
      { suffix: 'یدِم', tense: 'past_1s' },
      { suffix: 'یدی', tense: 'past_2s' },
      { suffix: 'یدِه', tense: 'past_3s' },
      { suffix: 'ِم', tense: 'first_person_marker' },
      { suffix: 'ی', tense: 'second_person_marker' }
    ];
  }

  analyzeWord(word) {
    for (const { suffix, tense } of this.suffixPatterns) {
      if (word.endsWith(suffix) && word.length > suffix.length) {
        return {
          word,
          root: word.slice(0, word.length - suffix.length),
          suffix,
          tenseGuess: tense
        };
      }
    }
    return { word, root: word, suffix: null, tenseGuess: 'unknown' };
  }

  analyzeText(text) {
    const words = text.split(/\s+/).filter(Boolean);
    return words.map((w) => this.analyzeWord(w));
  }
}

module.exports = MorphologyAnalyzer;
