from __future__ import annotations

import dataclasses
from typing import Any

from .errors import SafetyError, ValidationError
from .http import HttpClient
from .redaction import redact_any


@dataclasses.dataclass(frozen=True)
class CloudCallResult:
    ok: bool
    status: int | None
    url: str | None
    response_json: Any | None
    response_text: str | None
    error: str | None


class QdrantCloudHttpClient:
    def __init__(self, *, base_url: str, api_key: str | None, timeout_s: float, verbose: bool, user_agent: str):
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key
        self._http = HttpClient(timeout_s=timeout_s, verbose=verbose, user_agent=user_agent)

    @property
    def base_url(self) -> str:
        return self._base_url

    def _auth_header(self) -> dict[str, str]:
        if not self._api_key:
            raise ValidationError("Missing QDRANT_CLOUD_API_KEY (required for --live requests)")
        # From official docs: Authorization: apikey <KEY>
        return {"Authorization": f"apikey {self._api_key}"}

    def request_json(
        self,
        *,
        live: bool,
        method: str,
        path: str,
        path_params: dict[str, str] | None = None,
        query_params: dict[str, Any] | None = None,
        json_body: dict[str, Any] | None = None,
    ) -> CloudCallResult:
        if not live:
            raise SafetyError("Refusing to make network requests without --live")
        if not path.startswith("/"):
            raise ValidationError("Internal error: path must start with '/'")

        url_path = path
        for k, v in (path_params or {}).items():
            url_path = url_path.replace("{" + k + "}", str(v))

        url = f"{self._base_url}{url_path}"
        try:
            resp = self._http.request(
                method=method,
                url=url,
                headers=self._auth_header(),
                params=query_params,
                json_body=json_body,
                retries=1,
            )
        except Exception as e:  # noqa: BLE001
            return CloudCallResult(
                ok=False,
                status=None,
                url=url,
                response_json=None,
                response_text=None,
                error=f"{type(e).__name__}: {e}",
            )

        response_json: Any | None = None
        response_text: str | None = None
        try:
            response_json = resp.json()
        except Exception:
            response_text = resp.text()

        ok = 200 <= int(resp.status) < 400
        return CloudCallResult(
            ok=ok,
            status=int(resp.status),
            url=str(resp.url),
            response_json=redact_any(response_json) if response_json is not None else None,
            response_text=response_text,
            error=None if ok else (response_text or "HTTP error"),
        )

