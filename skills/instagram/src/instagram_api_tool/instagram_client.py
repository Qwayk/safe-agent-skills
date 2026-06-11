from __future__ import annotations

from urllib.parse import urlencode
from typing import Any

from . import __version__
from .config import Config
from .errors import ToolError, ValidationError
from .http import HttpClient, HttpResponse
from .oauth_tokens import read_access_token, token_path_for_env_file


class InstagramAPIClient:
    def __init__(
        self,
        cfg: Config,
        *,
        env_file: str,
        timeout_s: float,
        verbose: bool,
        token: str | None = None,
    ) -> None:
        self.cfg = cfg
        self.env_file = env_file
        self._token_override = token
        self._http = HttpClient(
            timeout_s=timeout_s,
            verbose=verbose,
            user_agent=f"instagram-api-tool/{__version__}",
        )

    def _graph_base(self, *, use_version: bool = True) -> str:
        base = self.cfg.base_url.rstrip("/")
        if not use_version:
            return base
        version = (self.cfg.graph_version or "").strip().strip("/")
        if not version:
            return base
        return f"{base}/{version}"

    def _graph_url(self, path: str, *, use_version: bool = True) -> str:
        return f"{self._graph_base(use_version=use_version)}/{str(path).lstrip('/')}"

    def _auth_api_url(self, path: str) -> str:
        return f"{self.cfg.auth_api_base_url.rstrip('/')}/{str(path).lstrip('/')}"

    def _auth_web_url(self, path: str) -> str:
        return f"{self.cfg.auth_web_base_url.rstrip('/')}/{str(path).lstrip('/')}"

    def _need_str(self, name: str, value: str | None) -> str:
        if not value or not str(value).strip():
            raise ValidationError(f"Missing required Instagram setting: {name}")
        return str(value).strip()

    def _token_from_state(self) -> str | None:
        return read_access_token(token_path_for_env_file(self.env_file))

    def _resolve_access_token(self) -> str:
        override = self._token_override
        if isinstance(override, str) and override.strip():
            return override.strip()
        if isinstance(self.cfg.token, str) and self.cfg.token.strip():
            return self.cfg.token.strip()
        token = self._token_from_state()
        if token:
            return token
        raise ValidationError("Missing access token. Run auth token set or auth code exchange.")

    @staticmethod
    def _parse_json_response(response: HttpResponse) -> Any:
        try:
            payload = response.json()
        except Exception as e:  # noqa: BLE001
            raise ToolError(
                f"Non-JSON response from {HttpClient.redact_url(response.url)}: {type(e).__name__}: {e}"
            ) from e
        return payload

    @staticmethod
    def _payload_error(payload: Any) -> dict[str, Any] | None:
        if not isinstance(payload, dict):
            return None
        if isinstance(payload.get("error"), dict):
            return payload["error"]
        if "error" in payload or "error_type" in payload or "error_message" in payload:
            return payload
        return None

    def _raise_payload_error(self, *, method: str, url: str, payload: Any) -> None:
        api_error = self._payload_error(payload)
        if api_error is None:
            return
        safe_url = HttpClient.redact_url(url)
        safe_payload = HttpClient.redact_text(str(api_error))
        raise ToolError(f"Instagram API error for {method} {safe_url}: {safe_payload}")

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json_body: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
        use_version: bool = True,
        with_access_token: bool = True,
    ) -> Any:
        final_params: dict[str, Any] = dict(params or {})
        if with_access_token:
            final_params["access_token"] = self._resolve_access_token()
        url = self._graph_url(path, use_version=use_version)
        try:
            resp = self._http.request(
                method,
                url,
                params=final_params or None,
                json_body=json_body,
                data=data,
            )
        except RuntimeError as e:
            raise ToolError(HttpClient.redact_text(str(e))) from e
        payload = self._parse_json_response(resp)
        self._raise_payload_error(method=method, url=url, payload=payload)
        return payload

    def _auth_request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
    ) -> Any:
        url = self._auth_api_url(path)
        try:
            resp = self._http.request(method, url, params=params, data=data)
        except RuntimeError as e:
            raise ToolError(HttpClient.redact_text(str(e))) from e
        payload = self._parse_json_response(resp)
        self._raise_payload_error(method=method, url=url, payload=payload)
        return payload

    def build_login_url(
        self,
        *,
        state: str | None = None,
        scope: str | None = None,
        response_type: str = "code",
        force_reauth: bool | None = None,
    ) -> str:
        app_id = self._need_str("INSTAGRAM_APP_ID", self.cfg.app_id)
        redirect_uri = self._need_str("INSTAGRAM_REDIRECT_URI", self.cfg.redirect_uri)
        q = {
            "client_id": app_id,
            "redirect_uri": redirect_uri,
            "response_type": response_type,
        }
        if scope:
            q["scope"] = scope
        if state:
            q["state"] = state
        if force_reauth is True:
            q["auth_type"] = "rerequest"

        # Use the documented OAuth authorize endpoint for Instagram Login.
        return f"{self._auth_web_url('oauth/authorize')}?{urlencode(q)}"

    def get_me(self, fields: str | None = None) -> Any:
        params: dict[str, Any] = {}
        if fields:
            params["fields"] = fields
        return self._request("GET", "/me", params=params)

    def exchange_auth_code(self, *, code: str) -> Any:
        app_id = self._need_str("INSTAGRAM_APP_ID", self.cfg.app_id)
        app_secret = self._need_str("INSTAGRAM_APP_SECRET", self.cfg.app_secret)
        redirect_uri = self._need_str("INSTAGRAM_REDIRECT_URI", self.cfg.redirect_uri)
        payload = self._auth_request(
            "POST",
            "/oauth/access_token",
            data={
                "client_id": app_id,
                "client_secret": app_secret,
                "grant_type": "authorization_code",
                "redirect_uri": redirect_uri,
                "code": code,
            },
        )
        if not isinstance(payload, dict):
            raise ToolError("Unexpected auth exchange response shape; expected JSON object")
        return payload

    def exchange_short_lived_to_long(self, *, short_lived_token: str | None = None) -> Any:
        app_secret = self._need_str("INSTAGRAM_APP_SECRET", self.cfg.app_secret)
        token = (short_lived_token or "").strip() or self._resolve_access_token()
        payload = self._request(
            "GET",
            "/access_token",
            params={"grant_type": "ig_exchange_token", "client_secret": app_secret, "access_token": token},
            with_access_token=False,
            use_version=False,
        )
        if not isinstance(payload, dict):
            raise ToolError("Unexpected long-lived exchange response shape; expected JSON object")
        return payload

    def refresh_long_lived_token(self, *, access_token: str | None = None) -> Any:
        token = (access_token or "").strip() or self._resolve_access_token()
        payload = self._request(
            "GET",
            "/refresh_access_token",
            params={"grant_type": "ig_refresh_token", "access_token": token},
            with_access_token=False,
            use_version=False,
        )
        if not isinstance(payload, dict):
            raise ToolError("Unexpected token refresh response shape; expected JSON object")
        return payload

    def get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        return self._request("GET", path, params=params)

    def post(self, path: str, params: dict[str, Any] | None = None, *, json_body: dict[str, Any] | None = None, data: dict[str, Any] | None = None) -> Any:
        return self._request("POST", path, params=params, json_body=json_body, data=data)

    def delete(self, path: str, params: dict[str, Any] | None = None) -> Any:
        return self._request("DELETE", path, params=params)
