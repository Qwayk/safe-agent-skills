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
                response = self._session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    params=params,
                    json=json_body,
                    data=data,
                    files=files,
                    timeout=self._timeout_s,
                )
            except requests.RequestException as exc:
                ms = int((time.time() - start) * 1000)
                if self._verbose:
                    print(
                        f"[http] {method} {display_url} -> EXCEPTION ({ms}ms): {type(exc).__name__}: {exc}",
                        file=sys.stderr,
                    )
                raise RuntimeError(
                    f"Request failed for {method} {display_url}: {type(exc).__name__}: {exc}"
                ) from exc

            ms = int((time.time() - start) * 1000)
            if self._verbose:
                print(f"[http] {method} {response.url} -> {response.status_code} ({ms}ms)", file=sys.stderr)

            if response.status_code < 400:
                return HttpResponse(
                    status=response.status_code,
                    headers={key.lower(): value for key, value in response.headers.items()},
                    body=response.content,
                    url=response.url,
                )

            if attempt <= retries and response.status_code in retry_on:
                time.sleep(min(2**attempt, 10))
                continue

            raise RuntimeError(f"HTTP {response.status_code} for {method} {response.url}\n{response.text}")
