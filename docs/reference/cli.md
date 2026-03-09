# CLI Reference

All commands available via `nboot` (or `navi-bootstrap`).

---

## nboot new

Create a new project with the **scaffold** and **base** packs.

```bash
nboot new <name> [options]
```

| Option | Description | Default |
|--------|-------------|---------|
| `--description` | Project description | --- |
| `--license` | License identifier (MIT, Apache-2.0, etc.) | MIT |
| `--python-version` | Minimum Python version | 3.12 |
| `--author` | Author name | --- |
| `--packs` | Additional packs to apply (comma-separated) | --- |
| `--skip-resolve` | Skip GitHub Action SHA resolution | false |
| `--dry-run` | Show what would be generated without writing | false |

**Example:**

```bash
nboot new my-project \
  --license Apache-2.0 \
  --python-version 3.13 \
  --author "Nelson Spence" \
  --description "Fractal dimension estimation"
```

Creates the project directory, applies scaffold + base, initializes git, and runs hooks (`uv lock`).

---

## nboot render

Render a single pack to a new directory.

```bash
nboot render --spec <path> --pack <name> --out <dir> [options]
```

| Option | Description | Default |
|--------|-------------|---------|
| `--spec` | Path to spec JSON file | **required** |
| `--pack` | Pack name to render | **required** |
| `--out` | Output directory | **required** |
| `--skip-resolve` | Skip GitHub Action SHA resolution | false |
| `--dry-run` | Show what would be generated without writing | false |
| `--trust` | Execute post-render hooks and validation | false |

**Example:**

```bash
nboot render \
  --spec nboot-spec.json \
  --pack scaffold \
  --out output/
```

---

## nboot apply

Apply a pack to an existing project. Non-destructive by default --- files with `mode: append` are appended, not overwritten.

```bash
nboot apply --spec <path> --pack <name> --target <dir> [options]
```

| Option | Description | Default |
|--------|-------------|---------|
| `--spec` | Path to spec JSON file | **required** |
| `--pack` | Pack name to apply | **required** |
| `--target` | Target project directory | **required** |
| `--skip-resolve` | Skip GitHub Action SHA resolution | false |
| `--dry-run` | Show what would be applied without writing | false |
| `--trust` | Execute post-render hooks and validation | false |

**Example:**

```bash
nboot apply \
  --spec nboot-spec.json \
  --pack security-scanning \
  --target .
```

---

## nboot diff

Preview changes without writing. Shows a unified diff of all files that would be created or modified.

```bash
nboot diff --spec <path> --pack <name> --target <dir> [options]
```

| Option | Description | Default |
|--------|-------------|---------|
| `--spec` | Path to spec JSON file | **required** |
| `--pack` | Pack name to diff | **required** |
| `--target` | Target project directory | **required** |
| `--skip-resolve` | Skip GitHub Action SHA resolution | false |

**Exit codes:**

- `0` --- no changes detected (project in sync with spec)
- `1` --- changes detected (drift from spec)

**Example:**

```bash
nboot diff \
  --spec nboot-spec.json \
  --pack base \
  --target .
```

Useful in CI for drift detection --- fail the build if packs are out of sync with reality.

---

## nboot init

Inspect an existing project and generate a spec from it.

```bash
nboot init --target <dir> [options]
```

| Option | Description | Default |
|--------|-------------|---------|
| `--target` | Project directory to inspect | **required** |
| `--out` | Output path for generated spec | nboot-spec.json |
| `--yes` | Skip interactive prompts | false |

**What it detects:**

- Project name (from pyproject.toml or directory name)
- Language and version
- Source and test directory structure
- Dependencies and dev tools
- Existing CI configuration
- Test count and coverage

**Example:**

```bash
nboot init --target . --out nboot-spec.json
```

---

## nboot validate

Validate a spec file (and optionally a pack manifest) against their JSON/YAML schemas.

```bash
nboot validate --spec <path> [--pack <name>]
```

| Option | Description | Default |
|--------|-------------|---------|
| `--spec` | Path to spec JSON file | **required** |
| `--pack` | Pack name to validate manifest | --- |

**Example:**

```bash
# Validate spec only
nboot validate --spec nboot-spec.json

# Validate spec + pack manifest
nboot validate --spec nboot-spec.json --pack release-pipeline
```

---

## nboot list-packs

List all available template packs with their version and description.

```bash
nboot list-packs
```

**Example output:**

```
scaffold              v0.1.0  Project skeleton — pyproject.toml, src layout, tests
base                  v0.1.0  CI workflows, pre-commit, dependabot, tool config
security-scanning     v0.1.0  CodeQL analysis, OpenSSF Scorecard
github-templates      v0.1.0  Issue forms, PR template
review-system         v0.1.0  Code review and security review workflows
quality-gates         v0.1.0  Quality metrics baseline, test parity map
code-hygiene          v0.1.0  CONTRIBUTING.md
release-pipeline      v0.1.0  SLSA L3 release workflow, changelog config
```

---

## Global behavior

### Dry run

All commands that write files support `--dry-run`. In dry-run mode, the full pipeline executes (resolve, validate, plan, render) but no files are written. The rendered file list is printed to stdout.

### Skip resolve

All commands that render templates support `--skip-resolve`. This skips Stage 0 (GitHub Action SHA resolution), which requires network access. Useful for offline development or when SHAs are already cached in the manifest.

### Trust

Commands that can execute hooks (`render`, `apply`) support `--trust`. Without this flag, stages 4--5 (validation and hooks) are skipped. This is a deliberate security boundary --- see [Security Model](../explanation/security-model.md).
