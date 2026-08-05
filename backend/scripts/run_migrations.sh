#!/bin/bash
# backend/scripts/run_migrations.sh

echo "================================================"
echo "🔄 اجرای مهاجرت‌های دیتابیس"
echo "================================================"

source venv/bin/activate

cd backend

python scripts/migrate_database.py

if [ $? -eq 0 ]; then
    echo "✅ مهاجرت‌ها با موفقیت اجرا شدند"
else
    echo "❌ خطا در اجرای مهاجرت‌ها"
    exit 1
fi
