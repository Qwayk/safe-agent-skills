from __future__ import annotations

import dataclasses
import json
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
import sys
import time
from typing import Any

import requests


def _redact_text(text: str, secrets: tuple[str | None, ...]) -> str:
    out = text
    for secret in secrets:
        if secret:
            out = out.replace(secret, "***REDACTED***")
    return out


def _redact_url(url: str, secrets: tuple[str | None, ...]) -> str:
    try:
        parts = urlsplit(url)
        query_items = []
        for key, value in parse_qsl(parts.query, keep_blank_values=True):
            if key in {"consumer_key", "consumer_secret"}:
                query_items.append((key, "***REDACTED***"))
            else:
                query_items.append((key, value))
        sanitized = urlunsplit(
            (
                parts.scheme,
                parts.netloc,
                parts.path,
                urlencode(query_items, doseq=True),
                parts.fragment,
            )
        )
    except Exception:
        sanitized = url
    return _redact_text(sanitized, secrets)


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
        verify_ssl: bool,
        secrets: tuple[str | None, ...] = (),
    ):
        self._timeout_s = timeout_s
        self._verbose = verbose
        self._verify_ssl = verify_ssl
        self._secrets = secrets
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
        json_body: dict[str, Any] | list[Any] | None = None,
        auth: tuple[str, str] | None = None,
        retries: int = 0,
        retry_on: tuple[int, ...] = (429, 500, 502, 503, 504),
    ) -> HttpResponse:
        attempt = 0
        raw_display_url = self._format_url(url, params)
        display_url = _redact_url(raw_display_url, self._secrets)
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
                    timeout=self._timeout_s,
                    auth=auth,
                    verify=self._verify_ssl,
                )
            except requests.RequestException as exc:
                ms = int((time.time() - start) * 1000)
                if self._verbose:
                    print(
                        f"[http] {method} {display_url} -> EXCEPTION ({ms}ms): {type(exc).__name__}: {exc}",
                        file=sys.stderr,
                    )
                redacted_message = _redact_text(str(exc), self._secrets)
                raise RuntimeError(
                    f"Request failed for {method} {display_url}: {type(exc).__name__}: {redacted_message}"
                ) from exc
            ms = int((time.time() - start) * 1000)
            response_url = _redact_url(resp.url, self._secrets)
            if self._verbose:
                print(f"[http] {method} {response_url} -> {resp.status_code} ({ms}ms)", file=sys.stderr)

            if resp.status_code < 400:
                return HttpResponse(
                    status=resp.status_code,
                    headers={key.lower(): value for key, value in resp.headers.items()},
                    body=resp.content,
                    url=resp.url,
                )

            if attempt <= retries and resp.status_code in retry_on:
                time.sleep(min(2**attempt, 10))
                continue

            response_text = _redact_text(resp.text, self._secrets)
            raise RuntimeError(f"HTTP {resp.status_code} for {method} {response_url}\n{response_text}")
