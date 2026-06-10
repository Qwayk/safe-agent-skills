from __future__ import annotations

from typing import Any

from ..errors import ValidationError
from ..pagination import validate_page, validate_per_page
from ..unsplash_client import UnsplashClient, validate_positive_int


def cmd_collections_list(args: Any, ctx: dict[str, Any]) -> int:
    page = validate_page(getattr(args, "page", None), field="--page")
    per_page = validate_per_page(getattr(args, "per_page", None), field="--per-page")
    client: UnsplashClient = ctx["client"]
    data = client.get("/collections", params={"page": page, "per_page": per_page})
    out = {"ok": True, "endpoint": "GET /collections", "params": {"page": page, "per_page": per_page}, "data": data}
    ctx["audit"].write("collections.list", out["params"])
    ctx["out"].emit(out)
    return 0


def cmd_collections_get(args: Any, ctx: dict[str, Any]) -> int:
    collection_id = validate_positive_int(getattr(args, "id", None), field="--id")
    client: UnsplashClient = ctx["client"]
    data = client.get(f"/collections/{collection_id}")
    out = {"ok": True, "endpoint": "GET /collections/:id", "id": collection_id, "data": data}
    ctx["audit"].write("collections.get", {"id": collection_id})
    ctx["out"].emit(out)
    return 0


def cmd_collections_photos(args: Any, ctx: dict[str, Any]) -> int:
    collection_id = validate_positive_int(getattr(args, "id", None), field="--id")
    page = validate_page(getattr(args, "page", None), field="--page")
    per_page = validate_per_page(getattr(args, "per_page", None), field="--per-page")
    orientation = str(getattr(args, "orientation", "") or "").strip() or None
    if orientation not in {None, "landscape", "portrait", "squarish"}:
        raise ValidationError("--orientation must be one of: landscape, portrait, squarish")

    client: UnsplashClient = ctx["client"]
    data = client.get(
        f"/collections/{collection_id}/photos",
        params={k: v for k, v in {"page": page, "per_page": per_page, "orientation": orientation}.items() if v is not None},
    )
    out = {
        "ok": True,
        "endpoint": "GET /collections/:id/photos",
        "id": collection_id,
        "params": {"page": page, "per_page": per_page, "orientation": orientation},
        "data": data,
    }
    ctx["audit"].write("collections.photos", {"id": collection_id, "page": page, "per_page": per_page})
    ctx["out"].emit(out)
    return 0


def cmd_collections_related(args: Any, ctx: dict[str, Any]) -> int:
    collection_id = validate_positive_int(getattr(args, "id", None), field="--id")
    client: UnsplashClient = ctx["client"]
    data = client.get(f"/collections/{collection_id}/related")
    out = {"ok": True, "endpoint": "GET /collections/:id/related", "id": collection_id, "data": data}
    ctx["audit"].write("collections.related", {"id": collection_id})
    ctx["out"].emit(out)
    return 0
