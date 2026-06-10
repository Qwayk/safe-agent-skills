from __future__ import annotations

from typing import Any
from urllib.parse import urlencode

from . import __version__
from .config import Config
from .errors import ToolError, ValidationError
from .http import HttpClient
from .oauth_tokens import read_access_token, token_path_for_env_file


class ThreadsAPIClient:
    def __init__(
        self,
        cfg: Config,
        *,
        env_file: str,
        timeout_s: float,
        verbose: bool,
        token: str | None = None,
    ) -> None:
        self._cfg = cfg
        self._env_file = env_file
        self._token_override = token
        self._app_access_token: str | None = None
        self._http = HttpClient(
            timeout_s=timeout_s,
            verbose=verbose,
            user_agent=f"threads-api-tool/{__version__}",
        )

    @staticmethod
    def _need_str(name: str, value: str | None) -> str:
        if value is None or not str(value).strip():
            raise ValidationError(f"Missing required Threads setting: {name}")
        return str(value).strip()

    @staticmethod
    def _api_bool(value: bool) -> str:
        return "true" if bool(value) else "false"

    def _resolve_app_access_token(self) -> str:
        if self._app_access_token:
            return self._app_access_token
        app_id = self._need_str("THREADS_APP_ID", self._cfg.app_id)
        app_secret = self._need_str("THREADS_APP_SECRET", self._cfg.app_secret)
        payload = self._request(
            "GET",
            "/oauth/access_token",
            params={
                "client_id": app_id,
                "client_secret": app_secret,
                "grant_type": "client_credentials",
            },
            with_access_token=False,
            use_version=False,
        )
        if not isinstance(payload, dict):
            raise ToolError("Unexpected app token response shape; expected JSON object")
        token = str(payload.get("access_token", "") or "").strip()
        if not token:
            raise ToolError("App token response missing access_token")
        self._app_access_token = token
        return token

    def _graph_base(self, *, use_version: bool = True) -> str:
        base = self._cfg.base_url.rstrip("/")
        if not use_version:
            return base
        return f"{base}/{self._cfg.api_version}"

    def _graph_url(self, path: str, *, use_version: bool = True) -> str:
        return f"{self._graph_base(use_version=use_version)}/{str(path).lstrip('/')}"

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json_body: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
        with_access_token: bool = True,
        use_version: bool = True,
    ) -> Any:
        final_params = dict(params or {})
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

    def _parse_json_response(self, resp) -> Any:
        try:
            return resp.json()
        except Exception as e:  # noqa: BLE001
            raise ToolError(
                f"Non-JSON response from {HttpClient.redact_url(resp.url)}: {type(e).__name__}: {e}"
            ) from e

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
        raise ToolError(f"Threads API error for {method} {HttpClient.redact_url(url)}: {HttpClient.redact_text(str(api_error))}")

    def _resolve_access_token(self) -> str:
        if self._token_override:
            return self._token_override.strip()
        if self._cfg.token:
            return self._cfg.token
        token = read_access_token(token_path_for_env_file(self._env_file))
        if token:
            return token
        raise ValidationError("Missing access token. Run auth code exchange or set THREADS_API_TOKEN.")

    # OAuth helpers
    def build_authorize_url(
        self,
        *,
        state: str | None = None,
        scope: str | None = None,
        response_type: str = "code",
    ) -> str:
        app_id = self._need_str("THREADS_APP_ID", self._cfg.app_id)
        redirect_uri = self._need_str("THREADS_REDIRECT_URI", self._cfg.redirect_uri)
        q = {
            "client_id": app_id,
            "redirect_uri": redirect_uri,
            "response_type": response_type,
        }
        if state:
            q["state"] = state
        if scope:
            q["scope"] = scope
        return f"https://threads.net/oauth/authorize?{urlencode(q)}"

    def exchange_auth_code(self, *, code: str) -> Any:
        app_id = self._need_str("THREADS_APP_ID", self._cfg.app_id)
        app_secret = self._need_str("THREADS_APP_SECRET", self._cfg.app_secret)
        redirect_uri = self._need_str("THREADS_REDIRECT_URI", self._cfg.redirect_uri)
        payload = {
            "client_id": app_id,
            "client_secret": app_secret,
            "grant_type": "authorization_code",
            "redirect_uri": redirect_uri,
            "code": code,
        }
        result = self._request(
            "POST",
            "/oauth/access_token",
            data=payload,
            with_access_token=False,
            use_version=False,
        )
        if not isinstance(result, dict):
            raise ToolError("Unexpected auth exchange response shape; expected JSON object")
        return result

    def exchange_short_lived_token(self, *, short_token: str | None = None) -> Any:
        app_secret = self._need_str("THREADS_APP_SECRET", self._cfg.app_secret)
        token = (short_token or "").strip() or self._resolve_access_token()
        result = self._request(
            "GET",
            "/access_token",
            params={
                "grant_type": "th_exchange_token",
                "client_secret": app_secret,
                "access_token": token,
            },
            with_access_token=False,
            use_version=False,
        )
        if not isinstance(result, dict):
            raise ToolError("Unexpected token exchange response shape; expected JSON object")
        return result

    def refresh_long_lived_token(self, *, long_token: str | None = None) -> Any:
        token = (long_token or "").strip() or self._resolve_access_token()
        result = self._request(
            "GET",
            "/refresh_access_token",
            params={
                "grant_type": "th_refresh_token",
                "access_token": token,
            },
            with_access_token=False,
            use_version=False,
        )
        if not isinstance(result, dict):
            raise ToolError("Unexpected token refresh response shape; expected JSON object")
        return result

    def generate_app_access_token(self) -> Any:
        app_id = self._need_str("THREADS_APP_ID", self._cfg.app_id)
        app_secret = self._need_str("THREADS_APP_SECRET", self._cfg.app_secret)
        result = self._request(
            "GET",
            "/oauth/access_token",
            params={
                "client_id": app_id,
                "client_secret": app_secret,
                "grant_type": "client_credentials",
            },
            with_access_token=False,
            use_version=False,
        )
        if not isinstance(result, dict):
            raise ToolError("Unexpected app token response shape; expected JSON object")
        return result

    def debug_token(self, *, input_token: str | None = None) -> Any:
        input_token_val = (input_token or "").strip() or self._resolve_access_token()
        if not input_token_val:
            raise ValidationError("No token available for debug-token")
        result = self._request(
            "GET",
            "/debug_token",
            params={
                "input_token": input_token_val,
                "access_token": self._resolve_access_token(),
            },
            with_access_token=False,
            use_version=False,
        )
        if not isinstance(result, dict):
            raise ToolError("Unexpected token debug response shape; expected JSON object")
        return result

    # Profile
    def get_me(self, *, fields: str | None = None) -> Any:
        params: dict[str, Any] = {}
        if fields:
            params["fields"] = fields
        return self._request("GET", "/me", params=params or None)

    def get_profile(self, *, threads_user_id: str, fields: str | None = None) -> Any:
        params: dict[str, Any] = {}
        if fields:
            params["fields"] = fields
        return self._request("GET", f"/{threads_user_id}", params=params or None)

    def lookup_profile(self, *, username: str, fields: str | None = None) -> Any:
        params: dict[str, Any] = {"username": username}
        if fields:
            params["fields"] = fields
        return self._request("GET", "/profile_lookup", params=params)

    # Posts
    def list_owned_posts(self, *, threads_user_id: str, params: dict[str, Any] | None = None) -> Any:
        return self._request("GET", f"/{threads_user_id}/threads", params=params)

    def list_public_posts(self, *, username: str, params: dict[str, Any] | None = None) -> Any:
        return self._request("GET", "/profile_posts", params={"username": username, **(params or {})})

    def get_post(self, *, threads_media_id: str, params: dict[str, Any] | None = None) -> Any:
        return self._request("GET", f"/{threads_media_id}", params=params)

    def posting_limits(self, *, threads_user_id: str) -> Any:
        return self._request("GET", f"/{threads_user_id}/threads_publishing_limit")

    def create_post(self, *, threads_user_id: str, payload: dict[str, Any]) -> Any:
        return self._request("POST", f"/{threads_user_id}/threads", data=payload)

    def publish_post(self, *, threads_user_id: str, creation_id: str) -> Any:
        return self._request("POST", f"/{threads_user_id}/threads_publish", data={"creation_id": creation_id})

    def post_status(self, *, threads_container_id: str, fields: str | None = None) -> Any:
        params: dict[str, Any] = {"fields": fields} if fields else None
        if params is None:
            params = {}
        if "status" not in params:
            params["fields"] = "id,status"
        return self._request("GET", f"/{threads_container_id}", params=params)

    def repost_media(self, *, threads_media_id: str) -> Any:
        return self._request("POST", f"/{threads_media_id}/repost")

    def delete_media(self, *, threads_media_id: str) -> Any:
        return self._request("DELETE", f"/{threads_media_id}")

    # Replies
    def list_replies(self, *, threads_media_id: str, params: dict[str, Any] | None = None) -> Any:
        return self._request("GET", f"/{threads_media_id}/replies", params=params)

    def reply_conversation(self, *, threads_media_id: str, params: dict[str, Any] | None = None) -> Any:
        return self._request("GET", f"/{threads_media_id}/conversation", params=params)

    def manage_reply(self, *, threads_reply_id: str, hide: bool) -> Any:
        return self._request(
            "POST",
            f"/{threads_reply_id}/manage_reply",
            params={"hide": self._api_bool(hide)},
        )

    def list_pending_replies(self, *, threads_media_id: str, params: dict[str, Any] | None = None) -> Any:
        return self._request("GET", f"/{threads_media_id}/pending_replies", params=params)

    def manage_pending_reply(self, *, threads_reply_id: str, approve: bool) -> Any:
        return self._request(
            "POST",
            f"/{threads_reply_id}/manage_pending_reply",
            params={"approve": self._api_bool(approve)},
        )

    # Mentions
    def list_mentions(self, *, threads_user_id: str, params: dict[str, Any] | None = None) -> Any:
        return self._request("GET", f"/{threads_user_id}/mentions", params=params)

    # Insights
    def media_insights(self, *, threads_media_id: str, params: dict[str, Any] | None = None) -> Any:
        return self._request("GET", f"/{threads_media_id}/insights", params=params)

    def user_insights(self, *, threads_user_id: str, params: dict[str, Any] | None = None) -> Any:
        return self._request("GET", f"/{threads_user_id}/threads_insights", params=params)

    # Search
    def search_keyword(self, *, query: str, params: dict[str, Any] | None = None) -> Any:
        merged = dict(params or {})
        merged["q"] = query
        return self._request("GET", "/keyword_search", params=merged)

    def search_topic_tag(self, *, topic_tag: str, params: dict[str, Any] | None = None) -> Any:
        merged = dict(params or {})
        merged["q"] = topic_tag
        return self._request("GET", "/keyword_search", params=merged)

    def recently_searched_keywords(self) -> Any:
        return self._request("GET", "/me", params={"fields": "recently_searched_keywords"})

    # Locations
    def search_locations_query(self, *, q: str, params: dict[str, Any] | None = None) -> Any:
        merged = dict(params or {})
        merged["q"] = q
        return self._request("GET", "/location_search", params=merged)

    def search_locations_coordinates(
        self,
        *,
        latitude: float,
        longitude: float,
        radius_km: float | None = None,
        params: dict[str, Any] | None = None,
    ) -> Any:
        merged = dict(params or {})
        merged.update({"latitude": latitude, "longitude": longitude})
        if radius_km is not None:
            merged["radius_km"] = radius_km
        return self._request("GET", "/location_search", params=merged)

    def get_location(self, *, location_id: str, fields: str | None = None) -> Any:
        params: dict[str, Any] = {}
        if fields:
            params["fields"] = fields
        return self._request("GET", f"/{location_id}", params=params or None)

    # oEmbed
    def oembed(self, *, url: str, params: dict[str, Any] | None = None) -> Any:
        merged = dict(params or {})
        merged["url"] = url
        merged["access_token"] = self._resolve_app_access_token()
        return self._request("GET", "/oembed", params=merged, with_access_token=False)
