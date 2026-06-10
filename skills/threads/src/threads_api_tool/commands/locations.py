from __future__ import annotations

from typing import Any

from ..commands.common import build_read_params
from ..errors import ValidationError
from ..threads_client import ThreadsAPIClient


def _client(ctx: dict[str, Any]) -> ThreadsAPIClient:
    return ThreadsAPIClient(
        cfg=ctx["cfg"],
        env_file=ctx["env_file"],
        timeout_s=ctx["timeout_s"],
        verbose=ctx["verbose"],
    )


def cmd_locations_search_query(args, ctx: dict[str, Any]) -> int:
    query = str(getattr(args, "q", "") or "").strip()
    if not query:
        raise ValidationError("Missing --q")
    params = build_read_params(args=args, include_pagination=False, include_reverse=False)
    result = _client(ctx).search_locations_query(q=query, params=params)
    out = {"ok": True, "command": "locations.search-query", "result": result}
    ctx["audit"].write("locations.search_query", out)
    ctx["out"].emit(out)
    return 0


def cmd_locations_search_coordinates(args, ctx: dict[str, Any]) -> int:
    try:
        latitude = float(getattr(args, "latitude"))
    except Exception:
        raise ValidationError("Missing --latitude")
    try:
        longitude = float(getattr(args, "longitude"))
    except Exception:
        raise ValidationError("Missing --longitude")

    params = build_read_params(args=args, include_pagination=False, include_reverse=False)
    result = _client(ctx).search_locations_coordinates(
        latitude=latitude,
        longitude=longitude,
        params=params,
    )
    out = {"ok": True, "command": "locations.search-coordinates", "result": result}
    ctx["audit"].write("locations.search_coordinates", out)
    ctx["out"].emit(out)
    return 0


def cmd_locations_get(args, ctx: dict[str, Any]) -> int:
    location_id = str(getattr(args, "location_id", "") or "").strip()
    if not location_id:
        raise ValidationError("Missing --location-id")
    params = build_read_params(args=args, include_pagination=False, include_reverse=False)
    out = {
        "ok": True,
        "command": "locations.get",
        "result": _client(ctx).get_location(location_id=location_id, fields=params.get("fields")),
    }
    ctx["audit"].write("locations.get", out)
    ctx["out"].emit(out)
    return 0
