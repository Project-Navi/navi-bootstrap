#!/usr/bin/env bash
# PostToolUse hook: delegate Python formatting, linting, and license-header
# enforcement to pre-commit so they stay lock-step with .pre-commit-config.yaml
# (pinned ruff SHA, insert-license rules). Single source of truth, no drift.
#
# Silent on success; failure is swallowed so the hook never blocks a tool call.

set -u

file=$(jq -r '.tool_input.file_path // empty' 2>/dev/null || true)
[[ -z "${file:-}" ]] && exit 0
[[ "$file" != *.py ]] && exit 0
[[ ! -f "$file" ]] && exit 0

# Only operate on files inside this repo's Python source/test/fuzz trees.
# Skips pack template files (packs/*/templates/*.py.j2) which contain Jinja2
# syntax that ruff would reject.
case "$file" in
  */src/navi_bootstrap/*|*/tests/*|*/fuzz/*) ;;
  *) exit 0 ;;
esac

# Delegate to pre-commit. The three hooks below are the Python-formatting
# subset; bandit / detect-secrets / gitleaks run on commit, not on every edit.
#
# `pre-commit run` takes a single hook id — trailing positionals after
# --files are treated as additional file paths, not hook ids. Loop one at
# a time to run a specific subset.
command -v pre-commit >/dev/null 2>&1 || exit 0
for hook in ruff ruff-format insert-license; do
  pre-commit run "$hook" --files "$file" >/dev/null 2>&1 || true
done
exit 0
