from __future__ import annotations

from typing import Any

from ..errors import ToolError, ValidationError
from ..plans import (
    BEFORE_STATE_REFUSAL_REASON,
    build_before_state_refusal_verification_plan,
    build_receipt,
    default_verification,
    summarize_request,
    write_receipt_to_file,
)
from ..commands._helpers import (
    ensure_json_output_file,
    find_operation,
    plan_for_operation,
    plan_from_file_for_apply,
    write_json_file,
)


def cmd_history_list(args, ctx) -> int:
    limit = getattr(args, "limit", None)
    op = find_operation("history_list")
    selector = {"kind": "history.list", "value": "workspace history"}
    params = {"limit": limit} if limit else None
    request = summarize_request(op=op, params=params)
    plan, plan_path = plan_for_operation(ctx=ctx, op=op, selector=selector, request=request)

    if not ctx.get("live"):
        ctx["audit"].write("history.list.plan", {"plan_out": plan_path})
        ctx["out"].emit({"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path})
        return 0

    if not ctx["cfg"].token:
        raise ValidationError("Missing ELEVENLABS_API_KEY required for --live")

    out_path = ensure_json_output_file(
        path=getattr(args, "out", None),
        overwrite=bool(getattr(args, "overwrite", False)),
    )
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
    fingerprint = write_json_file(out_path, payload)
    verification = default_verification(op=op)
    receipt = build_receipt(
        ctx=ctx,
        op=op,
        plan=plan,
        result={"status_code": resp.status, "file": fingerprint},
        verification=verification,
        outputs={"file": fingerprint},
        changed=False,
    )
    receipt_path = write_receipt_to_file(receipt=receipt, path=ctx.get("receipt_out"))
    ctx["audit"].write("history.list.apply", {"receipt_out": receipt_path})
    ctx["out"].emit(
        {
            "ok": True,
            "dry_run": False,
            "plan": plan,
            "receipt": receipt,
            "receipt_out": receipt_path,
            "file": fingerprint,
        }
    )
    return 0


def cmd_history_download(args, ctx) -> int:
    history_item_id = str(getattr(args, "history_item_id", "") or "").strip()
    if not history_item_id:
        raise ValidationError("Missing --history-item-id")

    op = find_operation("history_download")
    selector = {"kind": "history.download", "value": history_item_id}
    fmt = getattr(args, "format", "mp3") or "mp3"
    payload = {"history_item_ids": [history_item_id], "format": fmt}
    request = summarize_request(op=op, body=payload)
    plan, plan_path = plan_for_operation(ctx=ctx, op=op, selector=selector, request=request)

    if ctx.get("plan_in"):
        applied_plan = plan_from_file_for_apply(ctx=ctx, op=op)
        if applied_plan:
            plan = applied_plan

    if not ctx.get("apply"):
        ctx["audit"].write("history.download.plan", {"plan_out": plan_path})
        ctx["out"].emit({"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path})
        return 0

    if not ctx.get("live"):
        raise ValidationError("Missing --live for history download")
    ctx["audit"].write(
        "history.download.refused",
        {"reason": BEFORE_STATE_REFUSAL_REASON, "before_state": plan.get("before_state")},
    )
    ctx["out"].emit(
        {
            "ok": True,
            "dry_run": False,
            "refused": True,
            "reasons": [BEFORE_STATE_REFUSAL_REASON],
            "refusal_type": "SafetyError",
            "plan": plan,
            "plan_out": plan_path,
            "verification_plan": build_before_state_refusal_verification_plan(),
        }
    )
    return 0
