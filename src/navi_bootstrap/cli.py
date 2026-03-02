# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Project Navi

"""nboot CLI — render and apply template packs."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

import click

from navi_bootstrap.diff import compute_diffs
from navi_bootstrap.engine import plan, render, render_to_files
from navi_bootstrap.hooks import run_hooks
from navi_bootstrap.init import inspect_project
from navi_bootstrap.manifest import ManifestError, load_manifest
from navi_bootstrap.packs import PackError, get_ordered_packs, list_packs, resolve_pack
from navi_bootstrap.resolve import ResolveError, gh_available, resolve_action_shas
from navi_bootstrap.sanitize import sanitize_manifest, sanitize_spec
from navi_bootstrap.spec import SpecError, build_spec_for_new, load_spec
from navi_bootstrap.validate import run_validations

_GH_NOTICE = (
    "Notice: gh CLI not found — SHA resolution requires gh "
    "(https://cli.github.com).\n"
    "  Action SHAs left as placeholders. Re-run without --skip-resolve after installing gh."
)


def _check_gh_or_skip(skip_resolve: bool) -> bool:
    """Return effective skip_resolve, printing a notice if gh is unavailable."""
    if skip_resolve:
        return True
    if not gh_available():
        click.echo(_GH_NOTICE, err=True)
        return True
    return False


@click.group()
@click.version_option()
def cli() -> None:
    """nboot — bootstrap projects with template packs."""


@cli.command()
@click.option("--spec", required=True, type=click.Path(exists=True, path_type=Path))
@click.option("--pack", type=str, default=None)
def validate(spec: Path, pack: str | None) -> None:
    """Validate a spec (and optionally a pack manifest)."""
    try:
        load_spec(spec)
        click.echo(f"Spec valid: {spec}")
    except SpecError as e:
        raise click.ClickException(str(e)) from e

    if pack:
        try:
            pack_dir = resolve_pack(pack)
        except PackError as e:
            raise click.ClickException(str(e)) from e
        try:
            load_manifest(pack_dir / "manifest.yaml")
            click.echo(f"Manifest valid: {pack_dir / 'manifest.yaml'}")
        except ManifestError as e:
            raise click.ClickException(str(e)) from e


@cli.command("render")
@click.option("--spec", required=True, type=click.Path(exists=True, path_type=Path))
@click.option("--pack", required=True, type=str)
@click.option("--out", type=click.Path(path_type=Path), default=None)
@click.option("--dry-run", is_flag=True, default=False)
@click.option("--skip-resolve", is_flag=True, default=False, help="Skip SHA resolution (offline)")
@click.option("--trust", is_flag=True, default=False, help="Execute hooks from manifest (unsafe)")
def render_cmd(
    spec: Path, pack: str, out: Path | None, dry_run: bool, skip_resolve: bool, trust: bool
) -> None:
    """Render a template pack into a new project (greenfield)."""
    try:
        pack_dir = resolve_pack(pack)
    except PackError as e:
        raise click.ClickException(str(e)) from e

    try:
        spec_data = load_spec(spec)
    except SpecError as e:
        raise click.ClickException(str(e)) from e
    spec_data = sanitize_spec(spec_data)

    try:
        manifest = load_manifest(pack_dir / "manifest.yaml")
    except ManifestError as e:
        raise click.ClickException(str(e)) from e
    manifest = sanitize_manifest(manifest)

    if out is None:
        name = spec_data["name"]
        if not name or "/" in name or "\\" in name:
            raise click.ClickException(
                f"Unsafe spec name {name!r} cannot be used as output directory. "
                "Use --out to specify an explicit output path."
            )
        output_dir = Path(name)
    else:
        output_dir = out

    # Stage 0: Resolve SHAs
    effective_skip = _check_gh_or_skip(skip_resolve or dry_run)
    action_shas_config = manifest.get("action_shas", [])
    try:
        shas, versions = resolve_action_shas(action_shas_config, skip=effective_skip)
    except ResolveError as e:
        raise click.ClickException(str(e)) from e

    # Stage 2: Plan
    templates_dir = pack_dir / "templates"
    render_plan = plan(manifest, spec_data, templates_dir)

    if dry_run:
        click.echo("Dry run — render plan:")
        for entry in render_plan.entries:
            mode_tag = f" [{entry.mode}]" if entry.mode != "create" else ""
            click.echo(f"  {entry.src} → {entry.dest}{mode_tag}")
        return

    # Stage 3: Render
    output_dir.mkdir(parents=True, exist_ok=True)
    try:
        written = render(
            render_plan,
            spec_data,
            templates_dir,
            output_dir,
            mode="greenfield",
            action_shas=shas,
            action_versions=versions,
        )
    except FileExistsError as e:
        raise click.ClickException(str(e)) from e

    click.echo(f"Rendered {len(written)} files to {output_dir}")

    # Stage 5: Hooks
    hooks = manifest.get("hooks", [])
    if hooks:
        if trust:
            click.echo("Running hooks...")
            for r in run_hooks(hooks, output_dir):
                status = "OK" if r.success else "FAIL"
                click.echo(f"  [{status}] {r.command}")
        else:
            click.echo("Skipped hooks (manifest commands not trusted):")
            for h in hooks:
                click.echo(f"  {h}")
            click.echo("Pass --trust to execute.")


@cli.command()
@click.option("--spec", required=True, type=click.Path(exists=True, path_type=Path))
@click.option("--pack", required=True, type=str)
@click.option(
    "--target", required=True, type=click.Path(exists=True, file_okay=False, path_type=Path)
)
@click.option("--dry-run", is_flag=True, default=False)
@click.option("--skip-resolve", is_flag=True, default=False, help="Skip SHA resolution (offline)")
@click.option(
    "--trust", is_flag=True, default=False, help="Execute hooks/validations from manifest (unsafe)"
)
def apply(
    spec: Path, pack: str, target: Path, dry_run: bool, skip_resolve: bool, trust: bool
) -> None:
    """Apply a template pack to an existing project."""
    try:
        pack_dir = resolve_pack(pack)
    except PackError as e:
        raise click.ClickException(str(e)) from e

    try:
        spec_data = load_spec(spec)
    except SpecError as e:
        raise click.ClickException(str(e)) from e
    spec_data = sanitize_spec(spec_data)

    try:
        manifest = load_manifest(pack_dir / "manifest.yaml")
    except ManifestError as e:
        raise click.ClickException(str(e)) from e
    manifest = sanitize_manifest(manifest)

    # Stage 0: Resolve SHAs
    effective_skip = _check_gh_or_skip(skip_resolve or dry_run)
    action_shas_config = manifest.get("action_shas", [])
    try:
        shas, versions = resolve_action_shas(action_shas_config, skip=effective_skip)
    except ResolveError as e:
        raise click.ClickException(str(e)) from e

    # Stage 2: Plan
    templates_dir = pack_dir / "templates"
    render_plan = plan(manifest, spec_data, templates_dir)

    if dry_run:
        click.echo("Dry run — render plan:")
        for entry in render_plan.entries:
            mode_tag = f" [{entry.mode}]" if entry.mode != "create" else ""
            click.echo(f"  {entry.src} → {entry.dest}{mode_tag}")
        return

    # Stage 3: Render
    written = render(
        render_plan,
        spec_data,
        templates_dir,
        target,
        mode="apply",
        action_shas=shas,
        action_versions=versions,
    )
    click.echo(f"Applied {len(written)} files to {target}")

    # Stage 4: Validate + Stage 5: Hooks
    validations = manifest.get("validation", [])
    hooks = manifest.get("hooks", [])

    if trust:
        if validations:
            click.echo("Running validations...")
            for r in run_validations(validations, target):
                if r.skipped:
                    status = "SKIP"
                elif r.passed:
                    status = "PASS"
                else:
                    status = "FAIL"
                click.echo(f"  [{status}] {r.description}")

        if hooks:
            click.echo("Running hooks...")
            for h in run_hooks(hooks, target):
                status = "OK" if h.success else "FAIL"
                click.echo(f"  [{status}] {h.command}")
    else:
        skipped: list[str] = []
        for v in validations:
            cmd = v.get("command")
            if cmd:
                skipped.append(cmd)
        skipped.extend(hooks)
        if skipped:
            click.echo("Skipped validations/hooks (manifest commands not trusted):")
            for s in skipped:
                click.echo(f"  {s}")
            click.echo("Pass --trust to execute.")


@cli.command("diff")
@click.option("--spec", required=True, type=click.Path(exists=True, path_type=Path))
@click.option("--pack", required=True, type=str)
@click.option(
    "--target", required=True, type=click.Path(exists=True, file_okay=False, path_type=Path)
)
@click.option("--skip-resolve", is_flag=True, default=False, help="Skip SHA resolution (offline)")
def diff_cmd(spec: Path, pack: str, target: Path, skip_resolve: bool) -> None:
    """Preview what a pack would change without writing anything."""
    try:
        pack_dir = resolve_pack(pack)
    except PackError as e:
        raise click.ClickException(str(e)) from e

    try:
        spec_data = load_spec(spec)
    except SpecError as e:
        raise click.ClickException(str(e)) from e
    spec_data = sanitize_spec(spec_data)

    try:
        manifest = load_manifest(pack_dir / "manifest.yaml")
    except ManifestError as e:
        raise click.ClickException(str(e)) from e
    manifest = sanitize_manifest(manifest)

    # Stage 0: Resolve SHAs
    effective_skip = _check_gh_or_skip(skip_resolve)
    action_shas_config = manifest.get("action_shas", [])
    try:
        shas, versions = resolve_action_shas(action_shas_config, skip=effective_skip)
    except ResolveError as e:
        raise click.ClickException(str(e)) from e

    # Stage 2: Plan
    templates_dir = pack_dir / "templates"
    render_plan = plan(manifest, spec_data, templates_dir)

    # Stage 3: Render to memory (no filesystem writes)
    rendered_files = render_to_files(
        render_plan,
        spec_data,
        templates_dir,
        action_shas=shas,
        action_versions=versions,
    )

    # Compute diffs
    diffs = compute_diffs(rendered_files, target, pack_name=render_plan.pack_name)

    if not diffs:
        click.echo("No changes — target is up to date.")
        raise SystemExit(0)

    for d in diffs:
        label = "(new)" if d.is_new else "(changed)"
        click.echo(f"--- {d.dest} {label} ---")
        click.echo(d.diff_text)

    n = len(diffs)
    click.echo(f"\n{n} file{'s' if n != 1 else ''} would change.")
    raise SystemExit(1)


@cli.command("list-packs")
def list_packs_cmd() -> None:
    """List all bundled template packs."""
    packs = list_packs()
    if not packs:
        click.echo("No bundled packs found.")
        return
    for p in packs:
        click.echo(f"  {p.name:<25} v{p.version:<10} {p.description}")


@cli.command()
@click.option(
    "--target",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=".",
    help="Project directory to inspect (default: current directory)",
)
@click.option(
    "--out",
    type=click.Path(path_type=Path),
    default=None,
    help="Output path for spec file (default: <target>/nboot-spec.json)",
)
@click.option("--yes", "-y", is_flag=True, default=False, help="Skip confirmation prompts")
def init(target: Path, out: Path | None, yes: bool) -> None:
    """Generate a project spec by inspecting an existing project."""
    click.echo(f"Inspecting {target}...\n")

    spec = inspect_project(target)

    # Prompt for missing required fields
    if not spec.get("language"):
        if yes:
            raise click.ClickException(
                "Could not detect project language. Run without --yes to provide it interactively."
            )
        spec["language"] = click.prompt(
            "  Language", type=click.Choice(["python", "typescript", "go", "rust"])
        )

    if not spec.get("name"):
        if yes:
            raise click.ClickException(
                "Could not detect project name. Run without --yes to provide it interactively."
            )
        spec["name"] = click.prompt("  Project name")

    # Sanitize before display and write — spec values from pyproject.toml
    # may contain Jinja2 delimiters, homoglyphs, or zero-width chars.
    spec = sanitize_spec(spec)

    # Display detected spec
    _display_spec(spec)

    # Confirm
    if not yes:
        if not click.confirm("\nWrite spec?", default=True):
            click.echo("Aborted.")
            return

    # Write
    out_path = out or (target / "nboot-spec.json")
    out_path.write_text(json.dumps(spec, indent=2) + "\n")
    click.echo(f"\nWrote {out_path}")


@cli.command("new")
@click.argument("name")
@click.option("--description", default="", help="One-line project description")
@click.option("--license", "license_id", default="MIT", help="SPDX license identifier")
@click.option("--python-version", default="3.12", help="Minimum Python version")
@click.option("--author", default="", help="Author name")
@click.option("--packs", default=None, help="Comma-separated pack names (default: scaffold,base)")
@click.option("--skip-resolve", is_flag=True, default=False, help="Skip SHA resolution (offline)")
@click.option("--dry-run", is_flag=True, default=False, help="Show plan without writing files")
def new(
    name: str,
    description: str,
    license_id: str,
    python_version: str,
    author: str,
    packs: str | None,
    skip_resolve: bool,
    dry_run: bool,
) -> None:
    """Create a new Python project with operational infrastructure."""
    output_dir = Path(name)
    if output_dir.exists():
        raise click.ClickException(
            f"Directory {name!r} already exists. nboot new is for greenfield projects only."
        )

    # Build spec from CLI args
    try:
        spec_data = build_spec_for_new(
            name,
            description=description,
            license_id=license_id,
            python_version=python_version,
            author_name=author,
        )
    except SpecError as e:
        raise click.ClickException(str(e)) from e
    spec_data = sanitize_spec(spec_data)

    # Resolve pack order
    pack_names = packs.split(",") if packs else None
    try:
        pack_dirs = get_ordered_packs(pack_names)
    except PackError as e:
        raise click.ClickException(str(e)) from e

    if dry_run:
        click.echo(f"Dry run — would create {name}/")
        click.echo(f"  Packs: {', '.join(p.name for p in pack_dirs)}")
        for pack_dir in pack_dirs:
            try:
                manifest = load_manifest(pack_dir / "manifest.yaml")
            except ManifestError as e:
                raise click.ClickException(str(e)) from e
            manifest = sanitize_manifest(manifest)
            templates_dir = pack_dir / "templates"
            render_plan = plan(manifest, spec_data, templates_dir)
            click.echo(f"\n  [{manifest['name']}]")
            for entry in render_plan.entries:
                mode_tag = f" [{entry.mode}]" if entry.mode != "create" else ""
                click.echo(f"    {entry.src} → {entry.dest}{mode_tag}")
        return

    # Render packs in order
    effective_skip = _check_gh_or_skip(skip_resolve)
    output_dir.mkdir(parents=True)
    total_written: list[Path] = []

    for i, pack_dir in enumerate(pack_dirs):
        try:
            manifest = load_manifest(pack_dir / "manifest.yaml")
        except ManifestError as e:
            raise click.ClickException(str(e)) from e
        manifest = sanitize_manifest(manifest)

        # Stage 0: Resolve SHAs
        action_shas_config = manifest.get("action_shas", [])
        try:
            shas, versions = resolve_action_shas(action_shas_config, skip=effective_skip)
        except ResolveError as e:
            raise click.ClickException(str(e)) from e

        # Stage 2: Plan
        templates_dir = pack_dir / "templates"
        render_plan = plan(manifest, spec_data, templates_dir)

        # Stage 3: Render — first pack is greenfield, subsequent packs apply
        mode = "greenfield" if i == 0 else "apply"
        try:
            written = render(
                render_plan,
                spec_data,
                templates_dir,
                output_dir,
                mode=mode,
                action_shas=shas,
                action_versions=versions,
            )
        except (FileExistsError, ValueError) as e:
            raise click.ClickException(str(e)) from e

        total_written.extend(written)
        click.echo(f"  [{manifest['name']}] {len(written)} files")

    # Write spec file
    spec_path = output_dir / "nboot-spec.json"
    spec_path.write_text(json.dumps(spec_data, indent=2) + "\n")

    # Initialize git repo
    subprocess.run(
        ["git", "init"],
        cwd=output_dir,
        capture_output=True,
        check=False,
    )

    click.echo(
        f"\nCreated {name}/ — {len(total_written)} files from "
        f"{len(pack_dirs)} pack{'s' if len(pack_dirs) != 1 else ''}"
    )


def _display_spec(spec: dict[str, Any]) -> None:
    """Display a summary of the detected spec."""
    click.echo(f"  Name:        {spec.get('name', '(unknown)')}")
    click.echo(f"  Language:    {spec.get('language', '(unknown)')}")
    if v := spec.get("version"):
        click.echo(f"  Version:     {v}")
    if pv := spec.get("python_version"):
        click.echo(f"  Python:      {pv}")
    if s := spec.get("structure"):
        if src := s.get("src_dir"):
            click.echo(f"  Source:      {src}")
        if td := s.get("test_dir"):
            click.echo(f"  Tests:       {td}")
    if gh := spec.get("github"):
        click.echo(f"  GitHub:      {gh.get('org', '?')}/{gh.get('repo', '?')}")
    if f := spec.get("features"):
        active = [k for k, v in f.items() if v]
        if active:
            click.echo(f"  Features:    {', '.join(active)}")
    if r := spec.get("recon"):
        tools = r.get("existing_tools", {})
        found = [k for k, v in tools.items() if v]
        if found:
            click.echo(f"  Tools:       {', '.join(found)}")
        if tc := r.get("test_count"):
            click.echo(f"  Test count:  {tc}")
