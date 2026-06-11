from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Any
from urllib.parse import quote

from ..errors import SafetyError, ValidationError
from ..http import HttpClient
from ..json_files import read_json_file, write_json_file
from ..operation_specs import OperationSpec, get_operation, list_operation_query_params, list_operations


_STATUS_ONLY_VERIFICATION_NOTE = (
    "Response status is the verification signal for this operation; no follow-up readback is currently wired."
)
BEFORE_STATE_REFUSAL_REASON = (
    "Refused: this Figma write has no saved before-state snapshot or provider recovery point. "
    "Review the plan, confirm the recovery limit, then re-run with --ack-no-snapshot."
)


def _build_no_recovery_contract(spec: OperationSpec) -> dict[str, Any]:
    return {
        "automatic_rollback": False,
        "end_state": "irreversible_and_clearly_labeled",
        "strategy": "no_inverse",
        "rollback_ready": False,
        "backups": [],
        "snapshots": [],
        "rollback_plan": None,
        "restore_note": (
            f"{spec.area}:{spec.op_key}: no automated rollback is available for this command; "
            "it is treated as irreversible and needs manual cleanup if removal is required."
        ),
    }


def _build_before_state_contract(spec: OperationSpec, payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "required": True,
        "supported": False,
        "status": "no_snapshot_available",
        "approval_required": "--ack-no-snapshot",
        "operation": f"{spec.area}:{spec.op_key}",
        "target": {
            "method": payload["method"],
            "path": payload["path"],
            "path_params": payload["path_params"],
            "query": payload["query"],
        },
        "saved_path": None,
        "provider_backup_id": None,
        "reason": (
            "No useful before-state snapshot or provider recovery point is captured for this Figma write. "
            "The write may still run after the reviewed plan and explicit no-snapshot approval."
        ),
    }


def _build_before_state_refusal_verification_plan() -> dict[str, Any]:
    return {
        "type": "best_effort_after_apply",
        "status": "requires-no-snapshot-approval",
        "requires_no_snapshot_approval": True,
        "notes": (
            "Apply can run after explicit no-snapshot approval, then records provider response "
            "and best-effort read-back when available."
        ),
    }


def _status_only_verification_note(spec: OperationSpec) -> str:
    if spec.safety.mode != "write":
        return "Read response is the verification signal for this operation."
    return _STATUS_ONLY_VERIFICATION_NOTE


def _spec_to_dict(spec: OperationSpec) -> dict[str, Any]:
    data = asdict(spec)
    if isinstance(data.get("safety"), dict):
        return data
    return data


def _pick_operation(area: str, op_key: str) -> OperationSpec:
    key = f"{area}:{op_key}"
    spec = get_operation(area, op_key)
    if not spec:
        raise ValidationError(f"Unknown operation {key}")
    return spec


def _arg_to_flag_name(arg_name: str) -> str:
    return arg_name.replace("-", "_")


def _query_arg_dest(param_name: str) -> str:
    return f"query__{param_name}"


def _build_path(path_template: str, path_params: dict[str, str]) -> str:
    output = path_template
    start = 0
    while True:
        open_pos = output.find("{", start)
        if open_pos < 0:
            break
        close_pos = output.find("}", open_pos + 1)
        if close_pos < 0:
            raise ValidationError(f"Invalid path template: {path_template}")
        key = output[open_pos + 1 : close_pos]
        if key not in path_params:
            raise ValidationError(f"Missing required path parameter: {key}")
        value = quote(str(path_params[key]), safe="")
        output = output[:open_pos] + value + output[close_pos + 1 :]
        start = open_pos + len(value)
    return output


def _build_headers(cfg, *, has_token: bool = True, include_auth: bool = True) -> dict[str, str]:
    headers: dict[str, str] = {}
    if not include_auth:
        return headers
    token = getattr(cfg, "token", None)
    if token is None or not str(token).strip():
        if has_token:
            raise ValidationError("Missing token. Set FIGMA_ACCESS_TOKEN or provide token.json for oauth mode.")
        return headers

    if getattr(cfg, "auth_mode", "personal") in {"personal", "plan"}:
        headers["X-Figma-Token"] = str(token)
    else:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def _validate_query(spec: OperationSpec, query: dict[str, str]) -> None:
    missing_query = [k for k in spec.required_query_params if k not in query]
    if missing_query:
        raise ValidationError(f"Missing required query parameters: {', '.join(missing_query)}")
    for group in getattr(spec, "required_query_exactly_one_of", []):
        present = [k for k in group if k in query]
        if not present:
            raise ValidationError(
                f"Missing required query group; provide exactly one of: {', '.join(group)}"
            )
        if len(present) > 1:
            raise ValidationError(f"Provide exactly one of query parameters: {', '.join(group)}")


def _request_payload(
    spec: OperationSpec,
    cfg,
    path_params: dict[str, str],
    query: dict[str, str],
    body: Any | None,
    *,
    include_auth: bool = True,
) -> dict[str, Any]:
    missing_path_params = [k for k in spec.required_path_params if k not in path_params]
    if missing_path_params:
        raise ValidationError(f"Missing required path parameters: {', '.join(missing_path_params)}")

    _validate_query(spec, query)
    request_path = _build_path(path_template=spec.path_template, path_params=path_params)
    headers = _build_headers(cfg, include_auth=include_auth)
    url = (cfg.base_url.rstrip("/") + request_path).rstrip()
    return {
        "operation": f"{spec.area}:{spec.op_key}",
        "method": spec.method,
        "path": request_path,
        "url": url,
        "query": query,
        "path_params": path_params,
        "headers": headers,
        "body": body,
        "base_url": cfg.base_url,
        "auth_mode": cfg.auth_mode,
    }


def _request_payload_from_template(
    *,
    cfg,
    method: str,
    path_template: str,
    path_params: dict[str, str],
    query: dict[str, str] | None,
    body: Any | None,
) -> dict[str, Any]:
    request_path = _build_path(path_template=path_template, path_params=path_params)
    return {
        "method": method,
        "path": request_path,
        "url": (cfg.base_url.rstrip("/") + request_path),
        "query": query or {},
        "headers": _build_headers(cfg),
        "body": body,
    }


def _parse_response(resp) -> dict[str, Any]:
    try:
        body_obj = resp.json()
    except Exception:
        body_obj = None
    return {
        "status": resp.status,
        "url": resp.url,
        "body_json": body_obj,
        "body_text": None if body_obj is not None else resp.text(),
    }


def _run_request(cfg, ctx: dict[str, Any], payload: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    client = HttpClient(
        timeout_s=cfg.timeout_s,
        verbose=bool(ctx.get("verbose", False)),
        user_agent=f"{ctx['tool']}/{ctx['tool_version']}",
    )
    response = client.request(
        payload["method"],
        payload["url"],
        headers=payload["headers"],
        params=payload["query"] or None,
        json_body=payload["body"],
    )
    return _parse_response(response), payload


def _run_http(payload: dict[str, Any], cfg, ctx: dict[str, Any]) -> dict[str, Any]:
    parsed, _ = _run_request(cfg, ctx, payload)
    return {
        "ok": True,
        "operation": {
            "area": payload["operation"].split(":")[0],
            "op_key": payload["operation"].split(":")[1],
        },
        "request": {
            "method": payload["method"],
            "path": payload["path"],
            "query": payload["query"],
            "body": payload["body"],
        },
        "response": parsed,
        "response_status": parsed["status"],
        "dry_run": False,
        "verification_note": _STATUS_ONLY_VERIFICATION_NOTE,
    }


def _dry_run_output(
    *,
    payload: dict[str, Any],
    operation: OperationSpec,
    env_fingerprint: str | None,
    verification_note: str,
) -> dict[str, Any]:
    plan = {
        "operation_id": payload["operation"],
        "method": payload["method"],
        "path": payload["path"],
        "url": payload["url"],
        "query": payload["query"],
        "body": payload["body"],
        "env_fingerprint": env_fingerprint,
        "verification_note": verification_note,
    }
    if operation.safety.mode == "write":
        plan["before_state"] = _build_before_state_contract(operation, payload)
        plan["verification_plan"] = _build_before_state_refusal_verification_plan()
        plan["post_apply_verification_note"] = verification_note
        plan["recovery"] = _build_no_recovery_contract(operation)
    out = {
        "ok": True,
        "operation": {
            "area": operation.area,
            "op_key": operation.op_key,
            "title": operation.title,
            "method": operation.method,
            "path_template": operation.path_template,
            "safety": asdict(operation.safety),
        },
        "request": {
            "method": payload["method"],
            "path": payload["path"],
            "url": payload["url"],
            "query": payload["query"],
            "body": payload["body"],
            "headers": {k: ("***REDACTED***" if k.lower() in {"authorization", "x-figma-token", "x_figma_token"} else v) for k, v in payload["headers"].items()},
            "verification_note": verification_note,
        },
        "dry_run": True,
        "plan": plan,
        "verification_note": verification_note,
    }
    return out


def _before_state_refusal_output(
    *,
    payload: dict[str, Any],
    operation: OperationSpec,
    env_fingerprint: str | None,
) -> dict[str, Any]:
    result = _dry_run_output(
        payload=payload,
        operation=operation,
        env_fingerprint=env_fingerprint,
        verification_note=(
            "Write apply needs explicit no-snapshot approval before provider HTTP."
        ),
    )
    result["dry_run"] = False
    result["refused"] = True
    result["reasons"] = [BEFORE_STATE_REFUSAL_REASON]
    result["refusal_type"] = "SafetyError"
    result["verification_plan"] = _build_before_state_refusal_verification_plan()
    return result


def _write_output_payload(path: str | None, obj: Any, *, overwrite: bool) -> None:
    if not path:
        return
    output = Path(path)
    if output.exists() and not overwrite:
        raise ValidationError(f"Output file exists: {output}. Use --overwrite to replace it.")
    if isinstance(obj, (dict, list)):
        write_json_file(output, obj)
        return
    if isinstance(obj, (str, bytes)):
        output.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(obj, bytes):
            output.write_bytes(obj)
        else:
            output.write_text(obj, encoding="utf-8")
        return
    write_json_file(output, obj)


def _validate_plan_in(plan_path: str | None, payload: dict[str, Any]) -> None:
    if not plan_path:
        return
    if not Path(plan_path).exists():
        raise ValidationError(f"Plan file not found: {plan_path}")
    data = read_json_file(plan_path)
    if not isinstance(data, dict):
        raise ValidationError("Plan file must be a JSON object")

    plan_request = data.get("request") if "request" in data else data.get("plan")
    if not isinstance(plan_request, dict):
        raise ValidationError("Plan missing request object")

    expected = {
        "method": payload["method"],
        "path": payload["path"],
        "query": payload["query"],
        "url": payload["url"],
    }

    for key, expected_value in expected.items():
        value = plan_request.get(key)
        if expected_value != value:
            raise ValidationError(f"Plan drift for {key}: expected {expected_value!r}, found {value!r}")

    plan_body = plan_request.get("body")
    if (payload.get("body") or None) != (plan_body or None):
        raise ValidationError("Plan drift for body")


def _extract_identifier(body: Any, keys: list[str]) -> str | None:
    if not isinstance(body, dict):
        return None
    for key in keys:
        value = body.get(key)
        if isinstance(value, str) and value:
            return value
    nested = body.get("comment")
    if isinstance(nested, dict):
        for key in keys:
            value = nested.get(key)
            if isinstance(value, str) and value:
                return value
    return None


def _extract_items(body: Any, *keys: str) -> list[dict[str, Any]]:
    if isinstance(body, list):
        return [x for x in body if isinstance(x, dict)]
    if not isinstance(body, dict):
        return []
    for key in keys:
        value = body.get(key)
        if isinstance(value, list):
            return [x for x in value if isinstance(x, dict)]
    return []


def _verify_comments_contains_id(cfg, ctx: dict[str, Any], file_key: str, comment_id: str) -> str:
    payload = _request_payload_from_template(
        cfg=cfg,
        method="GET",
        path_template="/v1/files/{file_key}/comments",
        path_params={"file_key": file_key},
        query={},
        body=None,
    )
    response, _ = _run_request(cfg, ctx, payload)
    if response["status"] != 200:
        return f"Readback not complete: comment list check returned HTTP {response['status']}."

    comments = _extract_items(response["body_json"], "comments")
    if any(item.get("id") == comment_id or item.get("comment_id") == comment_id for item in comments):
        return "Readback verified: comment exists."
    return "Readback did not find comment in file comments."


def _verify_comments_does_not_contain_id(cfg, ctx: dict[str, Any], file_key: str, comment_id: str) -> str:
    payload = _request_payload_from_template(
        cfg=cfg,
        method="GET",
        path_template="/v1/files/{file_key}/comments",
        path_params={"file_key": file_key},
        query={},
        body=None,
    )
    response, _ = _run_request(cfg, ctx, payload)
    if response["status"] != 200:
        return f"Readback not complete: comment list check returned HTTP {response['status']}."

    comments = _extract_items(response["body_json"], "comments")
    if any(item.get("id") == comment_id or item.get("comment_id") == comment_id for item in comments):
        return "Readback not complete: comment still visible."
    return "Readback verified: comment is not visible."


def _verify_comment_reaction(
    cfg,
    ctx: dict[str, Any],
    *,
    file_key: str,
    comment_id: str,
    emoji: str | None,
    should_exist: bool,
) -> str:
    if not emoji:
        return "Readback not attempted; emoji is missing in request body."

    payload = _request_payload_from_template(
        cfg=cfg,
        method="GET",
        path_template="/v1/files/{file_key}/comments/{comment_id}/reactions",
        path_params={"file_key": file_key, "comment_id": comment_id},
        query={},
        body=None,
    )
    response, _ = _run_request(cfg, ctx, payload)
    if response["status"] != 200:
        return f"Readback not complete: reaction check returned HTTP {response['status']}."

    reactions = _extract_items(response["body_json"], "reactions")
    has_emoji = any(item.get("emoji") == emoji for item in reactions)
    if should_exist:
        if has_emoji:
            return "Readback verified: reaction exists."
        return "Readback not complete: reaction not visible."

    if has_emoji:
        return "Readback not complete: reaction still present."
    return "Readback verified: reaction is not present."


def _verify_webhook(
    cfg,
    ctx: dict[str, Any],
    *,
    webhook_id: str,
    should_exist: bool,
) -> str:
    payload = _request_payload_from_template(
        cfg=cfg,
        method="GET",
        path_template="/v2/webhooks/{webhook_id}",
        path_params={"webhook_id": webhook_id},
        query={},
        body=None,
    )
    response, _ = _run_request(cfg, ctx, payload)
    if should_exist:
        if response["status"] != 200:
            return f"Readback not complete: webhook check returned HTTP {response['status']}."
        return "Readback verified: webhook exists."
    if response["status"] in (200, 404, 410):
        return "Readback verified: webhook not visible." if response["status"] != 200 else "Readback not complete: webhook still visible."
    return f"Readback not complete: webhook delete check returned HTTP {response['status']}."


def _verify_dev_resource_delete(cfg, ctx: dict[str, Any], *, file_key: str, dev_resource_id: str) -> str:
    payload = _request_payload_from_template(
        cfg=cfg,
        method="GET",
        path_template="/v1/files/{file_key}/dev_resources",
        path_params={"file_key": file_key},
        query={},
        body=None,
    )
    response, _ = _run_request(cfg, ctx, payload)
    if response["status"] != 200:
        return f"Readback not complete: dev resource list check returned HTTP {response['status']}."

    resources = _extract_items(response["body_json"], "dev_resources", "resources")
    if any(item.get("id") == dev_resource_id or item.get("dev_resource_id") == dev_resource_id for item in resources):
        return "Readback not complete: dev resource still visible."
    return "Readback verified: dev resource is not visible."


def _best_effort_verification(
    spec: OperationSpec,
    cfg,
    ctx: dict[str, Any],
    payload: dict[str, Any],
    response: dict[str, Any],
) -> str:
    strategy = getattr(spec, "verification_strategy", None)
    if not strategy:
        return _status_only_verification_note(spec)
    if not isinstance(response.get("body_json"), dict):
        return f"Readback not attempted: response body was not JSON for {spec.area}:{spec.op_key}."

    try:
        if strategy == "comment-post":
            comment_id = _extract_identifier(response["body_json"], ["id", "comment_id"])
            if not comment_id:
                return "Readback not attempted: create response did not return a comment id."
            return _verify_comments_contains_id(
                cfg,
                ctx,
                file_key=payload["path_params"]["file_key"],
                comment_id=comment_id,
            )
        if strategy == "comment-delete":
            file_key = payload["path_params"]["file_key"]
            comment_id = payload["path_params"]["comment_id"]
            return _verify_comments_does_not_contain_id(
                cfg,
                ctx,
                file_key=file_key,
                comment_id=comment_id,
            )
        if strategy == "comment-reaction-post":
            emoji = None
            if isinstance(payload["body"], dict):
                emoji = str(payload["body"].get("emoji") or "").strip() or None
            file_key = payload["path_params"]["file_key"]
            comment_id = payload["path_params"]["comment_id"]
            return _verify_comment_reaction(cfg, ctx, file_key=file_key, comment_id=comment_id, emoji=emoji, should_exist=True)
        if strategy == "comment-reaction-delete":
            file_key = payload["path_params"]["file_key"]
            comment_id = payload["path_params"]["comment_id"]
            emoji = str(response["body_json"].get("emoji", "") or "").strip()
            if not emoji and isinstance(response["body_json"], dict):
                emoji = str(response["body_json"].get("removed_emoji", "") or "").strip()
            if not emoji:
                # fallback: best effort from query argument
                emoji = str(payload["query"].get("emoji", "")).strip() or None
            return _verify_comment_reaction(cfg, ctx, file_key=file_key, comment_id=comment_id, emoji=emoji, should_exist=False)
        if strategy == "webhook-create" or strategy == "webhook-update":
            webhook_id = _extract_identifier(response["body_json"], ["id", "webhook_id"])
            if not webhook_id:
                return "Readback not attempted: webhook response did not return webhook id."
            return _verify_webhook(cfg, ctx, webhook_id=webhook_id, should_exist=True)
        if strategy == "webhook-delete":
            webhook_id = payload["path_params"]["webhook_id"]
            return _verify_webhook(cfg, ctx, webhook_id=webhook_id, should_exist=False)
        if strategy == "dev-resource-delete":
            dev_resource_id = payload["path_params"]["dev_resource_id"]
            file_key = payload["path_params"]["file_key"]
            return _verify_dev_resource_delete(cfg, ctx, file_key=file_key, dev_resource_id=dev_resource_id)
    except Exception as exc:
        return f"Readback not attempted: {exc}"

    return _status_only_verification_note(spec)


def _collect_path_params(spec: OperationSpec, args: Any) -> dict[str, str]:
    params: dict[str, str] = {}
    for name in spec.required_path_params:
        value = str(getattr(args, _arg_to_flag_name(name), "") or "").strip()
        if value:
            params[name] = value
    return params


def _collect_query_params(spec: OperationSpec, args: Any) -> dict[str, str]:
    query: dict[str, str] = {}
    for name in list_operation_query_params(spec):
        value = getattr(args, _query_arg_dest(name), None)
        if value is None:
            continue
        text = str(value).strip()
        if text == "":
            continue
        query[name] = text
    return query


def _enforce_apply_safety(spec: OperationSpec, apply: bool, yes: bool, ack_irreversible: bool) -> None:
    if spec.safety.mode != "write":
        return
    if not apply:
        return
    if spec.safety.requires_yes and not yes:
        raise SafetyError("Write operation requires --yes to apply")
    if spec.safety.requires_ack_irreversible and not ack_irreversible:
        raise SafetyError("Write operation requires --ack-irreversible to apply")


def cmd_operations_list(args, ctx) -> int:
    area = (getattr(args, "area", "") or "").strip() or None
    method = (getattr(args, "method", "") or "").strip().upper() or None
    contains = (getattr(args, "contains", "") or "").strip().lower() or None
    include_writes = bool(getattr(args, "include_writes", False))

    entries: list[dict[str, Any]] = []
    for spec in list_operations(
        area=area,
        method=method,
        include_writes=include_writes,
        contains=contains,
    ):
        entries.append(
            {
                "area": spec.area,
                "op_key": spec.op_key,
                "method": spec.method,
                "path_template": spec.path_template,
                "title": spec.title,
                "safety": spec.safety.mode,
            }
        )

    ctx["out"].emit({"ok": True, "count": len(entries), "operations": entries, "include_writes": include_writes})
    return 0


def cmd_operations_show(args, ctx) -> int:
    area = str(getattr(args, "area"))
    op_key = str(getattr(args, "op_key"))
    spec = _pick_operation(area, op_key)
    data = _spec_to_dict(spec)
    ctx["out"].emit({"ok": True, "operation": data})
    return 0


def cmd_operations_execute(args, ctx) -> int:
    area = str(getattr(args, "op_area", "")).strip()
    op_key = str(getattr(args, "op_key", "")).strip()
    spec = _pick_operation(area, op_key)

    cfg = ctx["cfg"]
    path_params = _collect_path_params(spec, args)
    query = _collect_query_params(spec, args)
    body_json_file = getattr(args, "body_json_file", None)
    apply = bool(ctx.get("apply"))
    yes = bool(ctx.get("yes"))
    ack_irreversible = bool(ctx.get("ack_irreversible"))
    env_fingerprint = ctx.get("env_fingerprint") or f"{cfg.base_url}:{cfg.auth_mode}"
    out_path = getattr(args, "out", None)
    overwrite = bool(getattr(args, "overwrite", False))

    body = None
    if body_json_file:
        body = read_json_file(body_json_file)
    elif spec.body_json_file_expected and spec.safety.mode == "write":
        raise ValidationError("body-json-file is required for this write operation")

    payload = _request_payload(
        spec,
        cfg,
        path_params,
        query,
        body,
        include_auth=spec.safety.mode != "write",
    )
    payload["operation"] = f"{spec.area}:{spec.op_key}"

    _validate_plan_in(getattr(args, "plan_in", None), payload)
    _enforce_apply_safety(spec, apply=apply, yes=yes, ack_irreversible=ack_irreversible)

    if spec.safety.mode == "write" and not apply:
        verification_note = (
            "Write operation is in dry-run mode; apply needs explicit no-snapshot approval before provider HTTP."
        )
        result = _dry_run_output(
            payload=payload,
            operation=spec,
            env_fingerprint=env_fingerprint,
            verification_note=verification_note,
        )
    elif spec.safety.mode == "write":
        if not bool(ctx.get("ack_no_snapshot")):
            result = _before_state_refusal_output(
                payload=payload,
                operation=spec,
                env_fingerprint=env_fingerprint,
            )
            ctx["audit"].write(
                "operation.refused",
                {
                    "operation": payload["operation"],
                    "reason": BEFORE_STATE_REFUSAL_REASON,
                    "before_state": result.get("plan", {}).get("before_state"),
                },
            )
        else:
            payload = _request_payload(
                spec,
                cfg,
                path_params,
                query,
                body,
                include_auth=True,
            )
            payload["operation"] = f"{spec.area}:{spec.op_key}"
            result = _run_http(payload, cfg, ctx)
            primary_response = result.get("response", {})
            verification = _best_effort_verification(spec, cfg, ctx, payload, primary_response)
            result["verification_note"] = verification
            result["request"] = {
                **result["request"],
                "verification_note": verification,
            }
            result["plan"] = {
                "operation_id": payload["operation"],
                "method": payload["method"],
                "path": payload["path"],
                "url": payload["url"],
                "query": payload["query"],
                "body": payload["body"],
                "env_fingerprint": env_fingerprint,
                "verification_note": verification,
                "before_state": _build_before_state_contract(spec, payload),
                "verification_plan": _build_before_state_refusal_verification_plan(),
                "recovery": _build_no_recovery_contract(spec),
                "no_snapshot_approval": {"approved": True, "flag": "--ack-no-snapshot"},
            }
            result["operation"] = {
                **result["operation"],
                "method": payload["method"],
                "path_template": spec.path_template,
                "title": spec.title,
                "safety": asdict(spec.safety),
            }
            result["env_fingerprint"] = env_fingerprint
    else:
        result = _run_http(payload, cfg, ctx)
        primary_response = result.get("response", {})
        verification = _best_effort_verification(spec, cfg, ctx, payload, primary_response)
        result["verification_note"] = verification
        result["request"] = {
            **result["request"],
            "verification_note": verification,
        }
        result["plan"] = {
            "operation_id": payload["operation"],
            "method": payload["method"],
            "path": payload["path"],
            "url": payload["url"],
            "query": payload["query"],
            "body": payload["body"],
            "env_fingerprint": env_fingerprint,
            "verification_note": verification,
        }
        result["operation"] = {
            **result["operation"],
            "method": payload["method"],
            "path_template": spec.path_template,
            "title": spec.title,
            "safety": asdict(spec.safety),
        }
        result["env_fingerprint"] = env_fingerprint

    plan_out = getattr(args, "plan_out", None) or ctx.get("plan_out")
    if plan_out:
        write_json_file(plan_out, result.get("plan") or result)

    if ctx.get("receipt_out") and not result.get("refused"):
        receipt = dict(result)
        receipt["receipt"] = {"operation_id": result["operation"]["area"] + ":" + result["operation"]["op_key"] if isinstance(result.get("operation"), dict) else None}
        write_json_file(ctx["receipt_out"], receipt)

    if out_path and not result.get("refused"):
        payload_output = result.get("response", result)
        if isinstance(payload_output, dict) and payload_output.get("body_json") is not None:
            output_obj = payload_output.get("body_json")
        else:
            output_obj = payload_output
        _write_output_payload(str(out_path), output_obj, overwrite=overwrite)

    ctx["out"].emit(result)
    return 0
