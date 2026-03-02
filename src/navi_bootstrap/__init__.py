# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Project Navi

"""navi-bootstrap: Jinja2 rendering engine and template packs."""

from navi_bootstrap.packs import get_ordered_packs
from navi_bootstrap.spec import build_spec_for_new

__all__ = ["build_spec_for_new", "get_ordered_packs"]

__version__ = "0.1.1"
