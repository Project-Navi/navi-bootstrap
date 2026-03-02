# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Project Navi

"""Spec loading and JSON Schema validation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, cast

import jsonschema


def _find_schema(filename: str) -> Path:
    """Find schema file — works in both installed wheel and editable install."""
    # Installed wheel: navi_bootstrap/schema/
    pkg_path = Path(__file__).parent / "schema" / filename
    if pkg_path.exists():
        return pkg_path
    # Editable install: repo_root/schema/
    dev_path = Path(__file__).parent.parent.parent / "schema" / filename
    if dev_path.exists():
        return dev_path
    msg = f"Schema not found: {filename}"
    raise FileNotFoundError(msg)


class SpecError(Exception):
    """Raised when a spec is invalid or cannot be loaded."""


def _load_schema() -> dict[str, Any]:
    """Load the JSON Schema for spec validation."""
    return cast(dict[str, Any], json.loads(_find_schema("spec-schema.json").read_text()))


def validate_spec(spec: dict[str, Any]) -> None:
    """Validate a spec dict against the JSON Schema. Raises SpecError on failure."""
    schema = _load_schema()
    try:
        jsonschema.validate(instance=spec, schema=schema)
    except jsonschema.ValidationError as e:
        raise SpecError(f"Spec validation failed: {e.message}") from e


def load_spec(path: Path) -> dict[str, Any]:
    """Load and validate a spec from a JSON file. Returns the spec dict."""
    if not path.exists():
        raise SpecError(f"Spec file not found: {path}")
    try:
        spec = json.loads(path.read_text())
    except json.JSONDecodeError as e:
        raise SpecError(f"Failed to parse spec JSON: {e}") from e
    validate_spec(spec)
    return cast(dict[str, Any], spec)


def build_spec_for_new(
    name: str,
    *,
    description: str = "",
    license_id: str = "MIT",
    python_version: str = "3.12",
    author_name: str = "",
) -> dict[str, Any]:
    """Build a valid spec dict for a greenfield project from CLI arguments.

    Constructs a complete spec without reading pyproject.toml or inspecting an
    existing project.  The returned dict is validated against the JSON Schema
    before being returned.

    Args:
        name: Project name (required, non-empty).
        description: One-line project description.
        license_id: SPDX license identifier (default ``"MIT"``).
        python_version: Minimum Python version (default ``"3.12"``).
        author_name: Author display name; omitted from spec when empty.

    Returns:
        A spec dict that passes :func:`validate_spec`.

    Raises:
        SpecError: If the constructed spec fails schema validation.
    """
    pkg_dir = name.replace("-", "_")

    spec: dict[str, Any] = {
        "name": name,
        "version": "0.1.0",
        "language": "python",
        "python_version": python_version,
        "description": description,
        "structure": {
            "src_dir": f"src/{pkg_dir}",
            "test_dir": "tests",
        },
        "dependencies": {
            "runtime": [],
            "dev": ["pytest>=8.0", "ruff>=0.4", "mypy>=1.10"],
        },
        "features": {
            "ci": True,
            "pre_commit": True,
        },
    }

    if license_id:
        spec["license"] = license_id

    if author_name:
        spec["author"] = {"name": author_name}

    validate_spec(spec)
    return spec
