from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .config import Config
from .http import HttpClient


@dataclass(frozen=True)
class FreepikApi:
    cfg: Config
    http: HttpClient

    def _auth_headers(self) -> dict[str, str]:
        headers = {self.cfg.auth_header: f"{self.cfg.auth_prefix}{self.cfg.api_key}"}
        if self.cfg.accept_language:
            headers["Accept-Language"] = self.cfg.accept_language
        return headers

    def get_resources(self, *, query: str, page: int, limit: int, extra_params: dict[str, Any]) -> Any:
        params: dict[str, Any] = {"term": query, "page": page, "limit": limit}
        params.update(extra_params)
        url = f"{self.cfg.base_url}/resources"
        resp = self.http.request("GET", url, headers=self._auth_headers(), params=params, retries=2)
        return resp.json()

    def get_resource(self, resource_id: str) -> Any:
        url = f"{self.cfg.base_url}/resources/{resource_id}"
        resp = self.http.request("GET", url, headers=self._auth_headers(), retries=2)
        return resp.json()

    def download_by_id(self, resource_id: str, *, image_size: str | None = None) -> Any:
        params: dict[str, Any] = {}
        if image_size:
            params["image_size"] = image_size
        url = f"{self.cfg.base_url}/resources/{resource_id}/download"
        resp = self.http.request("GET", url, headers=self._auth_headers(), params=params or None, retries=2)
        return resp.json()

    def download_by_id_and_format(self, resource_id: str, *, fmt: str) -> Any:
        url = f"{self.cfg.base_url}/resources/{resource_id}/download/{fmt}"
        resp = self.http.request("GET", url, headers=self._auth_headers(), retries=2)
        return resp.json()
