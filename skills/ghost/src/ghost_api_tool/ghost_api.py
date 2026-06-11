from __future__ import annotations

import mimetypes
import os
from typing import Any

from .auth_jwt import JwtCache, generate_admin_jwt
from .config import Config
from .http import HttpClient, HttpResponse


class GhostAdminApi:
    def __init__(self, *, cfg: Config, http: HttpClient):
        self._cfg = cfg
        self._http = http
        self._jwt_cache = JwtCache()

    def _auth_headers(self) -> dict[str, str]:
        token = self._jwt_cache.get_valid()
        if not token:
            token, exp = generate_admin_jwt(self._cfg.admin_api_key)
            self._jwt_cache.set(token, exp)
        return {
            "Authorization": f"Ghost {token}",
            "Accept-Version": self._cfg.accept_version,
        }

    def request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json_body: dict[str, Any] | None = None,
        files: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
    ) -> HttpResponse:
        url = self._cfg.admin_api_url + path.lstrip("/")
        headers = self._auth_headers()
        if json_body is not None:
            headers = {**headers, "Content-Type": "application/json"}
        return self._http.request(
            method,
            url,
            headers=headers,
            params=params,
            json_body=json_body,
            files=files,
            data=data,
        )

    def get_site(self) -> dict[str, Any]:
        # This endpoint is unauthenticated, but we keep auth headers consistent.
        resp = self.request("GET", "/site/")
        return resp.json()

    def members_browse(self, *, params: dict[str, Any] | None = None) -> dict[str, Any]:
        resp = self.request("GET", "/members/", params=params)
        return resp.json()

    def members_read_by_id(self, member_id: str, *, params: dict[str, Any] | None = None) -> dict[str, Any]:
        resp = self.request("GET", f"/members/{member_id}/", params=params)
        return resp.json()

    def members_create(self, payload: dict[str, Any], *, params: dict[str, Any] | None = None) -> dict[str, Any]:
        resp = self.request("POST", "/members/", params=params, json_body=payload)
        return resp.json()

    def members_update(self, member_id: str, payload: dict[str, Any], *, params: dict[str, Any] | None = None) -> dict[str, Any]:
        resp = self.request("PUT", f"/members/{member_id}/", params=params, json_body=payload)
        return resp.json()

    def newsletters_browse(self, *, params: dict[str, Any] | None = None) -> dict[str, Any]:
        resp = self.request("GET", "/newsletters/", params=params)
        return resp.json()

    def newsletters_read_by_id(self, newsletter_id: str, *, params: dict[str, Any] | None = None) -> dict[str, Any]:
        resp = self.request("GET", f"/newsletters/{newsletter_id}/", params=params)
        return resp.json()

    def newsletters_create(self, payload: dict[str, Any], *, params: dict[str, Any] | None = None) -> dict[str, Any]:
        resp = self.request("POST", "/newsletters/", params=params, json_body=payload)
        return resp.json()

    def newsletters_update(
        self,
        newsletter_id: str,
        payload: dict[str, Any],
        *,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        resp = self.request("PUT", f"/newsletters/{newsletter_id}/", params=params, json_body=payload)
        return resp.json()

    def posts_browse(self, *, params: dict[str, Any] | None = None) -> dict[str, Any]:
        resp = self.request("GET", "/posts/", params=params)
        return resp.json()

    def posts_read_by_slug(self, slug: str, *, params: dict[str, Any] | None = None) -> dict[str, Any]:
        resp = self.request("GET", f"/posts/slug/{slug}/", params=params)
        return resp.json()

    def posts_read_by_id(self, post_id: str, *, params: dict[str, Any] | None = None) -> dict[str, Any]:
        resp = self.request("GET", f"/posts/{post_id}/", params=params)
        return resp.json()

    def posts_update(self, post_id: str, payload: dict[str, Any], *, params: dict[str, Any] | None = None) -> dict[str, Any]:
        resp = self.request("PUT", f"/posts/{post_id}/", params=params, json_body=payload)
        return resp.json()

    def posts_delete(self, post_id: str) -> HttpResponse:
        return self.request("DELETE", f"/posts/{post_id}/")

    def posts_create(self, payload: dict[str, Any], *, params: dict[str, Any] | None = None) -> dict[str, Any]:
        resp = self.request("POST", "/posts/", params=params, json_body=payload)
        return resp.json()

    def pages_browse(self, *, params: dict[str, Any] | None = None) -> dict[str, Any]:
        resp = self.request("GET", "/pages/", params=params)
        return resp.json()

    def pages_read_by_slug(self, slug: str, *, params: dict[str, Any] | None = None) -> dict[str, Any]:
        resp = self.request("GET", f"/pages/slug/{slug}/", params=params)
        return resp.json()

    def pages_read_by_id(self, page_id: str, *, params: dict[str, Any] | None = None) -> dict[str, Any]:
        resp = self.request("GET", f"/pages/{page_id}/", params=params)
        return resp.json()

    def pages_update(self, page_id: str, payload: dict[str, Any], *, params: dict[str, Any] | None = None) -> dict[str, Any]:
        resp = self.request("PUT", f"/pages/{page_id}/", params=params, json_body=payload)
        return resp.json()

    def pages_create(self, payload: dict[str, Any], *, params: dict[str, Any] | None = None) -> dict[str, Any]:
        resp = self.request("POST", "/pages/", params=params, json_body=payload)
        return resp.json()

    def pages_delete(self, page_id: str) -> HttpResponse:
        return self.request("DELETE", f"/pages/{page_id}/")

    def tags_browse(self, *, params: dict[str, Any] | None = None) -> dict[str, Any]:
        resp = self.request("GET", "/tags/", params=params)
        return resp.json()

    def tags_read_by_id(self, tag_id: str, *, params: dict[str, Any] | None = None) -> dict[str, Any]:
        resp = self.request("GET", f"/tags/{tag_id}/", params=params)
        return resp.json()

    def tags_delete(self, tag_id: str) -> HttpResponse:
        return self.request("DELETE", f"/tags/{tag_id}/")

    def tags_create(self, payload: dict[str, Any], *, params: dict[str, Any] | None = None) -> dict[str, Any]:
        resp = self.request("POST", "/tags/", params=params, json_body=payload)
        return resp.json()

    def tags_update(self, tag_id: str, payload: dict[str, Any], *, params: dict[str, Any] | None = None) -> dict[str, Any]:
        resp = self.request("PUT", f"/tags/{tag_id}/", params=params, json_body=payload)
        return resp.json()

    def posts_copy(self, post_id: str, *, params: dict[str, Any] | None = None) -> dict[str, Any]:
        resp = self.request("POST", f"/posts/{post_id}/copy", params=params)
        return resp.json()

    def pages_copy(self, page_id: str, *, params: dict[str, Any] | None = None) -> dict[str, Any]:
        resp = self.request("POST", f"/pages/{page_id}/copy", params=params)
        return resp.json()

    def tiers_browse(self, *, params: dict[str, Any] | None = None) -> dict[str, Any]:
        resp = self.request("GET", "/tiers/", params=params)
        return resp.json()

    def tiers_read_by_id(self, tier_id: str, *, params: dict[str, Any] | None = None) -> dict[str, Any]:
        resp = self.request("GET", f"/tiers/{tier_id}/", params=params)
        return resp.json()

    def tiers_create(self, payload: dict[str, Any], *, params: dict[str, Any] | None = None) -> dict[str, Any]:
        resp = self.request("POST", "/tiers/", params=params, json_body=payload)
        return resp.json()

    def tiers_update(self, tier_id: str, payload: dict[str, Any], *, params: dict[str, Any] | None = None) -> dict[str, Any]:
        resp = self.request("PUT", f"/tiers/{tier_id}/", params=params, json_body=payload)
        return resp.json()

    def offers_browse(self, *, params: dict[str, Any] | None = None) -> dict[str, Any]:
        resp = self.request("GET", "/offers/", params=params)
        return resp.json()

    def offers_read_by_id(self, offer_id: str, *, params: dict[str, Any] | None = None) -> dict[str, Any]:
        resp = self.request("GET", f"/offers/{offer_id}/", params=params)
        return resp.json()

    def offers_create(self, payload: dict[str, Any], *, params: dict[str, Any] | None = None) -> dict[str, Any]:
        resp = self.request("POST", "/offers/", params=params, json_body=payload)
        return resp.json()

    def offers_update(self, offer_id: str, payload: dict[str, Any], *, params: dict[str, Any] | None = None) -> dict[str, Any]:
        resp = self.request("PUT", f"/offers/{offer_id}/", params=params, json_body=payload)
        return resp.json()

    def themes_upload(self, *, file_path: str, upload_name: str | None = None) -> dict[str, Any]:
        if not os.path.exists(file_path):
            raise RuntimeError(f"File not found: {file_path}")
        content_type, _ = mimetypes.guess_type(file_path)
        if not content_type:
            content_type = "application/zip"
        with open(file_path, "rb") as f:
            if isinstance(upload_name, str) and upload_name.strip():
                candidate = upload_name.strip().replace("\\", "/")
                name = os.path.basename(candidate)
            else:
                name = os.path.basename(file_path)
            if not name:
                name = "theme.zip"
            files = {"file": (name, f, content_type)}
            resp = self.request("POST", "/themes/upload", files=files)
            return resp.json()

    def themes_activate(self, theme_name: str) -> dict[str, Any]:
        resp = self.request("PUT", f"/themes/{theme_name}/activate")
        return resp.json()

    def webhooks_create(self, payload: dict[str, Any], *, params: dict[str, Any] | None = None) -> dict[str, Any]:
        resp = self.request("POST", "/webhooks/", params=params, json_body=payload)
        return resp.json()

    def webhooks_update(self, webhook_id: str, payload: dict[str, Any], *, params: dict[str, Any] | None = None) -> dict[str, Any]:
        resp = self.request("PUT", f"/webhooks/{webhook_id}/", params=params, json_body=payload)
        return resp.json()

    def webhooks_delete(self, webhook_id: str) -> HttpResponse:
        return self.request("DELETE", f"/webhooks/{webhook_id}/")

    def upload_image(
        self,
        *,
        file_path: str,
        purpose: str,
        ref: str | None,
        upload_name: str | None = None,
    ) -> dict[str, Any]:
        if not os.path.exists(file_path):
            raise RuntimeError(f"File not found: {file_path}")
        data = {"purpose": purpose}
        if ref is not None:
            data["ref"] = ref
        content_type, _ = mimetypes.guess_type(file_path)
        if not content_type:
            content_type = "application/octet-stream"
        with open(file_path, "rb") as f:
            if isinstance(upload_name, str) and upload_name.strip():
                # Prevent path traversal / weird filenames. Ghost only needs a filename.
                candidate = upload_name.strip().replace("\\", "/")
                name = os.path.basename(candidate)
            else:
                name = os.path.basename(file_path)
            if not name:
                name = "upload"
            files = {"file": (name, f, content_type)}
            resp = self.request("POST", "/images/upload/", files=files, data=data)
            return resp.json()
