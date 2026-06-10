from __future__ import annotations

import dataclasses
import json
import sys
import time
import threading
from typing import Any

import requests

from .errors import ToolError


@dataclasses.dataclass(frozen=True)
class HttpResponse:
    status: int
    headers: dict[str, str]
    body: bytes
    url: str
    duration_ms: int
    attempts: int
    from_cache: bool = False

    def json(self) -> Any:
        return json.loads(self.body.decode("utf-8"))

    def text(self) -> str:
        return self.body.decode("utf-8", errors="replace")


class HttpClient:
    def __init__(
        self,
        *,
        connect_timeout_s: float,
        read_timeout_s: float,
        verbose: bool,
        progress: bool,
        user_agent: str,
    ):
        self._connect_timeout_s = float(connect_timeout_s)
        self._read_timeout_s = float(read_timeout_s)
        self._verbose = verbose
        self._progress = progress
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
        data: Any | None = None,
        files: Any | None = None,
        retries: int = 0,
        retry_on: tuple[int, ...] = (429, 500, 502, 503, 504),
    ) -> HttpResponse:
        attempt = 0
        display_url = self._format_url(url, params)

        def _should_retry_exception(e: requests.RequestException) -> bool:
            if method.upper() != "GET":
                return False
            return isinstance(
                e,
                (
                    requests.Timeout,
                    requests.ConnectionError,
                ),
            )

        def _heartbeat(done: threading.Event) -> None:
            start_beat = time.time()
            interval_s = 15.0
            threshold_s = 10.0
            while True:
                if done.wait(interval_s):
                    return
                elapsed = time.time() - start_beat
                if elapsed < threshold_s:
                    continue
                print(
                    f"[http] {method} {display_url} (elapsed {int(elapsed)}s; waiting for Cloudflare...)",
                    file=sys.stderr,
                )

        while True:
            attempt += 1
            start = time.time()
            if self._verbose:
                print(f"[http] {method} {display_url} (start)", file=sys.stderr)
            done = threading.Event()
            hb: threading.Thread | None = None
            if self._progress or self._verbose:
                # Verbose already implies the user is troubleshooting; progress heartbeats help avoid "hung" confusion
                # on slow Cloudflare endpoints.
                hb = threading.Thread(target=_heartbeat, args=(done,), daemon=True)
                hb.start()
            try:
                resp = self._session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    params=params,
                    json=json_body,
                    data=data,
                    files=files,
                    timeout=(self._connect_timeout_s, self._read_timeout_s),
                )
            except requests.RequestException as e:
                ms = int((time.time() - start) * 1000)
                done.set()
                if self._verbose:
                    print(
                        f"[http] {method} {display_url} -> EXCEPTION ({ms}ms): {type(e).__name__}: {e}",
                        file=sys.stderr,
                    )
                if attempt <= retries and _should_retry_exception(e):
                    sleep_s = min(2**attempt, 10)
                    time.sleep(max(0.0, min(float(sleep_s), 60.0)))
                    continue
                raise ToolError(f"Request failed for {method} {display_url}: {type(e).__name__}: {e}") from None
            ms = int((time.time() - start) * 1000)
            done.set()
            if self._verbose:
                print(f"[http] {method} {resp.url} -> {resp.status_code} ({ms}ms)", file=sys.stderr)

            if resp.status_code >= 400 and attempt <= retries and resp.status_code in retry_on:
                retry_after = str(resp.headers.get("Retry-After") or resp.headers.get("retry-after") or "").strip()
                sleep_s: float | None = None
                if retry_after:
                    try:
                        sleep_s = float(retry_after)
                    except Exception:
                        sleep_s = None
                if sleep_s is None:
                    sleep_s = min(2**attempt, 10)
                time.sleep(max(0.0, min(float(sleep_s), 60.0)))
                continue

            return HttpResponse(
                status=int(resp.status_code),
                headers={k.lower(): v for k, v in resp.headers.items()},
                body=resp.content,
                url=str(resp.url),
                duration_ms=ms,
                attempts=attempt,
            )
