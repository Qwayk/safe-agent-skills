from __future__ import annotations

import dataclasses
import json
import sys
import time
from typing import Any
from urllib.parse import parse_qsl, quote, quote_plus, urlencode, urlsplit, urlunsplit

import requests

SECRET_KEYS = {
    "access_token",
    "authorization",
    "client_secret",
    "client_id",
    "apikey",
    "api_key",
    "token",
}


def redact_url(url: str) -> str:
    try:
        parts = urlsplit(url)
        query = []
        for key, value in parse_qsl(parts.query, keep_blank_values=True):
            if key.lower() in SECRET_KEYS:
                query.append((key, "<redacted>"))
            else:
                query.append((key, value))
        return urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(query), parts.fragment))
    except Exception:
        return "<redacted-url>"


def redact_headers(headers: dict[str, str] | None) -> dict[str, str]:
    if not headers:
        return {}
    out: dict[str, str] = {}
    for key, value in headers.items():
        out[key] = "<redacted>" if key.lower() in SECRET_KEYS else value
    return out


def redact_secrets(text: str, secrets: tuple[str, ...]) -> str:
    forms = {
        form for secret in secrets if secret for form in (secret, quote(secret, safe=""), quote_plus(secret))
    }
    for value in sorted(forms, key=len, reverse=True):
        text = text.replace(value, "<redacted>")
    return text


def redact_response(value: Any, secrets: tuple[str, ...]) -> Any:
    if isinstance(value, dict):
        return {
            redact_secrets(key, secrets): (
                "<redacted>" if key.lower() in SECRET_KEYS else redact_response(item, secrets)
            )
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [redact_response(item, secrets) for item in value]
    if isinstance(value, str):
        return redact_secrets(value, secrets)
    return value


@dataclasses.dataclass(frozen=True)
class HttpResponse:
    status: int
    headers: dict[str, str]
    body: bytes
    url: str

    def json(self) -> Any:
        try:
            return json.loads(self.body.decode("utf-8"))
        except ValueError:
            raise RuntimeError("Skimlinks returned invalid JSON.") from None

    def text(self) -> str:
        return self.body.decode("utf-8", errors="replace")


class HttpClient:
    def __init__(self, *, timeout_s: float, verbose: bool, user_agent: str, credentials: tuple[str, ...] = ()):
        self._timeout_s = timeout_s
        self._verbose = verbose
        self._session = requests.Session()
        self._session.headers["User-Agent"] = user_agent
        self._credentials = credentials

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
        display_url = redact_secrets(self._format_url(url, params), self._credentials)
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
                if self._verbose:
                    print(
                        f"[http] {method} {display_url} -> EXCEPTION ({ms}ms): {type(e).__name__}",
                        file=sys.stderr,
                    )
                raise RuntimeError(
                    f"Request failed for {method} {display_url}: {type(e).__name__}"
                ) from None
            ms = int((time.time() - start) * 1000)
            if self._verbose:
                print(f"[http] {method} {display_url} -> {resp.status_code} ({ms}ms)", file=sys.stderr)

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

            raise RuntimeError(f"Skimlinks returned HTTP {resp.status_code} for {method} {display_url}.")
