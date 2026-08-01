from __future__ import annotations

import dataclasses
import json
import re
import sys
import time
from typing import Any
from urllib.parse import urlparse

import requests


@dataclasses.dataclass(frozen=True)
class HttpResponse:
    status: int
    headers: dict[str, str]
    body: bytes
    url: str
    attempts: int
    retry_after: int | None
    throttled: bool

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
        max_429_retries: int = 2,
    ):
        self._timeout_s = timeout_s
        self._verbose = verbose
        self._session = requests.Session()
        self._session.headers["User-Agent"] = user_agent
        self._max_429_retries = max_429_retries

    @staticmethod
    def _format_url(url: str, params: dict[str, Any] | None) -> str:
        if not params:
            return url
        try:
            return requests.Request("GET", url, params=params).prepare().url or url
        except Exception:
            return url

    @staticmethod
    def _ensure_https_api_host(url: str) -> None:
        parsed = urlparse(url)
        if parsed.scheme != "https":
            raise RuntimeError("Refused: unsafe scheme. Spaceship requests require https")
        if parsed.hostname != "spaceship.dev":
            raise RuntimeError("Refused: unsafe API host. Spaceship requests must target spaceship.dev")
        if not re.match(r"^/api(/|$)", parsed.path or ""):
            raise RuntimeError("Refused: unsafe path base. API path must start with /api")

    def _retry_delay(self, retry_after: str | None, attempt: int) -> float:
        if retry_after:
            try:
                return min(float(retry_after), 10.0)
            except Exception:
                pass
        return min((2**attempt), 2.0)

    def request(
        self,
        method: str,
        url: str,
        *,
        headers: dict[str, str] | None = None,
        params: dict[str, Any] | None = None,
        json_body: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
    ) -> HttpResponse:
        self._ensure_https_api_host(url)
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
                    data=data,
                    timeout=self._timeout_s,
                    allow_redirects=False,
                )
            except requests.RequestException as e:
                ms = int((time.time() - start) * 1000)
                if self._verbose:
                    print(
                        f"[http] {method} {display_url} -> EXCEPTION ({ms}ms): {type(e).__name__}: {e}",
                        file=sys.stderr,
                    )
                raise RuntimeError(
                    f"Request failed for {method} {display_url}: {type(e).__name__}: {e}"
                ) from e

            ms = int((time.time() - start) * 1000)
            if self._verbose:
                print(f"[http] {method} {resp.url} -> {resp.status_code} ({ms}ms)", file=sys.stderr)

            retry_after = resp.headers.get("Retry-After")
            if resp.status_code == 429 and attempt <= self._max_429_retries:
                delay = self._retry_delay(retry_after, attempt)
                if self._verbose:
                    print(f"[http] 429 received; retrying in {delay}s (attempt {attempt})", file=sys.stderr)
                time.sleep(delay)
                continue

            return HttpResponse(
                status=resp.status_code,
                headers={k.lower(): v for k, v in resp.headers.items()},
                body=resp.content,
                url=resp.url,
                attempts=attempt,
                retry_after=int(float(retry_after)) if retry_after else None,
                throttled=attempt > 1,
            )
