name=scripts/clean_backups.sh
#!/usr/bin/env bash
# scripts/clean_backups.sh
# Dry-run by default. Use --apply to delete.

DRY_RUN=1
if [[ ${1:-} == "--apply" ]]; then
  DRY_RUN=0
fi

echo "Searching for backup files (*.bak, *~) ..."
FILES=$(git ls-files --others --exclude-standard --cached -- "*.bak" "*~" || true)

if [[ -z "$FILES" ]]; then
  echo "No backup files tracked in git. Searching in filesystem..."
  FILES=$(find . -type f \( -name "*.bak" -o -name "*~" -o -name "backup_*" \)) || true
fi

if [[ -z "$FILES" ]]; then
  echo "No backup files found."
  exit 0
fi

echo "Found files:"
echo "$FILES"

if [[ $DRY_RUN -eq 1 ]]; then
  echo "Dry-run mode. To delete files, run: $0 --apply"
  exit 0
fi

for f in $FILES; do
  echo "Deleting $f"
  rm -f "$f"
done

echo "Done."