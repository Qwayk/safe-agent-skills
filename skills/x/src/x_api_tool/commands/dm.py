from __future__ import annotations

import csv
import json
import time
import urllib.parse
from pathlib import Path
from typing import Any

import requests

from ..api_dispatch import (
    build_api_call_plan,
    join_base_url_and_path,
    load_operations_from_pinned_snapshot,
    operations_by_id,
)
from ..errors import SafetyError, ValidationError
from ..http import HttpClient, redact_url
from ..json_files import read_json_file, write_json_file
from ..oauth_tokens import read_token_json, token_path_for_env_file
from .write_safety import (
    check_review,
    ensure_blocked_apply_contract,
    mark_reviewed,
    read_account,
    refusal_output,
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
    auth_raw = plan.get("auth")
    auth_obj: dict[str, Any] = auth_raw if isinstance(auth_raw, dict) else {}
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
    operation_raw = plan.get("operation")
    operation: dict[str, Any] = operation_raw if isinstance(operation_raw, dict) else {}
    filled_path = str(operation.get("path_filled") or "").strip()
    url = join_base_url_and_path(str(ctx["cfg"].base_url), filled_path)
    inputs_raw = plan.get("inputs")
    inputs: dict[str, Any] = inputs_raw if isinstance(inputs_raw, dict) else {}
    query = inputs.get("query")
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


def _read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        rows: list[dict[str, str]] = []
        for row in reader:
            if not row:
                continue
            rows.append({str(k): str(v) for k, v in row.items() if k})
        return rows


def _opted_out_set(opt_out_ledger: dict[str, Any]) -> set[str]:
    return {
        _normalize_recipient(str(r.get("recipient_norm") or r.get("recipient") or ""))
        for r in opt_out_ledger.get("recipients", [])
        if isinstance(r, dict)
    }


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



def _dm_rows(args: Any, *, bulk: bool) -> list[dict[str, str]]:
    if bulk:
        return _read_csv_rows(Path(args.csv))
    targets = [str(value).strip() for value in (args.to_user_id, args.to_username) if value]
    if len(targets) != 1:
        raise ValidationError("Give one recipient by username or user ID.")
    return [{"recipient": targets[0], "message": args.message, "intent_evidence": args.intent_evidence}]


def _dm_policy(
    rows: list[dict[str, str]], opt_out_line: str, opted_out: set[str]
) -> tuple[list[dict[str, str]], list[str]]:
    reasons: list[str] = []
    if not opt_out_line:
        reasons.append("Include an opt-out line.")
    if not rows:
        reasons.append("There are no recipient rows.")
    items = []
    recipients: set[str] = set()
    messages: set[str] = set()
    for i, row in enumerate(rows, start=1):
        recipient = _normalize_recipient(str(row.get("recipient") or ""))
        message = str(row.get("message") or "").strip()
        evidence = str(row.get("intent_evidence") or "").strip()
        if not recipient or not message or not evidence:
            reasons.append(f"Row {i}: give a recipient, a message, and intent_evidence for the invitation.")
        elif recipient in opted_out:
            reasons.append(f"Row {i}: recipient is opted out: {recipient}")
        elif recipient in recipients or " ".join(message.casefold().split()) in messages:
            reasons.append(f"Row {i}: the recipient or message repeats an earlier row.")
        else:
            recipients.add(recipient)
            messages.add(" ".join(message.casefold().split()))
            items.append({"recipient": recipient, "message": f"{message}\n\n{opt_out_line}", "intent_evidence": evidence})
    return items, reasons


def _dm_refusal(ctx: dict[str, Any], reasons: list[str]) -> int:
    ctx["audit"].write("dm.refused", {"reasons": reasons})
    ctx["out"].emit({"ok": True, "refused": True, "reasons": reasons, "refusal_type": "PolicyRefusal"})
    return 0


def _recipient_account(ctx: dict[str, Any], token: str, target: str) -> dict[str, str]:
    resource = urllib.parse.quote(target, safe="")
    path = f"/users/{resource}" if target.isascii() and target.isdigit() else f"/users/by/username/{resource}"
    client = HttpClient(timeout_s=float(ctx["timeout_s"]), verbose=bool(ctx.get("verbose")), user_agent="x-api-tool")
    response = client.request(
        "GET", ctx["cfg"].base_url.rstrip("/") + path, headers={"Authorization": f"Bearer {token}"}, retries=0,
    ).json()
    data = response.get("data") if isinstance(response, dict) else None
    if not isinstance(data, dict) or not data.get("id") or not data.get("username"):
        raise SafetyError(f"X did not confirm the recipient {target}.")
    return {"id": str(data["id"]), "username": _normalize_recipient(str(data["username"]))}


def _recipient_opted_out(opted_out: set[str], target: dict[str, str]) -> bool:
    return bool({target["id"], target["username"]} & opted_out)


def _run_dm(args: Any, ctx: dict[str, Any], *, bulk: bool) -> int:
    kind = "dm.bulk_send" if bulk else "dm.send"
    delay = args.min_delay_s if bulk else 0
    if not 0 <= delay < float("inf"):
        raise ValidationError("--min-delay-s must be a finite nonnegative number.")
    apply = bool(ctx.get("apply"))
    opted_out = _opted_out_set(_load_opt_out(str(ctx["env_file"])))
    opt_out_line = str(args.opt_out_line or "").strip()
    items, reasons = _dm_policy(_dm_rows(args, bulk=bulk), opt_out_line, opted_out)
    if reasons:
        return _dm_refusal(ctx, reasons)

    plan = ensure_blocked_apply_contract(
        {
            "kind": kind, "dry_run": True, "env_fingerprint": str(ctx["cfg"].base_url),
            "generated_at_utc": _utc_now(), "items": items, "count": len(items),
            "opt_out_line": opt_out_line, "min_delay_s": delay,
        },
        action=kind,
        provider_write={"service": "X API", "operation_id": "createDirectMessagesByParticipantId", "count": len(items)},
    )
    if not apply:
        plan_path = None
        if ctx.get("plan_out"):
            if ctx.get("live"):
                token = _load_user_access_token(str(ctx["env_file"]))
                if not token:
                    raise SafetyError("Connect the X user account before saving a reviewed message plan.")
                account = read_account(ctx, token)
                targets = [_recipient_account(ctx, token, item["recipient"]) for item in items]
                if len({target["id"] for target in targets}) != len(targets):
                    return _dm_refusal(ctx, ["Two rows refer to the same recipient."])
                for target in targets:
                    if _recipient_opted_out(opted_out, target):
                        return _dm_refusal(ctx, [f"Recipient is opted out: {target['username']}"])
                plan["targets"] = targets
                mark_reviewed(plan, account)
            plan_path = write_json_file(ctx["plan_out"], plan)
        ctx["out"].emit({"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path})
        return 0

    if not ctx.get("yes"):
        raise SafetyError("Sending messages requires --apply --yes.")
    if not ctx.get("ack_no_snapshot"):
        ctx["out"].emit(refusal_output(plan=plan))
        return 0
    if not ctx.get("plan_in"):
        raise SafetyError("Send from a reviewed plan with --plan-in.")
    saved = read_json_file(ctx["plan_in"])
    if not isinstance(saved, dict) or any(
        saved.get(key) != plan.get(key)
        for key in ("kind", "env_fingerprint", "items", "opt_out_line", "min_delay_s")
    ):
        raise SafetyError("The recipient, message, or settings changed after review. Save a new preview.")
    token = _load_user_access_token(str(ctx["env_file"]))
    if not token:
        raise SafetyError("Missing the connected X user token.")
    sender = check_review(saved, ctx, token)
    reviewed_targets = saved.get("targets")
    if not isinstance(reviewed_targets, list) or len(reviewed_targets) != len(items):
        raise SafetyError("Save a connected preview to identify the recipients.")
    targets = [_recipient_account(ctx, token, item["recipient"]) for item in items]
    if targets != reviewed_targets:
        raise SafetyError("A recipient changed after review. Save a new preview.")
    for target in targets:
        if _recipient_opted_out(opted_out, target):
            return _dm_refusal(ctx, [f"Recipient is opted out: {target['username']}"])

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json", "Accept": "application/json"}
    results: list[dict[str, Any]] = []
    for item, target in zip(items, targets, strict=True):
        opted_out = _opted_out_set(_load_opt_out(str(ctx["env_file"])))
        if item["recipient"] in opted_out or _recipient_opted_out(opted_out, target):
            results.append({"participant_id": target["id"], "ok": False, "reason": "Recipient opted out."})
            break
        url = _dm_send_url(ctx=ctx, participant_id=target["id"])
        result: dict[str, Any] = {"participant_id": target["id"], "ok": False}
        try:
            response = requests.post(url, headers=headers, json={"text": item["message"]}, timeout=float(ctx["timeout_s"]))
        except requests.RequestException:
            result.update(status="unconfirmed", reason="The reply was lost. Check X before trying again.")
        else:
            body = _response_body_json(response)
            data = body.get("data") if isinstance(body, dict) else None
            event = data.get("dm_event_id") if isinstance(data, dict) else None
            accepted = 200 <= response.status_code < 300 and bool(event)
            status = "accepted" if accepted else "rejected" if 400 <= response.status_code < 500 else "unconfirmed"
            result.update(ok=accepted, status=status, http_status=response.status_code, dm_event_id=event if accepted else None)
            if status == "unconfirmed":
                result["reason"] = "X did not confirm the send. Check X before trying again."
        results.append(result)
        if not result["ok"]:
            break
        if len(results) < len(items) and delay:
            time.sleep(delay)

    ok = all(result["ok"] for result in results) and len(results) == len(items)
    receipt = {
        "kind": kind, "sender": sender, "count": len(results),
        "before_state": plan["before_state"],
        "no_snapshot_approval": {"acknowledged": True, "flag": "--ack-no-snapshot"},
        "verification": {"ok": ok, "mode": "X acceptance with a message event ID"},
        "results": results,
    }
    receipt_path = write_json_file(ctx["receipt_out"], receipt) if ctx.get("receipt_out") else None
    ctx["audit"].write("dm.apply", {"kind": kind, "attempted": len(results), "ok": ok})
    ctx["out"].emit({"ok": ok, "dry_run": False, "receipt": receipt, "receipt_out": receipt_path})
    return 0 if ok else 1


def cmd_dm_bulk_send(args: Any, ctx: dict[str, Any]) -> int:
    return _run_dm(args, ctx, bulk=True)


def cmd_dm_send(args: Any, ctx: dict[str, Any]) -> int:
    return _run_dm(args, ctx, bulk=False)
