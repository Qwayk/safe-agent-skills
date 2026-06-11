from __future__ import annotations

import dataclasses
import json
import re
import sys
import time
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

import requests


SECRET_KEYS = {
    "access_token",
    "accessToken",
    "authorization",
    "api_key",
    "apikey",
    "client_id",
    "client_secret",
    "token",
    "x_api_key",
    "x-api-key",
}
_SECRET_KEYS_LOWER = {key.lower() for key in SECRET_KEYS}
_SECRET_PATH_SEGMENTS_LOWER = _SECRET_KEYS_LOWER | {"apikey"}


def _redact_path(path: str) -> str:
    if not path:
        return path
    parts = path.split("/")
    for idx, part in enumerate(parts[:-1]):
        if part.lower() in _SECRET_PATH_SEGMENTS_LOWER and parts[idx + 1]:
            parts[idx + 1] = "<redacted>"
    return "/".join(parts)


def _collect_secret_values(
    *, url: str, headers: dict[str, str] | None, params: dict[str, Any] | None
) -> set[str]:
    values: set[str] = set()
    for items in (headers or {}, params or {}):
        for key, value in items.items():
            if str(key).lower() not in _SECRET_KEYS_LOWER:
                continue
            raw = str(value or "").strip()
            if not raw:
                continue
            values.add(raw)
            if raw.lower().startswith("bearer "):
                bearer_value = raw[7:].strip()
                if bearer_value:
                    values.add(bearer_value)

    try:
        path_parts = urlsplit(url).path.split("/")
        for idx, part in enumerate(path_parts[:-1]):
            if part.lower() in _SECRET_PATH_SEGMENTS_LOWER and path_parts[idx + 1]:
                values.add(path_parts[idx + 1])
    except Exception:
        return values
    return values


def redact_text(text: str, *, secret_values: set[str] | None = None) -> str:
    out = str(text or "")
    for secret in sorted(secret_values or set(), key=len, reverse=True):
        if secret:
            out = out.replace(secret, "<redacted>")
    out = re.sub(
        r"([?&](?:access_token|accessToken|authorization|api_key|apikey|token|x_api_key|x-api-key)=)[^&#\s]+",
        r"\1<redacted>",
        out,
        flags=re.IGNORECASE,
    )
    out = re.sub(
        r"(/(?:access_token|accessToken|authorization|api_key|apikey|token|x_api_key|x-api-key)/)[^/?#\s]+",
        r"\1<redacted>",
        out,
        flags=re.IGNORECASE,
    )
    return out


def redact_url(url: str) -> str:
    try:
        parts = urlsplit(url)
        query = []
        for key, value in parse_qsl(parts.query, keep_blank_values=True):
            if key.lower() in _SECRET_KEYS_LOWER:
                query.append((key, "<redacted>"))
            else:
                query.append((key, value))
        return urlunsplit((parts.scheme, parts.netloc, _redact_path(parts.path), urlencode(query), parts.fragment))
    except Exception:
        return "<redacted-url>"


def redact_headers(headers: dict[str, str] | None) -> dict[str, str]:
    if not headers:
        return {}
    out: dict[str, str] = {}
    for key, value in headers.items():
        out[key] = "<redacted>" if key.lower() in _SECRET_KEYS_LOWER else value
    return out


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
            return redact_url(url)
        try:
            return redact_url(requests.Request("GET", url, params=params).prepare().url or url)
        except Exception:
            return redact_url(url)

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
        display_url = self._format_url(url, params)
        secret_values = _collect_secret_values(url=url, headers=headers, params=params)
        while True:
            attempt += 1
            start = time.time()
            if self._verbose:
                print(
                    f"[http] {method} {display_url} headers={redact_headers(headers)} (start)",
                    file=sys.stderr,
                )
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
                safe_error = redact_text(str(e), secret_values=secret_values)
                if self._verbose:
                    print(
                        f"[http] {method} {display_url} headers={redact_headers(headers)} -> EXCEPTION ({ms}ms): {type(e).__name__}: {safe_error}",
                        file=sys.stderr,
                    )
                raise RuntimeError(
                    f"Request failed for {method} {display_url} headers={redact_headers(headers)}: {type(e).__name__}: {safe_error}"
                ) from e
            ms = int((time.time() - start) * 1000)
            if self._verbose:
                print(
                    f"[http] {method} {redact_url(resp.url)} -> {resp.status_code} ({ms}ms)",
                    file=sys.stderr,
                )

            if resp.status_code < 400:
                return HttpResponse(
                    status=resp.status_code,
                    headers={k.lower(): v for k, v in resp.headers.items()},
                    body=resp.content,
                    url=resp.url,
                )

            if attempt <= retries and resp.status_code in retry_on:
                time.sleep(min(2**attempt, 10))
                continue

            raise RuntimeError(
                f"HTTP {resp.status_code} for {method} {redact_url(resp.url)} "
                f"headers={redact_headers(headers)} "
                f"response_body=<suppressed {len(resp.content)} bytes>"
            )
