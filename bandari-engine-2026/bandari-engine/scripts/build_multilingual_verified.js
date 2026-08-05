// این اسکریپت dictionary/multilingual_words.json را از داده‌های واقعی مستندات
// (نه حدس زبان‌شناختی من) تولید می‌کند. دو منبع کیفیت متفاوت دارند:
//  - "verified": از سند دیکشنری چندزبانه، با IPA/مثال/امتیاز اطمینان واقعی (۹۰-۹۵)
//  - "sourced": از اسناد شهرستان‌ها/فرهنگ/رانندگی، فقط داده بندری (بدون ۸ گویش دیگر)
const fs = require('fs');
const path = require('path');

const entries = [];

function addVerified(e) {
  entries.push({ ...e, confidence_score: e.confidence_score ?? 80, data_quality: 'verified' });
}
function addSourced(e) {
  entries.push({ ...e, confidence_score: e.confidence_score ?? 75, data_quality: 'sourced' });
}

// =====================================================================
// بخش ۱: نمونه‌های واقعی ۹-گویشی از «دیکشنری تخصصی چندزبانه هرمزگان»
// =====================================================================

addVerified({
  word_standard: 'سلام', part_of_speech: 'interjection', category: 'greeting', subcategory: 'greeting',
  definition: 'سلام کردن، احوالپرسی',
  dialects: { ban: 'سَلام براری', min: 'سَلام چَکری؟', qes: 'سَلام قِشمی', jas: 'سَلام', lan: 'سَلام چَکری؟', bas: 'سَلام', kha: 'سَلام', rud: 'سَلام چَگُری؟', sir: 'سَلام' },
  ipa: { ban: 'sælɒːm bærɒːriː', min: 'sælɒːm tʃækriː' },
  examples: { ban: 'سَلام براری چطوری؟', min: 'سَلام چَکری؟' },
  region_usage: 'همه مناطق', etymology: 'عربی', cultural_note: 'رایج‌ترین احوالپرسی', confidence_score: 90
});

addVerified({
  word_standard: 'چطوری', part_of_speech: 'question', category: 'greeting', subcategory: 'question',
  definition: 'پرسیدن حال و احوال',
  dialects: { ban: 'ابی چش', min: 'چَکری', qes: 'چطوری', jas: 'چطوری', lan: 'چَکری', bas: 'چطوری', kha: 'چطوری', rud: 'چَگُری', sir: 'چطوری' },
  ipa: { ban: 'æbiː tʃeʃ', min: 'tʃækriː' },
  examples: { ban: 'ابی چش داداش؟', min: 'چَکری رفیق؟' },
  region_usage: 'همه مناطق', etymology: 'فارسی', cultural_note: 'پرسش روزمره', confidence_score: 95
});

addVerified({
  word_standard: 'خداحافظ', part_of_speech: 'interjection', category: 'greeting', subcategory: 'farewell',
  definition: 'خداحافظی کردن',
  dialects: { ban: 'خدا نگهدار', min: 'خدا نگهدار', qes: 'خدا نگهدار', jas: 'خدا نگهدار', lan: 'خدا نگهدار', bas: 'خدا نگهدار', kha: 'خدا نگهدار', rud: 'خدا نِگَهدار', sir: 'خدا نگهدار' },
  ipa: { ban: 'xodɒː negæhdɒːr', min: 'xodɒː negæhdɒːr' },
  examples: { ban: 'خدا نگهدار بازم سر بزن', min: 'خدا نگهدار' },
  region_usage: 'همه مناطق', etymology: 'فارسی', cultural_note: 'خداحافظی محترمانه', confidence_score: 90
});

addVerified({
  word_standard: 'برادر', part_of_speech: 'noun', category: 'family', subcategory: 'siblings',
  definition: 'برادر، برادر بزرگتر',
  dialects: { ban: 'برار', min: 'برار', qes: 'برار', jas: 'برار', lan: 'برار', bas: 'برار', kha: 'برار', rud: 'بَرار', sir: 'برار' },
  ipa: { ban: 'bærɒːr', min: 'bærɒːr' },
  examples: { ban: 'برارم از سفر اومده', min: 'برارم اومده' },
  region_usage: 'همه مناطق', etymology: 'فارسی', cultural_note: 'خطاب محبت‌آمیز', confidence_score: 95
});

addVerified({
  word_standard: 'خواهر', part_of_speech: 'noun', category: 'family', subcategory: 'siblings',
  definition: 'خواهر',
  dialects: { ban: 'خاهر', min: 'خاهر', qes: 'خواهر', jas: 'خواهر', lan: 'خواهر', bas: 'خواهر', kha: 'خواهر', rud: 'خواهر', sir: 'خواهر' },
  ipa: { ban: 'xɒːher', min: 'xɒːher' },
  examples: { ban: 'خاهرم کوچه ست', min: 'خواهرم کوچه‌ست' },
  region_usage: 'بندرعباس', etymology: 'فارسی', cultural_note: 'واژه قدیمی‌تر', confidence_score: 85
});

addVerified({
  word_standard: 'مادر', part_of_speech: 'noun', category: 'family', subcategory: 'parents',
  definition: 'مادر',
  dialects: { ban: 'مُم', min: 'مادر', qes: 'مادر', jas: 'مادر', lan: 'مادر', bas: 'مادر', kha: 'مادر', rud: 'مار', sir: 'مادر' },
  ipa: { ban: 'mæm', min: 'mɒːdær' },
  examples: { ban: 'مم رفته بازار', min: 'مار رفته بازار' },
  region_usage: 'بندرعباس/رودان', etymology: 'فارسی', cultural_note: 'لفظ محبت‌آمیز', confidence_score: 85
});

addVerified({
  word_standard: 'آب', part_of_speech: 'noun', category: 'nature', subcategory: 'water',
  definition: 'آب آشامیدنی، آب دریا',
  dialects: { ban: 'هو', min: 'او', qes: 'او', jas: 'او', lan: 'او', bas: 'او', kha: 'او', rud: 'آو', sir: 'او' },
  ipa: { ban: 'huː', min: 'uː' },
  examples: { ban: 'هو بیار تشنمه', min: 'او بیار' },
  region_usage: 'همه مناطق', etymology: 'فارسی باستان', cultural_note: 'واکه شاخص بندری', confidence_score: 95
});

addVerified({
  word_standard: 'دریا', part_of_speech: 'noun', category: 'nature', subcategory: 'sea',
  definition: 'دریا و آب‌های آزاد',
  dialects: { ban: 'جویی', min: 'دریا', qes: 'دریا', jas: 'دریا', lan: 'دریا', bas: 'دریا', kha: 'دریا', rud: 'دریا', sir: 'دریا' },
  ipa: { ban: 'dʒuːjiː', min: 'dæriːjɒː' },
  examples: { ban: 'بریم جویی', min: 'بریم دریا' },
  region_usage: 'بندرعباس', etymology: 'فارسی', cultural_note: 'اصطلاح دریایی', confidence_score: 90
});

addVerified({
  word_standard: 'نخل خرما', part_of_speech: 'noun', category: 'nature', subcategory: 'tree',
  definition: 'نخل خرما، درخت خرما',
  dialects: { ban: 'نغال', min: 'نخل', qes: 'نخل', jas: 'نخل', lan: 'نخل', bas: 'نخل', kha: 'نخل', rud: 'نَخل', sir: 'نخل' },
  ipa: { ban: 'næɣɒːl', min: 'næxl' },
  examples: { ban: 'نغال خرما داره', min: 'نخل خرما داره' },
  region_usage: 'همه مناطق', etymology: 'فارسی', cultural_note: 'کشاورزی اصلی هرمزگان', confidence_score: 90
});

addVerified({
  word_standard: 'قلیه ماهی', part_of_speech: 'noun', category: 'food', subcategory: 'dish',
  definition: 'خورشت ماهی محلی با تمبر هندی',
  dialects: { ban: 'قلیه ماهی', min: 'قلیه ماهی', qes: 'قلیه ماهی', jas: 'قلیه ماهی', lan: 'قلیه ماهی', bas: 'قلیه ماهی', kha: 'قلیه ماهی', rud: 'قلیه ماهی', sir: 'قلیه ماهی' },
  ipa: { ban: 'ɣæliːje mɒːhiː', min: 'ɣæliːje mɒːhiː' },
  examples: { ban: 'قلیه ماهی درست کن', min: 'قلیه ماهی درست کن' },
  region_usage: 'بندرعباس', etymology: 'فارسی', cultural_note: 'غذای اصیل جنوب', confidence_score: 95
});

addVerified({
  word_standard: 'خرما', part_of_speech: 'noun', category: 'food', subcategory: 'fruit',
  definition: 'میوه نخل خرما',
  dialects: { ban: 'حرما', min: 'خرما', qes: 'خرما', jas: 'خرما', lan: 'خرما', bas: 'خرما', kha: 'خرما', rud: 'خُرما', sir: 'خرما' },
  ipa: { ban: 'hærmɒː', min: 'xormɒː' },
  examples: { ban: 'حرما شیرینه', min: 'خرما شیرینه' },
  region_usage: 'همه مناطق', etymology: 'عربی', cultural_note: 'محصول اصلی', confidence_score: 90
});

addVerified({
  word_standard: 'ترافیک سنگین', part_of_speech: 'noun', category: 'driving', subcategory: 'traffic',
  definition: 'ترافیک سنگین، راه بندان',
  dialects: { ban: 'خون جاده', min: 'ترافیک', qes: 'ترافیک', jas: 'ترافیک', lan: 'ترافیک', bas: 'ترافیک', kha: 'ترافیک', rud: 'جاده خون', sir: 'ترافیک' },
  ipa: { ban: 'xuːn dʒɒːde', min: 'dʒɒːde xuːn' },
  examples: { ban: 'خون جاده افتادیم', min: 'جاده خون شده' },
  region_usage: 'همه مناطق', etymology: 'فارسی', cultural_note: 'اصطلاح رانندگان', confidence_score: 90
});

addVerified({
  word_standard: 'کامیون', part_of_speech: 'noun', category: 'driving', subcategory: 'vehicle',
  definition: 'کامیون باربری بزرگ',
  dialects: { ban: 'لنج خشکی', min: 'کامیون', qes: 'لنج', jas: 'کامیون', lan: 'کامیون', bas: 'کامیون', kha: 'کامیون', rud: 'کامیون', sir: 'کامیون' },
  ipa: { ban: 'lændʒ xoʃkiː', min: 'kɒːmjuːn' },
  examples: { ban: 'با لنج خشکی میریم', min: 'کامیون میاد' },
  region_usage: 'همه مناطق', etymology: 'انگلیسی', cultural_note: 'واژه محلی', confidence_score: 85
});

addVerified({
  word_standard: 'جاده بسته', part_of_speech: 'noun', category: 'driving', subcategory: 'road',
  definition: 'جاده بسته و مسدود',
  dialects: { ban: 'جاده بند', min: 'جاده بسته', qes: 'جاده بسته', jas: 'جاده بسته', lan: 'جاده بسته', bas: 'جاده بسته', kha: 'جاده بسته', rud: 'راه بند', sir: 'جاده بسته' },
  ipa: { ban: 'dʒɒːde bænd', min: 'dʒɒːde bæste' },
  examples: { ban: 'جاده بنده برنگردیم', min: 'جاده بسته' },
  region_usage: 'همه مناطق', etymology: 'فارسی', cultural_note: 'هشدار جاده‌ای', confidence_score: 90
});

fs.writeFileSync(
  path.join(__dirname, '_verified_count.json'),
  JSON.stringify({ count: entries.length }),
  'utf8'
);

module.exports = entries;
