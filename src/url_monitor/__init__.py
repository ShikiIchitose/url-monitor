# SPDX-License-Identifier: MIT
"""URL monitor that checks endpoints and generates a Markdown report.

Public API:
- run_monitor: run checks + compute summary + render report
- save_outputs: write report.md and results.json
"""

from __future__ import annotations

from .outputs import save_outputs
from .pipeline import run_monitor

__all__ = ["run_monitor", "save_outputs"]
