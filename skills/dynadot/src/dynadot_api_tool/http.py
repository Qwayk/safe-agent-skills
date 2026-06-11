from __future__ import annotations

import dataclasses
import json
import re
import sys
import time
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

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
    def _redact_text(text: str) -> str:
        # Ensure we never leak Dynadot's API key in exception strings.
        # Some requests exceptions include the full request URL, which contains `key=...`.
        if not text:
            return text
        out = text
        out = re.sub(r"(?i)(\bkey=)([^&\s]+)", r"\1***REDACTED***", out)
        out = re.sub(r"(?i)(\bkey%3d)([^&\s]+)", r"\1***REDACTED***", out)
        return out

    @staticmethod
    def _redact_url(url: str) -> str:
        # Dynadot's API key is passed as a URL query parameter (key=...).
        # Never print or store full URLs containing the raw key value.
        try:
            parts = urlsplit(url)
            q = []
            changed = False
            for k, v in parse_qsl(parts.query, keep_blank_values=True):
                if k.lower() == "key":
                    q.append((k, "***REDACTED***"))
                    changed = True
                else:
                    q.append((k, v))
            if not changed:
                return url
            return urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(q, doseq=True), parts.fragment))
        except Exception:
            return url

    @staticmethod
    def _redact_params(params: dict[str, Any] | None) -> dict[str, Any] | None:
        if not params:
            return params
        out = dict(params)
        for k in list(out.keys()):
            if str(k).lower() == "key":
                out[k] = "***REDACTED***"
        return out

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
        retries: int = 0,
        retry_on: tuple[int, ...] = (429, 500, 502, 503, 504),
    ) -> HttpResponse:
        attempt = 0
        display_url = self._redact_url(self._format_url(url, self._redact_params(params)))
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
                )
            except requests.RequestException as e:
                ms = int((time.time() - start) * 1000)
                safe_e = self._redact_text(str(e))
                if self._verbose:
                    print(
                        f"[http] {method} {display_url} -> EXCEPTION ({ms}ms): {type(e).__name__}: {safe_e}",
                        file=sys.stderr,
                    )
                raise RuntimeError(
                    f"Request failed for {method} {display_url}: {type(e).__name__}: {safe_e}"
                ) from e
            ms = int((time.time() - start) * 1000)
            if self._verbose:
                print(f"[http] {method} {self._redact_url(resp.url)} -> {resp.status_code} ({ms}ms)", file=sys.stderr)

            if resp.status_code < 400:
                return HttpResponse(
                    status=resp.status_code,
                    headers={k.lower(): v for k, v in resp.headers.items()},
                    body=resp.content,
                    url=self._redact_url(resp.url),
                )

            if attempt <= retries and resp.status_code in retry_on:
                time.sleep(min(2**attempt, 10))
                continue

            safe_url = self._redact_url(resp.url)
            safe_text = self._redact_text(resp.text)
            raise RuntimeError(f"HTTP {resp.status_code} for {method} {safe_url}\n{safe_text}")
