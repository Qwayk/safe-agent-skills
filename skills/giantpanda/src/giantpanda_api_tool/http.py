from __future__ import annotations

import dataclasses
import json
import sys
from typing import Any

import requests


class HttpError(RuntimeError):
    """HTTP failure from the provider."""


@dataclasses.dataclass(frozen=True)
class HttpResponse:
    status: int
    body: bytes
    url: str
    headers: dict[str, str]

    def json(self) -> Any:
        return json.loads(self.body.decode("utf-8"))


class HttpClient:
    def __init__(self, *, timeout_s: float, verbose: bool) -> None:
        self._timeout_s = timeout_s
        self._verbose = verbose
        self._session = requests.Session()

    @staticmethod
    def _hide_auth_headers(headers: dict[str, str] | None) -> dict[str, str]:
        if not headers:
            return {}
        out = dict(headers)
        if "Authorization" in out:
            out["Authorization"] = "***REDACTED***"
        return out

    def request(
        self,
        method: str,
        url: str,
        *,
        headers: dict[str, str] | None = None,
        params: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
        json_body: dict[str, Any] | None = None,
    ) -> HttpResponse:
        safe_headers = self._hide_auth_headers(headers)
        if self._verbose:
            print(
                f"[http] {method} {url} params={params or {}} headers={safe_headers}",
                file=sys.stderr,
            )

        try:
            resp = self._session.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                data=data,
                json=json_body,
                timeout=self._timeout_s,
                allow_redirects=False,
            )
        except requests.RequestException as exc:
            raise HttpError(f"{method} request failed") from exc

        if self._verbose:
            print(f"[http] {method} {resp.url} status={resp.status_code}", file=sys.stderr)

        if 300 <= resp.status_code < 400:
            raise HttpError(f"Redirect response refused for {method} {url}")

        if resp.status_code >= 400:
            raise HttpError(f"HTTP {resp.status_code} for {method} {url}")

        return HttpResponse(
            status=resp.status_code,
            body=resp.content,
            url=resp.url,
            headers={k.lower(): v for k, v in resp.headers.items()},
        )
