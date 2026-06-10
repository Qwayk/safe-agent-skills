from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .errors import ValidationError
from .http import HttpClient

REDACTED = "***REDACTED***"


def _redact_header(key: str) -> bool:
    return str(key).strip().lower() == "authorization"


def build_headers(token: str | None, request_from: str | None) -> dict[str, str]:
    headers: dict[str, str] = {}
    if token:
        headers["Authorization"] = f"Token token={token}"
    if request_from:
        headers["Request-From"] = request_from
    return headers


def redact_headers(headers: dict[str, str] | None) -> dict[str, str]:
    out: dict[str, str] = {}
    if not headers:
        return out
    for key, value in headers.items():
        if _redact_header(key):
            out[str(key)] = REDACTED
        else:
            out[str(key)] = str(value)
    return out


def parse_payload_json(raw: str | None) -> dict[str, Any] | list[Any]:
    if raw is None:
        raise ValidationError("Missing --payload-json")
    raw = str(raw).strip()
    if not raw:
        raise ValidationError("Missing --payload-json")
    try:
        payload = json.loads(raw)
    except Exception as e:  # noqa: BLE001
        raise ValidationError("Invalid --payload-json") from e
    if not isinstance(payload, (dict, list)):
        raise ValidationError("--payload-json must be a JSON object or array")
    return payload


def build_request_metadata(
    method: str,
    url: str,
    headers: dict[str, str],
    payload: Any | None = None,
    params: dict[str, Any] | None = None,
    form_fields: dict[str, Any] | None = None,
    media_file: str | None = None,
) -> dict[str, Any]:
    payload_json = payload if payload is not None else None
    request_meta: dict[str, Any] = {
        "method": str(method).upper(),
        "url": url,
        "headers": redact_headers(headers),
    }
    if params is not None:
        request_meta["params"] = params
    if form_fields is not None:
        request_meta["form"] = form_fields
    if media_file:
        request_meta["media_file"] = {"filename": Path(media_file).name}
    if payload_json is not None:
        request_meta["json"] = payload_json
    return request_meta


def build_response_metadata(response: Any) -> dict[str, Any]:
    try:
        body = response.json()
    except Exception:
        body = {"text": response.text()}
    return {
        "status": response.status,
        "url": response.url,
        "headers": response.headers,
        "body": body,
    }


def execute_call(
    cfg: Any,
    *,
    method: str,
    url: str,
    timeout_s: float,
    verbose: bool,
    user_agent: str,
    payload: Any | None = None,
    params: dict[str, Any] | None = None,
    form_fields: dict[str, Any] | None = None,
    media_file: str | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    headers = build_headers(getattr(cfg, "token", None), getattr(cfg, "request_from", None))
    request_meta = build_request_metadata(
        method=method,
        url=url,
        headers=headers,
        payload=payload,
        params=params,
        form_fields=form_fields,
        media_file=media_file,
    )
    client = HttpClient(timeout_s=timeout_s, verbose=bool(verbose), user_agent=user_agent)

    if media_file:
        with open(media_file, "rb") as media_handle:
            files = {
                "media_file": (Path(media_file).name, media_handle),
            }
            response = client.request(
                method,
                url,
                headers=headers,
                params=params,
                data=form_fields,
                files=files,
            )
    else:
        response = client.request(
            method,
            url,
            headers=headers,
            params=params,
            json_body=payload,
        )

    response_meta = build_response_metadata(response)
    return request_meta, response_meta
