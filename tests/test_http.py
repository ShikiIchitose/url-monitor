import requests

from url_monitor.http import check_url


def test_check_url_200(requests_mock):
    url = "https://example.test/ok"
    requests_mock.get(url, status_code=200)

    r = check_url(url, timeout=1.0, session=None)
    assert r.ok is True
    assert r.status_code == 200
    assert r.error is None
    assert r.elapsed_ms is not None
    assert r.elapsed_ms >= 0


def test_check_url_404_is_failure(requests_mock):
    url = "https://example.test/notfound"
    requests_mock.get(url, status_code=404)

    r = check_url(url, timeout=1.0, session=None)
    assert r.ok is False
    assert r.status_code == 404
    assert r.error is None
    assert r.elapsed_ms is not None
    assert r.elapsed_ms >= 0


def test_check_url_timeout(requests_mock):
    url = "https://example.test/timeout"
    requests_mock.get(url, exc=requests.exceptions.ConnectTimeout("boom"))

    r = check_url(url, timeout=0.01, session=None)
    assert r.ok is False
    assert r.status_code is None
    assert r.error is not None
    assert r.elapsed_ms is not None
    assert r.elapsed_ms >= 0
