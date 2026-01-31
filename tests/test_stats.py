import pytest

from url_monitor.model import CheckResult
from url_monitor.stats import summarize


def test_summarize_counts_smoke():
    results = [
        CheckResult("https://a", True, 200, 10.0, None),
        CheckResult("https://b", False, 404, 20.0, None),
        CheckResult("https://c", False, None, 5.0, "Timeout"),
    ]
    s = summarize(results)
    assert s["total"] == 3
    assert s["ok"] == 1
    assert s["fail"] == 2
    assert s["http_failures"] == 1
    assert s["exceptions"] == 1
    assert s["by_status_class"]["2xx"] == 1
    assert s["by_status_class"]["4xx"] == 1
    assert s["by_status_class"]["other"] == 1


def test_p95_demo_offline_is_deterministic():
    # 20 samples required by current implementation (_p95_inclusive uses n=20)
    results = [
        CheckResult(f"https://x{i}.test", True, 200, float(i), None)
        for i in range(1, 21)  # 1..20 ms
    ]
    s = summarize(results)

    assert s["success_samples"] == 20
    # statistics.quantiles(..., n=20, method="inclusive") for 1..20 => 19.05
    p95 = s["success_p95_ms"]
    assert p95 is not None, "expected p95 to be computed (got None)"
    assert p95 == pytest.approx(19.05, abs=1e-9)
