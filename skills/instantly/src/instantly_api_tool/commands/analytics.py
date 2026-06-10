from __future__ import annotations

from typing import Any

from ..arg_parsing import parse_comma_separated_strings, parse_yyyy_mm_dd
from ..errors import ValidationError
from ..http import HttpClient
from ..instantly_client import InstantlyClient


def _client(ctx: dict) -> InstantlyClient:
    cfg = ctx["cfg"]
    http = HttpClient(timeout_s=float(ctx["timeout_s"]), verbose=bool(ctx.get("verbose")), user_agent="instantly-api-tool")
    return InstantlyClient(cfg=cfg, http=http)


def _emails_arg(args: Any) -> list[str]:
    emails_raw = str(getattr(args, "emails", "") or "").strip()
    return parse_comma_separated_strings(emails_raw, field="emails", min_items=1)


def cmd_analytics_warmup(args: Any, ctx: dict) -> int:
    emails = _emails_arg(args)
    client = _client(ctx)
    res = client.post("/accounts/warmup-analytics", json_body={"emails": emails})
    out = {"ok": True, "warmup_analytics": res.data}
    ctx["audit"].write("analytics.warmup", {"ok": True})
    ctx["out"].emit(out)
    return 0


def cmd_analytics_accounts_daily(args: Any, ctx: dict) -> int:
    emails = _emails_arg(args)
    start_date = parse_yyyy_mm_dd(getattr(args, "start_date", ""), field="start-date")
    end_date = parse_yyyy_mm_dd(getattr(args, "end_date", ""), field="end-date")
    client = _client(ctx)
    res = client.get(
        "/accounts/analytics/daily",
        params={"emails": ",".join(emails), "start_date": start_date, "end_date": end_date},
    )
    out = {"ok": True, "daily_account_analytics": res.data}
    ctx["audit"].write("analytics.accounts_daily", {"ok": True})
    ctx["out"].emit(out)
    return 0


def cmd_analytics_account_vitals(args: Any, ctx: dict) -> int:
    emails = _emails_arg(args)
    client = _client(ctx)
    res = client.post("/accounts/test/vitals", json_body={"emails": emails})
    out = {"ok": True, "account_vitals": res.data}
    ctx["audit"].write("analytics.account_vitals", {"ok": True})
    ctx["out"].emit(out)
    return 0


def _campaign_ids(args: Any) -> list[str]:
    ids: list[str] = []
    raw = getattr(args, "campaign_id", None)
    if raw is None:
        return []
    if isinstance(raw, list):
        vals = raw
    else:
        vals = [raw]
    for v in vals:
        s = str(v or "").strip()
        if s:
            ids.append(s)
    # Deduplicate while preserving order
    seen: set[str] = set()
    out: list[str] = []
    for cid in ids:
        if cid in seen:
            continue
        seen.add(cid)
        out.append(cid)
    return out


def _optional_bool(args: Any, name: str) -> bool | None:
    v = getattr(args, name, None)
    if v:
        return True
    return None


def _optional_int(args: Any, name: str) -> int | None:
    v = getattr(args, name, None)
    if v is None:
        return None
    try:
        return int(v)
    except Exception as e:  # noqa: BLE001
        raise ValidationError(f"Invalid --{name.replace('_', '-')} (expected int)") from e


def _campaign_analytics_date_params(args: Any) -> dict[str, Any]:
    start_date = parse_yyyy_mm_dd(getattr(args, "start_date", ""), field="start-date")
    end_date = parse_yyyy_mm_dd(getattr(args, "end_date", ""), field="end-date")
    return {"start_date": start_date, "end_date": end_date}


def cmd_analytics_campaigns(args: Any, ctx: dict) -> int:
    params: dict[str, Any] = dict(_campaign_analytics_date_params(args))
    cids = _campaign_ids(args)
    if len(cids) == 1:
        params["id"] = cids[0]
    elif len(cids) > 1:
        params["ids"] = cids
    exclude_total = _optional_bool(args, "exclude_total_leads_count")
    if exclude_total is not None:
        params["exclude_total_leads_count"] = exclude_total

    client = _client(ctx)
    res = client.get("/campaigns/analytics", params=params)
    out = {"ok": True, "campaign_analytics": res.data}
    ctx["audit"].write("analytics.campaigns", {"ok": True})
    ctx["out"].emit(out)
    return 0


def cmd_analytics_campaigns_overview(args: Any, ctx: dict) -> int:
    params: dict[str, Any] = dict(_campaign_analytics_date_params(args))
    cids = _campaign_ids(args)
    if len(cids) == 1:
        params["id"] = cids[0]
    elif len(cids) > 1:
        params["ids"] = cids
    campaign_status = _optional_int(args, "campaign_status")
    if campaign_status is not None:
        params["campaign_status"] = campaign_status
    expand_crm = _optional_bool(args, "expand_crm_events")
    if expand_crm is not None:
        params["expand_crm_events"] = expand_crm

    client = _client(ctx)
    res = client.get("/campaigns/analytics/overview", params=params)
    out = {"ok": True, "campaign_analytics_overview": res.data}
    ctx["audit"].write("analytics.campaigns_overview", {"ok": True})
    ctx["out"].emit(out)
    return 0


def cmd_analytics_campaigns_daily(args: Any, ctx: dict) -> int:
    campaign_id = str(getattr(args, "campaign_id", "") or "").strip()
    if not campaign_id:
        raise ValidationError("Missing --campaign-id")
    params: dict[str, Any] = dict(_campaign_analytics_date_params(args))
    params["campaign_id"] = campaign_id
    campaign_status = _optional_int(args, "campaign_status")
    if campaign_status is not None:
        params["campaign_status"] = campaign_status

    client = _client(ctx)
    res = client.get("/campaigns/analytics/daily", params=params)
    out = {"ok": True, "daily_campaign_analytics": res.data}
    ctx["audit"].write("analytics.campaigns_daily", {"ok": True})
    ctx["out"].emit(out)
    return 0


def cmd_analytics_campaign_steps(args: Any, ctx: dict) -> int:
    campaign_id = str(getattr(args, "campaign_id", "") or "").strip()
    if not campaign_id:
        raise ValidationError("Missing --campaign-id")
    params: dict[str, Any] = dict(_campaign_analytics_date_params(args))
    params["campaign_id"] = campaign_id
    include_opp = _optional_bool(args, "include_opportunities_count")
    if include_opp is not None:
        params["include_opportunities_count"] = include_opp

    client = _client(ctx)
    res = client.get("/campaigns/analytics/steps", params=params)
    out = {"ok": True, "campaign_steps_analytics": res.data}
    ctx["audit"].write("analytics.campaign_steps", {"ok": True})
    ctx["out"].emit(out)
    return 0
