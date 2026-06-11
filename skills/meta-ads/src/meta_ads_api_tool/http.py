from __future__ import annotations

import dataclasses
import json
import random
import re
import sys
import time
from typing import Any

import requests

from .errors import NotSupportedError


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
    def redact_url(url: str) -> str:
        """
        Redact known secret-ish query params.

        Graph API pagination can include tokens in next URLs depending on how requests are made.
        Never print raw tokens to stderr.
        """
        try:
            return re.sub(r"(?i)(access_token=)[^&]+", r"\\1***REDACTED***", url)
        except Exception:
            return url

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
        if str(method).upper() != "GET":
            raise NotSupportedError(f"Refusing non-GET HTTP method: {method}")

        attempt = 0
        display_url = self._format_url(url, params)
        redacted_display_url = self.redact_url(display_url)
        while True:
            attempt += 1
            start = time.time()
            if self._verbose:
                print(
                    f"[http] {method} {redacted_display_url} (start)",
                    file=sys.stderr,
                )
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
                safe_err = self.redact_url(str(e))
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
                ra = resp.headers.get("Retry-After") or resp.headers.get("retry-after")
                if ra:
                    try:
                        sleep_s = float(ra)
                    except Exception:
                        sleep_s = 0.0
                else:
                    # Exponential backoff with light jitter.
                    sleep_s = min(2 ** (attempt - 1), 20.0) + random.uniform(0, 0.25)
                time.sleep(max(0.0, min(sleep_s, 30.0)))
                continue

            # Never include headers; and redact any token-looking query params.
            raise RuntimeError(
                f"HTTP {resp.status_code} for {method} {self.redact_url(resp.url)}\n{resp.text}"
            )
