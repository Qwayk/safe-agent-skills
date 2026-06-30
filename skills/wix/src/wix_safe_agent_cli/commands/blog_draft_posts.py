from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from ..authz import resolve_auth_mode
from ..errors import SafetyError, ValidationError
from ..http import HttpClient
from ..json_files import read_json_file, write_json_file
from ..write_safety import reviewed_plan_apply_requested


COMMAND_FAMILY = "blog-draft-posts"
BASE_PATH = "/blog/v3/draft-posts"


def _coerce_text(raw: Any, *, field: str) -> str:
    if raw is None:
        raise ValidationError(f"Missing --{field}")
    if not isinstance(raw, str):
        raise ValidationError(f"--{field} must be a string")
    value = raw.strip()
    if not value:
        raise ValidationError(f"--{field} cannot be empty")
    return value


def _read_json_arg(raw: Any, *, field: str, allow_empty: bool = False) -> dict[str, Any]:
    value = _coerce_text(raw, field=field)
    if value.startswith("@"):
        path = Path(value[1:])
        if not path.exists():
            raise ValidationError(f"--{field} file not found: {path}")
        value = path.read_text(encoding="utf-8").strip()
    try:
        payload = json.loads(value)
    except json.JSONDecodeError as exc:
        raise ValidationError(f"Invalid JSON for --{field}: {exc.msg}") from exc
    if not isinstance(payload, dict):
        raise ValidationError(f"--{field} must be a JSON object")
    if not allow_empty and not payload:
        raise ValidationError(f"--{field} cannot be empty")
    return payload


def _resolve_auth(ctx: dict[str, Any]) -> dict[str, Any]:
    return resolve_auth_mode(
        cfg=ctx["cfg"],
        env_file=str(ctx["env_file"]),
        verbose=bool(ctx.get("verbose")),
        command_family=COMMAND_FAMILY,
    )


def _request_json(
    *,
    method: str,
    path: str,
    headers: dict[str, str],
    params: dict[str, Any] | None,
    json_body: dict[str, Any] | None,
    ctx: dict[str, Any],
) -> dict[str, Any]:
    request_headers = dict(headers)
    if method.upper() != "GET":
        request_headers["Content-Type"] = "application/json"
    client = HttpClient(timeout_s=float(ctx["cfg"].timeout_s), verbose=bool(ctx.get("verbose")), user_agent="wix-safe-agent-cli")
    response = client.request(
        method=method,
        url=ctx["cfg"].base_url.rstrip("/") + "/" + path.lstrip("/"),
        headers=request_headers,
        params=params,
        json_body=json_body,
    )
    payload = response.json()
    if not isinstance(payload, dict):
        raise ValidationError("Wix API returned a non-object JSON response")
    return payload


def _utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _emit_error(ctx: dict[str, Any], *, method: str, exc: Exception) -> int:
    if isinstance(exc, SafetyError):
        ctx["out"].emit({"ok": True, "dry_run": True, "refused": True, "reasons": [str(exc)], "refusal_type": "SafetyError", "method": method})
        return 0
    if isinstance(exc, ValidationError):
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": method})
        return 1
    ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": method})
    return 1


def _run_read(
    *,
    method_name: str,
    http_method: str,
    path: str,
    params: dict[str, Any] | None,
    body: dict[str, Any] | None,
    ctx: dict[str, Any],
) -> int:
    auth = _resolve_auth(ctx)
    response = _request_json(method=http_method, path=path, headers=auth["headers"], params=params, json_body=body, ctx=ctx)
    request: dict[str, Any] = {"method": http_method, "path": path}
    if params is not None:
        request["params"] = params
    if body is not None:
        request["body"] = body
    out = {"ok": True, "method": method_name, "auth_mode": auth["mode"], "request": request, "response": response}
    ctx["audit"].write(method_name, out)
    ctx["out"].emit(out)
    return 0


def _build_plan(
    *,
    method_name: str,
    request: dict[str, Any],
    selector: dict[str, Any],
    proposed_changes: list[dict[str, Any]],
    ctx: dict[str, Any],
    requires_ack: bool,
    risk_reasons: list[str],
    verification_notes: str,
) -> dict[str, Any]:
    preconditions = ["env_fingerprint must match", "selector must match", "apply requires --plan-in, --apply, and --yes"]
    if requires_ack:
        preconditions.append("apply also requires --ack-irreversible")
    return {
        "tool": ctx.get("tool") or "wix-safe-agent-cli",
        "version": ctx.get("tool_version") or None,
        "generated_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "method": method_name,
        "risk_level": "high" if requires_ack else "medium",
        "risk_reasons": risk_reasons,
        "preconditions": preconditions,
        "selector": selector,
        "request": request,
        "baseline": {"env_fingerprint": ctx["cfg"].base_url, "selector": selector, "before_state": {}},
        "state_capture": {"before_state_available": False, "notes": "Blog Draft Posts plans do not capture a full before-state snapshot in this slice."},
        "proposed_changes": proposed_changes,
        "verification_plan": {"type": "provider-response", "notes": verification_notes},
        "rollback": {"supported": False, "notes": "No automatic rollback. Verify with blog-draft-posts get/list/query or the Wix dashboard when needed."},
    }


def _load_plan(*, plan_in: str | None, expected_method: str, expected_selector: dict[str, Any], ctx: dict[str, Any]) -> dict[str, Any]:
    if not plan_in:
        raise ValidationError("Missing --plan-in")
    plan = read_json_file(plan_in)
    if not isinstance(plan, dict):
        raise ValidationError("Plan file must be a JSON object")
    if str(plan.get("method") or "") != expected_method:
        raise SafetyError("Refused: plan method does not match current command")
    baseline = plan.get("baseline")
    if not isinstance(baseline, dict):
        raise SafetyError("Refused: plan baseline missing")
    if str(baseline.get("env_fingerprint") or "") != str(ctx["cfg"].base_url):
        raise SafetyError("Refused: plan env_fingerprint does not match current environment")
    if baseline.get("selector") != expected_selector:
        raise SafetyError("Refused: plan selector does not match current command")
    return plan


def _run_write(
    *,
    method_name: str,
    http_method: str,
    path: str,
    params: dict[str, Any] | None,
    body: dict[str, Any] | None,
    selector: dict[str, Any],
    proposed_changes: list[dict[str, Any]],
    ctx: dict[str, Any],
    requires_ack: bool,
    risk_reasons: list[str],
    verification_notes: str,
) -> int:
    auth = _resolve_auth(ctx)
    request: dict[str, Any] = {"method": http_method, "path": path}
    if params is not None:
        request["params"] = params
    if body is not None:
        request["body"] = body
    plan = _build_plan(
        method_name=method_name,
        request=request,
        selector=selector,
        proposed_changes=proposed_changes,
        ctx=ctx,
        requires_ack=requires_ack,
        risk_reasons=risk_reasons,
        verification_notes=verification_notes,
    )
    apply_allowed = reviewed_plan_apply_requested(ctx, requires_ack=requires_ack, command_label=method_name)
    if not apply_allowed:
        out = {"ok": True, "dry_run": True, "method": method_name, "auth_mode": auth["mode"], "plan": plan}
        if not ctx.get("apply") and ctx.get("plan_out"):
            out["plan_out"] = write_json_file(ctx["plan_out"], plan)
        ctx["audit"].write(f"{method_name}.plan", out)
        ctx["out"].emit(out)
        return 0
    loaded_plan = _load_plan(plan_in=ctx.get("plan_in"), expected_method=method_name, expected_selector=selector, ctx=ctx)
    response = _request_json(method=http_method, path=path, headers=auth["headers"], params=params, json_body=body, ctx=ctx)
    receipt = {
        "tool": ctx.get("tool") or "wix-safe-agent-cli",
        "version": ctx.get("tool_version") or None,
        "applied_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "method": method_name,
        "selector": selector,
        "request": request,
        "response": response,
        "changed": True,
        "verification": {"ok": True, "type": "provider-response", "notes": verification_notes},
        "diff_applied": loaded_plan.get("proposed_changes") or [],
        "backups": [],
        "rollback_plan": None,
        "recovery": {"automatic": False, "notes": "Recovery is manual only."},
    }
    out = {"ok": True, "dry_run": False, "method": method_name, "auth_mode": auth["mode"], "receipt": receipt}
    if ctx.get("receipt_out"):
        out["receipt_out"] = write_json_file(ctx["receipt_out"], receipt)
    ctx["audit"].write(f"{method_name}.apply", out)
    ctx["out"].emit(out)
    return 0


def cmd_blog_draft_posts_get(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.get"
    try:
        draft_post_id = _coerce_text(getattr(args, "draft_post_id", None), field="draft-post-id")
        params = _read_json_arg(getattr(args, "params_json", "{}"), field="params-json", allow_empty=True)
        return _run_read(method_name=method, http_method="GET", path=f"{BASE_PATH}/{draft_post_id}", params=params, body=None, ctx=ctx)
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_blog_draft_posts_query(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.query"
    try:
        body = _read_json_arg(getattr(args, "query_json", "{}"), field="query-json", allow_empty=True)
        return _run_read(method_name=method, http_method="POST", path=f"{BASE_PATH}/query", params=None, body=body, ctx=ctx)
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_blog_draft_posts_list(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.list"
    try:
        params = _read_json_arg(getattr(args, "params_json", "{}"), field="params-json", allow_empty=True)
        return _run_read(method_name=method, http_method="GET", path=BASE_PATH, params=params, body=None, ctx=ctx)
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_blog_draft_posts_get_deleted(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.get-deleted"
    try:
        draft_post_id = _coerce_text(getattr(args, "draft_post_id", None), field="draft-post-id")
        params = _read_json_arg(getattr(args, "params_json", "{}"), field="params-json", allow_empty=True)
        return _run_read(method_name=method, http_method="GET", path=f"{BASE_PATH}/trash-bin/{draft_post_id}", params=params, body=None, ctx=ctx)
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_blog_draft_posts_list_deleted(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.list-deleted"
    try:
        params = _read_json_arg(getattr(args, "params_json", "{}"), field="params-json", allow_empty=True)
        return _run_read(method_name=method, http_method="GET", path=f"{BASE_PATH}/trash-bin", params=params, body=None, ctx=ctx)
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def _write_body(args, *, attr: str, field: str) -> dict[str, Any]:
    return _read_json_arg(getattr(args, attr, None), field=field)


def cmd_blog_draft_posts_create(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.create"
    try:
        body = _write_body(args, attr="draft_post_json", field="draft-post-json")
        return _run_write(method_name=method, http_method="POST", path=BASE_PATH, params=None, body=body, selector={"kind": COMMAND_FAMILY, "operation": "create"}, proposed_changes=[{"operation": "create-draft-post", "body": body}], ctx=ctx, requires_ack=False, risk_reasons=["blog-draft-post-create"], verification_notes="Provider response confirms the Create Draft Post request was accepted.")
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_blog_draft_posts_update(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.update"
    try:
        draft_post_id = _coerce_text(getattr(args, "draft_post_id", None), field="draft-post-id")
        body = _write_body(args, attr="draft_post_json", field="draft-post-json")
        return _run_write(method_name=method, http_method="PATCH", path=f"{BASE_PATH}/{draft_post_id}", params=None, body=body, selector={"kind": COMMAND_FAMILY, "draft_post_id": draft_post_id, "operation": "update"}, proposed_changes=[{"operation": "update-draft-post", "draft_post_id": draft_post_id, "body": body}], ctx=ctx, requires_ack=False, risk_reasons=["blog-draft-post-update"], verification_notes="Provider response confirms the Update Draft Post request was accepted.")
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_blog_draft_posts_delete(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.delete"
    try:
        draft_post_id = _coerce_text(getattr(args, "draft_post_id", None), field="draft-post-id")
        permanent = bool(getattr(args, "permanent", False))
        params = {"permanent": True} if permanent else None
        return _run_write(method_name=method, http_method="DELETE", path=f"{BASE_PATH}/{draft_post_id}", params=params, body=None, selector={"kind": COMMAND_FAMILY, "draft_post_id": draft_post_id, "operation": "delete", "permanent": permanent}, proposed_changes=[{"operation": "delete-draft-post", "draft_post_id": draft_post_id, "permanent": permanent}], ctx=ctx, requires_ack=permanent, risk_reasons=["blog-draft-post-delete"] + (["permanent-delete-cannot-be-restored"] if permanent else ["moves-to-trash-bin"]), verification_notes="Provider response confirms the Delete Draft Post request was accepted.")
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_blog_draft_posts_bulk_create(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.bulk-create"
    try:
        body = _write_body(args, attr="draft_posts_json", field="draft-posts-json")
        return _run_write(method_name=method, http_method="POST", path=f"/blog/v3/bulk/draft-posts/create", params=None, body=body, selector={"kind": COMMAND_FAMILY, "operation": "bulk-create"}, proposed_changes=[{"operation": "bulk-create-draft-posts", "body": body}], ctx=ctx, requires_ack=False, risk_reasons=["blog-draft-post-bulk-create"], verification_notes="Provider response confirms the Bulk Create Draft Posts request was accepted.")
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_blog_draft_posts_bulk_update(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.bulk-update"
    try:
        body = _write_body(args, attr="draft_posts_json", field="draft-posts-json")
        return _run_write(method_name=method, http_method="PATCH", path=f"{BASE_PATH}/update", params=None, body=body, selector={"kind": COMMAND_FAMILY, "operation": "bulk-update"}, proposed_changes=[{"operation": "bulk-update-draft-posts", "body": body}], ctx=ctx, requires_ack=False, risk_reasons=["blog-draft-post-bulk-update"], verification_notes="Provider response confirms the Bulk Update Draft Posts request was accepted.")
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_blog_draft_posts_bulk_delete(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.bulk-delete"
    try:
        body = _write_body(args, attr="draft_posts_json", field="draft-posts-json")
        return _run_write(method_name=method, http_method="DELETE", path=f"/blog/v3/bulk/draft-posts", params=None, body=body, selector={"kind": COMMAND_FAMILY, "operation": "bulk-delete"}, proposed_changes=[{"operation": "bulk-delete-draft-posts", "body": body}], ctx=ctx, requires_ack=True, risk_reasons=["blog-draft-post-bulk-delete", "multi-draft-delete"], verification_notes="Provider response confirms the Bulk Delete Draft Posts request was accepted.")
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_blog_draft_posts_publish(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.publish"
    try:
        draft_post_id = _coerce_text(getattr(args, "draft_post_id", None), field="draft-post-id")
        body = _read_json_arg(getattr(args, "publish_json", "{}"), field="publish-json", allow_empty=True)
        return _run_write(method_name=method, http_method="POST", path=f"{BASE_PATH}/{draft_post_id}/publish", params=None, body=body, selector={"kind": COMMAND_FAMILY, "draft_post_id": draft_post_id, "operation": "publish"}, proposed_changes=[{"operation": "publish-draft-post", "draft_post_id": draft_post_id, "body": body}], ctx=ctx, requires_ack=False, risk_reasons=["blog-draft-post-publish", "public-content-change"], verification_notes="Provider response confirms the Publish Draft Post request was accepted.")
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_blog_draft_posts_remove_from_trash_bin(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.remove-from-trash-bin"
    try:
        draft_post_id = _coerce_text(getattr(args, "draft_post_id", None), field="draft-post-id")
        return _run_write(method_name=method, http_method="DELETE", path=f"{BASE_PATH}/trash-bin/{draft_post_id}", params=None, body=None, selector={"kind": COMMAND_FAMILY, "draft_post_id": draft_post_id, "operation": "remove-from-trash-bin"}, proposed_changes=[{"operation": "remove-draft-post-from-trash-bin", "draft_post_id": draft_post_id}], ctx=ctx, requires_ack=True, risk_reasons=["blog-draft-post-remove-from-trash-bin", "permanent-delete-cannot-be-restored"], verification_notes="Provider response confirms the Remove From Trash Bin request was accepted.")
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_blog_draft_posts_restore_from_trash_bin(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.restore-from-trash-bin"
    try:
        draft_post_id = _coerce_text(getattr(args, "draft_post_id", None), field="draft-post-id")
        body = _read_json_arg(getattr(args, "restore_json", "{}"), field="restore-json", allow_empty=True)
        return _run_write(method_name=method, http_method="POST", path=f"{BASE_PATH}/trash-bin/{draft_post_id}/restore", params=None, body=body, selector={"kind": COMMAND_FAMILY, "draft_post_id": draft_post_id, "operation": "restore-from-trash-bin"}, proposed_changes=[{"operation": "restore-draft-post-from-trash-bin", "draft_post_id": draft_post_id, "body": body}], ctx=ctx, requires_ack=False, risk_reasons=["blog-draft-post-restore-from-trash-bin"], verification_notes="Provider response confirms the Restore From Trash Bin request was accepted.")
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)
