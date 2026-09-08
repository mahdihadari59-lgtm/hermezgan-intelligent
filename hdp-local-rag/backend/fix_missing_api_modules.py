#!/usr/bin/env python3
# ============================================================
# fix_missing_api_modules.py
# بررسی و بازسازی خودکار ماژول‌های گم‌شده app/api/*
# که در __init__.py یا server.py ایمپورت می‌شوند ولی فایلشان حذف شده
# ============================================================
import os
import re
import ast

APP_DIR = "app"
API_DIR = os.path.join(APP_DIR, "api")

# الگوی فایل‌های "re-export ساده" که قبلاً پیدا کردیم
STUB_TEMPLATE = """from __future__ import annotations

from app.api.chat import router
"""


def find_imports_of_app_api(root):
    """پیدا کردن همه importهای app.api.X در کل پروژه"""
    imports = set()
    pattern = re.compile(r"from\s+app\.api\.(\w+)\s+import|from\s+\.(\w+)\s+import")

    for dirpath, dirnames, filenames in os.walk(root):
        if "__pycache__" in dirpath or ".venv" in dirpath or "venv" in dirpath:
            continue
        for fname in filenames:
            if not fname.endswith(".py"):
                continue
            fpath = os.path.join(dirpath, fname)
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    content = f.read()
            except (IOError, UnicodeDecodeError):
                continue

            # فقط داخل app/api/__init__.py حالت نسبی (from .X) معتبره
            for m in pattern.finditer(content):
                if m.group(1):
                    imports.add(m.group(1))
                elif m.group(2) and dirpath == API_DIR:
                    imports.add(m.group(2))

    return imports


def main():
    print("🔍 در حال بررسی importهای app.api.* در کل پروژه...\n")

    referenced = find_imports_of_app_api(APP_DIR)
    print(f"📦 ماژول‌های ارجاع‌داده‌شده: {sorted(referenced)}\n")

    missing = []
    existing = []

    for mod in sorted(referenced):
        fpath = os.path.join(API_DIR, f"{mod}.py")
        if os.path.exists(fpath):
            existing.append(mod)
        else:
            # ممکنه پکیج (پوشه با __init__.py) باشه نه فایل تکی
            dirpath = os.path.join(API_DIR, mod)
            if os.path.isdir(dirpath) and os.path.exists(os.path.join(dirpath, "__init__.py")):
                existing.append(mod)
            else:
                missing.append(mod)

    print(f"✅ موجود ({len(existing)}): {existing}")
    print(f"❌ گم‌شده ({len(missing)}): {missing}\n")

    if not missing:
        print("🎉 همه ماژول‌های ارجاع‌داده‌شده موجودن. مشکلی نیست.")
        return

    print("=" * 60)
    for mod in missing:
        fpath = os.path.join(API_DIR, f"{mod}.py")
        print(f"⚠️ در حال بازسازی: {fpath}")
        with open(fpath, "w", encoding="utf-8") as f:
            f.write(STUB_TEMPLATE)
        print(f"   ✅ ساخته شد (stub ساده — re-export از app.api.chat)")

    print("\n" + "=" * 60)
    print(f"✅ {len(missing)} فایل بازسازی شد.")
    print("⚠️ توجه: این‌ها stubهای موقتی‌ان (فقط router چت رو re-export می‌کنن).")
    print("   اگه منطق واقعی‌ای باید داشته باشن، باید جداگونه پیاده‌سازی بشن.")


if __name__ == "__main__":
    main()
