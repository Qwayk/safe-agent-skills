from __future__ import annotations

import base64
import json
from dataclasses import dataclass
from typing import Any
from urllib.parse import urljoin

from .config import Config
from .errors import SafetyError
from .http import HttpClient, HttpResponse


def _join_url(base_url: str, path: str) -> str:
    # urljoin treats paths without trailing slash as file segments, so normalize.
    return urljoin(base_url.rstrip("/") + "/", path.lstrip("/"))


def _basic_auth_header(token: str) -> str:
    # Mercury's OpenAPI describes Basic auth as `username=token, password=(empty)`.
    raw = f"{token}:".encode("utf-8")
    b64 = base64.b64encode(raw).decode("ascii")
    return f"Basic {b64}"


@dataclass(frozen=True)
class MercuryRequest:
    method: str
    url: str
    params: dict[str, Any] | None


class MercuryClient:
    def __init__(self, *, cfg: Config, http: HttpClient):
        self._cfg = cfg
        self._http = http

    def _auth_headers(self) -> dict[str, str]:
        if self._cfg.auth_scheme == "basic":
            return {"Authorization": _basic_auth_header(self._cfg.token)}
        return {"Authorization": f"Bearer {self._cfg.token}"}

    def request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        accept: str | None = None,
    ) -> HttpResponse:
        if method.upper() != "GET":
            raise SafetyError("Refused: Mercury tool is read-only and only allows GET requests")
        url = _join_url(self._cfg.base_url, path)
        headers = self._auth_headers()
        if accept:
            headers["Accept"] = accept
        return self._http.request("GET", url, headers=headers, params=params)

    def get_json(self, path: str, *, params: dict[str, Any] | None = None) -> Any:
        resp = self.request("GET", path, params=params, accept="application/json")
        try:
            return json.loads(resp.body.decode("utf-8"))
        except Exception as e:  # noqa: BLE001
            raise RuntimeError(f"Invalid JSON response from Mercury for GET {resp.url}: {type(e).__name__}: {e}") from None

    def get_pdf(self, path: str, *, params: dict[str, Any] | None = None) -> bytes:
        resp = self.request("GET", path, params=params, accept="application/pdf")
        return resp.body

    def get_bytes_from_url(self, url: str) -> bytes:
        # Attachment download URLs are signed and should not require Authorization.
        resp = self._http.request("GET", url)
        return resp.body
