# OpenSSF Best Practices — Passing-level Checklist

> Working checklist for the OpenSSF (CII) Best Practices Passing badge.
> Form at <https://www.bestpractices.dev/en/projects/new>.
>
> Source of truth: `criteria/criteria.yml` + `config/locales/en.yml`
> on [`main` of `coreinfrastructure/best-practices-badge`](https://github.com/coreinfrastructure/best-practices-badge).
> 67 Passing-level criteria across 6 categories.

**Legend**
- **MUST** — absolute requirement; Met or documented N/A
- **SHOULD** — normally required; exceptions permitted with justification
- **SUGGESTED** — recommended; any answer accepted
- Per-criterion status: `[x] Met` / `[ ] Unmet` / `[N/A]` / `[?] Unknown` / `[TODO]` human decision needed

---

## Project form fields

| Field | Proposed answer |
|---|---|
| `project_name` | navi-bootstrap |
| `description` | Jinja2 rendering engine and template packs for bootstrapping projects |
| `entry_locale` | en |
| `homepage_url` | https://project-navi.github.io/navi-bootstrap/ |
| `repo_url` | https://github.com/Project-Navi/navi-bootstrap |
| `implementation_languages` | Python |
| `additional_rights_changes` | — |

---

## Basics

### Basic project website content

- [x] **`description_good`** (MUST) — Project website succinctly describes what the software does.
  - Evidence: `README.md` top matter + homepage hero.

- [x] **`interact`** (MUST) — Information on how to obtain, provide feedback, and contribute.
  - Evidence: `README.md` Quick-start + `CONTRIBUTING.md`; GitHub Issues/PRs linked.

- [x] **`contribution`** (MUST) — Contribution process is documented (URL required).
  - Evidence: `CONTRIBUTING.md` at repo root.
  - URL: `https://github.com/Project-Navi/navi-bootstrap/blob/main/CONTRIBUTING.md`

- [x] **`contribution_requirements`** (SHOULD) — Requirements for acceptable contributions (coding standard, etc.).
  - Evidence: `CONTRIBUTING.md` references conventional commits, ruff, mypy, pre-commit, 80% test coverage.

### FLOSS license

- [x] **`floss_license`** (MUST) — Software released as FLOSS.
  - Evidence: MIT license, SPDX-approved.

- [x] **`floss_license_osi`** (SUGGESTED) — License is OSI-approved.
  - Evidence: MIT is OSI-approved.

- [x] **`license_location`** (MUST) — License posted in a standard location (URL required).
  - Evidence: `LICENSE` at repo root.
  - URL: `https://github.com/Project-Navi/navi-bootstrap/blob/main/LICENSE`

### Documentation

- [x] **`documentation_basics`** (MUST) — Basic documentation: install, start, use, use-securely.
  - Evidence: `README.md` Quick-start; zensical docs site under `/docs`.
  - URL: `https://project-navi.github.io/navi-bootstrap/`

- [x] **`documentation_interface`** (MUST) — Reference documentation of external interface (API, CLI).
  - Evidence: `nboot --help` (Click auto-generated); `docs/reference/cli-reference.md`.

### Other

- [x] **`sites_https`** (MUST) — Project sites support HTTPS.
  - Evidence: github.com (HTTPS), project-navi.github.io (HTTPS via GitHub Pages).

- [x] **`discussion`** (MUST) — Searchable, URL-addressable discussion mechanism.
  - Evidence: GitHub Issues + PR conversations.

- [x] **`english`** (SHOULD) — Documentation in English; accepts English bug reports.
  - Evidence: All repo content is English.

- [x] **`maintained`** (MUST) — Project is maintained.
  - Evidence: Active commit history; this checklist itself is evidence of active maintenance.

---

## Change Control

### Public version-controlled source repository

- [x] **`repo_public`** (MUST) — Public version-controlled source repository with URL.
  - URL: `https://github.com/Project-Navi/navi-bootstrap`

- [x] **`repo_track`** (MUST) — Repository tracks who/when/what of changes.
  - Evidence: Git (repo is on GitHub).

- [x] **`repo_interim`** (MUST) — Interim versions between releases, not just final releases.
  - Evidence: Regular commits on `main`; PRs for every change.

- [x] **`repo_distributed`** (SUGGESTED) — Common distributed VCS used.
  - Evidence: git.

### Unique version numbering

- [x] **`version_unique`** (MUST) — Unique version identifier per release.
  - Evidence: `pyproject.toml` version (`0.1.2`); git tags per release.

- [x] **`version_semver`** (SUGGESTED) — SemVer or CalVer used.
  - Evidence: SemVer (`0.1.2`).

- [x] **`version_tags`** (SUGGESTED) — Releases identified via VCS tags.
  - Evidence: `release.yml` workflow creates git tags for each release.

### Release notes

- [TODO] **`release_notes`** (MUST) — Human-readable release notes per release (URL required).
  - Status: `cliff.toml` configured for git-cliff changelog generation.
  - Action: confirm `CHANGELOG.md` is auto-generated on release OR mark N/A if using continuous delivery.
  - URL once in place: `https://github.com/Project-Navi/navi-bootstrap/blob/main/CHANGELOG.md`

- [?] **`release_notes_vulns`** (MUST) — Release notes identify publicly-known vulnerabilities fixed.
  - Status: No public vulnerabilities have been disclosed against this project yet. Answer N/A until first vuln-fix release.

---

## Reporting

### Bug-reporting process

- [x] **`report_process`** (MUST) — Process for submitting bug reports (URL required).
  - URL: `https://github.com/Project-Navi/navi-bootstrap/issues/new/choose`

- [x] **`report_tracker`** (SHOULD) — Issue tracker used.
  - Evidence: GitHub Issues.

- [TODO] **`report_responses`** (MUST) — Majority of bug reports in last 2-12 months acknowledged.
  - Action: audit issue responsiveness; note the ratio.

- [TODO] **`enhancement_responses`** (SHOULD) — Majority of enhancement requests in last 2-12 months responded to.
  - Action: audit enhancement-label issues.

- [x] **`report_archive`** (MUST) — Publicly available archive (URL required).
  - URL: `https://github.com/Project-Navi/navi-bootstrap/issues?q=is%3Aissue`

### Vulnerability report process

- [x] **`vulnerability_report_process`** (MUST) — Process published (URL required).
  - Evidence: `SECURITY.md` at repo root.
  - URL: `https://github.com/Project-Navi/navi-bootstrap/blob/main/SECURITY.md`

- [TODO] **`vulnerability_report_private`** (MUST) — Private reporting mechanism documented.
  - Action: confirm GitHub's "Private vulnerability reporting" is enabled under repo Settings → Security. If enabled, the URL is `https://github.com/Project-Navi/navi-bootstrap/security/advisories/new`.

- [N/A] **`vulnerability_report_response`** (MUST) — Initial response ≤14 days for reports in last 6 months.
  - Status: No vulnerability reports received in last 6 months.

---

## Quality

### Working build system

- [x] **`build`** (MUST) — Working build system (or N/A).
  - Evidence: `hatchling` builds the wheel from source.

- [x] **`build_common_tools`** (SUGGESTED) — Common tools used.
  - Evidence: `hatchling`, standard PEP-517 pattern.

- [x] **`build_floss_tools`** (SHOULD) — Buildable using only FLOSS tools.
  - Evidence: `hatchling`, `uv`, Python — all FLOSS.

### Automated test suite

- [x] **`test`** (MUST) — At least one FLOSS automated test suite documented.
  - Evidence: `pytest` with tests under `tests/`; CLAUDE.md documents invocation.

- [x] **`test_invocation`** (SHOULD) — Invocable in standard way for the language.
  - Evidence: `uv run pytest tests/` (documented in `CLAUDE.md`, `README.md`).

- [x] **`test_most`** (SUGGESTED) — Test suite covers most code branches/input fields.
  - Evidence: 93% coverage (per `nboot-spec.json:recon.coverage_pct`); 378 tests.

- [x] **`test_continuous_integration`** (SUGGESTED) — CI runs tests on every change.
  - Evidence: `.github/workflows/tests.yml` on every PR + main push.

### New functionality testing

- [x] **`test_policy`** (MUST) — Policy that major new functionality gets tests.
  - Evidence: `CONTRIBUTING.md` + pre-commit hooks require tests; quality-gate workflow enforces coverage.

- [x] **`tests_are_added`** (MUST) — Evidence of policy being followed in recent changes.
  - Evidence: Every recent PR (#41, #42, #46–49) added tests alongside code changes.

- [x] **`tests_documented_added`** (SUGGESTED) — Policy documented in change-proposal instructions.
  - Evidence: `CONTRIBUTING.md` describes TDD expectation; PR template requests a test plan.

### Warning flags

- [x] **`warnings`** (MUST) — Compiler warnings / safe mode / linter enabled.
  - Evidence: `ruff` (`E, F, I, N, W, UP, B, RUF, C4`); `mypy --strict`; bandit; detect-secrets; gitleaks.

- [x] **`warnings_fixed`** (MUST) — Warnings are addressed.
  - Evidence: CI fails on ruff/mypy/bandit issues; branch is required to be clean before merge.

- [x] **`warnings_strict`** (SUGGESTED) — Maximally strict warnings where practical.
  - Evidence: `mypy --strict`, broad `ruff` rule-set, pre-commit gates, `insert-license` header enforcement.

---

## Security

### Secure development knowledge

- [TODO] **`know_secure_design`** (MUST) — At least one primary developer knows secure-design principles (Saltzer & Schroeder 8 + limited attack surface + input-validation allowlists).
  - Self-certify. User decision.

- [TODO] **`know_common_errors`** (MUST) — Primary developer knows common vulnerability classes + mitigations.
  - Self-certify. User decision (OWASP Top 10, CWE/SANS 25 familiarity).

### Use basic good cryptographic practices

- [N/A] **`crypto_published`** (MUST) — Only publicly published/reviewed crypto.
  - Status: navi-bootstrap does not implement or call into cryptographic primitives directly. Rendering engine only.

- [N/A] **`crypto_call`** (SHOULD) — Calls only established crypto libraries.
  - Status: not applicable (no crypto).

- [N/A] **`crypto_floss`** (MUST) — Crypto dependencies are FLOSS-implementable.
  - Status: not applicable.

- [N/A] **`crypto_keylength`** (MUST) — Keylengths meet NIST-2030 minimums.
  - Status: not applicable.

- [N/A] **`crypto_working`** (MUST) — No dependence on broken algorithms.
  - Status: not applicable.

- [N/A] **`crypto_weaknesses`** (SHOULD) — No dependence on weak algorithms.
  - Status: not applicable.

- [N/A] **`crypto_pfs`** (SHOULD) — Perfect forward secrecy for key-agreement.
  - Status: not applicable.

- [N/A] **`crypto_password_storage`** (MUST) — Iterated salted hashing for stored passwords.
  - Status: not applicable (no password handling).

- [N/A] **`crypto_random`** (MUST) — CSPRNG for keys/nonces.
  - Status: not applicable.

### Secured delivery against MITM

- [x] **`delivery_mitm`** (MUST) — Delivery mechanism counters MITM (HTTPS / ssh+scp / signed packages).
  - Evidence: PyPI over HTTPS; SLSA L3 signed releases via `release.yml`.

- [x] **`delivery_unsigned`** (MUST) — Cryptographic hashes not retrieved over HTTP-without-signature.
  - Evidence: All third-party actions pinned to commit SHAs; dependencies resolved via `uv.lock` with hashes.

### Publicly known vulnerabilities fixed

- [x] **`vulnerabilities_fixed_60_days`** (MUST) — No unpatched medium+ vulns public >60 days.
  - Evidence: Dependabot alerts — DB#3 (pytest) fixed via #47; DB#2 (Pygments) fix in flight via #49; no remaining unpatched vulns.

- [x] **`vulnerabilities_critical_fixed`** (SHOULD) — Critical vulns fixed rapidly.
  - Evidence: No critical-severity vulnerabilities reported.

### Other security issues

- [x] **`no_leaked_credentials`** (MUST) — No valid private credentials leaked.
  - Evidence: detect-secrets baseline scan (pre-commit); gitleaks scan (pre-commit + CI). `.gitleaks.toml` allowlists baseline-fingerprint file only.

---

## Analysis

### Static code analysis

- [x] **`static_analysis`** (MUST) — Static analysis tool applied to major production releases (justification required).
  - Evidence: CodeQL (`codeql.yml`), Semgrep (`semgrep.yml` with `p/python` + `p/owasp-top-ten`), bandit (pre-commit + `tests.yml`), ruff.

- [x] **`static_analysis_common_vulnerabilities`** (SUGGESTED) — SAST rules look for common vuln classes.
  - Evidence: Semgrep `p/owasp-top-ten` ruleset; CodeQL security-extended queries.

- [x] **`static_analysis_fixed`** (MUST) — Medium+ exploitable findings fixed timely.
  - Evidence: #49 addresses Semgrep findings #41, #42. Other SAST findings triaged and dismissed with justification in security dashboard.

- [x] **`static_analysis_often`** (SUGGESTED) — Runs on every commit or daily.
  - Evidence: CodeQL + Semgrep on every PR and main push.

### Dynamic code analysis

- [x] **`dynamic_analysis`** (SUGGESTED) — Dynamic analysis on major releases.
  - Evidence: atheris fuzz harness under `fuzz/fuzz_sanitize.py`; `fuzz.yml` runs on every PR.

- [N/A] **`dynamic_analysis_unsafe`** (SUGGESTED) — Memory-safety sanitizer for memory-unsafe languages.
  - Status: Python is memory-safe (no C/C++/Rust/etc.).

- [TODO] **`dynamic_analysis_enable_assertions`** (SUGGESTED) — Dynamic analysis with assertions enabled.
  - Action: confirm pytest runs with `__debug__ == True` (Python default); document if so.

- [x] **`dynamic_analysis_fixed`** (MUST) — Medium+ dynamic-analysis findings fixed timely.
  - Evidence: No outstanding dynamic-analysis findings; fuzz harness reports via `fuzz.yml`.

---

## Residual TODOs (before submitting)

| Criterion | Action |
|---|---|
| `release_notes` | Confirm `CHANGELOG.md` is generated on release, or answer N/A if using continuous delivery |
| `release_notes_vulns` | Mark N/A (no public vulns fixed yet) |
| `report_responses` | Audit issue-ack ratio for last 2-12 months |
| `enhancement_responses` | Audit enhancement-response ratio for last 2-12 months |
| `vulnerability_report_private` | Enable GitHub "Private vulnerability reporting" under Settings → Security → Code security and analysis |
| `know_secure_design` | Self-certify familiarity with Saltzer & Schroeder + extensions |
| `know_common_errors` | Self-certify familiarity with OWASP Top 10 / CWE-SANS Top 25 |
| `dynamic_analysis_enable_assertions` | Confirm assertions enabled in test runs |

---

*Submit at <https://www.bestpractices.dev/en/projects/new> once TODOs are resolved.*
