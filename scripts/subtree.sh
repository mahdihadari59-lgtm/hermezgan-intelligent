#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════
# HDP Subtree Helper
# Add/update MLOps as git subtree
# ═══════════════════════════════════════════════════════════════

set -euo pipefail

PROJECT_ROOT="${1:-$(pwd)}"
MLOPS_REPO="${2:-}"
PREFIX="${3:-mlops_platform}"

cd "$PROJECT_ROOT"

if [[ -z "$MLOPS_REPO" ]]; then
    echo "Usage: $0 <project-path> <mlops-repo-path> [prefix]"
    echo "Example: $0 ~/hdp ~/mlops_platform_v2"
    exit 1
fi

echo "🌳 Subtree Helper"
echo "================="
echo "Project: $PROJECT_ROOT"
echo "MLOps:   $MLOPS_REPO"
echo "Prefix:  $PREFIX"
echo ""

# Check repos
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "❌ Not a git repository: $PROJECT_ROOT"
    exit 1
fi

if [[ ! -d "$MLOPS_REPO/.git" ]]; then
    echo "❌ Not a git repository: $MLOPS_REPO"
    exit 1
fi

# Check if already exists
if [[ -d "$PREFIX" ]]; then
    echo "⚠️  $PREFIX/ already exists!"
    echo "Options:"
    echo "  1) Update (pull)"
    echo "  2) Replace (remove + add)"
    echo "  3) Abort"
    echo -n "Choose [1/2/3]: "
    read -r choice

    case "$choice" in
        1)
            echo "🔄 Updating subtree..."
            git subtree pull --prefix="$PREFIX" "$MLOPS_REPO" main --squash
            echo "✅ Subtree updated!"
            ;;
        2)
            echo "🗑️  Removing old subtree..."
            git rm -rf "$PREFIX/"
            git commit -m "chore: remove old $PREFIX for re-integration" || true

            echo "🌳 Adding new subtree..."
            git subtree add --prefix="$PREFIX" --message="feat(mlops): integrate MLOps platform" "$MLOPS_REPO" main
            echo "✅ Subtree replaced!"
            ;;
        *)
            echo "❌ Aborted"
            exit 1
            ;;
    esac
else
    echo "🌳 Adding subtree..."
    git subtree add --prefix="$PREFIX" --message="feat(mlops): integrate MLOps platform v2.0" "$MLOPS_REPO" main
    echo "✅ Subtree added!"
fi

# Create integration docs
cat > "$PREFIX/INTEGRATION.md" << EOF
# MLOps Integration

**Date:** $(date)
**Source:** $MLOPS_REPO

## Commands

\`\`\`bash
# Update from upstream
git subtree pull --prefix=$PREFIX $MLOPS_REPO main --squash

# Remove
git rm -rf $PREFIX/
git commit -m "chore: remove MLOps integration"
\`\`\`
EOF

git add "$PREFIX/INTEGRATION.md"
git commit -m "docs: add MLOps integration docs" || true

echo ""
echo "✅ Subtree integration complete!"
echo ""
echo "Structure:"
find "$PREFIX" -maxdepth 2 -type f | head -15
echo ""
echo "Next: cd $PREFIX && docker-compose up --build -d"
