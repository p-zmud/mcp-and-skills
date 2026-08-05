"""A thin client for the Raindrop.io REST API v1.

Auth:  the ``Authorization: Bearer {token}`` header.
Base:  https://api.raindrop.io/rest/v1  ->  paths start with ``/...``.

Gotchas (verified against the live API):
- Some responses are HTTP 200 plus ``{"result": false, "errorMessage": ...}`` -
  we treat that as an ERROR. BUT ``import/url/exists`` returns
  ``{"result": false, "ids": []}`` with no ``errorMessage`` when nothing matched,
  and that is a CORRECT response, not an error. So we only raise when
  result==False AND an errorMessage/error field is present.
- Collection export and backup download return RAW bytes (CSV/HTML/ZIP), not
  JSON -> the ``download`` method.
- File and cover upload is multipart/form-data -> the ``upload`` method.
- Rate limit is roughly 120 req/min -> retry 429/5xx with exponential backoff.
- ``/raindrop/{id}/suggest`` and ``/raindrop/suggest`` are Pro features -> on a
  free account they return HTTP 403 (the client raises a readable RaindropError).
"""
from __future__ import annotations

import time
from typing import Any

import requests

from .config import API_BASE

_RETRYABLE = {429, 500, 502, 503, 504}


class RaindropError(RuntimeError):
    """A transport error, a non-2xx response, or result:false with an errorMessage."""


class RaindropClient:
    def __init__(
        self,
        token: str,
        timeout: int = 30,
        max_retries: int = 4,
        session: requests.Session | None = None,
    ):
        self.token = token
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_base_delay = 1.0
        self._session = session or requests.Session()
        self._auth = {"Authorization": f"Bearer {token}"}
        self._headers = {**self._auth, "Content-Type": "application/json"}

    # --- transport --------------------------------------------------------
    def _send(
        self,
        method: str,
        path: str,
        *,
        params: dict | None = None,
        json: dict | None = None,
        headers: dict | None = None,
        files: dict | None = None,
        data: dict | None = None,
    ) -> requests.Response:
        """A request with retries on 429/5xx. Raises RaindropError on non-2xx.

        Every tool goes through this helper, so auth, timeout and backoff come
        for free. ``files``/``data`` are for multipart (no JSON header).
        """
        url = f"{API_BASE}{path}"
        hdrs = headers if headers is not None else (self._auth if files else self._headers)
        last: RaindropError | None = None
        for attempt in range(self.max_retries):
            try:
                resp = self._session.request(
                    method,
                    url,
                    headers=hdrs,
                    params=params,
                    json=json,
                    files=files,
                    data=data,
                    timeout=self.timeout,
                )
            except requests.exceptions.RequestException as e:
                last = RaindropError(f"{method} {path} transport error: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_base_delay * (2**attempt))
                continue
            if resp.status_code in _RETRYABLE and attempt < self.max_retries - 1:
                # Respect Retry-After when the API sends one (in seconds).
                delay = self.retry_base_delay * (2**attempt)
                ra = resp.headers.get("Retry-After")
                if ra and ra.isdigit():
                    delay = max(delay, float(ra))
                time.sleep(delay)
                continue
            if resp.status_code // 100 != 2:
                raise RaindropError(
                    f"{method} {path} HTTP {resp.status_code}: {resp.text[:300]}"
                )
            return resp
        raise last or RaindropError(f"{method} {path}: retries exhausted")

    # --- JSON API ---------------------------------------------------------
    def call(
        self, method: str, path: str, *, params: dict | None = None, json: dict | None = None
    ) -> Any:
        """A request returning JSON. Raises RaindropError on result:false + errorMessage."""
        resp = self._send(method, path, params=params, json=json)
        if not resp.content:
            return {}
        data = resp.json()
        if isinstance(data, dict) and data.get("result") is False:
            err = data.get("errorMessage") or data.get("error")
            if err:
                raise RaindropError(f"{method} {path}: {err}")
        return data

    # --- raw files (export / backup) --------------------------------------
    def download(self, path: str, *, params: dict | None = None) -> tuple[bytes, str]:
        """A GET returning raw bytes plus the content type (export/backup)."""
        resp = self._send("GET", path, params=params)
        return resp.content, resp.headers.get("Content-Type", "")

    # --- multipart upload -------------------------------------------------
    def upload(self, path: str, *, files: dict, data: dict | None = None) -> Any:
        """A multipart/form-data PUT (file or cover upload). Returns JSON."""
        resp = self._send("PUT", path, files=files, data=data)
        if not resp.content:
            return {}
        out = resp.json()
        if isinstance(out, dict) and out.get("result") is False:
            err = out.get("errorMessage") or out.get("error")
            if err:
                raise RaindropError(f"PUT {path}: {err}")
        return out
