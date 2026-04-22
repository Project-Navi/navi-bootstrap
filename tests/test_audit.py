# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Project Navi

"""Tests for the pack-conformance audit pipeline."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest
from click.testing import CliRunner

from navi_bootstrap.audit import (
    AuditError,
    AuditFinding,
    findings_to_sarif,
    findings_to_text,
    run_audit,
)
from navi_bootstrap.cli import cli

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _write_spec(tmp_path: Path) -> Path:
    """Write a minimal but complete spec that scaffold / base will render against."""
    spec = tmp_path / "nboot-spec.json"
    spec.write_text(
        json.dumps(
            {
                "name": "audit-fixture",
                "version": "0.0.1",
                "description": "Fixture project for audit tests.",
                "license": "MIT",
                "language": "python",
                "python_version": "3.12",
                "author": {"name": "Test"},
                "structure": {"src_dir": "src/audit_fixture", "test_dir": "tests"},
                "dependencies": {"runtime": [], "dev": ["pytest"], "optional": {}},
                "features": {"ci": False, "pre_commit": False},
                "github": {"org": "test", "repo": "audit-fixture"},
                "release": {"has_docker": False},
                "recon": {
                    "test_framework": "pytest",
                    "test_count": 0,
                    "coverage_pct": 0,
                    "python_test_versions": ["3.12"],
                    "codeql_languages": ["python"],
                    "existing_ci": [],
                    "existing_tools": {},
                    "has_pyproject_toml": False,
                    "has_github_dir": False,
                    "updated_at": "2026-04-22T00:00:00+00:00",
                },
            }
        )
    )
    return spec


# ---------------------------------------------------------------------------
# AuditFinding unit tests
# ---------------------------------------------------------------------------


class TestAuditFinding:
    def test_missing_finding_maps_to_correct_rule(self) -> None:
        f = AuditFinding(kind="missing", dest="README.md", pack="scaffold")
        assert f.rule_id == "pack-drift-missing"
        assert "missing" in f.message.lower()
        assert "scaffold" in f.message

    def test_changed_finding_maps_to_correct_rule(self) -> None:
        f = AuditFinding(kind="changed", dest=".github/workflows/tests.yml", pack="base")
        assert f.rule_id == "pack-drift-changed"
        assert "differs" in f.message.lower()

    def test_to_sarif_result_carries_fields(self) -> None:
        f = AuditFinding(kind="missing", dest="x/y.py", pack="scaffold")
        r = f.to_sarif_result()
        assert r.rule_id == "pack-drift-missing"
        assert r.artifact_uri == "x/y.py"


# ---------------------------------------------------------------------------
# findings_to_text / findings_to_sarif unit tests
# ---------------------------------------------------------------------------


class TestFindingsToText:
    def test_empty_says_ok(self) -> None:
        out = findings_to_text([])
        assert "OK" in out

    def test_sections_group_by_kind(self) -> None:
        findings = [
            AuditFinding(kind="missing", dest="a", pack="p"),
            AuditFinding(kind="changed", dest="b", pack="p"),
            AuditFinding(kind="missing", dest="c", pack="p"),
        ]
        out = findings_to_text(findings)
        assert "Missing files (2)" in out
        assert "Changed files (1)" in out
        assert "- a" in out
        assert "- b" in out
        assert "- c" in out


class TestFindingsToSarif:
    def test_empty_produces_valid_report(self) -> None:
        r = findings_to_sarif([], tool_name="t", tool_version="v")
        d = r.to_dict()
        assert d["runs"][0]["results"] == []
        assert d["runs"][0]["tool"]["driver"]["name"] == "t"

    def test_findings_appear_as_results(self) -> None:
        findings = [
            AuditFinding(kind="missing", dest="a.py", pack="scaffold"),
            AuditFinding(kind="changed", dest="b.py", pack="scaffold"),
        ]
        r = findings_to_sarif(findings, tool_name="nboot-audit", tool_version="0.1.2")
        results = r.to_dict()["runs"][0]["results"]
        assert len(results) == 2
        assert {r["ruleId"] for r in results} == {"pack-drift-missing", "pack-drift-changed"}


# ---------------------------------------------------------------------------
# run_audit — end-to-end against real packs
# ---------------------------------------------------------------------------


class TestRunAudit:
    def test_empty_target_flags_every_pack_file_as_missing(self, tmp_path: Path) -> None:
        spec = _write_spec(tmp_path)
        target = tmp_path / "empty-target"
        target.mkdir()

        findings = run_audit(spec, "scaffold", target, skip_resolve=True)

        assert findings  # scaffold has at least pyproject.toml + README + LICENSE
        assert all(f.kind == "missing" for f in findings)
        assert all(f.pack == "scaffold" for f in findings)

    def test_conforming_target_has_no_findings(self, tmp_path: Path) -> None:
        # Run nboot new to produce a conforming project, then audit it against
        # scaffold — expect zero findings (full conformance).
        spec = _write_spec(tmp_path)
        target = tmp_path / "conforming"
        subprocess.run(
            [
                "uv",
                "run",
                "nboot",
                "apply",
                "--spec",
                str(spec),
                "--pack",
                "scaffold",
                "--target",
                str(target),
                "--skip-resolve",
            ],
            check=False,
            capture_output=True,
            cwd=Path(__file__).resolve().parents[1],
        )
        # Engine's apply refuses to write to a non-existent target, so pre-create.
        # Instead we use render/apply via the engine directly:
        from navi_bootstrap.engine import plan, render_to_files, write_rendered
        from navi_bootstrap.manifest import load_manifest
        from navi_bootstrap.packs import resolve_pack
        from navi_bootstrap.sanitize import sanitize_manifest, sanitize_spec
        from navi_bootstrap.spec import load_spec

        target.mkdir()
        pack_dir = resolve_pack("scaffold")
        spec_data = sanitize_spec(load_spec(spec))
        manifest = sanitize_manifest(load_manifest(pack_dir / "manifest.yaml"))
        render_plan = plan(manifest, spec_data, pack_dir / "templates")
        rendered = render_to_files(
            render_plan,
            spec_data,
            pack_dir / "templates",
            action_shas={},
            action_versions={},
        )
        write_rendered(rendered, target, pack_name="scaffold")

        findings = run_audit(spec, "scaffold", target, skip_resolve=True)
        assert findings == [], f"Expected full conformance, got drift: {findings}"

    def test_single_drift_reported_as_changed(self, tmp_path: Path) -> None:
        # Render scaffold, mutate one file, audit — expect exactly one "changed".
        from navi_bootstrap.engine import plan, render_to_files, write_rendered
        from navi_bootstrap.manifest import load_manifest
        from navi_bootstrap.packs import resolve_pack
        from navi_bootstrap.sanitize import sanitize_manifest, sanitize_spec
        from navi_bootstrap.spec import load_spec

        spec = _write_spec(tmp_path)
        target = tmp_path / "drifted"
        target.mkdir()

        pack_dir = resolve_pack("scaffold")
        spec_data = sanitize_spec(load_spec(spec))
        manifest = sanitize_manifest(load_manifest(pack_dir / "manifest.yaml"))
        render_plan = plan(manifest, spec_data, pack_dir / "templates")
        rendered = render_to_files(
            render_plan,
            spec_data,
            pack_dir / "templates",
            action_shas={},
            action_versions={},
        )
        write_rendered(rendered, target, pack_name="scaffold")

        # Introduce drift
        readme = target / "README.md"
        readme.write_text(readme.read_text() + "\n\n<!-- drifted -->\n")

        findings = run_audit(spec, "scaffold", target, skip_resolve=True)
        changed = [f for f in findings if f.kind == "changed"]
        assert any(f.dest == "README.md" for f in changed), findings

    def test_unknown_pack_raises_audit_error(self, tmp_path: Path) -> None:
        spec = _write_spec(tmp_path)
        target = tmp_path
        with pytest.raises(AuditError):
            run_audit(spec, "no-such-pack-here", target, skip_resolve=True)


# ---------------------------------------------------------------------------
# CLI integration
# ---------------------------------------------------------------------------


class TestAuditCli:
    def test_text_format_default(self, tmp_path: Path) -> None:
        spec = _write_spec(tmp_path)
        target = tmp_path / "target"
        target.mkdir()
        runner = CliRunner()
        result = runner.invoke(
            cli,
            ["audit", "--spec", str(spec), "--pack", "scaffold", "--target", str(target)],
        )
        # Drift present -> exit 1 by default
        assert result.exit_code == 1
        assert "drift" in result.output.lower() or "missing" in result.output.lower()

    def test_sarif_format_produces_valid_json(self, tmp_path: Path) -> None:
        spec = _write_spec(tmp_path)
        target = tmp_path / "target"
        target.mkdir()
        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "audit",
                "--spec",
                str(spec),
                "--pack",
                "scaffold",
                "--target",
                str(target),
                "--format",
                "sarif",
            ],
        )
        assert result.exit_code == 1  # drift -> exit 1
        parsed = json.loads(result.output)
        assert parsed["version"] == "2.1.0"
        assert parsed["runs"][0]["tool"]["driver"]["name"] == "nboot-audit"
        assert parsed["runs"][0]["results"]

    def test_exit_zero_flag_allows_success_with_drift(self, tmp_path: Path) -> None:
        spec = _write_spec(tmp_path)
        target = tmp_path / "target"
        target.mkdir()
        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "audit",
                "--spec",
                str(spec),
                "--pack",
                "scaffold",
                "--target",
                str(target),
                "--exit-zero",
            ],
        )
        assert result.exit_code == 0
        assert "drift" in result.output.lower() or "missing" in result.output.lower()

    def test_output_file_written(self, tmp_path: Path) -> None:
        spec = _write_spec(tmp_path)
        target = tmp_path / "target"
        target.mkdir()
        out_file = tmp_path / "report.sarif.json"
        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "audit",
                "--spec",
                str(spec),
                "--pack",
                "scaffold",
                "--target",
                str(target),
                "--format",
                "sarif",
                "--output",
                str(out_file),
            ],
        )
        assert result.exit_code == 1  # drift found
        assert out_file.exists()
        parsed = json.loads(out_file.read_text())
        assert parsed["version"] == "2.1.0"
