from __future__ import annotations

from typing import Any

from ..arg_parsing import clamp_limit, parse_yyyy_mm_dd, quote_path_segment
from ..errors import ValidationError
from ..http import HttpClient
from ..instantly_client import InstantlyClient


def _client(ctx: dict) -> InstantlyClient:
    cfg = ctx["cfg"]
    http = HttpClient(timeout_s=float(ctx["timeout_s"]), verbose=bool(ctx.get("verbose")), user_agent="instantly-api-tool")
    return InstantlyClient(cfg=cfg, http=http)


def _pagination_params(args: Any) -> dict[str, Any]:
    params: dict[str, Any] = {}
    limit = clamp_limit(getattr(args, "limit", None), default=20, max_value=50)
    if limit is not None:
        params["limit"] = limit
    if getattr(args, "starting_after", None):
        params["starting_after"] = str(args.starting_after).strip()
    if getattr(args, "webhook_id", None):
        params["webhook_id"] = str(args.webhook_id).strip()
    return params


def cmd_webhook_events_list(args: Any, ctx: dict) -> int:
    client = _client(ctx)
    res = client.get("/webhook-events", params=_pagination_params(args))
    out = {"ok": True, "events": res.data, "next_starting_after": res.next_starting_after}
    ctx["audit"].write("webhook_events.list", {"ok": True})
    ctx["out"].emit(out)
    return 0


def cmd_webhook_events_get(args: Any, ctx: dict) -> int:
    event_id = str(getattr(args, "event_id", "") or "").strip()
    if not event_id:
        raise ValidationError("Missing --event-id")
    client = _client(ctx)
    res = client.get(f"/webhook-events/{quote_path_segment(event_id, field='event-id')}")
    out = {"ok": True, "event": res.data}
    ctx["audit"].write("webhook_events.get", {"ok": True})
    ctx["out"].emit(out)
    return 0


def cmd_webhook_events_summary(args: Any, ctx: dict) -> int:
    from_date = parse_yyyy_mm_dd(getattr(args, "from_date", ""), field="from")
    to_date = parse_yyyy_mm_dd(getattr(args, "to_date", ""), field="to")
    client = _client(ctx)
    res = client.get("/webhook-events/summary", params={"from": from_date, "to": to_date})
    out = {"ok": True, "summary": res.data}
    ctx["audit"].write("webhook_events.summary", {"ok": True})
    ctx["out"].emit(out)
    return 0


def cmd_webhook_events_summary_by_date(args: Any, ctx: dict) -> int:
    from_date = parse_yyyy_mm_dd(getattr(args, "from_date", ""), field="from")
    to_date = parse_yyyy_mm_dd(getattr(args, "to_date", ""), field="to")
    client = _client(ctx)
    res = client.get("/webhook-events/summary-by-date", params={"from": from_date, "to": to_date})
    out = {"ok": True, "summary_by_date": res.data}
    ctx["audit"].write("webhook_events.summary_by_date", {"ok": True})
    ctx["out"].emit(out)
    return 0
