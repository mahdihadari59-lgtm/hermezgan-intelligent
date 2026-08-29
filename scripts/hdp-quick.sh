#!/bin/bash
# HDP Quick Integration — Termux Ready
# One script: check → backup → integrate

set -e

PROJECT="${1:-$HOME/hermezgan-intelligent}"
MLOPS="${2:-$HOME/mlops_platform_v2}"

echo "═══════════════════════════════════════"
echo "  HDP Quick Integration"
echo "═══════════════════════════════════════"
echo "Project: $PROJECT"
echo "MLOPS:   $MLOPS"
echo ""

cd "$PROJECT"

# ─── CHECK ───
echo "🔍 Checking conflicts..."
git fetch origin 2>/dev/null || true

echo ""
echo "Branches:"
git branch -vv

echo ""
echo "Modified files in develop-v1.4:"
git diff --name-only main..develop-v1.4 2>/dev/null || echo "  (no diff)"

# ─── BACKUP ───
echo ""
echo "💾 Creating backup tags..."
TS=$(date +%Y%m%d_%H%M%S)
git tag "bak-develop-$TS" develop-v1.4 2>/dev/null || true
git tag "bak-main-$TS" main 2>/dev/null || true
echo "  ✅ Tags created: bak-develop-$TS, bak-main-$TS"

# ─── INTEGRATE ───
echo ""
echo "🌳 Adding MLOps subtree..."

if [ -d "mlops_platform" ]; then
    echo "  ⚠️  mlops_platform exists"
    echo -n "  Replace? [y/N]: "
    read ans
    if [ "$ans" = "y" ] || [ "$ans" = "Y" ]; then
        git rm -rf mlops_platform/ 2>/dev/null || rm -rf mlops_platform/
        git commit -m "chore: remove old mlops_platform" 2>/dev/null || true
    else
        echo "  Skipped"
        exit 0
    fi
fi

git subtree add --prefix=mlops_platform \
    --message="feat(mlops): integrate MLOps platform" \
    "$MLOPS" main

# ─── VERIFY ───
echo ""
echo "✅ Done!"
echo ""
echo "Structure:"
ls -la mlops_platform/ 2>/dev/null || echo "  (not found)"

echo ""
echo "Next:"
echo "  cd mlops_platform && docker-compose up --build -d"
echo ""
echo "Rollback if needed:"
echo "  git reset --hard bak-develop-$TS"
