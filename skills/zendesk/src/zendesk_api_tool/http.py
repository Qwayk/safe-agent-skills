from __future__ import annotations

import dataclasses
import json
import random
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
        files: dict[str, tuple[str, bytes]] | None = None,
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
                    data=data,
                    files=files,
                    timeout=self._timeout_s,
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

            if resp.status_code < 400:
                return HttpResponse(
                    status=resp.status_code,
                    headers={k.lower(): v for k, v in resp.headers.items()},
                    body=resp.content,
                    url=resp.url,
                )

            if attempt <= retries and resp.status_code in retry_on:
                delay_s = self._retry_delay_s(attempt=attempt, status=resp.status_code, headers=resp.headers)
                time.sleep(delay_s)
                continue

            raise RuntimeError(f"HTTP {resp.status_code} for {method} {resp.url}\n{resp.text}")

    @staticmethod
    def _retry_delay_s(*, attempt: int, status: int, headers: Any) -> float:
        """
        Return a capped exponential backoff delay with jitter.

        For 429, best-effort honor Retry-After (seconds) when present, bounded.
        """
        # Base exponential (seconds).
        base = min(0.5 * (2 ** max(0, attempt - 1)), 10.0)

        retry_after_s: float | None = None
        if int(status) == 429:
            try:
                ra = None
                if hasattr(headers, "get"):
                    ra = headers.get("Retry-After") or headers.get("retry-after")
                if ra is not None:
                    retry_after_s = float(str(ra).strip())
            except Exception:
                retry_after_s = None

        delay = base
        if retry_after_s is not None and retry_after_s >= 0:
            delay = min(max(retry_after_s, base), 30.0)

        # Jitter avoids retry storms.
        jitter = 0.75 + (random.random() * 0.5)  # [0.75, 1.25)
        return float(max(0.0, min(delay * jitter, 30.0)))
