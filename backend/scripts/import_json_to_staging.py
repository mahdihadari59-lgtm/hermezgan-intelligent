#!/usr/bin/env python3
"""
اسکریپت ساده برای وارد کردن فایل JSON به staging
"""

import json
import os
import sys
import sqlite3

# اضافه کردن مسیر پروژه
sys.path.insert(0, os.path.abspath("."))

from utils.persian_normalizer import PersianNormalizer

def import_json_to_staging(json_path: str, staging_db: str = "data/staging/hormozgan_staging.db"):
    """وارد کردن فایل JSON به staging"""
    
    print(f"📂 بارگذاری فایل: {json_path}")
    
    if not os.path.exists(json_path):
        print(f"❌ فایل پیدا نشد: {json_path}")
        return False
    
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # استخراج تمام رکوردها از ساختار تو در تو
    documents = []
    
    def extract_records(obj, parent_key=""):
        """استخراج رکوردها از ساختار تو در تو"""
        if isinstance(obj, dict):
            # اگر دیکشنری دارای فیلدهای استاندارد است
            if 'name' in obj and ('description' in obj or 'address' in obj):
                title = obj.get('name', '')
                content = f"{obj.get('description', '')} {obj.get('address', '')} {obj.get('specialty', '')}"
                if title and content:
                    documents.append({
                        'title': title,
                        'content': content,
                        'category': parent_key
                    })
            else:
                # بررسی مقادیر دیکشنری
                for key, value in obj.items():
                    extract_records(value, f"{parent_key}/{key}" if parent_key else key)
        elif isinstance(obj, list):
            for item in obj:
                extract_records(item, parent_key)
        elif isinstance(obj, str) and len(obj) > 50 and parent_key:
            # اگر مقدار string بلند است
            documents.append({
                'title': parent_key.replace('/', ' - '),
                'content': obj,
                'category': 'general'
            })
    
    extract_records(data)
    
    print(f"✅ {len(documents)} رکورد استخراج شد")
    
    # نمایش نمونه
    if documents:
        print(f"\n📝 نمونه رکوردها:")
        for i, doc in enumerate(documents[:3], 1):
            print(f"   {i}. {doc['title'][:60]}")
    
    # اتصال به staging
    conn = sqlite3.connect(staging_db)
    cursor = conn.cursor()
    
    # درج رکوردها
    count = 0
    for doc in documents:
        title = PersianNormalizer.normalize(doc['title'])[:500]
        content = PersianNormalizer.normalize(doc['content'])[:5000]
        
        cursor.execute("""
            INSERT INTO hormozgan_knowledge (title, original_title, content, category, source)
            VALUES (?, ?, ?, ?, ?)
        """, (title, doc['title'], content, doc.get('category', 'ترافیک'), 'json_import'))
        
        last_id = cursor.lastrowid
        cursor.execute("""
            INSERT INTO hormozgan_fts (rowid, title, content, category)
            VALUES (?, ?, ?, ?)
        """, (last_id, title, content, doc.get('category', 'ترافیک')))
        
        count += 1
        if count % 100 == 0:
            conn.commit()
            print(f"   درج شده: {count}/{len(documents)}")
    
    conn.commit()
    conn.close()
    
    print(f"\n✅ {count} رکورد به staging اضافه شد")
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("استفاده: python import_json_to_staging.py <json_file>")
        sys.exit(1)
    
    success = import_json_to_staging(sys.argv[1])
    sys.exit(0 if success else 1)
