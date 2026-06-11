from __future__ import annotations

import dataclasses
import json
import re
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
    def __init__(self, *, timeout_s: float, verbose: bool, user_agent: str):
        self._timeout_s = timeout_s
        self._verbose = verbose
        self._session = requests.Session()
        self._session.headers["User-Agent"] = user_agent

    @staticmethod
    def redact_text(text: str) -> str:
        try:
            safe = str(text)
        except Exception:
            return text

        safe = re.sub(
            r"(?i)((?:access_token|refresh_token|client_secret|token|code|secret|app_secret)=)[^&\s]+",
            lambda match: f"{match.group(1)}***REDACTED***",
            safe,
        )

        for key in ("access_token", "refresh_token", "client_secret", "token", "code"):
            safe = re.sub(
                rf"(?i)([\"']?{key}[\"']?\s*[:=]\s*[\"'])([^\"']+)([\"'])",
                lambda match: f"{match.group(1)}***REDACTED***{match.group(3)}",
                safe,
            )
        return safe

    @classmethod
    def redact_url(cls, url: str) -> str:
        return cls.redact_text(url)

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
        redacted_display_url = self.redact_url(display_url)
        while True:
            attempt += 1
            start = time.time()
            if self._verbose:
                print(f"[http] {method} {redacted_display_url} (start)", file=sys.stderr)
            try:
                resp = self._session.request(
                    method,
                    url,
                    headers=headers,
                    params=params,
                    json=json_body,
                    data=data,
                    timeout=self._timeout_s,
                )
            except requests.RequestException as e:
                ms = int((time.time() - start) * 1000)
                safe_err = self.redact_text(str(e))
                if self._verbose:
                    print(
                        f"[http] {method} {redacted_display_url} -> EXCEPTION ({ms}ms): {type(e).__name__}: {safe_err}",
                        file=sys.stderr,
                    )
                raise RuntimeError(
                    f"Request failed for {method} {redacted_display_url}: {type(e).__name__}: {safe_err}"
                ) from e
            ms = int((time.time() - start) * 1000)
            if self._verbose:
                print(
                    f"[http] {method} {self.redact_url(resp.url)} -> {resp.status_code} ({ms}ms)",
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

            raise RuntimeError(
                f"HTTP {resp.status_code} for {method} {self.redact_url(resp.url)}\n"
                f"{self.redact_text(resp.text)}"
            )
