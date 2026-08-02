class EntityParser {
  constructor() {
    this.destinationAliases = [
      { pattern: /^(بندر\s?عباس|بندرعباس|bandar\s*abbas)$/i, value: 'بندرعباس' },
      { pattern: /^(قشم|جزیره\s*قشم|qeshm)$/i, value: 'قشم' },
      { pattern: /^(کیش|kish)$/i, value: 'کیش' },
      { pattern: /^(میناب|minab)$/i, value: 'میناب' },
      { pattern: /^(هرمز|hormuz)$/i, value: 'هرمز' },
      { pattern: /^(جاسک|jask)$/i, value: 'جاسک' },
      { pattern: /^(بستک|bastak)$/i, value: 'بستک' },
      { pattern: /^(رودان|rudan)$/i, value: 'رودان' },
      { pattern: /^(پارسیان|parsian)$/i, value: 'پارسیان' },
      { pattern: /^(حاجی\s?آباد|حاجی‌آباد|hajiabad)$/i, value: 'حاجی‌آباد' }
    ];

    this.categoryAliases = [
      { pattern: /(تعمیرگاه|مکانیک|صافکاری|پنچرگیری)/, value: 'تعمیرگاه' },
      { pattern: /(پمپ\s?بنزین|جایگاه\s?سوخت|cng)/i, value: 'پمپ بنزین' },
      { pattern: /(بیمارستان|درمانگاه|اورژانس|کلینیک)/, value: 'بیمارستان' },
      { pattern: /(داروخانه)/, value: 'داروخانه' },
      { pattern: /(هتل|اقامتگاه|مهمانپذیر)/, value: 'هتل' },
      { pattern: /(رستوران|غذاخوری|کافه)/, value: 'رستوران' },
      { pattern: /(مسجد|حسینیه|امامزاده)/, value: 'مسجد' },
      { pattern: /(بندر|اسکله|ترمینال|فرودگاه)/, value: 'حمل و نقل' },
      { pattern: /(مرکز\s?خرید|بازار|مال)/, value: 'مرکز خرید' },
      { pattern: /(اتوبوس|تاکسی|شناور|لندی|پرواز)/, value: 'حمل و نقل' }
    ];

    this.destinationPatterns = [
      /(?:راه|مسیر|به|تا|برم|برسیم|بریم|فاصله|آب و هوای|هوای|جاذبه‌های|دیدنی‌های|دیدنی های|جاذبه های)\s+([^\s،.]+(?:\s+[^\s،.]+){0,2})/,
      /([^\s]+(?:\s+[^\s]+){0,2})\s+(?:کجاست|چطوره|چگونه است|چند کیلومتر|چقدر دوره|هواش|آب و هواش)/,
      /(?:می‌خوام|میخوام|می خوام|برویم|بریم|برم)\s+(?:به\s+)?([^\s،.]+(?:\s+[^\s،.]+){0,2})/,
      /(?:یه\s+)?(?:مسیر|راه)\s+(?:تا|به|از\s+[^\s]+\s+تا|از\s+[^\s]+\s+به)?\s*([^\s،.]+(?:\s+[^\s،.]+){0,2})/
    ];

    this.radiusPatterns = [
      /(?:شعاع|در|تا|تا\s+حدود)\s*(\d+)\s*(?:کیلومتر|کیلومتری|km|متر|متری|m)/i,
      /(\d+)\s*(?:کیلومتر|کیلومتری|km|متر|متری|m)\s*(?:شعاع|اطراف|نزدیک)/i
    ];

    this.feelingPatterns = ['گرمه', 'سرده', 'شرجیه', 'طوفانیه', 'بارونیه', 'آفتابیه'];
  }

  parse(text) {
    const categoryPatterns = this.categoryAliases.map(item => item.pattern);
    const entities = {
      destination: this._canonicalDestination(this._extract(text, this.destinationPatterns)),
      radius: this._extractRadius(text),
      category: this._canonicalCategory(this._extract(text, categoryPatterns)),
      feeling: this._extractFeeling(text),
      origin: null
    };

    const routeMatch = text.match(/از\s+([^\s،.]+(?:\s+[^\s،.]+){0,2})\s+تا\s+([^\s،.]+(?:\s+[^\s،.]+){0,2})/);
    if (routeMatch) {
      entities.origin = this._canonicalDestination(routeMatch[1].trim());
      entities.destination = this._canonicalDestination(routeMatch[2].trim());
    }
    return entities;
  }

  _extract(text, patterns) {
    for (const pattern of patterns) {
      const m = text.match(pattern);
      if (m && m[1]) return m[1].trim();
    }
    return null;
  }

  _extractRadius(text) {
    const m = text.match(this.radiusPatterns[0]) || text.match(this.radiusPatterns[1]);
    if (m) {
      let val = parseInt(m[1], 10);
      if (text.includes('متر') || text.includes('m')) val = val / 1000;
      return val;
    }
    if (/(نزدیک|اطراف|نزدیکم|اطرافم)/.test(text)) return 5;
    return null;
  }

  _extractFeeling(text) {
    for (const feeling of this.feelingPatterns) {
      if (text.includes(feeling)) return feeling;
    }
    return null;
  }

  _canonicalDestination(value) {
    if (!value) return null;
    const cleaned = value.trim();
    for (const item of this.destinationAliases) {
      if (item.pattern.test(cleaned)) return item.value;
    }
    return cleaned;
  }

  _canonicalCategory(value) {
    if (!value) return null;
    const cleaned = value.trim();
    for (const item of this.categoryAliases) {
      if (item.pattern.test(cleaned)) return item.value;
    }
    return cleaned;
  }
}
module.exports = EntityParser;
