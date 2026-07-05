#!/usr/bin/env bash
# Run all tests with coverage

set -e

echo "🧪 Running Unit Tests..."
echo ""

cd backend

# Activate virtual environment if needed
if [ -d "venv" ]; then
    source venv/bin/activate
fi

echo "📊 Running tests with coverage..."
pytest tests/ -v --cov=app --cov-report=html --cov-report=term-missing

echo ""
echo "✅ Tests completed!"
echo "📁 Coverage report: htmlcov/index.html"
