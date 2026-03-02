# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Project Navi

"""Pack discovery and resolution."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml


class PackError(Exception):
    """Raised when a pack cannot be found or resolved."""


@dataclass
class PackInfo:
    """Metadata about a bundled pack."""

    name: str
    version: str
    description: str
    path: Path


def bundled_packs_dir() -> Path | None:
    """Find the bundled packs directory, or None if not available."""
    # Installed wheel: navi_bootstrap/packs/
    pkg_path = Path(__file__).parent / "packs"
    if pkg_path.is_dir():
        return pkg_path
    # Editable install: repo_root/packs/
    dev_path = Path(__file__).parent.parent.parent / "packs"
    if dev_path.is_dir():
        return dev_path
    return None


def resolve_pack(pack_arg: str) -> Path:
    """Resolve a pack name or filesystem path to a directory Path.

    Resolution order:
    1. If it looks like a path (contains / or \\ or starts with .), treat as filesystem path.
    2. Otherwise, try as a bundled pack name.
    3. If neither works, raise PackError with available names.
    """
    if "/" in pack_arg or "\\" in pack_arg or pack_arg.startswith("."):
        path = Path(pack_arg)
        if not path.is_dir():
            msg = f"Pack directory not found: {pack_arg}"
            raise PackError(msg)
        return path

    packs_dir = bundled_packs_dir()
    if packs_dir is not None:
        candidate = packs_dir / pack_arg
        if candidate.is_dir():
            return candidate

    available = [p.name for p in _list_pack_dirs()]
    if available:
        names = ", ".join(sorted(available))
        msg = f"Unknown pack {pack_arg!r}. Available packs: {names}"
    else:
        msg = f"Unknown pack {pack_arg!r} and no bundled packs found."
    raise PackError(msg)


def list_packs() -> list[PackInfo]:
    """Enumerate all bundled packs with metadata from their manifests."""
    results: list[PackInfo] = []
    for pack_dir in _list_pack_dirs():
        manifest_path = pack_dir / "manifest.yaml"
        if not manifest_path.exists():
            continue
        try:
            data = yaml.safe_load(manifest_path.read_text())
        except yaml.YAMLError:
            continue
        if not isinstance(data, dict):
            continue
        results.append(
            PackInfo(
                name=data.get("name", pack_dir.name),
                version=data.get("version", "unknown"),
                description=data.get("description", "").strip(),
                path=pack_dir,
            )
        )
    return sorted(results, key=lambda p: p.name)


PACK_ORDER: list[str] = ["scaffold", "base"]


def get_ordered_packs(names: list[str] | None = None) -> list[Path]:
    """Return pack directories in render order.

    If *names* is ``None``, the default :data:`PACK_ORDER` is used.
    Each name is resolved via :func:`resolve_pack`.
    """
    order = names if names is not None else PACK_ORDER
    return [resolve_pack(name) for name in order]


def _list_pack_dirs() -> list[Path]:
    """Return all pack directories from the bundled packs location."""
    packs_dir = bundled_packs_dir()
    if packs_dir is None:
        return []
    return [p for p in sorted(packs_dir.iterdir()) if p.is_dir()]
