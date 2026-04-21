# CLAUDE.md

This file provides guidance to Claude Code when working with code in this repository.

## Project Overview

**navi-bootstrap** is a Jinja2 rendering engine and template packs for bootstrapping projects.

- **Language:** Python
- **Python version:** >= 3.12
- **Build system:** hatchling
- **Package manager:** uv
- **CLI entry point:** `nboot` (Click-based) — `nboot new` creates projects, `nboot apply` layers packs

### Repository Layout

```
src/
  navi_bootstrap/   # 12 modules — engine, CLI, spec, manifest, resolve, validate, diff, hooks, init, sanitize, packs
packs/              # 8 template packs — scaffold, base, code-hygiene, github-templates, quality-gates, release-pipeline, review-system, security-scanning
tests/              # unit/integration + adversarial/ suite (unicode-hostile, path-traversal, template-injection)
schema/             # JSON Schema for spec + manifest (force-included in wheel)
fuzz/               # atheris fuzz harness (fuzz_sanitize.py)
docs/               # zensical documentation site
.github/workflows/  # 8 workflows — see CI Pipeline below
```

### Pipeline (engine stages)

`spec + pack → [0 Resolve] → [1 Validate] → [2 Plan] → [3 Render] → [4 Validate] → [5 Hooks] → output`

Stages 0-3 are pure. All project opinions live in the spec/pack, never the engine.

## Development Commands

```bash
# Install dependencies
uv sync

# Run all tests
uv run pytest tests/ -v

# Run tests with coverage
uv run pytest tests/ -v --cov=src/navi_bootstrap --cov-report=term-missing

# Lint
uv run ruff check src/navi_bootstrap/ tests/

# Format
uv run ruff format src/navi_bootstrap/ tests/

# Type check
uv run mypy src/navi_bootstrap/

# Security scan
uv run bandit -r src/navi_bootstrap -ll

# Run all quality checks
uv run ruff format --check src/navi_bootstrap/ tests/ && \
  uv run ruff check src/navi_bootstrap/ tests/ && \
  uv run mypy src/navi_bootstrap/

# Pre-commit (run all hooks)
pre-commit run --all-files
```

### Dev loop for CLI/pack changes

```bash
# Exercise the CLI without installing
uv run nboot new /tmp/demo
uv run nboot apply --spec nboot-spec.json --pack security-scanning --target /tmp/demo
uv run nboot diff  --spec nboot-spec.json --pack base              --target /tmp/demo
```

## Code Quality Standards

- Line length: 100 characters
- Linter: ruff (select: E, F, I, N, W, UP, B, RUF, C4)
- Type checking: mypy (strict mode)
- Security: bandit, detect-secrets (baseline in `.secrets.baseline`), gitleaks
- License headers: SPDX `MIT` enforced via pre-commit on `.py` files
- First-party dep: `navi-sanitize` — all user input flows through it (homoglyphs, traversal, injection)

## CI Pipeline

- **tests.yml** — pytest on 3.12 & 3.13; ruff + mypy + bandit on 3.12; aggregates to `test` + `quality-gate` required checks
- **codeql.yml** — GitHub CodeQL security scanning
- **scorecard.yml** — OSSF Scorecard
- **semgrep.yml** — SAST rules
- **grippy-review.yml** — code review bot (skips fork/bot-authored PRs)
- **fuzz.yml** — atheris fuzz harness
- **docs.yml** — zensical docs build/deploy
- **release.yml** — SLSA L3 release pipeline (on tag push: `v*`)

## Commit Conventions

- Use conventional commits: `feat:`, `fix:`, `chore:`, `docs:`, `test:`, `refactor:`
- Keep commits atomic — one logical change per commit
- Run quality checks before committing

## Scope Boundaries

- Do not modify files outside `src/`, `tests/`, `packs/`, and `docs/` without explicit approval
- Do not bump `requires-python` or change dependency version constraints without discussion
- Do not modify `.github/workflows/` without discussion — CI changes affect branch protection
