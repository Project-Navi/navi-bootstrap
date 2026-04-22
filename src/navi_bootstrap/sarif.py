# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Project Navi

"""SARIF 2.1.0 emitter for nboot audit output.

Hand-rolled to avoid adding a runtime dependency. Produces GitHub-compatible
SARIF that lands in the Security tab when uploaded via
github/codeql-action/upload-sarif.

Only the subset we need is implemented:
  - One run per report
  - One tool driver with pre-declared rules
  - Per-finding result with physicalLocation artifactLocation
  - partialFingerprints for cross-run deduplication
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any

SARIF_SCHEMA_URI = (
    "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json"
)
SARIF_VERSION = "2.1.0"

TOOL_INFORMATION_URI = "https://github.com/Project-Navi/navi-bootstrap"

# Rule registry — every audit finding must cite one of these rule IDs.
AUDIT_RULES: tuple[dict[str, Any], ...] = (
    {
        "id": "pack-drift-missing",
        "name": "PackDriftMissing",
        "shortDescription": {
            "text": "File is expected by the pack but missing from the target.",
        },
        "fullDescription": {
            "text": (
                "The target project is missing a file the conformance pack "
                "would render. Run `nboot apply --pack <name> --target <path>` "
                "to create it, or mark the pack as optional for this project."
            ),
        },
        "helpUri": "https://github.com/Project-Navi/navi-bootstrap/blob/main/docs/reference/audit.md",
        "defaultConfiguration": {"level": "warning"},
    },
    {
        "id": "pack-drift-changed",
        "name": "PackDriftChanged",
        "shortDescription": {
            "text": "File content differs from what the pack would render.",
        },
        "fullDescription": {
            "text": (
                "The target project has a file whose content no longer matches "
                "the conformance pack. Review `nboot diff --pack <name> --target <path>` "
                "for the unified diff; `nboot apply` will overwrite (create mode) "
                "or merge (append mode)."
            ),
        },
        "helpUri": "https://github.com/Project-Navi/navi-bootstrap/blob/main/docs/reference/audit.md",
        "defaultConfiguration": {"level": "warning"},
    },
)


@dataclass
class SarifResult:
    """A single SARIF result — one audit finding."""

    rule_id: str
    message: str
    artifact_uri: str
    level: str = "warning"

    def fingerprint(self) -> str:
        """Stable hash for cross-run deduplication in the GitHub UI."""
        basis = f"{self.rule_id}:{self.artifact_uri}"
        return hashlib.sha256(basis.encode("utf-8")).hexdigest()

    def to_dict(self) -> dict[str, Any]:
        return {
            "ruleId": self.rule_id,
            "level": self.level,
            "message": {"text": self.message},
            "locations": [
                {
                    "physicalLocation": {
                        "artifactLocation": {"uri": self.artifact_uri},
                    },
                },
            ],
            "partialFingerprints": {
                "primaryLocationLineHash": self.fingerprint(),
            },
        }


@dataclass
class SarifReport:
    """A SARIF 2.1.0 report — one tool run + N results."""

    tool_name: str
    tool_version: str
    results: list[SarifResult] = field(default_factory=list)
    rules: tuple[dict[str, Any], ...] = AUDIT_RULES

    def add_result(self, result: SarifResult) -> None:
        # Defensive: reject results referencing unknown rules rather than emitting
        # invalid SARIF that GitHub would silently drop.
        known_ids = {rule["id"] for rule in self.rules}
        if result.rule_id not in known_ids:
            raise ValueError(
                f"Unknown SARIF rule id {result.rule_id!r}; expected one of {sorted(known_ids)}"
            )
        self.results.append(result)

    def to_dict(self) -> dict[str, Any]:
        return {
            "$schema": SARIF_SCHEMA_URI,
            "version": SARIF_VERSION,
            "runs": [
                {
                    "tool": {
                        "driver": {
                            "name": self.tool_name,
                            "version": self.tool_version,
                            "informationUri": TOOL_INFORMATION_URI,
                            "rules": list(self.rules),
                        },
                    },
                    "results": [r.to_dict() for r in self.results],
                },
            ],
        }

    def to_json(self, *, indent: int | None = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, sort_keys=False)
