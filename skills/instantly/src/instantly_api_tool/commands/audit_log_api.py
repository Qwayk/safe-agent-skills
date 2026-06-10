from __future__ import annotations

from typing import Any

from ..arg_parsing import clamp_limit, parse_yyyy_mm_dd
from ..errors import SafetyError, ValidationError
from ..http import HttpClient
from ..instantly_client import InstantlyClient
from ..json_files import write_json_file


def _client(ctx: dict) -> InstantlyClient:
    cfg = ctx["cfg"]
    http = HttpClient(timeout_s=float(ctx["timeout_s"]), verbose=bool(ctx.get("verbose")), user_agent="instantly-api-tool")
    return InstantlyClient(cfg=cfg, http=http)


def _extract_items(obj: Any) -> list[dict[str, Any]]:
    if isinstance(obj, list):
        return [x for x in obj if isinstance(x, dict)]
    if isinstance(obj, dict):
        for k in ("items", "data", "results", "events"):
            v = obj.get(k)
            if isinstance(v, list):
                return [x for x in v if isinstance(x, dict)]
    return []


def _summarize_item(item: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for k in ("id", "activity_type", "created_at", "createdAt", "ts", "timestamp"):
        if k in item:
            out[k] = item.get(k)
    return out


def cmd_audit_log_list(args: Any, ctx: dict) -> int:
    start_date = parse_yyyy_mm_dd(getattr(args, "start_date", ""), field="start-date")
    end_date = parse_yyyy_mm_dd(getattr(args, "end_date", ""), field="end-date")
    limit = clamp_limit(getattr(args, "limit", None), default=20, max_value=50)
    starting_after = str(getattr(args, "starting_after", "") or "").strip() or None
    search = str(getattr(args, "search", "") or "").strip() or None
    activity_type = getattr(args, "activity_type", None)

    params: dict[str, Any] = {"start_date": start_date, "end_date": end_date}
    if limit is not None:
        params["limit"] = limit
    if starting_after:
        params["starting_after"] = starting_after
    if search:
        params["search"] = search
    if activity_type is not None:
        try:
            params["activity_type"] = int(activity_type)
        except Exception as e:  # noqa: BLE001
            raise ValidationError("Invalid --activity-type (expected int)") from e

    include_items = bool(getattr(args, "include_items", False))
    out_path = str(getattr(args, "out", "") or "").strip() or None
    if include_items and not out_path:
        raise SafetyError("Refused: audit-log list --include-items requires --out <path> (file-only output)")

    client = _client(ctx)
    res = client.get("/audit-logs", params=params)

    items = _extract_items(res.data)
    out: dict[str, Any] = {
        "ok": True,
        "count": len(items) if items else None,
        "next_starting_after": res.next_starting_after,
    }
    out["audit_log_summaries"] = [_summarize_item(i) for i in items]
    if include_items and out_path:
        out_file = write_json_file(out_path, res.data)
        out["out_path"] = out_file

    ctx["audit"].write("audit_log.list", {"ok": True, "include_items": include_items, "out_path": out_path})
    ctx["out"].emit(out)
    return 0
