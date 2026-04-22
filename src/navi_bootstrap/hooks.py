# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Project Navi

"""Stage 5: Post-render hook runner."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass
class HookResult:
    """Result of a single hook execution."""

    command: str
    success: bool
    stdout: str = ""
    stderr: str = ""
    returncode: int = 0


def run_hooks(hooks: list[str], working_dir: Path) -> list[HookResult]:
    """Run hook commands sequentially. Reports failures but does not stop."""
    results: list[HookResult] = []

    for command in hooks:
        # Defensive type check: schema validation should catch non-string entries
        # at Stage 1, but the engine runs even if the manifest was not re-validated.
        # Return a failed result rather than crashing subprocess.run.
        if not isinstance(command, str):
            results.append(
                HookResult(
                    command=repr(command),
                    success=False,
                    stderr=f"Invalid hook type: expected str, got {type(command).__name__}",
                    returncode=-1,
                )
            )
            continue

        try:
            # shell=True is required: manifest hooks are arbitrary shell one-liners
            # (pipes, redirects, &&). Executed only when the user opts in via --trust
            # at the CLI boundary — see cli.py.
            result = subprocess.run(
                command,
                # nosemgrep: python.lang.security.audit.subprocess-shell-true.subprocess-shell-true
                shell=True,  # nosec B602
                capture_output=True,
                text=True,
                cwd=working_dir,
                timeout=300,
            )
            results.append(
                HookResult(
                    command=command,
                    success=result.returncode == 0,
                    stdout=result.stdout,
                    stderr=result.stderr,
                    returncode=result.returncode,
                )
            )
        except subprocess.TimeoutExpired:
            results.append(
                HookResult(
                    command=command,
                    success=False,
                    stderr="Timed out after 300 seconds",
                    returncode=-1,
                )
            )

    return results
