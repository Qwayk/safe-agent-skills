from __future__ import annotations

import dataclasses
import json
import sys
import time
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


class HttpClient:
    def __init__(
        self,
        *,
        timeout_s: float,
        verbose: bool,
        user_agent: str,
        redacted_values: tuple[str, ...] = (),
    ):
        self._timeout_s = timeout_s
        self._verbose = verbose
        self._redacted_values = tuple(v for v in redacted_values if v and v != "1")
        self._session = requests.Session()
        self._session.headers["User-Agent"] = user_agent

    def _redact_text(self, text: str) -> str:
        clean = text
        for value in sorted(set(self._redacted_values), key=len, reverse=True):
            clean = clean.replace(value, "***REDACTED***")
        return clean

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
        retries: int = 0,
        retry_on: tuple[int, ...] = (429, 500, 502, 503, 504),
    ) -> HttpResponse:
        attempt = 0
        display_url = self._redact_text(self._format_url(url, params))
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
                    timeout=self._timeout_s,
                )
            except requests.RequestException as exc:
                ms = int((time.time() - start) * 1000)
                if self._verbose:
                    print(
                        f"[http] {method} {display_url} -> EXCEPTION ({ms}ms): {type(exc).__name__}: {self._redact_text(str(exc))}",
                        file=sys.stderr,
                    )
                raise RuntimeError(
                    f"Request failed for {method} {display_url}: {type(exc).__name__}: {self._redact_text(str(exc))}"
                ) from exc

            ms = int((time.time() - start) * 1000)
            safe_response_url = self._redact_text(str(resp.url))
            if self._verbose:
                print(f"[http] {method} {safe_response_url} -> {resp.status_code} ({ms}ms)", file=sys.stderr)

            if resp.status_code < 400:
                return HttpResponse(
                    status=resp.status_code,
                    headers={k.lower(): v for k, v in resp.headers.items()},
                    body=resp.content,
                    url=str(resp.url),
                )

            if attempt <= retries and resp.status_code in retry_on:
                time.sleep(min(2**attempt, 10))
                continue

            body_text = self._redact_text(resp.text.strip())
            body_preview = body_text[:400] if body_text else "No response body"
            raise RuntimeError(f"HTTP {resp.status_code} for {method} {safe_response_url}: {body_preview}")
