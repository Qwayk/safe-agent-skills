from __future__ import annotations

from typing import Any

from .config import ContentConfig
from .http import HttpClient, HttpResponse


class GhostContentApi:
    def __init__(self, *, cfg: ContentConfig, http: HttpClient):
        self._cfg = cfg
        self._http = http

    def request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
    ) -> HttpResponse:
        url = self._cfg.content_api_url + path.lstrip("/")
        headers = {"Accept-Version": self._cfg.accept_version}
        req_params = dict(params or {})
        req_params["key"] = self._cfg.content_api_key
        return self._http.request(method, url, headers=headers, params=req_params)

    def posts_browse(self, *, params: dict[str, Any] | None = None) -> dict[str, Any]:
        return self.request("GET", "/posts/", params=params).json()

    def posts_read_by_id(self, post_id: str, *, params: dict[str, Any] | None = None) -> dict[str, Any]:
        return self.request("GET", f"/posts/{post_id}/", params=params).json()

    def posts_read_by_slug(self, slug: str, *, params: dict[str, Any] | None = None) -> dict[str, Any]:
        return self.request("GET", f"/posts/slug/{slug}/", params=params).json()

    def pages_browse(self, *, params: dict[str, Any] | None = None) -> dict[str, Any]:
        return self.request("GET", "/pages/", params=params).json()

    def pages_read_by_id(self, page_id: str, *, params: dict[str, Any] | None = None) -> dict[str, Any]:
        return self.request("GET", f"/pages/{page_id}/", params=params).json()

    def pages_read_by_slug(self, slug: str, *, params: dict[str, Any] | None = None) -> dict[str, Any]:
        return self.request("GET", f"/pages/slug/{slug}/", params=params).json()

    def tags_browse(self, *, params: dict[str, Any] | None = None) -> dict[str, Any]:
        return self.request("GET", "/tags/", params=params).json()

    def tags_read_by_id(self, tag_id: str, *, params: dict[str, Any] | None = None) -> dict[str, Any]:
        return self.request("GET", f"/tags/{tag_id}/", params=params).json()

    def tags_read_by_slug(self, slug: str, *, params: dict[str, Any] | None = None) -> dict[str, Any]:
        return self.request("GET", f"/tags/slug/{slug}/", params=params).json()

    def authors_browse(self, *, params: dict[str, Any] | None = None) -> dict[str, Any]:
        return self.request("GET", "/authors/", params=params).json()

    def authors_read_by_id(self, author_id: str, *, params: dict[str, Any] | None = None) -> dict[str, Any]:
        return self.request("GET", f"/authors/{author_id}/", params=params).json()

    def authors_read_by_slug(self, slug: str, *, params: dict[str, Any] | None = None) -> dict[str, Any]:
        return self.request("GET", f"/authors/slug/{slug}/", params=params).json()

    def tiers_browse(self, *, params: dict[str, Any] | None = None) -> dict[str, Any]:
        return self.request("GET", "/tiers/", params=params).json()

    def settings_get(self) -> dict[str, Any]:
        return self.request("GET", "/settings/").json()

