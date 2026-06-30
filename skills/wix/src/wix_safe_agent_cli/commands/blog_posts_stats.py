from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ..authz import resolve_auth_mode
from ..errors import ValidationError
from ..http import HttpClient


COMMAND_FAMILY = "blog-posts-stats"


def _coerce_text(raw: Any, *, field: str) -> str:
    if raw is None:
        raise ValidationError(f"Missing --{field}")
    if not isinstance(raw, str):
        raise ValidationError(f"--{field} must be a string")
    value = raw.strip()
    if not value:
        raise ValidationError(f"--{field} cannot be empty")
    return value


def _read_json_arg(raw: Any, *, field: str, allow_empty: bool = False) -> dict[str, Any]:
    value = _coerce_text(raw, field=field)
    if value.startswith("@"):
        path = Path(value[1:])
        if not path.exists():
            raise ValidationError(f"--{field} file not found: {path}")
        value = path.read_text(encoding="utf-8").strip()
    try:
        payload = json.loads(value)
    except json.JSONDecodeError as exc:
        raise ValidationError(f"Invalid JSON for --{field}: {exc.msg}") from exc
    if not isinstance(payload, dict):
        raise ValidationError(f"--{field} must be a JSON object")
    if not allow_empty and not payload:
        raise ValidationError(f"--{field} cannot be empty")
    return payload


def _resolve_auth(ctx: dict[str, Any]) -> dict[str, Any]:
    return resolve_auth_mode(
        cfg=ctx["cfg"],
        env_file=str(ctx["env_file"]),
        verbose=bool(ctx.get("verbose")),
        command_family=COMMAND_FAMILY,
    )


def _request_json(
    *,
    method: str,
    path: str,
    headers: dict[str, str],
    params: dict[str, Any] | None,
    json_body: dict[str, Any] | None,
    ctx: dict[str, Any],
) -> dict[str, Any]:
    request_headers = dict(headers)
    if method.upper() != "GET":
        request_headers["Content-Type"] = "application/json"
    client = HttpClient(timeout_s=float(ctx["cfg"].timeout_s), verbose=bool(ctx.get("verbose")), user_agent="wix-safe-agent-cli")
    response = client.request(
        method=method,
        url=ctx["cfg"].base_url.rstrip("/") + "/" + path.lstrip("/"),
        headers=request_headers,
        params=params,
        json_body=json_body,
    )
    payload = response.json()
    if not isinstance(payload, dict):
        raise ValidationError("Wix API returned a non-object JSON response")
    return payload


def _emit_error(ctx: dict[str, Any], *, method: str, exc: Exception) -> int:
    if isinstance(exc, ValidationError):
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": method})
        return 1
    ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": method})
    return 1


def _run_read(
    *,
    method_name: str,
    http_method: str,
    path: str,
    params: dict[str, Any] | None,
    body: dict[str, Any] | None,
    ctx: dict[str, Any],
) -> int:
    auth = _resolve_auth(ctx)
    response = _request_json(method=http_method, path=path, headers=auth["headers"], params=params, json_body=body, ctx=ctx)
    request: dict[str, Any] = {"method": http_method, "path": path}
    if params is not None:
        request["params"] = params
    if body is not None:
        request["body"] = body
    out = {"ok": True, "method": method_name, "auth_mode": auth["mode"], "request": request, "response": response}
    ctx["audit"].write(method_name, out)
    ctx["out"].emit(out)
    return 0


def cmd_blog_posts_stats_get(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.get"
    try:
        post_id = _coerce_text(getattr(args, "post_id", None), field="post-id")
        params = _read_json_arg(getattr(args, "params_json", "{}"), field="params-json", allow_empty=True)
        return _run_read(method_name=method, http_method="GET", path=f"/v3/posts/{post_id}", params=params, body=None, ctx=ctx)
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_blog_posts_stats_query(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.query"
    try:
        body = _read_json_arg(getattr(args, "query_json", "{}"), field="query-json", allow_empty=True)
        return _run_read(method_name=method, http_method="POST", path="/v3/posts/query", params=None, body=body, ctx=ctx)
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_blog_posts_stats_list(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.list"
    try:
        params = _read_json_arg(getattr(args, "params_json", "{}"), field="params-json", allow_empty=True)
        return _run_read(method_name=method, http_method="GET", path="/v3/posts", params=params, body=None, ctx=ctx)
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_blog_posts_stats_get_by_slug(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.get-by-slug"
    try:
        slug = _coerce_text(getattr(args, "slug", None), field="slug")
        params = _read_json_arg(getattr(args, "params_json", "{}"), field="params-json", allow_empty=True)
        return _run_read(method_name=method, http_method="GET", path=f"/v3/posts/slugs/{slug}", params=params, body=None, ctx=ctx)
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_blog_posts_stats_get_metrics(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.get-metrics"
    try:
        post_id = _coerce_text(getattr(args, "post_id", None), field="post-id")
        params = _read_json_arg(getattr(args, "params_json", "{}"), field="params-json", allow_empty=True)
        return _run_read(method_name=method, http_method="GET", path=f"/v3/posts/{post_id}/metrics", params=params, body=None, ctx=ctx)
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_blog_posts_stats_get_total(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.get-total"
    try:
        params = _read_json_arg(getattr(args, "params_json", "{}"), field="params-json", allow_empty=True)
        return _run_read(method_name=method, http_method="GET", path="/blog/v2/stats/posts/total", params=params, body=None, ctx=ctx)
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_blog_posts_stats_query_count(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.query-count"
    try:
        params = _read_json_arg(getattr(args, "params_json", "{}"), field="params-json", allow_empty=True)
        return _run_read(method_name=method, http_method="GET", path="/blog/v2/stats/post/count", params=params, body=None, ctx=ctx)
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)
