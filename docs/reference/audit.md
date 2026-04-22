# `nboot audit` — pack-conformance audit

Check whether an existing project still matches a navi-bootstrap pack, and
emit findings as either human-readable text or SARIF 2.1.0 for upload to
GitHub's Security tab.

## Why

Most templating tools (Cookiecutter, Backstage Scaffolder, Yeoman) are
**create-only** — they generate a project once, then walk away. Copier has
an `update` flow but depends on the target having been Copier-generated in
the first place.

`nboot audit` flips the problem: it re-renders a pack **in memory** and
compares the output to an existing project's files on disk. No merge, no
write, no state. You get a list of files that are missing or drifted from
the pack — the template becomes a living specification.

This is especially useful for:

- **Fleet surveys** — "which of our 100 repos still conform to the
  `security-scanning` pack?"
- **CI gates** — run `nboot audit … --format sarif` in a nightly job and
  upload via [`github/codeql-action/upload-sarif`] so drift appears in the
  Security tab alongside CodeQL and Semgrep.
- **Regression detection** — after a bulk refactor, confirm no workflow or
  pre-commit config silently fell out of conformance.

[`github/codeql-action/upload-sarif`]: https://github.com/github/codeql-action

## Usage

```bash
uv run nboot audit \
  --spec nboot-spec.json \
  --pack security-scanning \
  --target /path/to/existing/project
```

Drift is reported and the command exits non-zero so CI fails:

```
Audit found 3 drift finding(s):

Missing files (2):
  - .github/workflows/codeql.yml
  - .github/workflows/scorecard.yml

Changed files (1):
  - .github/dependabot.yml
```

## Flags

| Flag | Default | Effect |
|---|---|---|
| `--spec` | (required) | Path to the project spec JSON |
| `--pack` | (required) | Pack name to audit against (`scaffold`, `base`, `security-scanning`, …) |
| `--target` | (required) | Existing project directory to inspect |
| `--format` | `text` | `text` for humans, `sarif` for GitHub Security tab |
| `--output` | stdout | Write to a file instead of stdout (useful with `--format sarif`) |
| `--resolve` | off | Resolve action SHAs via `gh` before planning (default: offline) |
| `--exit-zero` | off | Exit 0 even when drift is found (report-only CI surveys) |

By default `audit` runs **offline** — no GitHub API calls. This lets fleet
audits run reliably from air-gapped or rate-limited environments. Pass
`--resolve` if the pack's rendered output depends on freshly-resolved
action SHAs.

## SARIF output

The SARIF 2.1.0 report declares two rules:

- `pack-drift-missing` — file expected by the pack but absent from the target
- `pack-drift-changed` — file content differs from the pack's rendered output

Each finding includes a stable `partialFingerprints.primaryLocationLineHash`
so GitHub's Security tab deduplicates across runs.

Upload it in CI:

```yaml
- name: Audit against security-scanning pack
  run: |
    uv run nboot audit \
      --spec nboot-spec.json \
      --pack security-scanning \
      --target . \
      --format sarif \
      --output audit.sarif.json \
      --exit-zero

- name: Upload audit findings
  uses: github/codeql-action/upload-sarif@v4
  with:
    sarif_file: audit.sarif.json
    category: nboot-audit
```

## Exit codes

| Exit | Meaning |
|---|---|
| 0 | Target fully conforms to the pack, OR drift found with `--exit-zero` |
| 1 | Drift found without `--exit-zero` |
| >1 | Pipeline error (bad spec, missing pack, template render failure) |

## Relationship to other verbs

| Verb | Writes? | Output | Use when |
|---|---|---|---|
| `nboot diff` | No | Unified diff text | Human preview before `apply` |
| `nboot audit` | No | Finding list / SARIF | CI gate, fleet survey, Security-tab upload |
| `nboot apply` | Yes | Files on disk | Remediate drift by overwriting / merging |

`diff` and `audit` run the same pipeline; they differ in output shape.
