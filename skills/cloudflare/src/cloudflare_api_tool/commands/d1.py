from __future__ import annotations

from typing import Any

from ..errors import SafetyError, ValidationError
from ..json_files import read_json_file
from ._storage_db_common import (
    base_plan,
    base_receipt,
    build_json_body_meta,
    emit_plan,
    emit_receipt,
    require_apply,
    require_token,
    require_yes,
    resolve_account_id,
    verify_and_require_plan,
    write_raw_response_to_file,
)


def cmd_d1_databases_list(args, ctx) -> int:
    require_token(ctx)
    account_id = resolve_account_id(args, ctx)
    res = ctx["cf"].get_json(f"/accounts/{account_id}/d1/database")
    items = res.result or []
    ctx["out"].emit(
        {
            "ok": True,
            "command": "d1.databases.list",
            "account_id": account_id,
            "count": len(items) if isinstance(items, list) else None,
            "result": items,
            "result_info": res.result_info,
        }
    )
    return 0


def cmd_d1_databases_get(args, ctx) -> int:
    require_token(ctx)
    account_id = resolve_account_id(args, ctx)
    database_id = str(getattr(args, "database_id", "") or "").strip()
    if not database_id:
        raise ValidationError("Missing --database-id")
    res = ctx["cf"].get_json(f"/accounts/{account_id}/d1/database/{database_id}")
    ctx["out"].emit(
        {
            "ok": True,
            "command": "d1.databases.get",
            "account_id": account_id,
            "database_id": database_id,
            "result": res.result,
        }
    )
    return 0


def cmd_d1_export(args, ctx) -> int:
    """
    Export D1 database as SQL (sensitive output; file-only). Read-like POST (no --yes).
    """
    require_token(ctx)
    account_id = resolve_account_id(args, ctx)
    database_id = str(getattr(args, "database_id", "") or "").strip()
    out_path = str(getattr(args, "out", "") or "").strip()
    overwrite = bool(getattr(args, "overwrite", False))
    if not database_id:
        raise ValidationError("Missing --database-id")
    if bool(ctx.get("apply")) and not out_path:
        raise SafetyError("Refusing: D1 export is a sensitive read. Provide --out.")

    selector = {"account_id": account_id, "database_id": database_id, "out": out_path or None}
    plan = base_plan(ctx, selector=selector, risk_level="medium", risk_reasons=["D1 export can reveal database contents; output is file-only."])
    plan["request"] = {"method": "POST", "path": f"/accounts/{account_id}/d1/database/{database_id}/export", "sensitivity": "sensitive_read", "out": out_path or None}
    if out_path:
        plan["proposed_changes"] = [{"resource": "local_file", "action": "write", "path": out_path, "reason": "d1_export"}]
        plan["verification_plan"] = ["Confirm the output file exists after apply and record its sha256."]
    else:
        plan["notes"].append("Provide --out to write the export to a file (required on --apply).")
        plan["verification_plan"] = ["No-op (dry-run)."]

    if not bool(ctx.get("apply")):
        return emit_plan(ctx, command="d1.export", plan=plan)

    require_apply(ctx)
    verify_and_require_plan(ctx, plan=plan)
    assert out_path

    ctx["audit"].write("apply", {"command": "d1.export", "account_id": account_id, "database_id": database_id, "out": out_path})
    resp = ctx["cf"].request_raw("POST", f"/accounts/{account_id}/d1/database/{database_id}/export", retries=3)
    wrote = write_raw_response_to_file(
        ctx=ctx,
        out_path=out_path,
        overwrite=overwrite,
        method="POST",
        http_status=int(resp.status),
        body=resp.body,
    )

    receipt = base_receipt(ctx, selector=selector, changed=False)
    receipt["diff_applied"] = [{"resource": "d1_export", "action": "exported", "account_id": account_id, "database_id": database_id, "output_file": wrote["out_rel"]}]
    receipt["verification"] = {"ok": True, "method": "file_written", "details": {"sha256": wrote["sha256"]}}
    receipt["output_file"] = wrote
    return emit_receipt(ctx, command="d1.export", receipt=receipt, extra={"file": wrote})


def cmd_d1_query(args, ctx) -> int:
    """
    Query D1 database (sensitive output; file-only). Potentially mutating SQL -> requires --yes.
    """
    require_token(ctx)
    account_id = resolve_account_id(args, ctx)
    database_id = str(getattr(args, "database_id", "") or "").strip()
    body_json_file = str(getattr(args, "body_json_file", "") or "").strip()
    out_path = str(getattr(args, "out", "") or "").strip()
    overwrite = bool(getattr(args, "overwrite", False))
    if not database_id:
        raise ValidationError("Missing --database-id")
    if not body_json_file:
        raise ValidationError("Missing --body-json-file")
    if bool(ctx.get("apply")) and not out_path:
        raise SafetyError("Refusing: D1 query can return sensitive values. Provide --out.")

    body_obj: Any = read_json_file(body_json_file)
    body_meta = build_json_body_meta(body_obj, source=body_json_file)

    selector = {"account_id": account_id, "database_id": database_id, "out": out_path or None, "body": {"source": body_json_file, "sha256": body_meta["sha256"]}}
    plan = base_plan(
        ctx,
        selector=selector,
        risk_level="high",
        risk_reasons=["D1 query is a non-GET operation and SQL can be mutating.", "Response can include database contents; output is file-only."],
    )
    plan["request"] = {
        "method": "POST",
        "path": f"/accounts/{account_id}/d1/database/{database_id}/query",
        "body_meta": body_meta,
        "sensitivity": "sensitive_read",
        "out": out_path or None,
    }
    if out_path:
        plan["proposed_changes"] = [{"resource": "local_file", "action": "write", "path": out_path, "reason": "d1_query"}]
        plan["verification_plan"] = ["Confirm the output file exists after apply and record its sha256."]
    else:
        plan["notes"].append("Provide --out to write the result to a file (required on --apply).")
        plan["verification_plan"] = ["No-op (dry-run)."]

    if not bool(ctx.get("apply")):
        return emit_plan(ctx, command="d1.query", plan=plan)

    require_apply(ctx)
    require_yes(ctx)
    verify_and_require_plan(ctx, plan=plan)
    assert out_path

    ctx["audit"].write("apply", {"command": "d1.query", "account_id": account_id, "database_id": database_id, "out": out_path, "body_meta": {"sha256": body_meta["sha256"], "size_bytes": body_meta["size_bytes"]}})
    resp = ctx["cf"].request_raw(
        "POST",
        f"/accounts/{account_id}/d1/database/{database_id}/query",
        json_body=body_obj if isinstance(body_obj, dict) else body_obj,
        retries=3,
    )
    wrote = write_raw_response_to_file(
        ctx=ctx,
        out_path=out_path,
        overwrite=overwrite,
        method="POST",
        http_status=int(resp.status),
        body=resp.body,
    )

    receipt = base_receipt(ctx, selector=selector, changed=True)
    receipt["diff_applied"] = [{"resource": "d1_query", "action": "queried", "account_id": account_id, "database_id": database_id, "output_file": wrote["out_rel"]}]
    receipt["verification"] = {"ok": True, "method": "file_written", "details": {"sha256": wrote["sha256"]}}
    receipt["output_file"] = wrote
    return emit_receipt(ctx, command="d1.query", receipt=receipt, extra={"file": wrote})
