from __future__ import annotations

import dataclasses
import json
from typing import Any

from .errors import ToolError, ValidationError
from .http import HttpClient


@dataclasses.dataclass(frozen=True)
class GraphQLResponse:
    http_status: int
    data: dict[str, Any] | None
    errors: list[dict[str, Any]] | None
    raw: dict[str, Any] | None


class ShopifyAdminGraphQLClient:
    def __init__(
        self,
        *,
        shop_domain: str,
        admin_access_token: str,
        api_version: str,
        timeout_s: float,
        verbose: bool,
        user_agent: str,
    ) -> None:
        shop = str(shop_domain or "").strip().removeprefix("https://").removeprefix("http://").strip().strip("/")
        if not shop:
            raise ValidationError("Missing shop_domain")
        if "." not in shop:
            raise ValidationError("Invalid SHOPIFY_SHOP_DOMAIN (expected a domain like your-shop.myshopify.com)")
        if not str(api_version or "").strip():
            raise ValidationError("Missing api_version")
        if not str(admin_access_token or "").strip():
            raise ValidationError("Missing admin_access_token")

        self._shop_domain = shop
        self._api_version = str(api_version).strip()
        self._http = HttpClient(timeout_s=timeout_s, verbose=verbose, user_agent=user_agent)
        self._token = str(admin_access_token).strip()

    @property
    def endpoint_url(self) -> str:
        return f"https://{self._shop_domain}/admin/api/{self._api_version}/graphql.json"

    def execute(self, *, query: str, variables: dict[str, Any]) -> GraphQLResponse:
        if not str(query or "").strip():
            raise ValidationError("Missing query")
        if not isinstance(variables, dict):
            raise ValidationError("variables must be an object/dict")

        headers = {
            "Content-Type": "application/json",
            "X-Shopify-Access-Token": self._token,
        }
        body = {"query": query, "variables": variables}

        resp = self._http.request(
            "POST",
            self.endpoint_url,
            headers=headers,
            json_body=body,
            allow_http_error=True,
            retries=0,
        )
        raw: dict[str, Any] | None
        try:
            raw_obj = json.loads(resp.body.decode("utf-8"))
            raw = raw_obj if isinstance(raw_obj, dict) else None
        except Exception:
            raw = None

        if raw is None:
            raise ToolError(f"Shopify Admin GraphQL returned non-JSON (HTTP {resp.status})")

        data = raw.get("data") if isinstance(raw.get("data"), dict) else None
        errors = raw.get("errors") if isinstance(raw.get("errors"), list) else None
        return GraphQLResponse(http_status=resp.status, data=data, errors=errors, raw=raw)

