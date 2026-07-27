from __future__ import annotations

import dataclasses
import json
import sys
import time
from typing import Any, BinaryIO
from urllib.parse import urlsplit

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
        session: requests.Session | None = None,
    ):
        self._timeout_s = timeout_s
        self._verbose = verbose
        self._session = session or requests.Session()
        self._session.headers["User-Agent"] = user_agent

    @staticmethod
    def _display_url(url: str) -> str:
        parts = urlsplit(url)
        return f"{parts.scheme}://{parts.netloc}{parts.path}"

    def request(
        self,
        method: str,
        url: str,
        *,
        headers: dict[str, str] | None = None,
        params: dict[str, Any] | None = None,
        json_body: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
        files: dict[str, tuple[str, BinaryIO]] | None = None,
        retries: int = 2,
        retry_on: tuple[int, ...] = (429, 500, 502, 503, 504),
    ) -> HttpResponse:
        display_url = self._display_url(url)
        for attempt in range(retries + 1):
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
                    allow_redirects=False,
                )
            except requests.RequestException as exc:
                if attempt < retries:
                    time.sleep(min(2 ** (attempt + 1), 10))
                    continue
                raise RuntimeError(
                    f"Asana request failed before a response: {type(exc).__name__}"
                ) from None
            elapsed_ms = int((time.time() - start) * 1000)
            if self._verbose:
                print(
                    f"[http] {method} {display_url} -> {response.status_code} ({elapsed_ms}ms)",
                    file=sys.stderr,
                )
            if response.status_code not in retry_on or attempt >= retries:
                return HttpResponse(
                    status=response.status_code,
                    headers={key.lower(): value for key, value in response.headers.items()},
                    body=response.content,
                    url=response.url,
                )
            retry_after = response.headers.get("Retry-After", "")
            try:
                delay = min(max(float(retry_after), 0.0), 30.0)
            except ValueError:
                delay = min(2 ** (attempt + 1), 10)
            time.sleep(delay)
        raise RuntimeError("Asana request retry loop ended unexpectedly")
