# navi-bootstrap

[![Tests](https://github.com/Project-Navi/navi-bootstrap/actions/workflows/tests.yml/badge.svg)](https://github.com/Project-Navi/navi-bootstrap/actions/workflows/tests.yml)
[![CodeQL](https://github.com/Project-Navi/navi-bootstrap/actions/workflows/codeql.yml/badge.svg)](https://github.com/Project-Navi/navi-bootstrap/actions/workflows/codeql.yml)
[![codecov](https://codecov.io/gh/Project-Navi/navi-bootstrap/graph/badge.svg?token=PJ9F194alS)](https://codecov.io/gh/Project-Navi/navi-bootstrap)
[![OpenSSF Scorecard](https://api.scorecard.dev/projects/github.com/Project-Navi/navi-bootstrap/badge)](https://scorecard.dev/viewer/?uri=github.com/Project-Navi/navi-bootstrap)
[![SLSA 3](https://slsa.dev/images/gh-badge-level3.svg)](https://slsa.dev)
[![PyPI](https://img.shields.io/pypi/v/navi-bootstrap)](https://pypi.org/project/navi-bootstrap/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/downloads/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

navi-bootstrap generates operational infrastructure for Python projects — CI, security scanning, code review, release pipelines, quality gates, and the project skeleton itself — from declarative template packs.

---

## Quick start

```bash
pip install navi-bootstrap

nboot new my-project
```

One command, complete project:

```
my-project/
├── pyproject.toml
├── src/my_project/__init__.py
├── src/my_project/py.typed
├── tests/conftest.py
├── tests/test_my_project.py
├── README.md
├── LICENSE
├── .gitignore
├── .github/workflows/tests.yml
├── .github/dependabot.yml
├── .pre-commit-config.yaml
├── AGENTS.md
├── DEBT.md
└── nboot-spec.json
```

## How it works

```
spec (what your project is) + pack (what to generate) → rendered output
```

The **spec** describes your project: name, owner, Python version, license. The **pack** is a set of Jinja2 templates with a manifest declaring conditions and loops. The **engine** connects them deterministically — same spec + same pack = same output, every time.

## Packs

Eight template packs, layered with explicit dependencies:

| Pack | What it generates |
|------|-------------------|
| **scaffold** | Project skeleton — pyproject.toml, src layout, tests, README, LICENSE, .gitignore |
| **base** | CI workflows, pre-commit config, dependabot, tool config, AGENTS.md, DEBT.md |
| **security-scanning** | CodeQL analysis, OpenSSF Scorecard |
| **github-templates** | Bug report, feature request, issue config, PR template |
| **review-system** | Code review and security review workflows |
| **quality-gates** | Quality metrics baseline, test parity map |
| **code-hygiene** | CONTRIBUTING.md |
| **release-pipeline** | SLSA L3 build workflow, release dispatcher, changelog config |

`nboot new` applies `scaffold` + `base`. All other packs are elective and can be layered on afterward with `nboot apply`.

## CLI reference

| Command | Description |
|---------|-------------|
| `nboot new <name>` | Create a new project with scaffold + base packs |
| `nboot render --spec --pack --out` | Render a single pack to a new directory |
| `nboot apply --spec --pack --target` | Apply a pack to an existing project |
| `nboot diff --spec --pack --target` | Preview changes without writing |
| `nboot init --target` | Generate spec by inspecting an existing project |
| `nboot validate --spec` | Validate spec and manifest |
| `nboot list-packs` | List available packs |

## Architecture

Six-stage pipeline. Stateless and deterministic through stage 3.

```
spec.json + pack/
  -> [Stage 0: Resolve]   action SHAs via gh api
  -> [Stage 1: Validate]  spec + manifest against schemas
  -> [Stage 2: Plan]      evaluate conditions, expand loops, build render list
  -> [Stage 3: Render]    Jinja2 render to memory
  -> [Stage 4: Validate]  run post-render checks
  -> [Stage 5: Hooks]     post-render shell commands
  -> output/
```

Stages 0-3 are pure functions — spec and pack in, rendered files out, no side effects. All project-specific opinions live in the spec and the template pack, never in the engine.

```
src/navi_bootstrap/
├── cli.py        # Click CLI: new, init, render, apply, diff, validate, list-packs
├── engine.py     # Plan + Render (stages 2-3), sandboxed dest paths
├── manifest.py   # Manifest loading + validation
├── spec.py       # Spec loading + JSON Schema validation
├── resolve.py    # Stage 0: action SHA resolution
├── validate.py   # Stage 4: post-render validation
├── hooks.py      # Stage 5: hook runner
├── sanitize.py   # Input sanitization (homoglyphs, traversal, injection)
├── init.py       # Project inspection -> spec generation
├── diff.py       # Drift detection (render-to-memory + unified diff)
└── packs.py      # Pack discovery, resolution, and ordering
```

## Development

```bash
uv sync                                                # Install dependencies
uv run pytest tests/ -v                                # Run all tests
uv run ruff check src/navi_bootstrap/ tests/           # Lint
uv run ruff format src/navi_bootstrap/ tests/          # Format
uv run mypy src/navi_bootstrap/                        # Type check
uv run bandit -r src/navi_bootstrap -ll                # Security scan
pre-commit run --all-files                             # All hooks
```

Conventional commits: `feat:`, `fix:`, `chore:`, `docs:`, `test:`, `refactor:`.

Full documentation: **[Wiki](https://github.com/Project-Navi/navi-bootstrap/wiki)** — architecture, pack reference, spec schema, CLI reference, custom pack authoring.

## License

[MIT](LICENSE) -- Copyright (c) 2026 Project Navi
