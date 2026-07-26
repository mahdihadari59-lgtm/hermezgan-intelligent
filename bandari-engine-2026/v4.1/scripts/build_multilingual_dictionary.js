// این اسکریپت dictionary/multilingual_words.json را از داده‌های واقعی که کاربر
// فرستاده (نه حدس زبان‌شناختی من) تولید می‌کند. دو منبع:
//  - doc4: ۱۴ مدخل با ترجمه کامل به هر ۹ گویش + IPA + مثال (معتبرترین داده)
//  - doc7: ۳۳ اصطلاح رانندگی غلیظ بندری (فقط گویش بندری، از رانندگان واقعی)
const fs = require('fs');
const path = require('path');

// ۹ گویش پشتیبانی‌شده، طبق سند ۴
const DIALECTS = ['bandari','minabi','qeshm','jaski','langari','bastaki','khamiri','rudani','siriki'];
const DIALECT_META = {
  bandari:  { code: 'ban', label: 'بندری',   region: 'بندرعباس', population: 680000 },
  minabi:   { code: 'min', label: 'مینابی',   region: 'میناب',     population: 80000 },
  qeshm:    { code: 'qes', label: 'قشمی',     region: 'جزیره قشم', population: 150000 },
  jaski:    { code: 'jas', label: 'جاسکی',    region: 'جاسک',      population: 60000 },
  langari:  { code: 'lan', label: 'لنگه‌ای',  region: 'بندر لنگه', population: 50000 },
  bastaki:  { code: 'bas', label: 'بستکی',    region: 'بستک',      population: 40000 },
  khamiri:  { code: 'kha', label: 'خمیری',    region: 'خمیر',      population: 35000 },
  rudani:   { code: 'rud', label: 'رودانی',   region: 'رودان',     population: 80000 },
  siriki:   { code: 'sir', label: 'سیریکی',   region: 'سیریک',     population: 30000 }
};

// --- منبع ۱: سند ۴ (۱۴ مدخل چندگویشی کامل) ---
const multiDialectEntries = [
  { word_standard: 'سلام', category: 'greeting', subcategory: 'greeting',
    dialects: { bandari: 'سَلام براری', minabi: 'سَلام چَکری؟', qeshm: 'سَلام قِشمی', jaski: 'سَلام', langari: 'سَلام چَکری؟', bastaki: 'سَلام', khamiri: 'سَلام', rudani: 'سَلام چَگُری؟', siriki: 'سَلام' },
    ipa: { bandari: 'sælɒːm bærɒːriː', minabi: 'sælɒːm tʃækriː' },
    examples: { bandari: 'سَلام براری چطوری؟', minabi: 'سَلام چَکری؟' },
    region_usage: 'همه مناطق', etymology: 'عربی', cultural_note: 'رایج‌ترین احوالپرسی', confidence_score: 90 },
  { word_standard: 'چطوری', category: 'greeting', subcategory: 'question',
    dialects: { bandari: 'ابی چش', minabi: 'چَکری', qeshm: 'چطوری', jaski: 'چطوری', langari: 'چَکری', bastaki: 'چطوری', khamiri: 'چطوری', rudani: 'چَگُری', siriki: 'چطوری' },
    ipa: { bandari: 'æbiː tʃeʃ', minabi: 'tʃækriː' },
    examples: { bandari: 'ابی چش داداش؟', minabi: 'چَکری رفیق؟' },
    region_usage: 'همه مناطق', etymology: 'فارسی', cultural_note: 'پرسش روزمره', confidence_score: 95 },
  { word_standard: 'خداحافظ', category: 'greeting', subcategory: 'farewell',
    dialects: { bandari: 'خدا نگهدار', minabi: 'خدا نگهدار', qeshm: 'خدا نگهدار', jaski: 'خدا نگهدار', langari: 'خدا نگهدار', bastaki: 'خدا نگهدار', khamiri: 'خدا نگهدار', rudani: 'خدا نِگَهدار', siriki: 'خدا نگهدار' },
    ipa: { bandari: 'xodɒː negæhdɒːr', minabi: 'xodɒː negæhdɒːr' },
    examples: { bandari: 'خدا نگهدار بازم سر بزن', minabi: 'خدا نگهدار' },
    region_usage: 'همه مناطق', etymology: 'فارسی', cultural_note: 'خداحافظی محترمانه', confidence_score: 90 },
  { word_standard: 'برادر', category: 'family', subcategory: 'siblings',
    dialects: { bandari: 'برار', minabi: 'برار', qeshm: 'برار', jaski: 'برار', langari: 'برار', bastaki: 'برار', khamiri: 'برار', rudani: 'بَرار', siriki: 'برار' },
    ipa: { bandari: 'bærɒːr', minabi: 'bærɒːr' },
    examples: { bandari: 'برارم از سفر اومده', minabi: 'برارم اومده' },
    region_usage: 'همه مناطق', etymology: 'فارسی', cultural_note: 'خطاب محبت‌آمیز', confidence_score: 95 },
  { word_standard: 'خواهر', category: 'family', subcategory: 'siblings',
    dialects: { bandari: 'خاهر', minabi: 'خاهر', qeshm: 'خواهر', jaski: 'خواهر', langari: 'خواهر', bastaki: 'خواهر', khamiri: 'خواهر', rudani: 'خواهر', siriki: 'خواهر' },
    ipa: { bandari: 'xɒːher', minabi: 'xɒːher' },
    examples: { bandari: 'خاهرم کوچه ست', minabi: 'خواهرم کوچه‌ست' },
    region_usage: 'بندرعباس', etymology: 'فارسی', cultural_note: 'واژه قدیمی‌تر', confidence_score: 85 },
  { word_standard: 'مادر', category: 'family', subcategory: 'parents',
    dialects: { bandari: 'مُم', minabi: 'مادر', qeshm: 'مادر', jaski: 'مادر', langari: 'مادر', bastaki: 'مادر', khamiri: 'مادر', rudani: 'مار', siriki: 'مادر' },
    ipa: { bandari: 'mæm', minabi: 'mɒːdær' },
    examples: { bandari: 'مم رفته بازار', minabi: 'مار رفته بازار' },
    region_usage: 'بندرعباس/رودان', etymology: 'فارسی', cultural_note: 'لفظ محبت‌آمیز', confidence_score: 85 },
  { word_standard: 'آب', category: 'nature', subcategory: 'water',
    dialects: { bandari: 'هو', minabi: 'او', qeshm: 'او', jaski: 'او', langari: 'او', bastaki: 'او', khamiri: 'او', rudani: 'آو', siriki: 'او' },
    ipa: { bandari: 'huː', minabi: 'uː' },
    examples: { bandari: 'هو بیار تشنمه', minabi: 'او بیار' },
    region_usage: 'همه مناطق', etymology: 'فارسی باستان', cultural_note: 'واکه شاخص بندری', confidence_score: 95 },
  { word_standard: 'دریا', category: 'nature', subcategory: 'sea',
    dialects: { bandari: 'جویی', minabi: 'دریا', qeshm: 'دریا', jaski: 'دریا', langari: 'دریا', bastaki: 'دریا', khamiri: 'دریا', rudani: 'دریا', siriki: 'دریا' },
    ipa: { bandari: 'dʒuːjiː', minabi: 'dæriːjɒː' },
    examples: { bandari: 'بریم جویی', minabi: 'بریم دریا' },
    region_usage: 'بندرعباس', etymology: 'فارسی', cultural_note: 'اصطلاح دریایی', confidence_score: 90 },
  { word_standard: 'نخل خرما', category: 'nature', subcategory: 'tree',
    dialects: { bandari: 'نغال', minabi: 'نخل', qeshm: 'نخل', jaski: 'نخل', langari: 'نخل', bastaki: 'نخل', khamiri: 'نخل', rudani: 'نَخل', siriki: 'نخل' },
    ipa: { bandari: 'næɣɒːl', minabi: 'næxl' },
    examples: { bandari: 'نغال خرما داره', minabi: 'نخل خرما داره' },
    region_usage: 'همه مناطق', etymology: 'فارسی', cultural_note: 'کشاورزی اصلی هرمزگان', confidence_score: 90 },
  { word_standard: 'قلیه ماهی', category: 'food', subcategory: 'dish',
    dialects: { bandari: 'قلیه ماهی', minabi: 'قلیه ماهی', qeshm: 'قلیه ماهی', jaski: 'قلیه ماهی', langari: 'قلیه ماهی', bastaki: 'قلیه ماهی', khamiri: 'قلیه ماهی', rudani: 'قلیه ماهی', siriki: 'قلیه ماهی' },
    ipa: { bandari: 'ɣæliːje mɒːhiː', minabi: 'ɣæliːje mɒːhiː' },
    examples: { bandari: 'قلیه ماهی درست کن', minabi: 'قلیه ماهی درست کن' },
    region_usage: 'بندرعباس', etymology: 'فارسی', cultural_note: 'غذای اصیل جنوب', confidence_score: 95 },
  { word_standard: 'خرما', category: 'food', subcategory: 'fruit',
    dialects: { bandari: 'حرما', minabi: 'خرما', qeshm: 'خرما', jaski: 'خرما', langari: 'خرما', bastaki: 'خرما', khamiri: 'خرما', rudani: 'خُرما', siriki: 'خرما' },
    ipa: { bandari: 'hærmɒː', minabi: 'xormɒː' },
    examples: { bandari: 'حرما شیرینه', minabi: 'خرما شیرینه' },
    region_usage: 'همه مناطق', etymology: 'عربی', cultural_note: 'محصول اصلی', confidence_score: 90 },
  { word_standard: 'ترافیک سنگین', category: 'driving', subcategory: 'traffic',
    dialects: { bandari: 'خون جاده', minabi: 'ترافیک', qeshm: 'ترافیک', jaski: 'ترافیک', langari: 'ترافیک', bastaki: 'ترافیک', khamiri: 'ترافیک', rudani: 'جاده خون', siriki: 'ترافیک' },
    ipa: { bandari: 'xuːn dʒɒːde', minabi: 'dʒɒːde xuːn' },
    examples: { bandari: 'خون جاده افتادیم', minabi: 'جاده خون شده' },
    region_usage: 'همه مناطق', etymology: 'فارسی', cultural_note: 'اصطلاح رانندگان', confidence_score: 90 },
  { word_standard: 'کامیون', category: 'driving', subcategory: 'vehicle',
    dialects: { bandari: 'لنج خشکی', minabi: 'کامیون', qeshm: 'لنج', jaski: 'کامیون', langari: 'کامیون', bastaki: 'کامیون', khamiri: 'کامیون', rudani: 'کامیون', siriki: 'کامیون' },
    ipa: { bandari: 'lændʒ xoʃkiː', minabi: 'kɒːmjuːn' },
    examples: { bandari: 'با لنج خشکی میریم', minabi: 'کامیون میاد' },
    region_usage: 'همه مناطق', etymology: 'انگلیسی', cultural_note: 'واژه محلی', confidence_score: 85 },
  { word_standard: 'جاده بسته', category: 'driving', subcategory: 'road',
    dialects: { bandari: 'جاده بند', minabi: 'جاده بسته', qeshm: 'جاده بسته', jaski: 'جاده بسته', langari: 'جاده بسته', bastaki: 'جاده بسته', khamiri: 'جاده بسته', rudani: 'راه بند', siriki: 'جاده بسته' },
    ipa: { bandari: 'dʒɒːde bænd', minabi: 'dʒɒːde bæste' },
    examples: { bandari: 'جاده بنده برنگردیم', minabi: 'جاده بسته' },
    region_usage: 'همه مناطق', etymology: 'فارسی', cultural_note: 'هشدار جاده‌ای', confidence_score: 90 }
];

// --- منبع ۲: سند ۷ (۳۳ اصطلاح غلیظ رانندگی، فقط گویش بندری، از رانندگان واقعی) ---
// ساختار خام: [واژه/عبارت بندری, معنی فارسی, زیردسته, مثال]
const drivingSlangRaw = [
  ['خون جاده', 'ترافیک بسیار سنگین، راه بندان شدید', 'traffic_heavy', 'از صبح افتادیم تو خون جاده، هنوز نرسیدیم'],
  ['پوست گاوی', 'ترافیک بسیار بد و کلافه‌کننده', 'traffic_heavy', 'چهارراه غزی پوست گاوی شده'],
  ['راه وا شد', 'ترافیک باز شد، راه خلوت شد', 'traffic_light', 'خداروشکر راه وا شد، بریم'],
  ['بستن به تنگ', 'راه بسته شدن کامل، گیر کردن', 'traffic_jam', 'کمربندی بست به تنگ، از راه دیگه برو'],
  ['لنج خشکی', 'کامیون بزرگ و قدیمی', 'truck', 'با اون لنج خشکی نمی‌رسی به وقت'],
  ['خاور بدو', 'کامیون‌های تندرو و مسابقه‌ای در جاده', 'truck', 'خاور بدوها دارن جاده رو قاپ میزنن'],
  ['بار داغ', 'باری که زمان تحویل آن کم است', 'cargo_urgent', 'بار داغه، نیم ساعت وخت باید برسونم'],
  ['چفت کردن بار', 'محکم بستن بار روی کامیون', 'cargo_secure', 'بارو خوب چفت کن، جاده لرزه'],
  ['بار دوز', 'باری که حجم زیادی دارد', 'cargo_type', 'بار دوزه، دوتا خاور میخواد'],
  ['ته بار', 'آخرین بار سفارش داده‌شده', 'cargo_order', 'ته بار رو بردم بندرعباس'],
  ['دوربین شکارچی', 'دوربین مخفی کنترل سرعت', 'radar', 'مواظب باش دوربین شکارچیه اینجا'],
  ['گوشی دستت', 'دست گرفتن موبایل حین رانندگی', 'violation', 'اونی که گوشی دستش بود عکس انداخت'],
  ['کمربند نزدی', 'نبستن کمربند ایمنی', 'violation', 'کمربند نزدی رد شد دوربین ازت عکس گرفت'],
  ['سبقت ممنوع', 'خطای سبقت غیرمجاز', 'violation', 'تو پیچ سبقت ممنوع عکس انداخت'],
  ['جریمه سیار', 'دوربین سیار پلیس', 'radar', 'جریمه سیار گذاشتن این هفته'],
  ['بزن تو دهنه', 'وارد مسیر اصلی یا خیابان اصلی شو', 'direction', 'برو بزن تو دهنه بلوار'],
  ['برو تندرو', 'از خط تندرو (سمت چپ) حرکت کن', 'direction', 'تندرو برو زودتر میرسی'],
  ['بکش کنار', 'خودرو را به کنار جاده ببر', 'direction', 'بکش کنار بذار رد بشم'],
  ['بزن بیرون', 'از جاده خارج شو یا بپیچ', 'direction', 'اینجا بزن بیرون میرسی میدان'],
  ['بیا تودست', 'وارد کوچه یا فرعی شو', 'direction', 'بیا تودست زودتر میرسی'],
  ['گربه خواب', 'سرعت‌گیر دست‌ساز یا غیراستاندارد', 'warning', 'مواظب باش گربه خواس جلوتره'],
  ['چاله چوله', 'جاده ناهموار و پر از دست‌انداز', 'warning', 'این جاده پر از چاله چوله، آهسته برو'],
  ['روزنه', 'فضای خالی بین دو خودرو', 'warning', 'روزنه بذار رد بشم'],
  ['لعنت به این جاده', 'ابراز ناراحتی از جاده بد', 'complaint', 'لعنت به این جاده آدم رو میندازه'],
  ['نیم ساعت وخت', 'حدود نیم ساعت دیگر', 'time_estimate', 'نیم ساعت وخت میرسم ببینمت'],
  ['یک پُشت', 'یک مسیر رفت و برگشت', 'distance', 'یک پُشت رفتم بندرعباس برگشتم'],
  ['سره', 'مقصد یا انتهای مسیر', 'destination', 'سره راه کو؟'],
  ['پا پیچ', 'مسیر پیاده یا نزدیک', 'distance', 'از اینجا پا پیچه میرسم'],
  ['تفنگ', 'دستگاه دیاگ خودرو', 'repair', 'ببر ماشینو بزن به تفنگ ببین چی شده'],
  ['دور انداختن', 'حداکثر دور موتور گرفتن', 'engine', 'دور انداختم برسم به موقع'],
  ['روغن نریختن', 'عدم تعویض روغن به موقع', 'maintenance', 'روغن نریختی، موتور صدا میده'],
  ['لنت کشیدن', 'فرسوده شدن لنت ترمز', 'brake', 'لنت کشیده، ببر تعویض کن'],
  ['لامپ سوز', 'چراغ سوخته خودرو', 'light', 'چراغات لامپ سوزه، جریمه میشی']
];

// [هشدار همپوشانی] 'خون جاده' و 'لنج خشکی' هم در doc4 (چندگویشی) و هم اینجا آمده‌اند.
// چون doc4 چندگویشیه و اینجا فقط بندریه با جزئیات بیشتر (مثال/زیردسته)، این دو را
// این‌جا SKIP می‌کنیم تا تکراری در دیکشنری نداشته باشیم (already covered above).
const skipDuplicates = new Set(['خون جاده', 'لنج خشکی']);

const drivingEntries = drivingSlangRaw
  .filter(([word]) => !skipDuplicates.has(word))
  .map(([bandariWord, meaning, subcategory, example]) => ({
    word_standard: meaning,           // چون این‌ها اصطلاحن، «واژه استاندارد» همون توضیح فارسیه
    category: 'driving',
    subcategory,
    dialects: { bandari: bandariWord },  // فقط بندری موجوده (منبع فقط بندری داشت)
    examples: { bandari: example },
    region_usage: 'بندرعباس (رانندگان محلی)',
    etymology: null,
    cultural_note: 'اصطلاح واقعی رانندگان لنج‌خشکی/کامیون‌داران، نه ترجمه تحت‌اللفظی',
    confidence_score: 85
  }));

const allEntries = [...multiDialectEntries, ...drivingEntries].map((e, i) => ({ id: i + 1, ...e }));

fs.writeFileSync(
  path.join(__dirname, '..', 'dictionary', 'multilingual_words.json'),
  JSON.stringify({ dialects: DIALECTS, dialect_meta: DIALECT_META, entries: allEntries }, null, 2),
  'utf8'
);

console.log(`✅ ${allEntries.length} مدخل چندگویشی نوشته شد (${multiDialectEntries.length} کامل ۹گویشی از doc4 + ${drivingEntries.length} اصطلاح رانندگی بندری از doc7، ۲ مورد تکراری skip شد)`);
