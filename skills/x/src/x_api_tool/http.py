from __future__ import annotations

import dataclasses
import json
import sys
import time
import urllib.parse
from typing import Any

import requests


_SENSITIVE_QUERY_KEYS = {
    "access_token",
    "oauth_token",
    "token",
    "id_token",
    "refresh_token",
    "client_secret",
    "bearer_token",
    "authorization",
}

_SENSITIVE_HEADER_KEYS = {
    "authorization",
    "x-api-key",
    "x-auth-token",
    "x-access-token",
}


def redact_headers(headers: dict[str, str] | None) -> dict[str, str] | None:
    if headers is None:
        return None
    out: dict[str, str] = {}
    for k, v in headers.items():
        lk = str(k).lower()
        if lk in _SENSITIVE_HEADER_KEYS:
            out[str(k)] = "***REDACTED***"
        else:
            out[str(k)] = str(v)
    return out


def redact_query_params(params: dict[str, Any] | None) -> dict[str, Any] | None:
    if params is None:
        return None
    out: dict[str, Any] = {}
    for k, v in params.items():
        lk = str(k).lower()
        if lk in _SENSITIVE_QUERY_KEYS or lk.endswith("_token") or lk.endswith("_secret"):
            out[str(k)] = "***REDACTED***"
        else:
            out[str(k)] = v
    return out


def redact_url(url: str) -> str:
    try:
        parsed = urllib.parse.urlsplit(url)
        if not parsed.query:
            return url
        qs = urllib.parse.parse_qsl(parsed.query, keep_blank_values=True)
        safe_qs: list[tuple[str, str]] = []
        for k, v in qs:
            lk = (k or "").lower()
            if lk in _SENSITIVE_QUERY_KEYS or lk.endswith("_token") or lk.endswith("_secret"):
                safe_qs.append((k, "***REDACTED***"))
            else:
                safe_qs.append((k, v))
        safe_query = urllib.parse.urlencode(safe_qs, doseq=True)
        return urllib.parse.urlunsplit((parsed.scheme, parsed.netloc, parsed.path, safe_query, parsed.fragment))
    except Exception:
        return url


@dataclasses.dataclass(frozen=True)
class HttpResponse:
    status: int
    headers: dict[str, str]
    body: bytes
    url: str

    def json(self) -> Any:
        return json.loads(self.body.decode("utf-8"))

    def text(self) -> str:
        return self.body.decode("utf-8", errors="replace")


class HttpClient:
    def __init__(self, *, timeout_s: float, verbose: bool, user_agent: str):
        self._timeout_s = timeout_s
        self._verbose = verbose
        self._session = requests.Session()
        self._session.headers["User-Agent"] = user_agent

    @staticmethod
    def _format_url(url: str, params: dict[str, Any] | None) -> str:
        if not params:
            return url
        try:
            return requests.Request("GET", url, params=params).prepare().url or url
        except Exception:
            return url

    def request(
        self,
        method: str,
        url: str,
        *,
        headers: dict[str, str] | None = None,
        params: dict[str, Any] | None = None,
        json_body: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
        retries: int = 0,
        retry_on: tuple[int, ...] = (429, 500, 502, 503, 504),
    ) -> HttpResponse:
        attempt = 0
        display_url = self._format_url(url, params)
        while True:
            attempt += 1
            start = time.time()
            safe_display_url = redact_url(display_url)
            if self._verbose:
                print(f"[http] {method} {safe_display_url} (start)", file=sys.stderr)
            try:
                resp = self._session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    params=params,
                    json=json_body,
                    data=data,
                    timeout=self._timeout_s,
                )
            except requests.RequestException as e:
                ms = int((time.time() - start) * 1000)
                if self._verbose:
                    print(
                        f"[http] {method} {safe_display_url} -> EXCEPTION ({ms}ms): {type(e).__name__}: {e}",
                        file=sys.stderr,
                    )
                raise RuntimeError(
                    f"Request failed for {method} {safe_display_url}: {type(e).__name__}: {e}"
                ) from e
            ms = int((time.time() - start) * 1000)
            if self._verbose:
                print(
                    f"[http] {method} {redact_url(resp.url)} -> {resp.status_code} ({ms}ms)",
                    file=sys.stderr,
                )

            if resp.status_code < 400:
                return HttpResponse(
                    status=resp.status_code,
                    headers={k.lower(): v for k, v in resp.headers.items()},
                    body=resp.content,
                    url=resp.url,
                )

            if attempt <= retries and resp.status_code in retry_on:
                time.sleep(min(2**attempt, 10))
                continue

            raise RuntimeError(f"HTTP {resp.status_code} for {method} {redact_url(resp.url)}")
