from __future__ import annotations

from typing import Any

from ..authz import resolve_auth_mode
from ..errors import ValidationError
from ..http import HttpClient


COMMAND_FAMILY = "headless-sitemap"
LIST_SITEMAP_PAGES_PATH = "/v1/list-sitemap-pages"

ITEM_TYPES = {
    "BLOG_ARCHIVE",
    "BLOG_CATEGORY",
    "BLOG_POST",
    "BLOG_TAGS",
    "BOOKINGS_SERVICE",
    "CHALLENGES_PAGE",
    "EVENTS_PAGE",
    "FORUM_CATEGORY",
    "FORUM_POST",
    "GROUPS_PAGE",
    "GROUPS_POST",
    "MEMBERS_AREA_PROFILE",
    "PORTFOLIO_COLLECTIONS",
    "PORTFOLIO_PROJECTS",
    "PRICING_PLANS",
    "RESTAURANTS_MENU_PAGE",
    "STORES_CATEGORY",
    "STORES_PRODUCT",
    "STORES_SUB_CATEGORY",
}


def _coerce_optional_text(raw: Any, *, field: str) -> str | None:
    if raw is None:
        return None
    if not isinstance(raw, str):
        raise ValidationError(f"--{field} must be a string")
    value = raw.strip()
    if not value:
        raise ValidationError(f"--{field} cannot be empty")
    return value


def _coerce_item_type(raw: Any) -> str | None:
    value = _coerce_optional_text(raw, field="item-type")
    if value is None:
        return None
    normalized = value.upper()
    if normalized not in ITEM_TYPES:
        expected = ", ".join(sorted(ITEM_TYPES))
        raise ValidationError(f"--item-type must be one of: {expected}")
    return normalized


def _coerce_limit(raw: Any) -> int | None:
    if raw is None:
        return None
    if isinstance(raw, bool):
        raise ValidationError("--limit must be an integer")
    if isinstance(raw, int):
        value = raw
    elif isinstance(raw, str):
        text = raw.strip()
        if not text:
            raise ValidationError("--limit must be an integer")
        try:
            value = int(text)
        except ValueError as exc:
            raise ValidationError("--limit must be an integer") from exc
    else:
        raise ValidationError("--limit must be an integer")
    if value < 0 or value > 200:
        raise ValidationError("--limit must be between 0 and 200")
    return value


def _coerce_cursor(raw: Any) -> str | None:
    value = _coerce_optional_text(raw, field="cursor")
    if value is None:
        return None
    if len(value) > 16000:
        raise ValidationError("--cursor must be 16000 characters or fewer")
    return value


def _resolve_auth(ctx: dict[str, Any]) -> dict[str, Any]:
    return resolve_auth_mode(
        cfg=ctx["cfg"],
        env_file=str(ctx["env_file"]),
        verbose=bool(ctx.get("verbose")),
        command_family=COMMAND_FAMILY,
    )


def _request_json(*, path: str, headers: dict[str, str], params: dict[str, Any], ctx: dict[str, Any]) -> dict[str, Any]:
    client = HttpClient(
        timeout_s=float(ctx["cfg"].timeout_s),
        verbose=bool(ctx.get("verbose")),
        user_agent="wix-safe-agent-cli",
    )
    response = client.request(
        method="GET",
        url=ctx["cfg"].base_url.rstrip("/") + "/" + path.lstrip("/"),
        headers=dict(headers),
        params=params or None,
        json_body=None,
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


def _build_params(*, item_type: str | None, limit: int | None, cursor: str | None) -> dict[str, Any]:
    params: dict[str, Any] = {}
    if item_type is not None:
        params["itemType"] = item_type
    if limit is not None:
        params["paging.limit"] = limit
    if cursor is not None:
        params["paging.cursor"] = cursor
    return params


def cmd_headless_sitemap_list_pages(args, ctx) -> int:
    method = "headlessSitemap.listSitemapPages"
    try:
        params = _build_params(
            item_type=_coerce_item_type(getattr(args, "item_type", None)),
            limit=_coerce_limit(getattr(args, "limit", None)),
            cursor=_coerce_cursor(getattr(args, "cursor", None)),
        )
        auth = _resolve_auth(ctx)
        response = _request_json(path=LIST_SITEMAP_PAGES_PATH, headers=auth["headers"], params=params, ctx=ctx)
        request: dict[str, Any] = {"method": "GET", "path": LIST_SITEMAP_PAGES_PATH}
        if params:
            request["params"] = params
        out = {"ok": True, "method": method, "auth_mode": auth["mode"], "request": request, "response": response}
        ctx["audit"].write(method, out)
        ctx["out"].emit(out)
        return 0
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)
