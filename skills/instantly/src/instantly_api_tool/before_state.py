from __future__ import annotations

import json
import re
import time
from contextlib import contextmanager
from contextvars import ContextVar
from pathlib import Path
from typing import Any, Iterator

from .errors import SafetyError


_WRITE_CTX: ContextVar[dict[str, Any] | None] = ContextVar("instantly_write_ctx", default=None)
_DISABLED: ContextVar[bool] = ContextVar("instantly_before_state_disabled", default=False)


def _utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


@contextmanager
def write_context(ctx: dict[str, Any]) -> Iterator[None]:
    token = _WRITE_CTX.set(ctx)
    try:
        yield
    finally:
        _WRITE_CTX.reset(token)


@contextmanager
def _disabled() -> Iterator[None]:
    token = _DISABLED.set(True)
    try:
        yield
    finally:
        _DISABLED.reset(token)


def _slug(value: str) -> str:
    s = re.sub(r"[^A-Za-z0-9_.-]+", "_", value.strip("/").replace("/", "__"))
    return s[:140] or "root"


def _artifact_before_dir(ctx: dict[str, Any]) -> Path:
    artifacts_dir = ctx.get("artifacts_dir")
    if not artifacts_dir:
        raise SafetyError(
            "Refused: live writes require a local run artifact folder so before-state can be saved. "
            "Remove --no-artifacts or pass --artifacts-dir."
        )
    before_dir = Path(artifacts_dir) / "before"
    before_dir.mkdir(parents=True, exist_ok=True)
    return before_dir


def _capture_list(ctx: dict[str, Any]) -> list[dict[str, Any]]:
    captures = ctx.setdefault("_before_state_captures", [])
    if not isinstance(captures, list):
        captures = []
        ctx["_before_state_captures"] = captures
    return captures


def _mark_no_snapshot(ctx: dict[str, Any], *, write_method: str, write_path: str, reason: str) -> dict[str, Any]:
    before_state = {
        "required": True,
        "supported": False,
        "status": "no_snapshot_available",
        "reason": reason,
        "write": {"method": write_method, "path": write_path},
    }
    ctx["_before_state_no_snapshot"] = before_state
    return before_state


def _save_capture(
    *,
    ctx: dict[str, Any],
    write_method: str,
    write_path: str,
    read_method: str,
    read_path: str,
    data: Any,
    status: int,
) -> dict[str, Any]:
    captures = _capture_list(ctx)
    try:
        before_dir = _artifact_before_dir(ctx)
    except SafetyError as e:
        reason = str(e)
        _mark_no_snapshot(ctx, write_method=write_method, write_path=write_path, reason=reason)
        if bool(ctx.get("ack_no_snapshot")):
            return {
                "captured_at_utc": _utc_now(),
                "write_method": write_method,
                "write_path": write_path,
                "read_method": read_method,
                "read_path": read_path,
                "status": status,
                "saved": False,
                "reason": reason,
            }
        raise
    index = len(captures) + 1
    path = before_dir / f"{index:02d}_{_slug(write_method + '_' + write_path)}.json"
    payload = {
        "captured_at_utc": _utc_now(),
        "write": {"method": write_method, "path": write_path},
        "before_read": {"method": read_method, "path": read_path, "status": status},
        "data": data,
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    capture = {
        "path": str(path),
        "captured_at_utc": payload["captured_at_utc"],
        "write_method": write_method,
        "write_path": write_path,
        "read_method": read_method,
        "read_path": read_path,
        "status": status,
    }
    captures.append(capture)
    return capture


def _ids_from_body(body: dict[str, Any], *keys: str) -> list[str]:
    ids: list[str] = []
    for key in keys:
        value = body.get(key)
        if isinstance(value, list):
            ids.extend(str(item).strip() for item in value if str(item).strip())
        elif value:
            s = str(value).strip()
            if s:
                ids.append(s)
    seen: set[str] = set()
    out: list[str] = []
    for item in ids:
        if item not in seen:
            seen.add(item)
            out.append(item)
    return out


def _emails_from_body(body: dict[str, Any]) -> list[str]:
    return _ids_from_body(body, "emails", "email_accounts", "email_account_ids")


def _target_read_paths(method: str, path: str, body: dict[str, Any] | None) -> list[str] | None:
    body = body or {}

    exact_get_prefixes = (
        r"^/campaigns/[^/]+$",
        r"^/accounts/[^/]+$",
        r"^/leads/[^/]+$",
        r"^/webhooks/[^/]+$",
        r"^/emails/[^/]+$",
        r"^/block-lists-entries/[^/]+$",
        r"^/workspace-members/[^/]+$",
        r"^/workspace-group-members/[^/]+$",
        r"^/lead-lists/[^/]+$",
        r"^/lead-labels/[^/]+$",
        r"^/custom-tags/[^/]+$",
        r"^/subsequences/[^/]+$",
        r"^/inbox-placement-tests/[^/]+$",
    )
    if method in {"PATCH", "DELETE"} and any(re.match(pattern, path) for pattern in exact_get_prefixes):
        return [path]

    if path in {"/workspaces/current", "/workspaces/current/change-owner"}:
        return ["/workspaces/current"]
    if path == "/workspaces/current/whitelabel-domain":
        return ["/workspaces/current/whitelabel-domain"]

    for pattern, read_suffix in (
        (r"^(/campaigns/[^/]+)/(activate|pause|share)$", ""),
        (r"^(/campaigns/[^/]+)/variables$", ""),
        (r"^(/accounts/[^/]+)/(warmup/enable|warmup/disable|pause|resume|mark-fixed)$", ""),
        (r"^(/subsequences/[^/]+)/(pause|resume)$", ""),
        (r"^(/webhooks/[^/]+)/resume$", ""),
    ):
        match = re.match(pattern, path)
        if match:
            return [match.group(1) + read_suffix]

    match = re.match(r"^(/supersearch-enrichment/[^/]+)/settings$", path)
    if match:
        return [match.group(1)]

    if method == "DELETE" and path == "/leads":
        lead_ids = _ids_from_body(body, "lead_ids", "ids")
        return [f"/leads/{lead_id}" for lead_id in lead_ids] if lead_ids else None

    if method == "POST" and path == "/leads/merge":
        lead_ids = _ids_from_body(body, "source_lead_id", "target_lead_id", "lead_ids")
        return [f"/leads/{lead_id}" for lead_id in lead_ids] if lead_ids else None

    if method == "POST" and path in {
        "/leads/update-interest-status",
        "/leads/subsequence/remove",
        "/leads/bulk-assign",
        "/leads/move",
        "/leads/subsequence/move",
    }:
        lead_ids = _ids_from_body(body, "lead_ids", "ids")
        return [f"/leads/{lead_id}" for lead_id in lead_ids] if lead_ids else None

    if method == "POST" and path in {"/accounts/move", "/accounts/warmup/enable", "/accounts/warmup/disable"}:
        emails = _emails_from_body(body)
        return [f"/accounts/{email}" for email in emails] if emails else None

    if method == "DELETE" and path.startswith("/api-keys/"):
        return ["/api-keys"]

    if method == "POST" and path == "/api-keys":
        return ["/api-keys"]

    if method == "DELETE" and path.startswith("/crm-actions/phone-numbers/"):
        return ["/crm-actions/phone-numbers"]

    return None


def _is_read_like_write(method: str, path: str) -> bool:
    if method == "POST" and re.match(r"^/campaigns/[^/]+/export$", path):
        return True
    return method == "POST" and path in {
        "/accounts/test/vitals",
        "/dfy-email-account-orders/domains/check",
        "/dfy-email-account-orders/domains/similar",
    }


def capture_before_state_if_needed(client: Any, method: str, path: str, json_body: dict[str, Any] | None) -> None:
    ctx = _WRITE_CTX.get()
    if not ctx or _DISABLED.get():
        return
    if not bool(ctx.get("apply")) or not bool(ctx.get("write_capable")):
        return

    write_method = method.upper().strip()
    write_path = str(path or "").strip()
    if write_method == "GET" or _is_read_like_write(write_method, write_path):
        return

    read_paths = _target_read_paths(write_method, write_path, json_body)
    if not read_paths:
        reason = f"Instantly has no safe pre-read for {write_method} {write_path}."
        _mark_no_snapshot(ctx, write_method=write_method, write_path=write_path, reason=reason)
        if bool(ctx.get("ack_no_snapshot")):
            return
        raise SafetyError(
            f"Refused: {reason} Review the dry-run plan and pass --ack-no-snapshot only when the approved change "
            "should continue without an automatic restore point."
        )

    with _disabled():
        for read_path in read_paths:
            res = client.get(read_path)
            _save_capture(
                ctx=ctx,
                write_method=write_method,
                write_path=write_path,
                read_method="GET",
                read_path=read_path,
                data=res.data,
                status=res.status,
            )


def _public_captures(ctx: dict[str, Any] | None) -> list[dict[str, Any]]:
    if not ctx:
        return []
    captures = ctx.get("_before_state_captures")
    if not isinstance(captures, list):
        return []
    return [dict(item) for item in captures if isinstance(item, dict)]


def _public_no_snapshot(ctx: dict[str, Any] | None) -> dict[str, Any] | None:
    if not ctx:
        return None
    before_state = ctx.get("_before_state_no_snapshot")
    return dict(before_state) if isinstance(before_state, dict) else None


def augment_output_with_before_state(obj: Any) -> Any:
    if not isinstance(obj, dict):
        return obj
    ctx = _WRITE_CTX.get()
    captures = _public_captures(ctx)
    no_snapshot = _public_no_snapshot(ctx)
    if not captures and not no_snapshot:
        return obj

    out = dict(obj)
    before_state = {"saved": captures} if captures else no_snapshot
    out.setdefault("before_state", before_state)

    receipt = out.get("receipt")
    if isinstance(receipt, dict):
        receipt = dict(receipt)
        receipt.setdefault("before_state", before_state)
        if no_snapshot is not None:
            receipt.setdefault(
                "no_snapshot_approval",
                {
                    "approved": bool(ctx.get("ack_no_snapshot")) if ctx else False,
                    "reason": "No saved before-state snapshot was available for this Instantly write.",
                },
            )
        out["receipt"] = receipt

    receipt_out = out.get("receipt_out")
    if isinstance(receipt_out, str) and receipt_out.strip():
        receipt_path = Path(receipt_out)
        if receipt_path.exists():
            try:
                saved = json.loads(receipt_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                saved = None
            if isinstance(saved, dict):
                saved.setdefault("before_state", before_state)
                if no_snapshot is not None:
                    saved.setdefault(
                        "no_snapshot_approval",
                        {
                            "approved": bool(ctx.get("ack_no_snapshot")) if ctx else False,
                            "reason": "No saved before-state snapshot was available for this Instantly write.",
                        },
                    )
                receipt_path.write_text(
                    json.dumps(saved, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                    encoding="utf-8",
                )

    return out
