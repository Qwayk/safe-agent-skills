from __future__ import annotations

import argparse
import hashlib
import re
import time
from pathlib import Path
from typing import Any
from typing import Type

from ..domains_list import chunk, parse_domains_from_args
from ..dynadot_api import DynadotApi
from ..errors import SafetyError, ValidationError
from ..http import HttpClient
from ..json_files import read_json_file, write_json_file
from ._write_safety import (
    build_before_state_refusal_verification_plan,
    build_no_recovery_contract,
    emit_before_state_refusal,
    ensure_before_state_refusal_plan,
)


def _utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _api(ctx: dict[str, Any]) -> DynadotApi:
    injected = ctx.get("api")
    if injected is not None:
        return injected  # type: ignore[return-value]
    cfg = ctx["cfg"]
    if not cfg.api_key:
        raise ValidationError("Missing DYNADOT_API_KEY")
    http = HttpClient(timeout_s=float(ctx["timeout_s"]), verbose=bool(ctx["verbose"]), user_agent="dynadot-api-tool")
    return DynadotApi(base_url=cfg.base_url, api_key=cfg.api_key, http=http)


def _validate_plan_for_apply(plan: dict[str, Any], *, baseline: dict[str, Any], ctx: dict[str, Any]) -> None:
    if str(plan.get("env_fingerprint") or "") != str(ctx["cfg"].base_url):
        raise SafetyError("Refused: plan env_fingerprint does not match current environment")
    b = plan.get("baseline")
    if not isinstance(b, dict):
        raise ValidationError("Plan missing baseline object")
    for k, v in baseline.items():
        if str(b.get(k) or "") != str(v or ""):
            raise SafetyError(f"Refused: plan baseline mismatch for {k}")


def _normalize_name_servers(items: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for raw in items:
        ns = str(raw or "").strip().lower().rstrip(".")
        if not ns:
            continue
        if ns in seen:
            continue
        seen.add(ns)
        out.append(ns)
    return sorted(out)


def _parse_name_servers_from_get_ns_response(payload: dict[str, Any]) -> list[str]:
    ns_content = payload.get("NsContent")
    if not isinstance(ns_content, dict):
        return []
    hosts: list[str] = []
    for i in range(0, 13):
        v = ns_content.get(f"Host{i}")
        if v is None:
            continue
        s = str(v).strip()
        if s:
            hosts.append(s)
    return _normalize_name_servers(hosts)


_NAMESERVER_HOST_RE = re.compile(
    r"^(?=.{1,253}$)([a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?)(\.[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?)+$"
)


def _normalize_desired_name_servers(items: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for raw in items:
        ns = str(raw or "").strip().lower().rstrip(".")
        if not ns:
            continue
        if not _NAMESERVER_HOST_RE.match(ns):
            raise ValidationError(f"Invalid name server hostname: {ns}")
        if ns in seen:
            continue
        seen.add(ns)
        out.append(ns)
    if not out:
        raise ValidationError("No desired name servers provided (use --desired-ns or --desired-ns-file)")
    if len(out) > 13:
        raise ValidationError("Dynadot supports up to 13 name servers (ns0-ns12)")
    return sorted(out)


def _parse_domains_from_domains_list_export(path: str) -> list[str]:
    obj = read_json_file(path)
    if not isinstance(obj, dict):
        raise ValidationError("Domains export must be a JSON object")
    domains_any = obj.get("domains")
    if not isinstance(domains_any, list):
        raise ValidationError("Domains export missing domains list")
    domains: list[str] = []
    for item in domains_any:
        if not isinstance(item, dict):
            continue
        name = item.get("Name")
        if name is None:
            continue
        domains.append(str(name))
    return parse_domains_from_args(domains=domains, domains_file=None)


def _sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk_bytes in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk_bytes)
    return h.hexdigest()


def _parse_resume_receipt_domains(
    path: str,
    *,
    expected_selector_kind: str,
    expected_selector_value: str | None,
    ctx: dict[str, Any],
) -> tuple[str, set[str]]:
    obj = read_json_file(path)
    if not isinstance(obj, dict):
        raise ValidationError("Resume receipt must be a JSON object")

    env_fp = obj.get("env_fingerprint")
    if env_fp is not None and str(env_fp or "") != str(ctx["cfg"].base_url):
        raise SafetyError("Refused: resume receipt env_fingerprint does not match current environment")

    sel_any = obj.get("selector")
    if not isinstance(sel_any, dict):
        raise ValidationError("Resume receipt missing selector object")
    if str(sel_any.get("kind") or "") != expected_selector_kind:
        raise ValidationError(f"Resume receipt selector kind mismatch (expected {expected_selector_kind})")
    if expected_selector_value is not None and str(sel_any.get("value") or "") != str(expected_selector_value):
        raise ValidationError("Resume receipt selector value mismatch")

    done: set[str] = set()
    diff_applied_any = obj.get("diff_applied")
    if isinstance(diff_applied_any, list):
        for row_any in diff_applied_any:
            if not isinstance(row_any, dict):
                continue
            d = str(row_any.get("domain") or "").strip().lower().rstrip(".")
            if d:
                done.add(d)

    if not done:
        results_any = obj.get("results")
        if isinstance(results_any, list):
            for row_any in results_any:
                if not isinstance(row_any, dict):
                    continue
                if row_any.get("ok") is not True:
                    continue
                domains_any = row_any.get("domains")
                if not isinstance(domains_any, list):
                    continue
                for d_any in domains_any:
                    d = str(d_any or "").strip().lower().rstrip(".")
                    if d:
                        done.add(d)

    return _sha256_file(path), done


def _parse_server_list_response(payload: dict[str, Any]) -> list[str]:
    # Official docs: ServerList is a list of {ServerName: "..."} objects.
    # Be tolerant of alternative shapes.
    candidates: list[Any] = []

    sl_any = payload.get("ServerList")
    if isinstance(sl_any, list):
        candidates = sl_any

    if not candidates:
        nsl_any = payload.get("NameServerList")
        if isinstance(nsl_any, dict):
            lst_any = nsl_any.get("List")
            if isinstance(lst_any, list):
                candidates = lst_any

    out: list[str] = []
    for item_any in candidates:
        if not isinstance(item_any, dict):
            continue
        name = item_any.get("ServerName")
        if name is None:
            continue
        s = str(name).strip().lower().rstrip(".")
        if s and s not in out:
            out.append(s)
    return sorted(out)


def cmd_domains_push(args: Any, ctx: dict[str, Any]) -> int:
    to_username = str(getattr(args, "to_username", "") or "").strip()
    if not to_username:
        raise ValidationError("Missing --to-username")

    unlock = not bool(getattr(args, "no_unlock", False))
    sleep_between_batches_s = float(getattr(args, "sleep_between_batches_s", 0.0) or 0.0)
    if sleep_between_batches_s < 0:
        raise ValidationError("--sleep-between-batches-s must be >= 0")
    max_batches_raw = getattr(args, "max_batches", None)
    max_batches = int(max_batches_raw) if max_batches_raw is not None else None
    if max_batches is not None and max_batches < 1:
        raise ValidationError("--max-batches must be >= 1")
    domains_in = parse_domains_from_args(domains=getattr(args, "domain", None), domains_file=getattr(args, "domains_file", None))
    original_count = len(domains_in)

    resume_from_receipt = str(getattr(args, "resume_from_receipt", "") or "").strip() or None
    resume_receipt_sha256 = ""
    done: set[str] = set()
    if resume_from_receipt:
        resume_receipt_sha256, done = _parse_resume_receipt_domains(
            resume_from_receipt,
            expected_selector_kind="domains.push",
            expected_selector_value=to_username,
            ctx=ctx,
        )

    domains = [d for d in domains_in if d not in done]
    skipped_already_done_count = original_count - len(domains)

    # Dynadot docs: up to 50 domains per push request, separated by semicolons.
    chunks = chunk(domains, 50)

    total_batches = len(chunks)
    planned_batches = min(total_batches, max_batches) if max_batches is not None else total_batches
    planned_domains = sum(len(chunks[i]) for i in range(0, planned_batches)) if planned_batches else 0
    preview = {
        "original_count": original_count,
        "skipped_already_done_count": skipped_already_done_count,
        "count": len(domains),
        "chunk_size": 50,
        "total_batches": total_batches,
        "sleep_between_batches_s": sleep_between_batches_s,
        "max_batches": max_batches,
        "planned_batches": planned_batches,
        "planned_domains": planned_domains,
    }

    baseline = {
        "to_username": to_username,
        "unlock_domain_for_push": "1" if unlock else "0",
        "domains_semicolon": ";".join(domains_in),
        "sleep_between_batches_s": str(sleep_between_batches_s),
        "max_batches": "" if max_batches is None else str(max_batches),
        "resume_receipt_sha256": resume_receipt_sha256,
    }

    plan_in = ctx.get("plan_in")
    if plan_in:
        plan_obj = read_json_file(plan_in)
        if not isinstance(plan_obj, dict):
            raise ValidationError("Plan file must be a JSON object")
        plan = plan_obj
        ensure_before_state_refusal_plan(
            plan,
            selector_kind="domains.push",
            selector_value=to_username,
            notes="Domain push has no reliable generic before-state snapshot here; apply requires explicit no-snapshot approval.",
        )
    else:
        recovery = build_no_recovery_contract(
            notes="Domain push stays proof-first only in this CLI. There is no built-in backup, snapshot restore, or direct undo path."
        )
        plan = {
            "tool": ctx.get("tool") or "dynadot-api-tool",
            "version": ctx.get("tool_version") or None,
            "generated_at_utc": _utc_now(),
            "env_fingerprint": ctx["cfg"].base_url,
            "command": ctx.get("command_str") or None,
            "selector": {"kind": "domains.push", "value": to_username},
            "risk_level": "high",
            "risk_reasons": ["domain-transfer", "bulk"] if len(domains) > 1 else ["domain-transfer"],
            "preconditions": ["env_fingerprint must match", "receiver username must be correct"],
            "baseline": baseline,
            "preview": preview,
            "proposed_changes": [{"domain": d} for d in domains],
            "post_apply_verification_plan": {
                "type": "api-response-only",
                "notes": "Dynadot push creates a push request. As the sender, we verify ResponseCode=0 per chunk.",
            },
            "verification_plan": build_before_state_refusal_verification_plan(),
            "rollback": {"supported": False, "notes": "Domain push is not safely auto-reversible."},
            "recovery": recovery,
        }
        ensure_before_state_refusal_plan(
            plan,
            selector_kind="domains.push",
            selector_value=to_username,
            notes="Domain push has no reliable generic before-state snapshot here; apply requires explicit no-snapshot approval.",
        )

    plan_out = ctx.get("plan_out")
    plan_path = write_json_file(plan_out, plan) if plan_out and not bool(ctx.get("apply")) else None

    if not bool(ctx.get("apply")):
        out = {
            "ok": True,
            "dry_run": True,
            "count": len(domains),
            "preview": preview,
            "plan": plan,
            "plan_out": plan_path,
        }
        ctx["audit"].write("domains.push.plan", {"count": len(domains), "plan_out": plan_path})
        ctx["out"].emit(out)
        return 0

    # High-risk safety rule: require a reviewed plan file for apply.
    if not plan_in:
        auto_plan_path = None
        try:
            ad = ctx.get("artifacts_dir")
            if ad:
                auto_plan_path = write_json_file(str(ad / "plan.json"), plan)  # type: ignore[operator]
        except Exception:
            auto_plan_path = None
        out = {
            "ok": True,
            "dry_run": False,
            "refused": True,
            "reasons": ["Refused: domains push apply requires a reviewed plan file (--plan-in). Run the dry-run first."],
            "refusal_type": "SafetyError",
            "plan": plan,
            "plan_out": auto_plan_path,
            "count": len(domains),
        }
        ctx["audit"].write("domains.push.refused", {"count": len(domains), "plan_out": auto_plan_path})
        ctx["out"].emit(out)
        return 0

    if not bool(ctx.get("yes")):
        raise SafetyError("Refused: pushing domains requires --apply --yes")

    _validate_plan_for_apply(
        plan,
        baseline=baseline,
        ctx=ctx,
    )
    if not bool(ctx.get("ack_no_snapshot")):
        return emit_before_state_refusal(
            ctx=ctx,
            plan=plan,
            audit_event="domains.push.refused",
            extra={"count": len(domains), "errors": 0},
        )

    api = _api(ctx)
    results: list[dict[str, Any]] = []
    errors = 0
    attempted_chunks: list[list[str]] = []
    for idx, c in enumerate(chunks, start=1):
        if max_batches is not None and idx > max_batches:
            break
        attempted_chunks.append(c)
        payload = {"domain": ";".join(c), "receiver_push_username": to_username}
        if unlock:
            payload["unlock_domain_for_push"] = "1"
        try:
            res = api.call(command="push", params=payload)
            results.append({"chunk": idx, "domains": c, "ok": True, "status": res.status, "response": res.response})
        except Exception as e:  # noqa: BLE001
            errors += 1
            results.append({"chunk": idx, "domains": c, "ok": False, "error": str(e)})
            break
        if sleep_between_batches_s > 0 and idx < len(chunks) and (max_batches is None or idx < max_batches):
            time.sleep(sleep_between_batches_s)

    applied_domains: list[str] = []
    for row in results:
        if row.get("ok") is True:
            applied_domains.extend(list(row.get("domains") or []))
    partial = errors == 0 and (len(attempted_chunks) < len(chunks))
    remaining_domains = domains[len(applied_domains) :]

    recovery = build_no_recovery_contract(
        notes="Domain push stays proof-first only in this CLI. There is no built-in backup, snapshot restore, or direct undo path."
    )
    receipt = {
        "tool": ctx.get("tool") or "dynadot-api-tool",
        "version": ctx.get("tool_version") or None,
        "applied_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "selector": {"kind": "domains.push", "value": to_username},
        "before_state": plan.get("before_state"),
        "no_snapshot_approval": {
            "acknowledged": True,
            "flag": "--ack-no-snapshot",
            "reason": "No reliable before-state snapshot is available for this Dynadot domain push.",
        },
        "changed": bool(domains) and errors == 0 and not partial,
        "partial": partial,
        "preview": preview,
        "verification": {
            "ok": errors == 0,
            "details": {
                "type": "api-response-only",
                "errors": errors,
                "partial": partial,
                "attempted_batches": len(attempted_chunks),
                "total_batches": len(chunks),
                "remaining_domains_count": len(remaining_domains),
            },
        },
        "diff_applied": [{"domain": d, "to_username": to_username} for d in applied_domains] if errors == 0 else [],
        "results": results,
        "backups": recovery["backups"],
        "rollback_plan": recovery["rollback_plan"],
        "recovery": recovery,
    }
    receipt_out = ctx.get("receipt_out")
    receipt_path = write_json_file(receipt_out, receipt) if receipt_out else None

    out = {
        "ok": errors == 0,
        "dry_run": False,
        "receipt": receipt,
        "receipt_out": receipt_path,
        "count": len(domains),
        "errors": errors,
        "partial": partial,
        "remaining_domains_count": len(remaining_domains),
    }
    ctx["audit"].write("domains.push.apply", {"count": len(domains), "errors": errors, "receipt_out": receipt_path})
    ctx["out"].emit(out)
    return 1 if errors else 0


def _parse_push_request_domains(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(x).strip().lower() for x in value if str(x).strip()]
    s = str(value).strip()
    if s.startswith("[") and s.endswith("]"):
        s = s[1:-1]
    out: list[str] = []
    # Docs show `pushDomainName` like: "[a.com,b.com]".
    # Be tolerant: accept commas or semicolons.
    s = s.replace(";", ",")
    for part in s.split(","):
        d = part.strip().strip('"').strip("'").strip().lower().rstrip(".")
        if d and d not in out:
            out.append(d)
    return out


def cmd_push_requests_list(args: Any, ctx: dict[str, Any]) -> int:
    _ = args
    api = _api(ctx)
    res = api.call(command="get_domain_push_request")

    domains = _parse_push_request_domains(res.response.get("pushDomainName"))
    out = {"ok": True, "dry_run": True, "count": len(domains), "domains": domains, "raw": res.response}
    ctx["audit"].write("domains.push_requests.list", {"count": len(domains)})
    ctx["out"].emit(out)
    return 0


def _cmd_push_requests_set(args: Any, ctx: dict[str, Any], *, action: str) -> int:
    act = str(action).strip().lower()
    if act not in {"accept", "decline"}:
        raise ValidationError("Internal error: action must be accept or decline")

    sleep_between_batches_s = float(getattr(args, "sleep_between_batches_s", 0.0) or 0.0)
    if sleep_between_batches_s < 0:
        raise ValidationError("--sleep-between-batches-s must be >= 0")
    max_batches_raw = getattr(args, "max_batches", None)
    max_batches = int(max_batches_raw) if max_batches_raw is not None else None
    if max_batches is not None and max_batches < 1:
        raise ValidationError("--max-batches must be >= 1")

    domains_in = parse_domains_from_args(domains=getattr(args, "domain", None), domains_file=getattr(args, "domains_file", None))
    original_count = len(domains_in)

    resume_from_receipt = str(getattr(args, "resume_from_receipt", "") or "").strip() or None
    resume_receipt_sha256 = ""
    done: set[str] = set()
    if resume_from_receipt:
        resume_receipt_sha256, done = _parse_resume_receipt_domains(
            resume_from_receipt,
            expected_selector_kind="domains.push-requests",
            expected_selector_value=act,
            ctx=ctx,
        )

    domains = [d for d in domains_in if d not in done]
    skipped_already_done_count = original_count - len(domains)

    chunks = chunk(domains, 50)

    total_batches = len(chunks)
    planned_batches = min(total_batches, max_batches) if max_batches is not None else total_batches
    planned_domains = sum(len(chunks[i]) for i in range(0, planned_batches)) if planned_batches else 0
    preview = {
        "original_count": original_count,
        "skipped_already_done_count": skipped_already_done_count,
        "count": len(domains),
        "chunk_size": 50,
        "total_batches": total_batches,
        "sleep_between_batches_s": sleep_between_batches_s,
        "max_batches": max_batches,
        "planned_batches": planned_batches,
        "planned_domains": planned_domains,
    }

    plan_in = ctx.get("plan_in")
    if plan_in:
        plan_obj = read_json_file(plan_in)
        if not isinstance(plan_obj, dict):
            raise ValidationError("Plan file must be a JSON object")
        plan = plan_obj
        ensure_before_state_refusal_plan(
            plan,
            selector_kind="domains.push-requests",
            selector_value=act,
            notes="Push-request accept/decline has no reliable generic before-state snapshot here; apply requires explicit no-snapshot approval.",
        )
    else:
        recovery = build_no_recovery_contract(
            notes="Push-request accept and decline flows stay proof-first only in this CLI. There is no built-in backup, snapshot restore, or direct undo path."
        )
        plan = {
            "tool": ctx.get("tool") or "dynadot-api-tool",
            "version": ctx.get("tool_version") or None,
            "generated_at_utc": _utc_now(),
            "env_fingerprint": ctx["cfg"].base_url,
            "command": ctx.get("command_str") or None,
            "selector": {"kind": "domains.push-requests", "value": act},
            "risk_level": "high",
            "risk_reasons": ["domain-transfer", "bulk"] if len(domains) > 1 else ["domain-transfer"],
            "preconditions": ["env_fingerprint must match", "domains must match intended push requests"],
            "baseline": {
                "action": act,
                "domains_comma": ",".join(domains_in),
                "sleep_between_batches_s": str(sleep_between_batches_s),
                "max_batches": "" if max_batches is None else str(max_batches),
                "resume_receipt_sha256": resume_receipt_sha256,
            },
            "preview": preview,
            "proposed_changes": [{"domain": d, "action": act} for d in domains],
            "post_apply_verification_plan": {
                "type": "read-back",
                "notes": "After accept/decline, re-check get_domain_push_request and confirm domains are no longer present.",
            },
            "verification_plan": build_before_state_refusal_verification_plan(),
            "rollback": {"supported": False, "notes": "Accepting/declining pushes is not safely auto-reversible."},
            "recovery": recovery,
        }
        ensure_before_state_refusal_plan(
            plan,
            selector_kind="domains.push-requests",
            selector_value=act,
            notes="Push-request accept/decline has no reliable generic before-state snapshot here; apply requires explicit no-snapshot approval.",
        )

    plan_out = ctx.get("plan_out")
    plan_path = write_json_file(plan_out, plan) if plan_out and not bool(ctx.get("apply")) else None

    if not bool(ctx.get("apply")):
        out = {
            "ok": True,
            "dry_run": True,
            "count": len(domains),
            "preview": preview,
            "plan": plan,
            "plan_out": plan_path,
        }
        ctx["audit"].write("domains.push_requests.plan", {"action": act, "count": len(domains), "plan_out": plan_path})
        ctx["out"].emit(out)
        return 0

    # High-risk safety rule: require a reviewed plan file for apply.
    if not plan_in:
        auto_plan_path = None
        try:
            ad = ctx.get("artifacts_dir")
            if ad:
                auto_plan_path = write_json_file(str(ad / "plan.json"), plan)  # type: ignore[operator]
        except Exception:
            auto_plan_path = None
        out = {
            "ok": True,
            "dry_run": False,
            "refused": True,
            "reasons": [
                "Refused: push-requests accept/decline apply requires a reviewed plan file (--plan-in). Run the dry-run first."
            ],
            "refusal_type": "SafetyError",
            "plan": plan,
            "plan_out": auto_plan_path,
            "count": len(domains),
        }
        ctx["audit"].write(
            "domains.push_requests.refused",
            {"action": act, "count": len(domains), "plan_out": auto_plan_path},
        )
        ctx["out"].emit(out)
        return 0

    if not bool(ctx.get("yes")):
        raise SafetyError("Refused: accepting/declining pushes requires --apply --yes")

    _validate_plan_for_apply(
        plan,
        baseline={
            "action": act,
            "domains_comma": ",".join(domains_in),
            "sleep_between_batches_s": str(sleep_between_batches_s),
            "max_batches": "" if max_batches is None else str(max_batches),
            "resume_receipt_sha256": resume_receipt_sha256,
        },
        ctx=ctx,
    )
    if not bool(ctx.get("ack_no_snapshot")):
        return emit_before_state_refusal(
            ctx=ctx,
            plan=plan,
            audit_event="domains.push_requests.refused",
            extra={"count": len(domains), "errors": 0},
        )

    api = _api(ctx)
    results: list[dict[str, Any]] = []
    errors = 0
    attempted_chunks: list[list[str]] = []
    for idx, c in enumerate(chunks, start=1):
        if max_batches is not None and idx > max_batches:
            break
        attempted_chunks.append(c)
        payload = {"domains": ",".join(c), "action": act}
        try:
            res = api.call(command="set_domain_push_request", params=payload)
            results.append({"chunk": idx, "domains": c, "ok": True, "status": res.status, "response": res.response})
        except Exception as e:  # noqa: BLE001
            errors += 1
            results.append({"chunk": idx, "domains": c, "ok": False, "error": str(e)})
            break
        if sleep_between_batches_s > 0 and idx < len(chunks) and (max_batches is None or idx < max_batches):
            time.sleep(sleep_between_batches_s)

    verify_ok = False
    remaining: list[str] = []
    try:
        after = api.call(command="get_domain_push_request")
        present = set(_parse_push_request_domains(after.response.get("pushDomainName")))
        remaining = [d for d in domains if d in present]
        partial = errors == 0 and (len(attempted_chunks) < len(chunks))
        verify_ok = errors == 0 and (len(remaining) == 0 or partial)
    except Exception:
        verify_ok = False
        partial = False

    applied_domains: list[str] = []
    for row in results:
        if row.get("ok") is True:
            applied_domains.extend(list(row.get("domains") or []))

    recovery = build_no_recovery_contract(
        notes="Push-request accept and decline flows stay proof-first only in this CLI. There is no built-in backup, snapshot restore, or direct undo path."
    )
    receipt = {
        "tool": ctx.get("tool") or "dynadot-api-tool",
        "version": ctx.get("tool_version") or None,
        "applied_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "selector": {"kind": "domains.push-requests", "value": act},
        "before_state": plan.get("before_state"),
        "no_snapshot_approval": {
            "acknowledged": True,
            "flag": "--ack-no-snapshot",
            "reason": "No reliable before-state snapshot is available for this Dynadot push-request write.",
        },
        "changed": bool(domains) and errors == 0 and not partial,
        "partial": partial,
        "preview": preview,
        "verification": {
            "ok": verify_ok,
            "details": {
                "type": "read-back",
                "remaining": remaining,
                "partial": partial,
                "attempted_batches": len(attempted_chunks),
                "total_batches": len(chunks),
            },
        },
        "diff_applied": [{"domain": d, "action": act} for d in applied_domains] if errors == 0 else [],
        "results": results,
        "backups": recovery["backups"],
        "rollback_plan": recovery["rollback_plan"],
        "recovery": recovery,
    }
    receipt_out = ctx.get("receipt_out")
    receipt_path = write_json_file(receipt_out, receipt) if receipt_out else None

    out = {
        "ok": errors == 0 and verify_ok,
        "dry_run": False,
        "receipt": receipt,
        "receipt_out": receipt_path,
        "count": len(domains),
        "errors": errors,
        "partial": partial,
    }
    ctx["audit"].write(
        "domains.push_requests.apply",
        {"action": act, "count": len(domains), "errors": errors, "verify_ok": verify_ok, "receipt_out": receipt_path},
    )
    ctx["out"].emit(out)
    return 1 if (errors or not verify_ok) else 0


def cmd_push_requests_accept(args: Any, ctx: dict[str, Any]) -> int:
    return _cmd_push_requests_set(args, ctx, action="accept")


def cmd_push_requests_decline(args: Any, ctx: dict[str, Any]) -> int:
    return _cmd_push_requests_set(args, ctx, action="decline")


def cmd_domains_name_servers_export(args: Any, ctx: dict[str, Any]) -> int:
    api = _api(ctx)
    sleep_s = float(getattr(args, "sleep_s", 0.0) or 0.0)
    if sleep_s < 0:
        raise ValidationError("--sleep-s must be >= 0")
    max_domains_raw = getattr(args, "max_domains", None)
    max_domains = int(max_domains_raw) if max_domains_raw is not None else None
    if max_domains is not None and max_domains < 1:
        raise ValidationError("--max-domains must be >= 1")
    out_path = str(getattr(args, "out", "") or "").strip() or None

    domains_any = getattr(args, "domain", None)
    domains_file = getattr(args, "domains_file", None)
    domains_export_in = str(getattr(args, "domains_export_in", "") or "").strip() or None
    if domains_export_in and (domains_file or domains_any):
        raise ValidationError("Provide only one source: --domains-export-in OR (--domains-file/--domain)")
    if domains_export_in:
        domains = _parse_domains_from_domains_list_export(domains_export_in)
    else:
        domains = parse_domains_from_args(domains=domains_any, domains_file=domains_file)

    if max_domains is not None and len(domains) > max_domains:
        raise SafetyError(f"Refused: domain set size {len(domains)} exceeds --max-domains {max_domains}")

    results: list[dict[str, Any]] = []
    errors = 0
    for idx, d in enumerate(domains):
        if idx and sleep_s > 0:
            time.sleep(sleep_s)
        try:
            res = api.call(command="get_ns", params={"domain": d})
            name_servers = _parse_name_servers_from_get_ns_response(res.response)
            results.append({"domain": d, "ok": True, "name_servers": name_servers, "response": res.response})
        except Exception as e:  # noqa: BLE001
            errors += 1
            results.append({"domain": d, "ok": False, "error": str(e)})

    export = {
        "tool": ctx.get("tool") or "dynadot-api-tool",
        "version": ctx.get("tool_version") or None,
        "generated_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": "get_ns",
        "adapter": {"kind": "domains.name_servers.export", "notes": "One get_ns call per domain; normalized output."},
        "params": {
            "domains_source": "domains_export_in" if domains_export_in else "domains_file",
            "domains_export_in": domains_export_in,
            "sleep_s": sleep_s,
            "max_domains": max_domains,
        },
        "count": len(domains),
        "errors": errors,
        "results": results,
    }
    export_written = write_json_file(out_path, export) if out_path else None
    out = {
        "ok": errors == 0,
        "dry_run": True,
        "command": "get_ns",
        "count": len(domains),
        "errors": errors,
        "out_path": export_written,
        "results": results if not export_written else None,
    }
    ctx["audit"].write(
        "domains.name_servers.export",
        {"count": len(domains), "errors": errors, "out_path": export_written},
    )
    ctx["out"].emit(out)
    return 1 if errors else 0


def _parse_name_server_export_for_diff(path: str) -> tuple[list[str], dict[str, list[str]]]:
    obj = read_json_file(path)
    if not isinstance(obj, dict):
        raise ValidationError("Name-server export must be a JSON object")
    results_any = obj.get("results")
    if not isinstance(results_any, list):
        raise ValidationError("Name-server export missing results list")
    domains: list[str] = []
    current_by_domain: dict[str, list[str]] = {}
    for row_any in results_any:
        if not isinstance(row_any, dict):
            continue
        domain = str(row_any.get("domain") or "").strip().lower().rstrip(".")
        if not domain:
            continue
        if row_any.get("ok") is not True:
            continue
        ns_any = row_any.get("name_servers")
        if ns_any is None:
            ns_any = row_any.get("nameservers")
        if isinstance(ns_any, list):
            ns = _normalize_name_servers([str(x) for x in ns_any])
        else:
            ns = []
        if domain not in current_by_domain:
            domains.append(domain)
        current_by_domain[domain] = ns
    if not domains:
        raise ValidationError("No successful domains found in name-server export")
    return domains, current_by_domain


def _parse_desired_name_servers_from_args(args: Any) -> list[str]:
    desired = getattr(args, "desired_ns", None)
    desired_file = str(getattr(args, "desired_ns_file", "") or "").strip() or None
    items: list[str] = []
    if desired:
        items.extend([str(x) for x in desired])
    if desired_file:
        try:
            raw = open(desired_file, "r", encoding="utf-8").read().splitlines()
        except FileNotFoundError:
            raise ValidationError(f"Desired name servers file not found: {desired_file}") from None
        for line in raw:
            s = line.strip()
            if not s or s.startswith("#"):
                continue
            items.append(s)
    return _normalize_desired_name_servers(items)


def cmd_domains_name_servers_diff(args: Any, ctx: dict[str, Any]) -> int:
    current_in = str(getattr(args, "current_in", "") or "").strip()
    if not current_in:
        raise ValidationError("Missing --current-in")
    out_path = str(getattr(args, "out", "") or "").strip() or None
    desired = _parse_desired_name_servers_from_args(args)

    domains, current_by_domain = _parse_name_server_export_for_diff(current_in)
    results: list[dict[str, Any]] = []
    changes: list[dict[str, Any]] = []
    unchanged = 0
    for d in domains:
        cur = current_by_domain.get(d, [])
        match = cur == desired
        results.append(
            {
                "domain": d,
                "current_name_servers": cur,
                "desired_name_servers": desired,
                "match": match,
                "will_change": not match,
            }
        )
        if match:
            unchanged += 1
        else:
            changes.append({"domain": d, "from": cur, "to": desired})

    export = {
        "tool": ctx.get("tool") or "dynadot-api-tool",
        "version": ctx.get("tool_version") or None,
        "generated_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": "diff_name_servers",
        "params": {"current_in": current_in, "desired_name_servers": desired},
        "count": len(domains),
        "unchanged": unchanged,
        "to_change": len(changes),
        "changes": changes,
        "results": results,
    }
    export_written = write_json_file(out_path, export) if out_path else None

    out = {
        "ok": True,
        "dry_run": True,
        "count": len(domains),
        "unchanged": unchanged,
        "to_change": len(changes),
        "out_path": export_written,
        "changes": changes if not export_written else None,
    }
    ctx["audit"].write(
        "domains.name_servers.diff",
        {"count": len(domains), "unchanged": unchanged, "to_change": len(changes), "out_path": export_written},
    )
    ctx["out"].emit(out)
    return 0


def _parse_name_servers_diff_for_set(path: str) -> tuple[list[str], list[str], str]:
    obj = read_json_file(path)
    if not isinstance(obj, dict):
        raise ValidationError("Diff file must be a JSON object")

    # Backward/forward compatible schema:
    # - Old diff schema (current): {"params": {"desired_name_servers": [...]}, "changes": [{"domain", "from", "to"}]}
    # - Newer schema variants may use: {"desired_nameservers": [...], "to_change": [{"domain", ...}]}
    desired_any = obj.get("desired_nameservers")
    if desired_any is None:
        desired_any = obj.get("desired_name_servers")
    if desired_any is None:
        params_any = obj.get("params")
        if isinstance(params_any, dict):
            desired_any = params_any.get("desired_name_servers")
    if not isinstance(desired_any, list):
        raise ValidationError("Diff file missing desired name servers list")
    desired = _normalize_desired_name_servers([str(x) for x in desired_any])

    to_change_any = obj.get("changes")
    if not isinstance(to_change_any, list):
        fallback_any = obj.get("to_change")
        if isinstance(fallback_any, list):
            to_change_any = fallback_any
    if not isinstance(to_change_any, list):
        raise ValidationError("Diff file missing changes list")

    domains: list[str] = []
    for item_any in to_change_any:
        if not isinstance(item_any, dict):
            continue
        d = str(item_any.get("domain") or "").strip().lower().rstrip(".")
        if not d:
            continue
        domains.append(d)
    if not domains:
        raise ValidationError("Diff file has no domains to change")
    digest = _sha256_file(path)
    return domains, desired, digest


def _build_name_server_availability_check(*, api, desired: list[str]) -> dict[str, Any]:
    res = api.call(command="server_list")
    available = _parse_server_list_response(res.response)
    missing = sorted(set(desired) - set(available))
    check: dict[str, Any] = {
        "source": "dynadot_server_list",
        "available_count": len(available),
        "missing": missing,
        "advisory_only": True,
    }
    if missing:
        check["warning"] = (
            "Some desired name servers are not listed in Dynadot server_list. "
            "External providers like Cloudflare can still work. Prefer warn mode plus read-back verification."
        )
    return check


def cmd_domains_name_servers_set(args: Any, ctx: dict[str, Any]) -> int:
    diff_in = str(getattr(args, "diff_in", "") or "").strip()
    if not diff_in:
        raise ValidationError("Missing --diff-in")

    sleep_between_batches_s = float(getattr(args, "sleep_between_batches_s", 0.0) or 0.0)
    if sleep_between_batches_s < 0:
        raise ValidationError("--sleep-between-batches-s must be >= 0")
    sleep_between_verifications_s = float(getattr(args, "sleep_between_verifications_s", 0.0) or 0.0)
    if sleep_between_verifications_s < 0:
        raise ValidationError("--sleep-between-verifications-s must be >= 0")
    max_batches_raw = getattr(args, "max_batches", None)
    max_batches = int(max_batches_raw) if max_batches_raw is not None else None
    if max_batches is not None and max_batches < 1:
        raise ValidationError("--max-batches must be >= 1")
    max_domains_raw = getattr(args, "max_domains", None)
    max_domains = int(max_domains_raw) if max_domains_raw is not None else None
    if max_domains is not None and max_domains < 1:
        raise ValidationError("--max-domains must be >= 1")
    continue_on_error = bool(getattr(args, "continue_on_error", False))

    domains_all, desired, diff_digest = _parse_name_servers_diff_for_set(diff_in)

    require_available_name_servers = bool(getattr(args, "require_available_name_servers", False))
    skip_availability_check = bool(getattr(args, "skip_availability_check", False))
    availability_check_mode = "skip" if skip_availability_check else ("require" if require_available_name_servers else "warn")

    resume_from_receipt = str(getattr(args, "resume_from_receipt", "") or "").strip() or None
    resume_receipt_sha256 = ""
    done: set[str] = set()
    if resume_from_receipt:
        resume_receipt_sha256, done = _parse_resume_receipt_domains(
            resume_from_receipt,
            expected_selector_kind="domains.name_servers.set",
            expected_selector_value=diff_digest,
            ctx=ctx,
        )

    domains_remaining = [d for d in domains_all if d not in done]
    skipped_already_done_count = len(domains_all) - len(domains_remaining)

    total_domains = len(domains_remaining)
    planned_domains = min(total_domains, max_domains) if max_domains is not None else total_domains
    domains = domains_remaining[:planned_domains]
    batches = chunk(domains, 100)
    total_batches = len(batches)
    planned_batches = min(total_batches, max_batches) if max_batches is not None else total_batches

    preview = {
        "diff_in": diff_in,
        "diff_sha256": diff_digest,
        "desired_name_servers": desired,
        "skipped_already_done_count": skipped_already_done_count,
        "count": total_domains,
        "planned_domains": planned_domains,
        "chunk_size": 100,
        "total_batches": total_batches,
        "sleep_between_batches_s": sleep_between_batches_s,
        "sleep_between_verifications_s": sleep_between_verifications_s,
        "max_batches": max_batches,
        "planned_batches": planned_batches,
        "continue_on_error": continue_on_error,
        "availability_check_mode": availability_check_mode,
    }

    baseline = {
        "diff_sha256": diff_digest,
        "desired_name_servers_comma": ",".join(desired),
        "domains_comma": ",".join(domains_all),
        "sleep_between_batches_s": str(sleep_between_batches_s),
        "sleep_between_verifications_s": "" if sleep_between_verifications_s == 0 else str(sleep_between_verifications_s),
        "max_batches": "" if max_batches is None else str(max_batches),
        "max_domains": "" if max_domains is None else str(max_domains),
        "continue_on_error": "1" if continue_on_error else "0",
        "availability_check_mode": "" if availability_check_mode == "warn" else availability_check_mode,
        "resume_receipt_sha256": resume_receipt_sha256,
    }

    plan_in = ctx.get("plan_in")
    if plan_in:
        plan_obj = read_json_file(plan_in)
        if not isinstance(plan_obj, dict):
            raise ValidationError("Plan file must be a JSON object")
        plan = plan_obj
        ensure_before_state_refusal_plan(
            plan,
            selector_kind="domains.name_servers.set",
            selector_value=diff_digest,
            notes="Name-server set has no reliable generic before-state snapshot here; apply requires explicit no-snapshot approval and read-back verification.",
        )
    else:
        preconditions = [
            "env_fingerprint must match",
            "diff_sha256 must match the reviewed diff file",
            "desired name servers must be correct",
        ]
        recovery = build_no_recovery_contract(
            notes="Name-server changes use read-back verification only. The related Dynadot snapshots in receipts are verification evidence, not restorable backups."
        )
        plan = {
            "tool": ctx.get("tool") or "dynadot-api-tool",
            "version": ctx.get("tool_version") or None,
            "generated_at_utc": _utc_now(),
            "env_fingerprint": ctx["cfg"].base_url,
            "command": ctx.get("command_str") or None,
            "selector": {"kind": "domains.name_servers.set", "value": diff_digest},
            "risk_level": "high",
            "risk_reasons": (["name-server-change", "bulk"] if total_domains > 1 else ["name-server-change"]),
            "preconditions": preconditions,
            "baseline": baseline,
            "preview": preview,
            "proposed_changes": [{"domain": d, "to_name_servers": desired} for d in domains_all],
            "post_apply_verification_plan": {
                "type": "read-back",
                "notes": "After set_ns, re-fetch get_ns for each domain and confirm it matches desired name servers.",
            },
            "verification_plan": build_before_state_refusal_verification_plan(),
            "rollback": {
                "supported": False,
                "notes": "Name server changes are not safely auto-reversible without a known previous state for each domain.",
            },
            "recovery": recovery,
        }
        ensure_before_state_refusal_plan(
            plan,
            selector_kind="domains.name_servers.set",
            selector_value=diff_digest,
            notes="Name-server set has no reliable generic before-state snapshot here; apply requires explicit no-snapshot approval and read-back verification.",
        )

    plan_out = ctx.get("plan_out")
    plan_path = write_json_file(plan_out, plan) if plan_out and not bool(ctx.get("apply")) else None

    if not bool(ctx.get("apply")):
        availability_check = None
        if availability_check_mode != "skip":
            api = _api(ctx)
            availability_check = _build_name_server_availability_check(api=api, desired=desired)
        out = {
            "ok": True,
            "dry_run": True,
            "count": total_domains,
            "preview": preview,
            "availability_check": availability_check,
            "plan": plan,
            "plan_out": plan_path,
        }
        ctx["audit"].write(
            "domains.name_servers.set.plan",
            {"count": total_domains, "planned_domains": planned_domains, "plan_out": plan_path},
        )
        ctx["out"].emit(out)
        return 0

    # High-risk safety rule: require a reviewed plan file for apply.
    if not plan_in:
        auto_plan_path = None
        try:
            ad = ctx.get("artifacts_dir")
            if ad:
                auto_plan_path = write_json_file(str(ad / "plan.json"), plan)  # type: ignore[operator]
        except Exception:
            auto_plan_path = None
        out = {
            "ok": True,
            "dry_run": False,
            "refused": True,
            "reasons": [
                "Refused: set name servers apply requires a reviewed plan file (--plan-in). Run the dry-run first."
            ],
            "refusal_type": "SafetyError",
            "plan": plan,
            "plan_out": auto_plan_path,
            "count": total_domains,
        }
        ctx["audit"].write("domains.name_servers.set.refused", {"count": total_domains, "plan_out": auto_plan_path})
        ctx["out"].emit(out)
        return 0

    if not bool(ctx.get("yes")):
        raise SafetyError("Refused: setting name servers requires --apply --yes")

    _validate_plan_for_apply(plan, baseline=baseline, ctx=ctx)
    if not bool(ctx.get("ack_no_snapshot")):
        return emit_before_state_refusal(
            ctx=ctx,
            plan=plan,
            audit_event="domains.name_servers.set.refused",
            extra={"count": total_domains, "errors": 0},
        )

    api = _api(ctx)
    availability_check = None
    if availability_check_mode != "skip":
        availability_check = _build_name_server_availability_check(api=api, desired=desired)
        missing = list(availability_check.get("missing") or [])
        if availability_check_mode == "require" and missing:
            out = {
                "ok": True,
                "dry_run": False,
                "refused": True,
                "reasons": [
                    "Refused: desired name servers are not listed in Dynadot server_list for this account. "
                    "For external providers like Cloudflare, use the default warn mode plus read-back verification."
                ],
                "refusal_type": "SafetyError",
                "availability_check": availability_check,
                "plan": plan,
                "count": total_domains,
            }
            ctx["audit"].write(
                "domains.name_servers.set.refused",
                {"count": total_domains, "missing": missing},
            )
            ctx["out"].emit(out)
            return 0
    results: list[dict[str, Any]] = []
    errors = 0
    attempted_batches: list[list[str]] = []
    verified: dict[str, bool] = {}
    mismatches: list[dict[str, Any]] = []
    interrupted = False
    verification_sleep_count = 0

    ns_params: dict[str, Any] = {}
    for idx, ns in enumerate(desired):
        ns_params[f"ns{idx}"] = ns

    try:
        for idx, batch_domains in enumerate(batches, start=1):
            if max_batches is not None and idx > max_batches:
                break
            attempted_batches.append(batch_domains)
            payload = {"domain": ",".join(batch_domains)} | ns_params
            try:
                res = api.call(command="set_ns", params=payload)
                results.append({"batch": idx, "domains": batch_domains, "ok": True, "status": res.status, "response": res.response})
            except Exception as e:  # noqa: BLE001
                errors += 1
                results.append({"batch": idx, "domains": batch_domains, "ok": False, "error": str(e)})
                if continue_on_error and len(batch_domains) > 1:
                    for d in batch_domains:
                        try:
                            res1 = api.call(command="set_ns", params=({"domain": d} | ns_params))
                            results.append({"batch": idx, "domains": [d], "ok": True, "status": res1.status, "response": res1.response})
                        except Exception as e1:  # noqa: BLE001
                            errors += 1
                            results.append({"batch": idx, "domains": [d], "ok": False, "error": str(e1)})
                            if not continue_on_error:
                                break
                if not continue_on_error:
                    break

            for d in batch_domains:
                try:
                    if sleep_between_verifications_s > 0 and verification_sleep_count > 0:
                        time.sleep(sleep_between_verifications_s)
                    verification_sleep_count += 1
                    after = api.call(command="get_ns", params={"domain": d})
                    cur = _parse_name_servers_from_get_ns_response(after.response)
                    ok = set(cur) == set(desired)
                    verified[d] = ok
                    if not ok:
                        mismatches.append({"domain": d, "current": cur, "desired": desired})
                except Exception as ve:  # noqa: BLE001
                    verified[d] = False
                    errors += 1
                    results.append({"domain": d, "verification_ok": False, "verification_error": str(ve)})
                    if not continue_on_error:
                        break
            if errors and not continue_on_error:
                break

            if sleep_between_batches_s > 0 and idx < len(batches) and (max_batches is None or idx < max_batches):
                time.sleep(sleep_between_batches_s)
    except KeyboardInterrupt:
        interrupted = True

    attempted_domains = [d for batch_domains in attempted_batches for d in batch_domains]
    remaining_domains = domains_remaining[len(attempted_domains) :]
    partial_due_to_limits = (planned_domains < total_domains) or (planned_batches < total_batches)
    partial = interrupted or partial_due_to_limits or (errors > 0)

    verify_ok = all(verified.get(d, False) for d in attempted_domains) if attempted_domains else (total_domains == 0)
    recovery = build_no_recovery_contract(
        notes="Name-server changes use read-back verification only. The related Dynadot snapshots in receipts are verification evidence, not restorable backups."
    )
    receipt = {
        "tool": ctx.get("tool") or "dynadot-api-tool",
        "version": ctx.get("tool_version") or None,
        "applied_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "selector": {"kind": "domains.name_servers.set", "value": diff_digest},
        "before_state": plan.get("before_state"),
        "no_snapshot_approval": {
            "acknowledged": True,
            "flag": "--ack-no-snapshot",
            "reason": "No reliable before-state snapshot is available for this Dynadot name-server write.",
        },
        "changed": bool(attempted_domains) and errors == 0 and verify_ok and not partial,
        "partial": partial,
        "interrupted": interrupted,
        "preview": preview,
        "availability_check": availability_check,
        "verification": {
            "ok": errors == 0 and verify_ok,
            "details": {
                "type": "read-back",
                "verified": verified,
                "mismatches": mismatches,
                "attempted_batches": len(attempted_batches),
                "total_batches": total_batches,
                "remaining_domains_count": len(remaining_domains),
            },
        },
        "diff_applied": [{"domain": d, "to_name_servers": desired} for d in attempted_domains if verified.get(d) is True],
        "results": results,
        "errors": errors,
        "backups": recovery["backups"],
        "rollback_plan": recovery["rollback_plan"],
        "recovery": recovery,
    }
    receipt_out = ctx.get("receipt_out")
    receipt_path = write_json_file(receipt_out, receipt) if receipt_out else None

    out = {
        "ok": errors == 0 and verify_ok,
        "dry_run": False,
        "receipt": receipt,
        "receipt_out": receipt_path,
        "count": total_domains,
        "errors": errors,
        "partial": partial,
        "remaining_domains_count": len(remaining_domains),
    }
    ctx["audit"].write(
        "domains.name_servers.set.apply",
        {
            "count": total_domains,
            "errors": errors,
            "verify_ok": verify_ok,
            "partial": partial,
            "receipt_out": receipt_path,
        },
    )
    ctx["out"].emit(out)
    if interrupted:
        return 130
    return 1 if (errors or not verify_ok) else 0


def _extract_list_domain_records(payload: dict[str, Any]) -> list[dict[str, Any]]:
    for key in ("MainDomains", "Domains", "DomainInfoList", "DomainInfo", "DomainList"):
        v = payload.get(key)
        if isinstance(v, list):
            return [x for x in v if isinstance(x, dict)]
        if isinstance(v, dict):
            # Some shapes might wrap lists under a dict.
            for inner_key in ("Domains", "MainDomains", "DomainInfo", "DomainInfoList", "DomainList"):
                inner = v.get(inner_key)
                if isinstance(inner, list):
                    return [x for x in inner if isinstance(x, dict)]
    return []


def cmd_domains_list(args: Any, ctx: dict[str, Any]) -> int:
    api = _api(ctx)
    start_page = int(getattr(args, "page", 1) or 1)
    if start_page < 1:
        raise ValidationError("--page must be >= 1")
    page_size_raw = getattr(args, "page_size", None)
    page_size = int(page_size_raw) if page_size_raw is not None else None
    if page_size is not None and page_size < 1:
        raise ValidationError("--page-size must be >= 1")

    all_pages = bool(getattr(args, "all", False))
    max_pages = int(getattr(args, "max_pages", 50) or 50)
    if max_pages < 1:
        raise ValidationError("--max-pages must be >= 1")
    sleep_s = float(getattr(args, "sleep_s", 0.0) or 0.0)
    if sleep_s < 0:
        raise ValidationError("--sleep-s must be >= 0")
    out_path = str(getattr(args, "out", "") or "").strip() or None

    pages: list[dict[str, Any]] = []
    combined: list[dict[str, Any]] = []
    stopped_reason = "single_page"

    total_attempted = 0
    for offset in range(0, (max_pages if all_pages else 1)):
        page_index = start_page + offset
        total_attempted += 1
        params: dict[str, Any] = {"page_index": page_index}
        if page_size is not None:
            params["count_per_page"] = page_size
        res = api.call(command="list_domain", params=params)
        records = _extract_list_domain_records(res.response)
        pages.append(
            {
                "page_index": page_index,
                "count": len(records),
                "response": res.response,
            }
        )
        combined.extend(records)
        if all_pages:
            if len(records) == 0:
                stopped_reason = "empty_page"
                break
            if offset + 1 >= max_pages:
                stopped_reason = "max_pages"
                break
            if sleep_s > 0:
                time.sleep(sleep_s)

    export = {
        "tool": ctx.get("tool") or "dynadot-api-tool",
        "version": ctx.get("tool_version") or None,
        "generated_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": "list_domain",
        "params": {
            "page_index": start_page,
            "count_per_page": page_size,
            "all": all_pages,
            "max_pages": max_pages,
            "sleep_s": sleep_s,
        },
        "paging": {"attempted_pages": total_attempted, "stopped_reason": stopped_reason},
        "count": len(combined),
        "pages": pages,
        "domains": combined,
    }

    export_written = write_json_file(out_path, export) if out_path else None
    out = {
        "ok": True,
        "dry_run": True,
        "command": "list_domain",
        "count": len(combined),
        "page": start_page,
        "page_size": page_size,
        "all": all_pages,
        "max_pages": max_pages if all_pages else 1,
        "attempted_pages": total_attempted,
        "stopped_reason": stopped_reason,
        "out_path": export_written,
    }
    ctx["audit"].write("domains.list", {"count": len(combined), "attempted_pages": total_attempted, "out_path": export_written})
    ctx["out"].emit(out)
    return 0


def cmd_domains_search(args: Any, ctx: dict[str, Any]) -> int:
    api = _api(ctx)
    domains_any = getattr(args, "domain", None)
    domains_raw = domains_any if isinstance(domains_any, list) else []
    domains: list[str] = []
    for d_any in domains_raw:
        d = str(d_any or "").strip().lower().rstrip(".")
        if d:
            domains.append(d)

    if not domains:
        raise ValidationError("Missing --domain (provide at least 1)")
    if len(domains) > 100:
        raise ValidationError("--domain max is 100 domains per request")

    show_price = bool(getattr(args, "show_price", False))
    currency = str(getattr(args, "currency", "") or "").strip().upper() or None
    if currency is not None and currency not in {"USD", "EUR", "CNY"}:
        raise ValidationError("--currency must be one of: USD, EUR, CNY")
    if currency is not None and not show_price:
        raise ValidationError("--currency requires --show-price")

    params: dict[str, Any] = {}
    for idx, d in enumerate(domains):
        params[f"domain{idx}"] = d
    if show_price:
        params["show_price"] = "1"
        if currency is not None:
            params["currency"] = currency.lower()

    res = api.call(command="search", params=params)

    out_path = str(getattr(args, "out", "") or "").strip() or None
    export = {
        "tool": ctx.get("tool") or "dynadot-api-tool",
        "version": ctx.get("tool_version") or None,
        "generated_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": "search",
        "params": {
            "count": len(domains),
            "show_price": show_price,
            "currency": currency,
        },
        "domains": domains,
        "response": res.response,
    }
    export_written = write_json_file(out_path, export) if out_path else None

    out = {
        "ok": True,
        "dry_run": True,
        "command": "search",
        "count": len(domains),
        "show_price": show_price,
        "currency": currency,
        "out_path": export_written,
        "dynadot": {
            "command": "search",
            "status": res.status,
            "response_code": res.response_code,
            "raw": res.response,
        },
    }
    ctx["audit"].write("domains.search", {"count": len(domains), "show_price": show_price, "currency": currency, "out_path": export_written})
    ctx["out"].emit(out)
    return 0


def _domain_info_from_response(payload: dict[str, Any]) -> dict[str, Any] | None:
    for key in ("DomainInfo", "Domain", "domain", "domainInfo"):
        v = payload.get(key)
        if isinstance(v, dict):
            return v
    return None


def cmd_domains_info(args: Any, ctx: dict[str, Any]) -> int:
    api = _api(ctx)
    sleep_s = float(getattr(args, "sleep_s", 0.0) or 0.0)
    if sleep_s < 0:
        raise ValidationError("--sleep-s must be >= 0")
    max_domains_raw = getattr(args, "max_domains", None)
    max_domains = int(max_domains_raw) if max_domains_raw is not None else None
    if max_domains is not None and max_domains < 1:
        raise ValidationError("--max-domains must be >= 1")
    out_path = str(getattr(args, "out", "") or "").strip() or None

    domains = parse_domains_from_args(domains=getattr(args, "domain", None), domains_file=getattr(args, "domains_file", None))
    if max_domains is not None and len(domains) > max_domains:
        raise SafetyError(f"Refused: domain set size {len(domains)} exceeds --max-domains {max_domains}")

    results: list[dict[str, Any]] = []
    errors = 0
    for idx, d in enumerate(domains):
        if idx and sleep_s > 0:
            time.sleep(sleep_s)
        try:
            res = api.call(command="domain_info", params={"domain": d})
            results.append({"domain": d, "ok": True, "response": res.response, "domain_info": _domain_info_from_response(res.response)})
        except Exception as e:  # noqa: BLE001
            errors += 1
            results.append({"domain": d, "ok": False, "error": str(e)})

    export = {
        "tool": ctx.get("tool") or "dynadot-api-tool",
        "version": ctx.get("tool_version") or None,
        "generated_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": "domain_info",
        "params": {"sleep_s": sleep_s, "max_domains": max_domains},
        "count": len(domains),
        "errors": errors,
        "results": results,
    }
    export_written = write_json_file(out_path, export) if out_path else None
    out = {
        "ok": errors == 0,
        "dry_run": True,
        "command": "domain_info",
        "count": len(domains),
        "errors": errors,
        "out_path": export_written,
        "results": results if not export_written else None,
    }
    ctx["audit"].write("domains.info", {"count": len(domains), "errors": errors, "out_path": export_written})
    ctx["out"].emit(out)
    return 1 if errors else 0


def cmd_domains_status(args: Any, ctx: dict[str, Any]) -> int:
    api = _api(ctx)
    sleep_s = float(getattr(args, "sleep_s", 0.0) or 0.0)
    if sleep_s < 0:
        raise ValidationError("--sleep-s must be >= 0")
    max_domains_raw = getattr(args, "max_domains", None)
    max_domains = int(max_domains_raw) if max_domains_raw is not None else None
    if max_domains is not None and max_domains < 1:
        raise ValidationError("--max-domains must be >= 1")
    out_path = str(getattr(args, "out", "") or "").strip() or None

    domains = parse_domains_from_args(domains=getattr(args, "domain", None), domains_file=getattr(args, "domains_file", None))
    if max_domains is not None and len(domains) > max_domains:
        raise SafetyError(f"Refused: domain set size {len(domains)} exceeds --max-domains {max_domains}")

    results: list[dict[str, Any]] = []
    errors = 0
    for idx, d in enumerate(domains):
        if idx and sleep_s > 0:
            time.sleep(sleep_s)
        try:
            res = api.call(command="domain_info", params={"domain": d})
            di = _domain_info_from_response(res.response) or {}
            status = di.get("Status")
            results.append({"domain": d, "ok": True, "status": status, "domain_info": di})
        except Exception as e:  # noqa: BLE001
            errors += 1
            results.append({"domain": d, "ok": False, "error": str(e)})

    export = {
        "tool": ctx.get("tool") or "dynadot-api-tool",
        "version": ctx.get("tool_version") or None,
        "generated_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": "domain_info",
        "adapter": {"kind": "domains.status", "notes": "Derived from domain_info.DomainInfo.Status (Dynadot API docs do not list a separate domain status command)."},
        "params": {"sleep_s": sleep_s, "max_domains": max_domains},
        "count": len(domains),
        "errors": errors,
        "results": results,
    }
    export_written = write_json_file(out_path, export) if out_path else None
    out = {
        "ok": errors == 0,
        "dry_run": True,
        "command": "domains.status",
        "count": len(domains),
        "errors": errors,
        "out_path": export_written,
        "results": results if not export_written else None,
    }
    ctx["audit"].write("domains.status", {"count": len(domains), "errors": errors, "out_path": export_written})
    ctx["out"].emit(out)
    return 1 if errors else 0


def cmd_domains_folders_list(args: Any, ctx: dict[str, Any]) -> int:
    _ = args
    api = _api(ctx)
    out_path = str(getattr(args, "out", "") or "").strip() or None
    res = api.call(command="folder_list")
    folder_list = res.response.get("FolderList")
    folders = folder_list if isinstance(folder_list, list) else []
    export = {
        "tool": ctx.get("tool") or "dynadot-api-tool",
        "version": ctx.get("tool_version") or None,
        "generated_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": "folder_list",
        "count": len(folders),
        "folders": folders,
        "response": res.response,
    }
    export_written = write_json_file(out_path, export) if out_path else None
    out = {
        "ok": True,
        "dry_run": True,
        "command": "folder_list",
        "count": len(folders),
        "out_path": export_written,
        "folders": folders if not export_written else None,
    }
    ctx["audit"].write("domains.folders.list", {"count": len(folders), "out_path": export_written})
    ctx["out"].emit(out)
    return 0


def register_domains(
    subparsers: argparse._SubParsersAction,  # type: ignore[name-defined]
    *,
    parser_class: Type[argparse.ArgumentParser],
) -> None:
    domains = subparsers.add_parser("domains", help="Domain workflows (inventory, name servers, push, push requests)")
    domains_sub = domains.add_subparsers(dest="domains_cmd", required=True, parser_class=parser_class)

    ns = domains_sub.add_parser("name-servers", help="Name server audit + bulk set (safe)")
    ns_sub = ns.add_subparsers(dest="name_servers_cmd", required=True, parser_class=parser_class)

    ns_export = ns_sub.add_parser("export", help="Export current name servers per domain (read-only)")
    ns_export.add_argument("--domains-file", default=None, help="File with one domain per line")
    ns_export.add_argument(
        "--domains-export-in",
        dest="domains_export_in",
        default=None,
        help="Input domains list export JSON from domains list --out ...",
    )
    ns_export.add_argument("--sleep-s", type=float, default=0.0, help="Sleep seconds between domains (default: 0)")
    ns_export.add_argument("--max-domains", type=int, default=None, help="Safety cap on input domain count")
    ns_export.add_argument("--out", default=None, help="Write full JSON export to a file")
    ns_export.set_defaults(func=cmd_domains_name_servers_export, write_capable=False)

    ns_diff = ns_sub.add_parser("diff", help="Diff current name servers vs desired (read-only)")
    ns_diff.add_argument("--current-in", dest="current_in", required=True, help="Input export JSON from domains name-servers export")
    ns_diff.add_argument("--desired-ns", dest="desired_ns", action="append", default=None, help="Desired name server (repeatable)")
    ns_diff.add_argument("--desired-ns-file", dest="desired_ns_file", default=None, help="File with one name server per line")
    ns_diff.add_argument("--out", default=None, help="Write full diff JSON to a file")
    ns_diff.set_defaults(func=cmd_domains_name_servers_diff, write_capable=False)

    ns_set = ns_sub.add_parser("set", help="Bulk set name servers from a diff file (preview-first)")
    ns_set.add_argument("--diff-in", dest="diff_in", required=True, help="Diff JSON from domains name-servers diff --out ...")
    ns_set.add_argument("--sleep-between-batches-s", type=float, default=0.0, help="Sleep seconds between API batches during apply (default: 0)")
    ns_set.add_argument(
        "--sleep-between-verifications-s",
        type=float,
        default=0.0,
        help="Sleep seconds between per-domain verification reads (get_ns) during apply (default: 0)",
    )
    ns_set.add_argument("--max-batches", type=int, default=None, help="Limit number of 100-domain batches attempted during apply (partial completion)")
    ns_set.add_argument("--max-domains", type=int, default=None, help="Limit number of domains applied (partial completion)")
    ns_set.add_argument("--continue-on-error", action="store_true", help="Continue after an error (default is stop-on-first-error)")
    ns_set.add_argument(
        "--resume-from-receipt",
        dest="resume_from_receipt",
        default=None,
        help="Resume from a previous name-servers set receipt (skips already verified domains)",
    )
    ns_set.add_argument(
        "--skip-availability-check",
        dest="skip_availability_check",
        action="store_true",
        help="Skip the name-server availability check (default is to warn if servers are missing)",
    )
    ns_set.add_argument(
        "--require-available-name-servers",
        dest="require_available_name_servers",
        action="store_true",
        help="Refuse apply if the desired name servers are not available in this Dynadot account",
    )
    ns_set.set_defaults(func=cmd_domains_name_servers_set, write_capable=True)

    domains_list = domains_sub.add_parser("list", help="List domains (read-only)")
    domains_list.add_argument("--page", type=int, default=1, help="Page index (default: 1)")
    domains_list.add_argument("--page-size", type=int, default=None, help="Entities per page (default: API default)")
    domains_list.add_argument("--all", action="store_true", help="Fetch multiple pages until empty page (uses --max-pages)")
    domains_list.add_argument("--max-pages", type=int, default=50, help="Safety cap for --all (default: 50)")
    domains_list.add_argument("--sleep-s", type=float, default=0.0, help="Sleep seconds between pages (default: 0)")
    domains_list.add_argument("--out", default=None, help="Write full JSON export to a file")
    domains_list.set_defaults(func=cmd_domains_list, write_capable=False)

    domains_search = domains_sub.add_parser("search", help="Search domain availability (read-only)")
    domains_search.add_argument("--domain", action="append", default=None, help="One domain (repeatable; max 100)")
    domains_search.add_argument("--show-price", dest="show_price", action="store_true", help="Include prices in search results")
    domains_search.add_argument("--currency", default=None, choices=("USD", "EUR", "CNY"), help="Currency (requires --show-price)")
    domains_search.add_argument("--out", default=None, help="Write full JSON export to a file")
    domains_search.set_defaults(func=cmd_domains_search, write_capable=False)

    domains_info = domains_sub.add_parser("info", help="Get domain info (read-only; one request per domain)")
    domains_info.add_argument("--domain", action="append", default=None, help="One domain (repeatable)")
    domains_info.add_argument("--domains-file", default=None, help="File with one domain per line")
    domains_info.add_argument("--sleep-s", type=float, default=0.0, help="Sleep seconds between domains (default: 0)")
    domains_info.add_argument("--max-domains", type=int, default=None, help="Safety cap on input domain count")
    domains_info.add_argument("--out", default=None, help="Write full JSON export to a file")
    domains_info.set_defaults(func=cmd_domains_info, write_capable=False)

    domains_status = domains_sub.add_parser("status", help="Get domain status (read-only; derived from domain_info)")
    domains_status.add_argument("--domain", action="append", default=None, help="One domain (repeatable)")
    domains_status.add_argument("--domains-file", default=None, help="File with one domain per line")
    domains_status.add_argument("--sleep-s", type=float, default=0.0, help="Sleep seconds between domains (default: 0)")
    domains_status.add_argument("--max-domains", type=int, default=None, help="Safety cap on input domain count")
    domains_status.add_argument("--out", default=None, help="Write full JSON export to a file")
    domains_status.set_defaults(func=cmd_domains_status, write_capable=False)

    folders = domains_sub.add_parser("folders", help="Folder/group reads (read-only)")
    folders_sub = folders.add_subparsers(dest="folders_cmd", required=True, parser_class=parser_class)
    folders_list = folders_sub.add_parser("list", help="List folders (read-only)")
    folders_list.add_argument("--out", default=None, help="Write full JSON export to a file")
    folders_list.set_defaults(func=cmd_domains_folders_list, write_capable=False)

    domains_push = domains_sub.add_parser("push", help="Push domains to another Dynadot account (sender side)")
    domains_push.add_argument(
        "--to-push-username",
        "--to-username",
        dest="to_username",
        required=True,
        help="Receiver Push Username (not their login username)",
    )
    domains_push.add_argument("--domain", action="append", default=None, help="One domain (repeatable)")
    domains_push.add_argument("--domains-file", default=None, help="File with one domain per line")
    domains_push.add_argument(
        "--no-unlock",
        action="store_true",
        help="Do not set unlock_domain_for_push=1 (default is to unlock for push)",
    )
    domains_push.add_argument(
        "--sleep-between-batches-s",
        type=float,
        default=0.0,
        help="Sleep seconds between API batches during apply (default: 0)",
    )
    domains_push.add_argument(
        "--max-batches",
        type=int,
        default=None,
        help="Limit number of 50-domain batches attempted during apply (partial completion)",
    )
    domains_push.add_argument(
        "--resume-from-receipt",
        dest="resume_from_receipt",
        default=None,
        help="Resume from a previous domains push receipt (skips already pushed domains)",
    )
    domains_push.set_defaults(func=cmd_domains_push, write_capable=True)

    pr = domains_sub.add_parser("push-requests", help="Incoming domain push requests (receiver side)")
    pr_sub = pr.add_subparsers(dest="push_requests_cmd", required=True, parser_class=parser_class)
    pr_list = pr_sub.add_parser("list", help="List incoming push requests")
    pr_list.set_defaults(func=cmd_push_requests_list, write_capable=False)
    pr_accept = pr_sub.add_parser("accept", help="Accept push requests for specific domains")
    pr_accept.add_argument("--domain", action="append", default=None, help="One domain (repeatable)")
    pr_accept.add_argument("--domains-file", default=None, help="File with one domain per line")
    pr_accept.add_argument(
        "--sleep-between-batches-s",
        type=float,
        default=0.0,
        help="Sleep seconds between API batches during apply (default: 0)",
    )
    pr_accept.add_argument(
        "--max-batches",
        type=int,
        default=None,
        help="Limit number of 50-domain batches attempted during apply (partial completion)",
    )
    pr_accept.add_argument(
        "--resume-from-receipt",
        dest="resume_from_receipt",
        default=None,
        help="Resume from a previous push-requests receipt (skips already accepted domains)",
    )
    pr_accept.set_defaults(func=cmd_push_requests_accept, write_capable=True)
    pr_decline = pr_sub.add_parser("decline", help="Decline push requests for specific domains")
    pr_decline.add_argument("--domain", action="append", default=None, help="One domain (repeatable)")
    pr_decline.add_argument("--domains-file", default=None, help="File with one domain per line")
    pr_decline.add_argument(
        "--sleep-between-batches-s",
        type=float,
        default=0.0,
        help="Sleep seconds between API batches during apply (default: 0)",
    )
    pr_decline.add_argument(
        "--max-batches",
        type=int,
        default=None,
        help="Limit number of 50-domain batches attempted during apply (partial completion)",
    )
    pr_decline.add_argument(
        "--resume-from-receipt",
        dest="resume_from_receipt",
        default=None,
        help="Resume from a previous push-requests receipt (skips already declined domains)",
    )
    pr_decline.set_defaults(func=cmd_push_requests_decline, write_capable=True)
