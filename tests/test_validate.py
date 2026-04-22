# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Project Navi
"""Tests for post-render validation runner."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

from navi_bootstrap.validate import run_validations


class TestRunValidations:
    @patch("navi_bootstrap.validate.subprocess.run")
    def test_passing_validation(self, mock_run: MagicMock, tmp_path: Path) -> None:
        mock_run.return_value = MagicMock(returncode=0, stdout="ok", stderr="")
        results = run_validations(
            [{"description": "test", "command": "echo ok", "expect": "exit_code_0"}],
            tmp_path,
        )
        assert len(results) == 1
        assert results[0].passed

    @patch("navi_bootstrap.validate.subprocess.run")
    def test_failing_validation(self, mock_run: MagicMock, tmp_path: Path) -> None:
        mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="fail")
        results = run_validations(
            [{"description": "test", "command": "bad", "expect": "exit_code_0"}],
            tmp_path,
        )
        assert len(results) == 1
        assert not results[0].passed

    @patch("navi_bootstrap.validate.subprocess.run")
    def test_warnings_accepted(self, mock_run: MagicMock, tmp_path: Path) -> None:
        mock_run.return_value = MagicMock(returncode=1, stdout="warning", stderr="")
        results = run_validations(
            [{"description": "test", "command": "warn", "expect": "exit_code_0_or_warnings"}],
            tmp_path,
        )
        assert len(results) == 1
        assert results[0].passed

    def test_empty_validations(self, tmp_path: Path) -> None:
        results = run_validations([], tmp_path)
        assert results == []

    @patch("navi_bootstrap.validate.subprocess.run")
    def test_skips_method_based_validations(self, mock_run: MagicMock, tmp_path: Path) -> None:
        results = run_validations(
            [{"description": "SHA check", "method": "sha_verification"}],
            tmp_path,
        )
        assert len(results) == 1
        assert results[0].skipped
        mock_run.assert_not_called()

    @patch("navi_bootstrap.validate.subprocess.run")
    def test_rejects_non_dict_validation_entry(self, mock_run: MagicMock, tmp_path: Path) -> None:
        # A hostile/malformed manifest can pass a bare string or list through a
        # loose schema. Defensive runtime check must return a failed result
        # rather than crashing with TypeError on v.get() or v["command"].
        results = run_validations(
            [
                {"description": "good", "command": "echo ok"},
                "bare string entry",  # type: ignore[list-item]
                ["python", "-m", "pytest"],  # type: ignore[list-item]
            ],
            tmp_path,
        )
        assert len(results) == 3
        assert "expected dict, got str" in results[1].stderr
        assert "expected dict, got list" in results[2].stderr
        assert not results[1].passed
        assert not results[2].passed

    @patch("navi_bootstrap.validate.subprocess.run")
    def test_rejects_non_string_command(self, mock_run: MagicMock, tmp_path: Path) -> None:
        # Copilot-flagged case: command field is a list instead of a string.
        # subprocess.run with shell=True would crash or behave unexpectedly.
        results = run_validations(
            [
                {"description": "listy command", "command": ["python", "-m", "pytest"]},
                {"description": "missing command"},
            ],
            tmp_path,
        )
        assert len(results) == 2
        assert not results[0].passed
        assert "expected str, got list" in results[0].stderr
        assert not results[1].passed
        assert "expected str, got NoneType" in results[1].stderr
        mock_run.assert_not_called()
