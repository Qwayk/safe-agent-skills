from __future__ import annotations

import dataclasses
import json
import sys
import time
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

import requests


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
    def _redact_url(url: str) -> str:
        try:
            parts = urlsplit(url)
        except Exception:
            return url
        if not parts.query:
            return url

        sensitive = {"key", "token", "access_token", "refresh_token", "api_key", "password"}
        q = []
        for k, v in parse_qsl(parts.query, keep_blank_values=True):
            if str(k).casefold() in sensitive:
                q.append((k, "<redacted>"))
            else:
                q.append((k, v))
        try:
            new_query = urlencode(q, doseq=True)
        except Exception:
            return url
        return urlunsplit((parts.scheme, parts.netloc, parts.path, new_query, parts.fragment))

    @staticmethod
    def _format_url(url: str, params: dict[str, Any] | None) -> str:
        if not params:
            return HttpClient._redact_url(url)
        try:
            formatted = requests.Request("GET", url, params=params).prepare().url or url
            return HttpClient._redact_url(formatted)
        except Exception:
            return HttpClient._redact_url(url)

    def request(
        self,
        method: str,
        url: str,
        *,
        headers: dict[str, str] | None = None,
        params: dict[str, Any] | None = None,
        json_body: dict[str, Any] | None = None,
        files: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
        retries: int = 0,
        retry_on: tuple[int, ...] = (429, 500, 502, 503, 504),
    ) -> HttpResponse:
        attempt = 0
        display_url = self._format_url(url, params)
        while True:
            attempt += 1
            start = time.time()
            if self._verbose:
                print(f"[http] {method} {display_url} (start)", file=sys.stderr)
            try:
                resp = self._session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    params=params,
                    json=json_body,
                    files=files,
                    data=data,
                    timeout=self._timeout_s,
                )
            except requests.RequestException as e:
                ms = int((time.time() - start) * 1000)
                if self._verbose:
                    print(
                        f"[http] {method} {display_url} -> EXCEPTION ({ms}ms): {type(e).__name__}",
                        file=sys.stderr,
                    )
                raise RuntimeError(f"Request failed for {method} {display_url}: {type(e).__name__}") from e
            ms = int((time.time() - start) * 1000)
            if self._verbose:
                print(f"[http] {method} {self._redact_url(resp.url)} -> {resp.status_code} ({ms}ms)", file=sys.stderr)

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

            raise RuntimeError(f"HTTP {resp.status_code} for {method} {self._redact_url(resp.url)}\n{resp.text}")
