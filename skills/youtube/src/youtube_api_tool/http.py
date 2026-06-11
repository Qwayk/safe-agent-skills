from __future__ import annotations

import dataclasses
import json
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

    _SENSITIVE_QUERY_KEYS = {
        "key",
        "access_token",
        "oauth_token",
        "token",
        "authorization",
        "refresh_token",
        "id_token",
        # Resumable upload session identifiers can be used to continue an upload.
        "upload_id",
        "uploadid",
    }

    _SENSITIVE_HEADER_KEYS = {
        "authorization",
        "proxy-authorization",
        "x-api-key",
    }

    @classmethod
    def redact_url(cls, url: str) -> str:
        """
        Redact secret-bearing query params from URLs so they can be logged safely.
        """
        try:
            parts = urlsplit(url)
            if not parts.query:
                return url
            q = []
            for k, v in parse_qsl(parts.query, keep_blank_values=True):
                if str(k).lower() in cls._SENSITIVE_QUERY_KEYS:
                    q.append((k, "***REDACTED***"))
                else:
                    q.append((k, v))
            new_query = urlencode(q, doseq=True)
            return urlunsplit((parts.scheme, parts.netloc, parts.path, new_query, parts.fragment))
        except Exception:
            return url

    @classmethod
    def redact_headers(cls, headers: dict[str, str] | None) -> dict[str, str] | None:
        if headers is None:
            return None
        out: dict[str, str] = {}
        for k, v in headers.items():
            lk = str(k).lower()
            if lk in cls._SENSITIVE_HEADER_KEYS or lk.endswith("-token") or lk.endswith("_token"):
                out[k] = "***REDACTED***"
            else:
                out[k] = v
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
        json_body: Any | None = None,
        data: Any | None = None,
        files: Any | None = None,
        retries: int = 0,
        retry_on: tuple[int, ...] = (429, 500, 502, 503, 504),
    ) -> HttpResponse:
        attempt = 0
        display_url = self.redact_url(self._format_url(url, params))
        display_headers = self.redact_headers(headers)
        while True:
            attempt += 1
            start = time.time()
            if self._verbose:
                print(f"[http] {method} {display_url} (start)", file=sys.stderr)
                if display_headers:
                    print(f"[http] headers={json.dumps(display_headers, sort_keys=True)}", file=sys.stderr)
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
                    f"Request failed for {method} {display_url}: {type(e).__name__}"
                ) from e
            ms = int((time.time() - start) * 1000)
            if self._verbose:
                print(
                    f"[http] {method} {self.redact_url(str(resp.url))} -> {resp.status_code} ({ms}ms)",
                    file=sys.stderr,
                )

            if resp.status_code < 400:
                safe_url = self.redact_url(str(resp.url))
                return HttpResponse(
                    status=resp.status_code,
                    headers={k.lower(): v for k, v in resp.headers.items()},
                    body=resp.content,
                    url=safe_url,
                )

            if attempt <= retries and resp.status_code in retry_on:
                time.sleep(min(2**attempt, 10))
                continue

            safe_url = self.redact_url(str(resp.url))
            raise RuntimeError(f"HTTP {resp.status_code} for {method} {safe_url}")
