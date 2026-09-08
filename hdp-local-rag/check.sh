#!/bin/bash

echo "========================================="
echo "📊  تحلیل ساختار پروژه"
echo "========================================="

BASE_DIR="frontend/src"

# 1. پوشه‌های سطح اول
echo ""
echo "📂 پوشه‌های اصلی:"
ls -d $BASE_DIR/*/ 2>/dev/null | while read dir; do
  count=$(find "$dir" -type f \( -name "*.js" -o -name "*.jsx" \) 2>/dev/null | wc -l)
  echo "  📁 $(basename "$dir") - $count فایل"
done

# 2. فایل‌های تکراری
echo ""
echo "🔍 فایل‌های تکراری:"
find $BASE_DIR -type f -name "*.js" -o -name "*.jsx" 2>/dev/null | \
  sed 's|.*/||' | sort | uniq -d | while read f; do
  echo "  📄 $f"
  find $BASE_DIR -name "$f" 2>/dev/null | while read path; do
    lines=$(wc -l < "$path" 2>/dev/null)
    echo "     → $path ($lines خط)"
  done
  echo ""
done

# 3. اسلایس‌ها
echo ""
echo "🎯 اسلایس‌های Redux:"
find $BASE_DIR -type f -name "*Slice.js" 2>/dev/null | while read file; do
  lines=$(wc -l < "$file" 2>/dev/null)
  echo "  📄 $(basename "$file") - $lines خط"
  echo "     📍 $file"
done

# 4. آمار کلی
echo ""
echo "📊 آمار کلی:"
total_files=$(find $BASE_DIR -type f \( -name "*.js" -o -name "*.jsx" -o -name "*.css" \) 2>/dev/null | wc -l)
total_lines=$(find $BASE_DIR -type f \( -name "*.js" -o -name "*.jsx" \) -exec wc -l {} \; 2>/dev/null | awk '{sum+=$1} END {print sum}')
echo "  کل فایل‌ها: $total_files"
echo "  کل خطوط کد: $total_lines"

echo ""
echo "✅ انجام شد!"
