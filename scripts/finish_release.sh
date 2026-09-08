#!/usr/bin/env bash
set -euo pipefail

# finish_release.sh
# Usage:
#   ./scripts/finish_release.sh [--auto-merge] [--tag v2.0.0] [--branch feature/...] [--base main]
#
# Requirements:
# - gh (GitHub CLI) installed and authenticated: `gh auth login`
# - git installed and repository cloned locally (run from repo root)
# - You must have push/merge permissions on the repository to merge & create releases
#
# What it does:
# 1) Pushes the target branch to origin
# 2) Creates a Pull Request if none open
# 3) (Optional) Waits for checks and merges the PR (if --auto-merge)
# 4) After merge, creates a git tag and a GitHub Release using release_notes.md

REPO="mahdihadari59-lgtm/hermezgan-intelligent"
REPO_OWNER="${REPO%%/*}"
BRANCH="feature/complete-orchestrator"
BASE="main"
PR_TITLE="به‌روزرسانی و تکمیل: Orchestrator و API"
PR_BODY_FILE="PR_BODY.md"
RELEASE_NOTES_FILE="release_notes.md"
TAG="v2.0.0"
AUTO_MERGE=false
WAIT_FOR_CHECKS=true
CHECK_POLL_INTERVAL=10  # seconds
CHECK_POLL_MAX=60       # max polls (total wait = interval * max)

function usage() {
  echo "Usage: $0 [--auto-merge] [--no-wait-checks] [--tag vX.Y.Z] [--branch BRANCH] [--base BASE]"
  exit 1
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --auto-merge) AUTO_MERGE=true; shift ;;
    --no-wait-checks) WAIT_FOR_CHECKS=false; shift ;;
    --tag) TAG="$2"; shift 2 ;;
    --branch) BRANCH="$2"; shift 2 ;;
    --base) BASE="$2"; shift 2 ;;
    -h|--help) usage ;;
    *) echo "Unknown arg: $1"; usage ;;
  esac
done

# Basic checks
command -v gh >/dev/null 2>&1 || { echo "gh (GitHub CLI) is required. Install: https://cli.github.com/"; exit 2; }
command -v git >/dev/null 2>&1 || { echo "git is required."; exit 2; }

if [ ! -d .git ]; then
  echo "Error: Run this script from the repository root (where .git exists)."
  exit 2
fi

# Ensure branch exists locally (fetch from origin if needed)
if ! git rev-parse --verify "$BRANCH" >/dev/null 2>&1; then
  echo "Local branch $BRANCH not found. Attempting to fetch from origin..."
  git fetch origin "$BRANCH":"$BRANCH"
fi

echo "Checking out branch: $BRANCH"
git checkout "$BRANCH"

echo "Pushing branch to origin..."
git push origin "$BRANCH"

# Build gh head spec
HEAD_SPEC="${REPO_OWNER}:${BRANCH}"

# Find existing open PR for this head -> base
echo "Searching for existing open PR for $HEAD_SPEC -> $BASE ..."
PR_URL=$(gh pr list --repo "$REPO" --head "$HEAD_SPEC" --base "$BASE" --state open --json url --jq '.[0].url' 2>/dev/null || true)

if [ -z "$PR_URL" ] || [ "$PR_URL" = "null" ]; then
  echo "No open PR found. Creating a new PR..."
  if [ ! -f "$PR_BODY_FILE" ]; then
    echo "Warning: PR body file '$PR_BODY_FILE' not found. Using empty body."
    PR_URL=$(gh pr create --repo "$REPO" --base "$BASE" --head "$HEAD_SPEC" --title "$PR_TITLE" --body "" --json url --jq .url)
  else
    PR_URL=$(gh pr create --repo "$REPO" --base "$BASE" --head "$HEAD_SPEC" --title "$PR_TITLE" --body-file "$PR_BODY_FILE" --json url --jq .url)
  fi
  echo "PR created: $PR_URL"
else
  echo "Found existing PR: $PR_URL"
fi

# Optionally wait for checks to pass before merge
if [ "$AUTO_MERGE" = true ]; then
  echo "Auto-merge requested."
  if [ "$WAIT_FOR_CHECKS" = true ]; then
    echo "Waiting for checks to complete (poll every $CHECK_POLL_INTERVAL s, up to $((CHECK_POLL_INTERVAL*CHECK_POLL_MAX))s)..."
    count=0
    while true; do
      # Get combined check status for the PR
      CHECK_STATUS=$(gh pr checks "$PR_URL" --repo "$REPO" --json conclusion --jq '.[0].conclusion' 2>/dev/null || true)
      # conclusion can be "SUCCESS", "FAILURE", "PENDING", null if no checks
      if [[ "$CHECK_STATUS" == "SUCCESS" ]]; then
        echo "Checks passed."
        break
      elif [[ "$CHECK_STATUS" == "FAILURE" ]]; then
        echo "Checks failed. Aborting auto-merge."
        exit 3
      else
        count=$((count+1))
        if [ $count -ge $CHECK_POLL_MAX ]; then
          echo "Timed out waiting for checks. You can retry later or merge manually."
          exit 4
        fi
        echo "Checks not ready yet (status: ${CHECK_STATUS:-unknown}). Sleeping $CHECK_POLL_INTERVAL s..."
        sleep $CHECK_POLL_INTERVAL
      fi
    done
  fi

  echo "Merging PR..."
  gh pr merge "$PR_URL" --repo "$REPO" --merge --delete-branch
  echo "PR merged."
else
  echo "Auto-merge not requested. Please review and merge the PR manually when ready: $PR_URL"
fi

# After merge: ensure base updated
echo "Updating local $BASE branch..."
git checkout "$BASE"
git pull origin "$BASE"

# Create tag and push
echo "Creating and pushing tag: $TAG"
git tag -a "$TAG" -m "Release $TAG"
git push origin "$TAG"

# Create GitHub Release using release_notes.md if available
if [ -f "$RELEASE_NOTES_FILE" ]; then
  echo "Creating GitHub Release ($TAG) with notes from $RELEASE_NOTES_FILE ..."
  gh release create "$TAG" --repo "$REPO" --title "$TAG" --notes-file "$RELEASE_NOTES_FILE"
else
  echo "Release notes file '$RELEASE_NOTES_FILE' not found. Creating release with empty notes."
  gh release create "$TAG" --repo "$REPO" --title "$TAG" --notes "Release $TAG"
fi

echo "Done. Release $TAG created. PR: $PR_URL"]
