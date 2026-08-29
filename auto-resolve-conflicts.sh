#!/bin/bash
# HDP Auto Conflict Resolver for PR #22
# Resolves conflicts by keeping "theirs" (PR branch) for most files

set -e

echo "═══════════════════════════════════════════════════════"
echo "  HDP Auto Conflict Resolver"
echo "  PR #22: fix/complete-integration-v2"
echo "═══════════════════════════════════════════════════════"
echo ""

cd ~/hermezgan-intelligent

# Check if we're in a merge state
if ! git rev-parse -q --verify MERGE_HEAD > /dev/null 2>&1; then
    echo "❌ Not in a merge state. Run merge first:"
    echo "   git merge --no-commit --no-ff origin/fix/complete-integration-v2"
    exit 1
fi

echo "🔍 Current merge state detected"
echo ""

# Strategy: For each conflict, choose THEIRS (PR branch) or OURS (main)
# Backend files → keep THEIRS (PR has newer code)
# Frontend backup files → keep OURS (main has restructured code)

echo "⚙️ Resolving conflicts..."
echo ""

# === BACKEND FILES: Keep THEIRS (PR branch) ===
echo "📁 Backend files → keeping PR version (theirs)..."
for file in     "backend/app/api/chat.py"     "backend/app/api/copilot.py"     "backend/app/api/v1/endpoints/chat.py"     "backend/app/api/v1/endpoints/locations.py"     "backend/app/api/v1/routers.py"     "backend/app/api/v1/traffic.py"     "backend/app/main.py"     "backend/app/providers/bandari_provider.py"     "backend/requirements.txt"; do

    if [ -f "$file" ]; then
        git checkout --theirs "$file" 2>/dev/null && echo "  ✅ $file (theirs)" || echo "  ⚠️  $file (skipped)"
        git add "$file" 2>/dev/null || true
    fi
done

# === BANDARI ENGINE: Keep THEIRS ===
echo ""
echo "📁 Bandari Engine → keeping PR version..."
git checkout --theirs "bandari-engine-2026/bandari-engine/api/routes.js" 2>/dev/null && echo "  ✅ routes.js" || echo "  ⚠️  routes.js"
git add "bandari-engine-2026/bandari-engine/api/routes.js" 2>/dev/null || true

# === DOCS: Keep THEIRS ===
echo ""
echo "📁 Documentation → keeping PR version..."
git checkout --theirs "docs/CHANGELOG.md" 2>/dev/null && echo "  ✅ CHANGELOG.md" || echo "  ⚠️  CHANGELOG"
git add "docs/CHANGELOG.md" 2>/dev/null || true

# === FRONTEND: Keep THEIRS for package.json, useChat.js ===
echo ""
echo "📁 Frontend → keeping PR version..."
git checkout --theirs "frontend/package.json" 2>/dev/null && echo "  ✅ package.json" || echo "  ⚠️  package.json"
git add "frontend/package.json" 2>/dev/null || true

git checkout --theirs "frontend/src/hooks/useChat.js" 2>/dev/null && echo "  ✅ useChat.js" || echo "  ⚠️  useChat.js"
git add "frontend/src/hooks/useChat.js" 2>/dev/null || true

# === .gitignore: Merge manually (keep both) ===
echo ""
echo "📁 .gitignore → merging..."
cat > .gitignore << 'GITIGNORE'
# Dependencies
node_modules/
__pycache__/
*.pyc
.env
.venv/

# Build outputs
build/
dist/
*.egg-info/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# Database
*.db
*.sqlite
*.sqlite3

# Audio
*.wav
*.mp3
*.ogg

# Backup files
*.bak*
*.backup*
*.old*
*.mangled*

# Version backups
.version-backups/
.backup-*/

# Archive
_archive/
backup_imports/
frontend_OLD_*/
GITIGNORE
git add .gitignore && echo "  ✅ .gitignore merged"

# === FRONTEND BACKUP FILES: Keep OURS (skip them) ===
echo ""
echo "📁 Frontend backup files → skipping (keeping main structure)..."
for file in $(git status --short | grep "frontend_OLD_redux_backup" | awk '{print $2}'); do
    git rm -f "$file" 2>/dev/null && echo "  🗑️  Removed: $file" || true
done

# === Check remaining conflicts ===
echo ""
echo "═══════════════════════════════════════════════════════"
echo "🔍 Checking remaining conflicts..."
echo "═══════════════════════════════════════════════════════"

CONFLICTS=$(git diff --name-only --diff-filter=U 2>/dev/null || true)

if [ -z "$CONFLICTS" ]; then
    echo ""
    echo "✅ ALL CONFLICTS RESOLVED!"
    echo ""
    echo "Next steps:"
    echo "  1. Review changes: git status"
    echo "  2. Commit: git commit -m 'merge: integrate PR #22 - complete integration v2'"
    echo "  3. Push: git push origin main"
    echo ""
else
    echo ""
    echo "⚠️  Remaining conflicts (need manual review):"
    echo "$CONFLICTS" | while read f; do
        echo "  - $f"
    done
    echo ""
    echo "To resolve manually:"
    echo "  git checkout --theirs <file>   # keep PR version"
    echo "  git checkout --ours <file>     # keep main version"
    echo "  git add <file>"
fi

echo ""
echo "📊 Final status:"
git status --short | head -20
echo ""
