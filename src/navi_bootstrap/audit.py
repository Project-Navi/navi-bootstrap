# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Project Navi

"""Pack-conformance auditing.

Runs the engine pipeline (resolve, validate, plan, render) in memory, then
diffs the rendered output against an existing target project. Reports files
that are missing or drifted relative to the conformance pack.

Audit = diff-as-conformance-check, with structured output (SARIF or text).
Compared to `nboot diff` (human preview), audit is designed for:
  - Fleet conformance surveys (run across N repos, aggregate findings)
  - CI gating (fail a build when a repo drifts from a required pack)
  - GitHub Security tab integration via SARIF upload
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import jinja2

from navi_bootstrap.diff import DiffResult, compute_diffs
from navi_bootstrap.engine import plan, render_to_files
from navi_bootstrap.manifest import ManifestError, load_manifest
from navi_bootstrap.packs import PackError, resolve_pack
from navi_bootstrap.resolve import ResolveError, resolve_action_shas
from navi_bootstrap.sanitize import sanitize_manifest, sanitize_spec
from navi_bootstrap.sarif import SarifReport, SarifResult
from navi_bootstrap.spec import SpecError, load_spec


class AuditError(Exception):
    """Raised for any failure inside run_audit before findings can be produced."""


@dataclass(frozen=True)
class AuditFinding:
    """One audit finding — a file that's missing or drifted vs the pack.

    The `kind` field maps 1:1 to SARIF rule ids in sarif.py.
    """

    kind: str  # "missing" | "changed"
    dest: str  # path relative to target repo
    pack: str

    @property
    def rule_id(self) -> str:
        return {"missing": "pack-drift-missing", "changed": "pack-drift-changed"}[self.kind]

    @property
    def message(self) -> str:
        if self.kind == "missing":
            return (
                f"File '{self.dest}' is missing; pack '{self.pack}' would "
                f"create it. Run `nboot apply --pack {self.pack}` to remediate."
            )
        return (
            f"File '{self.dest}' differs from pack '{self.pack}'. "
            f"Run `nboot diff --pack {self.pack}` to review the drift."
        )

    def to_sarif_result(self) -> SarifResult:
        return SarifResult(
            rule_id=self.rule_id,
            message=self.message,
            artifact_uri=self.dest,
        )


def _diff_result_to_finding(diff: DiffResult, pack: str) -> AuditFinding:
    return AuditFinding(
        kind="missing" if diff.is_new else "changed",
        dest=diff.dest,
        pack=pack,
    )


def run_audit(
    spec_path: Path,
    pack: str,
    target: Path,
    *,
    skip_resolve: bool = False,
) -> list[AuditFinding]:
    """Run a pack-conformance audit against an existing project.

    Returns a list of AuditFinding (possibly empty for a fully-conforming repo).
    Raises AuditError on any pipeline-stage failure (bad spec, missing pack,
    template render error). Network operations (action-SHA resolution) can be
    skipped via ``skip_resolve=True``; this is the default for ``nboot audit``
    because conformance checks shouldn't depend on GitHub API availability.
    """
    try:
        pack_dir = resolve_pack(pack)
    except PackError as e:
        raise AuditError(str(e)) from e

    try:
        spec_data = load_spec(spec_path)
    except SpecError as e:
        raise AuditError(str(e)) from e
    spec_data = sanitize_spec(spec_data)

    try:
        manifest = load_manifest(pack_dir / "manifest.yaml")
    except ManifestError as e:
        raise AuditError(str(e)) from e
    manifest = sanitize_manifest(manifest)

    # Stage 0 — resolve action SHAs (optional for audit; offline by default).
    action_shas_config = manifest.get("action_shas", [])
    try:
        shas, versions = resolve_action_shas(action_shas_config, skip=skip_resolve)
    except ResolveError as e:
        raise AuditError(str(e)) from e

    # Stage 2 — plan.
    templates_dir = pack_dir / "templates"
    try:
        render_plan = plan(manifest, spec_data, templates_dir)
    except (jinja2.TemplateError, TypeError) as e:
        raise AuditError(f"Template planning error: {e}") from e

    # Stage 3 — render to memory (no filesystem writes).
    try:
        rendered = render_to_files(
            render_plan,
            spec_data,
            templates_dir,
            action_shas=shas,
            action_versions=versions,
        )
    except (jinja2.TemplateError, TypeError) as e:
        raise AuditError(f"Template render error: {e}") from e

    # Use the manifest's canonical pack name (what `apply` writes into append
    # marker blocks), NOT the raw CLI arg — `resolve_pack` accepts a filesystem
    # path and the two forms should not affect drift detection.
    canonical_pack_name = render_plan.pack_name

    # Diff rendered-in-memory vs existing target filesystem.
    diffs = compute_diffs(rendered, target, pack_name=canonical_pack_name)

    return [_diff_result_to_finding(d, canonical_pack_name) for d in diffs]


def findings_to_sarif(
    findings: list[AuditFinding],
    *,
    tool_name: str,
    tool_version: str,
) -> SarifReport:
    """Build a SARIF report from a list of audit findings."""
    report = SarifReport(tool_name=tool_name, tool_version=tool_version)
    for finding in findings:
        report.add_result(finding.to_sarif_result())
    return report


def findings_to_text(findings: list[AuditFinding]) -> str:
    """Human-readable audit summary.

    Used by `nboot audit` when ``--format text`` (the default).
    """
    if not findings:
        return "OK — target conforms to the pack."

    lines: list[str] = [
        f"Audit found {len(findings)} drift finding(s):",
        "",
    ]
    by_kind: dict[str, list[AuditFinding]] = {"missing": [], "changed": []}
    for f in findings:
        by_kind[f.kind].append(f)

    for label, kind in (("Missing files", "missing"), ("Changed files", "changed")):
        items = by_kind[kind]
        if not items:
            continue
        lines.append(f"{label} ({len(items)}):")
        for f in items:
            lines.append(f"  - {f.dest}")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


__all__ = [
    "AuditError",
    "AuditFinding",
    "findings_to_sarif",
    "findings_to_text",
    "run_audit",
]
