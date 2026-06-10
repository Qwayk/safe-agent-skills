from __future__ import annotations

from ..errors import SafetyError, ValidationError
from ._storage_db_common import (
    base_plan,
    base_receipt,
    emit_plan,
    emit_receipt,
    require_apply,
    require_token,
    resolve_account_id,
    verify_and_require_plan,
    write_raw_response_to_file,
)


def cmd_queues_list(args, ctx) -> int:
    require_token(ctx)
    account_id = resolve_account_id(args, ctx)
    res = ctx["cf"].get_json(f"/accounts/{account_id}/queues")
    items = res.result or []
    ctx["out"].emit(
        {
            "ok": True,
            "command": "queues.list",
            "account_id": account_id,
            "count": len(items) if isinstance(items, list) else None,
            "result": items,
            "result_info": res.result_info,
        }
    )
    return 0


def cmd_queues_get(args, ctx) -> int:
    require_token(ctx)
    account_id = resolve_account_id(args, ctx)
    queue_id = str(getattr(args, "queue_id", "") or "").strip()
    if not queue_id:
        raise ValidationError("Missing --queue-id")
    res = ctx["cf"].get_json(f"/accounts/{account_id}/queues/{queue_id}")
    ctx["out"].emit(
        {
            "ok": True,
            "command": "queues.get",
            "account_id": account_id,
            "queue_id": queue_id,
            "result": res.result,
        }
    )
    return 0


def cmd_queues_pull(args, ctx) -> int:
    """
    Pull Queue messages (sensitive output; file-only). Read-like POST (no --yes).
    """
    require_token(ctx)
    account_id = resolve_account_id(args, ctx)
    queue_id = str(getattr(args, "queue_id", "") or "").strip()
    out_path = str(getattr(args, "out", "") or "").strip()
    overwrite = bool(getattr(args, "overwrite", False))
    if not queue_id:
        raise ValidationError("Missing --queue-id")
    if bool(ctx.get("apply")) and not out_path:
        raise SafetyError("Refusing: queues pull returns message bodies (sensitive). Provide --out.")

    selector = {"account_id": account_id, "queue_id": queue_id, "out": out_path or None}
    plan = base_plan(ctx, selector=selector, risk_level="medium", risk_reasons=["Queues pull returns message bodies; output is file-only."])
    plan["request"] = {"method": "POST", "path": f"/accounts/{account_id}/queues/{queue_id}/messages/pull", "sensitivity": "sensitive_read", "out": out_path or None}
    if out_path:
        plan["proposed_changes"] = [{"resource": "local_file", "action": "write", "path": out_path, "reason": "queues_pull"}]
        plan["verification_plan"] = ["Confirm the output file exists after apply and record its sha256."]
    else:
        plan["notes"].append("Provide --out to write the result to a file (required on --apply).")
        plan["verification_plan"] = ["No-op (dry-run)."]

    if not bool(ctx.get("apply")):
        return emit_plan(ctx, command="queues.pull", plan=plan)

    require_apply(ctx)
    verify_and_require_plan(ctx, plan=plan)
    assert out_path

    ctx["audit"].write("apply", {"command": "queues.pull", "account_id": account_id, "queue_id": queue_id, "out": out_path})
    resp = ctx["cf"].request_raw("POST", f"/accounts/{account_id}/queues/{queue_id}/messages/pull", retries=3)
    wrote = write_raw_response_to_file(
        ctx=ctx,
        out_path=out_path,
        overwrite=overwrite,
        method="POST",
        http_status=int(resp.status),
        body=resp.body,
    )

    receipt = base_receipt(ctx, selector=selector, changed=False)
    receipt["diff_applied"] = [{"resource": "queues_pull", "action": "pulled", "account_id": account_id, "queue_id": queue_id, "output_file": wrote["out_rel"]}]
    receipt["verification"] = {"ok": True, "method": "file_written", "details": {"sha256": wrote["sha256"]}}
    receipt["output_file"] = wrote
    return emit_receipt(ctx, command="queues.pull", receipt=receipt, extra={"file": wrote})
