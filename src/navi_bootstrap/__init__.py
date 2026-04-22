# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Project Navi

"""navi-bootstrap: Jinja2 rendering engine and template packs."""

from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as _pkg_version

from navi_bootstrap.packs import get_ordered_packs
from navi_bootstrap.spec import build_spec_for_new

try:
    __version__ = _pkg_version("navi-bootstrap")
except PackageNotFoundError:  # pragma: no cover — only during dev without install
    __version__ = "0.0.0+unknown"

__all__ = ["__version__", "build_spec_for_new", "get_ordered_packs"]
