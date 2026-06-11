from __future__ import annotations

import dataclasses
import json
import re
import sys
import time
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
from typing import Any

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


_REDACTED_VALUE = "***REDACTED***"
_SENSITIVE_QUERY_PARAMS = {
    "secret",
    "app_secret",
    "client_secret",
    "access_token",
    "access-token",
    "refresh_token",
    "id_token",
    "token",
    "authorization",
}
_SECRET_QUERY_RE = re.compile(
    r"(?i)([?&](?:secret|app_secret|client_secret|access_token|access-token|refresh_token|id_token|token|authorization)=)([^&\s#]+)"
)


class HttpClient:
    def __init__(self, *, timeout_s: float, verbose: bool, user_agent: str):
        self._timeout_s = timeout_s
        self._verbose = verbose
        self._session = requests.Session()
        self._session.headers["User-Agent"] = user_agent

    @staticmethod
    def _sanitize_url(url: str) -> str:
        if not url:
            return url
        parsed = urlsplit(url)
        if not parsed.query:
            return url
        query_pairs = parse_qsl(parsed.query, keep_blank_values=True)
        sanitized: list[tuple[str, str]] = []
        changed = False
        for key, value in query_pairs:
            if str(key).lower() in _SENSITIVE_QUERY_PARAMS:
                sanitized.append((key, _REDACTED_VALUE))
                changed = True
            else:
                sanitized.append((key, value))
        if not changed:
            return url
        return urlunsplit((parsed.scheme, parsed.netloc, parsed.path, urlencode(sanitized, doseq=True), parsed.fragment))

    @staticmethod
    def _collect_sensitive_values(params: dict[str, Any] | None) -> set[str]:
        values: set[str] = set()
        if not params:
            return values
        for key, value in params.items():
            if str(key).lower() in _SENSITIVE_QUERY_PARAMS:
                text = str(value)
                if text:
                    values.add(text)
        return values

    @classmethod
    def _redact_secret_values(cls, text: str, *, sensitive_values: set[str] | None = None) -> str:
        safe = _SECRET_QUERY_RE.sub(r"\1" + _REDACTED_VALUE, text)
        for value in sorted(sensitive_values or set(), key=len, reverse=True):
            if value:
                safe = safe.replace(value, _REDACTED_VALUE)
        return safe

    @staticmethod
    def _format_url(url: str, params: dict[str, Any] | None) -> str:
        if not params:
            return url
        try:
            return HttpClient._sanitize_url(requests.Request("GET", url, params=params).prepare().url or url)
        except Exception:
            return HttpClient._sanitize_url(url)

    def request(
        self,
        method: str,
        url: str,
        *,
        headers: dict[str, str] | None = None,
        params: dict[str, Any] | None = None,
        json_body: Any | None = None,
        data: dict[str, Any] | None = None,
        files: dict[str, Any] | None = None,
        retries: int = 0,
        retry_on: tuple[int, ...] = (429, 500, 502, 503, 504),
    ) -> HttpResponse:
        attempt = 0
        display_url = self._format_url(url, params)
        redacted_display_url = self._sanitize_url(display_url)
        sensitive_values = self._collect_sensitive_values(params)
        while True:
            attempt += 1
            start = time.time()
            if self._verbose:
                print(f"[http] {method} {redacted_display_url} (start)", file=sys.stderr)
            try:
                resp = self._session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    params=params,
                    json=json_body,
                    data=data,
                    files=files,
                    timeout=self._timeout_s,
                )
            except requests.RequestException as e:
                ms = int((time.time() - start) * 1000)
                error_text = self._redact_secret_values(
                    f"{type(e).__name__}: {e}",
                    sensitive_values=sensitive_values,
                )
                if self._verbose:
                    print(
                        f"[http] {method} {redacted_display_url} -> EXCEPTION ({ms}ms): {error_text}",
                        file=sys.stderr,
                    )
                raise RuntimeError(
                    f"Request failed for {method} {redacted_display_url}: {error_text}"
                ) from e

            ms = int((time.time() - start) * 1000)
            if self._verbose:
                print(
                    f"[http] {method} {self._sanitize_url(str(resp.url))} -> {resp.status_code} ({ms}ms)",
                    file=sys.stderr,
                )

            if resp.status_code < 400:
                return HttpResponse(
                    status=resp.status_code,
                    headers={k.lower(): v for k, v in resp.headers.items()},
                    body=resp.content,
                    url=self._sanitize_url(str(resp.url)),
                )

            if attempt <= retries and resp.status_code in retry_on:
                time.sleep(min(2**attempt, 10))
                continue

            response_body = str(getattr(resp, "text", ""))
            redacted_text = self._redact_secret_values(
                response_body,
                sensitive_values=sensitive_values,
            )
            raise RuntimeError(
                f"HTTP {resp.status_code} for {method} {self._sanitize_url(str(resp.url))}\n{redacted_text}"
            )
