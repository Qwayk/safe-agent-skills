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
    def __init__(self, *, timeout_s: float, verbose: bool, user_agent: str, min_delay_s: float):
        self._timeout_s = timeout_s
        self._verbose = verbose
        self._min_delay_s = max(0.0, float(min_delay_s))
        self._next_request_at = 0.0
        self._session = requests.Session()
        self._session.headers["User-Agent"] = user_agent

    def _throttle(self) -> None:
        if self._min_delay_s <= 0:
            return
        now = time.monotonic()
        if now < self._next_request_at:
            time.sleep(self._next_request_at - now)
        self._next_request_at = time.monotonic() + self._min_delay_s

    @staticmethod
    def _format_url(url: str, params: dict[str, Any] | None) -> str:
        if not params:
            return url
        try:
            return requests.Request("GET", url, params=params).prepare().url or url
        except Exception:
            return url

    @staticmethod
    def _parse_retry_after_s(headers: dict[str, str]) -> float | None:
        # Best-effort; only handle numeric seconds.
        ra = (headers.get("retry-after") or "").strip()
        if not ra:
            return None
        try:
            return float(ra)
        except Exception:
            return None

    @staticmethod
    def _is_retryable_403(body: bytes) -> bool:
        # Google APIs sometimes use 403 for quota/rate-limit errors.
        try:
            obj = json.loads(body.decode("utf-8"))
        except Exception:
            return False
        if not isinstance(obj, dict):
            return False
        err = obj.get("error")
        if not isinstance(err, dict):
            return False
        errs = err.get("errors")
        if not isinstance(errs, list):
            return False
        reasons: set[str] = set()
        for item in errs:
            if isinstance(item, dict):
                r = item.get("reason")
                if isinstance(r, str) and r.strip():
                    reasons.add(r.strip())
        return bool(reasons & {"quotaExceeded", "rateLimitExceeded", "userRateLimitExceeded", "dailyLimitExceeded"})

    @staticmethod
    def _backoff_s(attempt: int) -> float:
        # Deterministic exponential backoff (no jitter).
        return float(min(2**attempt, 30))

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
        retry_on: tuple[int, ...] = (403, 429, 500, 502, 503, 504),
    ) -> HttpResponse:
        attempt = 0
        display_url = self._format_url(url, params)
        while True:
            attempt += 1
            self._throttle()
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
                )
            except requests.RequestException as e:
                ms = int((time.time() - start) * 1000)
                if self._verbose:
                    print(
                        f"[http] {method} {display_url} -> EXCEPTION ({ms}ms): {type(e).__name__}: {e}",
                        file=sys.stderr,
                    )
                if attempt <= retries:
                    time.sleep(self._backoff_s(attempt))
                    continue
                raise RuntimeError(f"Request failed for {method} {display_url}: {type(e).__name__}: {e}") from e
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

            should_retry = False
            if resp.status_code in retry_on:
                if resp.status_code != 403:
                    should_retry = True
                else:
                    should_retry = self._is_retryable_403(resp.content)

            if attempt <= retries and should_retry:
                headers_lc = {k.lower(): v for k, v in resp.headers.items()}
                retry_after_s = self._parse_retry_after_s(headers_lc) or 0.0
                time.sleep(max(self._backoff_s(attempt), retry_after_s))
                continue

            raise RuntimeError(f"HTTP {resp.status_code} for {method} {resp.url}\n{resp.text}")
