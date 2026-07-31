from __future__ import annotations

import dataclasses
import json
import sys
import time
from typing import Any
from urllib.parse import urlsplit, urlunsplit

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
        transport: requests.Session | None = None,
    ):
        self._timeout_s = timeout_s
        self._verbose = verbose
        self._session = requests.Session() if transport is None else transport
        if hasattr(self._session, "headers"):
            self._session.headers["User-Agent"] = user_agent

    @staticmethod
    def _strip_query(url: str) -> str:
        parts = urlsplit(url)
        return urlunsplit((parts.scheme, parts.netloc, parts.path, "", ""))

    def request(
        self,
        method: str,
        url: str,
        headers: dict[str, str] | None = None,
        params: dict[str, Any] | None = None,
        json_body: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
        retries: int = 0,
        retry_on: tuple[int, ...] = (),
        raise_on_error: bool = True,
    ) -> HttpResponse:
        safe_url = self._strip_query(url)
        _ = retries
        _ = retry_on
        start = time.time()
        if self._verbose:
            print(f"[http] {method} {safe_url} (start)", file=sys.stderr)
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
                    f"[http] {method} {safe_url} -> EXCEPTION ({ms}ms): {type(e).__name__}",
                    file=sys.stderr,
                )
            raise RuntimeError(
                f"Request failed for {method} {safe_url}: {type(e).__name__}"
            ) from None
        ms = int((time.time() - start) * 1000)
        if self._verbose:
            print(f"[http] {method} {self._strip_query(resp.url)} -> {resp.status_code} ({ms}ms)", file=sys.stderr)

        if not raise_on_error or resp.status_code < 400:
            return HttpResponse(
                status=resp.status_code,
                headers={k.lower(): v for k, v in resp.headers.items()},
                body=resp.content,
                url=resp.url,
            )

        if self._verbose:
            print(
                f"[http] {method} {self._strip_query(resp.url)} -> ERROR {resp.status_code}",
                file=sys.stderr,
            )
        raise RuntimeError(f"HTTP {resp.status_code} for {method} {safe_url}")
