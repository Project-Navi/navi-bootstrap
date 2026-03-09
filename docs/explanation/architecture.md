# Architecture

How navi-bootstrap turns declarative specs into complete project infrastructure.

---

## Core principle: spec + pack = output

All project-specific opinions live in the **spec** (what your project is) and the **pack** (what to generate). The engine is a generic, deterministic connector between them.

```
spec.json + pack/ → engine → rendered files
```

Same spec + same pack = same output, every time. No hidden state, no ambient configuration, no network calls during rendering.

---

## The six-stage pipeline

```
spec.json + pack/
  → [Stage 0: Resolve]   action SHAs via gh api
  → [Stage 1: Validate]  spec + manifest against schemas
  → [Stage 2: Plan]      evaluate conditions, expand loops, build render list
  → [Stage 3: Render]    Jinja2 render to memory
  → [Stage 4: Validate]  run post-render checks
  → [Stage 5: Hooks]     post-render shell commands
  → output/
```

### Stage 0 --- Resolve

GitHub Action references in templates use pinned SHAs for supply-chain security (e.g., `actions/checkout@<sha>`). Stage 0 resolves version tags to commit SHAs via the GitHub API.

**Skippable** with `--skip-resolve` for offline use.

### Stage 1 --- Validate

The spec is validated against a JSON Schema. The pack manifest is validated against a YAML Schema. If either fails, the pipeline stops with a clear error.

### Stage 2 --- Plan

The engine reads the pack's `manifest.yaml` and evaluates:

- **Conditions** --- which templates to include (e.g., `spec.features.ci` gates CI workflow templates)
- **Loops** --- which templates to expand (e.g., iterating over configured languages)
- **Dependency ordering** --- packs declare dependencies; the engine topologically sorts them

The output is a **render list** --- an ordered sequence of (template, destination) pairs.

### Stage 3 --- Render

Each template in the render list is rendered via Jinja2 with the spec as context. All rendering happens in memory --- no files are written until the full render succeeds.

**Destination paths are sandboxed.** The engine rejects any template that would write outside the output directory (path traversal prevention).

### Stages 4--5 --- Validate and hooks

**Stage 4** runs post-render checks declared in the manifest (e.g., "generated YAML is valid," "generated JSON parses"). **Stage 5** runs shell hooks (e.g., `uv lock`).

These stages are **opt-in** --- they only run with the `--trust` flag. By default, nboot generates files and nothing else.

---

## The determinism guarantee

Stages 0--3 are **pure functions**. Given the same inputs:

- No network calls (stage 0 is skippable, and SHAs are cached in the manifest)
- No filesystem reads beyond the spec and pack
- No randomness, timestamps, or environment variables in the render path
- Templates are rendered in deterministic order (topological sort of dependencies, then alphabetical within a pack)

This means `nboot diff` is reliable --- if it shows no changes, the project is in sync with its spec.

---

## Module layout

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
├── init.py       # Project inspection → spec generation
├── diff.py       # Drift detection (render-to-memory + unified diff)
└── packs.py      # Pack discovery, resolution, and ordering
```

Each module owns one stage or concern. The engine (`engine.py`) is the smallest module --- it just connects plan to render.

---

## Pack structure

Every pack is a directory containing:

```
packs/<pack-name>/
├── manifest.yaml      # Declares templates, conditions, loops, deps, hooks
└── templates/        # Jinja2 templates (.j2 extension)
    ├── file1.j2
    └── subdir/
        └── file2.j2
```

The manifest declares:

- **`templates`** --- list of template files with their destination paths
- **`conditions`** --- expressions evaluated against the spec (e.g., `spec.features.ci`)
- **`dependencies`** --- other packs that must be applied first
- **`action_shas`** --- GitHub Action version → SHA mappings
- **`hooks`** --- shell commands to run after rendering
- **`validation`** --- post-render checks

See the [Pack Catalog](../reference/packs.md) for all 8 built-in packs.

---

## Design decisions

### Why specs, not config files?

Config files accumulate opinions over time. Specs are declarative snapshots --- they describe what the project **is**, not what it **should do**. The pack decides what to generate from that description.

### Why Jinja2?

Jinja2 is the most widely understood template language in the Python ecosystem. It has conditionals, loops, filters, and a sandboxed execution model. No reason to invent something new.

### Why pinned action SHAs?

GitHub Actions referenced by tag (e.g., `actions/checkout@v4`) are mutable --- the tag can be force-pushed. Pinning to commit SHAs makes CI workflows reproducible and resistant to supply-chain attacks. Stage 0 automates this resolution.

### Why layered packs?

Not every project needs every feature. `nboot new` gives you the essentials (scaffold + base). Everything else is opt-in, applied incrementally, and previewable via `nboot diff` before writing.
