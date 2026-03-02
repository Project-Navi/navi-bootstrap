# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Project Navi

"""Tests for pack discovery and resolution."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest
import yaml

from navi_bootstrap.packs import PackError, PackInfo, bundled_packs_dir, list_packs, resolve_pack


class TestBundledPacksDir:
    def test_returns_path(self) -> None:
        result = bundled_packs_dir()
        assert result is not None
        assert result.is_dir()

    def test_returns_none_when_no_packs(self, tmp_path: Path) -> None:
        fake_file = tmp_path / "fake.py"
        fake_file.write_text("")
        with patch("navi_bootstrap.packs.__file__", str(fake_file)):
            result = bundled_packs_dir()
        assert result is None


class TestResolvePack:
    def test_resolve_bundled_pack_by_name(self) -> None:
        path = resolve_pack("base")
        assert path.is_dir()
        assert (path / "manifest.yaml").exists()

    def test_resolve_filesystem_path(self, tmp_path: Path) -> None:
        pack_dir = tmp_path / "my-pack"
        pack_dir.mkdir()
        result = resolve_pack(str(pack_dir))
        assert result == pack_dir

    def test_resolve_dot_prefixed_path(self, tmp_path: Path) -> None:
        pack_dir = tmp_path / "my-pack"
        pack_dir.mkdir()
        # Use a genuinely relative path by creating a subdir
        dot_path = "./my-pack"
        import os

        old_cwd = os.getcwd()
        os.chdir(tmp_path)
        try:
            result = resolve_pack(dot_path)
            assert result == Path(dot_path)
        finally:
            os.chdir(old_cwd)

    def test_resolve_nonexistent_name_raises(self) -> None:
        with pytest.raises(PackError, match="Unknown pack 'nonexistent'"):
            resolve_pack("nonexistent")

    def test_resolve_nonexistent_name_lists_available(self) -> None:
        with pytest.raises(PackError, match="Available packs:"):
            resolve_pack("nonexistent")

    def test_resolve_nonexistent_path_raises(self) -> None:
        with pytest.raises(PackError, match="Pack directory not found"):
            resolve_pack("/tmp/does-not-exist-at-all")

    def test_all_bundled_packs_resolvable(self) -> None:
        expected = {
            "base",
            "code-hygiene",
            "github-templates",
            "quality-gates",
            "release-pipeline",
            "review-system",
            "scaffold",
            "security-scanning",
        }
        for name in expected:
            path = resolve_pack(name)
            assert path.is_dir(), f"Pack {name} did not resolve to a directory"


class TestListPacks:
    def test_lists_all_bundled_packs(self) -> None:
        packs = list_packs()
        names = {p.name for p in packs}
        expected = {
            "base",
            "code-hygiene",
            "github-templates",
            "quality-gates",
            "release-pipeline",
            "review-system",
            "scaffold",
            "security-scanning",
        }
        assert names == expected

    def test_returns_pack_info(self) -> None:
        packs = list_packs()
        assert len(packs) == 8
        for p in packs:
            assert isinstance(p, PackInfo)
            assert p.name
            assert p.version
            assert p.path.is_dir()

    def test_packs_sorted_by_name(self) -> None:
        packs = list_packs()
        names = [p.name for p in packs]
        assert names == sorted(names)

    def test_skips_dirs_without_manifest(self, tmp_path: Path) -> None:
        """A directory without manifest.yaml is silently skipped."""
        pack_dir = tmp_path / "packs"
        pack_dir.mkdir()
        (pack_dir / "good-pack").mkdir()
        (pack_dir / "good-pack" / "manifest.yaml").write_text(
            yaml.dump({"name": "good-pack", "version": "1.0", "description": "A good pack"})
        )
        (pack_dir / "no-manifest").mkdir()

        with patch("navi_bootstrap.packs.bundled_packs_dir", return_value=pack_dir):
            packs = list_packs()
        assert len(packs) == 1
        assert packs[0].name == "good-pack"


class TestSchemaResolution:
    def test_manifest_schema_loads(self) -> None:
        from navi_bootstrap.manifest import _load_schema

        schema = _load_schema()
        assert isinstance(schema, dict)
        assert "properties" in schema or "type" in schema

    def test_spec_schema_loads(self) -> None:
        from navi_bootstrap.spec import _load_schema

        schema = _load_schema()
        assert isinstance(schema, dict)
        assert "properties" in schema or "type" in schema
