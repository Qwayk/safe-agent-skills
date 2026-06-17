from __future__ import annotations

import mimetypes
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from .auth_runtime import resolve_access_token
from .errors import ValidationError
from .http import HttpClient
from .write_safety import enforce_write_apply_contract


def _build_request_url(base_url: str, path: str) -> str:
    if path.startswith("https://") or path.startswith("http://"):
        return path
    if path.startswith("/api/"):
        parts = urlsplit(base_url)
        if not parts.scheme or not parts.netloc:
            raise ValidationError("FORTNOX_API_BASE_URL must be an absolute URL")
        return f"{parts.scheme}://{parts.netloc}{path}"
    return f"{base_url}{path}"


def request_data(
    *,
    ctx: dict[str, Any],
    method: str,
    path: str,
    json_body: dict[str, Any] | None = None,
    query_params: dict[str, Any] | None = None,
    files: dict[str, Any] | None = None,
    expect_json: bool = True,
    expect_json_object: bool = True,
) -> dict[str, Any]:
    enforce_write_apply_contract(ctx=ctx, method=method, path=path)
    cfg = ctx["cfg"]
    resolved = resolve_access_token(cfg=cfg, env_file=ctx["env_file"])
    if not resolved.token:
        raise ValidationError("No Fortnox access token is available. Run `fortnox-api-tool auth login` first.")
    if resolved.expired is True and resolved.source == "token_file":
        raise ValidationError("Stored Fortnox access token looks expired. Run `fortnox-api-tool auth refresh` first.")

    client = HttpClient(
        timeout_s=float(ctx["timeout_s"]),
        verbose=bool(ctx.get("verbose")),
        user_agent=f"{ctx['tool']}/{ctx['tool_version']}",
    )
    url = _build_request_url(cfg.base_url, path)
    headers = {
        "Authorization": f"Bearer {resolved.token}",
        "Accept": "application/json",
    }
    if json_body is not None and files is None:
        headers["Content-Type"] = "application/json"
    resp = client.request(method, url, headers=headers, params=query_params, json_body=json_body, files=files)
    payload: Any
    if resp.body:
        decoded = resp.json()
        if expect_json_object and not isinstance(decoded, dict):
            raise RuntimeError(f"Expected JSON object from {method} {path}")
        payload = decoded
    elif expect_json:
        expected_kind = "JSON object" if expect_json_object else "JSON value"
        raise RuntimeError(f"Expected {expected_kind} from {method} {path}")
    else:
        payload = None
    return {
        "status": resp.status,
        "url": resp.url,
        "token_source": resolved.source,
        "token_expired": resolved.expired,
        "body": payload,
    }


def request_raw(
    *,
    ctx: dict[str, Any],
    method: str,
    path: str,
    query_params: dict[str, Any] | None = None,
    accept: str = "application/octet-stream",
) -> dict[str, Any]:
    cfg = ctx["cfg"]
    resolved = resolve_access_token(cfg=cfg, env_file=ctx["env_file"])
    if not resolved.token:
        raise ValidationError("No Fortnox access token is available. Run `fortnox-api-tool auth login` first.")
    if resolved.expired is True and resolved.source == "token_file":
        raise ValidationError("Stored Fortnox access token looks expired. Run `fortnox-api-tool auth refresh` first.")

    client = HttpClient(
        timeout_s=float(ctx["timeout_s"]),
        verbose=bool(ctx.get("verbose")),
        user_agent=f"{ctx['tool']}/{ctx['tool_version']}",
    )
    url = _build_request_url(cfg.base_url, path)
    resp = client.request(
        method,
        url,
        headers={
            "Authorization": f"Bearer {resolved.token}",
            "Accept": accept,
        },
        params=query_params,
    )
    return {
        "status": resp.status,
        "url": resp.url,
        "token_source": resolved.source,
        "token_expired": resolved.expired,
        "content_type": resp.headers.get("content-type"),
        "body_bytes": resp.body,
    }


def request_json(
    *,
    ctx: dict[str, Any],
    method: str,
    path: str,
    json_body: dict[str, Any] | None = None,
    query_params: dict[str, Any] | None = None,
    expect_json: bool = True,
) -> dict[str, Any]:
    return request_data(
        ctx=ctx,
        method=method,
        path=path,
        json_body=json_body,
        query_params=query_params,
        expect_json=expect_json,
        expect_json_object=True,
    )


def request_multipart_file(
    *,
    ctx: dict[str, Any],
    method: str,
    path: str,
    file_path: str,
    query_params: dict[str, Any] | None = None,
    file_field: str = "file",
    expect_json: bool = True,
) -> dict[str, Any]:
    upload_path = Path(file_path)
    if not upload_path.exists():
        raise ValidationError(f"Upload file not found: {upload_path}")
    if not upload_path.is_file():
        raise ValidationError(f"Upload path must be a file: {upload_path}")
    content_type = mimetypes.guess_type(upload_path.name)[0] or "application/octet-stream"
    return request_data(
        ctx=ctx,
        method=method,
        path=path,
        query_params=query_params,
        files={file_field: (upload_path.name, upload_path.read_bytes(), content_type)},
        expect_json=expect_json,
        expect_json_object=True,
    )


def get_json(*, ctx: dict[str, Any], path: str) -> dict[str, Any]:
    return request_json(ctx=ctx, method="GET", path=path, expect_json=True)
