---
hide:
  - navigation
  - toc
---

<div class="hero-glow" markdown>

# navi-bootstrap

**Spec-driven Jinja2 engine and template packs for bootstrapping Python projects.**

One command. Complete project. CI, security scanning, release pipelines, quality gates --- all from declarative specs.

[Get Started](getting-started/quickstart.md){ .md-button .md-button--primary }
[Pack Catalog](reference/packs.md){ .md-button }

</div>

---

## How it works

```
spec (what your project is) + pack (what to generate) → rendered output
```

The **spec** describes your project: name, Python version, license. The **pack** is a set of Jinja2 templates with a manifest declaring conditions and loops. The **engine** connects them deterministically --- same spec + same pack = same output, every time.

---

## Eight template packs

| Pack | What it generates |
|------|-------------------|
| **scaffold** | Project skeleton --- pyproject.toml, src layout, tests, README, LICENSE, .gitignore |
| **base** | CI workflows, pre-commit config, dependabot, tool config, AGENTS.md, DEBT.md |
| **security-scanning** | CodeQL analysis, OpenSSF Scorecard |
| **github-templates** | Bug report, feature request, issue config, PR template |
| **review-system** | Code review and security review workflows |
| **quality-gates** | Quality metrics baseline, test parity map |
| **code-hygiene** | CONTRIBUTING.md |
| **release-pipeline** | SLSA L3 build workflow, release dispatcher, changelog config |

`nboot new` applies **scaffold** + **base**. All other packs are elective --- layer them on with `nboot apply`.

---

## Six-stage pipeline

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

Stages 0--3 are pure functions --- spec and pack in, rendered files out, no side effects. All project-specific opinions live in the spec and the template pack, never in the engine.

---

## Documentation

| Section | What you'll find |
|---------|-----------------|
| **[Quickstart](getting-started/quickstart.md)** | Install, create your first project, layer on packs |
| **[Architecture](explanation/architecture.md)** | Six-stage pipeline, spec+pack design, determinism guarantees |
| **[Security Model](explanation/security-model.md)** | Sandboxing, adversarial testing, trust model |
| **[Contributing](how-to/contributing.md)** | Development setup, testing, PR process |
| **[CLI Reference](reference/cli.md)** | All 7 commands with options and examples |
| **[Pack Catalog](reference/packs.md)** | All 8 packs with templates, conditions, dependencies |
| **[Changelog](reference/changelog.md)** | Release history |
