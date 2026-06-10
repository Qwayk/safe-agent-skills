from __future__ import annotations

import dataclasses
import json
import re
import sys
import time
from typing import Any

import requests


_REDACTED = "***REDACTED***"
_QUERY_SECRET_RE = re.compile(
    r"([?&](?:accessToken|token|api_key|apikey|x-api-key)=)([^&#\s]+)",
    flags=re.IGNORECASE,
)
_JSON_SECRET_RE = re.compile(
    r'((?:"|\')(?:accessToken|authorization|token|api_key|apikey|x-api-key)(?:"|\')\s*:\s*(?:"|\'))([^"\']*)((?:"|\'))',
    flags=re.IGNORECASE,
)
_AUTH_BEARER_RE = re.compile(
    r"((?:Authorization|authorization)\s*[:=]\s*Bearer\s+)([^\s,;]+)",
    flags=re.IGNORECASE,
)
_AUTH_VALUE_RE = re.compile(
    r"((?:x-api-key|X-API-Key|api-key|API-Key)\s*[:=]\s*)([^\s,;]+)",
    flags=re.IGNORECASE,
)


def _extract_secret_values(
    *,
    headers: dict[str, Any] | None,
    params: dict[str, Any] | None,
) -> set[str]:
    secrets: set[str] = set()

    if headers:
        for key, value in headers.items():
            raw = str(value or "").strip()
            if not raw:
                continue
            lower = str(key).lower()
            if lower == "authorization" and raw.lower().startswith("bearer "):
                secrets.add(raw[7:].strip())
            elif lower in {"authorization", "x-api-key", "api-key"}:
                secrets.add(raw)

    if params:
        for key, value in params.items():
            lower = str(key).lower()
            if lower in {"accesstoken", "token", "api_key", "apikey", "x-api-key"}:
                raw = str(value or "").strip()
                if raw:
                    secrets.add(raw)

    return {secret for secret in secrets if secret and secret != _REDACTED}


def redact_sensitive_text(value: Any, *, secrets: set[str] | None = None) -> str:
    text = str(value)

    text = _QUERY_SECRET_RE.sub(r"\1" + _REDACTED, text)
    text = _JSON_SECRET_RE.sub(r"\1" + _REDACTED + r"\3", text)
    text = _AUTH_BEARER_RE.sub(r"\1" + _REDACTED, text)
    text = _AUTH_VALUE_RE.sub(r"\1" + _REDACTED, text)

    for secret in sorted(secrets or set(), key=len, reverse=True):
        if secret:
            text = text.replace(secret, _REDACTED)

    return text


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
        retries: int = 0,
        retry_on: tuple[int, ...] = (429, 500, 502, 503, 504),
    ) -> HttpResponse:
        attempt = 0
        secrets = _extract_secret_values(headers=headers, params=params)
        display_url = redact_sensitive_text(self._format_url(url, params), secrets=secrets)
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
                safe_error = redact_sensitive_text(f"{type(e).__name__}: {e}", secrets=secrets)
                if self._verbose:
                    print(
                        f"[http] {method} {display_url} -> EXCEPTION ({ms}ms): {safe_error}",
                        file=sys.stderr,
                    )
                raise RuntimeError(
                    f"Request failed for {method} {display_url}: {safe_error}"
                ) from e
            ms = int((time.time() - start) * 1000)
            safe_response_url = redact_sensitive_text(resp.url, secrets=secrets)
            if self._verbose:
                print(f"[http] {method} {safe_response_url} -> {resp.status_code} ({ms}ms)", file=sys.stderr)

            if resp.status_code < 400:
                return HttpResponse(
                    status=resp.status_code,
                    headers={k.lower(): v for k, v in resp.headers.items()},
                    body=resp.content,
                    url=safe_response_url,
                )

            if attempt <= retries and resp.status_code in retry_on:
                time.sleep(min(2**attempt, 10))
                continue

            safe_body = redact_sensitive_text(resp.text, secrets=secrets)
            raise RuntimeError(f"HTTP {resp.status_code} for {method} {safe_response_url}\n{safe_body}")
