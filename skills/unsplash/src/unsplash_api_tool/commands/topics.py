from __future__ import annotations

from typing import Any

from ..errors import ValidationError
from ..pagination import validate_page, validate_per_page
from ..unsplash_client import UnsplashClient


def _validate_topic_id(value: str) -> str:
    v = (value or "").strip()
    if not v:
        raise ValidationError("Missing --id")
    return v


def cmd_topics_list(args: Any, ctx: dict[str, Any]) -> int:
    page = validate_page(getattr(args, "page", None), field="--page")
    per_page = validate_per_page(getattr(args, "per_page", None), field="--per-page")
    order_by = str(getattr(args, "order_by", "") or "").strip() or None
    if order_by not in {None, "featured", "latest", "oldest", "position"}:
        raise ValidationError("--order-by must be one of: featured, latest, oldest, position")

    client: UnsplashClient = ctx["client"]
    data = client.get(
        "/topics",
        params={k: v for k, v in {"page": page, "per_page": per_page, "order_by": order_by}.items() if v is not None},
    )
    out = {"ok": True, "endpoint": "GET /topics", "params": {"page": page, "per_page": per_page, "order_by": order_by}, "data": data}
    ctx["audit"].write("topics.list", out["params"])
    ctx["out"].emit(out)
    return 0


def cmd_topics_get(args: Any, ctx: dict[str, Any]) -> int:
    topic_id = _validate_topic_id(str(getattr(args, "id", "") or ""))
    client: UnsplashClient = ctx["client"]
    data = client.get(f"/topics/{topic_id}")
    out = {"ok": True, "endpoint": "GET /topics/:id", "id": topic_id, "data": data}
    ctx["audit"].write("topics.get", {"id": topic_id})
    ctx["out"].emit(out)
    return 0


def cmd_topics_photos(args: Any, ctx: dict[str, Any]) -> int:
    topic_id = _validate_topic_id(str(getattr(args, "id", "") or ""))
    page = validate_page(getattr(args, "page", None), field="--page")
    per_page = validate_per_page(getattr(args, "per_page", None), field="--per-page")
    orientation = str(getattr(args, "orientation", "") or "").strip() or None
    if orientation not in {None, "landscape", "portrait", "squarish"}:
        raise ValidationError("--orientation must be one of: landscape, portrait, squarish")

    client: UnsplashClient = ctx["client"]
    data = client.get(
        f"/topics/{topic_id}/photos",
        params={k: v for k, v in {"page": page, "per_page": per_page, "orientation": orientation}.items() if v is not None},
    )
    out = {
        "ok": True,
        "endpoint": "GET /topics/:id/photos",
        "id": topic_id,
        "params": {"page": page, "per_page": per_page, "orientation": orientation},
        "data": data,
    }
    ctx["audit"].write("topics.photos", {"id": topic_id, "page": page, "per_page": per_page})
    ctx["out"].emit(out)
    return 0
