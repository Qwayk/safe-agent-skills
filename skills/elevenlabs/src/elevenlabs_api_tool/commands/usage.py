from __future__ import annotations

from datetime import datetime, timedelta, timezone

from ..commands._helpers import find_operation, plan_for_operation
from ..errors import ToolError, ValidationError
from ..plans import build_receipt, default_verification, summarize_request, write_receipt_to_file


def _default_usage_window_ms() -> tuple[int, int]:
    now = datetime.now(timezone.utc)
    start = (now - timedelta(days=30)).replace(hour=0, minute=0, second=0, microsecond=0)
    return int(start.timestamp() * 1000), int(now.timestamp() * 1000)


def cmd_usage_get(args, ctx) -> int:
    op = find_operation("usage_metrics")
    selector = {"kind": "usage.get", "value": "workspace usage"}
    start_unix = getattr(args, "start_unix", None)
    end_unix = getattr(args, "end_unix", None)
    if start_unix is None or end_unix is None:
        default_start, default_end = _default_usage_window_ms()
        if start_unix is None:
            start_unix = default_start
        if end_unix is None:
            end_unix = default_end

    params: dict[str, object] = {
        "start_unix": start_unix,
        "end_unix": end_unix,
    }
    if getattr(args, "include_workspace_metrics", False):
        params["include_workspace_metrics"] = True
    if getattr(args, "breakdown_type", None):
        params["breakdown_type"] = args.breakdown_type
    if getattr(args, "aggregation_interval", None):
        params["aggregation_interval"] = args.aggregation_interval
    if getattr(args, "aggregation_bucket_size", None) is not None:
        params["aggregation_bucket_size"] = args.aggregation_bucket_size
    if getattr(args, "metric", None):
        params["metric"] = args.metric

    request = summarize_request(op=op, params=params)
    plan, plan_path = plan_for_operation(ctx=ctx, op=op, selector=selector, request=request)

    if not ctx.get("live"):
        ctx["audit"].write("usage.get.plan", {"plan_out": plan_path})
        ctx["out"].emit({"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path})
        return 0

    if not ctx["cfg"].token:
        raise ValidationError("Missing ELEVENLABS_API_KEY required for --live")

    headers = {"xi-api-key": ctx["cfg"].token}
    try:
        resp = ctx["http_client"].request(
            "GET",
            f"{ctx['cfg'].base_url}{op.path}",
            headers=headers,
            params=params,
        )
    except RuntimeError as exc:
        raise ToolError(str(exc)) from exc

    payload = resp.json()
    verification = default_verification(op=op)
    receipt = build_receipt(
        ctx=ctx,
        op=op,
        plan=plan,
        result=payload,
        verification=verification,
        outputs={"usage": payload},
        changed=False,
    )
    receipt_path = write_receipt_to_file(receipt=receipt, path=ctx.get("receipt_out"))
    ctx["audit"].write("usage.get.apply", {"receipt_out": receipt_path})
    ctx["out"].emit(
        {
            "ok": True,
            "dry_run": False,
            "plan": plan,
            "receipt": receipt,
            "receipt_out": receipt_path,
            "response": payload,
        }
    )
    return 0
