"""Tests for RaindropClient - no network, a fake session is injected.

They pin the gotchas documented in raindrop.py: result:false with an
errorMessage is an error, result:false without one is a valid response, 429 is
retried, non-2xx raises.
"""
from __future__ import annotations

import json as _json

import pytest

from src.raindrop import RaindropClient, RaindropError


class FakeResp:
    def __init__(self, status, payload=None, raw=None, headers=None):
        self.status_code = status
        self._payload = payload
        self.content = (raw if raw is not None else (_json.dumps(payload).encode() if payload is not None else b""))
        self.text = self.content.decode("utf-8", "replace")
        self.headers = headers or {}

    def json(self):
        if self._payload is None:
            raise ValueError("no json")
        return self._payload


class FakeSession:
    """Hands back the scheduled responses in order and counts the requests."""

    def __init__(self, responses):
        self._responses = list(responses)
        self.calls = []

    def request(self, method, url, **kw):
        self.calls.append((method, url, kw))
        return self._responses.pop(0)


def _client(responses):
    sess = FakeSession(responses)
    c = RaindropClient("tok", max_retries=4, session=sess)
    c.retry_base_delay = 0  # no real sleeping in a test
    return c, sess


def test_result_true_returns_data():
    c, _ = _client([FakeResp(200, {"result": True, "items": [1, 2]})])
    assert c.call("GET", "/x") == {"result": True, "items": [1, 2]}


def test_result_false_with_error_message_raises():
    c, _ = _client([FakeResp(200, {"result": False, "errorMessage": "bad thing"})])
    with pytest.raises(RaindropError) as ei:
        c.call("POST", "/collection", json={"title": ""})
    assert "bad thing" in str(ei.value)


def test_result_false_without_error_is_valid_response():
    # import/url/exists: {"result": false, "ids": []} is a CORRECT response, not an error
    c, _ = _client([FakeResp(200, {"result": False, "ids": []})])
    assert c.call("POST", "/import/url/exists", json={"urls": ["x"]}) == {"result": False, "ids": []}


def test_non_2xx_raises_with_status():
    c, _ = _client([FakeResp(403, {"result": False}, raw=b'{"result":false}')])
    with pytest.raises(RaindropError) as ei:
        c.call("GET", "/raindrop/1/suggest")
    assert "403" in str(ei.value)


def test_retry_on_429_then_success():
    c, sess = _client([
        FakeResp(429, raw=b"slow down", headers={"Retry-After": "0"}),
        FakeResp(200, {"result": True, "ok": 1}),
    ])
    assert c.call("GET", "/x") == {"result": True, "ok": 1}
    assert len(sess.calls) == 2  # one 429, one 200


def test_retry_exhausted_raises():
    c, _ = _client([FakeResp(500, raw=b"boom") for _ in range(4)])
    with pytest.raises(RaindropError):
        c.call("GET", "/x")


def test_empty_body_returns_empty_dict():
    c, _ = _client([FakeResp(200, payload=None, raw=b"")])
    assert c.call("DELETE", "/collection/1") == {}


def test_download_returns_bytes_and_ctype():
    c, _ = _client([FakeResp(200, raw=b"a,b,c\n1,2,3", headers={"Content-Type": "text/csv"})])
    content, ctype = c.download("/raindrops/0/export.csv")
    assert content == b"a,b,c\n1,2,3"
    assert ctype == "text/csv"
