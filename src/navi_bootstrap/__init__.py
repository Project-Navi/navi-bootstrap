# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Project Navi

"""navi-bootstrap: Jinja2 rendering engine and template packs."""

from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as _pkg_version

from navi_bootstrap.packs import get_ordered_packs
from navi_bootstrap.spec import build_spec_for_new

# Single-source the version from installed package metadata so __init__.py
# tracks pyproject.toml automatically. The fallback only triggers when the
# package isn't installed (uncommon: editable-install dev sessions where the
# package was deleted, or a source checkout being imported via PYTHONPATH
# without `pip install -e .`). Downstream consumers — notably the SARIF
# `tool.driver.version` field emitted by `nboot audit` — must tolerate the
# `0.0.0+unknown` form. The pragma excludes it from coverage because it
# only fires in that uncommon dev configuration and isn't worth simulating
# in tests.
try:
    __version__ = _pkg_version("navi-bootstrap")
except PackageNotFoundError:  # pragma: no cover — only during dev without install
    __version__ = "0.0.0+unknown"

__all__ = ["__version__", "build_spec_for_new", "get_ordered_packs"]
