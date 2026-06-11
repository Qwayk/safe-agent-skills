from __future__ import annotations

import json
import time
import sys
from dataclasses import dataclass
from typing import Any

import requests


@dataclass(frozen=True)
class HttpResponse:
    status: int
    headers: dict[str, str]
    body: bytes
    url: str

    def json(self) -> Any:
        return json.loads(self.body.decode("utf-8"))


class HttpClient:
    def __init__(self, *, timeout_s: float, verbose: bool, user_agent: str):
        self._timeout_s = timeout_s
        self._verbose = verbose
        self._session = requests.Session()
        self._session.headers["User-Agent"] = user_agent

    def request(
        self,
        method: str,
        url: str,
        *,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> HttpResponse:
        method = method.upper()
        start = time.time()
        if self._verbose:
            print(f"[http] {method} {url} (start)", file=sys.stderr)
        try:
            resp = self._session.request(
                method=method,
                url=url,
                params=params,
                headers=headers,
                timeout=self._timeout_s,
            )
        except requests.RequestException as e:
            raise RuntimeError(f"Request failed for {method} {url}: {type(e).__name__}: {e}") from e

        ms = int((time.time() - start) * 1000)
        if self._verbose:
            print(f"[http] {method} {resp.url} -> {resp.status_code} ({ms}ms)", file=sys.stderr)

        if resp.status_code >= 400:
            raise RuntimeError(f"HTTP {resp.status_code} for {resp.url}: {resp.text}")

        return HttpResponse(
            status=resp.status_code,
            headers={k.lower(): v for k, v in resp.headers.items()},
            body=resp.content,
            url=resp.url,
        )
