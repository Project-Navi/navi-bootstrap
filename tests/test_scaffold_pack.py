"""Tests for the scaffold template pack."""

from __future__ import annotations

from pathlib import Path

from navi_bootstrap.engine import plan, render
from navi_bootstrap.manifest import load_manifest
from navi_bootstrap.packs import resolve_pack
from navi_bootstrap.sanitize import sanitize_manifest, sanitize_spec
from navi_bootstrap.spec import build_spec_for_new


class TestScaffoldManifest:
    def test_manifest_loads(self) -> None:
        """Scaffold manifest passes schema validation."""
        pack_dir = resolve_pack("scaffold")
        manifest = load_manifest(pack_dir / "manifest.yaml")
        assert manifest["name"] == "scaffold"
        assert len(manifest["templates"]) == 8

    def test_manifest_has_required_fields(self) -> None:
        """Manifest has all required engine fields."""
        pack_dir = resolve_pack("scaffold")
        manifest = load_manifest(pack_dir / "manifest.yaml")
        assert "conditions" in manifest
        assert "loops" in manifest
        assert "templates" in manifest

    def test_manifest_has_license_condition(self) -> None:
        """LICENSE template is conditional on spec.license."""
        pack_dir = resolve_pack("scaffold")
        manifest = load_manifest(pack_dir / "manifest.yaml")
        assert manifest["conditions"]["LICENSE.j2"] == "spec.license"


class TestScaffoldRender:
    def test_templates_render(self, tmp_path: Path) -> None:
        """All scaffold templates render without error."""
        pack_dir = resolve_pack("scaffold")
        manifest = load_manifest(pack_dir / "manifest.yaml")
        manifest = sanitize_manifest(manifest)
        spec = build_spec_for_new("test-project", author_name="Test Author")
        spec = sanitize_spec(spec)
        templates_dir = pack_dir / "templates"
        render_plan = plan(manifest, spec, templates_dir)
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        written = render(
            render_plan,
            spec,
            templates_dir,
            output_dir,
            mode="greenfield",
            action_shas={},
            action_versions={},
        )
        assert len(written) == 8

    def test_output_structure(self, tmp_path: Path) -> None:
        """Rendered files are at expected paths."""
        pack_dir = resolve_pack("scaffold")
        manifest = load_manifest(pack_dir / "manifest.yaml")
        manifest = sanitize_manifest(manifest)
        spec = build_spec_for_new("my-lib", author_name="Test")
        spec = sanitize_spec(spec)
        templates_dir = pack_dir / "templates"
        render_plan = plan(manifest, spec, templates_dir)
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        render(
            render_plan,
            spec,
            templates_dir,
            output_dir,
            mode="greenfield",
            action_shas={},
            action_versions={},
        )
        assert (output_dir / "pyproject.toml").exists()
        assert (output_dir / "src" / "my_lib" / "__init__.py").exists()
        assert (output_dir / "src" / "my_lib" / "py.typed").exists()
        assert (output_dir / "tests" / "conftest.py").exists()
        assert (output_dir / "tests" / "test_my_lib.py").exists()
        assert (output_dir / "README.md").exists()
        assert (output_dir / "LICENSE").exists()
        assert (output_dir / ".gitignore").exists()

    def test_no_license_without_spec_license(self, tmp_path: Path) -> None:
        """LICENSE file is skipped when spec has no license."""
        pack_dir = resolve_pack("scaffold")
        manifest = load_manifest(pack_dir / "manifest.yaml")
        manifest = sanitize_manifest(manifest)
        spec = build_spec_for_new("my-lib", license_id="")
        spec = sanitize_spec(spec)
        templates_dir = pack_dir / "templates"
        render_plan = plan(manifest, spec, templates_dir)
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        render(
            render_plan,
            spec,
            templates_dir,
            output_dir,
            mode="greenfield",
            action_shas={},
            action_versions={},
        )
        assert not (output_dir / "LICENSE").exists()

    def test_render_count_without_license(self, tmp_path: Path) -> None:
        """Only 7 files rendered when license is omitted."""
        pack_dir = resolve_pack("scaffold")
        manifest = load_manifest(pack_dir / "manifest.yaml")
        manifest = sanitize_manifest(manifest)
        spec = build_spec_for_new("my-lib", license_id="")
        spec = sanitize_spec(spec)
        templates_dir = pack_dir / "templates"
        render_plan = plan(manifest, spec, templates_dir)
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        written = render(
            render_plan,
            spec,
            templates_dir,
            output_dir,
            mode="greenfield",
            action_shas={},
            action_versions={},
        )
        assert len(written) == 7

    def test_pyproject_toml_content(self, tmp_path: Path) -> None:
        """pyproject.toml contains expected project metadata."""
        pack_dir = resolve_pack("scaffold")
        manifest = load_manifest(pack_dir / "manifest.yaml")
        manifest = sanitize_manifest(manifest)
        spec = build_spec_for_new(
            "my-lib",
            description="A test library",
            author_name="Test Author",
        )
        spec = sanitize_spec(spec)
        templates_dir = pack_dir / "templates"
        render_plan = plan(manifest, spec, templates_dir)
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        render(
            render_plan,
            spec,
            templates_dir,
            output_dir,
            mode="greenfield",
            action_shas={},
            action_versions={},
        )
        content = (output_dir / "pyproject.toml").read_text()
        assert "my-lib" in content
        assert "A test library" in content
        assert "Test Author" in content

    def test_readme_contains_project_name(self, tmp_path: Path) -> None:
        """README.md references the project name."""
        pack_dir = resolve_pack("scaffold")
        manifest = load_manifest(pack_dir / "manifest.yaml")
        manifest = sanitize_manifest(manifest)
        spec = build_spec_for_new("my-lib")
        spec = sanitize_spec(spec)
        templates_dir = pack_dir / "templates"
        render_plan = plan(manifest, spec, templates_dir)
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        render(
            render_plan,
            spec,
            templates_dir,
            output_dir,
            mode="greenfield",
            action_shas={},
            action_versions={},
        )
        content = (output_dir / "README.md").read_text()
        assert "my-lib" in content
