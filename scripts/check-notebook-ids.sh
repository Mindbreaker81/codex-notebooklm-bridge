#!/usr/bin/env bash
# Flag suspiciously long real-looking NotebookLM IDs in tracked files.
# Real IDs are typically 32+ chars of [A-Za-z0-9_-]. The placeholder we use
# in docs is the literal "<id>", which is allowed.
#
# Usage: scripts/check-notebook-ids.sh [files...]
# With no args, scans all tracked files. Intended for use as a pre-commit hook.

set -euo pipefail

if [[ $# -eq 0 ]]; then
  mapfile -t files < <(git ls-files)
else
  files=("$@")
fi

pattern='notebooklm\.google\.com/notebook/[A-Za-z0-9_-]{20,}'
hits=0

for f in "${files[@]}"; do
  [[ -f "$f" ]] || continue
  case "$f" in
    *.png|*.jpg|*.jpeg|*.gif|*.pdf|*.zip) continue ;;
  esac
  if grep -nE "$pattern" "$f" >/dev/null 2>&1; then
    echo "Possible real NotebookLM ID in $f:"
    grep -nE "$pattern" "$f"
    hits=$((hits + 1))
  fi
done

if [[ $hits -gt 0 ]]; then
  echo
  echo "Refusing to commit. Replace real notebook IDs with the literal placeholder <id>."
  echo "If this is a false positive, bypass with: git commit --no-verify"
  exit 1
fi
