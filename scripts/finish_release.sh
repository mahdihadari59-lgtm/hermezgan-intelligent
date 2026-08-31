#!/usr/bin/env bash
set -euo pipefail

# finish_release.sh
# Usage:
#   ./scripts/finish_release.sh [--auto-merge] [--tag v2.0.0]
# Requirements:
# - gh (GitHub CLI) installed and authenticated (gh auth login)
# - git configured and on a clone of this repo
# - You must have push/merge permissions on the repository
# - Run this from the repository root

AUTO_MERGE=false
TAG="v2.0.0"
BRANCH="feature/complete-orchestrator"
REPO="mahdihadari59-lgtm/hermezgan-intelligent"
PR_TITLE="به‌روزرسانی و تکمیل: Orchestrator و API"
PR_BODY_FILE="PR_BODY.md"
RELEASE_NOTES_FILE="release_notes.md"

while [[ "$#" -gt 0 ]]; do
  case $1 in
    --auto-merge) AUTO_MERGE=true; shift ;;
    --tag) TAG="$2"; shift 2 ;;
    *) echo "Unknown arg: $1"; exit 1 ;;
  esac
done

echo "Repository: $REPO"
echo "Branch: $BRANCH"
echo "Tag: $TAG"

# Basic environment checks
if ! command -v gh >/dev/null 2>&1; then
  echo "Error: gh (GitHub CLI) is not installed. Install it: https://cli.github.com/" >&2
  exit 2
fi
if ! command -v git >/dev/null 2>&1; then
  echo "Error: git is not installed." >&2
  exit 2
fi

# Ensure we are in a git repo
if [ ! -d .git ]; then
  echo "Error: This script must be run from the repository root (where .git exists)." >&2
  exit 2
fi

# Ensure current branch exists locally
if ! git rev-parse --verify "$BRANCH" >/dev/null 2>&1; then
  echo "Local branch $BRANCH not found. Attempting to fetch from origin..."
  git fetch origin "$BRANCH":"$BRANCH"
fi

# Checkout branch
git checkout "$BRANCH"

echo "Pushing branch to origin (ensure your changes are committed)..."
git push origin "$BRANCH"

# Create PR if none exists
EXISTING_PR_URL=$(gh pr list --repo "$REPO" --head "$REPO.split('/') | awk -F/ '{print $1}'" --state open --json number,url,title --jq '.[] | select(.title=="'