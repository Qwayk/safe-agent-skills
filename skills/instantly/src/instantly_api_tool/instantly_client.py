from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .before_state import capture_before_state_if_needed
from .config import Config
from .http import HttpClient


@dataclass(frozen=True)
class InstantlyResponse:
    ok: bool
    status: int
    data: Any
    url: str
    next_starting_after: str | None = None


def _maybe_next_starting_after(obj: Any) -> str | None:
    if not isinstance(obj, dict):
        return None
    v = obj.get("next_starting_after")
    if v is None:
        return None
    s = str(v).strip()
    return s or None


class InstantlyClient:
    def __init__(self, *, cfg: Config, http: HttpClient):
        self._cfg = cfg
        self._http = http

    def _url(self, path: str) -> str:
        return f"{self._cfg.base_url.rstrip('/')}/{path.lstrip('/')}"

    def _auth_headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self._cfg.api_key}"}

    def request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json_body: dict[str, Any] | None = None,
    ) -> InstantlyResponse:
        capture_before_state_if_needed(self, method, path, json_body)
        resp = self._http.request(
            method,
            self._url(path),
            headers=self._auth_headers(),
            params=params,
            json_body=json_body,
        )
        data = resp.json()
        return InstantlyResponse(
            ok=True,
            status=resp.status,
            data=data,
            url=resp.url,
            next_starting_after=_maybe_next_starting_after(data),
        )

    def get(self, path: str, *, params: dict[str, Any] | None = None) -> InstantlyResponse:
        return self.request("GET", path, params=params)

    def post(
        self,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json_body: dict[str, Any] | None = None,
    ) -> InstantlyResponse:
        return self.request("POST", path, params=params, json_body=json_body)

    def patch(
        self,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json_body: dict[str, Any] | None = None,
    ) -> InstantlyResponse:
        return self.request("PATCH", path, params=params, json_body=json_body)

    def delete(
        self,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json_body: dict[str, Any] | None = None,
    ) -> InstantlyResponse:
        return self.request("DELETE", path, params=params, json_body=json_body)
