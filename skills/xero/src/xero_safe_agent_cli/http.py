from __future__ import annotations

import dataclasses
import json
import sys
import time
from typing import Any
from urllib.parse import urlsplit, urlunsplit

import requests

MAX_AUTOMATIC_RETRY_DELAY_S = 30.0


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
        try:
            parsed = urlsplit(url)
            return urlunsplit((parsed.scheme, parsed.netloc, parsed.path, "", ""))
        except ValueError:
            return "<fixed-xero-url>"

    def request(
        self,
        method: str,
        url: str,
        *,
        headers: dict[str, str] | None = None,
        params: dict[str, Any] | None = None,
        json_body: Any | None = None,
        data: Any | None = None,
        files: dict[str, Any] | None = None,
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
                        f"[http] {method} {display_url} -> EXCEPTION ({ms}ms): {type(e).__name__}",
                        file=sys.stderr,
                    )
                raise RuntimeError(
                    f"Xero request failed before a response: {type(e).__name__}"
                ) from None
            ms = int((time.time() - start) * 1000)
            if self._verbose:
                response_url = self._format_url(resp.url, None)
                print(
                    f"[http] {method} {response_url} -> {resp.status_code} ({ms}ms)",
                    file=sys.stderr,
                )

            if attempt <= retries and resp.status_code in retry_on:
                retry_after = resp.headers.get("Retry-After")
                try:
                    delay = float(retry_after) if retry_after is not None else min(2**attempt, 10)
                except ValueError:
                    delay = min(2**attempt, 10)
                if delay <= MAX_AUTOMATIC_RETRY_DELAY_S:
                    time.sleep(max(0.0, delay))
                    continue
            return HttpResponse(
                status=resp.status_code,
                headers={k.lower(): v for k, v in resp.headers.items()},
                body=resp.content,
                url=resp.url,
            )
