from __future__ import annotations

from ..commands._helpers import (
    ensure_json_output_file,
    find_operation,
    plan_for_operation,
    write_json_file,
)
from ..errors import ToolError, ValidationError
from ..plans import (
    build_receipt,
    default_verification,
    summarize_request,
    write_receipt_to_file,
)


def cmd_auth_check(args, ctx) -> int:
    _ = args
    cfg = ctx["cfg"]
    op = find_operation("user_info")
    selector = {"kind": "user.info", "value": "workspace user"}
    request = summarize_request(op=op)
    plan, plan_path = plan_for_operation(ctx=ctx, op=op, selector=selector, request=request)
    if not ctx.get("live"):
        out_payload = {
            "ok": True,
            "dry_run": True,
            "plan": plan,
            "plan_out": plan_path,
            "base_url": cfg.base_url,
            "env_token_present": bool(cfg.token),
        }
        ctx["audit"].write("auth.check.plan", {"plan_out": plan_path})
        ctx["out"].emit(out_payload)
        return 0

    if not cfg.token:
        raise ValidationError("Missing ELEVENLABS_API_KEY required for --live")

    out_path = ensure_json_output_file(
        path=getattr(args, "out", None),
        overwrite=bool(getattr(args, "overwrite", False)),
    )

    headers = {"xi-api-key": cfg.token}
    try:
        resp = ctx["http_client"].request("GET", f"{cfg.base_url}{op.path}", headers=headers)
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
    ctx["audit"].write("auth.check.apply", {"receipt_out": receipt_path})
    out_payload = {
        "ok": True,
        "dry_run": False,
        "plan": plan,
        "plan_out": plan_path,
        "receipt": receipt,
        "receipt_out": receipt_path,
        "file": fingerprint,
    }
    ctx["out"].emit(out_payload)
    return 0
