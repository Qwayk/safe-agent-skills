from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from typing import Any
from urllib.parse import urljoin

import requests

from .errors import ToolError
from .google_auth import ensure_fresh


@dataclass(frozen=True)
class HttpResponse:
    status: int
    headers: dict[str, str]
    json: Any | None
    text: str | None


class GscHttpClient:
    def __init__(
        self,
        *,
        base_url: str,
        timeout_s: float,
        verbose: bool,
        creds: Any,
    ) -> None:
        self._base_url = base_url.rstrip("/") + "/"
        self._timeout_s = float(timeout_s)
        self._verbose = bool(verbose)
        self._creds = creds

    def _auth_headers(self) -> dict[str, str]:
        ensure_fresh(self._creds)
        token = getattr(self._creds, "token", None)
        if not token:
            raise ToolError("Missing access token (credentials not refreshed)")
        return {"Authorization": f"Bearer {token}"}

    def request_json(
        self,
        *,
        http_method: str,
        path: str,
        query: dict[str, Any] | None,
        body: Any | None,
    ) -> HttpResponse:
        url = urljoin(self._base_url, path.lstrip("/"))
        headers = {"Accept": "application/json", **self._auth_headers()}

        if self._verbose:
            print(f"[gsc] {http_method} {url}", file=sys.stderr)

        try:
            resp = requests.request(
                http_method,
                url,
                params=query or None,
                json=body if body is not None else None,
                headers=headers,
                timeout=self._timeout_s,
            )
        except Exception as e:  # noqa: BLE001
            raise ToolError(f"HTTP request failed: {type(e).__name__}: {e}") from None

        if self._verbose:
            print(f"[gsc] -> {resp.status_code}", file=sys.stderr)

        parsed_json = None
        text = None
        if resp.content:
            ct = (resp.headers.get("Content-Type") or "").lower()
            if "application/json" in ct or ct.endswith("+json"):
                try:
                    parsed_json = resp.json()
                except Exception:
                    parsed_json = None
                    text = resp.text
            else:
                text = resp.text

        if resp.status_code >= 400:
            msg = None
            if isinstance(parsed_json, dict):
                err = parsed_json.get("error")
                if isinstance(err, dict) and isinstance(err.get("message"), str):
                    msg = err.get("message")
            msg = msg or (text.strip() if isinstance(text, str) and text.strip() else None)
            raise ToolError(f"HTTP {resp.status_code}: {msg or 'Request failed'}")

        return HttpResponse(
            status=int(resp.status_code),
            headers={str(k): str(v) for k, v in resp.headers.items()},
            json=parsed_json,
            text=text,
        )


def redact_http_response_for_receipt(resp: HttpResponse) -> dict[str, Any]:
    out: dict[str, Any] = {"status": resp.status}
    # Responses should not contain secrets, but keep receipts small and deterministic.
    if isinstance(resp.json, (dict, list)):
        try:
            out["json"] = json.loads(json.dumps(resp.json))
        except Exception:
            out["json"] = None
    return out

