# SPDX-License-Identifier: MIT
"""Command-line interface for URL monitor."""

from __future__ import annotations

import argparse
from pathlib import Path

from .outputs import save_outputs
from .pipeline import run_monitor


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="url-monitor")
    p.add_argument(
        "--input", default="urls.txt", help="Path to input file (default: urls.txt)"
    )
    p.add_argument(
        "--out",
        default="report.md",
        help="Path to output report.md (default: report.md)",
    )
    p.add_argument(
        "--out-dir",
        default=None,
        help="If set, write report.md + results.json into OUT_DIR directory",
    )
    p.add_argument(
        "--timeout",
        type=float,
        default=5.0,
        help="Request timeout seconds (default: 5.0)",
    )
    p.add_argument(
        "--strict", action="store_true", help="Fail fast on invalid input URLs"
    )
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    input_path = Path(args.input)

    results, summary, report_md, _invalids = run_monitor(
        input_path,
        timeout=float(args.timeout),
        strict=bool(args.strict),
    )

    if args.out_dir:
        out_dir = Path(args.out_dir)
        save_outputs(
            results=results,
            summary=summary,
            report_md=report_md,
            source=str(input_path),
            out_dir=out_dir,
        )
        print(f"Wrote: {out_dir / 'report.md'}")
        print(f"Wrote: {out_dir / 'results.json'}")
    else:
        out_path = Path(args.out)
        out_path.write_text(report_md, encoding="utf-8")
        print(f"Wrote: {out_path}")

    return 0
