from __future__ import annotations

import base64
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
    _SENSITIVE_QUERY_KEYS = {
        "access_token",
        "refresh_token",
        "accessjwt",
        "refreshjwt",
        "token",
        "password",
        "app_password",
        "secret",
        "id_token",
        "client_secret",
        "authorization",
    }

    _SENSITIVE_HEADER_KEYS = {
        "authorization",
        "proxy-authorization",
        "x-api-key",
        "x-auth-token",
    }

    _BEARER_REDACTION_RE = re.compile(
        r"(?i)(authorization\s*[:=]\s*)?(bearer)\s+[^\s\"']+"
    )

    def __init__(self, *, timeout_s: float, verbose: bool, user_agent: str):
        self._timeout_s = timeout_s
        self._verbose = verbose
        self._session = requests.Session()
        self._session.headers["User-Agent"] = user_agent

    @classmethod
    def redact_url(cls, url: str) -> str:
        try:
            parts = urlsplit(url)
            if not parts.query:
                return url
            query: list[tuple[str, str]] = []
            for key, value in parse_qsl(parts.query, keep_blank_values=True):
                if str(key).lower() in cls._SENSITIVE_QUERY_KEYS:
                    query.append((key, "***REDACTED***"))
                else:
                    query.append((key, value))
            safe_query = urlencode(query, doseq=True)
            return urlunsplit((parts.scheme, parts.netloc, parts.path, safe_query, parts.fragment))
        except Exception:
            return url

    @classmethod
    def redact_headers(cls, headers: dict[str, str] | None) -> dict[str, str] | None:
        if not headers:
            return None
        out: dict[str, str] = {}
        for key, value in headers.items():
            lk = str(key).lower()
            if lk in cls._SENSITIVE_HEADER_KEYS or lk.endswith("-token") or lk.endswith("_token") or lk == "authorization":
                out[key] = "***REDACTED***"
            else:
                out[key] = value
        return out

    @classmethod
    def _redact_json_value(cls, value: Any) -> Any:
        if isinstance(value, dict):
            out: dict[str, Any] = {}
            for key, item in value.items():
                lk = str(key).lower()
                if lk in cls._SENSITIVE_QUERY_KEYS or lk.endswith("_token") or lk == "password" or lk == "secret":
                    out[key] = "***REDACTED***"
                else:
                    out[key] = cls._redact_json_value(item)
            return out
        if isinstance(value, list):
            return [cls._redact_json_value(item) for item in value]
        return value

    @classmethod
    def _collect_sensitive_values(cls, value: Any, key: str | None = None, out: set[str] | None = None) -> set[str]:
        if out is None:
            out = set()
        if key and isinstance(value, str):
            if cls._is_sensitive_key_name(key):
                out.add(value)
            return out
        if isinstance(value, dict):
            for item_key, item_value in value.items():
                cls._collect_sensitive_values(item_value, key=str(item_key), out=out)
            return out
        if isinstance(value, (list, tuple)):
            for item in value:
                cls._collect_sensitive_values(item, key=key, out=out)
            return out
        return out

    @classmethod
    def _collect_auth_values(
        cls,
        *,
        headers: dict[str, str] | None,
        params: dict[str, Any] | None,
        json_body: Any,
        data: Any,
    ) -> set[str]:
        values = set()
        if headers:
            for key, value in headers.items():
                values.update(cls._collect_sensitive_values(value, key=key))
                if str(key).lower() == "authorization" and isinstance(value, str):
                    m = re.match(r"(?i)^bearer\s+(.+)$", value.strip())
                    if m:
                        values.add(m.group(1).strip())
                        values.add(value)
        cls._collect_sensitive_values(params, out=values)
        cls._collect_sensitive_values(json_body, out=values)
        cls._collect_sensitive_values(data, out=values)
        values.discard("")
        return values

    @classmethod
    def _is_sensitive_key_name(cls, key: str) -> bool:
        lk = str(key).lower()
        if lk in cls._SENSITIVE_QUERY_KEYS:
            return True
        if lk.endswith("_token") or lk.endswith("-token") or lk.endswith("token"):
            return True
        return lk in {"password", "secret", "authorization"}

    @classmethod
    def _redact_text(cls, value: str, *, secret_values: set[str]) -> str:
        redacted = cls.redact_url(value)
        redacted = cls._BEARER_REDACTION_RE.sub(
            lambda m: f"{m.group(1) or ''}Bearer ***REDACTED***",
            redacted,
        )
        if secret_values:
            for secret in sorted(secret_values, key=len, reverse=True):
                redacted = redacted.replace(secret, "***REDACTED***")
        return redacted

    @classmethod
    def _redact_error_body(cls, body: str, *, secret_values: set[str]) -> str:
        try:
            payload = json.loads(body)
            redacted = cls._redact_json_value(payload)
            return json.dumps(redacted)
        except Exception:
            return cls._redact_text(body, secret_values=secret_values)

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
        content: bytes | None = None,
        retries: int = 0,
        retry_on: tuple[int, ...] = (429, 500, 502, 503, 504),
    ) -> HttpResponse:
        attempt = 0
        display_url = self.redact_url(self._format_url(url, params))
        display_headers = self.redact_headers(headers)
        secret_values = self._collect_auth_values(
            headers=headers,
            params=params,
            json_body=json_body,
            data=data,
        )
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
                    data=content if content is not None else data,
                    timeout=self._timeout_s,
                )
            except requests.RequestException as e:
                ms = int((time.time() - start) * 1000)
                message = self._redact_text(f"{type(e).__name__}: {e}", secret_values=secret_values)
                if self._verbose:
                    print(
                        f"[http] {method} {display_url} -> EXCEPTION ({ms}ms): {message}",
                        file=sys.stderr,
                    )
                raise RuntimeError(
                    f"Request failed for {method} {display_url}: {message}"
                ) from e
            ms = int((time.time() - start) * 1000)
            if self._verbose:
                print(f"[http] {method} {self.redact_url(str(resp.url))} -> {resp.status_code} ({ms}ms)", file=sys.stderr)

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

            safe_url = self.redact_url(str(resp.url))
            safe_body = self._redact_error_body(resp.text, secret_values=secret_values)
            raise RuntimeError(f"HTTP {resp.status_code} for {method} {safe_url}\n{safe_body}")

    def capture_websocket_frames(
        self,
        url: str,
        *,
        headers: dict[str, str] | None = None,
        event_limit: int,
        idle_timeout_s: float | None = None,
    ) -> list[dict[str, Any]]:
        try:
            import websocket  # type: ignore[import-not-found]
        except Exception as e:  # noqa: BLE001
            raise RuntimeError(
                "websocket-client is required for live subscription calls. Install the tool dependencies first."
            ) from e

        timeout_s = float(idle_timeout_s if idle_timeout_s is not None else self._timeout_s)
        ws_url = url
        if ws_url.startswith("https://"):
            ws_url = "wss://" + ws_url[len("https://") :]
        elif ws_url.startswith("http://"):
            ws_url = "ws://" + ws_url[len("http://") :]

        header_lines = [f"{key}: {value}" for key, value in (headers or {}).items()]
        if self._verbose:
            print(f"[ws] connect {ws_url}", file=sys.stderr)
        conn = websocket.create_connection(ws_url, header=header_lines, timeout=timeout_s)
        try:
            frames: list[dict[str, Any]] = []
            for _ in range(max(1, int(event_limit))):
                frame = conn.recv()
                if isinstance(frame, bytes):
                    frames.append(
                        {
                            "type": "bytes",
                            "size": len(frame),
                            "body_base64": base64.b64encode(frame).decode("ascii"),
                        }
                    )
                    continue
                text = str(frame)
                try:
                    payload = json.loads(text)
                    frames.append({"type": "json", "body_json": payload})
                except Exception:
                    frames.append({"type": "text", "body_text": text})
            return frames
        finally:
            conn.close()
