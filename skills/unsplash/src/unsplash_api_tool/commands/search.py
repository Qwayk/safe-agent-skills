from __future__ import annotations

from typing import Any

from ..errors import ValidationError
from ..pagination import validate_page, validate_per_page
from ..unsplash_client import UnsplashClient


def cmd_search_photos(args: Any, ctx: dict[str, Any]) -> int:
    query = str(getattr(args, "query", "") or "").strip()
    if not query:
        raise ValidationError("Missing --query")
    page = validate_page(getattr(args, "page", None), field="--page")
    per_page = validate_per_page(getattr(args, "per_page", None), field="--per-page")

    client: UnsplashClient = ctx["client"]
    data = client.get("/search/photos", params={"query": query, "page": page, "per_page": per_page})
    out = {"ok": True, "endpoint": "GET /search/photos", "params": {"query": query, "page": page, "per_page": per_page}, "data": data}
    ctx["audit"].write("search.photos", {"query": query, "page": page, "per_page": per_page})
    ctx["out"].emit(out)
    return 0


def cmd_search_collections(args: Any, ctx: dict[str, Any]) -> int:
    query = str(getattr(args, "query", "") or "").strip()
    if not query:
        raise ValidationError("Missing --query")
    page = validate_page(getattr(args, "page", None), field="--page")
    per_page = validate_per_page(getattr(args, "per_page", None), field="--per-page")

    client: UnsplashClient = ctx["client"]
    data = client.get("/search/collections", params={"query": query, "page": page, "per_page": per_page})
    out = {
        "ok": True,
        "endpoint": "GET /search/collections",
        "params": {"query": query, "page": page, "per_page": per_page},
        "data": data,
    }
    ctx["audit"].write("search.collections", {"query": query, "page": page, "per_page": per_page})
    ctx["out"].emit(out)
    return 0


def cmd_search_users(args: Any, ctx: dict[str, Any]) -> int:
    query = str(getattr(args, "query", "") or "").strip()
    if not query:
        raise ValidationError("Missing --query")
    page = validate_page(getattr(args, "page", None), field="--page")
    per_page = validate_per_page(getattr(args, "per_page", None), field="--per-page")

    client: UnsplashClient = ctx["client"]
    data = client.get("/search/users", params={"query": query, "page": page, "per_page": per_page})
    out = {"ok": True, "endpoint": "GET /search/users", "params": {"query": query, "page": page, "per_page": per_page}, "data": data}
    ctx["audit"].write("search.users", {"query": query, "page": page, "per_page": per_page})
    ctx["out"].emit(out)
    return 0
