#!/usr/bin/env python3
"""
مقایسه دقیق بین JSON اصلی و دیتابیس SQLite فعلی
برای پیدا کردن رکوردهایی که در دیتابیس نیستند
"""

import json
import sqlite3
import re
from typing import Dict, Set, List, Tuple

# مسیرها
JSON_PATH = "/data/data/com.termux/files/home/hormozgan-driver-pro121/hdp_flask_app/data/hormozgan_knowledge.json"
SQLITE_PATH = "data/hdp_v2.db"

# کلیدهای متادیتا که باید حذف شوند
METADATA_KEYS = {
    "version", "total_keys", "east_hormozgan_version", 
    "atlas_version", "total_records", "version_info"
}

# کلیدهای کوتاه ولی معتبر (گویش بندری)
VALID_SHORT_KEYS = {
    "شوهر بندری", "شب بندری", "موج بندری", "year"
}

def load_json_keys() -> Tuple[Dict, Set[str], Set[str]]:
    """بارگذاری کلیدهای JSON"""
    with open(JSON_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    all_keys = set(data.keys())
    
    # تشخیص متادیتا (کلیدهایی که باید حذف شوند)
    metadata_keys = set()
    for key in all_keys:
        kl = key.lower()
        if kl.endswith("version") or kl.startswith("total_") or kl in METADATA_KEYS:
            metadata_keys.add(key)
    
    # کلیدهای معتبر (غیر متادیتا)
    valid_keys = all_keys - metadata_keys
    
    return data, all_keys, metadata_keys, valid_keys

def load_sqlite_titles() -> Set[str]:
    """بارگذاری عناوین از SQLite"""
    conn = sqlite3.connect(SQLITE_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT title FROM hormozgan_knowledge")
    titles = {row[0] for row in cursor.fetchall()}
    conn.close()
    return titles

def find_missing_keys(json_keys: Set[str], sqlite_titles: Set[str]) -> List[Tuple[str, str]]:
    """پیدا کردن کلیدهایی که در SQLite نیستند"""
    missing = []
    for key in json_keys:
        # نرمال‌سازی برای مقایسه
        normalized_key = key.strip()
        if normalized_key not in sqlite_titles:
            missing.append((key, "missing"))
    return missing

def find_extra_in_sqlite(json_keys: Set[str], sqlite_titles: Set[str]) -> List[str]:
    """پیدا کردن رکوردهایی که در SQLite هستند ولی در JSON نیستند"""
    extra = []
    for title in sqlite_titles:
        if title not in json_keys:
            extra.append(title)
    return extra

def categorize_missing(missing: List[Tuple[str, str]], json_data: Dict) -> Dict:
    """دسته‌بندی رکوردهای گم شده"""
    categories = {
        "metadata": [],      # متادیتا (قابل حذف)
        "short_valid": [],   # کوتاه ولی معتبر
        "valuable": []       # ارزشمند (باید حفظ شوند)
    }
    
    for key, _ in missing:
        # بررسی متادیتا
        kl = key.lower()
        if kl.endswith("version") or kl.startswith("total_") or key in METADATA_KEYS:
            categories["metadata"].append(key)
        # بررسی کوتاه ولی معتبر
        elif key in VALID_SHORT_KEYS or len(key) < 10:
            content = json_data.get(key, "")[:100]
            categories["short_valid"].append({"key": key, "content": content})
        else:
            content = json_data.get(key, "")[:200]
            categories["valuable"].append({"key": key, "content": content})
    
    return categories

def main():
    print("=" * 80)
    print("🔍 مقایسه دقیق JSON اصلی و دیتابیس SQLite")
    print("=" * 80)
    
    # بارگذاری JSON
    json_data, json_all_keys, json_metadata, json_valid = load_json_keys()
    print(f"\n📂 JSON اصلی:")
    print(f"   • کل کلیدها: {len(json_all_keys):,}")
    print(f"   • متادیتا (قابل حذف): {len(json_metadata)}")
    print(f"   • کلیدهای معتبر: {len(json_valid):,}")
    
    # بارگذاری SQLite
    sqlite_titles = load_sqlite_titles()
    print(f"\n🗄️ دیتابیس SQLite فعلی:")
    print(f"   • تعداد رکوردها: {len(sqlite_titles):,}")
    
    # پیدا کردن اختلاف‌ها
    missing = find_missing_keys(json_valid, sqlite_titles)
    extra = find_extra_in_sqlite(json_valid, sqlite_titles)
    
    print(f"\n📊 آمار اختلاف:")
    print(f"   • رکوردهای در JSON که در SQLite نیستند: {len(missing)}")
    print(f"   • رکوردهای در SQLite که در JSON نیستند: {len(extra)}")
    
    # دسته‌بندی رکوردهای گم شده
    if missing:
        categorized = categorize_missing(missing, json_data)
        
        print(f"\n📋 جزئیات رکوردهای گم شده:")
        
        # متادیتا
        if categorized["metadata"]:
            print(f"\n   🗑️ متادیتا (قابل حذف): {len(categorized['metadata'])} مورد")
            for key in categorized["metadata"]:
                print(f"      - {key}")
        
        # کوتاه ولی معتبر
        if categorized["short_valid"]:
            print(f"\n   ⚠️ رکوردهای کوتاه ولی معتبر: {len(categorized['short_valid'])} مورد")
            for item in categorized["short_valid"]:
                print(f"      - {item['key']}: {item['content'][:80]}")
        
        # ارزشمند
        if categorized["valuable"]:
            print(f"\n   🔥 رکوردهای ارزشمند (باید حفظ شوند): {len(categorized['valuable'])} مورد")
            for item in categorized["valuable"]:
                print(f"\n      📌 {item['key']}:")
                print(f"         {item['content'][:200]}...")
    
    # رکوردهای اضافی در SQLite
    if extra:
        print(f"\n   ⚠️ رکوردهایی که در SQLite هستند ولی در JSON نیستند:")
        for title in extra[:10]:
            print(f"      - {title[:60]}")
    
    # پیشنهاد نهایی
    print(f"\n" + "=" * 80)
    print("💡 پیشنهاد نهایی برای Master Dataset")
    print("=" * 80)
    
    total_valid_json = len(json_valid)
    total_to_keep = total_valid_json - len(categorized.get("metadata", []))
    
    print(f"\n   • کل رکوردهای JSON معتبر: {total_valid_json:,}")
    print(f"   • متادیتا (حذف شود): {len(categorized.get('metadata', []))}")
    print(f"   • رکوردهای قابل نگهداری: {total_to_keep:,}")
    
    if categorized.get("valuable"):
        print(f"\n   ⚠️ {len(categorized['valuable'])} رکورد ارزشمند در دیتابیس فعلی وجود ندارد!")
        print(f"   📌 این رکوردها باید به دیتابیس جدید اضافه شوند.")
    
    # ذخیره گزارش
    report = {
        "json_total": len(json_all_keys),
        "json_metadata": list(json_metadata),
        "json_valid": len(json_valid),
        "sqlite_total": len(sqlite_titles),
        "missing_count": len(missing),
        "missing_metadata": categorized.get("metadata", []),
        "missing_short_valid": categorized.get("short_valid", []),
        "missing_valuable": categorized.get("valuable", []),
        "extra_in_sqlite": extra[:20]
    }
    
    report_path = "data/logs/json_sqlite_comparison.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n📄 گزارش کامل در {report_path} ذخیره شد")

if __name__ == "__main__":
    main()
