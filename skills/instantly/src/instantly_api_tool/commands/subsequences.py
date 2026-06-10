from __future__ import annotations

from pathlib import Path
from typing import Any

from ..errors import SafetyError, ValidationError
from ..http import HttpClient
from ..instantly_client import InstantlyClient
from ..json_files import read_json_file, write_json_file
from ..plans import build_plan, utc_now, validate_plan_env, validate_plan_kind
from ..redaction import sanitize


def _client(ctx: dict) -> InstantlyClient:
    cfg = ctx["cfg"]
    http = HttpClient(timeout_s=float(ctx["timeout_s"]), verbose=bool(ctx.get("verbose")), user_agent="instantly-api-tool")
    return InstantlyClient(cfg=cfg, http=http)


def _pagination_params(args: Any) -> dict[str, Any]:
    params: dict[str, Any] = {}
    if getattr(args, "limit", None) is not None:
        params["limit"] = int(args.limit)
    if getattr(args, "starting_after", None):
        params["starting_after"] = str(args.starting_after).strip()
    return params


def _load_file_json(file_path: str) -> dict[str, Any]:
    p = Path(file_path)
    body_any = read_json_file(p)
    if not isinstance(body_any, dict):
        raise ValidationError("Input JSON file must be a JSON object")
    return dict(body_any)


def _extract_id(obj: Any) -> str | None:
    if isinstance(obj, dict):
        for k in ("id", "subsequence_id", "subsequenceId"):
            v = obj.get(k)
            if v:
                s = str(v).strip()
                if s:
                    return s
    return None


def cmd_subsequences_list(args: Any, ctx: dict) -> int:
    client = _client(ctx)
    res = client.get("/subsequences", params=_pagination_params(args))
    out = {"ok": True, "subsequences": res.data, "next_starting_after": res.next_starting_after}
    ctx["audit"].write("subsequences.list", {"ok": True})
    ctx["out"].emit(out)
    return 0


def cmd_subsequences_get(args: Any, ctx: dict) -> int:
    subsequence_id = str(getattr(args, "subsequence_id", "") or "").strip()
    if not subsequence_id:
        raise ValidationError("Missing --subsequence-id")
    client = _client(ctx)
    res = client.get(f"/subsequences/{subsequence_id}")
    out = {"ok": True, "subsequence": res.data}
    ctx["audit"].write("subsequences.get", {"ok": True})
    ctx["out"].emit(out)
    return 0


def cmd_subsequences_create(args: Any, ctx: dict) -> int:
    file_path = str(getattr(args, "file", "") or "").strip()
    if not file_path:
        raise ValidationError("Missing --file (subsequence JSON)")
    body = _load_file_json(file_path)

    plan = build_plan(
        tool=str(ctx.get("tool") or "instantly-api-tool"),
        version=str(ctx.get("tool_version") or ""),
        env_fingerprint=str(ctx["cfg"].base_url),
        command=str(ctx.get("command_str") or ""),
        selector={"kind": "subsequences.create", "value": file_path},
        risk_level="medium",
        risk_reasons=["creates-subsequence"],
        request={"method": "POST", "path": "/subsequences", "body": sanitize(body)},
        verification_plan={"type": "read-back", "notes": "Best-effort: GET subsequence by returned id."},
        baseline={"env_fingerprint": str(ctx["cfg"].base_url)},
    )
    plan_out = ctx.get("plan_out")
    plan_path = write_json_file(plan_out, sanitize(plan)) if (plan_out and not bool(ctx.get("apply"))) else None

    if not bool(ctx.get("apply")):
        out = {"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path}
        ctx["audit"].write("subsequences.create.plan", {"ok": True, "plan_out": plan_path})
        ctx["out"].emit(out)
        return 0

    client = _client(ctx)
    created = client.post("/subsequences", json_body=body).data
    verify = None
    subsequence_id = _extract_id(created)
    if subsequence_id:
        try:
            verify = client.get(f"/subsequences/{subsequence_id}").data
        except Exception:  # noqa: BLE001
            verify = None

    receipt = {
        "tool": str(ctx.get("tool") or "instantly-api-tool"),
        "version": str(ctx.get("tool_version") or ""),
        "applied_at_utc": utc_now(),
        "env_fingerprint": str(ctx["cfg"].base_url),
        "command": str(ctx.get("command_str") or ""),
        "selector": plan.get("selector"),
        "changed": True,
        "verification": {"ok": verify is not None, "details": {"type": "subsequences.get", "subsequence_id": subsequence_id}},
        "result": {"created": sanitize(created), "verified_subsequence": sanitize(verify)},
        "backups": [],
        "rollback_plan": None,
    }
    receipt_out = ctx.get("receipt_out")
    receipt_path = write_json_file(receipt_out, sanitize(receipt)) if receipt_out else None
    out = {"ok": True, "dry_run": False, "receipt": receipt, "receipt_out": receipt_path}
    ctx["audit"].write("subsequences.create.apply", {"ok": True, "receipt_out": receipt_path})
    ctx["out"].emit(out)
    return 0


def cmd_subsequences_patch(args: Any, ctx: dict) -> int:
    subsequence_id = str(getattr(args, "subsequence_id", "") or "").strip()
    if not subsequence_id:
        raise ValidationError("Missing --subsequence-id")
    file_path = str(getattr(args, "file", "") or "").strip()
    if not file_path:
        raise ValidationError("Missing --file (subsequence patch JSON)")
    body = _load_file_json(file_path)
    path = f"/subsequences/{subsequence_id}"

    plan = build_plan(
        tool=str(ctx.get("tool") or "instantly-api-tool"),
        version=str(ctx.get("tool_version") or ""),
        env_fingerprint=str(ctx["cfg"].base_url),
        command=str(ctx.get("command_str") or ""),
        selector={"kind": "subsequences.patch", "value": subsequence_id},
        risk_level="medium",
        risk_reasons=["updates-subsequence"],
        request={"method": "PATCH", "path": path, "body": sanitize(body)},
        verification_plan={"type": "read-back", "notes": "GET subsequence after apply."},
        baseline={"env_fingerprint": str(ctx["cfg"].base_url), "subsequence_id": subsequence_id},
    )
    plan_out = ctx.get("plan_out")
    plan_path = write_json_file(plan_out, sanitize(plan)) if (plan_out and not bool(ctx.get("apply"))) else None

    if not bool(ctx.get("apply")):
        out = {"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path}
        ctx["audit"].write("subsequences.patch.plan", {"ok": True, "plan_out": plan_path})
        ctx["out"].emit(out)
        return 0

    client = _client(ctx)
    changed = client.patch(path, json_body=body).data
    verify = None
    try:
        verify = client.get(path).data
    except Exception:  # noqa: BLE001
        verify = None

    receipt = {
        "tool": str(ctx.get("tool") or "instantly-api-tool"),
        "version": str(ctx.get("tool_version") or ""),
        "applied_at_utc": utc_now(),
        "env_fingerprint": str(ctx["cfg"].base_url),
        "command": str(ctx.get("command_str") or ""),
        "selector": plan.get("selector"),
        "changed": True,
        "verification": {"ok": verify is not None, "details": {"type": "subsequences.get", "subsequence_id": subsequence_id}},
        "result": {"operation_result": sanitize(changed), "verified_subsequence": sanitize(verify)},
        "backups": [],
        "rollback_plan": None,
    }
    receipt_out = ctx.get("receipt_out")
    receipt_path = write_json_file(receipt_out, sanitize(receipt)) if receipt_out else None
    out = {"ok": True, "dry_run": False, "receipt": receipt, "receipt_out": receipt_path}
    ctx["audit"].write("subsequences.patch.apply", {"ok": True, "receipt_out": receipt_path})
    ctx["out"].emit(out)
    return 0


def cmd_subsequences_delete(args: Any, ctx: dict) -> int:
    apply = bool(ctx.get("apply"))
    yes = bool(ctx.get("yes"))
    plan_in = ctx.get("plan_in")

    if plan_in and not apply:
        raise ValidationError("--plan-in can only be used with --apply")
    if apply:
        if not yes:
            raise SafetyError("Refused: subsequences delete requires --apply --yes")
        if not plan_in:
            raise SafetyError("Refused: subsequences delete on apply requires --plan-in (plan-file workflow)")

    if plan_in:
        plan_obj_any = read_json_file(plan_in)
        if not isinstance(plan_obj_any, dict):
            raise ValidationError("Plan file must be a JSON object")
        plan_obj: dict[str, Any] = dict(plan_obj_any)
        validate_plan_env(plan_obj, env_fingerprint=str(ctx["cfg"].base_url))
        validate_plan_kind(plan_obj, kind="subsequences.delete")
        baseline = plan_obj.get("baseline") or {}
        if not isinstance(baseline, dict):
            raise ValidationError("Plan baseline must be a JSON object")
        subsequence_id = str(baseline.get("subsequence_id") or "").strip()
        if not subsequence_id:
            raise ValidationError("Plan baseline missing subsequence_id")
    else:
        subsequence_id = str(getattr(args, "subsequence_id", "") or "").strip()
        if not subsequence_id:
            raise ValidationError("Missing --subsequence-id (or provide --plan-in)")

    path = f"/subsequences/{subsequence_id}"
    plan = build_plan(
        tool=str(ctx.get("tool") or "instantly-api-tool"),
        version=str(ctx.get("tool_version") or ""),
        env_fingerprint=str(ctx["cfg"].base_url),
        command=str(ctx.get("command_str") or ""),
        selector={"kind": "subsequences.delete", "value": subsequence_id},
        risk_level="high",
        risk_reasons=["deletes-subsequence"],
        request={"method": "DELETE", "path": path, "body": {}},
        verification_plan={"type": "best-effort", "notes": "Best-effort: try GET subsequence after delete (should fail/404)."},
        baseline={"env_fingerprint": str(ctx["cfg"].base_url), "subsequence_id": subsequence_id},
    )

    plan_out = ctx.get("plan_out")
    plan_path = write_json_file(plan_out, sanitize(plan)) if (plan_out and not apply) else None

    if not apply:
        out = {"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path}
        ctx["audit"].write("subsequences.delete.plan", {"ok": True, "plan_out": plan_path})
        ctx["out"].emit(out)
        return 0

    client = _client(ctx)
    result = client.delete(path, json_body={}).data
    verify = None
    try:
        verify = client.get(path).data
    except Exception:  # noqa: BLE001
        verify = None

    receipt = {
        "tool": str(ctx.get("tool") or "instantly-api-tool"),
        "version": str(ctx.get("tool_version") or ""),
        "applied_at_utc": utc_now(),
        "env_fingerprint": str(ctx["cfg"].base_url),
        "command": str(ctx.get("command_str") or ""),
        "selector": plan.get("selector"),
        "changed": True,
        "verification": {"ok": verify is None, "details": {"type": "subsequences.get", "subsequence_id": subsequence_id}},
        "result": {"operation_result": sanitize(result), "subsequence_after": sanitize(verify)},
        "backups": [],
        "rollback_plan": None,
    }
    receipt_out = ctx.get("receipt_out")
    receipt_path = write_json_file(receipt_out, sanitize(receipt)) if receipt_out else None
    out = {"ok": True, "dry_run": False, "receipt": receipt, "receipt_out": receipt_path}
    ctx["audit"].write("subsequences.delete.apply", {"ok": True, "receipt_out": receipt_path})
    ctx["out"].emit(out)
    return 0


def cmd_subsequences_sending_status(args: Any, ctx: dict) -> int:
    subsequence_id = str(getattr(args, "subsequence_id", "") or "").strip()
    if not subsequence_id:
        raise ValidationError("Missing --subsequence-id")
    params: dict[str, Any] = {}
    if bool(getattr(args, "with_ai_summary", False)):
        params["with_ai_summary"] = True
    client = _client(ctx)
    res = client.get(f"/subsequences/{subsequence_id}/sending-status", params=params or None)
    ctx["audit"].write("subsequences.sending_status", {"ok": True})
    ctx["out"].emit({"ok": True, "sending_status": res.data})
    return 0


def cmd_subsequences_duplicate(args: Any, ctx: dict) -> int:
    subsequence_id = str(getattr(args, "subsequence_id", "") or "").strip()
    if not subsequence_id:
        raise ValidationError("Missing --subsequence-id")
    if bool(ctx.get("apply")) and not bool(ctx.get("yes")):
        raise SafetyError("Refused: subsequences duplicate requires --apply --yes")
    path = f"/subsequences/{subsequence_id}/duplicate"

    plan = build_plan(
        tool=str(ctx.get("tool") or "instantly-api-tool"),
        version=str(ctx.get("tool_version") or ""),
        env_fingerprint=str(ctx["cfg"].base_url),
        command=str(ctx.get("command_str") or ""),
        selector={"kind": "subsequences.duplicate", "value": subsequence_id},
        risk_level="high",
        risk_reasons=["duplicates-subsequence"],
        request={"method": "POST", "path": path, "body": {}},
        verification_plan={"type": "read-back", "notes": "Best-effort GET by returned subsequence id."},
        baseline={"env_fingerprint": str(ctx['cfg'].base_url), "subsequence_id": subsequence_id},
    )
    plan_out = ctx.get("plan_out")
    plan_path = write_json_file(plan_out, sanitize(plan)) if (plan_out and not bool(ctx.get("apply"))) else None

    if not bool(ctx.get("apply")):
        ctx["audit"].write("subsequences.duplicate.plan", {"ok": True, "plan_out": plan_path})
        ctx["out"].emit({"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path})
        return 0

    client = _client(ctx)
    result = client.post(path, json_body={}).data
    new_id = _extract_id(result)
    verify = None
    if new_id:
        try:
            verify = client.get(f"/subsequences/{new_id}").data
        except Exception:  # noqa: BLE001
            verify = None

    receipt = {
        "tool": str(ctx.get("tool") or "instantly-api-tool"),
        "version": str(ctx.get("tool_version") or ""),
        "applied_at_utc": utc_now(),
        "env_fingerprint": str(ctx["cfg"].base_url),
        "command": str(ctx.get("command_str") or ""),
        "selector": plan.get("selector"),
        "changed": True,
        "verification": {"ok": verify is not None, "details": {"type": "subsequences.get", "subsequence_id": new_id}},
        "result": {"operation_result": sanitize(result), "new_subsequence_id": new_id, "verified_subsequence": sanitize(verify)},
        "backups": [],
        "rollback_plan": None,
    }
    receipt_out = ctx.get("receipt_out")
    receipt_path = write_json_file(receipt_out, sanitize(receipt)) if receipt_out else None
    ctx["audit"].write("subsequences.duplicate.apply", {"ok": True, "receipt_out": receipt_path})
    ctx["out"].emit({"ok": True, "dry_run": False, "receipt": receipt, "receipt_out": receipt_path})
    return 0


def _pause_resume_common(args: Any, ctx: dict, *, op: str) -> int:
    if op not in {"pause", "resume"}:
        raise ValidationError("Invalid operation")
    subsequence_id = str(getattr(args, "subsequence_id", "") or "").strip()
    if not subsequence_id:
        raise ValidationError("Missing --subsequence-id")
    path = f"/subsequences/{subsequence_id}/{op}"

    plan = build_plan(
        tool=str(ctx.get("tool") or "instantly-api-tool"),
        version=str(ctx.get("tool_version") or ""),
        env_fingerprint=str(ctx["cfg"].base_url),
        command=str(ctx.get("command_str") or ""),
        selector={"kind": f"subsequences.{op}", "value": subsequence_id},
        risk_level="medium",
        risk_reasons=[f"subsequence-{op}"],
        request={"method": "POST", "path": path, "body": {}},
        verification_plan={"type": "read-back", "notes": "Best-effort GET subsequence after apply."},
        baseline={"env_fingerprint": str(ctx['cfg'].base_url), "subsequence_id": subsequence_id},
    )
    plan_out = ctx.get("plan_out")
    plan_path = write_json_file(plan_out, sanitize(plan)) if (plan_out and not bool(ctx.get("apply"))) else None

    if not bool(ctx.get("apply")):
        ctx["audit"].write(f"subsequences.{op}.plan", {"ok": True, "plan_out": plan_path})
        ctx["out"].emit({"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path})
        return 0

    client = _client(ctx)
    result = client.post(path, json_body={}).data
    verify = None
    try:
        verify = client.get(f"/subsequences/{subsequence_id}").data
    except Exception:  # noqa: BLE001
        verify = None

    receipt = {
        "tool": str(ctx.get("tool") or "instantly-api-tool"),
        "version": str(ctx.get("tool_version") or ""),
        "applied_at_utc": utc_now(),
        "env_fingerprint": str(ctx["cfg"].base_url),
        "command": str(ctx.get("command_str") or ""),
        "selector": plan.get("selector"),
        "changed": True,
        "verification": {"ok": verify is not None, "details": {"type": "subsequences.get", "subsequence_id": subsequence_id}},
        "result": {"operation_result": sanitize(result), "verified_subsequence": sanitize(verify)},
        "backups": [],
        "rollback_plan": None,
    }
    receipt_out = ctx.get("receipt_out")
    receipt_path = write_json_file(receipt_out, sanitize(receipt)) if receipt_out else None
    ctx["audit"].write(f"subsequences.{op}.apply", {"ok": True, "receipt_out": receipt_path})
    ctx["out"].emit({"ok": True, "dry_run": False, "receipt": receipt, "receipt_out": receipt_path})
    return 0


def cmd_subsequences_pause(args: Any, ctx: dict) -> int:
    return _pause_resume_common(args, ctx, op="pause")


def cmd_subsequences_resume(args: Any, ctx: dict) -> int:
    return _pause_resume_common(args, ctx, op="resume")
