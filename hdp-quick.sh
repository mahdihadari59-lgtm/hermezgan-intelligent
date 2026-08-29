#!/bin/bash
set -e
PROJECT="${1:-$HOME/hermezgan-intelligent}"
MLOPS="${2:-$HOME/mlops_platform_v2}"
echo "═══════════════════════════════════════"
echo "  HDP Quick Integration"
echo "═══════════════════════════════════════"
cd "$PROJECT"
echo "🔍 Branches:"
git branch -vv
echo ""
echo "💾 Backup..."
TS=$(date +%Y%m%d_%H%M%S)
git tag "bak-develop-$TS" develop-v1.4 2>/dev/null || true
git tag "bak-main-$TS" main 2>/dev/null || true
echo "  ✅ Tags created"
echo ""
echo "🌳 Subtree..."
if [ -d "mlops_platform" ]; then
    echo -n "  Replace? [y/N]: "
    read ans
    [ "$ans" = "y" ] && git rm -rf mlops_platform/ 2>/dev/null && git commit -m "chore: remove old" 2>/dev/null || true
fi
git subtree add --prefix=mlops_platform --message="feat(mlops): integrate" "$MLOPS" main
echo ""
echo "✅ Done!"
ls mlops_platform/
