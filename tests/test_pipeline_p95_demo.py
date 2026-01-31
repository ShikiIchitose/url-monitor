import pytest

from url_monitor.pipeline import run_monitor


def test_run_monitor_p95_demo_offline(monkeypatch, tmp_path, requests_mock):
    # Replace load_urls to avoid file I/O and make the test deterministic
    urls = [f"https://demo.test/{i}" for i in range(20)]

    def fake_load_urls(_path, strict):
        return urls, []

    monkeypatch.setattr("url_monitor.pipeline.load_urls", fake_load_urls)

    # Return 200 for all URLs (zero external network)
    for u in urls:
        requests_mock.get(u, status_code=200)

    # Advance perf_counter deterministically so that each URL has elapsed 1..20 ms.
    # Enforce: perf_counter is called exactly twice per URL (start/end).
    expected_calls = len(urls) * 2

    # Precompute [start1, end1, start2, end2, ...] where elapsed is 1..20 ms.
    t = 0.0
    timeline: list[float] = []
    for ms in range(1, len(urls) + 1):
        timeline.append(t)  # start
        t += ms / 1000.0  # end = start + ms
        timeline.append(t)  # end

    times = iter(timeline)
    calls = 0

    def fake_perf_counter() -> float:
        nonlocal calls
        calls += 1
        try:
            return next(times)
        except StopIteration:
            raise AssertionError(
                f"perf_counter called more than expected ({expected_calls})"
            ) from None

    monkeypatch.setattr("url_monitor.http.time.perf_counter", fake_perf_counter)

    dummy_path = tmp_path / "dummy.txt"
    dummy_path.write_text("https://will-not-be-read.test\n", encoding="utf-8")

    results, summary, report_md, invalids = run_monitor(
        dummy_path,
        timeout=1.0,
        strict=False,
    )

    assert len(results) == 20
    assert summary["success_samples"] == 20
    # expected_calls twice per URL for 20 URLs ==> 40
    assert len(urls) == 20
    assert calls == expected_calls
    # statistics.quantiles(..., n=20, method="inclusive") for 1..20 => 19.05
    p95 = summary["success_p95_ms"]
    assert p95 is not None, "expected p95 to be computed (got None)"
    assert p95 == pytest.approx(19.05, abs=1e-9)
    assert "# URL Monitor Report" in report_md
    assert invalids == []
