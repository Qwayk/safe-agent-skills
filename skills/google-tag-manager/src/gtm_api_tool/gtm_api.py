from __future__ import annotations

import dataclasses
import json
from typing import Any

from .auth import AccessToken, get_access_token
from .config import Config
from .http import HttpClient


@dataclasses.dataclass(frozen=True)
class ApiResponse:
    status: int
    url: str
    body_json: Any | None
    body_text: str | None


class GtmApi:
    def __init__(self, *, cfg: Config, verbose: bool, user_agent: str, timeout_s: float | None = None):
        self._cfg = cfg
        self._timeout_s = float(timeout_s) if timeout_s is not None else cfg.timeout_s
        self._http = HttpClient(
            timeout_s=self._timeout_s,
            verbose=verbose,
            user_agent=user_agent,
            min_delay_s=cfg.min_delay_s,
        )

    def _auth_header(self, tok: AccessToken) -> dict[str, str]:
        return {"Authorization": f"Bearer {tok.token}"}

    def request(
        self,
        *,
        http_method: str,
        path: str,
        query: dict[str, Any] | None = None,
        body: dict[str, Any] | None = None,
        retries: int = 0,
    ) -> ApiResponse:
        tok = get_access_token(self._cfg)
        url = self._cfg.base_url.rstrip("/") + "/" + str(path or "").lstrip("/")
        resp = self._http.request(
            method=http_method,
            url=url,
            headers=self._auth_header(tok),
            params=query,
            json_body=body,
            retries=int(retries),
        )
        bj = None
        bt = None
        try:
            bj = resp.json()
        except Exception:
            bt = resp.text()
        return ApiResponse(status=resp.status, url=resp.url, body_json=bj, body_text=bt)


def safe_error_from_http_exception(msg: str) -> dict[str, Any]:
    # Keep error payload safe and short (never include headers).
    return {"ok": False, "error": msg, "error_type": "HttpError"}
