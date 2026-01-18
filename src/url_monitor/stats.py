# SPDX-License-Identifier: MIT
"""Compute summary statistics for URL check results."""

from __future__ import annotations

import statistics
from typing import Any, Iterable

from .model import CheckResult
from .validate import classify_status


def _p95_inclusive(values: list[float]) -> float | None:
    # 95th percentile via n=20 (each 5%), inclusive method
    if len(values) < 20:
        return None
    return statistics.quantiles(values, n=20, method="inclusive")[-1]


def summarize(results: Iterable[CheckResult]) -> dict[str, Any]:
    results = list(results)

    total = len(results)
    ok_count = sum(1 for r in results if r.ok)
    fail_count = total - ok_count

    http_failures = [
        r
        for r in results
        if (not r.ok) and (r.status_code is not None) and (r.error is None)
    ]
    exceptions = [r for r in results if (not r.ok) and (r.error is not None)]

    # Status breakdown (by status_code class; exceptions fall into "other")
    by_class: dict[str, int] = {"2xx": 0, "3xx": 0, "4xx": 0, "5xx": 0, "other": 0}
    for r in results:
        by_class[classify_status(r.status_code)] += 1

    # Success latency stats (only ok)
    success_elapsed = [
        r.elapsed_ms for r in results if r.ok and r.elapsed_ms is not None
    ]
    success_elapsed_f = [float(x) for x in success_elapsed]
    success_avg = statistics.mean(success_elapsed_f) if success_elapsed_f else None
    success_max = max(success_elapsed_f) if success_elapsed_f else None
    success_p95 = _p95_inclusive(success_elapsed_f)

    # Failure latency stats (non-ok; include both HTTP failures + exceptions if elapsed exists)
    failure_elapsed = [
        r.elapsed_ms for r in results if (not r.ok) and r.elapsed_ms is not None
    ]
    failure_elapsed_f = [float(x) for x in failure_elapsed]
    failure_avg = statistics.mean(failure_elapsed_f) if failure_elapsed_f else None
    failure_p95 = _p95_inclusive(failure_elapsed_f)

    # Slowest (top 5) overall by elapsed_ms
    slowest = sorted(
        (r for r in results if r.elapsed_ms is not None),
        key=lambda r: r.elapsed_ms,  # type: ignore[arg-type]
        reverse=True,
    )[:5]

    error_rate = (fail_count / total) if total else 0.0

    return {
        "total": total,
        "ok": ok_count,
        "fail": fail_count,
        "http_failures": len(http_failures),
        "exceptions": len(exceptions),
        "error_rate": error_rate,
        "by_status_class": by_class,
        "success_samples": len(success_elapsed_f),
        "success_max_ms": success_max,
        "success_avg_ms": success_avg,
        "success_p95_ms": success_p95,
        "failure_samples": len(failure_elapsed_f),
        "failure_avg_ms": failure_avg,
        "failure_p95_ms": failure_p95,
        "slowest": [
            {"url": r.url, "elapsed_ms": r.elapsed_ms, "status": r.status_code}
            for r in slowest
        ],
    }
