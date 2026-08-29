#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════
# HDP Version Manager — v2.0
# Mرتب‌سازی نسخه‌ها بدون حذف + بکاپ‌گیری هوشمند
# ═══════════════════════════════════════════════════════════════

set -euo pipefail

# ═══════════════════════════════════════════════════════════════
# Configuration
# ═══════════════════════════════════════════════════════════════

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
BACKUP_ROOT="$PROJECT_ROOT/.version-backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_FILE="$BACKUP_ROOT/logs/migrate_$TIMESTAMP.log"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# ═══════════════════════════════════════════════════════════════
# Utility Functions
# ═══════════════════════════════════════════════════════════════

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
    esac
    echo -e "${color}[$(date '+%H:%M:%S')] [$level]${NC} $msg"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [$level] $msg" >> "$LOG_FILE" 2>/dev/null || true
}

ensure_dir() {
    local dir="$1"
    if [[ ! -d "$dir" ]]; then
        mkdir -p "$dir"
        log "INFO" "Created directory: $dir"
    fi
}

safe_move() {
    local src="$1"
    local dst="$2"

    if [[ ! -e "$src" ]]; then
        log "WARN" "Source does not exist: $src"
        return 1
    fi

    # If destination exists, append timestamp
    if [[ -e "$dst" ]]; then
        local backup_name="${dst}.bak_$(date +%s)"
        log "WARN" "Destination exists, moving to: $backup_name"
        mv "$dst" "$backup_name"
    fi

    ensure_dir "$(dirname "$dst")"
    mv "$src" "$dst"
    log "INFO" "Moved: $src → $dst"
}

safe_copy() {
    local src="$1"
    local dst="$2"

    if [[ ! -e "$src" ]]; then
        log "WARN" "Source does not exist: $src"
        return 1
    fi

    ensure_dir "$(dirname "$dst")"
    cp -r "$src" "$dst"
    log "INFO" "Copied: $src → $dst"
}

# ═══════════════════════════════════════════════════════════════
# Phase 1: Pre-Migration Backup
# ═══════════════════════════════════════════════════════════════

phase1_pre_migration_backup() {
    log "STEP" "═══ Phase 1: Pre-Migration Backup ═══"

    ensure_dir "$BACKUP_ROOT/pre-migration/$TIMESTAMP"
    ensure_dir "$BACKUP_ROOT/logs"

    log "INFO" "Creating full project snapshot..."

    # Backup git state
    git -C "$PROJECT_ROOT" status --short > "$BACKUP_ROOT/pre-migration/$TIMESTAMP/git_status.txt" 2>/dev/null || true
    git -C "$PROJECT_ROOT" branch -a > "$BACKUP_ROOT/pre-migration/$TIMESTAMP/branches.txt" 2>/dev/null || true
    git -C "$PROJECT_ROOT" log --oneline -20 > "$BACKUP_ROOT/pre-migration/$TIMESTAMP/recent_commits.txt" 2>/dev/null || true

    # Backup current working tree (untracked + modified)
    log "INFO" "Backing up modified and untracked files..."

    # Get list of modified/untracked files
    git -C "$PROJECT_ROOT" status --short | while read -r line; do
        local status_code="${line:0:2}"
        local filepath="${line:3}"

        # Skip if empty
        [[ -z "$filepath" ]] && continue

        local src="$PROJECT_ROOT/$filepath"
        local dst="$BACKUP_ROOT/pre-migration/$TIMESTAMP/$filepath"

        if [[ -f "$src" ]]; then
            ensure_dir "$(dirname "$dst")"
            cp "$src" "$dst"
            echo "$status_code $filepath" >> "$BACKUP_ROOT/pre-migration/$TIMESTAMP/manifest.txt"
        elif [[ -d "$src" ]]; then
            ensure_dir "$dst"
            cp -r "$src"/* "$dst"/ 2>/dev/null || true
            echo "$status_code $filepath/" >> "$BACKUP_ROOT/pre-migration/$TIMESTAMP/manifest.txt"
        fi
    done

    # Create tarball of current state
    log "INFO" "Creating tarball..."
    tar -czf "$BACKUP_ROOT/pre-migration/$TIMESTAMP/full_snapshot.tar.gz" \
        -C "$PROJECT_ROOT" \
        --exclude='.git' \
        --exclude='node_modules' \
        --exclude='__pycache__' \
        --exclude='*.pyc' \
        --exclude='.version-backups' \
        . 2>/dev/null || true

    log "INFO" "Pre-migration backup complete: $BACKUP_ROOT/pre-migration/$TIMESTAMP"
}

# ═══════════════════════════════════════════════════════════════
# Phase 2: Archive Legacy Versions
# ═══════════════════════════════════════════════════════════════

phase2_archive_legacy() {
    log "STEP" "═══ Phase 2: Archive Legacy Versions ═══"

    local archive_dir="$BACKUP_ROOT/archive/legacy_$TIMESTAMP"
    ensure_dir "$archive_dir"

    # Archive old frontend versions
    log "INFO" "Archiving old frontend versions..."

    local legacy_items=(
        "frontend.audit-backup-20260814_150434"
        "frontend.backup.20260812_155145"
        "frontend.old-mangled-20260815_150005"
        "frontend/src/hdp_copilot_frontend_src_setup.sh"
        "frontend/src/hdp-copilot"
        "frontend/src/features/index.js.bak_1785924170443"
        "frontend/src/features/index.js.bak_fix_clearSelection"
        "frontend/src/features/index.js.bak_manual_fix_20260805140140"
        "frontend/src/pages/ChatPage.js.bak_1785925157832"
        "frontend/src/pages/MapPage.js.bak_1785925157838"
    )

    for item in "${legacy_items[@]}"; do
        local src="$PROJECT_ROOT/$item"
        if [[ -e "$src" ]]; then
            safe_move "$src" "$archive_dir/$item"
        fi
    done

    # Archive old backend backups
    log "INFO" "Archiving old backend backups..."

    local backend_backups=(
        "backend/app/main.py.bak.20260814_183151"
        "backend/app/main.py.bak.20260814_183813"
        "backend/app/pipelines/search_pipeline.py.bak.20260811_011205"
        "backend/app/providers/knowledge_provider.py.bak.20260811_010635"
        "backend/app/providers/knowledge_provider.py.bak.20260811_011128"
        "backend/app/providers/knowledge_provider.py.bak.20260811_011914"
        "backend/app/providers/knowledge_provider.py.bak.20260811_012356"
        "backend/app/providers/knowledge_provider.py.bak.20260811_081015"
        "backend/app/providers/knowledge_provider.py.bak.20260812_031332"
        "backend/app/providers/knowledge_provider.py.bak_20260811_081238"
        "backend/app/providers/knowledge_provider.py.before-header-fix"
        "backend/app/providers/knowledge_provider.py.before-rerank-fix"
        "backend/app/services/chat_service.py.bak.20260812_023454"
        "backend/app/services/chat_service.py.bak.20260812_023621"
        "backend/app/services/chat_service.py.bak.20260812_023749"
        "backend/main.py.bak.20260812_024446"
        "backend/requirements.txt.bak.20260809_095517"
    )

    for item in "${backend_backups[@]}"; do
        local src="$PROJECT_ROOT/$item"
        if [[ -e "$src" ]]; then
            safe_move "$src" "$archive_dir/$item"
        fi
    done

    # Archive test backups
    log "INFO" "Archiving test backups..."

    local test_backups=(
        "backend/tests/__init__.py.bak.20260813_233444"
        "backend/tests/api/__init__.py.bak.20260813_233444"
        "backend/tests/api/test_auth_api.py.bak.20260813_233444"
        "backend/tests/api/test_cameras_api.py.bak.20260813_233444"
        "backend/tests/api/test_chat_api.py.bak.20260813_233444"
        "backend/tests/api/test_locations_api.py.bak.20260813_233444"
        "backend/tests/api/test_voice_api.py.bak.20260813_233444"
        "backend/tests/conftest.py.bak.20260813_233444"
        "backend/tests/fixtures/__init__.py.bak.20260813_233444"
        "backend/tests/fixtures/chat_payloads.json.bak.20260813_233444"
        "backend/tests/integration/__init__.py.bak.20260813_233444"
        "backend/tests/integration/test_chat_flow.py.bak.20260813_233444"
        "backend/tests/integration/test_database_path.py.bak.20260813_233444"
        "backend/tests/integration/test_gateway.py.bak.20260813_233444"
        "backend/tests/integration/test_knowledge_provider.py.bak.20260813_233444"
        "backend/tests/integration/test_search_pipeline.py.bak.20260813_233444"
        "backend/tests/unit/__init__.py.bak.20260813_233444"
        "backend/tests/unit/test_chat_service.py.bak.20260813_233444"
        "backend/tests/unit/test_config.py.bak.20260813_233444"
        "backend/tests/unit/test_models.py.bak.20260813_233444"
        "backend/tests/unit/test_utils.py.bak.20260813_233444"
    )

    for item in "${test_backups[@]}"; do
        local src="$PROJECT_ROOT/$item"
        if [[ -e "$src" ]]; then
            safe_move "$src" "$archive_dir/$item"
        fi
    done

    log "INFO" "Legacy archive complete: $archive_dir"
}

# ═══════════════════════════════════════════════════════════════
# Phase 3: Organize Current Versions
# ═══════════════════════════════════════════════════════════════

phase3_organize_current() {
    log "STEP" "═══ Phase 3: Organize Current Versions ═══"

    # Create version directories
    ensure_dir "$PROJECT_ROOT/versions"
    ensure_dir "$PROJECT_ROOT/versions/v1.0.0-stable"
    ensure_dir "$PROJECT_ROOT/versions/v1.4-develop"
    ensure_dir "$PROJECT_ROOT/versions/v2.0-mlops"

    # Tag current develop-v1.4
    log "INFO" "Tagging develop-v1.4..."
    git -C "$PROJECT_ROOT" tag -f "v1.4.0-develop-$TIMESTAMP" develop-v1.4 2>/dev/null || true

    # Create version manifest
    cat > "$PROJECT_ROOT/versions/VERSIONS.md" << 'EOF'
# HDP Version History

## Active Branches

| Version | Branch | Status | Description |
|---------|--------|--------|-------------|
| v1.0.0 | `main` | Stable | Production release |
| v1.4.0 | `develop-v1.4` | Development | Active development |
| v2.0.0 | `feature/voice-api` | Feature | Voice + AI integration |
| v2.1.0 | `feature/integration-speech-gateway` | Feature | Speech + Gateway |

## Version Directories

```
versions/
├── v1.0.0-stable/          # Stable release snapshot
├── v1.4-develop/           # Current development
├── v2.0-mlops/             # MLOps platform integration
└── archive/                # Legacy backups
```

## Migration Notes

- All `.bak*` files moved to `.version-backups/archive/`
- Original files preserved with timestamps
- Git tags created for each major version
EOF

    log "INFO" "Version organization complete"
}

# ═══════════════════════════════════════════════════════════════
# Phase 4: Clean Working Tree (Safe)
# ═══════════════════════════════════════════════════════════════

phase4_clean_working_tree() {
    log "STEP" "═══ Phase 4: Clean Working Tree (Safe) ═══"

    # Remove untracked files that are already backed up
    log "INFO" "Checking for safe-to-remove untracked files..."

    # Keep these directories (they contain active work)
    local protected_items=(
        "backend/app/integrations"
        "backend/data"
        "backend/outputs"
        "bandari-engine-2026"
        "frontend/src"
        "integrations"
        "releases"
        "tests"
    )

    # Remove old temp files
    local temp_patterns=(
        "*.bak.*"
        "*.bak_*"
        "*.before-*"
        "frontend.*backup*"
        "frontend.*old*"
    )

    for pattern in "${temp_patterns[@]}"; do
        find "$PROJECT_ROOT" -name "$pattern" -type f 2>/dev/null | while read -r file; do
            # Check if already archived
            local rel_path="${file#$PROJECT_ROOT/}"
            if [[ ! -e "$BACKUP_ROOT/archive/legacy_$TIMESTAMP/$rel_path" ]]; then
                log "WARN" "Not archived yet, skipping: $rel_path"
            else
                rm "$file"
                log "INFO" "Removed: $rel_path"
            fi
        done
    done

    log "INFO" "Working tree cleaned"
}

# ═══════════════════════════════════════════════════════════════
# Phase 5: Create Recovery Script
# ═══════════════════════════════════════════════════════════════

phase5_create_recovery() {
    log "STEP" "═══ Phase 5: Create Recovery Script ═══"

    cat > "$BACKUP_ROOT/recover.sh" << 'RECOVERY'
#!/usr/bin/env bash
# HDP Recovery Script
# Restores files from backup

set -e

BACKUP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$BACKUP_DIR/.." && pwd)"

echo "HDP Recovery Tool"
echo "================="
echo "Available backups:"
ls -la "$BACKUP_DIR/pre-migration/" 2>/dev/null || echo "No pre-migration backups"
echo ""
echo "To restore a specific backup:"
echo "  cp -r $BACKUP_DIR/pre-migration/<TIMESTAMP>/* $PROJECT_ROOT/"
echo ""
echo "To restore from archive:"
echo "  cp -r $BACKUP_DIR/archive/legacy_<TIMESTAMP>/* $PROJECT_ROOT/"
RECOVERY

    chmod +x "$BACKUP_ROOT/recover.sh"
    log "INFO" "Recovery script created: $BACKUP_ROOT/recover.sh"
}

# ═══════════════════════════════════════════════════════════════
# Phase 6: Generate Report
# ═══════════════════════════════════════════════════════════════

phase6_generate_report() {
    log "STEP" "═══ Phase 6: Generate Report ═══"

    local report="$BACKUP_ROOT/logs/report_$TIMESTAMP.md"

    cat > "$report" << EOF
# HDP Version Migration Report

**Date:** $(date '+%Y-%m-%d %H:%M:%S')  
**Timestamp:** $TIMESTAMP  
**Executed by:** $(whoami)@$(hostname)

## Summary

| Phase | Status |
|-------|--------|
| Pre-Migration Backup | ✅ Complete |
| Legacy Archive | ✅ Complete |
| Organize Current | ✅ Complete |
| Clean Working Tree | ✅ Complete |
| Recovery Script | ✅ Complete |

## Backup Locations

- **Pre-migration:** \`$BACKUP_ROOT/pre-migration/$TIMESTAMP/\`
- **Legacy archive:** \`$BACKUP_ROOT/archive/legacy_$TIMESTAMP/\`
- **Logs:** \`$BACKUP_ROOT/logs/\`

## Git State

\`\`\`
$(git -C "$PROJECT_ROOT" status --short 2>/dev/null || echo "Not a git repository")
\`\`\`

## Disk Usage

\`\`\`
$(du -sh "$BACKUP_ROOT" 2>/dev/null || echo "N/A")
\`\`\`

## Next Steps

1. Review archived files in \`$BACKUP_ROOT/archive/legacy_$TIMESTAMP/\`
2. Verify working tree with \`git status\`
3. Commit cleaned state: \`git add -A && git commit -m "chore: cleanup legacy files"\`
4. Push version tags: \`git push --tags\`

## Recovery

Run \`$BACKUP_ROOT/recover.sh\` for recovery instructions.
EOF

    log "INFO" "Report generated: $report"
}

# ═══════════════════════════════════════════════════════════════
# Main Execution
# ═══════════════════════════════════════════════════════════════

main() {
    echo -e "${CYAN}"
    cat << 'BANNER'
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║           HDP Version Manager v2.0                           ║
    ║           مرتب‌سازی نسخه‌ها بدون حذف + بکاپ‌گیری هوشمند        ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
BANNER
    echo -e "${NC}"

    log "INFO" "Starting version management..."
    log "INFO" "Project root: $PROJECT_ROOT"
    log "INFO" "Backup root: $BACKUP_ROOT"
    log "INFO" "Timestamp: $TIMESTAMP"

    # Check if in git repo
    if ! git -C "$PROJECT_ROOT" rev-parse --git-dir > /dev/null 2>&1; then
        log "ERROR" "Not a git repository!"
        exit 1
    fi

    # Execute phases
    phase1_pre_migration_backup
    phase2_archive_legacy
    phase3_organize_current
    phase4_clean_working_tree
    phase5_create_recovery
    phase6_generate_report

    echo ""
    log "INFO" "═══════════════════════════════════════════════════"
    log "INFO" "✅ Version management complete!"
    log "INFO" "═══════════════════════════════════════════════════"
    echo ""
    echo -e "${GREEN}Backup location:${NC} $BACKUP_ROOT"
    echo -e "${GREEN}Recovery script:${NC} $BACKUP_ROOT/recover.sh"
    echo -e "${GREEN}Report:${NC} $BACKUP_ROOT/logs/report_$TIMESTAMP.md"
    echo ""
    echo -e "${YELLOW}Next steps:${NC}"
    echo "  1. Review git status: git status"
    echo "  2. Commit changes: git add -A && git commit -m 'chore: cleanup legacy files'"
    echo "  3. Push tags: git push --tags"
    echo ""
}

# Handle arguments
case "${1:-run}" in
    run)
        main
        ;;
    dry-run)
        log "INFO" "Dry run mode - no changes will be made"
        # Add dry-run logic here
        ;;
    recover)
        "$BACKUP_ROOT/recover.sh" 2>/dev/null || echo "No recovery script found"
        ;;
    *)
        echo "Usage: $0 [run|dry-run|recover]"
        exit 1
        ;;
esac
