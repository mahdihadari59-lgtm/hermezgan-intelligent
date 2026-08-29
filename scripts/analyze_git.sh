#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════
# HDP Git History Analyzer
# تحلیل کامل تاریخچه Git قبل از تصمیم‌گیری
# ═══════════════════════════════════════════════════════════════

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="${1:-$(cd "$SCRIPT_DIR/.." && pwd)}"
OUTPUT_DIR="$SCRIPT_DIR/analysis_$(date +%Y%m%d_%H%M%S)"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m'

mkdir -p "$OUTPUT_DIR"

echo -e "${CYAN}"
cat << 'BANNER'
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║           HDP Git History Analyzer                             ║
    ║           تحلیل تاریخچه Git قبل از تصمیم‌گیری              ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
BANNER
echo -e "${NC}"

echo -e "${BLUE}Project:${NC} $PROJECT_ROOT"
echo -e "${BLUE}Output:${NC}  $OUTPUT_DIR"
echo ""

# ═══════════════════════════════════════════════════════════════
# 1. Branch Analysis
# ═══════════════════════════════════════════════════════════════

echo -e "${MAGENTA}═══ 1. Branch Analysis ═══${NC}"

cd "$PROJECT_ROOT"

echo -e "\n${YELLOW}Local Branches:${NC}"
git branch -vv > "$OUTPUT_DIR/branches_local.txt"
cat "$OUTPUT_DIR/branches_local.txt"

echo -e "\n${YELLOW}Remote Branches:${NC}"
git branch -r -vv > "$OUTPUT_DIR/branches_remote.txt"
cat "$OUTPUT_DIR/branches_remote.txt"

echo -e "\n${YELLOW}Branch Relationships:${NC}"
for branch in $(git branch --format='%(refname:short)'); do
    echo "---"
    echo "Branch: $branch"
    echo "  Last commit: $(git log -1 --format='%h %s (%cr)' $branch)"
    echo "  Author: $(git log -1 --format='%an <%ae>' $branch)"
    echo "  Commits ahead of main: $(git rev-list --count main..$branch 2>/dev/null || echo 'N/A (not based on main)')"
    echo "  Commits behind main: $(git rev-list --count $branch..main 2>/dev/null || echo 'N/A')"
done > "$OUTPUT_DIR/branch_details.txt"
cat "$OUTPUT_DIR/branch_details.txt"

# ═══════════════════════════════════════════════════════════════
# 2. Commit History Analysis
# ═══════════════════════════════════════════════════════════════

echo -e "\n${MAGENTA}═══ 2. Commit History Analysis ═══${NC}"

echo -e "\n${YELLOW}Recent commits on each branch:${NC}"
for branch in $(git branch --format='%(refname:short)'); do
    echo ""
    echo "━━━ $branch ━━━"
    git log --oneline --graph -15 "$branch" 2>/dev/null || echo "  (no commits)"
done > "$OUTPUT_DIR/commit_history.txt"
cat "$OUTPUT_DIR/commit_history.txt"

echo -e "\n${YELLOW}Commit statistics (last 30 days):${NC}"
git log --format='%h|%an|%ae|%ad|%s' --date=short --since='30 days ago' --all > "$OUTPUT_DIR/commits_30days.csv"
echo "Total commits: $(wc -l < "$OUTPUT_DIR/commits_30days.csv")"
echo ""
echo "Top contributors:"
cut -d'|' -f2 "$OUTPUT_DIR/commits_30days.csv" | sort | uniq -c | sort -rn | head -10

echo -e "\n${YELLOW}Commit message patterns:${NC}"
git log --format='%s' --all | grep -oE '^(feat|fix|chore|docs|test|refactor|style|perf|ci|build|revert)(\([^)]*\))?:' | sort | uniq -c | sort -rn > "$OUTPUT_DIR/commit_types.txt" || true
cat "$OUTPUT_DIR/commit_types.txt"

# ═══════════════════════════════════════════════════════════════
# 3. Merge & Conflict Analysis
# ═══════════════════════════════════════════════════════════════

echo -e "\n${MAGENTA}═══ 3. Merge & Conflict Analysis ═══${NC}"

echo -e "\n${YELLOW}Merge commits:${NC}"
git log --all --merges --oneline > "$OUTPUT_DIR/merge_commits.txt"
if [[ -s "$OUTPUT_DIR/merge_commits.txt" ]]; then
    cat "$OUTPUT_DIR/merge_commits.txt"
    echo ""
    echo "Total merge commits: $(wc -l < "$OUTPUT_DIR/merge_commits.txt")"
else
    echo "  (no merge commits found)"
fi

echo -e "\n${YELLOW}Potential conflict areas (files modified in multiple branches):${NC}"
# Find files modified in multiple active branches
for branch in $(git branch --format='%(refname:short)' | grep -v '^main$'); do
    echo "--- $branch vs main ---"
    git diff --name-only main.."$branch" 2>/dev/null || echo "  (no diff)"
done > "$OUTPUT_DIR/branch_differences.txt"

# Find overlapping files
python3 << 'PYEOF'
import os
from collections import defaultdict

output_dir = os.environ.get('OUTPUT_DIR', '.')
branch_files = defaultdict(list)

try:
    with open(f"{output_dir}/branch_differences.txt", 'r') as f:
        current_branch = None
        for line in f:
            line = line.strip()
            if line.startswith('---') and line.endswith('---'):
                current_branch = line.replace('--- ', '').replace(' ---', '')
            elif line and not line.startswith('(') and current_branch:
                branch_files[line].append(current_branch)

    print("Files modified in multiple branches (potential conflicts):")
    print("=" * 60)
    conflicts_found = False
    for file, branches in sorted(branch_files.items(), key=lambda x: -len(x[1])):
        if len(branches) > 1:
            conflicts_found = True
            print(f"⚠️  {file}")
            print(f"   Branches: {', '.join(branches)}")

    if not conflicts_found:
        print("✅ No overlapping file modifications detected")
except Exception as e:
    print(f"Error analyzing conflicts: {e}")
PYEOF

# ═══════════════════════════════════════════════════════════════
# 4. File Lifecycle Analysis
# ═══════════════════════════════════════════════════════════════

echo -e "\n${MAGENTA}═══ 4. File Lifecycle Analysis ═══${NC}"

echo -e "\n${YELLOW}Most frequently modified files (top 20):${NC}"
git log --all --format='' --name-only | sort | uniq -c | sort -rn | head -20 > "$OUTPUT_DIR/hot_files.txt"
cat "$OUTPUT_DIR/hot_files.txt"

echo -e "\n${YELLOW}Large files in history (potential LFS candidates):${NC}"
git rev-list --objects --all | git cat-file --batch-check='%(objecttype) %(objectname) %(objectsize) %(rest)' | awk '$1 == "blob" && $3 > 1000000 {print $3, $4}' | sort -rn | head -20 > "$OUTPUT_DIR/large_files.txt" || true
if [[ -s "$OUTPUT_DIR/large_files.txt" ]]; then
    cat "$OUTPUT_DIR/large_files.txt"
else
    echo "  (no large files > 1MB found)"
fi

echo -e "\n${YELLOW}Deleted files that might need recovery:${NC}"
git log --all --diff-filter=D --summary | grep 'delete mode' | awk '{print $4}' | sort | uniq -c | sort -rn | head -20 > "$OUTPUT_DIR/deleted_files.txt" || true
if [[ -s "$OUTPUT_DIR/deleted_files.txt" ]]; then
    cat "$OUTPUT_DIR/deleted_files.txt"
else
    echo "  (no recently deleted files)"
fi

# ═══════════════════════════════════════════════════════════════
# 5. Working Tree Status
# ═══════════════════════════════════════════════════════════════

echo -e "\n${MAGENTA}═══ 5. Working Tree Status ═══${NC}"

echo -e "\n${YELLOW}Current status:${NC}"
git status > "$OUTPUT_DIR/git_status.txt"
cat "$OUTPUT_DIR/git_status.txt"

echo -e "\n${YELLOW}Untracked files by type:${NC}"
git status --short | grep '^??' | awk '{print $2}' | while read file; do
    if [[ -f "$file" ]]; then
        size=$(du -h "$file" 2>/dev/null | cut -f1)
        echo "$size  $file"
    fi
done | sort -rh > "$OUTPUT_DIR/untracked_files.txt"
cat "$OUTPUT_DIR/untracked_files.txt"

echo -e "\n${YELLOW}Modified files (not staged):${NC}"
git diff --name-only > "$OUTPUT_DIR/modified_unstaged.txt"
if [[ -s "$OUTPUT_DIR/modified_unstaged.txt" ]]; then
    cat "$OUTPUT_DIR/modified_unstaged.txt"
else
    echo "  (no modified unstaged files)"
fi

echo -e "\n${YELLOW}Staged files:${NC}"
git diff --cached --name-only > "$OUTPUT_DIR/modified_staged.txt"
if [[ -s "$OUTPUT_DIR/modified_staged.txt" ]]; then
    cat "$OUTPUT_DIR/modified_staged.txt"
else
    echo "  (no staged files)"
fi

# ═══════════════════════════════════════════════════════════════
# 6. Tag & Release Analysis
# ═══════════════════════════════════════════════════════════════

echo -e "\n${MAGENTA}═══ 6. Tag & Release Analysis ═══${NC}"

echo -e "\n${YELLOW}Tags:${NC}"
git tag -l -n1 > "$OUTPUT_DIR/tags.txt" || true
if [[ -s "$OUTPUT_DIR/tags.txt" ]]; then
    cat "$OUTPUT_DIR/tags.txt"
else
    echo "  (no tags found)"
fi

echo -e "\n${YELLOW}Version pattern in tags:${NC}"
git tag -l | grep -E '^v?[0-9]+\.[0-9]+' | sort -V > "$OUTPUT_DIR/version_tags.txt" || true
if [[ -s "$OUTPUT_DIR/version_tags.txt" ]]; then
    cat "$OUTPUT_DIR/version_tags.txt"
else
    echo "  (no semantic version tags found)"
fi

# ═══════════════════════════════════════════════════════════════
# 7. Recommendations
# ═══════════════════════════════════════════════════════════════

echo -e "\n${MAGENTA}═══ 7. Recommendations ═══${NC}"

cat > "$OUTPUT_DIR/recommendations.md" << EOF
# HDP Git Analysis Recommendations

**Analysis Date:** $(date '+%Y-%m-%d %H:%M:%S')  
**Project:** $(basename "$PROJECT_ROOT")

## Summary

| Metric | Value |
|--------|-------|
| Total branches | $(git branch | wc -l) |
| Total commits (all time) | $(git rev-list --all --count) |
| Commits (30 days) | $(wc -l < "$OUTPUT_DIR/commits_30days.csv") |
| Merge commits | $(wc -l < "$OUTPUT_DIR/merge_commits.txt" 2>/dev/null || echo 0) |
| Untracked files | $(git status --short | grep -c '^??' || echo 0) |
| Modified files | $(git diff --name-only | wc -l) |

## Key Findings

### Branches
$(cat "$OUTPUT_DIR/branches_local.txt" | sed 's/^/- /')

### Potential Conflicts
$(python3 -c "
import os
output_dir = '$OUTPUT_DIR'
try:
    with open(f'{output_dir}/branch_differences.txt', 'r') as f:
        content = f.read()
        if content.strip():
            print(content[:500] + '...' if len(content) > 500 else content)
        else:
            print('No conflicts detected')
except:
    print('Unable to analyze conflicts')
")

## Recommended Actions

1. **Before any merge:**
   - Review branch_differences.txt for overlapping files
   - Test each branch independently
   - Create backup tags: \`git tag backup-<branch>-<date> <branch>\`

2. **Clean up:**
   - Archive or delete merged branches
   - Handle untracked files (add to .gitignore or commit)

3. **For MLOps integration:**
   - Create feature branch from develop-v1.4
   - Merge mlops_platform as subtree or submodule
   - Test integration before merging to main

## Next Steps

\`\`\`bash
# Create backup tags before any operation
git tag backup-main-$(date +%Y%m%d) main
git tag backup-develop-$(date +%Y%m%d) develop-v1.4

# Safe merge strategy
git checkout develop-v1.4
git pull origin develop-v1.4
git checkout -b feature/integrate-mlops
git merge --no-ff feature/voice-api --no-commit
git status  # Check for conflicts
\`\`\`
EOF

cat "$OUTPUT_DIR/recommendations.md"

# ═══════════════════════════════════════════════════════════════
# Final Output
# ═══════════════════════════════════════════════════════════════

echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ Analysis complete!${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════${NC}"
echo ""
echo -e "${CYAN}Output files:${NC}"
find "$OUTPUT_DIR" -type f | while read f; do
    size=$(du -h "$f" | cut -f1)
    echo "  $size  $(basename "$f")"
done
echo ""
echo -e "${YELLOW}Key files to review:${NC}"
echo "  📄 $OUTPUT_DIR/recommendations.md"
echo "  📄 $OUTPUT_DIR/branch_details.txt"
echo "  📄 $OUTPUT_DIR/branch_differences.txt"
echo "  📄 $OUTPUT_DIR/commit_history.txt"
echo ""
