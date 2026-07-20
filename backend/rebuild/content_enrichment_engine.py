#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
HDP Content Enrichment Engine
موتور غنی‌سازی محتوای دانش با طبقه‌بندی خودکار
"""

import sqlite3
import sys
from pathlib import Path

# اضافه کردن مسیر پروژه به sys.path
sys.path.insert(0, str(Path(__file__).parent))

from normalizer import normalize
from classifier import KnowledgeClassifier
from models import KnowledgeRecord

DB = "/data/data/com.termux/files/home/ai-system/hdp_x1/development/data/hdp_v2.db"


class ContentEnrichmentEngine:
    """
    موتور غنی‌سازی محتوای دانش
    - طبقه‌بندی خودکار
    - تشخیص موجودیت‌ها
    - تشخیص Intent
    """

    def __init__(self):
        self.conn = sqlite3.connect(DB)
        self.conn.row_factory = sqlite3.Row
        self.cur = self.conn.cursor()
        self.cls = KnowledgeClassifier()
        
        # آمار
        self.stats = {
            'total': 0,
            'updated': 0,
            'errors': 0,
            'categories': {},
            'intents': {},
            'entities': {},
            'cities': {}
        }

    def enrich(self):
        """
        اجرای فرآیند غنی‌سازی روی همه رکوردها
        """
        print("=" * 60)
        print("🚀 HDP Content Enrichment Engine")
        print("=" * 60)

        # ==============================================================
        # 1. خواندن همه رکوردها
        # ==============================================================
        rows = self.cur.execute("""
            SELECT *
            FROM knowledge
            ORDER BY id
        """).fetchall()

        total = len(rows)
        self.stats['total'] = total
        print(f"📚 {total} رکورد برای غنی‌سازی پیدا شد.")
        print("-" * 40)

        # ==============================================================
        # 2. غنی‌سازی هر رکورد
        # ==============================================================
        for i, row in enumerate(rows, 1):
            try:
                # نرمال‌سازی
                title = normalize(row["title"] or "")
                content = normalize(row["content"] or "")
                
                # طبقه‌بندی
                record = KnowledgeRecord(
                    title=title,
                    content=content
                )
                record = self.cls.classify(record)
                
                # به‌روزرسانی دیتابیس
                self.cur.execute("""
                    UPDATE knowledge
                    SET
                        title = ?,
                        category = ?,
                        entity_type = ?,
                        city = ?,
                        intent = ?,
                        main_intent = ?,
                        sub_intent = ?,
                        topic = ?
                    WHERE id = ?
                """, (
                    title,
                    record.category,
                    record.entity_type,
                    record.city,
                    record.intent,
                    record.main_intent,
                    record.sub_intent,
                    record.topic,
                    row["id"]
                ))
                
                # آمار
                self.stats['updated'] += 1
                self.stats['categories'][record.category] = self.stats['categories'].get(record.category, 0) + 1
                self.stats['intents'][record.intent] = self.stats['intents'].get(record.intent, 0) + 1
                self.stats['entities'][record.entity_type] = self.stats['entities'].get(record.entity_type, 0) + 1
                if record.city:
                    self.stats['cities'][record.city] = self.stats['cities'].get(record.city, 0) + 1

            except Exception as e:
                self.stats['errors'] += 1
                print(f"❌ خطا در رکورد {row['id']}: {e}")
                continue

            # Commit هر ۵۰۰ رکورد
            if i % 500 == 0:
                self.conn.commit()
                print(f"📊 {i:,}/{total:,} رکورد پردازش شد...")

        # ==============================================================
        # 3. ذخیره نهایی و نمایش آمار
        # ==============================================================
        self.conn.commit()
        self._print_stats()

    def _print_stats(self):
        """نمایش آمار نهایی"""
        print("\n" + "=" * 60)
        print("📊 آمار نهایی غنی‌سازی")
        print("=" * 60)
        print(f"   کل رکوردها: {self.stats['total']:,}")
        print(f"   به‌روزرسانی: {self.stats['updated']:,}")
        print(f"   خطاها: {self.stats['errors']:,}")

        print("\n📂 توزیع دسته‌بندی‌ها:")
        for cat, count in sorted(self.stats['categories'].items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"      {cat}: {count:,}")

        print("\n🎯 توزیع Intent‌ها:")
        for intent, count in sorted(self.stats['intents'].items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"      {intent}: {count:,}")

        print("\n🏷️ توزیع نوع موجودیت‌ها:")
        for entity, count in sorted(self.stats['entities'].items(), key=lambda x: x[1], reverse=True):
            print(f"      {entity}: {count:,}")

        print("\n🏙️ شهرهای شناسایی‌شده:")
        for city, count in sorted(self.stats['cities'].items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"      {city}: {count:,}")

        print("\n" + "=" * 60)
        print("✅ غنی‌سازی محتوا کامل شد!")
        print("=" * 60)

    def close(self):
        """بستن اتصال دیتابیس"""
        self.conn.close()


if __name__ == "__main__":
    engine = ContentEnrichmentEngine()
    try:
        engine.enrich()
    finally:
        engine.close()
