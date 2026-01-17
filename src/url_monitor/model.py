# SPDX-License-Identifier: MIT
"""Model for URL check results."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class CheckResult:
    url: str
    ok: bool
    status_code: Optional[int]
    elapsed_ms: Optional[float]
    error: Optional[str]
