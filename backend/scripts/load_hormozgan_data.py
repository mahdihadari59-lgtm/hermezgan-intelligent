#!/usr/bin/env python3
"""
بارگذاری داده‌های hormozgan_knowledge.json در SQLite + FTS5
ساختار واقعی: دیکشنری با 9631 کلید (عنوان → محتوا)

گزینه‌ها:
  --reset    پاک کردن داده‌های قبلی قبل از بارگذاری
  --reindex  بازسازی کامل ایندکس
  --dry-run  فقط نمایش آماده بدون بارگذاری واقعی
"""

import json
import os
import sys
import argparse

# اضافه کردن مسیر پروژه
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.sqlite_service import SQLiteService
from utils.persian_normalizer import PersianNormalizer

def extract_category_from_title(title: str) -> str:
    """استخراج دسته‌بندی از عنوان"""
    categories = {
        'ترافیک': ['ترافیک', 'چهارراه', 'میدان', 'بلوار', 'خیابان', 'گلوگاه', 'تقاطع'],
        'گردشگری': ['معرفی', 'جزیره', 'ساحل', 'جاذبه', 'تاریخی', 'طبیعی', 'بازار', 'جاذبه‌های'],
        'آب و هوا': ['آب و هوا', 'دما', 'بارش', 'رطوبت', 'باد', 'اقلیم'],
        'قوانین': ['قانون', 'مقررات', 'آیین نامه', 'ماده', 'قوانین'],
        'رانندگی': ['رانندگی', 'گواهینامه', 'سبقت', 'سرعت', 'رانندگان'],
        'امدادی': ['بیمارستان', 'درمانگاه', 'اورژانس', 'پلیس', 'امداد'],
        'فرهنگی': ['فرهنگ', 'آداب', 'رسوم', 'محلی', 'گویش'],
        'اقتصادی': ['اقتصاد', 'بازار', 'تجارت', 'صادرات', 'اقتصاد'],
        'تاریخی': ['تاریخ', 'پیشینه', 'باستان', 'قلعه', 'تاریخی'],
        'آموزشی': ['آموزش', 'مدرسه', 'دانشگاه', 'کتاب', 'آموزشی']
    }
    
    for category, keywords in categories.items():
        for keyword in keywords:
            if keyword in title:
                return category
    return 'عمومی'

def load_hormozgan_data(reset: bool = False, dry_run: bool = False):
    """بارگذاری داده‌ها"""
    
    print("=" * 80)
    print("📦 بارگذاری داده‌های دانش هرمزگان (ساختار دیکشنری)")
    print("=" * 80)
    
    if dry_run:
        print("⚠️ حالت Dry-run - هیچ تغییری در دیتابیس اعمال نمی‌شود")
    
    # مسیر فایل دانش
    knowledge_path = os.path.expanduser("~/hormozgan-driver-pro121/hdp_flask_app/data/hormozgan_knowledge.json")
    
    if not os.path.exists(knowledge_path):
        print(f"❌ فایل پیدا نشد: {knowledge_path}")
        return False
    
    print(f"📂 بارگذاری فایل: {knowledge_path}")
    
    # بارگذاری فایل JSON
    with open(knowledge_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # بررسی ساختار
    if not isinstance(data, dict):
        print(f"❌ ساختار فایل دیکشنری نیست: {type(data).__name__}")
        return False
    
    print(f"✅ تعداد کلیدها: {len(data):,}")
    
    # تبدیل به لیست اسناد
    documents = []
    for title, content in data.items():
        if content and isinstance(content, str):
            documents.append({
                'title': title,
                'content': content
            })
    
    print(f"✅ تعداد اسناد معتبر: {len(documents):,}")
    
    # نرمال‌سازی داده‌ها
    print("\n🔄 نرمال‌سازی داده‌ها...")
    normalized_docs = []
    
    for i, doc in enumerate(documents):
        original_title = doc['title']
        original_content = doc['content']
        
        # نرمال‌سازی
        normalized_title = PersianNormalizer.normalize(original_title)
        normalized_content = PersianNormalizer.normalize(original_content)
        category = extract_category_from_title(original_title)
        
        # استخراج کلمات کلیدی از عنوان
        keywords = ' '.join(PersianNormalizer.tokenize(original_title)[:5])
        
        normalized_docs.append({
            'title': normalized_title[:500],
            'content': normalized_content[:5000],
            'original_title': original_title,
            'category': category,
            'keywords': keywords,
            'source': 'hormozgan_knowledge'
        })
        
        if (i + 1) % 1000 == 0:
            print(f"   پردازش شده: {i + 1:,} / {len(documents):,}")
    
    print(f"✅ نرمال‌سازی {len(normalized_docs):,} سند انجام شد")
    
    # نمایش نمونه
    print("\n🔍 نمونه داده نرمال‌شده:")
    if normalized_docs:
        sample = normalized_docs[0]
        print(f"   عنوان اصلی: {sample['original_title'][:80]}")
        print(f"   عنوان نرمال‌شده: {sample['title'][:80]}")
        print(f"   دسته: {sample['category']}")
        print(f"   کلمات کلیدی: {sample['keywords'][:80]}")
        print(f"   محتوا: {sample['content'][:150]}...")
    
    if dry_run:
        print("\n⚠️ حالت Dry-run - پایان کار")
        return True
    
    # اتصال به دیتابیس
    print("\n🔗 اتصال به SQLite...")
    db = SQLiteService("data/hdp_v2.db")
    
    if not db.connect():
        print("❌ خطا در اتصال به دیتابیس")
        return False
    
    # ایجاد جدول‌ها
    print("📊 ایجاد جدول‌ها...")
    db.create_tables()
    
    # پاک کردن داده‌های قبلی در صورت نیاز
    if reset:
        print("🔄 پاک کردن داده‌های قبلی...")
        db.cursor.execute("DELETE FROM hormozgan_knowledge")
        db.cursor.execute("DELETE FROM hormozgan_fts")
        db.conn.commit()
    
    # ایندکس کردن داده‌ها
    print("\n📚 ایندکس کردن داده‌ها در FTS5...")
    
    count = 0
    for doc in normalized_docs:
        db.cursor.execute('''
            INSERT INTO hormozgan_knowledge 
            (title, original_title, content, category, keywords, source)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            doc['title'],
            doc['original_title'],
            doc['content'],
            doc['category'],
            doc['keywords'],
            doc['source']
        ))
        
        last_id = db.cursor.lastrowid
        
        # درج در جدول FTS5
        db.cursor.execute('''
            INSERT INTO hormozgan_fts (rowid, title, content, category)
            VALUES (?, ?, ?, ?)
        ''', (
            last_id,
            doc['title'],
            doc['content'],
            doc['category']
        ))
        
        count += 1
        
        if count % 1000 == 0:
            db.conn.commit()
            print(f"   ایندکس شده: {count:,} / {len(normalized_docs):,}")
    
    db.conn.commit()
    
    # آمار نهایی
    print(f"\n✅ ایندکس {count:,} سند با موفقیت انجام شد")
    
    # دریافت آمار دسته‌بندی
    db.cursor.execute("SELECT category, COUNT(*) as count FROM hormozgan_knowledge GROUP BY category ORDER BY count DESC")
    categories = db.cursor.fetchall()
    
    print(f"\n📈 آمار دسته‌بندی:")
    for cat in categories[:15]:
        print(f"   • {cat['category']}: {cat['count']:,} سند")
    
    # تست جستجو
    print("\n🧪 تست جستجو:")
    test_queries = ["هرمزگان", "بندرعباس", "قشم"]
    for query in test_queries:
        results = db.search_fts(query, limit=3)
        print(f"   • '{query}': {len(results)} نتیجه")
    
    db.close()
    
    print("\n✅ بارگذاری و ایندکس کردن با موفقیت کامل شد!")
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='بارگذاری داده‌های هرمزگان در SQLite + FTS5')
    parser.add_argument('--reset', action='store_true', help='پاک کردن داده‌های قبلی')
    parser.add_argument('--reindex', action='store_true', help='بازسازی کامل ایندکس')
    parser.add_argument('--dry-run', action='store_true', help='فقط نمایش آماده بدون بارگذاری')
    
    args = parser.parse_args()
    
    # اگر reindex باشد، reset هم فعال می‌شود
    reset = args.reset or args.reindex
    
    success = load_hormozgan_data(reset=reset, dry_run=args.dry_run)
    sys.exit(0 if success else 1)
