# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Project Navi

"""Tests for the hand-rolled SARIF 2.1.0 emitter."""

from __future__ import annotations

import json

import pytest

from navi_bootstrap.sarif import (
    AUDIT_RULES,
    SARIF_SCHEMA_URI,
    SARIF_VERSION,
    SarifReport,
    SarifResult,
)


class TestSarifResult:
    def test_fingerprint_is_stable(self) -> None:
        r1 = SarifResult(rule_id="pack-drift-changed", message="x", artifact_uri="a/b.py")
        r2 = SarifResult(
            rule_id="pack-drift-changed", message="different msg", artifact_uri="a/b.py"
        )
        # Fingerprints must ignore message text to survive wording tweaks
        assert r1.fingerprint() == r2.fingerprint()

    def test_fingerprint_differs_for_different_files(self) -> None:
        r1 = SarifResult(rule_id="pack-drift-changed", message="x", artifact_uri="a.py")
        r2 = SarifResult(rule_id="pack-drift-changed", message="x", artifact_uri="b.py")
        assert r1.fingerprint() != r2.fingerprint()

    def test_fingerprint_differs_for_different_rules(self) -> None:
        r1 = SarifResult(rule_id="pack-drift-missing", message="x", artifact_uri="a.py")
        r2 = SarifResult(rule_id="pack-drift-changed", message="x", artifact_uri="a.py")
        assert r1.fingerprint() != r2.fingerprint()

    def test_to_dict_shape(self) -> None:
        r = SarifResult(rule_id="pack-drift-missing", message="hi", artifact_uri="x/y.yml")
        d = r.to_dict()
        assert d["ruleId"] == "pack-drift-missing"
        assert d["level"] == "warning"
        assert d["message"]["text"] == "hi"
        assert d["locations"][0]["physicalLocation"]["artifactLocation"]["uri"] == "x/y.yml"
        assert "primaryLocationLineHash" in d["partialFingerprints"]


class TestSarifReport:
    def test_empty_report_valid_shape(self) -> None:
        report = SarifReport(tool_name="nboot-audit", tool_version="0.1.2")
        d = report.to_dict()
        assert d["$schema"] == SARIF_SCHEMA_URI
        assert d["version"] == SARIF_VERSION
        assert len(d["runs"]) == 1
        assert d["runs"][0]["tool"]["driver"]["name"] == "nboot-audit"
        assert d["runs"][0]["tool"]["driver"]["version"] == "0.1.2"
        assert d["runs"][0]["results"] == []

    def test_rules_are_declared_on_driver(self) -> None:
        report = SarifReport(tool_name="nboot-audit", tool_version="0.1.2")
        rule_ids = {r["id"] for r in report.to_dict()["runs"][0]["tool"]["driver"]["rules"]}
        assert rule_ids == {"pack-drift-missing", "pack-drift-changed"}

    def test_rule_metadata_has_required_sarif_fields(self) -> None:
        for rule in AUDIT_RULES:
            assert "id" in rule
            assert "name" in rule
            assert "shortDescription" in rule and "text" in rule["shortDescription"]
            assert rule["defaultConfiguration"]["level"] == "warning"

    def test_add_result_rejects_unknown_rule(self) -> None:
        report = SarifReport(tool_name="nboot-audit", tool_version="0.1.2")
        bad = SarifResult(rule_id="made-up", message="x", artifact_uri="a.py")
        with pytest.raises(ValueError, match="Unknown SARIF rule id"):
            report.add_result(bad)

    def test_add_result_accepts_known_rule(self) -> None:
        report = SarifReport(tool_name="nboot-audit", tool_version="0.1.2")
        report.add_result(SarifResult(rule_id="pack-drift-missing", message="m", artifact_uri="a"))
        report.add_result(SarifResult(rule_id="pack-drift-changed", message="m", artifact_uri="b"))
        assert len(report.to_dict()["runs"][0]["results"]) == 2

    def test_to_json_is_valid_json_and_round_trips(self) -> None:
        report = SarifReport(tool_name="nboot-audit", tool_version="0.1.2")
        report.add_result(SarifResult(rule_id="pack-drift-missing", message="m", artifact_uri="a"))
        parsed = json.loads(report.to_json())
        assert parsed == report.to_dict()

    def test_to_json_schema_hint_present(self) -> None:
        # GitHub's SARIF upload accepts reports without $schema but tooling
        # is happier when it's there.
        report = SarifReport(tool_name="nboot-audit", tool_version="0.1.2")
        assert "$schema" in json.loads(report.to_json())
