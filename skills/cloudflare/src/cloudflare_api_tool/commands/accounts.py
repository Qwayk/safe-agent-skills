from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from ..errors import ValidationError
from ..errors import SafetyError
from ..plan_and_receipt import (
    load_plan_in,
    require_plan_matches,
    resolve_safe_out_path,
    sha256_of_file,
    utc_now,
    write_plan_if_requested,
    write_receipt_if_requested,
)
from ..state import set_default_account_id
from ..state import get_default_account_id


def cmd_accounts_list(args, ctx) -> int:
    cfg = ctx["cfg"]
    if not cfg.token:
        raise ValidationError("Missing CLOUDFLARE_API_TOKEN")

    page = int(getattr(args, "page", 1) or 1)
    per_page = int(getattr(args, "per_page", 50) or 50)

    res = ctx["cf"].get_json("/accounts", params={"page": page, "per_page": per_page})
    items = res.result or []
    out = {
        "ok": True,
        "command": "accounts.list",
        "page": page,
        "per_page": per_page,
        "count": len(items) if isinstance(items, list) else None,
        "result": items,
        "result_info": res.result_info,
    }
    ctx["audit"].write("accounts.list", {"page": page, "per_page": per_page, "count": out.get("count")})
    ctx["out"].emit(out)
    return 0


def _require_token(ctx) -> None:
    cfg = ctx["cfg"]
    if not cfg.token:
        raise ValidationError("Missing CLOUDFLARE_API_TOKEN")


def _resolve_account_id(args, ctx) -> str:
    account_id = str(getattr(args, "account_id", "") or "").strip()
    if account_id:
        return account_id
    default = get_default_account_id(ctx["env_file"], fingerprint=ctx.get("env_fingerprint"))
    if default:
        return default
    raise ValidationError(
        "Missing --account-id and no default is set. "
        "Run: cloudflare-api-tool accounts set-default --account-id <id>"
    )


def _require_apply(ctx, *, reason: str) -> None:
    if not bool(ctx.get("apply")):
        raise SafetyError(f"Refusing: {reason} Provide --apply to proceed.")


def _require_yes(ctx) -> None:
    if not bool(ctx.get("yes")):
        raise SafetyError("Refusing: this is a write. Re-run with --apply --yes after reviewing the plan.")


def _base_plan(ctx: dict, *, selector: dict[str, Any], risk_level: str, risk_reasons: list[str]) -> dict:
    cfg = ctx.get("cfg")
    base_url = getattr(cfg, "base_url", None) if cfg else None
    return {
        "tool": str(ctx.get("tool") or "cloudflare-api-tool"),
        "version": str(ctx.get("tool_version") or ""),
        "generated_at_utc": utc_now(),
        "env_fingerprint": str(base_url) if base_url else None,
        "command": str(ctx.get("command_str") or ""),
        "selector": selector,
        "risk_level": str(risk_level),
        "risk_reasons": list(risk_reasons),
        "preconditions": [
            "API token has least-privilege permissions needed for this action.",
        ],
        "proposed_changes": [],
        "verification_plan": [],
        "notes": [],
    }


def _base_receipt(ctx: dict, *, selector: dict[str, Any], changed: bool) -> dict:
    cfg = ctx.get("cfg")
    base_url = getattr(cfg, "base_url", None) if cfg else None
    return {
        "tool": str(ctx.get("tool") or "cloudflare-api-tool"),
        "version": str(ctx.get("tool_version") or ""),
        "applied_at_utc": utc_now(),
        "env_fingerprint": str(base_url) if base_url else None,
        "command": str(ctx.get("command_str") or ""),
        "selector": selector,
        "changed": bool(changed),
        "verification": {"ok": False, "details": {}},
        "diff_applied": [],
        "notes": [],
    }


def cmd_accounts_roles_list(args, ctx) -> int:
    _require_token(ctx)
    account_id = _resolve_account_id(args, ctx)

    items = list(ctx["cf"].paginate_page_per_page(f"/accounts/{account_id}/roles", page=1, per_page=50, max_pages=50))
    out = {
        "ok": True,
        "command": "accounts.roles.list",
        "account_id": account_id,
        "count": len(items),
        "result": items,
    }
    ctx["audit"].write("accounts.roles.list", {"account_id": account_id, "count": len(items)})
    ctx["out"].emit(out)
    return 0


def cmd_accounts_roles_get(args, ctx) -> int:
    _require_token(ctx)
    account_id = _resolve_account_id(args, ctx)
    role_id = str(getattr(args, "role_id", "") or "").strip()
    if not role_id:
        raise ValidationError("Missing --role-id")
    res = ctx["cf"].get_json(f"/accounts/{account_id}/roles/{role_id}").result
    out = {
        "ok": True,
        "command": "accounts.roles.get",
        "account_id": account_id,
        "role_id": role_id,
        "result": res,
    }
    ctx["audit"].write("accounts.roles.get", {"account_id": account_id, "role_id": role_id})
    ctx["out"].emit(out)
    return 0


def cmd_accounts_members_list(args, ctx) -> int:
    """
    PII-safe: writes the full member list to --out; never prints member objects to stdout.
    """
    _require_token(ctx)
    account_id = _resolve_account_id(args, ctx)
    status = str(getattr(args, "status", "") or "").strip() or None
    out_path = str(getattr(args, "out", "") or "").strip()
    overwrite = bool(getattr(args, "overwrite", False))

    safe = resolve_safe_out_path(project_dir=Path(ctx["project_dir"]), out_path=out_path, allow_overwrite=overwrite)
    selector = {"account_id": account_id, "status": status, "out": safe.rel_to_project}
    plan = _base_plan(
        ctx,
        selector=selector,
        risk_level="high",
        risk_reasons=["Account members include email addresses (PII). Output is file-only and never printed to stdout."],
    )
    plan["proposed_changes"] = [{"resource": "local_file", "action": "write", "path": safe.rel_to_project, "reason": "account_members_list"}]
    plan["verification_plan"] = ["Confirm the output file exists after apply and record its sha256."]
    plan["notes"] = ["PII safety: do not commit the output file to version control."]

    if not bool(ctx.get("apply")):
        _ = write_plan_if_requested(ctx, plan)
        ctx["out"].emit({"ok": True, "dry_run": True, "command": "accounts.members.list", "plan": plan})
        return 0

    _require_apply(ctx, reason="this is a sensitive read (PII) and writes output to a file.")
    provided = load_plan_in(ctx)
    if provided is not None:
        require_plan_matches(expected_plan=plan, provided_plan=provided)

    params: dict[str, Any] = {}
    if status:
        params["status"] = status
    members = list(ctx["cf"].paginate_page_per_page(f"/accounts/{account_id}/members", params=params, page=1, per_page=50, max_pages=100))
    payload = {
        "ok": True,
        "fetched_at_utc": utc_now(),
        "account_id": account_id,
        "status_filter": status,
        "members": members,
    }
    safe.abs_path.parent.mkdir(parents=True, exist_ok=True)
    safe.abs_path.write_text(json_dumps(payload), encoding="utf-8")
    digest = sha256_of_file(safe.abs_path)

    receipt = _base_receipt(ctx, selector=selector, changed=True)
    receipt["diff_applied"] = [{"resource": "local_file", "action": "written", "path": safe.rel_to_project, "sha256": digest}]
    receipt["verification"] = {"ok": safe.abs_path.exists(), "details": {"sha256": digest, "bytes_written": safe.abs_path.stat().st_size}}
    _ = write_receipt_if_requested(ctx, receipt)
    ctx["audit"].write("apply", {"action": "account_members_list", "account_id": account_id, "out": safe.rel_to_project, "count": len(members)})
    ctx["out"].emit(
        {
            "ok": True,
            "dry_run": False,
            "command": "accounts.members.list",
            "count": len(members),
            "output_file": {"out_rel": safe.rel_to_project, "out_path": str(safe.abs_path), "sha256": digest},
            "receipt": receipt,
        }
    )
    return 0


def cmd_accounts_members_get(args, ctx) -> int:
    """
    PII-safe: writes the full member object to --out; never prints it to stdout.
    """
    _require_token(ctx)
    account_id = _resolve_account_id(args, ctx)
    member_id = str(getattr(args, "member_id", "") or "").strip()
    out_path = str(getattr(args, "out", "") or "").strip()
    overwrite = bool(getattr(args, "overwrite", False))
    if not member_id:
        raise ValidationError("Missing --member-id")

    safe = resolve_safe_out_path(project_dir=Path(ctx["project_dir"]), out_path=out_path, allow_overwrite=overwrite)
    selector = {"account_id": account_id, "member_id": member_id, "out": safe.rel_to_project}
    plan = _base_plan(
        ctx,
        selector=selector,
        risk_level="high",
        risk_reasons=["Account member details include email addresses (PII). Output is file-only and never printed to stdout."],
    )
    plan["proposed_changes"] = [{"resource": "local_file", "action": "write", "path": safe.rel_to_project, "reason": "account_member_get"}]
    plan["verification_plan"] = ["Confirm the output file exists after apply and record its sha256."]
    plan["notes"] = ["PII safety: do not commit the output file to version control."]

    if not bool(ctx.get("apply")):
        _ = write_plan_if_requested(ctx, plan)
        ctx["out"].emit({"ok": True, "dry_run": True, "command": "accounts.members.get", "plan": plan})
        return 0

    _require_apply(ctx, reason="this is a sensitive read (PII) and writes output to a file.")
    provided = load_plan_in(ctx)
    if provided is not None:
        require_plan_matches(expected_plan=plan, provided_plan=provided)

    member = ctx["cf"].get_json(f"/accounts/{account_id}/members/{member_id}").result
    payload = {"ok": True, "fetched_at_utc": utc_now(), "account_id": account_id, "member_id": member_id, "member": member}
    safe.abs_path.parent.mkdir(parents=True, exist_ok=True)
    safe.abs_path.write_text(json_dumps(payload), encoding="utf-8")
    digest = sha256_of_file(safe.abs_path)

    receipt = _base_receipt(ctx, selector=selector, changed=True)
    receipt["diff_applied"] = [{"resource": "local_file", "action": "written", "path": safe.rel_to_project, "sha256": digest}]
    receipt["verification"] = {"ok": safe.abs_path.exists(), "details": {"sha256": digest, "bytes_written": safe.abs_path.stat().st_size}}
    _ = write_receipt_if_requested(ctx, receipt)
    ctx["audit"].write("apply", {"action": "account_member_get", "account_id": account_id, "member_id": member_id, "out": safe.rel_to_project})
    ctx["out"].emit(
        {
            "ok": True,
            "dry_run": False,
            "command": "accounts.members.get",
            "output_file": {"out_rel": safe.rel_to_project, "out_path": str(safe.abs_path), "sha256": digest},
            "receipt": receipt,
        }
    )
    return 0


def _email_sha256(email: str) -> str:
    s = str(email or "").strip().lower().encode("utf-8")
    return hashlib.sha256(s).hexdigest()


def _extract_member_role_ids(member_obj: Any) -> list[str]:
    if not isinstance(member_obj, dict):
        return []
    roles = member_obj.get("roles")
    out: list[str] = []
    if isinstance(roles, list):
        for r in roles:
            if isinstance(r, dict):
                rid = str(r.get("id") or "").strip()
                if rid:
                    out.append(rid)
            elif isinstance(r, str):
                if r.strip():
                    out.append(r.strip())
    return out


def _extract_member_status(member_obj: Any) -> str | None:
    if not isinstance(member_obj, dict):
        return None
    v = member_obj.get("status")
    return str(v).strip() if v is not None else None


def cmd_accounts_members_add(args, ctx) -> int:
    _require_token(ctx)
    account_id = _resolve_account_id(args, ctx)
    email = str(getattr(args, "email", "") or "").strip()
    role_ids = list(getattr(args, "role_id", None) or [])
    status = str(getattr(args, "status", "") or "").strip() or None
    role_ids = [str(x).strip() for x in role_ids if str(x).strip()]
    if not email:
        raise ValidationError("Missing --email")
    if not role_ids:
        raise ValidationError("Missing --role-id (provide at least one)")
    if status and status not in {"accepted", "pending"}:
        raise ValidationError("Invalid --status (expected accepted|pending)")

    selector = {"account_id": account_id, "email_sha256": _email_sha256(email), "role_ids": role_ids, "status": status}
    plan = _base_plan(
        ctx,
        selector=selector,
        risk_level="high",
        risk_reasons=["This grants Cloudflare account access to a person. Member email is treated as sensitive and never printed."],
    )
    plan["proposed_changes"] = [
        {"resource": "account_member", "action": "add", "account_id": account_id, "email_sha256": selector["email_sha256"], "role_ids": role_ids, "status": status}
    ]
    plan["verification_plan"] = ["Fetch member details and confirm role ids (and status if provided)."]
    plan["notes"] = ["PII safety: member emails are not written to stdout/stderr or audit logs."]

    if not bool(ctx.get("apply")):
        _ = write_plan_if_requested(ctx, plan)
        ctx["out"].emit({"ok": True, "dry_run": True, "command": "accounts.members.add", "plan": plan})
        return 0

    _require_apply(ctx, reason="this is a write.")
    _require_yes(ctx)
    provided = load_plan_in(ctx)
    if provided is not None:
        require_plan_matches(expected_plan=plan, provided_plan=provided)

    body: dict[str, Any] = {"email": email, "roles": role_ids}
    if status:
        body["status"] = status

    ctx["audit"].write(
        "apply",
        {"action": "account_member_add", "account_id": account_id, "email_sha256": selector["email_sha256"], "role_ids": role_ids, "status": status},
    )
    res = ctx["cf"].post_json(f"/accounts/{account_id}/members", json_body=body).result
    member_id = str(res.get("id") or "").strip() if isinstance(res, dict) else ""

    verification: dict[str, Any] = {"ok": False, "method": "read_back_get", "details": {}}
    if member_id:
        details = ctx["cf"].get_json(f"/accounts/{account_id}/members/{member_id}").result
        got_roles = sorted(set(_extract_member_role_ids(details)))
        exp_roles = sorted(set(role_ids))
        got_status = _extract_member_status(details)
        ok_roles = got_roles == exp_roles
        ok_status = True if status is None else (str(got_status or "").strip() == status)
        verification = {
            "ok": bool(ok_roles and ok_status),
            "method": "read_back_get",
            "details": {"member_id": member_id, "expected_role_ids": exp_roles, "got_role_ids": got_roles, "expected_status": status, "got_status": got_status},
        }
    else:
        verification = {"ok": False, "method": "read_back_get", "details": {"error": "member_id_missing_from_create_result"}}

    receipt = _base_receipt(ctx, selector=selector, changed=True)
    receipt["diff_applied"] = [{"resource": "account_member", "action": "added", "account_id": account_id, "member_id": member_id, "role_ids": role_ids, "status": status}]
    receipt["verification"] = verification
    _ = write_receipt_if_requested(ctx, receipt)
    ctx["out"].emit({"ok": True, "dry_run": False, "command": "accounts.members.add", "member_id": member_id or None, "receipt": receipt})
    return 0


def cmd_accounts_members_update(args, ctx) -> int:
    _require_token(ctx)
    account_id = _resolve_account_id(args, ctx)
    member_id = str(getattr(args, "member_id", "") or "").strip()
    role_ids = list(getattr(args, "role_id", None) or [])
    status = str(getattr(args, "status", "") or "").strip() or None
    role_ids = [str(x).strip() for x in role_ids if str(x).strip()]
    if not member_id:
        raise ValidationError("Missing --member-id")
    if status and status not in {"accepted", "pending"}:
        raise ValidationError("Invalid --status (expected accepted|pending)")
    if not role_ids and status is None:
        raise ValidationError("No changes requested (provide --role-id and/or --status)")

    selector = {"account_id": account_id, "member_id": member_id, "role_ids": role_ids or None, "status": status}
    plan = _base_plan(
        ctx,
        selector=selector,
        risk_level="high",
        risk_reasons=["This changes Cloudflare account member access/roles. Member objects include email; tool never prints it."],
    )
    plan["proposed_changes"] = [
        {"resource": "account_member", "action": "update", "account_id": account_id, "member_id": member_id, "role_ids": role_ids or None, "status": status}
    ]
    plan["verification_plan"] = ["Fetch member details and confirm role ids (and status if provided)."]
    plan["notes"] = ["PII safety: member emails are not written to stdout/stderr or audit logs."]

    if not bool(ctx.get("apply")):
        _ = write_plan_if_requested(ctx, plan)
        ctx["out"].emit({"ok": True, "dry_run": True, "command": "accounts.members.update", "plan": plan})
        return 0

    _require_apply(ctx, reason="this is a write.")
    _require_yes(ctx)
    provided = load_plan_in(ctx)
    if provided is not None:
        require_plan_matches(expected_plan=plan, provided_plan=provided)

    body: dict[str, Any] = {}
    if role_ids:
        # OpenAPI schema for update-with-roles uses full role objects; fetch details to build a compliant payload.
        role_objs: list[dict[str, Any]] = []
        for rid in role_ids:
            role = ctx["cf"].get_json(f"/accounts/{account_id}/roles/{rid}").result
            if isinstance(role, dict):
                role_objs.append(role)
            else:
                raise SafetyError("Refusing: role details returned non-object; cannot build update payload safely.")
        body["roles"] = role_objs
    if status is not None:
        body["status"] = status

    ctx["audit"].write("apply", {"action": "account_member_update", "account_id": account_id, "member_id": member_id, "role_ids": role_ids or None, "status": status})
    _ = ctx["cf"].put_json(f"/accounts/{account_id}/members/{member_id}", json_body=body).result

    details = ctx["cf"].get_json(f"/accounts/{account_id}/members/{member_id}").result
    got_roles = sorted(set(_extract_member_role_ids(details)))
    exp_roles = sorted(set(role_ids)) if role_ids else None
    got_status = _extract_member_status(details)
    ok_roles = True if exp_roles is None else (got_roles == exp_roles)
    ok_status = True if status is None else (str(got_status or "").strip() == status)
    verification = {
        "ok": bool(ok_roles and ok_status),
        "method": "read_back_get",
        "details": {"member_id": member_id, "expected_role_ids": exp_roles, "got_role_ids": got_roles, "expected_status": status, "got_status": got_status},
    }

    receipt = _base_receipt(ctx, selector=selector, changed=True)
    receipt["diff_applied"] = [{"resource": "account_member", "action": "updated", "account_id": account_id, "member_id": member_id, "role_ids": role_ids or None, "status": status}]
    receipt["verification"] = verification
    _ = write_receipt_if_requested(ctx, receipt)
    ctx["out"].emit({"ok": True, "dry_run": False, "command": "accounts.members.update", "member_id": member_id, "receipt": receipt})
    return 0


def cmd_accounts_members_remove(args, ctx) -> int:
    _require_token(ctx)
    account_id = _resolve_account_id(args, ctx)
    member_id = str(getattr(args, "member_id", "") or "").strip()
    if not member_id:
        raise ValidationError("Missing --member-id")

    selector = {"account_id": account_id, "member_id": member_id}
    plan = _base_plan(
        ctx,
        selector=selector,
        risk_level="high",
        risk_reasons=["This removes Cloudflare account access for a member."],
    )
    plan["proposed_changes"] = [{"resource": "account_member", "action": "remove", "account_id": account_id, "member_id": member_id}]
    plan["verification_plan"] = ["Attempt to fetch member details; expect not found, or confirm missing from member list."]

    if not bool(ctx.get("apply")):
        _ = write_plan_if_requested(ctx, plan)
        ctx["out"].emit({"ok": True, "dry_run": True, "command": "accounts.members.remove", "plan": plan})
        return 0

    _require_apply(ctx, reason="this is a write.")
    _require_yes(ctx)
    provided = load_plan_in(ctx)
    if provided is not None:
        require_plan_matches(expected_plan=plan, provided_plan=provided)

    ctx["audit"].write("apply", {"action": "account_member_remove", "account_id": account_id, "member_id": member_id})
    _ = ctx["cf"].delete_json(f"/accounts/{account_id}/members/{member_id}").result

    resp = ctx["cf"].request_raw_allow_errors("GET", f"/accounts/{account_id}/members/{member_id}")
    ok_absent = int(resp.status) == 404
    verification: dict[str, Any] = {"ok": ok_absent, "method": "read_back_get_expected_missing", "details": {"http_status": int(resp.status)}}
    if not ok_absent:
        # Fallback: check list.
        members = list(ctx["cf"].paginate_page_per_page(f"/accounts/{account_id}/members", page=1, per_page=50, max_pages=100))
        ids = [str(x.get("id") or "").strip() for x in members if isinstance(x, dict)]
        ok_absent = member_id not in ids
        verification = {
            "ok": ok_absent,
            "method": "read_back_list_expected_missing",
            "details": {"http_status_get": int(resp.status), "member_id": member_id, "present_in_list": (member_id in ids), "list_count": len(ids)},
        }

    receipt = _base_receipt(ctx, selector=selector, changed=True)
    receipt["diff_applied"] = [{"resource": "account_member", "action": "removed", "account_id": account_id, "member_id": member_id}]
    receipt["verification"] = verification
    _ = write_receipt_if_requested(ctx, receipt)
    ctx["out"].emit({"ok": True, "dry_run": False, "command": "accounts.members.remove", "member_id": member_id, "receipt": receipt})
    return 0


def cmd_accounts_set_default(args, ctx) -> int:
    account_id = str(getattr(args, "account_id", "") or "").strip()
    if not account_id:
        raise ValidationError("Missing --account-id")
    dest = set_default_account_id(ctx["env_file"], account_id, fingerprint=ctx.get("env_fingerprint"))
    out = {
        "ok": True,
        "command": "accounts.set_default",
        "default_account_id": account_id,
        "written_to": dest,
    }
    ctx["audit"].write("accounts.set_default", {"default_account_id": account_id, "written_to": dest})
    ctx["out"].emit(out)
    return 0


def json_dumps(obj: Any) -> str:
    # Local helper to ensure stable, unicode-safe files.
    import json

    return json.dumps(obj, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
