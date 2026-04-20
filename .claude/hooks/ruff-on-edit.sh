#!/usr/bin/env bash
# PostToolUse hook: format + lint-fix Python files after Edit/Write/MultiEdit.
# Silent on success; any failure is swallowed so the hook never blocks a tool.

set -u

file=$(jq -r '.tool_input.file_path // empty' 2>/dev/null || true)
[[ -z "${file:-}" ]] && exit 0
[[ "$file" != *.py ]] && exit 0
[[ ! -f "$file" ]] && exit 0

# Only operate on files inside this repo's Python source/test trees.
case "$file" in
  */src/navi_bootstrap/*|*/tests/*|*/fuzz/*) ;;
  *) exit 0 ;;
esac

uv run ruff format "$file" >/dev/null 2>&1 || true
uv run ruff check --fix "$file" >/dev/null 2>&1 || true
exit 0
