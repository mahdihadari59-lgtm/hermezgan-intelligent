#!/bin/bash
# filename: check_missing_files.sh

echo "========================================="
echo "🔍  بررسی فایل‌های موجود و کم‌بودها"
echo "========================================="

BASE_DIR="."
REPORT_FILE="missing_files_report.txt"

# ============================================
# 1️⃣  اطلاعات کلی
# ============================================
{
  echo "========================================="
  echo "📊  گزارش بررسی فایل‌های پروژه"
  echo "========================================="
  echo ""
  echo "تاریخ: $(date)"
  echo "مسیر: $(pwd)"
  echo ""
} > "$REPORT_FILE"

# ============================================
# 2️⃣  بررسی Frontend
# ============================================
{
  echo "========================================="
  echo "📁  بررسی Frontend"
  echo "========================================="
  echo ""
} >> "$REPORT_FILE"

# Frontend - پوشه‌های اصلی
{
  echo "📂 پوشه‌های موجود در frontend/src/:"
  ls -la frontend/src/ 2>/dev/null | grep "^d" | awk '{print "  📁 " $9}' || echo "  ❌ پوشه frontend/src وجود ندارد!"
  echo ""
} >> "$REPORT_FILE"

# Frontend - فایل‌های اصلی
{
  echo "📄 فایل‌های اصلی Frontend:"
  
  # فایل‌های ضروری
  files=(
    "frontend/src/App.js"
    "frontend/src/index.js"
    "frontend/src/App.css"
    "frontend/src/index.css"
    "frontend/package.json"
  )
  
  for f in "${files[@]}"; do
    if [ -f "$f" ]; then
      size=$(du -sh "$f" 2>/dev/null | awk '{print $1}')
      echo "  ✅ $f ($size)"
    else
      echo "  ❌ $f (وجود ندارد!)"
    fi
  done
  echo ""
} >> "$REPORT_FILE"

# Frontend - ماژول‌ها
{
  echo "📦 ماژول‌های Frontend:"
  
  modules=(
    "frontend/src/components"
    "frontend/src/features"
    "frontend/src/pages"
    "frontend/src/services"
    "frontend/src/hooks"
    "frontend/src/utils"
    "frontend/src/store"
    "frontend/src/hdp-copilot"
  )
  
  for m in "${modules[@]}"; do
    if [ -d "$m" ]; then
      count=$(find "$m" -type f \( -name "*.js" -o -name "*.jsx" \) 2>/dev/null | wc -l)
      size=$(du -sh "$m" 2>/dev/null | awk '{print $1}')
      echo "  ✅ $m → $count فایل | $size"
    else
      echo "  ❌ $m (وجود ندارد!)"
    fi
  done
  echo ""
} >> "$REPORT_FILE"

# ============================================
# 3️⃣  بررسی Backend
# ============================================
{
  echo "========================================="
  echo "📁  بررسی Backend"
  echo "========================================="
  echo ""
} >> "$REPORT_FILE"

# Backend - آیا وجود دارد؟
if [ -d "backend" ]; then
  {
    echo "✅ پوشه backend وجود دارد!"
    echo ""
    echo "📂 ساختار backend:"
    find backend -type d 2>/dev/null | head -20 | sed 's|backend/||' | while read dir; do
      if [ -n "$dir" ]; then
        count=$(find "backend/$dir" -type f -name "*.py" 2>/dev/null | wc -l)
        echo "  📁 $dir/ → $count فایل"
      fi
    done
    echo ""
  } >> "$REPORT_FILE"
  
  # Backend - فایل‌های اصلی
  {
    echo "📄 فایل‌های اصلی Backend:"
    
    files=(
      "backend/app/main.py"
      "backend/app/__init__.py"
      "backend/requirements.txt"
      "backend/.env"
      "backend/app/core/config.py"
      "backend/app/core/database.py"
      "backend/app/core/security.py"
      "backend/app/models/__init__.py"
      "backend/app/schemas/__init__.py"
      "backend/app/api/__init__.py"
    )
    
    for f in "${files[@]}"; do
      if [ -f "$f" ]; then
        size=$(du -sh "$f" 2>/dev/null | awk '{print $1}')
        lines=$(wc -l < "$f" 2>/dev/null)
        echo "  ✅ $f ($size, $lines خط)"
      else
        echo "  ❌ $f (وجود ندارد!)"
      fi
    done
    echo ""
  } >> "$REPORT_FILE"
  
  # Backend - مدل‌ها
  {
    echo "📊 مدل‌های Backend:"
    
    models=(
      "backend/app/models/service.py"
      "backend/app/models/hotspot.py"
      "backend/app/models/camera.py"
      "backend/app/models/user.py"
    )
    
    for m in "${models[@]}"; do
      if [ -f "$m" ]; then
        lines=$(wc -l < "$m" 2>/dev/null)
        echo "  ✅ $m ($lines خط)"
      else
        echo "  ❌ $m (وجود ندارد!)"
      fi
    done
    echo ""
  } >> "$REPORT_FILE"
  
  # Backend - سرویس‌ها
  {
    echo "🔧 سرویس‌های Backend:"
    
    services=(
      "backend/app/services/map_service.py"
      "backend/app/services/hotspot_service.py"
      "backend/app/services/camera_service.py"
    )
    
    for s in "${services[@]}"; do
      if [ -f "$s" ]; then
        lines=$(wc -l < "$s" 2>/dev/null)
        echo "  ✅ $s ($lines خط)"
      else
        echo "  ❌ $s (وجود ندارد!)"
      fi
    done
    echo ""
  } >> "$REPORT_FILE"
  
  # Backend - API Routes
  {
    echo "🛣️  API Routes:"
    
    routes=(
      "backend/app/api/routes/services.py"
      "backend/app/api/routes/hotspots.py"
      "backend/app/api/routes/cameras.py"
      "backend/app/api/routes/analytics.py"
    )
    
    for r in "${routes[@]}"; do
      if [ -f "$r" ]; then
        lines=$(wc -l < "$r" 2>/dev/null)
        echo "  ✅ $r ($lines خط)"
      else
        echo "  ❌ $r (وجود ندارد!)"
      fi
    done
    echo ""
  } >> "$REPORT_FILE"

else
  {
    echo "❌ پوشه backend وجود ندارد!"
    echo ""
    echo "💡 پیشنهاد: آیا نیاز به Backend دارید؟"
    echo "   اگر نیاز دارید، باید ساختار زیر را ایجاد کنید:"
    echo ""
    echo "   backend/"
    echo "   ├── app/"
    echo "   │   ├── __init__.py"
    echo "   │   ├── main.py"
    echo "   │   ├── core/"
    echo "   │   │   ├── config.py"
    echo "   │   │   ├── database.py"
    echo "   │   │   └── security.py"
    echo "   │   ├── models/"
    echo "   │   │   ├── service.py"
    echo "   │   │   ├── hotspot.py"
    echo "   │   │   ├── camera.py"
    echo "   │   │   └── user.py"
    echo "   │   ├── schemas/"
    echo "   │   │   ├── service.py"
    echo "   │   │   ├── hotspot.py"
    echo "   │   │   └── camera.py"
    echo "   │   ├── api/"
    echo "   │   │   ├── routes/"
    echo "   │   │   │   ├── services.py"
    echo "   │   │   │   ├── hotspots.py"
    echo "   │   │   │   ├── cameras.py"
    echo "   │   │   │   └── analytics.py"
    echo "   │   │   └── dependencies/"
    echo "   │   └── services/"
    echo "   │       ├── map_service.py"
    echo "   │       ├── hotspot_service.py"
    echo "   │       └── camera_service.py"
    echo "   ├── tests/"
    echo "   ├── requirements.txt"
    echo "   └── .env"
    echo ""
  } >> "$REPORT_FILE"
fi

# ============================================
# 4️⃣  فایل‌های مشترک بین Frontend و Backend
# ============================================
{
  echo ""
  echo "========================================="
  echo "🔗  فایل‌های مشترک بین Frontend و Backend"
  echo "========================================="
  echo ""
  
  echo "📄 سرویس‌های Frontend:"
  ls -la frontend/src/services/ 2>/dev/null | grep "\.js$" | awk '{print "  📄 " $9}' || echo "  ❌ پوشه services وجود ندارد!"
  
  echo ""
  echo "📄 سرویس‌های Backend (در صورت وجود):"
  if [ -d "backend/app/services" ]; then
    ls -la backend/app/services/ 2>/dev/null | grep "\.py$" | awk '{print "  📄 " $9}'
  else
    echo "  ❌ پوشه backend/app/services وجود ندارد!"
  fi
  echo ""
} >> "$REPORT_FILE"

# ============================================
# 5️⃣  فایل‌های گم شده در پروژه
# ============================================
{
  echo ""
  echo "========================================="
  echo "🔍  خلاصه فایل‌های گم شده"
  echo "========================================="
  echo ""
  
  missing_count=0
  
  # Frontend فایل‌های اصلی
  for f in "frontend/src/App.js" "frontend/src/index.js" "frontend/package.json"; do
    if [ ! -f "$f" ]; then
      echo "  ❌ $f"
      ((missing_count++))
    fi
  done
  
  # Backend فایل‌های اصلی (اگر backend وجود داشته باشد)
  if [ -d "backend" ]; then
    for f in "backend/app/main.py" "backend/requirements.txt" "backend/.env" "backend/app/core/config.py" "backend/app/core/database.py"; do
      if [ ! -f "$f" ]; then
        echo "  ❌ $f"
        ((missing_count++))
      fi
    done
  fi
  
  if [ $missing_count -eq 0 ]; then
    echo "  ✅ همه فایل‌های اصلی وجود دارند!"
  else
    echo ""
    echo "  📊 تعداد کل فایل‌های گم شده: $missing_count"
  fi
  echo ""
} >> "$REPORT_FILE"

# ============================================
# 6️⃣  نمایش نتیجه
# ============================================
echo ""
echo "========================================="
echo "✅  بررسی کامل شد!"
echo "========================================="
echo ""
echo "📄 فایل گزارش: $REPORT_FILE"
echo "💾 حجم فایل: $(du -h $REPORT_FILE 2>/dev/null | awk '{print $1}')"
echo ""
echo "🔍 برای مشاهده گزارش:"
echo "  cat $REPORT_FILE"
echo ""
echo "📊 خلاصه:"
echo "  • Frontend: $(find frontend/src -type f \( -name "*.js" -o -name "*.jsx" \) 2>/dev/null | wc -l) فایل"
if [ -d "backend" ]; then
  echo "  • Backend: $(find backend -type f -name "*.py" 2>/dev/null | wc -l) فایل"
else
  echo "  • Backend: ❌ وجود ندارد"
fi
echo "========================================="
