/**
 * لایه ۱: تشخیص گویش
 * بر اساس نشانگرهای واژگانی، احتمال تعلق متن به هرکدام از ۹ گویش/زبان
 * رایج استان هرمزگان را تخمین می‌زند. نشانگرها از دو منبع می‌آیند:
 *  - ویژگی شاخص هر گویش طبق جدول مستندات («تبدیل آب به هو» و مشابه)
 *  - واژه‌های واقعی موجود در dictionary/multilingual_words.json
 */
class DialectDetector {
  constructor() {
    this.dialects = {
      ban: {
        label: 'بندری (بندرعباس)',
        population: 680000,
        markers: ['هو', 'خَری', 'مِردُم', 'وَاویلا', 'اَبی چِش', 'دِلِمی', 'خُبَه رَه', 'خون جاده', 'لنج خشکی', 'حرما', 'نغال', 'جویی']
      },
      min: {
        label: 'مینابی (میناب)',
        population: 80000,
        markers: ['چَک', 'چَکری', 'یِنی', 'گُشنِه', 'اَمرُز', 'هَمِش']
      },
      qes: {
        label: 'قشمی (جزیره قشم)',
        population: 150000,
        markers: ['او', 'دریا', 'لَنج', 'صیاد', 'قِشمی']
      },
      jas: {
        label: 'جاسکی (جاسک)',
        population: 60000,
        markers: ['صیادی']
      },
      lan: {
        label: 'لنگه‌ای (بندر لنگه)',
        population: 50000,
        markers: ['چَکری']  // حفظ «چَکری» طبق ویژگی شاخص، مشترک با مینابی
      },
      bas: {
        label: 'بستکی (بستک)',
        population: 40000,
        markers: ['برکه', 'بایی', 'بی‌بی']
      },
      kha: {
        label: 'خمیری (خمیر)',
        population: 35000,
        markers: []  // طبق مستندات: «ترکیب با گویش‌های غربی»، نشانگر اختصاصی مجزا گزارش نشده
      },
      rud: {
        label: 'رودانی (رودان)',
        population: 80000,
        markers: ['مو', 'چَگُری', 'مار', 'آو']
      },
      sir: {
        label: 'سیریکی (سیریک)',
        population: 30000,
        markers: []  // طبق مستندات: «اصطلاحات شرقی»، نشانگر اختصاصی مجزا گزارش نشده
      }
    };
  }

  detect(text) {
    const scores = {};
    for (const [key, data] of Object.entries(this.dialects)) {
      let score = 0;
      for (const marker of data.markers) {
        if (marker && text.includes(marker)) score++;
      }
      scores[key] = score;
    }

    const sorted = Object.entries(scores).sort((a, b) => b[1] - a[1]);
    const [topDialect, topScore] = sorted[0];

    if (topScore === 0) {
      return { dialect: 'unknown', label: 'نامشخص', confidence: 0.2, scores };
    }

    const totalHits = Object.values(scores).reduce((a, b) => a + b, 0);
    const confidence = Math.min(0.95, 0.4 + (topScore / Math.max(1, totalHits)) * 0.5);

    return {
      dialect: topDialect,
      label: this.dialects[topDialect].label,
      confidence,
      scores
    };
  }

  listDialects() {
    return Object.entries(this.dialects).map(([code, d]) => ({
      code,
      label: d.label,
      population: d.population,
      markerCount: d.markers.length
    }));
  }
}

module.exports = DialectDetector;
