# SPDX-License-Identifier: MIT
"""Checking URLs with HTTP utilities."""

from __future__ import annotations

import time
from typing import Optional

import requests

from .model import CheckResult


def check_url(
    url: str,
    *,
    timeout: float = 5.0,
    session: Optional[requests.Session] = None,
) -> CheckResult:
    """
    Perform HTTP GET and return CheckResult.

    ok:
      - True only for 2xx responses
      - False for non-2xx responses and exceptions
    """
    owns_session = session is None
    sess = session or requests.Session()

    t0 = time.perf_counter()
    try:
        resp = sess.get(url, timeout=timeout)
        elapsed_ms = (time.perf_counter() - t0) * 1000.0

        status_code = resp.status_code
        ok = 200 <= status_code <= 299
        return CheckResult(
            url=url,
            ok=ok,
            status_code=status_code,
            elapsed_ms=elapsed_ms,
            error=None,
        )
    except requests.RequestException as e:
        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        return CheckResult(
            url=url,
            ok=False,
            status_code=None,
            elapsed_ms=elapsed_ms,
            error=f"{type(e).__name__}: {e}",
        )
    finally:
        if owns_session:
            sess.close()
