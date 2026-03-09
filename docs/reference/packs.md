# Pack Catalog

All 8 built-in template packs. Each pack is a set of Jinja2 templates with a manifest declaring conditions, dependencies, and hooks.

---

## scaffold

**Version:** 0.1.0 | **Dependencies:** none

Project skeleton --- the minimum viable Python project.

| Template | Destination | Condition |
|----------|-------------|-----------|
| `pyproject.toml.j2` | `pyproject.toml` | --- |
| `init.py.j2` | `src/<name>/__init__.py` | --- |
| `py.typed.j2` | `src/<name>/py.typed` | --- |
| `conftest.py.j2` | `tests/conftest.py` | --- |
| `test_placeholder.py.j2` | `tests/test_<name>.py` | --- |
| `README.md.j2` | `README.md` | --- |
| `LICENSE.j2` | `LICENSE` | `spec.license == 'MIT'` |
| `gitignore.j2` | `.gitignore` | --- |

Applied automatically by `nboot new`.

---

## base

**Version:** 0.1.0 | **Dependencies:** none | **Hooks:** `uv lock`

CI, tooling, and project hygiene. This is the foundation that all other packs depend on.

| Template | Destination | Condition |
|----------|-------------|-----------|
| `workflows/tests.yml.j2` | `.github/workflows/tests.yml` | `spec.features.ci` |
| `pre-commit-config.yaml.j2` | `.pre-commit-config.yaml` | `spec.features.pre_commit` |
| `dependabot.yml.j2` | `.github/dependabot.yml` | --- |
| `pyproject-tools.toml.j2` | `pyproject.toml` (append) | `!spec.recon.existing_tools.ruff` |
| `AGENTS.md.j2` | `AGENTS.md` | --- |
| `DEBT.md.j2` | `DEBT.md` | --- |
| `license-header.txt.j2` | `.license-header.txt` | `spec.license` |
| `secrets-baseline.json.j2` | `.secrets.baseline` | `spec.features.pre_commit` |

**Pinned action SHAs:**

- `actions/checkout@v4.2.2`
- `step-security/harden-runner@v2.10.4`
- `actions/setup-python@v5.4.0`
- `astral-sh/setup-uv@v5.3.0`

Applied automatically by `nboot new`.

---

## security-scanning

**Version:** 0.1.0 | **Dependencies:** base

CodeQL static analysis and OpenSSF Scorecard.

| Template | Destination | Condition |
|----------|-------------|-----------|
| `workflows/codeql.yml.j2` | `.github/workflows/codeql.yml` | `spec.features.ci` |
| `workflows/scorecard.yml.j2` | `.github/workflows/scorecard.yml` | `spec.features.ci` |

**Pinned action SHAs:**

- `actions/checkout@v4.2.2`
- `step-security/harden-runner@v2.10.4`
- `github/codeql-action@v3.28.13`
- `ossf/scorecard-action@v2.4.0`

---

## github-templates

**Version:** 0.1.0 | **Dependencies:** base

Issue forms and PR template for GitHub.

| Template | Destination | Condition |
|----------|-------------|-----------|
| `ISSUE_TEMPLATE/config.yml.j2` | `.github/ISSUE_TEMPLATE/config.yml` | --- |
| `ISSUE_TEMPLATE/bug-report.yml.j2` | `.github/ISSUE_TEMPLATE/bug_report.yml` | --- |
| `ISSUE_TEMPLATE/feature-request.yml.j2` | `.github/ISSUE_TEMPLATE/feature_request.yml` | --- |
| `PULL_REQUEST_TEMPLATE.md.j2` | `.github/PULL_REQUEST_TEMPLATE.md` | --- |

**Optional inputs:** `bug_categories`, `feature_categories`, `docs_url`

---

## review-system

**Version:** 0.1.0 | **Dependencies:** base

Code review instructions for GitHub Copilot and Claude Code, plus Grippy configuration.

| Template | Destination | Condition |
|----------|-------------|-----------|
| `instructions/workflows.instructions.md.j2` | `.github/instructions/workflows.instructions.md` | --- |
| `instructions/security.instructions.md.j2` | `.github/instructions/security.instructions.md` | --- |
| `grippy.yaml.j2` | `.grippy.yaml` | --- |

**Optional inputs:** `security_src_path`

---

## quality-gates

**Version:** 0.1.0 | **Dependencies:** base

Quality metric baselines and test parity tracking.

| Template | Destination | Condition |
|----------|-------------|-----------|
| `quality-gate.json.j2` | `.github/quality-gate.json` | --- |
| `test-parity-map.json.j2` | `.github/test-parity-map.json` | --- |

**Optional inputs:** `initial_coverage`, `initial_test_count`

---

## code-hygiene

**Version:** 0.1.0 | **Dependencies:** base

Contribution guidelines.

| Template | Destination | Condition |
|----------|-------------|-----------|
| `CONTRIBUTING.md.j2` | `CONTRIBUTING.md` | --- |

**Optional inputs:** `code_style_rules`

---

## release-pipeline

**Version:** 0.1.0 | **Dependencies:** base

SLSA Level 3 release workflow with build provenance, SBOM generation, git-cliff changelog, and optional Docker support.

| Template | Destination | Condition |
|----------|-------------|-----------|
| `workflows/release.yml.j2` | `.github/workflows/release.yml` | --- |
| `workflows/_build-reusable.yml.j2` | `.github/workflows/_build-reusable.yml` | --- |
| `cliff.toml.j2` | `cliff.toml` | --- |

**Pinned action SHAs (11):**

- `actions/checkout@v4.2.2`
- `step-security/harden-runner@v2.10.4`
- `astral-sh/setup-uv@v5.3.0`
- `anchore/sbom-action@v0.18.0`
- `orhun/git-cliff-action@v4.4.2`
- `actions/attest-build-provenance@v2.2.3`
- `docker/setup-buildx-action@v3.9.0`
- `docker/login-action@v3.4.0`
- `docker/metadata-action@v5.7.0`
- `docker/build-push-action@v6.14.0`
- `aquasecurity/trivy-action@0.34.1`

**Optional inputs:** `has_docker`, `release_artifacts`

---

## Pack dependency graph

```
scaffold    base
              ├── security-scanning
              ├── github-templates
              ├── review-system
              ├── quality-gates
              ├── code-hygiene
              └── release-pipeline
```

`scaffold` and `base` are independent roots. All other packs depend on `base`. The engine topologically sorts dependencies --- if you `nboot apply --pack release-pipeline` and `base` hasn't been applied yet, the engine applies `base` first.
