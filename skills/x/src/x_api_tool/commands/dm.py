from __future__ import annotations

import csv
import json
import time
import urllib.parse
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import requests

from ..api_dispatch import build_api_call_plan, join_base_url_and_path, load_operations_from_pinned_snapshot, operations_by_id
from ..errors import SafetyError, ValidationError
from ..http import HttpClient, redact_url
from ..json_files import read_json_file, write_json_file
from ..oauth_tokens import read_token_json, token_path_for_env_file
from .write_safety import (
    before_state_refusal_verification_plan,
    blocked_before_state,
    ensure_blocked_apply_contract,
    refusal_output,
    rollback_contract,
)


def _utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _opt_out_path(env_file: str) -> Path:
    root = Path(env_file).resolve().parent
    return root / ".state" / "dm_opt_out.json"


def _load_opt_out(env_file: str) -> dict[str, Any]:
    p = _opt_out_path(env_file)
    if not p.exists():
        return {"version": 1, "updated_at_utc": None, "recipients": []}
    obj = json.loads(p.read_text(encoding="utf-8"))
    if not isinstance(obj, dict):
        raise RuntimeError("Opt-out ledger must be a JSON object")
    if "recipients" not in obj or not isinstance(obj.get("recipients"), list):
        raise RuntimeError("Opt-out ledger missing recipients list")
    return obj


def _save_opt_out(env_file: str, obj: dict[str, Any]) -> None:
    p = _opt_out_path(env_file)
    p.parent.mkdir(parents=True, exist_ok=True)
    obj = dict(obj)
    obj["updated_at_utc"] = _utc_now()
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _normalize_recipient(v: str) -> str:
    s = str(v or "").strip()
    return s.lower() if not s.isdigit() else s


def cmd_dm_opt_out_add(args: Any, ctx: dict[str, Any]) -> int:
    recipient = str(getattr(args, "recipient", "") or "").strip()
    if not recipient:
        raise ValidationError("Missing --recipient")
    reason = str(getattr(args, "reason", "") or "").strip() or None

    obj = _load_opt_out(str(ctx["env_file"]))
    recs = obj.get("recipients")
    assert isinstance(recs, list)
    norm = _normalize_recipient(recipient)
    if any(isinstance(r, dict) and _normalize_recipient(str(r.get("recipient") or "")) == norm for r in recs):
        out = {"ok": True, "dry_run": False, "changed": False, "message": "Already opted out", "recipient": recipient}
        ctx["audit"].write("dm.opt_out.add.noop", {"recipient": recipient})
        ctx["out"].emit(out)
        return 0

    recs.append({"recipient": recipient, "recipient_norm": norm, "reason": reason, "added_at_utc": _utc_now()})
    obj["recipients"] = sorted(
        [r for r in recs if isinstance(r, dict)],
        key=lambda r: (str(r.get("recipient_norm") or ""), str(r.get("added_at_utc") or "")),
    )
    _save_opt_out(str(ctx["env_file"]), obj)
    out = {"ok": True, "dry_run": False, "changed": True, "recipient": recipient}
    ctx["audit"].write("dm.opt_out.add", {"recipient": recipient})
    ctx["out"].emit(out)
    return 0


def cmd_dm_opt_out_list(args: Any, ctx: dict[str, Any]) -> int:
    _ = args
    obj = _load_opt_out(str(ctx["env_file"]))
    recs = [r for r in obj.get("recipients", []) if isinstance(r, dict)]
    out = {"ok": True, "recipients": recs, "count": len(recs)}
    ctx["audit"].write("dm.opt_out.list", {"count": len(recs)})
    ctx["out"].emit(out)
    return 0


def _load_user_access_token(env_file: str) -> str | None:
    tok_path = token_path_for_env_file(env_file)
    data = read_token_json(tok_path)
    if not data:
        return None
    tok = data.get("access_token")
    if isinstance(tok, str) and tok.strip():
        return tok.strip()
    return None


def _resolve_user_id_live(*, username: str, ctx: dict[str, Any]) -> str:
    ops = operations_by_id(load_operations_from_pinned_snapshot())
    op = ops.get("getUsersByUsername")
    if not op:
        raise RuntimeError("Pinned OpenAPI snapshot missing operationId getUsersByUsername")

    plan = build_api_call_plan(
        tool=ctx.get("tool") or "x-api-tool",
        tool_version=ctx.get("tool_version") or "",
        env_fingerprint=str(ctx["cfg"].base_url),
        op=op,
        base_url=str(ctx["cfg"].base_url),
        env_file=str(ctx["env_file"]),
        env_bearer_token=ctx["cfg"].token,
        auth="auto",
        path_json=json.dumps({"username": username}),
        query_json=json.dumps({"user.fields": "id,username"}),
        body_json=None,
        path_pairs=None,
        query_pairs=None,
        file_pairs=None,
    )
    auth_obj = plan.get("auth") if isinstance(plan.get("auth"), dict) else {}
    auth_mode = str(auth_obj.get("mode") or "").strip()
    if auth_mode == "bearer":
        token = ctx["cfg"].token
    elif auth_mode == "oauth2":
        token = _load_user_access_token(str(ctx["env_file"]))
    else:
        token = None
    if auth_mode in {"bearer", "oauth2"} and not token:
        raise SafetyError("Refused: missing token for selected auth mode")
    if auth_mode == "unsupported":
        raise SafetyError("Refused: this operation requires an unsupported auth mode (UserToken)")

    headers = {"Authorization": f"Bearer {token}"} if token else {}
    filled_path = str(plan.get("operation", {}).get("path_filled") or "").strip()
    url = join_base_url_and_path(str(ctx["cfg"].base_url), filled_path)
    query = (plan.get("inputs") or {}).get("query") if isinstance(plan.get("inputs"), dict) else {}
    if not isinstance(query, dict):
        query = {}

    client = HttpClient(timeout_s=float(ctx["timeout_s"]), verbose=bool(ctx.get("verbose")), user_agent="x-api-tool")
    resp = client.request("GET", url, headers=headers or None, params=query or None, retries=0)
    data = resp.json()
    user = (data or {}).get("data") if isinstance(data, dict) else None
    if not isinstance(user, dict) or not str(user.get("id") or "").strip():
        raise RuntimeError("Could not resolve user id from API response")
    return str(user["id"]).strip()


def cmd_dm_can_send(args: Any, ctx: dict[str, Any]) -> int:
    to_username = str(getattr(args, "to_username", "") or "").strip()
    to_user_id = str(getattr(args, "to_user_id", "") or "").strip()
    if not to_username and not to_user_id:
        raise ValidationError("Missing --to-username or --to-user-id")

    if to_user_id:
        plan = {"ok": True, "dry_run": True, "note": "Provide --to-username to check receives_your_dm via users resolve."}
        ctx["audit"].write("dm.can_send.plan", {"to_user_id": to_user_id})
        ctx["out"].emit(plan)
        return 0

    # Build a plan for users resolve that requests receives_your_dm.
    ops = operations_by_id(load_operations_from_pinned_snapshot())
    op = ops.get("getUsersByUsername")
    if not op:
        raise RuntimeError("Pinned OpenAPI snapshot missing operationId getUsersByUsername")

    plan = build_api_call_plan(
        tool=ctx.get("tool") or "x-api-tool",
        tool_version=ctx.get("tool_version") or "",
        env_fingerprint=str(ctx["cfg"].base_url),
        op=op,
        base_url=str(ctx["cfg"].base_url),
        env_file=str(ctx["env_file"]),
        env_bearer_token=ctx["cfg"].token,
        auth="auto",
        path_json=json.dumps({"username": to_username}),
        query_json=json.dumps({"user.fields": "id,username,receives_your_dm"}),
        body_json=None,
        path_pairs=None,
        query_pairs=None,
        file_pairs=None,
    )

    if not bool(ctx.get("live")):
        out = {"ok": True, "dry_run": True, "plan": plan}
        ctx["audit"].write("dm.can_send.plan", {"to_username": to_username})
        ctx["out"].emit(out)
        return 0

    # Live check.
    auth_obj = plan.get("auth") if isinstance(plan.get("auth"), dict) else {}
    auth_mode = str(auth_obj.get("mode") or "").strip()
    if auth_mode == "bearer":
        token = ctx["cfg"].token
    elif auth_mode == "oauth2":
        token = _load_user_access_token(str(ctx["env_file"]))
    else:
        token = None
    if auth_mode in {"bearer", "oauth2"} and not token:
        raise SafetyError("Refused: missing token for selected auth mode")
    if auth_mode == "unsupported":
        raise SafetyError("Refused: this operation requires an unsupported auth mode (UserToken)")

    headers = {"Authorization": f"Bearer {token}"} if token else {}
    filled_path = str(plan.get("operation", {}).get("path_filled") or "").strip()
    url = join_base_url_and_path(str(ctx["cfg"].base_url), filled_path)
    query = (plan.get("inputs") or {}).get("query") if isinstance(plan.get("inputs"), dict) else {}
    if not isinstance(query, dict):
        query = {}

    client = HttpClient(timeout_s=float(ctx["timeout_s"]), verbose=bool(ctx.get("verbose")), user_agent="x-api-tool")
    resp = client.request("GET", url, headers=headers or None, params=query or None, retries=0)
    data = resp.json()
    user = (data or {}).get("data") if isinstance(data, dict) else None
    receives = None
    if isinstance(user, dict) and "receives_your_dm" in user:
        receives = user.get("receives_your_dm")
    out = {
        "ok": True,
        "dry_run": False,
        "to_username": to_username,
        "receives_your_dm": receives,
        "request": {"method": "GET", "url": redact_url(resp.url)},
    }
    ctx["audit"].write("dm.can_send.live", {"to_username": to_username, "status": resp.status})
    ctx["out"].emit(out)
    return 0


@dataclass(frozen=True)
class _DmSendItem:
    recipient: str
    recipient_id: str | None
    message: str
    intent_evidence: str | None


def _read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        rows: list[dict[str, str]] = []
        for row in reader:
            if not row:
                continue
            rows.append({str(k): str(v) for k, v in row.items() if k})
        return rows


def _bulk_policy_validate(
    *,
    rows: list[dict[str, str]],
    opt_out_line: str,
    opt_out_ledger: dict[str, Any],
) -> tuple[bool, list[str], list[_DmSendItem]]:
    reasons: list[str] = []
    if not opt_out_line.strip():
        reasons.append("Missing --opt-out-line (required for bulk DMs).")

    required_cols = {"recipient", "message", "intent_evidence"}
    if rows:
        missing_cols = sorted(required_cols - set(rows[0].keys()))
        if missing_cols:
            reasons.append("CSV missing required columns: " + ", ".join(missing_cols))
    else:
        reasons.append("CSV has no rows.")

    opted_out = {_normalize_recipient(str(r.get("recipient_norm") or r.get("recipient") or "")) for r in opt_out_ledger.get("recipients", []) if isinstance(r, dict)}

    items: list[_DmSendItem] = []
    for i, row in enumerate(rows, start=1):
        recipient = str(row.get("recipient") or "").strip()
        message = str(row.get("message") or "").strip()
        evidence = str(row.get("intent_evidence") or "").strip()
        if not recipient:
            reasons.append(f"Row {i}: missing recipient")
            continue
        if not message:
            reasons.append(f"Row {i}: missing message")
            continue
        if not evidence:
            reasons.append(f"Row {i}: missing intent_evidence")
            continue
        if _normalize_recipient(recipient) in opted_out:
            reasons.append(f"Row {i}: recipient is opted out: {recipient}")
            continue
        items.append(_DmSendItem(recipient=recipient, recipient_id=None, message=message, intent_evidence=evidence))

    ok = not reasons
    return ok, reasons, items


def _opted_out_set(opt_out_ledger: dict[str, Any]) -> set[str]:
    return {
        _normalize_recipient(str(r.get("recipient_norm") or r.get("recipient") or ""))
        for r in opt_out_ledger.get("recipients", [])
        if isinstance(r, dict)
    }


def _bulk_apply_validate_plan(
    *,
    plan: dict[str, Any],
    opt_out_ledger: dict[str, Any],
) -> tuple[bool, list[str]]:
    reasons: list[str] = []
    opt_out_line = str(plan.get("opt_out_line") or "")
    if not opt_out_line.strip():
        reasons.append("Plan missing non-empty opt_out_line (required for bulk DMs).")

    items = plan.get("items")
    if not isinstance(items, list) or not items:
        reasons.append("Plan has no items.")
        return False, reasons

    opted_out = _opted_out_set(opt_out_ledger)
    for i, it in enumerate(items, start=1):
        if not isinstance(it, dict):
            reasons.append(f"Plan item {i}: must be an object")
            continue
        recipient = str(it.get("recipient") or "").strip()
        recipient_norm = _normalize_recipient(str(it.get("recipient_norm") or recipient))
        message = str(it.get("message") or "")
        evidence = str(it.get("intent_evidence") or "").strip()
        if not recipient:
            reasons.append(f"Plan item {i}: missing recipient")
            continue
        if recipient_norm in opted_out:
            reasons.append(f"Plan item {i}: recipient is opted out: {recipient}")
            continue
        if not evidence:
            reasons.append(f"Plan item {i}: missing intent_evidence")
            continue
        if opt_out_line.strip() and opt_out_line.strip() not in message:
            reasons.append(f"Plan item {i}: message missing opt_out_line (required)")
            continue

    ok = not reasons
    return ok, reasons


def _post_json_with_backoff(
    *,
    url: str,
    headers: dict[str, str],
    json_body: dict[str, Any],
    timeout_s: float,
    max_attempts: int = 4,
) -> requests.Response:
    attempt = 0
    while True:
        attempt += 1
        resp = requests.post(url, headers=headers, json=json_body, timeout=timeout_s)
        if resp.status_code != 429 or attempt >= max_attempts:
            return resp
        ra = resp.headers.get("Retry-After")
        sleep_s = None
        if ra:
            try:
                sleep_s = int(float(ra))
            except Exception:
                sleep_s = None
        if sleep_s is None:
            sleep_s = min(2 ** (attempt - 1), 10)
        time.sleep(max(0, min(sleep_s, 60)))


def _dm_send_url(*, ctx: dict[str, Any], participant_id: str) -> str:
    ops = operations_by_id(load_operations_from_pinned_snapshot())
    op_send = ops.get("createDirectMessagesByParticipantId")
    if not op_send:
        raise RuntimeError("Pinned OpenAPI snapshot missing operationId createDirectMessagesByParticipantId")
    safe_id = urllib.parse.quote(str(participant_id), safe="")
    path = op_send.path.replace("{participant_id}", safe_id)
    return join_base_url_and_path(str(ctx["cfg"].base_url), path)


def _response_body_json(resp: requests.Response) -> Any:
    try:
        return resp.json()
    except Exception:
        return None


def cmd_dm_bulk_send(args: Any, ctx: dict[str, Any]) -> int:
    csv_path = Path(str(getattr(args, "csv", "") or "").strip())
    if not str(csv_path):
        raise ValidationError("Missing --csv")
    if not csv_path.exists():
        raise ValidationError(f"CSV not found: {csv_path}")

    opt_out_line = str(getattr(args, "opt_out_line", "") or "")
    ledger = _load_opt_out(str(ctx["env_file"]))
    rows = _read_csv_rows(csv_path)
    ok, reasons, items = _bulk_policy_validate(rows=rows, opt_out_line=opt_out_line, opt_out_ledger=ledger)
    if not ok:
        out = {"ok": True, "refused": True, "reasons": sorted(set(reasons)), "refusal_type": "PolicyRefusal"}
        ctx["audit"].write("dm.bulk_send.refused", {"reasons": out["reasons"]})
        ctx["out"].emit(out)
        return 0

    # Build plan (plan-only by default).
    plan = {
        "tool": ctx.get("tool") or "x-api-tool",
        "version": ctx.get("tool_version") or None,
        "generated_at_utc": _utc_now(),
        "env_fingerprint": str(ctx["cfg"].base_url),
        "kind": "dm.bulk_send",
        "csv": str(csv_path),
        "count": len(items),
        "opt_out_line": opt_out_line,
        "items": [
            {
                "recipient": it.recipient,
                "recipient_norm": _normalize_recipient(it.recipient),
                "recipient_is_id": it.recipient.isdigit(),
                "message": it.message + ("\n\n" + opt_out_line.strip()),
                "intent_evidence": it.intent_evidence,
            }
            for it in items
        ],
        "dry_run": True,
    }
    plan["before_state"] = blocked_before_state(
        action="dm.bulk_send",
        provider_write={
            "service": "X API",
            "operation_id": "createDirectMessagesByParticipantId",
            "method": "POST",
            "count": len(items),
        },
    )
    plan["verification_plan"] = before_state_refusal_verification_plan()
    plan["rollback"] = rollback_contract()

    plan_out = ctx.get("plan_out")
    plan_path = write_json_file(plan_out, plan) if plan_out else None

    if not bool(ctx.get("apply")):
        out = {"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path}
        ctx["audit"].write("dm.bulk_send.plan", {"count": len(items), "plan_out": plan_path})
        ctx["out"].emit(out)
        return 0

    if not bool(ctx.get("yes")):
        raise SafetyError("Refused: bulk DMs require --apply --yes")

    min_delay_s_raw = getattr(args, "min_delay_s", 1.0)
    try:
        min_delay_s = float(min_delay_s_raw)
    except Exception:
        raise ValidationError("--min-delay-s must be a number") from None
    if min_delay_s < 0:
        raise ValidationError("--min-delay-s must be >= 0")

    plan_in = ctx.get("plan_in")
    if plan_in:
        plan_obj = read_json_file(plan_in)
        if not isinstance(plan_obj, dict) or str(plan_obj.get("kind") or "") != "dm.bulk_send":
            raise ValidationError("Plan file must be a dm.bulk_send plan object")
        if str(plan_obj.get("env_fingerprint") or "") != str(ctx["cfg"].base_url):
            raise SafetyError("Refused: plan env_fingerprint does not match current environment")
        plan = plan_obj

    # Apply-time revalidation (critical): prevent plan-in from bypassing policy checks, and
    # ensure opt-out/intent/opt-out-line are still enforced at execution time.
    ledger_now = _load_opt_out(str(ctx["env_file"]))
    ok_apply, reasons_apply = _bulk_apply_validate_plan(plan=plan, opt_out_ledger=ledger_now)
    if not ok_apply:
        out = {"ok": True, "refused": True, "reasons": sorted(set(reasons_apply)), "refusal_type": "PolicyRefusal"}
        ctx["audit"].write("dm.bulk_send.refused", {"reasons": out["reasons"]})
        ctx["out"].emit(out)
        return 0

    plan = ensure_blocked_apply_contract(
        plan,
        action="dm.bulk_send",
        provider_write={
            "service": "X API",
            "operation_id": "createDirectMessagesByParticipantId",
            "method": "POST",
            "count": len(plan.get("items") or []),
        },
    )
    if not bool(ctx.get("ack_no_snapshot")):
        out = refusal_output(plan=plan)
        ctx["audit"].write("dm.bulk_send.refused", {"reasons": out["reasons"], "count": len(plan.get("items") or [])})
        ctx["out"].emit(out)
        return 0

    token = _load_user_access_token(str(ctx["env_file"]))
    if not token:
        raise SafetyError("Refused: missing OAuth access token for DM send")

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json", "Accept": "application/json"}
    results: list[dict[str, Any]] = []
    items_for_apply = [it for it in plan.get("items", []) if isinstance(it, dict)]
    for idx, item in enumerate(items_for_apply, start=1):
        recipient = str(item.get("recipient") or "").strip()
        recipient_id = recipient if bool(item.get("recipient_is_id")) else _resolve_user_id_live(username=recipient, ctx=ctx)
        message = str(item.get("message") or "")
        url = _dm_send_url(ctx=ctx, participant_id=recipient_id)
        resp = _post_json_with_backoff(
            url=url,
            headers=headers,
            json_body={"text": message},
            timeout_s=float(ctx["timeout_s"]),
        )
        results.append(
            {
                "row": idx,
                "recipient": recipient,
                "participant_id": recipient_id,
                "status": resp.status_code,
                "url": redact_url(getattr(resp, "url", url)),
                "body_json": _response_body_json(resp),
            }
        )
        if idx < len(items_for_apply):
            time.sleep(min_delay_s)

    receipt = {
        "tool": ctx.get("tool") or "x-api-tool",
        "version": ctx.get("tool_version") or None,
        "applied_at_utc": _utc_now(),
        "env_fingerprint": str(ctx["cfg"].base_url),
        "kind": "dm.bulk_send",
        "count": len(results),
        "before_state": plan.get("before_state"),
        "no_snapshot_approval": {
            "acknowledged": True,
            "flag": "--ack-no-snapshot",
            "reason": "No reliable before-state snapshot is available for X DM sends.",
        },
        "verification": {"ok": True, "mode": "provider-response-per-send"},
        "results": results,
    }
    receipt_out = ctx.get("receipt_out")
    receipt_path = write_json_file(receipt_out, receipt) if receipt_out else None
    out = {"ok": True, "dry_run": False, "receipt": receipt, "receipt_out": receipt_path, "results": results}
    ctx["audit"].write("dm.bulk_send.apply", {"count": len(results), "receipt_out": receipt_path})
    ctx["out"].emit(out)
    return 0


def cmd_dm_send(args: Any, ctx: dict[str, Any]) -> int:
    to_username = str(getattr(args, "to_username", "") or "").strip()
    to_user_id = str(getattr(args, "to_user_id", "") or "").strip()
    message = str(getattr(args, "message", "") or "").strip()
    if not to_username and not to_user_id:
        raise ValidationError("Missing --to-username or --to-user-id")
    if not message:
        raise ValidationError("Missing --message")

    ops = operations_by_id(load_operations_from_pinned_snapshot())
    op_send = ops.get("createDirectMessagesByParticipantId")
    if not op_send:
        raise RuntimeError("Pinned OpenAPI snapshot missing operationId createDirectMessagesByParticipantId")

    path_params = {"participant_id": to_user_id} if to_user_id else {}
    plan = build_api_call_plan(
        tool=ctx.get("tool") or "x-api-tool",
        tool_version=ctx.get("tool_version") or "",
        env_fingerprint=str(ctx["cfg"].base_url),
        op=op_send,
        base_url=str(ctx["cfg"].base_url),
        env_file=str(ctx["env_file"]),
        env_bearer_token=ctx["cfg"].token,
        auth="user",
        path_json=json.dumps(path_params),
        query_json=json.dumps({}),
        body_json=json.dumps({"text": message}),
        path_pairs=None,
        query_pairs=None,
        file_pairs=None,
    )

    plan_out = ctx.get("plan_out")
    plan_path = write_json_file(plan_out, plan) if plan_out else None

    if not bool(ctx.get("apply")):
        out = {"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path}
        ctx["audit"].write("dm.send.plan", {"to_username": to_username or None, "to_user_id": to_user_id or None})
        ctx["out"].emit(out)
        return 0

    if not bool(ctx.get("yes")):
        raise SafetyError("Refused: dm send requires --apply --yes")

    plan = ensure_blocked_apply_contract(
        plan,
        action="dm.send",
        provider_write={
            "service": "X API",
            "operation_id": "createDirectMessagesByParticipantId",
            "method": "POST",
            "recipient": to_user_id or to_username,
        },
    )
    if not bool(ctx.get("ack_no_snapshot")):
        out = refusal_output(plan=plan)
        ctx["audit"].write("dm.send.refused", {"reasons": out["reasons"], "to_username": to_username or None, "to_user_id": to_user_id or None})
        ctx["out"].emit(out)
        return 0

    token = _load_user_access_token(str(ctx["env_file"]))
    if not token:
        raise SafetyError("Refused: missing OAuth access token for DM send")

    if not to_user_id and to_username:
        to_user_id = _resolve_user_id_live(username=to_username, ctx=ctx)

    url = _dm_send_url(ctx=ctx, participant_id=to_user_id)
    resp = _post_json_with_backoff(
        url=url,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json", "Accept": "application/json"},
        json_body={"text": message},
        timeout_s=float(ctx["timeout_s"]),
    )
    receipt = {
        "tool": ctx.get("tool") or "x-api-tool",
        "version": ctx.get("tool_version") or None,
        "applied_at_utc": _utc_now(),
        "env_fingerprint": str(ctx["cfg"].base_url),
        "kind": "dm.send",
        "recipient": to_username or to_user_id,
        "participant_id": to_user_id,
        "before_state": plan.get("before_state"),
        "no_snapshot_approval": {
            "acknowledged": True,
            "flag": "--ack-no-snapshot",
            "reason": "No reliable before-state snapshot is available for X DM sends.",
        },
        "verification": {"ok": True, "mode": "provider-response"},
        "response": {"status": resp.status_code, "url": redact_url(getattr(resp, "url", url)), "body_json": _response_body_json(resp)},
    }
    receipt_out = ctx.get("receipt_out")
    receipt_path = write_json_file(receipt_out, receipt) if receipt_out else None
    out = {"ok": True, "dry_run": False, "receipt": receipt, "receipt_out": receipt_path}
    ctx["audit"].write("dm.send.apply", {"status": resp.status_code, "receipt_out": receipt_path, "to_user_id": to_user_id})
    ctx["out"].emit(out)
    return 0
