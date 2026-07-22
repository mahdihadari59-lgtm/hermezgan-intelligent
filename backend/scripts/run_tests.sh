#!/bin/bash
# backend/scripts/run_tests.sh

echo "================================================"
echo "🧪 اجرای تست‌های پروژه هرمزگان هوشمند"
echo "================================================"

source venv/bin/activate

pip install pytest pytest-cov pytest-asyncio pytest-xdist

echo ""
echo "📊 اجرای تست‌های Backend..."
cd backend

pytest tests/ -v \
    --cov=app \
    --cov-report=html \
    --cov-report=term \
    --maxfail=5 \
    -n auto

EXIT_CODE=$?

echo ""
echo "================================================"
if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ همه تست‌ها با موفقیت اجرا شدند!"
    echo "📊 گزارش Coverage: backend/htmlcov/index.html"
else
    echo "❌ برخی تست‌ها با خطا مواجه شدند!"
fi
echo "================================================"

exit $EXIT_CODE
