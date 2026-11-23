from __future__ import annotations

import dataclasses
import json
import sys
import time
from typing import Any
from urllib.parse import parse_qsl, quote, unquote, urlencode, urlsplit, urlunsplit

import requests

from .errors import HttpError

SENSITIVE_QUERY_KEYS = {"key", "apikey", "api_key", "site-api-key"}
SENSITIVE_BID_QUERY_KEYS = {"ip", "useragent", "referrerurl", "subid", "gdprconsent", "ccpaconsent", "gppconsent", "cuid"}


def redact_url(url: str) -> str:
    if not url:
        return url
    try:
        parts = urlsplit(url)
    except ValueError:
        return "***REDACTED***"
    path_parts = parts.path.split("/")
    for idx, part in enumerate(path_parts):
        if part == "sites" and idx + 1 < len(path_parts) and path_parts[idx + 1]:
            path_parts[idx + 1] = "***REDACTED***"
    safe_path = "/".join(path_parts)
    if not parts.query:
        return urlunsplit((parts.scheme, parts.netloc, safe_path, parts.query, parts.fragment))
    query_pairs = parse_qsl(parts.query, keep_blank_values=True)
    safe_pairs: list[tuple[str, str]] = []
    for key, value in query_pairs:
        if key.lower() in SENSITIVE_QUERY_KEYS | SENSITIVE_BID_QUERY_KEYS:
            safe_pairs.append((key, "***REDACTED***"))
        else:
            safe_pairs.append((key, value))
    return urlunsplit((parts.scheme, parts.netloc, safe_path, urlencode(safe_pairs), parts.fragment))


def redact_secrets(text: str, secrets: tuple[str, ...]) -> str:
    values = {form for secret in secrets if secret for form in (secret, quote(secret, safe=""))}
    for value in sorted(values, key=len, reverse=True):
        text = text.replace(value, "***REDACTED***")
    return text


def request_secrets(url: str, headers: dict | None, params: dict | None) -> tuple[str, ...]:
    parts = urlsplit(url).path.split("/")
    site_key = next((unquote(parts[index + 1]) for index, name in enumerate(parts[:-1]) if name == "sites"), "")
    keys = [str(value) for name, value in (params or {}).items() if name.lower() in SENSITIVE_QUERY_KEYS | SENSITIVE_BID_QUERY_KEYS and value]
    for name, value in (headers or {}).items():
        if name.lower() == "authorization":
            keys.append(str(value).removeprefix("secret "))
        elif name.lower() == "x-api-key":
            keys.append(str(value))
    return (*keys, site_key)


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
            prepared = requests.Request("GET", url, params=params).prepare().url or url
            return redact_url(prepared)
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
        secrets = request_secrets(url, headers, params)
        display_url = redact_secrets(self._format_url(url, params), secrets)
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
                message = redact_secrets(str(e), secrets)
                if self._verbose:
                    print(
                        f"[http] {method} {display_url} -> EXCEPTION ({ms}ms): {type(e).__name__}: {message}",
                        file=sys.stderr,
                    )
                raise HttpError(
                    f"Request failed for {method} {display_url}: {type(e).__name__}: {message}"
                ) from e
            ms = int((time.time() - start) * 1000)
            safe_url = redact_secrets(redact_url(resp.url), secrets)
            if self._verbose:
                print(
                    f"[http] {method} {safe_url} -> {resp.status_code} ({ms}ms)",
                    file=sys.stderr,
                )

            if resp.status_code < 400:
                return HttpResponse(
                    status=resp.status_code,
                    headers={k.lower(): v for k, v in resp.headers.items()},
                    body=resp.content,
                    url=safe_url,
                )

            if attempt <= retries and resp.status_code in retry_on:
                time.sleep(min(2**attempt, 10))
                continue

            retry_hint = ""
            if resp.status_code == 429:
                retry_after = redact_secrets(str(resp.headers.get("Retry-After") or "").strip(), secrets)
                if retry_after:
                    retry_hint = f"\nRetry hint: wait {retry_after} second(s) before retrying."
                else:
                    retry_hint = "\nRetry hint: the vendor rate-limited this request. Wait and retry later."
            raise HttpError(
                f"HTTP {resp.status_code} for {method} {safe_url}\n{redact_secrets(resp.text, secrets)}{retry_hint}"
            )
