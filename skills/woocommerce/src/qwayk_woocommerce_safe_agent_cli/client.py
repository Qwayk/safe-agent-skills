from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .config import Config, endpoint_url
from .errors import ValidationError
from .http import HttpClient, HttpResponse


@dataclass(frozen=True)
class ResponseEnvelope:
    response: HttpResponse
    payload: Any


class WooCommerceClient:
    def __init__(
        self,
        *,
        cfg: Config,
        timeout_s: float,
        verbose: bool,
        user_agent: str,
    ):
        self._cfg = cfg
        self._http = HttpClient(
            timeout_s=timeout_s,
            verbose=verbose,
            user_agent=user_agent,
            verify_ssl=cfg.verify_ssl,
            secrets=(cfg.consumer_key, cfg.consumer_secret),
        )

    def _auth_args(self, *, auth_required: bool, params: dict[str, Any]) -> tuple[tuple[str, str] | None, dict[str, Any]]:
        query_params = dict(params or {})
        if not auth_required:
            return None, query_params
        if not self._cfg.has_credentials:
            raise ValidationError("Missing WOOCOMMERCE_CONSUMER_KEY or WOOCOMMERCE_CONSUMER_SECRET")
        assert self._cfg.consumer_key is not None
        assert self._cfg.consumer_secret is not None
        if self._cfg.query_string_auth:
            query_params.setdefault("consumer_key", self._cfg.consumer_key)
            query_params.setdefault("consumer_secret", self._cfg.consumer_secret)
            return None, query_params
        return (self._cfg.consumer_key, self._cfg.consumer_secret), query_params

    def request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json_body: dict[str, Any] | list[Any] | None = None,
        auth_required: bool,
    ) -> HttpResponse:
        auth, query_params = self._auth_args(auth_required=auth_required, params=params or {})
        return self._http.request(
            method=method,
            url=endpoint_url(self._cfg, path),
            params=query_params,
            json_body=json_body,
            auth=auth,
        )

    def request_json(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json_body: dict[str, Any] | list[Any] | None = None,
        auth_required: bool,
    ) -> ResponseEnvelope:
        response = self.request(
            method,
            path,
            params=params,
            json_body=json_body,
            auth_required=auth_required,
        )
        text = response.text().strip()
        if not text:
            payload: Any = None
        else:
            try:
                payload = response.json()
            except Exception as exc:  # noqa: BLE001
                preview = text[:200]
                raise RuntimeError(
                    f"Expected JSON response for {method} {path} but got invalid JSON: {type(exc).__name__}: {preview}"
                ) from exc
        return ResponseEnvelope(response=response, payload=payload)
