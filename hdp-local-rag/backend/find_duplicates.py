#!/usr/bin/env python3
# ============================================================
# find_duplicates.py - شناسایی فایل‌های تکراری/همسان در پروژه
# ============================================================
"""
استفاده:
    python3 find_duplicates.py [مسیر ریشه پروژه] [--ext .py,.js,.json] [--near]

مثال:
    python3 find_duplicates.py .
    python3 find_duplicates.py . --ext .py
    python3 find_duplicates.py . --near     # فایل‌های "شبیه" (نه فقط دقیقاً یکسان)
"""
import sys
import os
import hashlib
import argparse
from collections import defaultdict

DEFAULT_IGNORE_DIRS = {
    ".git", "__pycache__", "node_modules", ".venv", "venv",
    "dist", "build", ".pytest_cache", ".mypy_cache", "outputs"
}


def sha256_of_file(path, block_size=65536):
    h = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(block_size), b""):
                h.update(chunk)
        return h.hexdigest()
    except (IOError, OSError):
        return None


def normalized_hash_of_file(path):
    """هش بعد از حذف فضای خالی و کامنت‌های خطی برای شناسایی فایل‌های 'تقریبا یکسان'"""
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            lines = []
            for line in f:
                stripped = line.strip()
                if not stripped:
                    continue
                lines.append(stripped)
            normalized = "\n".join(lines)
        return hashlib.sha256(normalized.encode("utf-8")).hexdigest()
    except (IOError, OSError):
        return None


def find_files(root, extensions=None, ignore_dirs=None):
    ignore_dirs = ignore_dirs or DEFAULT_IGNORE_DIRS
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in ignore_dirs]
        for fname in filenames:
            if extensions and not any(fname.endswith(ext) for ext in extensions):
                continue
            yield os.path.join(dirpath, fname)


def human_size(num_bytes):
    for unit in ["B", "KB", "MB", "GB"]:
        if num_bytes < 1024:
            return f"{num_bytes:.1f}{unit}"
        num_bytes /= 1024
    return f"{num_bytes:.1f}TB"


def main():
    parser = argparse.ArgumentParser(description="شناسایی فایل‌های تکراری در پروژه")
    parser.add_argument("root", nargs="?", default=".", help="مسیر ریشه پروژه")
    parser.add_argument("--ext", default=None,
                         help="فیلتر پسوند، مثلا: .py,.js (پیش‌فرض: همه فایل‌ها)")
    parser.add_argument("--near", action="store_true",
                         help="علاوه بر فایل‌های دقیقاً یکسان، فایل‌های تقریباً یکسان را هم پیدا کن")
    parser.add_argument("--min-size", type=int, default=1,
                         help="حداقل حجم فایل به بایت برای بررسی (پیش‌فرض 1، فایل خالی رد می‌شود)")
    args = parser.parse_args()

    extensions = None
    if args.ext:
        extensions = [e if e.startswith(".") else f".{e}" for e in args.ext.split(",")]

    root = os.path.abspath(args.root)
    print(f"🔍 در حال اسکن: {root}")
    if extensions:
        print(f"   پسوندها: {', '.join(extensions)}")

    exact_hashes = defaultdict(list)
    near_hashes = defaultdict(list)
    total_files = 0
    skipped = 0

    for path in find_files(root, extensions):
        try:
            size = os.path.getsize(path)
        except OSError:
            continue
        if size < args.min_size:
            skipped += 1
            continue

        total_files += 1
        h = sha256_of_file(path)
        if h:
            exact_hashes[h].append(path)

        if args.near:
            nh = normalized_hash_of_file(path)
            if nh:
                near_hashes[nh].append(path)

    print(f"📁 تعداد فایل بررسی‌شده: {total_files} (رد شده به دلیل حجم: {skipped})\n")

    # --- فایل‌های دقیقاً یکسان ---
    exact_dupes = {h: paths for h, paths in exact_hashes.items() if len(paths) > 1}
    if exact_dupes:
        print("=" * 60)
        print(f"❗ فایل‌های دقیقاً یکسان (byte-for-byte): {len(exact_dupes)} گروه")
        print("=" * 60)
        wasted = 0
        for h, paths in sorted(exact_dupes.items(), key=lambda x: -os.path.getsize(x[1][0])):
            size = os.path.getsize(paths[0])
            wasted += size * (len(paths) - 1)
            print(f"\n[{human_size(size)} × {len(paths)} نسخه] hash={h[:10]}...")
            for p in paths:
                rel = os.path.relpath(p, root)
                print(f"   - {rel}")
        print(f"\n💾 فضای هدررفته تقریبی: {human_size(wasted)}")
    else:
        print("✅ هیچ فایل دقیقاً یکسانی پیدا نشد.")

    # --- فایل‌های تقریباً یکسان (فقط اگر --near) ---
    if args.near:
        near_dupes = {
            h: paths for h, paths in near_hashes.items()
            if len(paths) > 1 and set(paths) not in [set(p) for p in exact_dupes.values()]
        }
        # حذف گروه‌هایی که دقیقاً همون گروه exact هستن
        exact_groups = {frozenset(p) for p in exact_dupes.values()}
        near_dupes = {h: p for h, p in near_dupes.items() if frozenset(p) not in exact_groups}

        if near_dupes:
            print("\n" + "=" * 60)
            print(f"⚠️  فایل‌های تقریباً یکسان (بدون احتساب فضای خالی/فرمت): {len(near_dupes)} گروه")
            print("=" * 60)
            for h, paths in near_dupes.items():
                print(f"\n[hash={h[:10]}...]")
                for p in paths:
                    rel = os.path.relpath(p, root)
                    print(f"   - {rel}")
        else:
            print("\n✅ هیچ فایل تقریباً یکسانی (فراتر از موارد دقیقاً یکسان) پیدا نشد.")

    if not exact_dupes and not (args.near and near_hashes):
        print("\n🎉 پروژه از این نظر تمیزه.")


if __name__ == "__main__":
    main()
