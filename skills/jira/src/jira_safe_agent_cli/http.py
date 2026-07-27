from __future__ import annotations

import dataclasses
import json
import sys
import time
from typing import Any

import requests

from .config import Config
from .errors import ToolError


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


class HttpError(ToolError):
    def __init__(self, *, status: int, method: str, url: str):
        super().__init__(f"Jira returned HTTP {status} for {method} {url}")
        self.status = status
        self.method = method
        self.url = url


class HttpClient:
    def __init__(self, *, config: Config, verbose: bool, user_agent: str):
        self._config = config
        self._verbose = verbose
        self._session = requests.Session()
        self._session.headers.update({"Accept": "application/json", "User-Agent": user_agent})

    def _auth(self) -> tuple[str, str] | None:
        if self._config.auth_mode == "basic":
            assert self._config.email is not None and self._config.api_token is not None
            return (self._config.email, self._config.api_token)
        return None

    def _headers(self, headers: dict[str, str] | None) -> dict[str, str]:
        result = dict(headers or {})
        if self._config.auth_mode == "bearer":
            assert self._config.oauth_access_token is not None
            result["Authorization"] = f"Bearer {self._config.oauth_access_token}"
        return result

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
        raise_for_status: bool = True,
    ) -> HttpResponse:
        attempt = 0
        while True:
            attempt += 1
            started = time.time()
            if self._verbose:
                print(f"[http] {method} {url} (start)", file=sys.stderr)
            try:
                response = self._session.request(
                    method=method,
                    url=url,
                    headers=self._headers(headers),
                    params=params,
                    json=json_body,
                    data=data,
                    files=files,
                    auth=self._auth(),
                    timeout=self._config.timeout_s,
                )
            except requests.RequestException as exc:
                raise ToolError(f"Jira request failed: {type(exc).__name__}") from None
            elapsed_ms = int((time.time() - started) * 1000)
            if self._verbose:
                print(
                    f"[http] {method} {response.url} -> {response.status_code} ({elapsed_ms}ms)",
                    file=sys.stderr,
                )
            if response.status_code in {429, 500, 502, 503, 504} and attempt <= retries:
                time.sleep(min(2**attempt, 10))
                continue
            result = HttpResponse(
                status=response.status_code,
                headers={key.lower(): value for key, value in response.headers.items()},
                body=response.content,
                url=response.url,
            )
            if raise_for_status and result.status >= 400:
                raise HttpError(status=result.status, method=method, url=result.url)
            return result
