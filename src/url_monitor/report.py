# SPDX-License-Identifier: MIT
"""Render a Markdown report for URL check results."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from .model import CheckResult


def _fmt_ms(x: float | None) -> str:
    if x is None:
        return "n/a"
    return f"{x:.1f} ms"


def _fmt_pct(x: float | None) -> str:
    if x is None:
        return "n/a"
    return f"{x * 100.0:.1f}%"


def _md_escape(text: str) -> str:
    # Minimal escaping for Markdown tables
    return text.replace("|", "\\|")


def render_report_md(
    *,
    source: str,
    summary: dict[str, Any],
    results: list[CheckResult],
    invalids: list[str] | None = None,
) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")

    total = summary.get("total", 0)
    ok = summary.get("ok", 0)
    fail = summary.get("fail", 0)

    http_failures_rows = [
        r
        for r in results
        if (not r.ok) and (r.status_code is not None) and (r.error is None)
    ]
    exceptions = [r for r in results if r.error]

    lines: list[str] = []
    lines.append("# URL Monitor Report")
    lines.append("")
    lines.append(f"- Generated (UTC): {now}")
    lines.append(f"- Source: `{_md_escape(source)}`")
    lines.append("")

    # ---- Summary ----
    lines.append("## Summary")
    lines.append(f"- Total checks: **{total}**")
    lines.append(f"- OK: **{ok}**")
    lines.append(f"- FAIL: **{fail}**")
    lines.append(
        f"  - HTTP failures (non-OK status): **{summary.get('http_failures', 0)}**"
    )
    lines.append(f"  - Exceptions: **{summary.get('exceptions', 0)}**")
    lines.append(f"- Error rate: **{_fmt_pct(summary.get('error_rate'))}**")
    lines.append(
        f"- Success samples (latency): **{summary.get('success_samples', 0)}**"
    )
    lines.append(
        f"- Max latency (success): **{_fmt_ms(summary.get('success_max_ms'))}**"
    )
    lines.append(
        f"- Average latency (success): **{_fmt_ms(summary.get('success_avg_ms'))}**"
    )
    lines.append(
        f"- p95 latency (success): **{_fmt_ms(summary.get('success_p95_ms'))}**"
    )
    lines.append(
        f"- Failure samples (latency): **{summary.get('failure_samples', 0)}**"
    )
    lines.append(
        f"- Average latency (failure): **{_fmt_ms(summary.get('failure_avg_ms'))}**"
    )
    lines.append(
        f"- p95 latency (failure): **{_fmt_ms(summary.get('failure_p95_ms'))}**"
    )
    lines.append("")

    # ---- Status breakdown ----
    lines.append("## Status breakdown")
    lines.append("| Class | Count |")
    lines.append("|---|---:|")
    by_class = summary.get("by_status_class", {})
    for k in ["2xx", "3xx", "4xx", "5xx", "other"]:
        lines.append(f"| {k} | {by_class.get(k, 0)} |")
    lines.append("")

    # ---- Slowest ----
    lines.append("## Slowest URLs (top 5)")
    lines.append("| URL | Status | Elapsed |")
    lines.append("|---|---:|---:|")
    for item in summary.get("slowest", []):
        url = _md_escape(str(item.get("url", "")))
        status = item.get("status", None)
        elapsed_ms = item.get("elapsed_ms", None)
        lines.append(
            f"| `{url}` | {status if status is not None else 'n/a'} | {_fmt_ms(elapsed_ms)} |"
        )
    lines.append("")

    # ---- HTTP failures (non-OK) ----
    lines.append("## HTTP failures (non-OK status)")
    if not http_failures_rows:
        lines.append("- (none)")
        lines.append("")
    else:
        lines.append("| URL | Status | Elapsed |")
        lines.append("|---|---:|---:|")

        # Prefer rows sorted by elapsed_ms desc; include rows with elapsed_ms=None at the end.
        items_with_elapsed = [r for r in http_failures_rows if r.elapsed_ms is not None]
        items_no_elapsed = [r for r in http_failures_rows if r.elapsed_ms is None]

        items_with_elapsed.sort(key=lambda r: r.elapsed_ms, reverse=True)  # type: ignore[arg-type]

        # Deduplicate by URL; cap at top 10
        seen: set[str] = set()
        rows: list[CheckResult] = []
        for r in items_with_elapsed + items_no_elapsed:
            if r.url in seen:
                continue
            seen.add(r.url)
            rows.append(r)
            if len(rows) >= 10:
                break

        for r in rows:
            lines.append(
                f"| `{_md_escape(r.url)}` | {r.status_code if r.status_code is not None else 'n/a'} | {_fmt_ms(r.elapsed_ms)} |"
            )
        lines.append("")

    # ---- Exceptions ----
    lines.append("## Exceptions")
    if not exceptions:
        lines.append("- (none)")
    else:
        for r in exceptions:
            lines.append(f"- `{_md_escape(r.url)}`: **{_md_escape(r.error or '')}**")
    lines.append("")

    # ---- Invalid inputs (when strict=False) ----
    lines.append("## Invalid input lines")
    if not invalids:
        lines.append("- (none)")
    else:
        for msg in invalids:
            lines.append(f"- {_md_escape(msg)}")
    lines.append("")

    return "\n".join(lines)
