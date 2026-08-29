#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════
# HDP Conflict Checker
# Standalone conflict detection for any git repo
# ═══════════════════════════════════════════════════════════════

set -euo pipefail

PROJECT_ROOT="${1:-$(pwd)}"
OUTPUT="${2:-conflict_report.md}"

cd "$PROJECT_ROOT"

cat > "$OUTPUT" << 'HEADER'
# HDP Conflict Analysis Report

HEADER

echo "# HDP Conflict Analysis Report" > "$OUTPUT"
echo "" >> "$OUTPUT"
echo "**Project:** $(basename "$PROJECT_ROOT")" >> "$OUTPUT"
echo "**Date:** $(date '+%Y-%m-%d %H:%M:%S')" >> "$OUTPUT"
echo "" >> "$OUTPUT"

# Get all branches
BRANCHES=$(git branch --format='%(refname:short)' | grep -v '^HEAD$')
MAIN_BRANCH="main"

# Check if main exists, otherwise use master
if ! git show-ref --verify --quiet "refs/heads/main"; then
    MAIN_BRANCH="master"
fi

echo "## Branch Overview" >> "$OUTPUT"
echo "" >> "$OUTPUT"
echo "| Branch | Last Commit | Ahead of $MAIN_BRANCH | Behind $MAIN_BRANCH | Status |" >> "$OUTPUT"
echo "|--------|-------------|----------------------|---------------------|--------|" >> "$OUTPUT"

for branch in $BRANCHES; do
    if [[ "$branch" == "$MAIN_BRANCH" ]]; then
        continue
    fi

    last_commit=$(git log -1 --format='%h %s' "$branch" 2>/dev/null || echo "N/A")
    ahead=$(git rev-list --count "$MAIN_BRANCH".."$branch" 2>/dev/null || echo "0")
    behind=$(git rev-list --count "$branch".."$MAIN_BRANCH" 2>/dev/null || echo "0")

    if [[ "$ahead" -gt 0 && "$behind" -gt 0 ]]; then
        status="⚠️ Diverged"
    elif [[ "$ahead" -gt 0 ]]; then
        status="✅ Ahead"
    elif [[ "$behind" -gt 0 ]]; then
        status="🔴 Behind"
    else
        status="✅ Synced"
    fi

    echo "| $branch | $last_commit | $ahead | $behind | $status |" >> "$OUTPUT"
done

echo "" >> "$OUTPUT"
echo "## File Overlap Analysis" >> "$OUTPUT"
echo "" >> "$OUTPUT"

# Find overlapping files
python3 << 'PYEOF'
import subprocess
import sys
from collections import defaultdict

project_root = sys.argv[1] if len(sys.argv) > 1 else "."
main_branch = sys.argv[2] if len(sys.argv) > 2 else "main"

branches = []
result = subprocess.run(
    ["git", "-C", project_root, "branch", "--format=%(refname:short)"],
    capture_output=True, text=True
)
for line in result.stdout.strip().split('\n'):
    branch = line.strip()
    if branch and branch != main_branch and not branch.startswith('HEAD'):
        branches.append(branch)

branch_files = defaultdict(list)

for branch in branches:
    result = subprocess.run(
        ["git", "-C", project_root, "diff", "--name-only", f"{main_branch}..{branch}"],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        for line in result.stdout.strip().split('\n'):
            if line.strip():
                branch_files[line.strip()].append(branch)

conflicts = []
for file, branches in sorted(branch_files.items(), key=lambda x: -len(x[1])):
    if len(branches) > 1:
        conflicts.append((file, branches))

output_file = sys.argv[3] if len(sys.argv) > 3 else "conflict_report.md"

with open(output_file, "a") as f:
    if conflicts:
        f.write(f"⚠️ **{len(conflicts)} files modified in multiple branches**\n\n")
        f.write("| File | Branches | Risk |\n")
        f.write("|------|----------|------|\n")

        for file, branches in conflicts:
            risk = "🔴 High" if len(branches) > 2 else "🟡 Medium"
            f.write(f"| `{file}` | {', '.join(branches)} | {risk} |\n")

        f.write("\n### Detailed Conflicts\n\n")
        for file, branches in conflicts:
            f.write(f"#### `{file}`\n\n")
            f.write(f"Modified in: {', '.join(branches)}\n\n")

            # Show diff stats for each branch
            for branch in branches:
                result = subprocess.run(
                    ["git", "-C", project_root, "diff", "--stat", f"{main_branch}..{branch}", "--", file],
                    capture_output=True, text=True
                )
                if result.stdout.strip():
                    f.write(f"**{branch}:**\n")
                    f.write(f"```\n{result.stdout.strip()}\n```\n\n")
    else:
        f.write("✅ **No overlapping file modifications detected**\n\n")
        f.write("All branches modify different files. Safe to merge!\n")

print(f"Analysis complete. {len(conflicts)} conflicts found." if conflicts else "Analysis complete. No conflicts found.")
PYEOF "$PROJECT_ROOT" "$MAIN_BRANCH" "$OUTPUT"

echo "" >> "$OUTPUT"
echo "## Recommendations" >> "$OUTPUT"
echo "" >> "$OUTPUT"

if grep -q "🔴 High" "$OUTPUT" 2>/dev/null; then
    echo "🔴 **High Risk:** Multiple branches modify the same files. Manual merge review required." >> "$OUTPUT"
elif grep -q "🟡 Medium" "$OUTPUT" 2>/dev/null; then
    echo "🟡 **Medium Risk:** Some files modified in 2 branches. Review before merge." >> "$OUTPUT"
else
    echo "✅ **Low Risk:** No overlapping modifications. Safe to proceed with merge." >> "$OUTPUT"
fi

echo "" >> "$OUTPUT"
echo "## Next Steps" >> "$OUTPUT"
echo "" >> "$OUTPUT"
echo "\`\`\`bash" >> "$OUTPUT"
echo "# If conflicts found, resolve manually:" >> "$OUTPUT"
echo "git checkout <target-branch>" >> "$OUTPUT"
echo "git merge <feature-branch> --no-commit" >> "$OUTPUT"
echo "git status  # Check conflicts" >> "$OUTPUT"
echo "# Resolve conflicts in editor" >> "$OUTPUT"
echo "git add -A" >> "$OUTPUT"
echo "git commit -m 'merge: resolve conflicts'" >> "$OUTPUT"
echo "\`\`\`" >> "$OUTPUT"

echo "✅ Conflict report generated: $OUTPUT"
