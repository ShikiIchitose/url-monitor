import pytest

from url_monitor.validate import classify_status, is_valid_url


@pytest.mark.parametrize(
    ("url", "ok"),
    [
        ("https://example.com", True),
        ("http://example.net", True),
        ("htts://example.com", False),
        ("https:///delay/1", False),
    ],
)
def test_is_valid_url(url: str, ok: bool):
    assert is_valid_url(url) is ok


def test_classify_status():
    assert classify_status(200) == "2xx"
    assert classify_status(302) == "3xx"
    assert classify_status(404) == "4xx"
    assert classify_status(503) == "5xx"
    assert classify_status(None) == "other"
