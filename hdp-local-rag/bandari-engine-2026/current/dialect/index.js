const logger = require('../utils/logger');

class DialectDetector {
  constructor() {
    this.dialects = {
      bandari: { label: 'بندری', markers: ['هو', 'جویی', 'مُم', 'برار', 'خاهر', 'ابی چش', 'خدا نگهدار', 'حرما'], soundPatterns: ['آب → هو'], region: 'بندرعباس' },
      minabi: { label: 'مینابی', markers: ['چَکری', 'مار', 'او'], soundPatterns: ['من → مو', 'چطوری → چکری'], region: 'میناب' },
      qeshm: { label: 'قشمی', markers: ['سَلام قِشمی', 'جزیره'], soundPatterns: ['آب → او'], region: 'جزیره قشم' },
      jaski: { label: 'جاسکی', markers: ['میگو', 'سَلام'], soundPatterns: [], region: 'جاسک' },
      langari: { label: 'لنگه‌ای', markers: ['بادگیر', 'سَلام چَکری'], soundPatterns: [], region: 'بندر لنگه' },
      bastaki: { label: 'بستکی', markers: ['قلعه', 'برکه'], soundPatterns: [], region: 'بستک' },
      khamiri: { label: 'خمیری', markers: ['اسکله', 'صیادی'], soundPatterns: [], region: 'خمیر' },
      rudani: { label: 'رودانی', markers: ['چَگُری', 'مار', 'خدا نِگَهدار', 'آو'], soundPatterns: ['من → مو'], region: 'رودان' },
      siriki: { label: 'سیریکی', markers: ['سَلام'], soundPatterns: [], region: 'سیریک' }
    };
    logger.debug(`${Object.keys(this.dialects).length} گویش برای تشخیص بارگذاری شد`);
  }

  detect(text) {
    const scores = {};
    let totalScore = 0;
    for (const [key, dialect] of Object.entries(this.dialects)) {
      let score = 0;
      for (const marker of dialect.markers) {
        if (text.includes(marker)) score += 2;
      }
      for (const pattern of dialect.soundPatterns) {
        const [, dialectal] = pattern.split(' → ');
        if (text.includes(dialectal)) score += 3;
      }
      scores[key] = score;
      totalScore += score;
    }
    let bestDialect = 'bandari';
    let bestScore = 0;
    for (const [key, score] of Object.entries(scores)) {
      if (score > bestScore) { bestScore = score; bestDialect = key; }
    }
    const confidence = totalScore > 0 ? Math.min(0.95, bestScore / (totalScore + 1)) : 0.3;
    return { dialect: bestDialect, label: this.dialects[bestDialect]?.label || bestDialect, confidence, scores, detectedMarkers: this._getDetectedMarkers(text, bestDialect) };
  }

  _getDetectedMarkers(text, dialectKey) {
    const dialect = this.dialects[dialectKey];
    if (!dialect) return [];
    const detected = [];
    for (const marker of dialect.markers) {
      if (text.includes(marker)) detected.push(marker);
    }
    return detected;
  }
}

module.exports = DialectDetector;
