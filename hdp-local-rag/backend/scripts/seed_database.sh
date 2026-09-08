#!/bin/bash
# backend/scripts/seed_database.sh

echo "================================================"
echo "🌱 پر کردن دیتابیس با داده‌های اولیه"
echo "================================================"

source venv/bin/activate

cd backend

python scripts/seed_database.py

if [ $? -eq 0 ]; then
    echo "✅ دیتابیس با موفقیت پر شد"
else
    echo "❌ خطا در پر کردن دیتابیس"
    exit 1
fi
