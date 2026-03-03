"""Tests for nboot new command and spec building."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from navi_bootstrap.cli import cli
from navi_bootstrap.spec import SpecError, build_spec_for_new


class TestBuildSpecForNew:
    def test_defaults(self) -> None:
        """build_spec_for_new with defaults produces valid spec."""
        spec = build_spec_for_new("my-project")
        assert spec["name"] == "my-project"
        assert spec["language"] == "python"
        assert spec["version"] == "0.1.0"
        assert spec["python_version"] == "3.12"
        assert spec["structure"]["src_dir"] == "src/my_project"
        assert spec["structure"]["test_dir"] == "tests"
        assert spec["features"]["ci"] is True
        assert spec["features"]["pre_commit"] is True
        assert spec["dependencies"]["runtime"] == []
        assert spec["dependencies"]["dev"] == ["pytest>=8.0", "ruff>=0.4", "mypy>=1.10"]
        assert spec["license"] == "MIT"

    def test_custom_args(self) -> None:
        """build_spec_for_new with custom args."""
        spec = build_spec_for_new(
            "cool-lib",
            description="A cool library",
            license_id="Apache-2.0",
            python_version="3.11",
            author_name="Jane Doe",
        )
        assert spec["name"] == "cool-lib"
        assert spec["description"] == "A cool library"
        assert spec["license"] == "Apache-2.0"
        assert spec["python_version"] == "3.11"
        assert spec["author"] == {"name": "Jane Doe"}
        assert spec["structure"]["src_dir"] == "src/cool_lib"

    def test_no_author_when_empty(self) -> None:
        """author field omitted when author_name is empty."""
        spec = build_spec_for_new("my-project", author_name="")
        assert "author" not in spec

    def test_no_license_when_empty(self) -> None:
        """license field omitted when license_id is empty."""
        spec = build_spec_for_new("my-project", license_id="")
        assert "license" not in spec

    def test_passes_validation(self) -> None:
        """Returned spec passes validate_spec."""
        from navi_bootstrap.spec import validate_spec

        spec = build_spec_for_new("my-project")
        validate_spec(spec)  # Should not raise

    def test_empty_name_raises(self) -> None:
        """Empty name fails schema validation."""
        with pytest.raises(SpecError, match="Spec validation failed"):
            build_spec_for_new("")

    def test_hyphenated_name_converted_to_underscores_in_src_dir(self) -> None:
        """Hyphens in project name become underscores in src_dir."""
        spec = build_spec_for_new("my-cool-project")
        assert spec["structure"]["src_dir"] == "src/my_cool_project"

    def test_description_defaults_to_empty(self) -> None:
        """Description defaults to empty string."""
        spec = build_spec_for_new("my-project")
        assert spec["description"] == ""


class TestNbootNew:
    @pytest.fixture()
    def runner(self) -> CliRunner:
        return CliRunner()

    def test_creates_project(self, runner: CliRunner, tmp_path: Path) -> None:
        """nboot new creates project directory with expected files."""
        with runner.isolated_filesystem(temp_dir=tmp_path):
            result = runner.invoke(cli, ["new", "my-project", "--skip-resolve"])
            assert result.exit_code == 0, result.output
            p = Path("my-project")
            assert p.exists()
            # Scaffold files
            assert (p / "pyproject.toml").exists()
            assert (p / "src" / "my_project" / "__init__.py").exists()
            assert (p / "src" / "my_project" / "py.typed").exists()
            assert (p / "tests" / "conftest.py").exists()
            assert (p / "tests" / "test_my_project.py").exists()
            assert (p / "README.md").exists()
            assert (p / "LICENSE").exists()
            assert (p / ".gitignore").exists()
            # Spec file
            assert (p / "nboot-spec.json").exists()
            spec = json.loads((p / "nboot-spec.json").read_text())
            assert spec["name"] == "my-project"
            # Git init
            assert (p / ".git").exists()

    def test_dry_run(self, runner: CliRunner, tmp_path: Path) -> None:
        """--dry-run shows plan without creating files."""
        with runner.isolated_filesystem(temp_dir=tmp_path):
            result = runner.invoke(cli, ["new", "my-project", "--dry-run"])
            assert result.exit_code == 0
            assert "Dry run" in result.output
            assert not (tmp_path / "my-project").exists()

    def test_rejects_existing_dir(self, runner: CliRunner, tmp_path: Path) -> None:
        """Existing directory is rejected."""
        with runner.isolated_filesystem(temp_dir=tmp_path):
            Path("my-project").mkdir()
            result = runner.invoke(cli, ["new", "my-project"])
            assert result.exit_code != 0
            assert "already exists" in result.output

    def test_multi_pack_order(self, runner: CliRunner, tmp_path: Path) -> None:
        """scaffold renders first (greenfield), base renders second (apply)."""
        with runner.isolated_filesystem(temp_dir=tmp_path):
            result = runner.invoke(cli, ["new", "my-project", "--skip-resolve"])
            assert result.exit_code == 0, result.output
            assert "[scaffold]" in result.output
            assert "[base]" in result.output
            # scaffold output before base in output
            scaffold_pos = result.output.index("[scaffold]")
            base_pos = result.output.index("[base]")
            assert scaffold_pos < base_pos

    def test_custom_packs(self, runner: CliRunner, tmp_path: Path) -> None:
        """--packs allows specifying pack order."""
        with runner.isolated_filesystem(temp_dir=tmp_path):
            result = runner.invoke(
                cli, ["new", "my-project", "--skip-resolve", "--packs", "scaffold"]
            )
            assert result.exit_code == 0, result.output
            assert "[scaffold]" in result.output
            assert "[base]" not in result.output

    def test_with_author(self, runner: CliRunner, tmp_path: Path) -> None:
        """--author populates author in rendered files."""
        with runner.isolated_filesystem(temp_dir=tmp_path):
            result = runner.invoke(
                cli,
                [
                    "new",
                    "my-project",
                    "--skip-resolve",
                    "--author",
                    "Jane Doe",
                    "--packs",
                    "scaffold",
                ],
            )
            assert result.exit_code == 0, result.output
            toml_content = (Path("my-project") / "pyproject.toml").read_text()
            assert "Jane Doe" in toml_content

    def test_with_description(self, runner: CliRunner, tmp_path: Path) -> None:
        """--description populates description in rendered files."""
        with runner.isolated_filesystem(temp_dir=tmp_path):
            result = runner.invoke(
                cli,
                [
                    "new",
                    "my-project",
                    "--skip-resolve",
                    "--description",
                    "A cool project",
                    "--packs",
                    "scaffold",
                ],
            )
            assert result.exit_code == 0, result.output
            toml_content = (Path("my-project") / "pyproject.toml").read_text()
            assert "A cool project" in toml_content

    def test_no_license_file_for_non_mit(self, runner: CliRunner, tmp_path: Path) -> None:
        """Non-MIT license skips LICENSE file generation."""
        with runner.isolated_filesystem(temp_dir=tmp_path):
            result = runner.invoke(
                cli,
                [
                    "new",
                    "my-project",
                    "--skip-resolve",
                    "--license",
                    "Apache-2.0",
                    "--packs",
                    "scaffold",
                ],
            )
            assert result.exit_code == 0, result.output
            assert not (Path("my-project") / "LICENSE").exists()
            # But spec still has the license
            spec = json.loads((Path("my-project") / "nboot-spec.json").read_text())
            assert spec["license"] == "Apache-2.0"

    def test_license_file_for_mit(self, runner: CliRunner, tmp_path: Path) -> None:
        """MIT license generates LICENSE file."""
        with runner.isolated_filesystem(temp_dir=tmp_path):
            result = runner.invoke(
                cli,
                [
                    "new",
                    "my-project",
                    "--skip-resolve",
                    "--license",
                    "MIT",
                    "--packs",
                    "scaffold",
                ],
            )
            assert result.exit_code == 0, result.output
            assert (Path("my-project") / "LICENSE").exists()
            content = (Path("my-project") / "LICENSE").read_text()
            assert "MIT License" in content

    def test_with_license(self, runner: CliRunner, tmp_path: Path) -> None:
        """--license is persisted in spec; LICENSE generation is MIT-only."""
        with runner.isolated_filesystem(temp_dir=tmp_path):
            result = runner.invoke(
                cli,
                [
                    "new",
                    "my-project",
                    "--skip-resolve",
                    "--license",
                    "Apache-2.0",
                    "--packs",
                    "scaffold",
                ],
            )
            assert result.exit_code == 0, result.output
            spec = json.loads((Path("my-project") / "nboot-spec.json").read_text())
            assert spec["license"] == "Apache-2.0"

    def test_spec_file_written(self, runner: CliRunner, tmp_path: Path) -> None:
        """nboot-spec.json is written to project root."""
        with runner.isolated_filesystem(temp_dir=tmp_path):
            result = runner.invoke(
                cli, ["new", "my-project", "--skip-resolve", "--packs", "scaffold"]
            )
            assert result.exit_code == 0, result.output
            spec_path = Path("my-project") / "nboot-spec.json"
            assert spec_path.exists()
            spec = json.loads(spec_path.read_text())
            assert spec["name"] == "my-project"
            assert spec["language"] == "python"

    def test_output_summary(self, runner: CliRunner, tmp_path: Path) -> None:
        """Output includes file count summary."""
        with runner.isolated_filesystem(temp_dir=tmp_path):
            result = runner.invoke(
                cli, ["new", "my-project", "--skip-resolve", "--packs", "scaffold"]
            )
            assert result.exit_code == 0, result.output
            assert "Created my-project/" in result.output
            assert "8 files" in result.output

    def test_no_duplicate_toml_sections(self, runner: CliRunner, tmp_path: Path) -> None:
        """scaffold + base produce valid TOML without duplicate sections."""
        with runner.isolated_filesystem(temp_dir=tmp_path):
            result = runner.invoke(cli, ["new", "my-project", "--skip-resolve"])
            assert result.exit_code == 0, result.output
            content = (Path("my-project") / "pyproject.toml").read_text()
            for section in [
                "[dependency-groups]",
                "[tool.ruff]",
                "[tool.ruff.lint]",
                "[tool.mypy]",
                "[tool.pytest.ini_options]",
            ]:
                count = content.count(section)
                assert count == 1, f"{section} appears {count} times:\n{content}"

    def test_scaffold_only_has_no_tool_config(self, runner: CliRunner, tmp_path: Path) -> None:
        """Scaffold alone produces pyproject.toml without tool config sections."""
        with runner.isolated_filesystem(temp_dir=tmp_path):
            result = runner.invoke(
                cli, ["new", "my-project", "--skip-resolve", "--packs", "scaffold"]
            )
            assert result.exit_code == 0, result.output
            content = (Path("my-project") / "pyproject.toml").read_text()
            assert "[build-system]" in content
            assert "[project]" in content
            assert "[tool.ruff]" not in content
            assert "[tool.mypy]" not in content
            assert "[dependency-groups]" not in content

    @pytest.mark.parametrize(
        "name",
        [
            "../traversal",
            "foo/bar",
            "foo\\bar",
            ".hidden",
            "..double",
        ],
    )
    def test_rejects_unsafe_names(self, runner: CliRunner, tmp_path: Path, name: str) -> None:
        """nboot new rejects names with path separators or leading dots."""
        with runner.isolated_filesystem(temp_dir=tmp_path):
            result = runner.invoke(cli, ["new", name, "--skip-resolve"])
            assert result.exit_code != 0
            assert "Unsafe project name" in result.output

    def test_cleans_up_on_failure(self, runner: CliRunner, tmp_path: Path) -> None:
        """Failed nboot new removes partial directory."""
        # Create a broken pack that will fail mid-render
        bad_pack = tmp_path / "badpack"
        bad_pack.mkdir()
        templates_dir = bad_pack / "templates"
        templates_dir.mkdir()

        manifest = {
            "name": "broken",
            "version": "0.1.0",
            "templates": [{"src": "out.j2", "dest": "out.txt"}],
            "conditions": {},
            "loops": {},
        }
        import yaml

        (bad_pack / "manifest.yaml").write_text(yaml.dump(manifest))
        (templates_dir / "out.j2").write_text("{{ undefined_var }}")

        with runner.isolated_filesystem(temp_dir=tmp_path):
            result = runner.invoke(
                cli, ["new", "myproj", "--skip-resolve", "--packs", str(bad_pack)]
            )
            assert result.exit_code != 0
            # Directory should be cleaned up
            assert not Path("myproj").exists()

    @patch("navi_bootstrap.cli.gh_available", return_value=False)
    def test_graceful_degradation_without_gh(
        self, mock_gh: MagicMock, runner: CliRunner, tmp_path: Path
    ) -> None:
        """nboot new without gh CLI degrades gracefully instead of failing."""
        with runner.isolated_filesystem(temp_dir=tmp_path):
            result = runner.invoke(cli, ["new", "my-project"])
            assert result.exit_code == 0, result.output
            assert "gh CLI not found" in result.output
            # SHAs should be placeholders
            ci_content = (Path("my-project") / ".github" / "workflows" / "tests.yml").read_text()
            assert "SKIP_SHA_RESOLUTION" in ci_content
