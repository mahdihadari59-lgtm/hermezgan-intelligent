#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
HDP Graph Builder - Knowledge Graph Construction
ساخت گراف دانش از کلمات کلیدی و موجودیت‌ها
"""

import sqlite3
import re
from collections import defaultdict
from typing import Dict, List


class GraphBuilder:
    """
    ساخت گراف دانش از کلمات کلیدی و موجودیت‌ها
    """

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row

    def build(self) -> int:
        """
        ساخت گراف دانش از کلمات کلیدی
        
        Returns:
            تعداد روابط ایجاد شده
        """
        cur = self.conn.cursor()

        # ==============================================================
        # 1. حذف روابط قبلی (برای جلوگیری از تکراری)
        # ==============================================================
        cur.execute("DELETE FROM knowledge_relations WHERE relation_type = 'keyword'")
        self.conn.commit()
        print("🗑️ روابط قبلی با نوع 'keyword' حذف شدند.")

        # ==============================================================
        # 2. خواندن داده‌ها
        # ==============================================================
        rows = cur.execute("""
            SELECT
                id,
                title,
                content,
                category,
                city,
                keywords
            FROM knowledge
            WHERE keywords IS NOT NULL AND keywords != ''
        """).fetchall()

        print(f"📚 {len(rows)} رکورد با کلمات کلیدی پیدا شد.")

        # ==============================================================
        # 3. ساخت ایندکس کلمات کلیدی
        # ==============================================================
        keyword_index = defaultdict(list)

        for row in rows:
            if not row["keywords"]:
                continue

            # جدا کردن کلمات کلیدی
            keywords = [
                w.strip().lower()
                for w in row["keywords"].split(",")
                if w.strip()
            ]

            for keyword in keywords:
                keyword_index[keyword].append(row["id"])

        print(f"🔑 {len(keyword_index)} کلمه کلیدی منحصر‌به‌فرد پیدا شد.")

        # ==============================================================
        # 4. ایجاد روابط با وزن‌دهی پویا
        # ==============================================================
        inserted = 0

        for keyword, ids in keyword_index.items():
            if len(ids) < 2:
                continue

            # محاسبه وزن بر اساس تعداد تکرار
            weight = min(len(ids) / 10.0, 5.0)

            # ایجاد روابط بین تمام زوج‌ها
            for i in range(len(ids)):
                for j in range(i + 1, len(ids)):
                    cur.execute("""
                        INSERT OR IGNORE INTO knowledge_relations
                        (
                            source_id,
                            target_id,
                            relation_type,
                            weight
                        )
                        VALUES
                        (
                            ?,
                            ?,
                            'keyword',
                            ?
                        )
                    """, (
                        ids[i],
                        ids[j],
                        weight
                    ))
                    inserted += 1

        # ==============================================================
        # 5. ذخیره تغییرات
        # ==============================================================
        self.conn.commit()

        print(f"✅ {inserted} رابطه ایجاد شد.")
        return inserted

    def build_entity_graph(self) -> int:
        """
        ساخت گراف بر اساس موجودیت‌های واقعی
        (بندرعباس، شهید رجایی، قشم، چهارراه شهدا، ...)
        
        Returns:
            تعداد روابط ایجاد شده
        """
        cur = self.conn.cursor()

        # ==============================================================
        # 1. حذف روابط قبلی
        # ==============================================================
        cur.execute("DELETE FROM knowledge_relations WHERE relation_type = 'entity'")
        self.conn.commit()
        print("🗑️ روابط قبلی با نوع 'entity' حذف شدند.")

        # ==============================================================
        # 2. خواندن داده‌ها
        # ==============================================================
        rows = cur.execute("""
            SELECT
                id,
                title,
                content,
                category,
                city
            FROM knowledge
        """).fetchall()

        print(f"📚 {len(rows)} رکورد برای استخراج موجودیت‌ها.")

        # ==============================================================
        # 3. الگوهای تشخیص موجودیت
        # ==============================================================
        entity_patterns = {
            'city': r'(بندرعباس|قشم|کیش|میناب|بندرلنگه|جاسک|حاجی‌آباد|رودان|بستک|سیریک|خمیر|پارسیان|ابوموسی|تنب بزرگ|تنب کوچک)',
            'district': r'(منطقه\s+\d+|شهرک\s+\w+|محله\s+\w+)',
            'hospital': r'(بیمارستان\s+\w+|مرکز\s+درمانی\s+\w+|کلینیک\s+\w+)',
            'street': r'(بلوار\s+\w+|خیابان\s+\w+|میدان\s+\w+|چهارراه\s+\w+|پل\s+\w+|کوچه\s+\w+)',
            'place': r'(جزیره\s+\w+|ساحل\s+\w+|پارک\s+\w+|موزه\s+\w+|هتل\s+\w+|رستوران\s+\w+|کافه\s+\w+)',
            'person': r'(شهید\s+\w+|امام\s+\w+|آیت‌الله\s+\w+|دکتر\s+\w+)'
        }

        # ==============================================================
        # 4. استخراج موجودیت‌ها
        # ==============================================================
        entity_index = defaultdict(list)

        for row in rows:
            text = f"{row['title']} {row['content']}"

            for entity_type, pattern in entity_patterns.items():
                matches = re.findall(pattern, text)
                for entity in matches:
                    entity_key = f"{entity_type}:{entity}"
                    entity_index[entity_key].append(row['id'])

        print(f"🔑 {len(entity_index)} موجودیت منحصر‌به‌فرد پیدا شد.")

        # ==============================================================
        # 5. ایجاد روابط موجودیتی (نسخه بهینه)
        # ==============================================================

        MAX_ENTITY_OCCURRENCES = 30
        MAX_NEIGHBOR_LINKS = 5

        inserted = 0

        for entity_key, ids in entity_index.items():

            # حذف رکوردهای تکراری
            ids = list(dict.fromkeys(ids))

            if len(ids) < 2:
                continue

            # محدود کردن موجودیت‌های پرتکرار
            if len(ids) > MAX_ENTITY_OCCURRENCES:
                ids = ids[:MAX_ENTITY_OCCURRENCES]

            weight = round(min(1 + len(ids) / 15.0, 5.0), 2)

            # اتصال هر رکورد فقط به چند همسایه بعدی
            for i in range(len(ids) - 1):

                end = min(i + 1 + MAX_NEIGHBOR_LINKS, len(ids))

                for j in range(i + 1, end):

                    if ids[i] == ids[j]:
                        continue

                    cur.execute("""
                        INSERT OR IGNORE INTO knowledge_relations
                        (
                            source_id,
                            target_id,
                            relation_type,
                            weight
                        )
                        VALUES (?, ?, 'entity', ?)
                    """, (
                        ids[i],
                        ids[j],
                        weight
                    ))

                    inserted += 1

        self.conn.commit()

        print(f"✅ {inserted:,} رابطه موجودیتی ایجاد شد.")
        return inserted

    def get_stats(self) -> Dict:
        """دریافت آمار گراف"""
        cur = self.conn.cursor()
        
        stats = {
            'total_relations': 0,
            'by_type': {},
            'avg_weight': 0,
            'total_nodes': 0
        }
        
        # تعداد کل روابط
        cur.execute("SELECT COUNT(*) as count FROM knowledge_relations")
        stats['total_relations'] = cur.fetchone()['count']
        
        # آمار بر اساس نوع
        cur.execute("""
            SELECT 
                relation_type,
                COUNT(*) as count,
                AVG(weight) as avg_weight
            FROM knowledge_relations
            GROUP BY relation_type
        """)
        
        for row in cur.fetchall():
            stats['by_type'][row['relation_type']] = {
                'count': row['count'],
                'avg_weight': row['avg_weight']
            }
        
        # تعداد گره‌های منحصر‌به‌فرد
        cur.execute("""
            SELECT COUNT(DISTINCT source_id) as count
            FROM knowledge_relations
        """)
        stats['total_nodes'] = cur.fetchone()['count']
        
        return stats

    def close(self):
        """بستن اتصال دیتابیس"""
        self.conn.close()


if __name__ == "__main__":
    import sys

    # مسیر دیتابیس
    DB_PATH = "/data/data/com.termux/files/home/ai-system/hdp_x1/development/data/hdp_v2.db"

    print("=" * 60)
    print("🏗️ HDP Graph Builder")
    print("=" * 60)

    builder = GraphBuilder(DB_PATH)

    # ==============================================================
    # ساخت گراف کلمات کلیدی
    # ==============================================================
    print("\n📊 مرحله 1: ساخت گراف کلمات کلیدی")
    print("-" * 40)
    keyword_count = builder.build()

    # ==============================================================
    # ساخت گراف موجودیت‌ها
    # ==============================================================
    print("\n📊 مرحله 2: ساخت گراف موجودیت‌ها")
    print("-" * 40)
    entity_count = builder.build_entity_graph()

    # ==============================================================
    # نمایش آمار
    # ==============================================================
    stats = builder.get_stats()
    
    print("\n📈 آمار نهایی گراف:")
    print("-" * 40)
    print(f"   کل روابط: {stats['total_relations']:,}")
    print(f"   گره‌های منحصر‌به‌فرد: {stats['total_nodes']:,}")
    print("\n   تفکیک بر اساس نوع:")
    for rel_type, data in stats['by_type'].items():
        print(f"      {rel_type}: {data['count']:,} رابطه (میانگین وزن: {data['avg_weight']:.2f})")

    builder.close()

    print("\n" + "=" * 60)
    print("✅ ساخت گراف دانش کامل شد!")
    print("=" * 60)
    print(f"   کلمات کلیدی: {keyword_count:,} رابطه")
    print(f"   موجودیت‌ها: {entity_count:,} رابطه")
    print("=" * 60)
