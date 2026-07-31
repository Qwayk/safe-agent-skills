from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

import requests


class Transport(Protocol):
    def request(
        self,
        method: str,
        url: str,
        *,
        headers: dict[str, str] | None = None,
        params: dict[str, Any] | None = None,
        json_body: dict[str, Any] | list[Any] | None = None,
        timeout_s: float = 30.0,
    ) -> TransportResponse:
        ...


@dataclass(frozen=True)
class TransportResponse:
    status: int
    headers: dict[str, str]
    body: bytes
    url: str


class RequestsTransport:
    """Production transport using requests."""

    def request(
        self,
        method: str,
        url: str,
        *,
        headers: dict[str, str] | None = None,
        params: dict[str, Any] | None = None,
        json_body: dict[str, Any] | list[Any] | None = None,
        timeout_s: float = 30.0,
    ) -> TransportResponse:
        resp = requests.request(
            method=method,
            url=url,
            headers=headers,
            params=params,
            json=json_body,
            timeout=timeout_s,
            allow_redirects=False,
        )
        return TransportResponse(
            status=resp.status_code,
            headers={k.lower(): str(v) for k, v in resp.headers.items()},
            body=resp.content,
            url=resp.url,
        )
