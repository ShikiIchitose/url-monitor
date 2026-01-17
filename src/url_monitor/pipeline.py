from __future__ import annotations

from pathlib import Path
from typing import Any

import requests

from .http import check_url
from .io import load_urls
from .model import CheckResult
from .report import render_report_md
from .stats import summarize


def run_monitor(
    urls_path: Path,
    *,
    timeout: float = 5.0,
    strict: bool = False,
) -> tuple[list[CheckResult], dict[str, Any], str, list[str]]:
    urls, invalids = load_urls(str(urls_path), strict=strict)

    results: list[CheckResult] = []
    with requests.Session() as sess:
        for u in urls:
            results.append(check_url(u, timeout=timeout, session=sess))

    summary = summarize(results)
    report_md = render_report_md(
        source=str(urls_path),
        summary=summary,
        results=results,
        invalids=invalids,
    )
    return results, summary, report_md, invalids
