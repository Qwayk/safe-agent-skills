from __future__ import annotations

from typing import Any

from ..api import PinterestApi, resolve_access_token


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


def _parse_kv_pairs(pairs: list[str] | None) -> dict[str, Any]:
    if not pairs:
        return {}
    out: dict[str, Any] = {}
    for raw in pairs:
        s = (raw or "").strip()
        if not s:
            continue
        if "=" not in s:
            raise RuntimeError(f"Invalid --param (expected key=value): {raw}")
        k, v = s.split("=", 1)
        k = k.strip()
        v = v.strip()
        if not k:
            raise RuntimeError(f"Invalid --param (empty key): {raw}")
        if k in out:
            prev = out[k]
            if isinstance(prev, list):
                prev.append(v)
            else:
                out[k] = [prev, v]
        else:
            out[k] = v
    return out


def _get_resources(args: Any, ctx: dict[str, Any], *, stage: str, path: str) -> int:
    api = _api(ctx)
    params = _parse_kv_pairs(getattr(args, "param", None))
    data = api.get(path, params=params or None)
    out = {"ok": True, "path": path, "params": params, "data": data}
    ctx["audit"].write(stage, {})
    ctx["out"].emit(out)
    return 0


def cmd_resources_ad_account_countries(args: Any, ctx: dict[str, Any]) -> int:
    return _get_resources(args, ctx, stage="resources.ad_account_countries", path="/resources/ad_account_countries")


def cmd_resources_delivery_metrics(args: Any, ctx: dict[str, Any]) -> int:
    return _get_resources(args, ctx, stage="resources.delivery_metrics", path="/resources/delivery_metrics")


def cmd_resources_metrics_ready_state(args: Any, ctx: dict[str, Any]) -> int:
    return _get_resources(args, ctx, stage="resources.metrics_ready_state", path="/resources/metrics_ready_state")


def cmd_resources_targeting(args: Any, ctx: dict[str, Any]) -> int:
    targeting_type = str(getattr(args, "targeting_type", "") or "").strip()
    if not targeting_type:
        raise RuntimeError("--targeting-type is required")
    return _get_resources(
        args,
        ctx,
        stage="resources.targeting",
        path=f"/resources/targeting/{targeting_type}",
    )


def cmd_resources_targeting_interest(args: Any, ctx: dict[str, Any]) -> int:
    interest_id = str(getattr(args, "interest_id", "") or "").strip()
    if not interest_id:
        raise RuntimeError("--interest-id is required")
    return _get_resources(
        args,
        ctx,
        stage="resources.targeting.interests",
        path=f"/resources/targeting/interests/{interest_id}",
    )

