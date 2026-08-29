#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════
# HDP Rebase Helper
# Safe rebase with automatic conflict detection
# ═══════════════════════════════════════════════════════════════

set -euo pipefail

PROJECT_ROOT="${1:-$(pwd)}"
BRANCH="${2:-feature/voice-api}"
TARGET="${3:-develop-v1.4}"

cd "$PROJECT_ROOT"

echo "🔄 Rebase Helper"
echo "================"
echo "Branch: $BRANCH"
echo "Target: $TARGET"
echo ""

# Check if branches exist
if ! git show-ref --verify --quiet "refs/heads/$BRANCH"; then
    echo "❌ Branch not found: $BRANCH"
    exit 1
fi

if ! git show-ref --verify --quiet "refs/heads/$TARGET"; then
    echo "❌ Target branch not found: $TARGET"
    exit 1
fi

# Create backup tag
BACKUP_TAG="backup-${BRANCH}-before-rebase-$(date +%Y%m%d_%H%M%S)"
git tag "$BACKUP_TAG" "$BRANCH"
echo "✅ Backup tag created: $BACKUP_TAG"

# Check if rebase is possible
echo ""
echo "📊 Checking rebase feasibility..."
DIVERGED=$(git merge-base "$BRANCH" "$TARGET")
echo "Common ancestor: $DIVERGED"

AHEAD=$(git rev-list --count "$TARGET".."$BRANCH")
BEHIND=$(git rev-list --count "$BRANCH".."$TARGET")

echo "Commits ahead of $TARGET: $AHEAD"
echo "Commits behind $TARGET: $BEHIND"

if [[ "$BEHIND" -eq 0 ]]; then
    echo "✅ Branch is already up-to-date with $TARGET"
    exit 0
fi

if [[ "$AHEAD" -eq 0 ]]; then
    echo "⚠️ Branch has no unique commits. Fast-forward possible."
    echo "Run: git checkout $BRANCH && git merge --ff-only $TARGET"
    exit 0
fi

# Preview conflicts
echo ""
echo "🔍 Previewing potential conflicts..."
git checkout "$BRANCH"

# Try merge without committing to preview conflicts
git merge --no-commit --no-ff "$TARGET" || true

if git diff --cached --name-only | grep -q "^"; then
    echo ""
    echo "📁 Files that would be modified:"
    git diff --cached --name-only

    CONFLICTS=$(git diff --cached --name-only --diff-filter=U 2>/dev/null | wc -l)
    if [[ "$CONFLICTS" -gt 0 ]]; then
        echo ""
        echo "⚠️ Potential conflicts in:"
        git diff --cached --name-only --diff-filter=U
    fi
fi

# Abort preview merge
git merge --abort 2>/dev/null || true

# Ask for confirmation
echo ""
echo -n "Proceed with rebase? [y/N]: "
read -r response
if [[ ! "$response" =~ ^[Yy]$ ]]; then
    echo "❌ Rebase cancelled"
    exit 1
fi

# Perform rebase
echo ""
echo "🔄 Starting rebase..."
git rebase "$TARGET" || {
    echo ""
    echo "❌ Rebase failed! Conflicts detected."
    echo ""
    echo "Resolve conflicts manually:"
    echo "  1. Edit conflicting files"
    echo "  2. git add <resolved-files>"
    echo "  3. git rebase --continue"
    echo ""
    echo "Or abort: git rebase --abort"
    echo ""
    echo "Backup tag: $BACKUP_TAG"
    exit 1
}

echo ""
echo "✅ Rebase successful!"
echo "Backup tag: $BACKUP_TAG"
echo ""
echo "Next steps:"
echo "  1. Test the branch"
echo "  2. git push --force-with-lease origin $BRANCH"
