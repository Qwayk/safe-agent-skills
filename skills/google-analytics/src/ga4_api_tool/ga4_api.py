from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from .auth import authorization_header
from .config import Config
from .http import HttpClient, HttpResponse


@dataclass(frozen=True)
class ApiResult:
    status: int
    url: str
    json: Any | None
    text: str | None


class Ga4ApiClient:
    def __init__(self, *, cfg: Config, timeout_s: float, verbose: bool, user_agent: str):
        self._cfg = cfg
        self._http = HttpClient(timeout_s=timeout_s, verbose=verbose, user_agent=user_agent)

    def _base_url(self, service: str) -> str:
        if service == "admin":
            return self._cfg.admin_base_url
        if service == "data":
            return self._cfg.data_base_url
        raise ValueError(f"Unknown GA4 service token: {service}")

    def request(
        self,
        *,
        service: str,
        method: str,
        path: str,
        query: dict[str, Any] | None,
        body: dict[str, Any] | None,
        retries: int,
    ) -> ApiResult:
        base = self._base_url(service)
        url = base.rstrip("/") + "/" + path.lstrip("/")

        headers = {"Accept": "application/json", **authorization_header(self._cfg, refresh=True)}
        resp: HttpResponse = self._http.request(
            method=method,
            url=url,
            headers=headers,
            params=query,
            json_body=body,
            retries=retries,
        )
        parsed_json: Any | None = None
        parsed_text: str | None = None
        content_type = str(resp.headers.get("content-type") or "")
        if "application/json" in content_type:
            try:
                parsed_json = resp.json()
            except Exception:
                parsed_text = resp.text()
        else:
            parsed_text = resp.text()
            try:
                parsed_json = json.loads(parsed_text)
            except Exception:
                parsed_json = None
        return ApiResult(status=resp.status, url=resp.url, json=parsed_json, text=parsed_text)

