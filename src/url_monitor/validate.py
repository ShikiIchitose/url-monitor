# SPDX-License-Identifier: MIT
"""Validate URLs."""

from __future__ import annotations

from typing import Optional
from urllib.parse import urlparse


def is_valid_url(url: str) -> bool:
    """
    Basic URL validation:
    - scheme must be http/https
    - netloc must exist
    """
    p = urlparse(url)
    return (p.scheme in ("http", "https")) and bool(p.netloc)


def classify_status(status_code: Optional[int]) -> str:
    if status_code is None:
        return "other"

    if 200 <= status_code <= 299:
        return "2xx"
    if 300 <= status_code <= 399:
        return "3xx"
    if 400 <= status_code <= 499:
        return "4xx"
    if 500 <= status_code <= 599:
        return "5xx"
    return "other"
