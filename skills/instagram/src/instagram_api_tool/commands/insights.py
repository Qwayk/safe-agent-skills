from __future__ import annotations

from typing import Any

from ..errors import ValidationError
from ..instagram_client import InstagramAPIClient
from .write_utils import split_csv_arg


def _client(ctx: dict[str, Any]) -> InstagramAPIClient:
    return InstagramAPIClient(
        cfg=ctx["cfg"],
        env_file=ctx["env_file"],
        timeout_s=ctx["timeout_s"],
        verbose=ctx["verbose"],
    )


def _build_insight_params(args: Any) -> dict[str, Any]:
    metrics = split_csv_arg(getattr(args, "metric", None))
    if not metrics:
        raise ValidationError("Missing --metric")
    params: dict[str, Any] = {"metric": ",".join(metrics)}
    period = str(getattr(args, "period", "") or "").strip()
    if period:
        params["period"] = period
    breakdown = split_csv_arg(getattr(args, "breakdown", None))
    if breakdown:
        params["breakdown"] = ",".join(breakdown)
    return params


def cmd_insights_account_get(args: Any, ctx: dict[str, Any]) -> int:
    ig_user_id = str(getattr(args, "ig_user_id", "") or "").strip()
    if not ig_user_id:
        raise ValidationError("Missing --ig-user-id")
    params = _build_insight_params(args)

    client = _client(ctx)
    result = client.get(f"/{ig_user_id}/insights", params=params)
    out = {"ok": True, "command": "insights.account.get", "result": result}
    ctx["audit"].write("insights.account.get", out)
    ctx["out"].emit(out)
    return 0


def cmd_insights_media_get(args: Any, ctx: dict[str, Any]) -> int:
    media_id = str(getattr(args, "media_id", "") or "").strip()
    if not media_id:
        raise ValidationError("Missing --media-id")
    params = _build_insight_params(args)

    client = _client(ctx)
    result = client.get(f"/{media_id}/insights", params=params)
    out = {"ok": True, "command": "insights.media.get", "result": result}
    ctx["audit"].write("insights.media.get", out)
    ctx["out"].emit(out)
    return 0
