#!/usr/bin/env bash
# PreToolUse hook: block edits to files listed in CLAUDE.md Scope Boundaries
# without explicit user approval. Exit 2 = block the tool call.

set -u

file=$(jq -r '.tool_input.file_path // empty' 2>/dev/null || true)
[[ -z "${file:-}" ]] && exit 0

case "$file" in
  */.github/workflows/*|*/uv.lock|*/.secrets.baseline|*/pyproject.toml)
    cat <<EOF >&2
Guarded file: $file

CLAUDE.md Scope Boundaries require explicit user approval before editing:
  - .github/workflows/**  (CI changes affect branch protection)
  - uv.lock              (dependency pins — regenerate via 'uv lock')
  - .secrets.baseline    (detect-secrets snapshot — regenerate via 'detect-secrets scan')
  - pyproject.toml       (deps, Python version constraints)

If the user has approved this edit, ask them to:
  1. Confirm the change is intentional, OR
  2. Temporarily bypass with: CLAUDE_DISABLE_HOOKS=1
EOF
    exit 2
    ;;
esac
exit 0
