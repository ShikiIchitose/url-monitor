from url_monitor.model import CheckResult
from url_monitor.report import render_report_md
from url_monitor.stats import summarize


def test_render_report_has_sections():
    results = [
        CheckResult("https://a", True, 200, 10.0, None),
        CheckResult("https://b", False, 404, 20.0, None),
        CheckResult("https://c", False, None, 5.0, "Timeout"),
    ]
    summary = summarize(results)
    md = render_report_md(
        source="urls.txt",
        summary=summary,
        results=results,
        invalids=["urls.txt:1: Invalid URL: 'x'"],
    )
    assert "# URL Monitor Report" in md
    assert "## Summary" in md
    assert "## Status breakdown" in md
    assert "## Slowest URLs (top 5)" in md
    assert "## HTTP failures (non-OK status)" in md
    assert "## Exceptions" in md
    assert "## Invalid input lines" in md
