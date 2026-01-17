# SPDX-License-Identifier: MIT
"""Save outputs to files."""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from .model import CheckResult


def save_outputs(
    *,
    results: list[CheckResult],
    summary: dict[str, Any],
    report_md: str,
    source: str,
    out_dir: Path,
) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)

    payload = {
        "source": source,
        "summary": summary,
        "results": [asdict(r) for r in results],
    }

    (out_dir / "results.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (out_dir / "report.md").write_text(report_md, encoding="utf-8")
