from __future__ import annotations

import dataclasses
import json
import sys
import time
from typing import Any
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


class _PipedriveSession(requests.Session):
    def rebuild_auth(self, prepared_request: requests.PreparedRequest, response: requests.Response) -> None:
        super().rebuild_auth(prepared_request, response)
        if urlsplit(prepared_request.url).netloc != urlsplit(response.request.url).netloc or self.should_strip_auth(
            response.request.url, prepared_request.url
        ):
            prepared_request.headers.pop("x-api-token", None)


class HttpClient:
    def __init__(self, *, timeout_s: float, verbose: bool, user_agent: str):
        self._timeout_s = timeout_s
        self._verbose = verbose
        self._session = _PipedriveSession()
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
        allow_redirects: bool = True,
        stream: bool = False,
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
                    allow_redirects=allow_redirects,
                    stream=stream,
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

            with resp:
                if resp.status_code < 400:
                    return HttpResponse(
                        status=resp.status_code,
                        headers={k.lower(): v for k, v in resp.headers.items()},
                        body=resp.content if not stream else b"",
                        url=resp.url,
                    )

                if attempt > retries or resp.status_code not in retry_on:
                    detail = "" if stream else f"\n{resp.text}"
                    raise RuntimeError(f"HTTP {resp.status_code} for {method} {resp.url}{detail}")

            time.sleep(min(2**attempt, 10))
