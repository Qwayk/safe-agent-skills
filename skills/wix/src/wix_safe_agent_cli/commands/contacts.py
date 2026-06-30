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


def _read_required_object(raw: Any, *, field: str) -> dict[str, Any]:
    payload = _read_json_arg(raw, field)
    if not isinstance(payload, dict):
        raise ValidationError(f"--{field} must be a JSON object")
    if not payload:
        raise ValidationError(f"--{field} cannot be empty")
    return payload


def _normalize_sort(sort_value: Any, *, field: str) -> list[dict[str, Any]] | dict[str, Any] | None:
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
    fields: list[str] | None,
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

        if "fieldName" in sort_obj:
            params["sort.fieldName"] = str(sort_obj["fieldName"])
        if "order" in sort_obj:
            params["sort.order"] = str(sort_obj["order"])

    if fields is not None:
        params["fields"] = fields
    if fieldsets is not None:
        params["fieldsets"] = fieldsets
    return params


def _normalize_query_payload(
    *,
    query_json: dict[str, Any] | None,
    filter_json: dict[str, Any] | None,
    sort_value: Any,
    search: str | None,
    fields: list[str] | None,
    limit: int | None,
    offset: int | None,
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
        if filter_json is not None:
            query_obj["filter"] = filter_json
        if search is not None:
            query_obj["search"] = search
        if sort_value is not None:
            query_obj["sort"] = sort_value
        if limit is not None or offset is not None:
            paging: dict[str, Any] = {}
            if limit is not None:
                paging["limit"] = int(limit)
            if offset is not None:
                paging["offset"] = int(offset)
            query_obj["paging"] = paging

    if fields is not None and isinstance(payload.get("query"), dict):
        payload["query"]["fields"] = fields
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


def _auth_token_for_ctx(ctx: dict[str, Any]) -> str:
    return _resolve_access_token(
        cfg=ctx["cfg"],
        env_file=str(ctx["env_file"]),
        verbose=bool(ctx.get("verbose")),
    )


def _run_read(
    *,
    method_name: str,
    http_method: str,
    path: str,
    ctx: dict[str, Any],
    params: dict[str, Any] | None = None,
    body: dict[str, Any] | None = None,
) -> int:
    token = _auth_token_for_ctx(ctx)
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
    request: dict[str, Any] = {"method": http_method, "path": path}
    if params:
        request["params"] = params
    if body is not None:
        request["body"] = body
    out = {"ok": True, "method": method_name, "request": request, "response": payload}
    ctx["audit"].write(method_name, out)
    ctx["out"].emit(out)
    return 0


def _build_write_plan(
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
            "notes": "Contacts V4 write plans in this slice do not capture a full before-state snapshot.",
        },
        "proposed_changes": proposed_changes,
        "verification_plan": {"type": "provider-response", "notes": verification_notes},
        "rollback": {
            "supported": False,
            "notes": "No automatic rollback. Use contacts get/query or contacts get-bulk-job when needed.",
        },
    }


def _load_plan(
    *,
    plan_in: str | None,
    expected_method: str,
    expected_selector: dict[str, Any],
    ctx: dict[str, Any],
) -> dict[str, Any]:
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
    body: dict[str, Any] | None,
    selector: dict[str, Any],
    proposed_changes: list[dict[str, Any]],
    ctx: dict[str, Any],
    requires_ack: bool,
    risk_reasons: list[str],
    verification_notes: str,
) -> int:
    token = _auth_token_for_ctx(ctx)
    request: dict[str, Any] = {"method": http_method, "path": path}
    if body is not None:
        request["body"] = body
    plan = _build_write_plan(
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


def cmd_contacts_list(args, ctx) -> int:
    try:
        sort_value = _normalize_sort(_read_json_arg(getattr(args, "sort_json", None), field="sort-json"), field="sort-json")
        fields = _read_str_list(getattr(args, "fields_json", None), field="fields-json")
        fieldsets = _read_str_list(getattr(args, "fieldsets_json", None), field="fieldsets-json")

        params = _build_list_params(
            limit=getattr(args, "limit", None),
            offset=getattr(args, "offset", None),
            sort_value=sort_value,
            fields=fields,
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
            path="/contacts/v4/contacts",
            token=token,
            params=params,
            json_body=None,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        out = {
            "ok": True,
            "method": "contacts.list",
            "request": {"method": "GET", "path": "/contacts/v4/contacts", "params": params},
            "response": payload,
        }
        ctx["audit"].write("contacts.list", out)
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


def cmd_contacts_get(args, ctx) -> int:
    try:
        contact_id = str(getattr(args, "contact_id", "") or "").strip()
        if not contact_id:
            raise ValidationError("Missing --contact-id")

        params: dict[str, Any] = {}
        fields = _read_str_list(getattr(args, "fields_json", None), field="fields-json")
        fieldsets = _read_str_list(getattr(args, "fieldsets_json", None), field="fieldsets-json")
        if fields is not None:
            params["fields"] = fields
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
            path=f"/contacts/v4/contacts/{contact_id}",
            token=token,
            params=params,
            json_body=None,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        out = {
            "ok": True,
            "method": "contacts.get",
            "request": {
                "method": "GET",
                "path": f"/contacts/v4/contacts/{contact_id}",
                "params": params,
            },
            "response": payload,
        }
        ctx["audit"].write("contacts.get", out)
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


def cmd_contacts_query(args, ctx) -> int:
    try:
        query_json = _read_json_arg(getattr(args, "query_json", None), field="query-json")
        if query_json is not None and not isinstance(query_json, dict):
            raise ValidationError("--query-json must be an object")

        filter_json = _read_json_arg(getattr(args, "filter_json", None), field="filter-json")
        if filter_json is not None and not isinstance(filter_json, dict):
            raise ValidationError("--filter-json must be an object")

        sort_value = _normalize_sort(_read_json_arg(getattr(args, "sort_json", None), field="sort-json"), field="sort-json")
        fields = _read_str_list(getattr(args, "fields_json", None), field="fields-json")
        search_text = str(getattr(args, "search", "") or "").strip() or None

        body = _normalize_query_payload(
            query_json=query_json,
            filter_json=filter_json,
            sort_value=sort_value,
            search=search_text,
            fields=fields,
            limit=getattr(args, "limit", None),
            offset=getattr(args, "offset", None),
        )

        token = _resolve_access_token(
            cfg=ctx["cfg"],
            env_file=str(ctx["env_file"]),
            verbose=bool(ctx.get("verbose")),
        )
        payload = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path="/contacts/v4/contacts/query",
            token=token,
            params=None,
            json_body=body,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        out = {
            "ok": True,
            "method": "contacts.query",
            "request": {"method": "POST", "path": "/contacts/v4/contacts/query", "body": body},
            "response": payload,
        }
        ctx["audit"].write("contacts.query", out)
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


def cmd_contacts_list_facets(args, ctx) -> int:
    method = "contacts.list-facets"
    try:
        return _run_read(method_name=method, http_method="GET", path="/contacts/v4/contacts/facets", ctx=ctx)
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_contacts_query_facets(args, ctx) -> int:
    method = "contacts.query-facets"
    try:
        body = _read_required_object(getattr(args, "query_json", None), field="query-json")
        if "query" not in body:
            body = {"query": body}
        return _run_read(method_name=method, http_method="POST", path="/contacts/v4/contacts/facets/query", ctx=ctx, body=body)
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_contacts_get_bulk_job(args, ctx) -> int:
    method = "contacts.get-bulk-job"
    try:
        job_id = _coerce_text(getattr(args, "job_id", None), field="job-id")
        return _run_read(method_name=method, http_method="GET", path=f"/contacts/v4/bulk/jobs/{job_id}", ctx=ctx)
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_contacts_preview_merge(args, ctx) -> int:
    method = "contacts.preview-merge"
    try:
        target_contact_id = _coerce_text(getattr(args, "target_contact_id", None), field="target-contact-id")
        body = _read_required_object(getattr(args, "merge_json", None), field="merge-json")
        return _run_read(
            method_name=method,
            http_method="POST",
            path=f"/contacts/v4/contacts/{target_contact_id}/preview-merge",
            ctx=ctx,
            body=body,
        )
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_contacts_create(args, ctx) -> int:
    method = "contacts.create"
    try:
        body = _read_required_object(getattr(args, "contact_json", None), field="contact-json")
        return _run_write(
            method_name=method,
            http_method="POST",
            path="/contacts/v4/contacts",
            body=body,
            selector={"kind": "contacts", "operation": "create"},
            proposed_changes=[{"operation": "create-contact", "body": body}],
            ctx=ctx,
            requires_ack=False,
            risk_reasons=["contact-create"],
            verification_notes="Provider response confirms Wix accepted the Create Contact request.",
        )
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_contacts_update(args, ctx) -> int:
    method = "contacts.update"
    try:
        contact_id = _coerce_text(getattr(args, "contact_id", None), field="contact-id")
        body = _read_required_object(getattr(args, "contact_json", None), field="contact-json")
        contact = body.get("contact")
        if not isinstance(contact, dict) or not str(contact.get("revision") or "").strip():
            raise ValidationError("--contact-json must include contact.revision for contacts update")
        return _run_write(
            method_name=method,
            http_method="PATCH",
            path=f"/contacts/v4/contacts/{contact_id}",
            body=body,
            selector={"kind": "contacts", "contact_id": contact_id, "operation": "update"},
            proposed_changes=[{"operation": "update-contact", "contact_id": contact_id, "body": body}],
            ctx=ctx,
            requires_ack=False,
            risk_reasons=["contact-update", "requires-current-revision"],
            verification_notes="Provider response confirms Wix accepted the Update Contact request.",
        )
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_contacts_delete(args, ctx) -> int:
    method = "contacts.delete"
    try:
        contact_id = _coerce_text(getattr(args, "contact_id", None), field="contact-id")
        return _run_write(
            method_name=method,
            http_method="DELETE",
            path=f"/contacts/v4/contacts/{contact_id}",
            body=None,
            selector={"kind": "contacts", "contact_id": contact_id, "operation": "delete"},
            proposed_changes=[{"operation": "delete-contact", "contact_id": contact_id}],
            ctx=ctx,
            requires_ack=True,
            risk_reasons=["contact-delete", "permanently-removes-contact"],
            verification_notes="Provider response confirms Wix accepted the Delete Contact request.",
        )
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_contacts_merge(args, ctx) -> int:
    method = "contacts.merge"
    try:
        target_contact_id = _coerce_text(getattr(args, "target_contact_id", None), field="target-contact-id")
        body = _read_required_object(getattr(args, "merge_json", None), field="merge-json")
        return _run_write(
            method_name=method,
            http_method="POST",
            path=f"/contacts/v4/contacts/{target_contact_id}/merge",
            body=body,
            selector={"kind": "contacts", "target_contact_id": target_contact_id, "operation": "merge"},
            proposed_changes=[{"operation": "merge-contacts", "target_contact_id": target_contact_id, "body": body}],
            ctx=ctx,
            requires_ack=True,
            risk_reasons=["contact-merge", "source-contacts-deleted-or-overwritten"],
            verification_notes="Provider response confirms Wix accepted the Merge Contacts request.",
        )
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_contacts_label(args, ctx) -> int:
    method = "contacts.label"
    try:
        contact_id = _coerce_text(getattr(args, "contact_id", None), field="contact-id")
        body = _read_required_object(getattr(args, "labels_json", None), field="labels-json")
        return _run_write(
            method_name=method,
            http_method="POST",
            path=f"/contacts/v4/contacts/{contact_id}/labels",
            body=body,
            selector={"kind": "contacts", "contact_id": contact_id, "operation": "label"},
            proposed_changes=[{"operation": "label-contact", "contact_id": contact_id, "body": body}],
            ctx=ctx,
            requires_ack=False,
            risk_reasons=["contact-label"],
            verification_notes="Provider response confirms Wix accepted the Label Contact request.",
        )
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_contacts_unlabel(args, ctx) -> int:
    method = "contacts.unlabel"
    try:
        contact_id = _coerce_text(getattr(args, "contact_id", None), field="contact-id")
        body = _read_required_object(getattr(args, "labels_json", None), field="labels-json")
        return _run_write(
            method_name=method,
            http_method="DELETE",
            path=f"/contacts/v4/contacts/{contact_id}/labels",
            body=body,
            selector={"kind": "contacts", "contact_id": contact_id, "operation": "unlabel"},
            proposed_changes=[{"operation": "unlabel-contact", "contact_id": contact_id, "body": body}],
            ctx=ctx,
            requires_ack=False,
            risk_reasons=["contact-unlabel"],
            verification_notes="Provider response confirms Wix accepted the Unlabel Contact request.",
        )
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_contacts_bulk_delete(args, ctx) -> int:
    method = "contacts.bulk-delete"
    try:
        body = _read_required_object(getattr(args, "bulk_json", None), field="bulk-json")
        if "filter" not in body and "search" not in body:
            raise ValidationError("--bulk-json must include filter or search for contacts bulk-delete")
        return _run_write(
            method_name=method,
            http_method="POST",
            path="/contacts/v4/bulk/contacts/delete",
            body=body,
            selector={"kind": "contacts", "operation": "bulk-delete"},
            proposed_changes=[{"operation": "bulk-delete-contacts", "body": body}],
            ctx=ctx,
            requires_ack=True,
            risk_reasons=["contact-bulk-delete", "can-delete-many-contacts"],
            verification_notes="Provider response confirms Wix started or accepted the Bulk Delete Contacts job.",
        )
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_contacts_bulk_update(args, ctx) -> int:
    method = "contacts.bulk-update"
    try:
        body = _read_required_object(getattr(args, "bulk_json", None), field="bulk-json")
        return _run_write(
            method_name=method,
            http_method="POST",
            path="/contacts/v4/bulk/contacts/update",
            body=body,
            selector={"kind": "contacts", "operation": "bulk-update"},
            proposed_changes=[{"operation": "bulk-update-contacts", "body": body}],
            ctx=ctx,
            requires_ack=True,
            risk_reasons=["contact-bulk-update", "can-update-many-contacts"],
            verification_notes="Provider response confirms Wix started or accepted the Bulk Update Contacts job.",
        )
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_contacts_bulk_label_unlabel(args, ctx) -> int:
    method = "contacts.bulk-label-unlabel"
    try:
        body = _read_required_object(getattr(args, "bulk_json", None), field="bulk-json")
        if "filter" not in body and "search" not in body:
            raise ValidationError("--bulk-json must include filter or search for contacts bulk-label-unlabel")
        return _run_write(
            method_name=method,
            http_method="POST",
            path="/contacts/v4/bulk/contacts/add-remove-labels",
            body=body,
            selector={"kind": "contacts", "operation": "bulk-label-unlabel"},
            proposed_changes=[{"operation": "bulk-label-unlabel-contacts", "body": body}],
            ctx=ctx,
            requires_ack=True,
            risk_reasons=["contact-bulk-label-unlabel", "can-change-labels-on-many-contacts"],
            verification_notes="Provider response confirms Wix started or accepted the Bulk Label and Unlabel Contacts job.",
        )
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)
