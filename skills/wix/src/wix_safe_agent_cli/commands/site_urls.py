from __future__ import annotations

from typing import Any

from ..authz import resolve_auth_mode
from ..errors import ValidationError
from ..http import HttpClient


def _coerce_field_path_args(raw: Any, field: str) -> list[str] | None:
    if raw is None:
        return None
    if not isinstance(raw, list):
        raise ValidationError(f"--{field} must be repeatable")

    seen: set[str] = set()
    field_paths: list[str] = []
    for i, item in enumerate(raw):
        if not isinstance(item, str):
            raise ValidationError(f"--{field}[{i}] must be a string")
        value = item.strip()
        if not value:
            raise ValidationError(f"--{field}[{i}] cannot be empty")
        if value in seen:
            continue
        seen.add(value)
        field_paths.append(value)
    return field_paths


def _resolve_site_urls_auth(*, ctx: dict[str, Any]) -> tuple[dict[str, str], str]:
    auth = resolve_auth_mode(
        cfg=ctx["cfg"],
        env_file=str(ctx["env_file"]),
        verbose=bool(ctx.get("verbose")),
        command_family="site-urls",
    )
    return auth["headers"], auth["mode"]


def _request_json(
    *,
    method: str,
    base_url: str,
    path: str,
    headers: dict[str, str],
    params: dict[str, Any] | None,
    json_body: dict[str, Any] | None,
    timeout_s: float,
    verbose: bool,
) -> dict[str, Any] | list[Any]:
    client = HttpClient(timeout_s=timeout_s, verbose=verbose, user_agent="wix-safe-agent-cli")
    response = client.request(
        method=method,
        url=base_url.rstrip("/") + "/" + path.lstrip("/"),
        headers=dict(headers),
        params=params,
        json_body=json_body,
    )
    payload = response.json()
    if not isinstance(payload, (dict, list)):
        raise ValidationError("Wix API returned a non-object-or-array JSON response")
    return payload


def cmd_site_urls_get_editor_urls(args, ctx) -> int:
    try:
        field_paths = _coerce_field_path_args(getattr(args, "field_path", None), field="field-path")

        auth_headers, auth_mode = _resolve_site_urls_auth(ctx=ctx)
        params = {"fields.paths": field_paths} if field_paths is not None else None
        payload = _request_json(
            method="GET",
            base_url=ctx["cfg"].base_url,
            path="/editor-urls/v2/editor-urls",
            headers=auth_headers,
            params=params,
            json_body=None,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )

        request = {"method": "GET", "path": "/editor-urls/v2/editor-urls"}
        if params is not None:
            request["params"] = params

        out = {
            "ok": True,
            "method": "site-urls.get-editor-urls",
            "auth_mode": auth_mode,
            "request": request,
            "response": payload,
        }
        ctx["out"].emit(out)
        return 0
    except ValidationError as exc:
        out = {"ok": False, "error": str(exc), "error_type": "ValidationError", "method": "site-urls.get-editor-urls"}
        ctx["out"].emit(out)
        return 1
    except RuntimeError as exc:
        out = {
            "ok": False,
            "error": str(exc),
            "error_type": exc.__class__.__name__,
            "method": "site-urls.get-editor-urls",
        }
        ctx["out"].emit(out)
        return 1


def cmd_site_urls_list_published_site_urls(args, ctx) -> int:
    try:
        _ = args
        auth_headers, auth_mode = _resolve_site_urls_auth(ctx=ctx)
        payload = _request_json(
            method="GET",
            base_url=ctx["cfg"].base_url,
            path="/urls-server/v2/published-site-urls",
            headers=auth_headers,
            params=None,
            json_body=None,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )

        out = {
            "ok": True,
            "method": "site-urls.list-published-site-urls",
            "auth_mode": auth_mode,
            "request": {"method": "GET", "path": "/urls-server/v2/published-site-urls"},
            "response": payload,
        }
        ctx["out"].emit(out)
        return 0
    except ValidationError as exc:
        out = {
            "ok": False,
            "error": str(exc),
            "error_type": "ValidationError",
            "method": "site-urls.list-published-site-urls",
        }
        ctx["out"].emit(out)
        return 1
    except RuntimeError as exc:
        out = {
            "ok": False,
            "error": str(exc),
            "error_type": exc.__class__.__name__,
            "method": "site-urls.list-published-site-urls",
        }
        ctx["out"].emit(out)
        return 1
