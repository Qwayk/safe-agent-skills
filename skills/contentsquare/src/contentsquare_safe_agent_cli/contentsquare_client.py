from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .config import Config
from .http import HttpClient


@dataclass(frozen=True)
class TokenInfo:
    access_token: str
    endpoint: str | None
    expires_in: int | None
    scope: str | None


def _json_body(path: str | None) -> dict[str, Any]:
    if not path:
        return {}
    text = Path(path).read_text(encoding="utf-8")
    obj = json.loads(text)
    if not isinstance(obj, dict):
        raise RuntimeError("JSON body file must contain one object")
    return obj


class ContentsquareClient:
    def __init__(self, *, cfg: Config, timeout_s: float, verbose: bool, oauth_project_id: str | None = None):
        self.cfg = cfg
        self.oauth_project_id = oauth_project_id or cfg.oauth_project_id
        self.http = HttpClient(
            timeout_s=timeout_s,
            verbose=verbose,
            user_agent="qwayk-contentsquare-safe-agent-cli/0.1.0",
        )
        self._tokens: dict[tuple[str | None, str | None, str | None], TokenInfo] = {}

    def token(
        self,
        *,
        scope: str | None = None,
        integration_id: str | None = None,
        project_id: str | None = None,
    ) -> TokenInfo:
        token_project_id = project_id or self.oauth_project_id
        cache_key = (scope, integration_id, token_project_id)
        if cache_key in self._tokens:
            return self._tokens[cache_key]
        data: dict[str, str] = {
            "grant_type": "client_credentials",
            "client_id": self.cfg.client_id,
            "client_secret": self.cfg.client_secret,
        }
        if scope:
            data["scope"] = scope
        if token_project_id:
            data["project_id"] = str(token_project_id)
        if integration_id:
            data["integration_id"] = integration_id
        resp = self.http.request("POST", f"{self.cfg.auth_base_url}/v1/oauth/token", json_body=data)
        payload = resp.json()
        token = payload.get("access_token")
        if not isinstance(token, str) or not token:
            raise RuntimeError("Contentsquare token response did not include an access token")
        endpoint = payload.get("endpoint") or payload.get("api_endpoint") or payload.get("base_url")
        token_info = TokenInfo(
            access_token=token,
            endpoint=endpoint if isinstance(endpoint, str) else None,
            expires_in=payload.get("expires_in") if isinstance(payload.get("expires_in"), int) else None,
            scope=payload.get("scope") if isinstance(payload.get("scope"), str) else scope,
        )
        self._tokens[cache_key] = token_info
        return token_info

    def api_base_url(self, *, scope: str | None = None, integration_id: str | None = None) -> str:
        if self.cfg.api_base_url:
            return self.cfg.api_base_url.rstrip("/")
        token = self.token(scope=scope, integration_id=integration_id)
        if token.endpoint:
            return token.endpoint.rstrip("/")
        return self.cfg.auth_base_url.rstrip("/")

    def me(self) -> dict[str, Any]:
        resp = self.http.request(
            "POST",
            f"{self.cfg.auth_base_url}/v1/oauth/me",
            json_body={
                "client_id": self.cfg.client_id,
                "client_secret": self.cfg.client_secret,
            },
        )
        payload = resp.json()
        return payload if isinstance(payload, dict) else {"value": payload}

    def request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        body: dict[str, Any] | None = None,
        scope: str | None = None,
        integration_id: str | None = None,
    ) -> Any:
        token = self.token(scope=scope, integration_id=integration_id)
        base = self.api_base_url(scope=scope, integration_id=integration_id)
        resp = self.http.request(
            method,
            f"{base}{path}",
            headers={"Authorization": f"Bearer {token.access_token}"},
            params=params,
            json_body=body,
            retries=2,
        )
        try:
            return resp.json()
        except Exception:
            return {"status": resp.status, "text": resp.text()}


def read_json_body(path: str | None) -> dict[str, Any]:
    return _json_body(path)
