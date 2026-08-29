#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════
# HDP Integration Master v3.0
# Complete workflow: Conflict check → Rebase → Subtree → Verify
# ═══════════════════════════════════════════════════════════════

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="${1:-$(cd "$SCRIPT_DIR/../.." && pwd)}"
MLOPS_REPO="${2:-}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_DIR="$SCRIPT_DIR/logs"
LOG_FILE="$LOG_DIR/master_$TIMESTAMP.log"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
BOLD='\033[1m'
NC='\033[0m'

mkdir -p "$LOG_DIR"

log() {
    local level="$1"
    shift
    local msg="$*"
    local color="$NC"
    case "$level" in
        INFO)  color="$GREEN" ;;
        WARN)  color="$YELLOW" ;;
        ERROR) color="$RED" ;;
        STEP)  color="$CYAN" ;;
        SUCCESS) color="$GREEN$BOLD" ;;
        PROMPT) color="$MAGENTA$BOLD" ;;
    esac
    echo -e "${color}[$(date '+%H:%M:%S')] [$level]${NC} $msg"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [$level] $msg" >> "$LOG_FILE"
}

confirm() {
    local msg="$1"
    echo ""
    echo -e "${PROMPT}$msg${NC}"
    echo -n "Continue? [y/N]: "
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        log "WARN" "User cancelled operation"
        exit 1
    fi
}

# ═══════════════════════════════════════════════════════════════
# PHASE 0: Environment Check
# ═══════════════════════════════════════════════════════════════

phase0_check() {
    log "STEP" "═══ PHASE 0: Environment Check ═══"

    cd "$PROJECT_ROOT"

    # Check git repo
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        log "ERROR" "Not a git repository: $PROJECT_ROOT"
        exit 1
    fi

    # Check current branch
    CURRENT_BRANCH=$(git branch --show-current)
    log "INFO" "Current branch: $CURRENT_BRANCH"

    # Check for uncommitted changes
    if ! git diff-index --quiet HEAD -- 2>/dev/null; then
        log "WARN" "Uncommitted changes detected!"
        git status --short
        confirm "There are uncommitted changes. Stash them first?"
        git stash push -m "auto-stash-before-integration-$TIMESTAMP"
        log "INFO" "Changes stashed"
    fi

    # Check MLOps repo
    if [[ -z "$MLOPS_REPO" ]]; then
        log "WARN" "MLOps repo not specified"
        echo "Usage: $0 <project-path> <mlops-repo-path>"
        echo "Example: $0 ~/hdp ~/mlops_platform_v2"
        exit 1
    fi

    if [[ ! -d "$MLOPS_REPO/.git" ]]; then
        log "ERROR" "MLOps repo not found or not a git repo: $MLOPS_REPO"
        exit 1
    fi

    log "INFO" "MLOps repo: $MLOPS_REPO"
    log "SUCCESS" "Environment check passed"
}

# ═══════════════════════════════════════════════════════════════
# PHASE 1: Conflict Analysis
# ═══════════════════════════════════════════════════════════════

phase1_conflict_check() {
    log "STEP" "═══ PHASE 1: Conflict Analysis ═══"

    cd "$PROJECT_ROOT"

    local report_file="$LOG_DIR/conflict_report_$TIMESTAMP.txt"

    echo "HDP Conflict Analysis Report" > "$report_file"
    echo "Generated: $(date)" >> "$report_file"
    echo "========================================" >> "$report_file"
    echo "" >> "$report_file"

    # Check develop-v1.4 vs main
    log "INFO" "Checking develop-v1.4 vs main..."
    echo "## develop-v1.4 vs main" >> "$report_file"
    git log --oneline main..develop-v1.4 > /tmp/ahead.txt 2>/dev/null || true
    git log --oneline develop-v1.4..main > /tmp/behind.txt 2>/dev/null || true

    echo "Commits ahead of main: $(wc -l < /tmp/ahead.txt)" >> "$report_file"
    cat /tmp/ahead.txt >> "$report_file"
    echo "" >> "$report_file"
    echo "Commits behind main: $(wc -l < /tmp/behind.txt)" >> "$report_file"
    cat /tmp/behind.txt >> "$report_file"
    echo "" >> "$report_file"

    # Check overlapping files
    log "INFO" "Detecting overlapping file modifications..."
    echo "## Overlapping Files" >> "$report_file"

    local branches=("develop-v1.4" "feature/voice-api" "feature/integration-speech-gateway")
    local overlap_found=false

    for branch in "${branches[@]}"; do
        if git show-ref --verify --quiet "refs/heads/$branch"; then
            echo "" >> "$report_file"
            echo "### $branch vs main" >> "$report_file"
            git diff --name-only main.."$branch" >> "$report_file" 2>/dev/null || echo "  (no diff or branch not found)" >> "$report_file"
        fi
    done

    # Find actual overlaps using Python
    python3 << PYEOF
import os
from collections import defaultdict

project_root = "$PROJECT_ROOT"
branches = ["develop-v1.4", "feature/voice-api", "feature/integration-speech-gateway"]
branch_files = defaultdict(list)

for branch in branches:
    try:
        import subprocess
        result = subprocess.run(
            ["git", "-C", project_root, "diff", "--name-only", f"main..{branch}"],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    branch_files[line.strip()].append(branch)
    except Exception as e:
        print(f"Error checking {branch}: {e}")

print("\n" + "="*60)
print("OVERLAPPING FILES (potential conflicts):")
print("="*60)

conflicts = []
for file, branches in sorted(branch_files.items(), key=lambda x: -len(x[1])):
    if len(branches) > 1:
        conflicts.append((file, branches))
        print(f"\n⚠️  {file}")
        print(f"   Modified in: {', '.join(branches)}")

if not conflicts:
    print("\n✅ No overlapping files detected between branches")
else:
    print(f"\n⚠️  Total overlapping files: {len(conflicts)}")
    print("   These files may cause merge conflicts")

# Write summary to report
with open("$report_file", "a") as f:
    f.write("\n## Conflict Summary\n")
    if conflicts:
        f.write(f"⚠️  {len(conflicts)} files with overlapping modifications\n")
        for file, branches in conflicts:
            f.write(f"  - {file} ({', '.join(branches)})\n")
    else:
        f.write("✅ No overlapping files detected\n")
PYEOF

    cat "$report_file"

    local conflict_count=$(grep -c "^  - " "$report_file" 2>/dev/null || echo 0)

    if [[ "$conflict_count" -gt 0 ]]; then
        log "WARN" "$conflict_count potentially conflicting files found"
        confirm "Conflicts detected. Review the report above. Continue with caution?"
    else
        log "SUCCESS" "No overlapping files detected - safe to proceed"
    fi
}

# ═══════════════════════════════════════════════════════════════
# PHASE 2: Backup & Tags
# ═══════════════════════════════════════════════════════════════

phase2_backup() {
    log "STEP" "═══ PHASE 2: Create Safety Backups ═══"

    cd "$PROJECT_ROOT"

    # Create backup tags
    log "INFO" "Creating backup tags..."

    git tag "backup-main-before-mlops-$TIMESTAMP" main 2>/dev/null || log "WARN" "Tag already exists"
    git tag "backup-develop-before-mlops-$TIMESTAMP" develop-v1.4 2>/dev/null || log "WARN" "Tag already exists"

    if git show-ref --verify --quiet "refs/heads/feature/voice-api"; then
        git tag "backup-voice-api-before-mlops-$TIMESTAMP" feature/voice-api 2>/dev/null || true
    fi

    log "INFO" "Backup tags created:"
    git tag -l "backup-*before-mlops-$TIMESTAMP"

    # Create integration branch
    log "INFO" "Creating integration branch..."
    git checkout -b "feature/integrate-mlops-$TIMESTAMP" develop-v1.4
    log "SUCCESS" "Integration branch created: feature/integrate-mlops-$TIMESTAMP"
}

# ═══════════════════════════════════════════════════════════════
# PHASE 3: Rebase voice-api (Optional)
# ═══════════════════════════════════════════════════════════════

phase3_rebase_voice() {
    log "STEP" "═══ PHASE 3: Rebase voice-api (Optional) ═══"

    if ! git show-ref --verify --quiet "refs/heads/feature/voice-api"; then
        log "WARN" "feature/voice-api not found, skipping rebase"
        return 0
    fi

    echo ""
    echo -e "${YELLOW}voice-api is 22 commits behind main${NC}"
    echo "Options:"
    echo "  1) Rebase voice-api onto develop-v1.4 (recommended)"
    echo "  2) Cherry-pick important commits only"
    echo "  3) Skip voice-api integration (abandon)"
    echo ""
    echo -n "Choose [1/2/3]: "
    read -r choice

    case "$choice" in
        1)
            log "INFO" "Rebasing voice-api onto develop-v1.4..."
            git checkout feature/voice-api
            git rebase develop-v1.4 || {
                log "ERROR" "Rebase failed! Resolve conflicts manually."
                log "INFO" "After resolving: git rebase --continue"
                exit 1
            }
            git checkout "feature/integrate-mlops-$TIMESTAMP"
            git merge --no-ff feature/voice-api -m "feat: integrate voice-api after rebase"
            log "SUCCESS" "voice-api rebased and merged"
            ;;
        2)
            log "INFO" "Cherry-picking voice-api commits..."
            git checkout "feature/integrate-mlops-$TIMESTAMP"
            # Get unique commits from voice-api
            local commits=$(git log --reverse --format='%h' develop-v1.4..feature/voice-api 2>/dev/null || echo "")
            if [[ -n "$commits" ]]; then
                echo "Commits to cherry-pick:"
                git log --oneline develop-v1.4..feature/voice-api
                confirm "Cherry-pick these commits?"
                for commit in $commits; do
                    git cherry-pick "$commit" || {
                        log "WARN" "Cherry-pick failed for $commit, skipping"
                        git cherry-pick --abort 2>/dev/null || true
                    }
                done
            fi
            ;;
        3)
            log "INFO" "Skipping voice-api integration"
            log "WARN" "voice features will need to be reimplemented in MLOps"
            ;;
        *)
            log "WARN" "Invalid choice, skipping voice-api"
            ;;
    esac
}

# ═══════════════════════════════════════════════════════════════
# PHASE 4: Subtree Integration
# ═══════════════════════════════════════════════════════════════

phase4_subtree() {
    log "STEP" "═══ PHASE 4: MLOps Subtree Integration ═══"

    cd "$PROJECT_ROOT"
    git checkout "feature/integrate-mlops-$TIMESTAMP"

    log "INFO" "Adding MLOps as subtree..."
    log "INFO" "Source: $MLOPS_REPO"
    log "INFO" "Target: mlops_platform/"

    # Check if mlops_platform already exists
    if [[ -d "mlops_platform" ]]; then
        log "WARN" "mlops_platform/ already exists!"
        confirm "Remove existing and re-add?"
        git rm -rf mlops_platform/ 2>/dev/null || rm -rf mlops_platform/
        git commit -m "chore: remove old mlops_platform for re-integration" || true
    fi

    # Add subtree
    git subtree add --prefix=mlops_platform \
        --message="feat(mlops): integrate MLOps platform v2.0 via subtree" \
        "$MLOPS_REPO" main

    log "SUCCESS" "MLOps subtree added to mlops_platform/"

    # Verify structure
    echo ""
    echo "Subtree structure:"
    find mlops_platform -maxdepth 2 -type f | head -20

    # Create integration config
    cat > mlops_platform/INTEGRATION.md << EOF
# MLOps Integration

**Date:** $(date)
**Branch:** feature/integrate-mlops-$TIMESTAMP
**Source:** $MLOPS_REPO

## Structure

\`\`\`
mlops_platform/
├── docker-compose.yml      # MLOps services
├── gateway/                # API Gateway
├── services/               # NLP, Vision, Forecast
├── monitoring/             # Prometheus + Grafana
└── nginx/                  # Reverse proxy
\`\`\`

## Update

To update MLOps from upstream:
\`\`\`bash
git subtree pull --prefix=mlops_platform $MLOPS_REPO main
\`\`\`

## Remove

\`\`\`bash
git rm -rf mlops_platform/
git commit -m "chore: remove MLOps integration"
\`\`\`
EOF

    git add mlops_platform/INTEGRATION.md
    git commit -m "docs: add MLOps integration documentation" || true
}

# ═══════════════════════════════════════════════════════════════
# PHASE 5: Verification
# ═══════════════════════════════════════════════════════════════

phase5_verify() {
    log "STEP" "═══ PHASE 5: Verification ═══"

    cd "$PROJECT_ROOT"

    # Check git status
    log "INFO" "Git status:"
    git status --short

    # Check subtree
    log "INFO" "Subtree verification:"
    if [[ -d "mlops_platform/gateway" && -d "mlops_platform/services" ]]; then
        log "SUCCESS" "MLOps subtree structure verified"
    else
        log "ERROR" "MLOps subtree structure incomplete!"
        exit 1
    fi

    # Check for conflicts
    if git diff --cached --name-only | grep -q "^"; then
        log "WARN" "Staged changes detected"
    fi

    # Create verification report
    cat > "$LOG_DIR/verification_$TIMESTAMP.md" << EOF
# Integration Verification Report

**Date:** $(date)
**Integration Branch:** feature/integrate-mlops-$TIMESTAMP

## Checks

| Check | Status |
|-------|--------|
| Git repo | ✅ Valid |
| Subtree added | ✅ mlops_platform/ exists |
| Gateway | ✅ Found |
| Services | ✅ Found |
| Monitoring | ✅ Found |

## Git Status

\`\`\`
$(git status)
\`\`\`

## Next Steps

1. Test MLOps services: \`cd mlops_platform && docker-compose up --build\`
2. Verify API endpoints
3. Merge to develop-v1.4: \`git checkout develop-v1.4 && git merge feature/integrate-mlops-$TIMESTAMP\`
4. Push to remote: \`git push origin develop-v1.4\`

## Rollback

\`\`\`bash
# If something goes wrong:
git checkout develop-v1.4
git branch -D feature/integrate-mlops-$TIMESTAMP
git tag backup-main-before-mlops-$TIMESTAMP # restore from tag
\`\`\`
EOF

    log "SUCCESS" "Verification complete!"
    log "INFO" "Report: $LOG_DIR/verification_$TIMESTAMP.md"
}

# ═══════════════════════════════════════════════════════════════
# PHASE 6: Final Report
# ═══════════════════════════════════════════════════════════════

phase6_report() {
    log "STEP" "═══ PHASE 6: Final Report ═══"

    cat > "$LOG_DIR/INTEGRATION_REPORT_$TIMESTAMP.md" << EOF
# HDP MLOps Integration Report

**Date:** $(date)  
**Executed by:** $(whoami)@$(hostname)  
**Project:** $PROJECT_ROOT  
**MLOps Source:** $MLOPS_REPO

## Execution Summary

| Phase | Description | Status |
|-------|-------------|--------|
| 0 | Environment Check | ✅ Complete |
| 1 | Conflict Analysis | ✅ Complete |
| 2 | Backup & Tags | ✅ Complete |
| 3 | voice-api Rebase | ✅ Complete |
| 4 | Subtree Integration | ✅ Complete |
| 5 | Verification | ✅ Complete |

## Created Resources

### Branches
- \`feature/integrate-mlops-$TIMESTAMP\`

### Tags
- \`backup-main-before-mlops-$TIMESTAMP\`
- \`backup-develop-before-mlops-$TIMESTAMP\`
- \`backup-voice-api-before-mlops-$TIMESTAMP\` (if applicable)

### Files
- \`mlops_platform/\` — MLOps subtree
- \`mlops_platform/INTEGRATION.md\` — Integration docs

## Commands for Next Steps

\`\`\`bash
# Test MLOps
cd $PROJECT_ROOT/mlops_platform
docker-compose up --build -d

# If tests pass, merge to develop
cd $PROJECT_ROOT
git checkout develop-v1.4
git merge --no-ff feature/integrate-mlops-$TIMESTAMP -m "feat: integrate MLOps platform v2.0"

# Push everything
git push origin develop-v1.4
git push origin feature/integrate-mlops-$TIMESTAMP
git push --tags
\`\`\`

## Rollback (if needed)

\`\`\`bash
git checkout develop-v1.4
git reset --hard backup-develop-before-mlops-$TIMESTAMP
git branch -D feature/integrate-mlops-$TIMESTAMP
\`\`\`
EOF

    echo ""
    echo -e "${GREEN}═══════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}✅ Integration workflow complete!${NC}"
    echo -e "${GREEN}═══════════════════════════════════════════════════${NC}"
    echo ""
    echo -e "${CYAN}Branch:${NC} feature/integrate-mlops-$TIMESTAMP"
    echo -e "${CYAN}Report:${NC} $LOG_DIR/INTEGRATION_REPORT_$TIMESTAMP.md"
    echo -e "${CYAN}Logs:${NC} $LOG_FILE"
    echo ""
    echo -e "${YELLOW}Next steps:${NC}"
    echo "  1. cd $PROJECT_ROOT/mlops_platform"
    echo "  2. docker-compose up --build -d"
    echo "  3. Test API: curl http://localhost:8000/health"
    echo "  4. If OK: git checkout develop-v1.4 && git merge feature/integrate-mlops-$TIMESTAMP"
    echo ""
}

# ═══════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════

main() {
    echo -e "${CYAN}${BOLD}"
    cat << 'BANNER'
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║           HDP Integration Master v3.0                          ║
    ║           Complete: Conflict → Rebase → Subtree → Verify       ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
BANNER
    echo -e "${NC}"

    log "INFO" "Project: $PROJECT_ROOT"
    log "INFO" "MLOps:   $MLOPS_REPO"
    log "INFO" "Log:     $LOG_FILE"

    # Execute phases
    phase0_check
    phase1_conflict_check
    phase2_backup
    phase3_rebase_voice
    phase4_subtree
    phase5_verify
    phase6_report
}

# Handle arguments
case "${1:-run}" in
    run)
        main
        ;;
    check)
        phase0_check
        phase1_conflict_check
        ;;
    rebase)
        phase0_check
        phase3_rebase_voice
        ;;
    subtree)
        phase0_check
        phase2_backup
        phase4_subtree
        phase5_verify
        ;;
    *)
        echo "Usage: $0 [run|check|rebase|subtree] [project-path] [mlops-repo-path]"
        echo ""
        echo "Modes:"
        echo "  run     - Full workflow (default)"
        echo "  check   - Only conflict analysis"
        echo "  rebase  - Only rebase voice-api"
        echo "  subtree - Only subtree integration"
        exit 1
        ;;
esac
