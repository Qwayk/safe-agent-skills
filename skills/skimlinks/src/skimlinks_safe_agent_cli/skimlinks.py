from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlencode, urljoin

from . import __version__
from .config import Config
from .errors import ValidationError
from .http import HttpClient, redact_url

SHARED_SCOPE = "shared"
PRODUCT_SCOPE = "product"


@dataclass(frozen=True)
class Credentials:
    client_id: str
    client_secret: str
    source: str


def make_http_client(ctx: dict[str, Any]) -> HttpClient:
    timeout_s = float(ctx.get("timeout_s") or 30)
    verbose = bool(ctx.get("verbose"))
    return HttpClient(
        timeout_s=timeout_s,
        verbose=verbose,
        user_agent=f"qwayk-skimlinks-safe-agent-cli/{__version__}",
    )


def require_publisher_id(cfg: Config, override: str | None = None) -> str:
    publisher_id = str(override or cfg.publisher_id or "").strip()
    if not publisher_id:
        raise ValidationError("Missing publisher ID. Set SKIMLINKS_PUBLISHER_ID or pass --publisher-id.")
    return publisher_id


def clean_params(params: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key, value in params.items():
        if value is None:
            continue
        if isinstance(value, str) and value == "":
            continue
        if isinstance(value, list):
            if value:
                out[key] = value
            continue
        out[key] = value
    return out


def safe_params(params: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in params.items() if k != "access_token"}


class SkimlinksClient:
    def __init__(self, *, cfg: Config, http: HttpClient):
        self.cfg = cfg
        self.http = http
        self._token_cache: dict[str, dict[str, Any]] = {}

    def credentials_for_scope(self, scope: str) -> Credentials:
        if scope == PRODUCT_SCOPE:
            if self.cfg.product_client_id and self.cfg.product_client_secret:
                return Credentials(
                    client_id=self.cfg.product_client_id,
                    client_secret=self.cfg.product_client_secret,
                    source="product",
                )
            if self.cfg.client_id and self.cfg.client_secret:
                return Credentials(
                    client_id=self.cfg.client_id,
                    client_secret=self.cfg.client_secret,
                    source="shared-fallback",
                )
            raise ValidationError(
                "Missing Product Key credentials. Set SKIMLINKS_PRODUCT_CLIENT_ID and "
                "SKIMLINKS_PRODUCT_CLIENT_SECRET, or shared SKIMLINKS_CLIENT_ID and "
                "SKIMLINKS_CLIENT_SECRET as a fallback."
            )

        if self.cfg.client_id and self.cfg.client_secret:
            return Credentials(
                client_id=self.cfg.client_id,
                client_secret=self.cfg.client_secret,
                source="shared",
            )
        raise ValidationError(
            "Missing Skimlinks credentials. Set SKIMLINKS_CLIENT_ID and SKIMLINKS_CLIENT_SECRET."
        )

    def access_token(self, *, scope: str = SHARED_SCOPE) -> dict[str, Any]:
        if scope in self._token_cache:
            return self._token_cache[scope]

        creds = self.credentials_for_scope(scope)
        response = self.http.request(
            "POST",
            self.cfg.auth_url,
            headers={"Content-Type": "application/json"},
            json_body={
                "client_id": creds.client_id,
                "client_secret": creds.client_secret,
                "grant_type": "client_credentials",
            },
        )
        body = response.json()
        if not isinstance(body, dict) or not body.get("access_token"):
            raise RuntimeError("Authentication response did not include access_token")
        token = {
            "access_token": str(body["access_token"]),
            "timestamp": body.get("timestamp"),
            "expiry_timestamp": body.get("expiry_timestamp"),
            "credential_source": creds.source,
        }
        self._token_cache[scope] = token
        return token

    def auth_check(self, *, scope: str) -> dict[str, Any]:
        token = self.access_token(scope=scope)
        return {
            "ok": True,
            "scope": scope,
            "credential_source": token.get("credential_source"),
            "token_received": True,
            "timestamp": token.get("timestamp"),
            "expiry_timestamp": token.get("expiry_timestamp"),
            "product_access_note": (
                "Product Key may still be disabled by Skimlinks even when shared credentials "
                "can mint a token."
                if scope == PRODUCT_SCOPE and token.get("credential_source") == "shared-fallback"
                else None
            ),
        }

    def get_json(
        self,
        *,
        base_url: str,
        path: str,
        params: dict[str, Any] | None = None,
        scope: str | None = SHARED_SCOPE,
    ) -> dict[str, Any]:
        all_params = clean_params(dict(params or {}))
        if scope:
            all_params["access_token"] = self.access_token(scope=scope)["access_token"]
        url = urljoin(base_url.rstrip("/") + "/", path.lstrip("/"))
        response = self.http.request("GET", url, params=all_params)
        data = response.json()
        return {
            "ok": True,
            "method": "GET",
            "url": redact_url(response.url),
            "path": path,
            "params": safe_params(all_params),
            "data": data,
        }

    def get_ndjson(
        self,
        *,
        base_url: str,
        path: str,
        params: dict[str, Any] | None = None,
        scope: str = SHARED_SCOPE,
    ) -> dict[str, Any]:
        all_params = clean_params(dict(params or {}))
        all_params["access_token"] = self.access_token(scope=scope)["access_token"]
        url = urljoin(base_url.rstrip("/") + "/", path.lstrip("/"))
        response = self.http.request("GET", url, params=all_params)
        rows = []
        for line in response.text().splitlines():
            stripped = line.strip()
            if stripped:
                rows.append(json.loads(stripped))
        return {
            "ok": True,
            "method": "GET",
            "url": redact_url(response.url),
            "path": path,
            "params": safe_params(all_params),
            "content_type": "application/x-ndjson",
            "rows": rows,
            "count": len(rows),
        }

    def post_json(
        self,
        *,
        base_url: str,
        path: str,
        params: dict[str, Any] | None = None,
        body: dict[str, Any] | None = None,
        scope: str = PRODUCT_SCOPE,
    ) -> dict[str, Any]:
        all_params = clean_params(dict(params or {}))
        all_params["access_token"] = self.access_token(scope=scope)["access_token"]
        url = urljoin(base_url.rstrip("/") + "/", path.lstrip("/"))
        query = f"?{urlencode(all_params, doseq=True)}" if all_params else ""
        response = self.http.request("POST", url + query, json_body=body or {})
        return {
            "ok": True,
            "method": "POST",
            "read_like": True,
            "url": redact_url(response.url),
            "path": path,
            "params": safe_params(all_params),
            "data": response.json(),
        }
