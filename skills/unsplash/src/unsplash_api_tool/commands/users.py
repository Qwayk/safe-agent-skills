from __future__ import annotations

from typing import Any

from ..errors import ValidationError
from ..pagination import validate_page, validate_per_page
from ..unsplash_client import UnsplashClient, validate_username


def cmd_users_get(args: Any, ctx: dict[str, Any]) -> int:
    username = validate_username(str(getattr(args, "username", "") or ""))
    client: UnsplashClient = ctx["client"]
    data = client.get(f"/users/{username}")
    out = {"ok": True, "endpoint": "GET /users/:username", "username": username, "data": data}
    ctx["audit"].write("users.get", {"username": username})
    ctx["out"].emit(out)
    return 0


def cmd_users_photos(args: Any, ctx: dict[str, Any]) -> int:
    username = validate_username(str(getattr(args, "username", "") or ""))
    page = validate_page(getattr(args, "page", None), field="--page")
    per_page = validate_per_page(getattr(args, "per_page", None), field="--per-page")
    order_by = str(getattr(args, "order_by", "") or "").strip() or None
    if order_by not in {None, "latest", "oldest", "popular", "views", "downloads"}:
        raise ValidationError("--order-by must be one of: latest, oldest, popular, views, downloads")
    orientation = str(getattr(args, "orientation", "") or "").strip() or None
    if orientation not in {None, "landscape", "portrait", "squarish"}:
        raise ValidationError("--orientation must be one of: landscape, portrait, squarish")

    client: UnsplashClient = ctx["client"]
    data = client.get(
        f"/users/{username}/photos",
        params={
            k: v
            for k, v in {"page": page, "per_page": per_page, "order_by": order_by, "orientation": orientation}.items()
            if v is not None
        },
    )
    out = {
        "ok": True,
        "endpoint": "GET /users/:username/photos",
        "username": username,
        "params": {"page": page, "per_page": per_page, "order_by": order_by, "orientation": orientation},
        "data": data,
    }
    ctx["audit"].write("users.photos", {"username": username, "page": page, "per_page": per_page})
    ctx["out"].emit(out)
    return 0


def cmd_users_likes(args: Any, ctx: dict[str, Any]) -> int:
    username = validate_username(str(getattr(args, "username", "") or ""))
    page = validate_page(getattr(args, "page", None), field="--page")
    per_page = validate_per_page(getattr(args, "per_page", None), field="--per-page")
    order_by = str(getattr(args, "order_by", "") or "").strip() or None
    if order_by not in {None, "latest", "oldest", "popular"}:
        raise ValidationError("--order-by must be one of: latest, oldest, popular")
    orientation = str(getattr(args, "orientation", "") or "").strip() or None
    if orientation not in {None, "landscape", "portrait", "squarish"}:
        raise ValidationError("--orientation must be one of: landscape, portrait, squarish")

    client: UnsplashClient = ctx["client"]
    data = client.get(
        f"/users/{username}/likes",
        params={
            k: v
            for k, v in {"page": page, "per_page": per_page, "order_by": order_by, "orientation": orientation}.items()
            if v is not None
        },
    )
    out = {
        "ok": True,
        "endpoint": "GET /users/:username/likes",
        "username": username,
        "params": {"page": page, "per_page": per_page, "order_by": order_by, "orientation": orientation},
        "data": data,
    }
    ctx["audit"].write("users.likes", {"username": username, "page": page, "per_page": per_page})
    ctx["out"].emit(out)
    return 0


def cmd_users_collections(args: Any, ctx: dict[str, Any]) -> int:
    username = validate_username(str(getattr(args, "username", "") or ""))
    page = validate_page(getattr(args, "page", None), field="--page")
    per_page = validate_per_page(getattr(args, "per_page", None), field="--per-page")

    client: UnsplashClient = ctx["client"]
    data = client.get(f"/users/{username}/collections", params={"page": page, "per_page": per_page})
    out = {
        "ok": True,
        "endpoint": "GET /users/:username/collections",
        "username": username,
        "params": {"page": page, "per_page": per_page},
        "data": data,
    }
    ctx["audit"].write("users.collections", {"username": username, "page": page, "per_page": per_page})
    ctx["out"].emit(out)
    return 0


def cmd_users_statistics(args: Any, ctx: dict[str, Any]) -> int:
    username = validate_username(str(getattr(args, "username", "") or ""))
    resolution = str(getattr(args, "resolution", "") or "").strip() or None
    quantity = str(getattr(args, "quantity", "") or "").strip() or None

    client: UnsplashClient = ctx["client"]
    data = client.get(
        f"/users/{username}/statistics",
        params={k: v for k, v in {"resolution": resolution, "quantity": quantity}.items() if v is not None},
    )
    out = {
        "ok": True,
        "endpoint": "GET /users/:username/statistics",
        "username": username,
        "params": {"resolution": resolution, "quantity": quantity},
        "data": data,
    }
    ctx["audit"].write("users.statistics", {"username": username, "resolution": resolution, "quantity": quantity})
    ctx["out"].emit(out)
    return 0
