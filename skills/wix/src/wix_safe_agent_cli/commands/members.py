from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from ..errors import SafetyError, ValidationError
from ..http import HttpClient
from ..json_files import read_json_file, write_json_file
from ..oauth_tokens import create_access_token, read_access_token_from_file, token_path_for_env_file
from ..write_safety import reviewed_plan_apply_requested


COMMAND_FAMILY = "members"


def _read_json_arg(raw: Any, field: str) -> Any:
    if raw is None:
        return None
    if not isinstance(raw, str):
        raise ValidationError(f"--{field} must be a JSON string, JSON file path, or omitted")

    text = raw.strip()
    if not text:
        raise ValidationError(f"--{field} cannot be empty")

    if text.startswith("@"):
        path = Path(text[1:])
        if not path.exists():
            raise ValidationError(f"--{field} file not found: {path}")
        text = path.read_text(encoding="utf-8").strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValidationError(f"Invalid JSON for --{field}: {exc.msg}") from exc


def _read_str_list(raw: Any, field: str) -> list[str] | None:
    if raw is None:
        return None
    value = _read_json_arg(raw, field=field)
    if not isinstance(value, list):
        raise ValidationError(f"--{field} must be a JSON array")
    for i, item in enumerate(value):
        if not isinstance(item, str):
            raise ValidationError(f"--{field}[{i}] must be a string")
    return value


def _coerce_text(raw: Any, *, field: str) -> str:
    if raw is None:
        raise ValidationError(f"Missing --{field}")
    if not isinstance(raw, str):
        raise ValidationError(f"--{field} must be a string")
    value = raw.strip()
    if not value:
        raise ValidationError(f"--{field} cannot be empty")
    return value


def _read_object_arg(raw: Any, *, field: str, allow_empty: bool = False) -> dict[str, Any]:
    value = _read_json_arg(raw, field=field)
    if not isinstance(value, dict):
        raise ValidationError(f"--{field} must be a JSON object")
    if not allow_empty and not value:
        raise ValidationError(f"--{field} cannot be empty")
    return value


def _read_member_ids_arg(raw: Any, *, field: str) -> dict[str, Any]:
    value = _read_json_arg(raw, field=field)
    if isinstance(value, dict):
        member_ids = value.get("memberIds")
        if not isinstance(member_ids, list):
            raise ValidationError(f"--{field} object must include memberIds array")
    elif isinstance(value, list):
        member_ids = value
        value = {"memberIds": member_ids}
    else:
        raise ValidationError(f"--{field} must be a JSON array or object with memberIds")
    for i, item in enumerate(member_ids):
        if not isinstance(item, str) or not item.strip():
            raise ValidationError(f"--{field}.memberIds[{i}] must be a non-empty string")
    return value


def _normalize_sort(sort_value: Any, field: str) -> list[dict[str, Any]] | dict[str, Any] | None:
    if sort_value is None:
        return None
    if isinstance(sort_value, list):
        if not sort_value:
            return []
        for i, item in enumerate(sort_value):
            if not isinstance(item, dict):
                raise ValidationError(f"Each item in --{field} must be an object")
            if not item:
                raise ValidationError(f"Item {i} in --{field} cannot be empty")
        return sort_value
    if isinstance(sort_value, dict):
        if not sort_value:
            raise ValidationError(f"--{field} cannot be empty")
        return sort_value
    raise ValidationError(f"--{field} must be an object or list of objects")


def _build_list_params(
    *,
    limit: int | None,
    offset: int | None,
    sort_value: Any,
    fieldsets: list[str] | None,
) -> dict[str, Any]:
    params: dict[str, Any] = {}
    if limit is not None:
        params["paging.limit"] = int(limit)
    if offset is not None:
        params["paging.offset"] = int(offset)

    if sort_value is not None:
        if isinstance(sort_value, list):
            sort_obj = sort_value[0]
        else:
            sort_obj = sort_value

        if isinstance(sort_obj, dict):
            if "fieldName" in sort_obj:
                params["sort.fieldName"] = str(sort_obj["fieldName"])
            if "order" in sort_obj:
                params["sort.order"] = str(sort_obj["order"])

    if fieldsets is not None:
        params["fieldsets"] = fieldsets
    return params


def _normalize_query_payload(
    *,
    query_json: dict[str, Any] | None,
    fieldsets: list[str] | None,
) -> dict[str, Any]:
    if query_json is not None:
        if "query" in query_json and isinstance(query_json["query"], dict):
            payload = dict(query_json)
            query_obj = payload["query"]
        else:
            payload = {"query": query_json}
            query_obj = payload["query"]
    else:
        payload = {"query": {}}
        query_obj = payload["query"]

    if not isinstance(query_obj, dict):
        raise ValidationError("Query payload must include a query object")

    if fieldsets is not None:
        query_obj["fieldsets"] = fieldsets
    return payload


def _resolve_access_token(*, cfg, env_file: str, verbose: bool) -> str:
    token = getattr(cfg, "access_token", None)
    if token:
        return str(token).strip()

    token_file = token_path_for_env_file(env_file)
    token = read_access_token_from_file(token_file)
    if token:
        return token

    if not bool(getattr(cfg, "has_official_app_auth", False)):
        raise ValidationError(
            "Missing official Wix credentials and no access token source. Add WIX_ACCESS_TOKEN or app credentials."
        )

    token_response = create_access_token(
        base_url=cfg.base_url,
        app_id=cfg.app_id,
        app_secret=cfg.app_secret,
        instance_id=cfg.instance_id,
        timeout_s=cfg.timeout_s,
        verbose=verbose,
    )
    access_token = token_response.get("access_token") if isinstance(token_response, dict) else None
    if not isinstance(access_token, str) or not access_token.strip():
        raise ValidationError("OAuth token response did not include access_token")
    return access_token.strip()


def _request_json(
    *,
    method: str,
    base_url: str,
    path: str,
    token: str,
    params: dict[str, Any] | None,
    json_body: dict[str, Any] | None,
    timeout_s: float,
    verbose: bool,
) -> dict[str, Any]:
    headers = {"Authorization": token}
    if method.upper() != "GET":
        headers["Content-Type"] = "application/json"

    client = HttpClient(timeout_s=timeout_s, verbose=verbose, user_agent="wix-safe-agent-cli")
    response = client.request(
        method=method,
        url=base_url.rstrip("/") + "/" + path.lstrip("/"),
        headers=headers,
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
        ctx["out"].emit(
            {
                "ok": True,
                "dry_run": True,
                "refused": True,
                "reasons": [str(exc)],
                "refusal_type": "SafetyError",
                "method": method,
            }
        )
        return 0
    if isinstance(exc, ValidationError):
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": method})
        return 1
    ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": method})
    return 1


def _build_request(*, method: str, path: str, body: dict[str, Any] | None = None) -> dict[str, Any]:
    request: dict[str, Any] = {"method": method, "path": path}
    if body is not None:
        request["body"] = body
    return request


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
        "state_capture": {
            "before_state_available": False,
            "notes": "Members plans use provider readbacks or responses for verification; no local rollback snapshot is available.",
        },
        "proposed_changes": proposed_changes,
        "verification_plan": {"type": "provider-response", "notes": verification_notes},
        "rollback": {"supported": False, "notes": "No automatic rollback. Use members get, members query, or the Wix dashboard to inspect state."},
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


def _run_read(*, method_name: str, http_method: str, path: str, params: dict[str, Any] | None, body: dict[str, Any] | None, ctx: dict[str, Any]) -> int:
    token = _resolve_access_token(cfg=ctx["cfg"], env_file=str(ctx["env_file"]), verbose=bool(ctx.get("verbose")))
    payload = _request_json(
        method=http_method,
        base_url=ctx["cfg"].base_url,
        path=path,
        token=token,
        params=params,
        json_body=body,
        timeout_s=float(ctx["cfg"].timeout_s),
        verbose=bool(ctx.get("verbose")),
    )
    request = _build_request(method=http_method, path=path, body=body)
    if params is not None:
        request["params"] = params
    out = {"ok": True, "method": method_name, "request": request, "response": payload}
    ctx["audit"].write(method_name, out)
    ctx["out"].emit(out)
    return 0


def _run_write(
    *,
    method_name: str,
    http_method: str,
    path: str,
    body: dict[str, Any] | None,
    selector: dict[str, Any],
    proposed_changes: list[dict[str, Any]],
    ctx: dict[str, Any],
    requires_ack: bool,
    risk_reasons: list[str],
    verification_notes: str,
) -> int:
    request = _build_request(method=http_method, path=path, body=body)
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
        out = {"ok": True, "dry_run": True, "method": method_name, "plan": plan}
        if not ctx.get("apply") and ctx.get("plan_out"):
            out["plan_out"] = write_json_file(ctx["plan_out"], plan)
        ctx["audit"].write(f"{method_name}.plan", out)
        ctx["out"].emit(out)
        return 0
    loaded_plan = _load_plan(plan_in=ctx.get("plan_in"), expected_method=method_name, expected_selector=selector, ctx=ctx)
    token = _resolve_access_token(cfg=ctx["cfg"], env_file=str(ctx["env_file"]), verbose=bool(ctx.get("verbose")))
    response = _request_json(
        method=http_method,
        base_url=ctx["cfg"].base_url,
        path=path,
        token=token,
        params=None,
        json_body=body,
        timeout_s=float(ctx["cfg"].timeout_s),
        verbose=bool(ctx.get("verbose")),
    )
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
    out = {"ok": True, "dry_run": False, "method": method_name, "receipt": receipt}
    if ctx.get("receipt_out"):
        out["receipt_out"] = write_json_file(ctx["receipt_out"], receipt)
    ctx["audit"].write(f"{method_name}.apply", out)
    ctx["out"].emit(out)
    return 0


def cmd_members_list(args, ctx) -> int:
    try:
        sort_value = _normalize_sort(_read_json_arg(getattr(args, "sort_json", None), field="sort-json"), field="sort-json")
        fieldsets = _read_str_list(getattr(args, "fieldsets_json", None), field="fieldsets-json")

        params = _build_list_params(
            limit=getattr(args, "limit", None),
            offset=getattr(args, "offset", None),
            sort_value=sort_value,
            fieldsets=fieldsets,
        )

        token = _resolve_access_token(
            cfg=ctx["cfg"],
            env_file=str(ctx["env_file"]),
            verbose=bool(ctx.get("verbose")),
        )
        payload = _request_json(
            method="GET",
            base_url=ctx["cfg"].base_url,
            path="/members/v1/members",
            token=token,
            params=params,
            json_body=None,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        out = {
            "ok": True,
            "method": "members.list",
            "request": {"method": "GET", "path": "/members/v1/members", "params": params},
            "response": payload,
        }
        ctx["audit"].write("members.list", out)
        ctx["out"].emit(out)
        return 0
    except ValidationError as exc:
        out = {"ok": False, "error": str(exc), "error_type": "ValidationError"}
        ctx["out"].emit(out)
        return 1
    except RuntimeError as exc:
        out = {"ok": False, "error": str(exc), "error_type": exc.__class__.__name__}
        ctx["out"].emit(out)
        return 1


def cmd_members_get(args, ctx) -> int:
    try:
        member_id = str(getattr(args, "member_id", "") or "").strip()
        if not member_id:
            raise ValidationError("Missing --member-id")

        fieldsets = _read_str_list(getattr(args, "fieldsets_json", None), field="fieldsets-json")
        params: dict[str, Any] = {}
        if fieldsets is not None:
            params["fieldsets"] = fieldsets

        token = _resolve_access_token(
            cfg=ctx["cfg"],
            env_file=str(ctx["env_file"]),
            verbose=bool(ctx.get("verbose")),
        )
        payload = _request_json(
            method="GET",
            base_url=ctx["cfg"].base_url,
            path=f"/members/v1/members/{member_id}",
            token=token,
            params=params,
            json_body=None,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        out = {
            "ok": True,
            "method": "members.get",
            "request": {"method": "GET", "path": f"/members/v1/members/{member_id}", "params": params},
            "response": payload,
        }
        ctx["audit"].write("members.get", out)
        ctx["out"].emit(out)
        return 0
    except ValidationError as exc:
        out = {"ok": False, "error": str(exc), "error_type": "ValidationError"}
        ctx["out"].emit(out)
        return 1
    except RuntimeError as exc:
        out = {"ok": False, "error": str(exc), "error_type": exc.__class__.__name__}
        ctx["out"].emit(out)
        return 1


def cmd_members_query(args, ctx) -> int:
    try:
        query_json = _read_json_arg(getattr(args, "query_json", None), field="query-json")
        if query_json is not None and not isinstance(query_json, dict):
            raise ValidationError("--query-json must be an object")

        fieldsets = _read_str_list(getattr(args, "fieldsets_json", None), field="fieldsets-json")
        body = _normalize_query_payload(query_json=query_json, fieldsets=fieldsets)

        token = _resolve_access_token(
            cfg=ctx["cfg"],
            env_file=str(ctx["env_file"]),
            verbose=bool(ctx.get("verbose")),
        )
        payload = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path="/members/v1/members/query",
            token=token,
            params=None,
            json_body=body,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        out = {
            "ok": True,
            "method": "members.query",
            "request": {"method": "POST", "path": "/members/v1/members/query", "body": body},
            "response": payload,
        }
        ctx["audit"].write("members.query", out)
        ctx["out"].emit(out)
        return 0
    except ValidationError as exc:
        out = {"ok": False, "error": str(exc), "error_type": "ValidationError"}
        ctx["out"].emit(out)
        return 1
    except RuntimeError as exc:
        out = {"ok": False, "error": str(exc), "error_type": exc.__class__.__name__}
        ctx["out"].emit(out)
        return 1


def cmd_members_get_my(args, ctx) -> int:
    method = "members.get-my"
    try:
        return _run_read(method_name=method, http_method="GET", path="/members/v1/members/my", params=None, body=None, ctx=ctx)
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_members_create(args, ctx) -> int:
    method = "members.create"
    try:
        body = _read_object_arg(getattr(args, "member_json", None), field="member-json")
        return _run_write(
            method_name=method,
            http_method="POST",
            path="/members/v1/members",
            body=body,
            selector={"kind": COMMAND_FAMILY, "operation": "create"},
            proposed_changes=[{"operation": "create-member", "body": body}],
            ctx=ctx,
            requires_ack=False,
            risk_reasons=["member-create", "official-docs-say-space-multiple-create-requests-at-least-one-second-apart"],
            verification_notes="Provider response confirms the Create Member request was accepted.",
        )
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_members_update(args, ctx) -> int:
    method = "members.update"
    try:
        member_id = _coerce_text(getattr(args, "member_id", None), field="member-id")
        body = _read_object_arg(getattr(args, "member_json", None), field="member-json")
        return _run_write(
            method_name=method,
            http_method="PATCH",
            path=f"/members/v1/members/{member_id}",
            body=body,
            selector={"kind": COMMAND_FAMILY, "member_id": member_id, "operation": "update"},
            proposed_changes=[{"operation": "update-member", "member_id": member_id, "body": body}],
            ctx=ctx,
            requires_ack=False,
            risk_reasons=["member-update", "official-docs-say-contact-arrays-overwrite-existing-array-values"],
            verification_notes="Provider response confirms the Update Member request was accepted.",
        )
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_members_delete(args, ctx) -> int:
    method = "members.delete"
    try:
        member_id = _coerce_text(getattr(args, "member_id", None), field="member-id")
        return _run_write(
            method_name=method,
            http_method="DELETE",
            path=f"/members/v1/members/{member_id}",
            body=None,
            selector={"kind": COMMAND_FAMILY, "member_id": member_id, "operation": "delete"},
            proposed_changes=[{"operation": "delete-member", "member_id": member_id}],
            ctx=ctx,
            requires_ack=True,
            risk_reasons=["member-delete", "official-docs-say-member-content-is-transferred-to-site-owner"],
            verification_notes="Provider response confirms the Delete Member request was accepted.",
        )
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_members_delete_my(args, ctx) -> int:
    method = "members.delete-my"
    try:
        body = _read_object_arg(getattr(args, "delete_json", "{}"), field="delete-json", allow_empty=True)
        return _run_write(
            method_name=method,
            http_method="DELETE",
            path="/members/v1/members/my",
            body=body,
            selector={"kind": COMMAND_FAMILY, "operation": "delete-my"},
            proposed_changes=[{"operation": "delete-current-member", "body": body}],
            ctx=ctx,
            requires_ack=True,
            risk_reasons=["delete-current-member", "official-docs-say-member-is-logged-out-and-content-is-transferred"],
            verification_notes="Provider response confirms the Delete My Member request was accepted.",
        )
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_members_bulk_delete(args, ctx) -> int:
    method = "members.bulk-delete"
    try:
        body = _read_member_ids_arg(getattr(args, "member_ids_json", None), field="member-ids-json")
        return _run_write(
            method_name=method,
            http_method="POST",
            path="/members/v1/members/bulk/delete",
            body=body,
            selector={"kind": COMMAND_FAMILY, "operation": "bulk-delete", "member_ids": body["memberIds"]},
            proposed_changes=[{"operation": "bulk-delete-members", "member_ids": body["memberIds"]}],
            ctx=ctx,
            requires_ack=True,
            risk_reasons=["bulk-member-delete", "official-docs-say-member-content-is-transferred-to-site-owner"],
            verification_notes="Provider response confirms the Bulk Delete Members request was accepted.",
        )
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def _run_member_action(args, ctx, *, action: str, requires_ack: bool, risk_reasons: list[str], verification_notes: str) -> int:
    method = f"members.{action}"
    try:
        member_id = _coerce_text(getattr(args, "member_id", None), field="member-id")
        return _run_write(
            method_name=method,
            http_method="POST",
            path=f"/members/v1/members/{member_id}/{action}",
            body=None,
            selector={"kind": COMMAND_FAMILY, "member_id": member_id, "operation": action},
            proposed_changes=[{"operation": action, "member_id": member_id}],
            ctx=ctx,
            requires_ack=requires_ack,
            risk_reasons=risk_reasons,
            verification_notes=verification_notes,
        )
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_members_approve(args, ctx) -> int:
    return _run_member_action(
        args,
        ctx,
        action="approve",
        requires_ack=False,
        risk_reasons=["member-approve-or-unblock"],
        verification_notes="Provider response confirms the Approve Member request was accepted.",
    )


def cmd_members_block(args, ctx) -> int:
    return _run_member_action(
        args,
        ctx,
        action="block",
        requires_ack=False,
        risk_reasons=["member-block", "blocked-members-cannot-log-in"],
        verification_notes="Provider response confirms the Block Member request was accepted.",
    )


def cmd_members_mute(args, ctx) -> int:
    return _run_member_action(
        args,
        ctx,
        action="mute",
        requires_ack=False,
        risk_reasons=["member-mute", "muted-members-cannot-engage-with-community-content"],
        verification_notes="Provider response confirms the Mute Member request was accepted.",
    )


def cmd_members_unmute(args, ctx) -> int:
    return _run_member_action(
        args,
        ctx,
        action="unmute",
        requires_ack=False,
        risk_reasons=["member-unmute"],
        verification_notes="Provider response confirms the Unmute Member request was accepted.",
    )


def cmd_members_disconnect(args, ctx) -> int:
    return _run_member_action(
        args,
        ctx,
        action="disconnect",
        requires_ack=True,
        risk_reasons=["member-disconnect", "official-docs-say-disconnect-is-irreversible"],
        verification_notes="Provider response confirms the Disconnect Member request was accepted.",
    )


def _run_bulk_filter_action(
    args,
    ctx,
    *,
    command_name: str,
    endpoint_action: str,
    field: str,
    risk_reasons: list[str],
    requires_ack: bool = False,
) -> int:
    method = f"members.{command_name}"
    try:
        body = _read_object_arg(getattr(args, field.replace("-", "_")), field=field)
        return _run_write(
            method_name=method,
            http_method="POST",
            path=f"/members/v1/members/bulk/{endpoint_action}-by-filter",
            body=body,
            selector={"kind": COMMAND_FAMILY, "operation": command_name, "filter_body": body},
            proposed_changes=[{"operation": command_name, "body": body}],
            ctx=ctx,
            requires_ack=requires_ack,
            risk_reasons=risk_reasons,
            verification_notes=f"Provider response confirms the {command_name.replace('-', ' ').title()} request was accepted.",
        )
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_members_bulk_approve(args, ctx) -> int:
    return _run_bulk_filter_action(
        args,
        ctx,
        command_name="bulk-approve",
        endpoint_action="approve",
        field="filter-json",
        risk_reasons=["bulk-approve-or-unblock-members"],
    )


def cmd_members_bulk_block(args, ctx) -> int:
    return _run_bulk_filter_action(
        args,
        ctx,
        command_name="bulk-block",
        endpoint_action="block",
        field="filter-json",
        risk_reasons=["bulk-block-members", "blocked-members-cannot-log-in"],
    )


def cmd_members_bulk_delete_by_filter(args, ctx) -> int:
    return _run_bulk_filter_action(
        args,
        ctx,
        command_name="bulk-delete-by-filter",
        endpoint_action="delete",
        field="filter-json",
        risk_reasons=["bulk-delete-members-by-filter", "official-docs-say-member-content-is-transferred-to-site-owner"],
        requires_ack=True,
    )


def _run_clear_contact_field(args, ctx, *, field_name: str) -> int:
    method = f"members.delete-{field_name}"
    try:
        member_id = _coerce_text(getattr(args, "member_id", None), field="member-id")
        return _run_write(
            method_name=method,
            http_method="DELETE",
            path=f"/members/v1/members/{member_id}/{field_name}",
            body=None,
            selector={"kind": COMMAND_FAMILY, "member_id": member_id, "operation": f"delete-{field_name}"},
            proposed_changes=[{"operation": f"clear-member-{field_name}", "member_id": member_id}],
            ctx=ctx,
            requires_ack=True,
            risk_reasons=[f"clear-member-{field_name}", "official-docs-say-this-clears-stored-contact-data"],
            verification_notes=f"Provider response confirms the Delete Member {field_name.title()} request was accepted.",
        )
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_members_delete_addresses(args, ctx) -> int:
    return _run_clear_contact_field(args, ctx, field_name="addresses")


def cmd_members_delete_emails(args, ctx) -> int:
    return _run_clear_contact_field(args, ctx, field_name="emails")


def cmd_members_delete_phones(args, ctx) -> int:
    return _run_clear_contact_field(args, ctx, field_name="phones")


def cmd_members_join_community(args, ctx) -> int:
    method = "members.join-community"
    try:
        return _run_write(
            method_name=method,
            http_method="POST",
            path="/members/v1/members/join-community",
            body=None,
            selector={"kind": COMMAND_FAMILY, "operation": "join-community"},
            proposed_changes=[{"operation": "join-current-member-community"}],
            ctx=ctx,
            requires_ack=False,
            risk_reasons=["current-member-profile-becomes-public"],
            verification_notes="Provider response confirms the Join Community request was accepted.",
        )
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_members_leave_community(args, ctx) -> int:
    method = "members.leave-community"
    try:
        return _run_write(
            method_name=method,
            http_method="POST",
            path="/members/v1/members/leave-community",
            body=None,
            selector={"kind": COMMAND_FAMILY, "operation": "leave-community"},
            proposed_changes=[{"operation": "leave-current-member-community"}],
            ctx=ctx,
            requires_ack=False,
            risk_reasons=["current-member-profile-becomes-private"],
            verification_notes="Provider response confirms the Leave Community request was accepted.",
        )
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_members_update_member_slug(args, ctx) -> int:
    method = "members.update-member-slug"
    try:
        member_id = _coerce_text(getattr(args, "member_id", None), field="member-id")
        slug = _coerce_text(getattr(args, "slug", None), field="slug")
        body = {"slug": slug}
        return _run_write(
            method_name=method,
            http_method="POST",
            path=f"/members/v1/members/{member_id}/slug",
            body=body,
            selector={"kind": COMMAND_FAMILY, "member_id": member_id, "operation": "update-member-slug"},
            proposed_changes=[{"operation": "update-member-slug", "member_id": member_id, "slug": slug}],
            ctx=ctx,
            requires_ack=False,
            risk_reasons=["member-slug-update"],
            verification_notes="Provider response confirms the Update Member Slug request was accepted.",
        )
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_members_update_my_slug(args, ctx) -> int:
    method = "members.update-my-slug"
    try:
        slug = _coerce_text(getattr(args, "slug", None), field="slug")
        body = {"slug": slug}
        return _run_write(
            method_name=method,
            http_method="POST",
            path="/members/v1/members/my/slug",
            body=body,
            selector={"kind": COMMAND_FAMILY, "operation": "update-my-slug"},
            proposed_changes=[{"operation": "update-current-member-slug", "slug": slug}],
            ctx=ctx,
            requires_ack=False,
            risk_reasons=["current-member-slug-update"],
            verification_notes="Provider response confirms the Update My Slug request was accepted.",
        )
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)
