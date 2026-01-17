# SPDX-License-Identifier: MIT
"""Module entry point for `python -m url_monitor`."""

from __future__ import annotations

from .cli import main

if __name__ == "__main__":
    raise SystemExit(main())
