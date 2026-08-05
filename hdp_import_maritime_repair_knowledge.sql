-- HDP import script for maritime schedules and auto repair data
PRAGMA foreign_keys = OFF;
BEGIN TRANSACTION;

-- ساعت حرکت شناورهای قشم
INSERT INTO knowledge (title, category, content, created_at, keywords, source, priority, subcategory, city, tags, topic, intent, status, verified, confidence, category_fa, subtopic, quality, is_deleted, graph_depth, graph_root, entity_type, last_verified, updated_at)
SELECT 'ساعت حرکت شناورهای قشم', 'maritime_transport', '🚢 **جدول حرکت شناورهای مسافری بندرعباس (اسکله حقانی) به جزیره قشم (اسکله ذاکری)**

📞 **اطلاعات تماس ضروری**:
• اسکله شهید حقانی (بندرعباس): ۰۷۶۳۲۲۳۷۷۸۱
• اسکله شهید ذاکری (قشم): ۰۷۶۳۵۲۲۵۵۳۶

💰 **هزینه بلیط**: ۱۰۵,۰۰۰ تومان (یک طرفه)

🕐 **ساعات حرکت از بندرعباس به قشم**:
| ساعت | توضیحات |
|------|----------|
| ۰۷:۰۰ | سرویس صبحگاهی |
| ۱۰:۰۰ | *فقط در ایام شلوغی* |
| ۱۲:۰۰ | سرویس ظهر |
| ۱۵:۰۰ | سرویس عصر |

🕐 **ساعات برگشت (قشم به بندرعباس)**:
| ساعت | توضیحات |
|------|----------|
| ۰۷:۰۰ | سرویس صبحگاهی |
| ۱۰:۰۰ | *فقط در ایام شلوغی* |
| ۱۲:۰۰ | سرویس ظهر |
| ۱۵:۰۰ | سرویس عصر |

⏱️ **مدت زمان سفر**: ۴۵-۶۰ دقیقه

⚠️ **نکات مهم**:
• در ایام تعطیلات نوروز و تابستان، سرویس‌ها افزایش می‌یابد
• در صورت طوفانی بودن دریا، تمام مسیرها لغو می‌شوند
• برای پایش آنلاین: سامانه zakeri2/monitoring', '2026-07-25', 'قشم, شناور, بندرعباس, قشم-بندرعباس, قشم ذاکری', 'maritime_schedule.json', '10', 'maritime_schedule', 'بندرعباس', 'maritime, ferry, qeshm', 'transport', 'maritime.schedule', 'active', '1', '0.95', 'حمل و نقل دریایی', 'qeshm', 'high', '0', '0', 'maritime_transport', 'knowledge_article', '2026-07-25', '2026-07-25'
WHERE NOT EXISTS (
        SELECT 1 FROM knowledge
        WHERE title='ساعت حرکت شناورهای قشم'
          AND category='maritime_transport'
          AND subcategory='maritime_schedule'
    );
INSERT INTO knowledge_aliases (alias_title, knowledge_id)
SELECT 'شناورهای قشم', id
FROM knowledge
WHERE title='ساعت حرکت شناورهای قشم' AND category='maritime_transport' AND subcategory='maritime_schedule'
  AND NOT EXISTS (
      SELECT 1 FROM knowledge_aliases ka
      WHERE ka.alias_title='شناورهای قشم' AND ka.knowledge_id=knowledge.id
  );

-- ساعت حرکت لندینگ کرافت
INSERT INTO knowledge (title, category, content, created_at, keywords, source, priority, subcategory, city, tags, topic, intent, status, verified, confidence, category_fa, subtopic, quality, is_deleted, graph_depth, graph_root, entity_type, last_verified, updated_at)
SELECT 'ساعت حرکت لندینگ کرافت', 'maritime_transport', '🚛 **جدول حرکت لندینگ کرافت (حمل خودرو) - مسیر بندر پُل به بندر لافت**

📍 **نقطه حرکت**: بندر پُل (شهرستان خمیر، ۸۵ کیلومتری بندرعباس)
📍 **مقصد**: بندر لافت (جزیره قشم)

🕐 **ساعت کاری**: همه روزه از ۰۶:۰۰ صبح تا ۲۳:۰۰ شب

⏱️ **زمان حرکت**: هر ۲ ساعت یک بار

⏱️ **مدت زمان سفر**: ۲۰-۳۰ دقیقه

💰 **هزینه حمل خودرو (سال ۱۴۰۴)**:
| نوع خودرو | هزینه |
|-----------|-------|
| خودرو سواری | ۲۰۰,۰۰۰ تومان |
| وانت | ۱۷۰,۰۰۰ تومان |
| مینی بوس | ۳۰۰,۰۰۰ تومان |

📋 **مدارک لازم**:
• اصل کارت خودرو
• بیمه شخص ثالث معتبر
• گواهینامه و کارت شناسایی راننده

⚠️ **نکته**: جزیره هرمز محدودیت ورود خودروهای شخصی غیربومی دارد!', '2026-07-25', 'لندینگ کرافت, بندر پُل, بندر لافت, حمل خودرو', 'maritime_schedule.json', '9', 'maritime_schedule', 'بندرعباس', 'maritime, landing-craft, vehicle', 'transport', 'maritime.landing_craft', 'active', '1', '0.95', 'حمل و نقل دریایی', 'landing_craft', 'high', '0', '0', 'maritime_transport', 'knowledge_article', '2026-07-25', '2026-07-25'
WHERE NOT EXISTS (
        SELECT 1 FROM knowledge
        WHERE title='ساعت حرکت لندینگ کرافت'
          AND category='maritime_transport'
          AND subcategory='maritime_schedule'
    );
INSERT INTO knowledge_aliases (alias_title, knowledge_id)
SELECT 'لندینگ کرافت', id
FROM knowledge
WHERE title='ساعت حرکت لندینگ کرافت' AND category='maritime_transport' AND subcategory='maritime_schedule'
  AND NOT EXISTS (
      SELECT 1 FROM knowledge_aliases ka
      WHERE ka.alias_title='لندینگ کرافت' AND ka.knowledge_id=knowledge.id
  );

-- ساعت حرکت شناورهای هرمز
INSERT INTO knowledge (title, category, content, created_at, keywords, source, priority, subcategory, city, tags, topic, intent, status, verified, confidence, category_fa, subtopic, quality, is_deleted, graph_depth, graph_root, entity_type, last_verified, updated_at)
SELECT 'ساعت حرکت شناورهای هرمز', 'maritime_transport', '🏝️ **جدول حرکت شناورهای مسافری بندرعباس به جزیره هرمز**

💰 **هزینه بلیط**: ۱۰۵,۰۰۰ تومان

🕐 **ساعات حرکت از بندرعباس به هرمز**:
| ساعت | توضیحات |
|------|----------|
| ۰۶:۳۰ | اولین سرویس صبح |
| ۰۹:۰۰ | سرویس صبح |
| ۱۳:۰۰ | سرویس ظهر |
| ۱۷:۰۰ | سرویس عصر |
| ۲۱:۰۰ | سرویس شب |

🕐 **ساعات برگشت (هرمز به بندرعباس)**:
| ساعت | توضیحات |
|------|----------|
| ۰۷:۰۰ | اولین سرویس |
| ۰۹:۰۰ | سرویس صبح |
| ۱۱:۰۰ | سرویس قبل از ظهر |
| ۱۴:۳۰ | سرویس بعد از ظهر |
| ۱۹:۰۰ | آخرین سرویس |

⏱️ **مدت زمان سفر**: ۳۰-۶۰ دقیقه

⚠️ **نکات مهم**:
• در روزهای پنجشنبه و جمعه، شناورها هر نیم ساعت یکبار حرکت می‌کنند
• جزیره هرمز محدودیت ورود خودروهای شخصی دارد', '2026-07-25', 'هرمز, شناور, بندرعباس, هرمز بندرعباس', 'maritime_schedule.json', '9', 'maritime_schedule', 'بندرعباس', 'maritime, ferry, hormoz', 'transport', 'maritime.schedule', 'active', '1', '0.95', 'حمل و نقل دریایی', 'hormoz', 'high', '0', '0', 'maritime_transport', 'knowledge_article', '2026-07-25', '2026-07-25'
WHERE NOT EXISTS (
        SELECT 1 FROM knowledge
        WHERE title='ساعت حرکت شناورهای هرمز'
          AND category='maritime_transport'
          AND subcategory='maritime_schedule'
    );
INSERT INTO knowledge_aliases (alias_title, knowledge_id)
SELECT 'شناورهای هرمز', id
FROM knowledge
WHERE title='ساعت حرکت شناورهای هرمز' AND category='maritime_transport' AND subcategory='maritime_schedule'
  AND NOT EXISTS (
      SELECT 1 FROM knowledge_aliases ka
      WHERE ka.alias_title='شناورهای هرمز' AND ka.knowledge_id=knowledge.id
  );

-- ساعت حرکت قشم-هرمز
INSERT INTO knowledge (title, category, content, created_at, keywords, source, priority, subcategory, city, tags, topic, intent, status, verified, confidence, category_fa, subtopic, quality, is_deleted, graph_depth, graph_root, entity_type, last_verified, updated_at)
SELECT 'ساعت حرکت قشم-هرمز', 'maritime_transport', '🔄 **جدول حرکت شناورهای مسافری بین جزایر (قشم ↔ هرمز)**

⏱️ **مدت زمان سفر**: حدود ۳۰ دقیقه

🕐 **ساعات حرکت از قشم به هرمز**:
• ۰۷:۰۰ صبح
• ۱۴:۰۰ بعد از ظهر

🕐 **ساعات برگشت (هرمز به قشم)**:
• ۰۸:۰۰ صبح
• ۱۵:۰۰ بعد از ظهر

⚠️ **توجه**: در ایام تعطیلات، سرویس‌ها افزایش می‌یابد', '2026-07-25', 'قشم, هرمز, بین جزایر, شناور', 'maritime_schedule.json', '8', 'maritime_schedule', 'بندرعباس', 'maritime, ferry, inter-island', 'transport', 'maritime.schedule', 'active', '1', '0.95', 'حمل و نقل دریایی', 'qeshm_hormoz', 'high', '0', '0', 'maritime_transport', 'knowledge_article', '2026-07-25', '2026-07-25'
WHERE NOT EXISTS (
        SELECT 1 FROM knowledge
        WHERE title='ساعت حرکت قشم-هرمز'
          AND category='maritime_transport'
          AND subcategory='maritime_schedule'
    );
INSERT INTO knowledge_aliases (alias_title, knowledge_id)
SELECT 'شناور قشم-هرمز', id
FROM knowledge
WHERE title='ساعت حرکت قشم-هرمز' AND category='maritime_transport' AND subcategory='maritime_schedule'
  AND NOT EXISTS (
      SELECT 1 FROM knowledge_aliases ka
      WHERE ka.alias_title='شناور قشم-هرمز' AND ka.knowledge_id=knowledge.id
  );

-- ساعت حرکت کیش
INSERT INTO knowledge (title, category, content, created_at, keywords, source, priority, subcategory, city, tags, topic, intent, status, verified, confidence, category_fa, subtopic, quality, is_deleted, graph_depth, graph_root, entity_type, last_verified, updated_at)
SELECT 'ساعت حرکت کیش', 'maritime_transport', '🏖️ **جدول حرکت شناورهای مسافری کیش به بندر چارک**

💰 **خرید بلیط اینترنتی**: ticket.kishports.com

⏱️ **مدت زمان سفر**: ۴۵-۶۰ دقیقه

🕐 **ساعات حرکت از کیش به چارک**:
| ساعت | نوع شناور |
|------|-----------|
| ۰۷:۰۰ | قایق تندرو |
| ۰۹:۰۰ | قایق تندرو |
| ۰۹:۴۵ | قایق تندرو |
| ۱۰:۳۰ | قایق تندرو |
| ۱۱:۳۰ | قایق تندرو |
| ۱۲:۱۵ | قایق تندرو |
| ۱۳:۰۰ | قایق تندرو |

🕐 **ساعات حرکت از چارک به کیش**:
| ساعت | نوع شناور |
|------|-----------|
| ۰۷:۰۰ | قایق تندرو |
| ۰۷:۴۵ | قایق تندرو |
| ۰۸:۳۰ | قایق تندرو |
| ۰۹:۳۰ | قایق تندرو |
| ۱۰:۳۰ | قایق تندرو |
| ۱۱:۳۰ | قایق تندرو |
| ۱۳:۰۰ | قایق تندرو |

🚛 **حمل خودرو (لندینگ کرافت)**:
• ساعات حرکت: ۰۵:۳۰ تا ۱۳:۰۰
• فقط در ساعات ابتدایی روز انجام می‌شود', '2026-07-25', 'کیش, چارک, شناور, لندینگ کرافت, قایق تندرو', 'maritime_schedule.json', '9', 'maritime_schedule', 'بندرعباس', 'maritime, ferry, kish', 'transport', 'maritime.schedule', 'active', '1', '0.95', 'حمل و نقل دریایی', 'kish', 'high', '0', '0', 'maritime_transport', 'knowledge_article', '2026-07-25', '2026-07-25'
WHERE NOT EXISTS (
        SELECT 1 FROM knowledge
        WHERE title='ساعت حرکت کیش'
          AND category='maritime_transport'
          AND subcategory='maritime_schedule'
    );
INSERT INTO knowledge_aliases (alias_title, knowledge_id)
SELECT 'شناورهای کیش', id
FROM knowledge
WHERE title='ساعت حرکت کیش' AND category='maritime_transport' AND subcategory='maritime_schedule'
  AND NOT EXISTS (
      SELECT 1 FROM knowledge_aliases ka
      WHERE ka.alias_title='شناورهای کیش' AND ka.knowledge_id=knowledge.id
  );

-- جدول کلی حرکت شناورها
INSERT INTO knowledge (title, category, content, created_at, keywords, source, priority, subcategory, city, tags, topic, intent, status, verified, confidence, category_fa, subtopic, quality, is_deleted, graph_depth, graph_root, entity_type, last_verified, updated_at)
SELECT 'جدول کلی حرکت شناورها', 'maritime_transport', '📊 **خلاصه جدول حرکت شناورها در بنادر هرمزگان**

| مسیر | مبدأ | مقصد | ساعات حرکت | مدت | هزینه |
|------|------|------|-------------|------|-------|
| قشم | بندرعباس | قشم | ۰۷:۰۰، ۱۰:۰۰، ۱۲:۰۰، ۱۵:۰۰ | ۴۵-۶۰ دقیقه | ۱۰۵,۰۰۰ |
| قشم | قشم | بندرعباس | ۰۷:۰۰، ۱۰:۰۰، ۱۲:۰۰، ۱۵:۰۰ | ۴۵-۶۰ دقیقه | ۱۰۵,۰۰۰ |
| هرمز | بندرعباس | هرمز | ۰۶:۳۰، ۰۹:۰۰، ۱۳:۰۰، ۱۷:۰۰، ۲۱:۰۰ | ۳۰-۶۰ دقیقه | ۱۰۵,۰۰۰ |
| هرمز | هرمز | بندرعباس | ۰۷:۰۰، ۰۹:۰۰، ۱۱:۰۰، ۱۴:۳۰، ۱۹:۰۰ | ۳۰-۶۰ دقیقه | ۱۰۵,۰۰۰ |
| قشم-هرمز | قشم | هرمز | ۰۷:۰۰، ۱۴:۰۰ | ۳۰ دقیقه | - |
| قشم-هرمز | هرمز | قشم | ۰۸:۰۰، ۱۵:۰۰ | ۳۰ دقیقه | - |
| کیش | کیش | چارک | ۰۷:۰۰-۱۳:۰۰ (۷ سرویس) | ۴۵-۶۰ دقیقه | - |
| کیش | چارک | کیش | ۰۷:۰۰-۱۳:۰۰ (۷ سرویس) | ۴۵-۶۰ دقیقه | - |

🚛 **لندینگ کرافت (حمل خودرو)**:
| مسیر | مبدأ | مقصد | ساعت کاری | مدت | هزینه خودرو |
|------|------|------|-----------|------|--------------|
| قشم (خودرو) | بندر پُل | بندر لافت | ۰۶:۰۰-۲۳:۰۰ (هر ۲ ساعت) | ۲۰-۳۰ دقیقه | ۲۰۰,۰۰۰ |
| کیش (خودرو) | چارک | کیش | ۰۵:۳۰-۱۳:۰۰ | ۴۵-۶۰ دقیقه | - |

⚠️ **قوانین مهم**:
• در صورت طوفانی بودن دریا، تمام مسیرها لغو می‌شوند
• جزیره هرمز محدودیت ورود خودروهای شخصی دارد
• پنجشنبه و جمعه، سرویس‌ها افزایش می‌یابد
• برای اطلاع لحظه‌ای: سامانه zakeri2/monitoring', '2026-07-25', 'شناورها, قشم, هرمز, کیش, چارک, بندرعباس', 'maritime_schedule.json', '10', 'maritime_schedule', 'هرمزگان', 'maritime, summary, schedules', 'transport', 'maritime.summary', 'active', '1', '0.95', 'حمل و نقل دریایی', 'summary', 'high', '0', '0', 'maritime_transport', 'knowledge_article', '2026-07-25', '2026-07-25'
WHERE NOT EXISTS (
        SELECT 1 FROM knowledge
        WHERE title='جدول کلی حرکت شناورها'
          AND category='maritime_transport'
          AND subcategory='maritime_schedule'
    );
INSERT INTO knowledge_aliases (alias_title, knowledge_id)
SELECT 'خلاصه حرکت شناورها', id
FROM knowledge
WHERE title='جدول کلی حرکت شناورها' AND category='maritime_transport' AND subcategory='maritime_schedule'
  AND NOT EXISTS (
      SELECT 1 FROM knowledge_aliases ka
      WHERE ka.alias_title='خلاصه حرکت شناورها' AND ka.knowledge_id=knowledge.id
  );

-- تعمیرگاه‌های مکانیک بندرعباس
INSERT INTO knowledge (title, category, content, created_at, keywords, source, priority, subcategory, city, tags, topic, intent, status, verified, confidence, category_fa, subtopic, quality, is_deleted, graph_depth, graph_root, entity_type, last_verified, updated_at)
SELECT 'تعمیرگاه‌های مکانیک بندرعباس', 'automotive_services', '🔧 **لیست تعمیرگاه‌های مکانیک خودرو در بندرعباس**

📍 **تعمیرگاه‌های تخصصی و عمومی**:

1. **خدمات فنی رنو** (نمایندگی مجاز)
   • تخصص: رنو
   • آدرس: بلوار جمهوری اسلامی، بلوار امام حسین، جنب باشگاه ابومسلم
   • ساعت کاری: ۲۴ ساعته

2. **تعمیرگاه بندر توربو**
   • تخصص: توربوشارژ، موتورهای قوی
   • آدرس: بلوار خلیج فارس، سنگ کن شرقی
   • ساعت کاری: ۰۸:۰۰ تا ۲۰:۰۰

3. **مرکز خدمات فنی تخصصی خودروی نعمت**
   • تخصص: مکانیک تخصصی (موتور و گیربکس)
   • آدرس: شهید حقانی، بلوار شهدا
   • ساعت کاری: ۲۴ ساعته

4. **تعمیرگاه هما خودرو**
   • تخصص: عمومی (مکانیک و برق)
   • آدرس: بلوار پاسداران، اسلام آباد
   • ساعت کاری: ۰۸:۰۰ تا ۱۸:۰۰

5. **تعمیرگاه تخصصی زانتیا**
   • تخصص: خودروهای چینی، زانتیا
   • آدرس: ۱۲ فروردین شرقی، امامت، امامت ۹
   • ساعت کاری: ۰۸:۰۰ تا ۲۱:۰۰

6. **تعمیرگاه بیژن**
   • تخصص: عمومی
   • آدرس: ۱۲ فروردین شرقی، امامت
   • ساعت کاری: ۲۴ ساعته

7. **تعمیرگاه کلکودی**
   • تخصص: عمومی
   • آدرس: آزادگان، شهید مسافری، فرزاد ۲۱
   • ساعت کاری: ۰۹:۰۰ تا ۱۷:۰۰

8. **تعمیرگاه رنو پوران**
   • تخصص: رنو تخصصی
   • آدرس: بلوار امام حسین، شهید باکری، باکری ۱۸', '2026-07-25', 'مکانیک, رنو, بندرعباس, تعمیرگاه', 'auto_repair_shops.json', '9', 'repair_shops', 'بندرعباس', 'automotive, mechanic, repair', 'automotive', 'repair.mechanic', 'active', '1', '0.95', 'خدمات خودرو', 'mechanic', 'high', '0', '0', 'automotive_services', 'knowledge_article', '2026-07-25', '2026-07-25'
WHERE NOT EXISTS (
        SELECT 1 FROM knowledge
        WHERE title='تعمیرگاه‌های مکانیک بندرعباس'
          AND category='automotive_services'
          AND subcategory='repair_shops'
    );
INSERT INTO knowledge_aliases (alias_title, knowledge_id)
SELECT 'مکانیکی بندرعباس', id
FROM knowledge
WHERE title='تعمیرگاه‌های مکانیک بندرعباس' AND category='automotive_services' AND subcategory='repair_shops'
  AND NOT EXISTS (
      SELECT 1 FROM knowledge_aliases ka
      WHERE ka.alias_title='مکانیکی بندرعباس' AND ka.knowledge_id=knowledge.id
  );

-- تنظیم موتور و دیاگ بندرعباس
INSERT INTO knowledge (title, category, content, created_at, keywords, source, priority, subcategory, city, tags, topic, intent, status, verified, confidence, category_fa, subtopic, quality, is_deleted, graph_depth, graph_root, entity_type, last_verified, updated_at)
SELECT 'تنظیم موتور و دیاگ بندرعباس', 'automotive_services', '⚙️ **مراکز تخصصی تنظیم موتور و دیاگ در بندرعباس**

1. **کهتک تکنیک**
   • تخصص: دیاگ، تنظیم موتور، گیربکس
   • آدرس: شهید تابدار، اخلاص ۱۴
   • ساعت کاری: ۰۸:۰۰ تا ۲۲:۰۰

2. **کیلومترسازی مهدی**
   • تخصص: کیلومترسازی، تنظیم موتور
   • آدرس: بلوار جمهوری اسلامی، بسیج ۱۸

3. **تعمیرگاه مدرن بندر**
   • تخصص: مکانیک مدرن، عیب‌یابی
   • آدرس: نبوت، نبوت ۱۱

4. **سی‌ان‌جی (CNG) تدبیر**
   • تخصص: سیستم سوخت CNG (تخصصی)
   • آدرس: خیابان شفا، بنفشه
   • ساعت کاری: ۰۸:۰۰ تا ۱۹:۰۰

5. **تنظیم موتوری و لوازم یدکی CNG**
   • تخصص: CNG، انژکتور، کاربراتور
   • آدرس: بلوار امام حسین
   • ساعت کاری: ۰۸:۰۰ تا ۲۲:۰۰', '2026-07-25', 'تنظیم موتور, دیاگ, گیربکس, بندرعباس', 'auto_repair_shops.json', '9', 'repair_shops', 'بندرعباس', 'automotive, tuning, diagnostic', 'automotive', 'repair.diagnostic', 'active', '1', '0.95', 'خدمات خودرو', 'engine_tuning', 'high', '0', '0', 'automotive_services', 'knowledge_article', '2026-07-25', '2026-07-25'
WHERE NOT EXISTS (
        SELECT 1 FROM knowledge
        WHERE title='تنظیم موتور و دیاگ بندرعباس'
          AND category='automotive_services'
          AND subcategory='repair_shops'
    );
INSERT INTO knowledge_aliases (alias_title, knowledge_id)
SELECT 'دیاگ بندرعباس', id
FROM knowledge
WHERE title='تنظیم موتور و دیاگ بندرعباس' AND category='automotive_services' AND subcategory='repair_shops'
  AND NOT EXISTS (
      SELECT 1 FROM knowledge_aliases ka
      WHERE ka.alias_title='دیاگ بندرعباس' AND ka.knowledge_id=knowledge.id
  );

-- صافکاری و نقاشی بندرعباس
INSERT INTO knowledge (title, category, content, created_at, keywords, source, priority, subcategory, city, tags, topic, intent, status, verified, confidence, category_fa, subtopic, quality, is_deleted, graph_depth, graph_root, entity_type, last_verified, updated_at)
SELECT 'صافکاری و نقاشی بندرعباس', 'automotive_services', '🎨 **مراکز صافکاری و نقاشی خودرو در بندرعباس**

📍 **مناطق اصلی تمرکز صافکاری**:

| منطقه | آدرس | تخصص |
|--------|------|------|
| بلوار پاسداران | اسلام‌آباد، بلوار پاسداران | صافکاری و نقاشی |
| بلوار خلیج فارس | سنگ کن شرقی | صافکاری تخصصی |
| بلوار جمهوری اسلامی | خیابان حر | صافکاری و نقاشی |
| بلوار امام خمینی | نایبند شمالی | صافکاری خودروهای سنگین و سبک |
| شهرک صنعتی | شمال شهر | صافکاری حرفه‌ای (خودروهای سنگین) |

💡 **نکته**: برای دسترسی به لیست کامل صافکاران، از سامانه میدانه یا بهترینو استفاده کنید.', '2026-07-25', 'صافکاری, نقاشی, بندرعباس, خودرو', 'auto_repair_shops.json', '8', 'repair_shops', 'بندرعباس', 'automotive, bodywork, paint', 'automotive', 'repair.bodywork', 'active', '1', '0.95', 'خدمات خودرو', 'bodywork', 'high', '0', '0', 'automotive_services', 'knowledge_article', '2026-07-25', '2026-07-25'
WHERE NOT EXISTS (
        SELECT 1 FROM knowledge
        WHERE title='صافکاری و نقاشی بندرعباس'
          AND category='automotive_services'
          AND subcategory='repair_shops'
    );
INSERT INTO knowledge_aliases (alias_title, knowledge_id)
SELECT 'صافکاری بندرعباس', id
FROM knowledge
WHERE title='صافکاری و نقاشی بندرعباس' AND category='automotive_services' AND subcategory='repair_shops'
  AND NOT EXISTS (
      SELECT 1 FROM knowledge_aliases ka
      WHERE ka.alias_title='صافکاری بندرعباس' AND ka.knowledge_id=knowledge.id
  );

-- باطری‌سازی و برق خودرو بندرعباس
INSERT INTO knowledge (title, category, content, created_at, keywords, source, priority, subcategory, city, tags, topic, intent, status, verified, confidence, category_fa, subtopic, quality, is_deleted, graph_depth, graph_root, entity_type, last_verified, updated_at)
SELECT 'باطری‌سازی و برق خودرو بندرعباس', 'automotive_services', '🔋 **مراکز باطری سازی و برق خودرو در بندرعباس**

📍 **مناطق اصلی تمرکز باطری فروشان**:

| منطقه | آدرس | خدمات |
|--------|------|--------|
| بلوار امام خمینی | چهارراه شهدا تا میدان ولیعصر | فروش، تعویض، شارژ باطری |
| خیابان اسدآبادی | چهارراه مرادی تا چهارراه فاطمیه | باطری تخصصی و لوازم یدکی |
| بلوار جمهوری اسلامی | نزدیک سه‌راه گاراژ | باطری خودروهای سنگین |
| بلوار شهید رجایی | میدان الغدیر | خدمات باطری خودروهای سنگین |

⚡ **خدمات قابل ارائه**:
• فروش باطری اسیدی و اتمی (صبا، سپاهان، نیرو باتری)
• تعویض و نصب باطری در محل
• شارژ باطری
• تست و عیب‌یابی دینام (آلترناتور)
• تست و عیب‌یابی استارت

🔌 **برق خودرو تخصصی**:
• **برق خودرو Help**: تعمیرات تخصصی برق خودرو
• آدرس: شهید حقانی، بین شهید جعفری و هرمزگان ۲
• ساعت کاری: ۰۸:۰۰ تا ۲۳:۰۰', '2026-07-25', 'باطری, برق خودرو, بندرعباس, دینام, استارت', 'auto_repair_shops.json', '8', 'repair_shops', 'بندرعباس', 'automotive, battery, electrical', 'automotive', 'repair.electrical', 'active', '1', '0.95', 'خدمات خودرو', 'battery_electric', 'high', '0', '0', 'automotive_services', 'knowledge_article', '2026-07-25', '2026-07-25'
WHERE NOT EXISTS (
        SELECT 1 FROM knowledge
        WHERE title='باطری‌سازی و برق خودرو بندرعباس'
          AND category='automotive_services'
          AND subcategory='repair_shops'
    );
INSERT INTO knowledge_aliases (alias_title, knowledge_id)
SELECT 'برق خودرو بندرعباس', id
FROM knowledge
WHERE title='باطری‌سازی و برق خودرو بندرعباس' AND category='automotive_services' AND subcategory='repair_shops'
  AND NOT EXISTS (
      SELECT 1 FROM knowledge_aliases ka
      WHERE ka.alias_title='برق خودرو بندرعباس' AND ka.knowledge_id=knowledge.id
  );

-- نمایندگی‌های مجاز بندرعباس
INSERT INTO knowledge (title, category, content, created_at, keywords, source, priority, subcategory, city, tags, topic, intent, status, verified, confidence, category_fa, subtopic, quality, is_deleted, graph_depth, graph_root, entity_type, last_verified, updated_at)
SELECT 'نمایندگی‌های مجاز بندرعباس', 'automotive_services', '🏢 **نمایندگی‌های مجاز خودرو در بندرعباس**

| برند | نام نمایندگی | موقعیت |
|------|-------------|--------|
| رنو | خدمات فنی رنو | بلوار جمهوری اسلامی، بلوار امام حسین |
| رنو | تعمیرگاه رنو پوران | بلوار امام حسین، شهید باکری ۱۸ |
| ولوو/رنو | تعمیرگاه ولوو، رنو دیاکو | بزرگراه سیرجان - بندرعباس |
| تویوتا | جهان نویس آریا (کد ۱۴۵۱) | گلشهر جنوبی، میدان ۹ دی، خیابان جامی ۱ |
| ایران خودرو | نمایندگی‌های متعدد | بلوار امام خمینی، نایبند شمالی، گلشهر |

💡 **توصیه**: برای خودروهای تحت گارانتی، حتماً به نمایندگی‌های مجاز مراجعه کنید.', '2026-07-25', 'نمایندگی, رنو, تویوتا, ایران خودرو, بندرعباس', 'auto_repair_shops.json', '8', 'repair_shops', 'بندرعباس', 'automotive, dealers, warranty', 'automotive', 'repair.dealer', 'active', '1', '0.95', 'خدمات خودرو', 'dealers', 'high', '0', '0', 'automotive_services', 'knowledge_article', '2026-07-25', '2026-07-25'
WHERE NOT EXISTS (
        SELECT 1 FROM knowledge
        WHERE title='نمایندگی‌های مجاز بندرعباس'
          AND category='automotive_services'
          AND subcategory='repair_shops'
    );
INSERT INTO knowledge_aliases (alias_title, knowledge_id)
SELECT 'نمایندگی خودرو بندرعباس', id
FROM knowledge
WHERE title='نمایندگی‌های مجاز بندرعباس' AND category='automotive_services' AND subcategory='repair_shops'
  AND NOT EXISTS (
      SELECT 1 FROM knowledge_aliases ka
      WHERE ka.alias_title='نمایندگی خودرو بندرعباس' AND ka.knowledge_id=knowledge.id
  );

-- تعمیرات تخصصی خودروهای چینی
INSERT INTO knowledge (title, category, content, created_at, keywords, source, priority, subcategory, city, tags, topic, intent, status, verified, confidence, category_fa, subtopic, quality, is_deleted, graph_depth, graph_root, entity_type, last_verified, updated_at)
SELECT 'تعمیرات تخصصی خودروهای چینی', 'automotive_services', '🇨🇳 **تعمیرگاه‌های تخصصی خودروهای چینی در بندرعباس**

1. **تعمیرگاه تخصصی زانتیا**
   • تخصص: خودروهای چینی، زانتیا
   • آدرس: ۱۲ فروردین شرقی، امامت، امامت ۹
   • ساعت کاری: ۰۸:۰۰ تا ۲۱:۰۰

2. **مکانیکی چینی حامی**
   • تخصص: خودروهای چینی
   • آدرس: گاز، گوهران ۵۲، گوهران ۳۹
   • ساعت کاری: جمعه ۰۸:۰۰ تا ۲۲:۰۰

3. **تعمیرگاه کینو کار**
   • تخصص: خودروهای چینی
   • آدرس: بلوار سوم خرداد، کار، استقلال', '2026-07-25', 'خودروهای چینی, زانتیا, بندرعباس, تعمیرگاه', 'auto_repair_shops.json', '8', 'repair_shops', 'بندرعباس', 'automotive, chinese-cars, repair', 'automotive', 'repair.chinese_cars', 'active', '1', '0.95', 'خدمات خودرو', 'chinese_cars', 'high', '0', '0', 'automotive_services', 'knowledge_article', '2026-07-25', '2026-07-25'
WHERE NOT EXISTS (
        SELECT 1 FROM knowledge
        WHERE title='تعمیرات تخصصی خودروهای چینی'
          AND category='automotive_services'
          AND subcategory='repair_shops'
    );
INSERT INTO knowledge_aliases (alias_title, knowledge_id)
SELECT 'تعمیرگاه خودروهای چینی', id
FROM knowledge
WHERE title='تعمیرات تخصصی خودروهای چینی' AND category='automotive_services' AND subcategory='repair_shops'
  AND NOT EXISTS (
      SELECT 1 FROM knowledge_aliases ka
      WHERE ka.alias_title='تعمیرگاه خودروهای چینی' AND ka.knowledge_id=knowledge.id
  );

-- تعمیرات تخصصی گیربکس
INSERT INTO knowledge (title, category, content, created_at, keywords, source, priority, subcategory, city, tags, topic, intent, status, verified, confidence, category_fa, subtopic, quality, is_deleted, graph_depth, graph_root, entity_type, last_verified, updated_at)
SELECT 'تعمیرات تخصصی گیربکس', 'automotive_services', '⚙️ **مراکز تخصصی تعمیرات گیربکس در بندرعباس**

1. **کهتک تکنیک**
   • تخصص: دیاگ، تنظیم موتور، گیربکس
   • آدرس: شهید تابدار، اخلاص ۱۴
   • ساعت کاری: ۰۸:۰۰ تا ۲۲:۰۰

2. **کیلومترسازی مهدی**
   • تخصص: کیلومترسازی، تنظیم موتور
   • آدرس: بلوار جمهوری اسلامی، بسیج ۱۸

⚠️ **نکته**: برای خودروهای با گیربکس اتوماتیک، حتماً به مراکز تخصصی مراجعه کنید.', '2026-07-25', 'گیربکس, تعمیرات, بندرعباس, اتوماتیک', 'auto_repair_shops.json', '8', 'repair_shops', 'بندرعباس', 'automotive, gearbox, repair', 'automotive', 'repair.gearbox', 'active', '1', '0.95', 'خدمات خودرو', 'gearbox', 'high', '0', '0', 'automotive_services', 'knowledge_article', '2026-07-25', '2026-07-25'
WHERE NOT EXISTS (
        SELECT 1 FROM knowledge
        WHERE title='تعمیرات تخصصی گیربکس'
          AND category='automotive_services'
          AND subcategory='repair_shops'
    );
INSERT INTO knowledge_aliases (alias_title, knowledge_id)
SELECT 'تعمیر گیربکس بندرعباس', id
FROM knowledge
WHERE title='تعمیرات تخصصی گیربکس' AND category='automotive_services' AND subcategory='repair_shops'
  AND NOT EXISTS (
      SELECT 1 FROM knowledge_aliases ka
      WHERE ka.alias_title='تعمیر گیربکس بندرعباس' AND ka.knowledge_id=knowledge.id
  );

-- تعمیرگاه‌های ۲۴ ساعته بندرعباس
INSERT INTO knowledge (title, category, content, created_at, keywords, source, priority, subcategory, city, tags, topic, intent, status, verified, confidence, category_fa, subtopic, quality, is_deleted, graph_depth, graph_root, entity_type, last_verified, updated_at)
SELECT 'تعمیرگاه‌های ۲۴ ساعته بندرعباس', 'automotive_services', '🌙 **تعمیرگاه‌های ۲۴ ساعته بندرعباس**

1. **خدمات فنی رنو**
   • تخصص: رنو (نمایندگی مجاز)
   • آدرس: بلوار جمهوری اسلامی، بلوار امام حسین
   • وضعیت: ۲۴ ساعته

2. **مرکز خدمات فنی تخصصی خودروی نعمت**
   • تخصص: مکانیک تخصصی (موتور و گیربکس)
   • آدرس: شهید حقانی، بلوار شهدا
   • وضعیت: ۲۴ ساعته

3. **تعمیرگاه بیژن**
   • تخصص: عمومی
   • آدرس: ۱۲ فروردین شرقی، امامت
   • وضعیت: ۲۴ ساعته

4. **تعمیرگاه تخصصی خودرو جزیره**
   • تخصص: عمومی تخصصی
   • آدرس: بلوار جمهوری اسلامی، بلوار شهدا
   • ساعت کاری: ۰۰:۰۰ تا ۱۳:۰۰ و جمعه ۰۹:۰۰ تا ۱۲:۰۰', '2026-07-25', 'تعمیرگاه 24 ساعته, شبانه روزی, بندرعباس', 'auto_repair_shops.json', '7', 'repair_shops', 'بندرعباس', 'automotive, 24h, repair', 'automotive', 'repair.24h', 'active', '1', '0.95', 'خدمات خودرو', '24h', 'high', '0', '0', 'automotive_services', 'knowledge_article', '2026-07-25', '2026-07-25'
WHERE NOT EXISTS (
        SELECT 1 FROM knowledge
        WHERE title='تعمیرگاه‌های ۲۴ ساعته بندرعباس'
          AND category='automotive_services'
          AND subcategory='repair_shops'
    );
INSERT INTO knowledge_aliases (alias_title, knowledge_id)
SELECT 'تعمیرگاه شبانه‌روزی بندرعباس', id
FROM knowledge
WHERE title='تعمیرگاه‌های ۲۴ ساعته بندرعباس' AND category='automotive_services' AND subcategory='repair_shops'
  AND NOT EXISTS (
      SELECT 1 FROM knowledge_aliases ka
      WHERE ka.alias_title='تعمیرگاه شبانه‌روزی بندرعباس' AND ka.knowledge_id=knowledge.id
  );

-- مناطق تمرکز تعمیرگاه‌ها
INSERT INTO knowledge (title, category, content, created_at, keywords, source, priority, subcategory, city, tags, topic, intent, status, verified, confidence, category_fa, subtopic, quality, is_deleted, graph_depth, graph_root, entity_type, last_verified, updated_at)
SELECT 'مناطق تمرکز تعمیرگاه‌ها', 'automotive_services', '🗺️ **مناطق اصلی تمرکز تعمیرگاه‌های خودرو در بندرعباس**

| منطقه | محدوده | نوع مراکز | تعداد تقریبی |
|--------|--------|-----------|--------------|
| بلوار جمهوری اسلامی | سه‌راه گاراژ تا بلوار امام حسین | مکانیک، صافکاری، تعمیرگاه عمومی | بالا (بیش از ۲۰ مرکز) |
| بلوار امام خمینی | نایبند شمالی و گلشهر | مکانیک، باطری سازی، نمایندگی | متوسط (۱۰-۱۵ مرکز) |
| بلوار شهید رجایی | میدان الغدیر تا سه‌راه گاراژ | خودروهای سنگین و نیمه سنگین | متوسط |
| بلوار پاسداران | اسلام‌آباد، شهرک شهید بهشتی | مکانیک عمومی، تعمیرگاه محلی | متوسط |
| خیابان اسدآبادی | چهارراه مرادی تا چهارراه فاطمیه | لوازم یدکی، باطری، برق خودرو | بالا |
| بلوار خلیج فارس | سنگ کن شرقی | تعمیرگاه تخصصی | پایین (کمتر از ۵ مرکز) |', '2026-07-25', 'مناطق تعمیرگاه, بلوار جمهوری اسلامی, بندرعباس', 'auto_repair_shops.json', '7', 'repair_shops', 'بندرعباس', 'automotive, areas, map', 'automotive', 'repair.service_areas', 'active', '1', '0.95', 'خدمات خودرو', 'service_areas', 'high', '0', '0', 'automotive_services', 'knowledge_article', '2026-07-25', '2026-07-25'
WHERE NOT EXISTS (
        SELECT 1 FROM knowledge
        WHERE title='مناطق تمرکز تعمیرگاه‌ها'
          AND category='automotive_services'
          AND subcategory='repair_shops'
    );
INSERT INTO knowledge_aliases (alias_title, knowledge_id)
SELECT 'مناطق تعمیرگاه بندرعباس', id
FROM knowledge
WHERE title='مناطق تمرکز تعمیرگاه‌ها' AND category='automotive_services' AND subcategory='repair_shops'
  AND NOT EXISTS (
      SELECT 1 FROM knowledge_aliases ka
      WHERE ka.alias_title='مناطق تعمیرگاه بندرعباس' AND ka.knowledge_id=knowledge.id
  );

-- راهنمای انتخاب تعمیرگاه
INSERT INTO knowledge (title, category, content, created_at, keywords, source, priority, subcategory, city, tags, topic, intent, status, verified, confidence, category_fa, subtopic, quality, is_deleted, graph_depth, graph_root, entity_type, last_verified, updated_at)
SELECT 'راهنمای انتخاب تعمیرگاه', 'automotive_services', '💡 **راهنمای انتخاب تعمیرگاه مناسب در بندرعباس**

📌 **بر اساس نوع خودرو**:
• خودروهای فرانسوی (رنو): خدمات فنی رنو، رنو پوران
• خودروهای چینی: تعمیرگاه زانتیا، مکانیکی چینی حامی
• خودروهای تویوتا: نمایندگی جهان نویس آریا
• خودروهای سنگین: بلوار شهید رجایی، شهرک صنعتی

📌 **بر اساس نوع تعمیر**:
• تنظیم موتور و دیاگ: کهتک تکنیک، کیلومترسازی مهدی
• گیربکس: کهتک تکنیک
• برق خودرو: برق خودرو Help
• صافکاری و نقاشی: بلوار پاسداران، بلوار خلیج فارس
• باطری: بلوار امام خمینی، خیابان اسدآبادی

📌 **خدمات شبانه‌روزی**:
• خدمات فنی رنو (۲۴ ساعته)
• مرکز نعمت (۲۴ ساعته)
• تعمیرگاه بیژن (۲۴ ساعته)

📌 **منابع آنلاین برای جستجو**:
• میدانه (meidane.com) - لیست ۳۰ تعمیرگاه برتر
• بهترینو (behtarino.com) - جستجوی تفکیکی
• اتحادیه تعمیرکاران استان هرمزگان - مرجع رسمی', '2026-07-25', 'راهنمای تعمیرگاه, انتخاب تعمیرگاه, بندرعباس', 'auto_repair_shops.json', '10', 'repair_shops', 'بندرعباس', 'automotive, guide, selection', 'automotive', 'repair.guide', 'active', '1', '0.95', 'خدمات خودرو', 'selection_guide', 'high', '0', '0', 'automotive_services', 'knowledge_article', '2026-07-25', '2026-07-25'
WHERE NOT EXISTS (
        SELECT 1 FROM knowledge
        WHERE title='راهنمای انتخاب تعمیرگاه'
          AND category='automotive_services'
          AND subcategory='repair_shops'
    );
INSERT INTO knowledge_aliases (alias_title, knowledge_id)
SELECT 'انتخاب تعمیرگاه', id
FROM knowledge
WHERE title='راهنمای انتخاب تعمیرگاه' AND category='automotive_services' AND subcategory='repair_shops'
  AND NOT EXISTS (
      SELECT 1 FROM knowledge_aliases ka
      WHERE ka.alias_title='انتخاب تعمیرگاه' AND ka.knowledge_id=knowledge.id
  );
COMMIT;