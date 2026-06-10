from __future__ import annotations

from ..errors import ToolError, ValidationError
from ..plans import build_receipt, default_verification, summarize_request, write_receipt_to_file
from ..commands._helpers import find_operation, plan_for_operation


def cmd_voices_list(args, ctx) -> int:
    _ = args
    op = find_operation("list_voices")
    selector = {"kind": "voices.list", "value": "workspace voices"}
    request = summarize_request(op=op)
    plan, plan_path = plan_for_operation(ctx=ctx, op=op, selector=selector, request=request)
    if not ctx.get("live"):
        ctx["audit"].write("voices.list.plan", {"plan_out": plan_path})
        ctx["out"].emit({"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path})
        return 0

    if not ctx["cfg"].token:
        raise ValidationError("Missing ELEVENLABS_API_KEY required for --live")

    headers = {"xi-api-key": ctx["cfg"].token}
    try:
        resp = ctx["http_client"].request("GET", f"{ctx['cfg'].base_url}{op.path}", headers=headers)
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
        outputs={"voices": payload},
        changed=False,
    )
    receipt_path = write_receipt_to_file(receipt=receipt, path=ctx.get("receipt_out"))
    ctx["audit"].write("voices.list.apply", {"receipt_out": receipt_path})
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
