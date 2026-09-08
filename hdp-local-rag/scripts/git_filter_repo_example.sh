name=scripts/git_filter_repo_example.sh
#!/usr/bin/env bash
# scripts/git_filter_repo_example.sh
# Example: rewrite git history to remove big files (DANGEROUS). Read comments.

cat <<'DOC'
This script illustrates how to use git filter-repo to remove files from history.
It is destructive: all collaborators must reclone after this.

Install git-filter-repo first:
  pip install git-filter-repo

Example usage to remove data/knowledge_base.json:
  git filter-repo --path data/knowledge_base.json --invert-paths

DO NOT RUN THIS UNLESS YOU KNOW WHAT YOU'RE DOING.
DOC