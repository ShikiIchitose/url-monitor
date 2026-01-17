# SPDX-License-Identifier: MIT
"""Input/output utilities."""

from __future__ import annotations

from pathlib import Path
from typing import Tuple

from .validate import is_valid_url


def load_urls(path: str, *, strict: bool = True) -> Tuple[list[str], list[str]]:
    """
    Load URLs from a text file.

    Rules:
    - Strip whitespace
    - Skip blank lines and comments starting with '#'
    - Validate URL (http/https + netloc)

    Returns:
      (urls, invalids)
    """
    p = Path(path)
    lines = p.read_text(encoding="utf-8").splitlines()

    urls: list[str] = []
    invalids: list[str] = []

    for i, raw in enumerate(lines, start=1):
        s = raw.strip()
        if not s or s.startswith("#"):
            continue

        if is_valid_url(s):
            urls.append(s)
        else:
            msg = f"{p.name}:{i}: Invalid URL: {s!r}"
            if strict:
                raise ValueError(msg)
            invalids.append(msg)

    return urls, invalids
