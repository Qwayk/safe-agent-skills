from __future__ import annotations

from typing import Any

from ..api import PinterestApi, build_analytics_params, resolve_access_token


def _api(ctx: dict[str, Any]) -> PinterestApi:
    cfg = ctx["cfg"]
    return PinterestApi(
        base_url=cfg.base_url,
        http=ctx["http"],
        access_token=resolve_access_token(
            env_file=ctx["env_file"],
            env_access_token=cfg.access_token,
            env_refresh_token=cfg.refresh_token,
            app_id=cfg.app_id,
            app_secret=cfg.app_secret,
            base_url=cfg.base_url,
            http=ctx["http"],
        ),
    )


def _default_metrics() -> list[str]:
    # Best-effort defaults (safe + common). Users can override via --metric or --param.
    return ["IMPRESSION"]


def cmd_analytics_user(args: Any, ctx: dict[str, Any]) -> int:
    api = _api(ctx)
    params = build_analytics_params(
        start_date=args.start_date,
        end_date=args.end_date,
        metrics=args.metric,
        extra_params=args.param,
        default_days=90,
        default_metrics=_default_metrics(),
    )
    if args.ad_account_id:
        params["ad_account_id"] = str(args.ad_account_id).strip()
    data = api.get("/user_account/analytics", params=params)
    out = {"ok": True, "params": params, "analytics": data}
    ctx["audit"].write("analytics.user", {"start_date": params["start_date"], "end_date": params["end_date"]})
    ctx["out"].emit(out)
    return 0


def cmd_analytics_top_pins(args: Any, ctx: dict[str, Any]) -> int:
    api = _api(ctx)
    params = build_analytics_params(
        start_date=args.start_date,
        end_date=args.end_date,
        metrics=args.metric,
        extra_params=args.param,
        default_days=90,
        default_metrics=_default_metrics(),
    )
    params["sort_by"] = str(args.sort_by or "IMPRESSION").strip().upper()
    if args.ad_account_id:
        params["ad_account_id"] = str(args.ad_account_id).strip()
    data = api.get("/user_account/analytics/top_pins", params=params)
    out = {"ok": True, "params": params, "analytics": data}
    ctx["audit"].write("analytics.top_pins", {"start_date": params["start_date"], "end_date": params["end_date"]})
    ctx["out"].emit(out)
    return 0


def cmd_analytics_top_video_pins(args: Any, ctx: dict[str, Any]) -> int:
    api = _api(ctx)
    params = build_analytics_params(
        start_date=args.start_date,
        end_date=args.end_date,
        metrics=args.metric,
        extra_params=args.param,
        default_days=90,
        default_metrics=_default_metrics(),
    )
    params["sort_by"] = str(args.sort_by or "IMPRESSION").strip().upper()
    if args.ad_account_id:
        params["ad_account_id"] = str(args.ad_account_id).strip()
    data = api.get("/user_account/analytics/top_video_pins", params=params)
    out = {"ok": True, "params": params, "analytics": data}
    ctx["audit"].write(
        "analytics.top_video_pins",
        {"start_date": params["start_date"], "end_date": params["end_date"]},
    )
    ctx["out"].emit(out)
    return 0


def cmd_analytics_pin(args: Any, ctx: dict[str, Any]) -> int:
    api = _api(ctx)
    pin_id = str(args.id).strip()
    if not pin_id:
        raise RuntimeError("--id is required")
    params = build_analytics_params(
        start_date=args.start_date,
        end_date=args.end_date,
        metrics=args.metric,
        extra_params=args.param,
        default_days=90,
        default_metrics=_default_metrics(),
    )
    if args.ad_account_id:
        params["ad_account_id"] = str(args.ad_account_id).strip()
    data = api.get(f"/pins/{pin_id}/analytics", params=params)
    out = {"ok": True, "pin_id": pin_id, "params": params, "analytics": data}
    ctx["audit"].write("analytics.pin", {"pin_id": pin_id, "start_date": params["start_date"], "end_date": params["end_date"]})
    ctx["out"].emit(out)
    return 0


def cmd_analytics_pins(args: Any, ctx: dict[str, Any]) -> int:
    api = _api(ctx)
    raw = str(args.ids).strip()
    if not raw:
        raise RuntimeError("--ids is required")
    ids = [s.strip() for s in raw.split(",") if s.strip()]
    if not ids:
        raise RuntimeError("--ids must contain at least one id")
    if len(ids) > 100:
        raise RuntimeError("--ids supports at most 100 ids")
    if not all(i.isdigit() for i in ids):
        raise RuntimeError("--ids must be a comma-separated list of numeric Pin IDs")

    params = build_analytics_params(
        start_date=args.start_date,
        end_date=args.end_date,
        metrics=args.metric,
        extra_params=args.param,
        default_days=90,
        default_metrics=_default_metrics(),
    )
    # Best-effort (based on common API conventions).
    params["pin_ids"] = ids
    if args.ad_account_id:
        params["ad_account_id"] = str(args.ad_account_id).strip()
    data = api.get("/pins/analytics", params=params)
    out = {"ok": True, "pin_ids": ids, "params": params, "analytics": data}
    ctx["audit"].write(
        "analytics.pins",
        {"pin_ids_count": len(ids), "start_date": params["start_date"], "end_date": params["end_date"]},
    )
    ctx["out"].emit(out)
    return 0
