from __future__ import annotations

import dataclasses
import json
import sys
import time
from typing import Any
from urllib.parse import quote, quote_plus

import requests


@dataclasses.dataclass(frozen=True)
class HttpResponse:
    status: int
    headers: dict[str, str]
    body: bytes
    url: str

    def json(self) -> Any:
        try:
            return json.loads(self.body.decode("utf-8"))
        except Exception as e:  # noqa: BLE001
            lower_url = (self.url or "").lower()
            body_text = ""
            try:
                body_text = self.text().lower()
            except Exception:
                body_text = ""

            looks_like_cloudflare_access = (
                "cloudflareaccess.com" in lower_url
                or "/cdn-cgi/access/login" in lower_url
                or "cloudflare access" in body_text
            )
            if looks_like_cloudflare_access:
                raise RuntimeError(
                    "Received a Cloudflare Access login page instead of JSON. "
                    "If your Plausible base URL is protected by Cloudflare Access, set "
                    "CF_ACCESS_CLIENT_ID and CF_ACCESS_CLIENT_SECRET in your env file."
                ) from e
            raise

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
        credentials: set[str] = set()
        for name, value in (headers or {}).items():
            if name.lower() == "authorization":
                credentials.add(value)
                if value.lower().startswith("bearer "):
                    credentials.add(value[7:])
            elif name.lower() in {"cf-access-client-id", "cf-access-client-secret"}:
                credentials.add(value)
        hidden = {
            variant
            for value in credentials
            if value
            for variant in (value, quote(value, safe=""), quote_plus(value), json.dumps(value)[1:-1])
        }
        hidden_values = sorted(hidden, key=len, reverse=True)

        def safe(text: str) -> str:
            for value in hidden_values:
                text = text.replace(value, "***REDACTED***")
            return text

        attempt = 0
        display_url = safe(self._format_url(url, params))
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
                        f"[http] {method} {display_url} -> EXCEPTION ({ms}ms): {type(e).__name__}: {safe(str(e))}",
                        file=sys.stderr,
                    )
                raise RuntimeError(
                    f"Request failed for {method} {display_url}: {type(e).__name__}: {safe(str(e))}"
                ) from None
            ms = int((time.time() - start) * 1000)
            if self._verbose:
                print(f"[http] {method} {safe(resp.url)} -> {resp.status_code} ({ms}ms)", file=sys.stderr)

            if resp.status_code < 400:
                return HttpResponse(
                    status=resp.status_code,
                    headers={k.lower(): v for k, v in resp.headers.items()},
                    body=resp.content,
                    url=safe(resp.url),
                )

            if attempt <= retries and resp.status_code in retry_on:
                time.sleep(min(2**attempt, 10))
                continue

            raise RuntimeError(f"HTTP {resp.status_code} for {method} {safe(resp.url)}\n{safe(resp.text)}")
