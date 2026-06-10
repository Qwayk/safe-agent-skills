from __future__ import annotations

from typing import Any

from ..errors import SafetyError, ValidationError
from ._storage_db_common import (
    base_plan,
    base_receipt,
    emit_plan,
    emit_receipt,
    require_ack_irreversible,
    require_apply,
    require_token,
    require_yes,
    resolve_account_id,
    verify_and_require_plan,
    write_raw_response_to_file,
)


def cmd_r2_buckets_list(args, ctx) -> int:
    require_token(ctx)
    account_id = resolve_account_id(args, ctx)
    res = ctx["cf"].get_json(f"/accounts/{account_id}/r2/buckets")
    items = res.result or []
    ctx["out"].emit(
        {
            "ok": True,
            "command": "r2.buckets.list",
            "account_id": account_id,
            "count": len(items) if isinstance(items, list) else None,
            "result": items,
            "result_info": res.result_info,
        }
    )
    return 0


def cmd_r2_buckets_get(args, ctx) -> int:
    require_token(ctx)
    account_id = resolve_account_id(args, ctx)
    bucket_name = str(getattr(args, "bucket_name", "") or "").strip()
    if not bucket_name:
        raise ValidationError("Missing --bucket-name")
    res = ctx["cf"].get_json(f"/accounts/{account_id}/r2/buckets/{bucket_name}")
    ctx["out"].emit(
        {
            "ok": True,
            "command": "r2.buckets.get",
            "account_id": account_id,
            "bucket_name": bucket_name,
            "result": res.result,
        }
    )
    return 0


def cmd_r2_temp_creds_create(args, ctx) -> int:
    """
    Create R2 temporary access credentials (secret-bearing; file-only).

    Requires --apply --yes --ack-irreversible and --out.
    """
    require_token(ctx)
    account_id = resolve_account_id(args, ctx)
    bucket = str(getattr(args, "bucket", "") or "").strip()
    permission = str(getattr(args, "permission", "") or "").strip()
    ttl_seconds = getattr(args, "ttl_seconds", None)
    parent_access_key_id = str(getattr(args, "parent_access_key_id", "") or "").strip()
    prefixes = getattr(args, "prefix", None) or []
    objects = getattr(args, "object", None) or []
    out_path = str(getattr(args, "out", "") or "").strip()
    overwrite = bool(getattr(args, "overwrite", False))

    if not bucket:
        raise ValidationError("Missing --bucket")
    if not permission:
        raise ValidationError("Missing --permission")
    if ttl_seconds is None:
        raise ValidationError("Missing --ttl-seconds")
    try:
        ttl_seconds_i = int(ttl_seconds)
    except Exception:
        raise ValidationError("--ttl-seconds must be an integer") from None
    if not parent_access_key_id:
        raise ValidationError("Missing --parent-access-key-id")
    if bool(ctx.get("apply")) and not out_path:
        raise SafetyError("Refusing: temp credentials can return secrets. Provide --out.")

    body: dict[str, Any] = {
        "bucket": bucket,
        "permission": permission,
        "ttlSeconds": ttl_seconds_i,
        "parentAccessKeyId": parent_access_key_id,
    }
    if prefixes:
        body["prefixes"] = [str(x) for x in prefixes if str(x).strip()]
    if objects:
        body["objects"] = [str(x) for x in objects if str(x).strip()]

    selector = {"account_id": account_id, "bucket": bucket, "permission": permission, "ttlSeconds": ttl_seconds_i, "out": out_path or None}
    plan = base_plan(
        ctx,
        selector=selector,
        risk_level="irreversible",
        risk_reasons=["Temporary credentials are secret-bearing and may be shown only once.", "This is a write-capable operation."],
    )
    plan["request"] = {"method": "POST", "path": f"/accounts/{account_id}/r2/temp-access-credentials", "sensitivity": "sensitive_write_result", "out": out_path or None}
    if out_path:
        plan["proposed_changes"] = [{"resource": "local_file", "action": "write", "path": out_path, "reason": "r2_temp_creds"}]
        plan["verification_plan"] = ["Confirm the output file exists after apply and record its sha256."]
    else:
        plan["notes"].append("Provide --out to write the credentials to a file (required on --apply).")
        plan["verification_plan"] = ["No-op (dry-run)."]

    if not bool(ctx.get("apply")):
        return emit_plan(ctx, command="r2.temp_creds.create", plan=plan, extra={"ack_required": True})

    require_apply(ctx)
    require_yes(ctx)
    require_ack_irreversible(ctx)
    verify_and_require_plan(ctx, plan=plan)
    assert out_path

    ctx["audit"].write("apply", {"command": "r2.temp_creds.create", "account_id": account_id, "bucket": bucket, "out": out_path})
    resp = ctx["cf"].request_raw(
        "POST",
        f"/accounts/{account_id}/r2/temp-access-credentials",
        json_body=body,
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
    receipt["diff_applied"] = [{"resource": "r2_temp_creds", "action": "created", "account_id": account_id, "bucket": bucket, "output_file": wrote["out_rel"]}]
    receipt["verification"] = {"ok": True, "method": "file_written", "details": {"sha256": wrote["sha256"]}}
    receipt["output_file"] = wrote
    return emit_receipt(ctx, command="r2.temp_creds.create", receipt=receipt, extra={"file": wrote})

