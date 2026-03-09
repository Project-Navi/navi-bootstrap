# Quickstart

Install navi-bootstrap and create your first project in under a minute.

---

## Install

```bash
pip install navi-bootstrap
```

Or with [uv](https://docs.astral.sh/uv/):

```bash
uv tool install navi-bootstrap
```

**Requirements:** Python 3.12+

---

## Create a project

```bash
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

This applies the **scaffold** and **base** packs --- a complete Python project with CI, pre-commit hooks, and dependency management.

---

## Customize with options

```bash
nboot new my-project \
  --license Apache-2.0 \
  --python-version 3.13 \
  --author "Your Name" \
  --description "What it does"
```

---

## Layer on more packs

The `nboot-spec.json` file in your new project is the source of truth. Use it to layer on additional packs:

```bash
cd my-project

# Add security scanning (CodeQL + OpenSSF Scorecard)
nboot apply --spec nboot-spec.json --pack security-scanning --target .

# Add GitHub issue/PR templates
nboot apply --spec nboot-spec.json --pack github-templates --target .

# Add SLSA L3 release pipeline
nboot apply --spec nboot-spec.json --pack release-pipeline --target .
```

See the [Pack Catalog](../reference/packs.md) for all 8 available packs.

---

## Preview before applying

Use `diff` to see what a pack would change without writing anything:

```bash
nboot diff --spec nboot-spec.json --pack release-pipeline --target .
```

This shows a unified diff of all files that would be created or modified. Exits with code 1 if changes are detected --- useful in CI for drift detection.

---

## Bootstrap an existing project

Already have a project? Generate a spec from it:

```bash
nboot init --target . --out nboot-spec.json
```

This inspects your project --- detects name, language, version, structure, dependencies, and tooling --- then generates a spec you can use with `nboot apply`.

---

## What's in the spec?

The `nboot-spec.json` captures everything about your project:

```json
{
  "name": "my-project",
  "description": "What it does",
  "language": "python",
  "python_version": "3.12",
  "license": "MIT",
  "structure": {
    "src_dir": "src/my_project",
    "test_dir": "tests"
  },
  "features": {
    "ci": true,
    "pre_commit": true
  }
}
```

The engine reads this spec and uses it to render templates. Same spec + same pack = same output, every time.

---

## Next steps

- **[CLI Reference](../reference/cli.md)** --- all 7 commands with full options
- **[Pack Catalog](../reference/packs.md)** --- what each pack generates
- **[Architecture](../explanation/architecture.md)** --- how the engine works
