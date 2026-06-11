from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path
from typing import Any

from ..api_client import GoogleBusinessProfileApiClient
from ..api_client import BUSINESS_INFORMATION_HOST
from ..errors import SafetyError, ValidationError
from ..json_files import read_json_file, write_json_file


def _utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _sha256(value: Any) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _normalize_mask(value: str) -> str:
    parts = [part.strip() for part in str(value).split(",")]
    return ",".join(part for part in parts if part)


def _validate_json_object(path: str, *, label: str) -> dict[str, Any]:
    data = read_json_file(path)
    if not isinstance(data, dict):
        raise ValidationError(f"{label} file must be a JSON object: {Path(path)}")
    if not data:
        raise ValidationError(f"{label} file must not be empty: {Path(path)}")
    return data


def _build_plan(
    *,
    operation: str,
    command: str,
    selector: str,
    tool: str,
    version: str,
    env_fingerprint: str,
    body: dict[str, Any],
    mask: str,
    risk_level: str,
    risk_reasons: list[str],
    verification_plan: list[str],
    preconditions: list[str],
    request_id: str | None = None,
) -> dict[str, Any]:
    proposed_change: dict[str, Any] = {
        "operation": operation,
        "selector": selector,
        "mask": mask,
        "body_fingerprint": _sha256(body),
    }
    if request_id is not None:
        proposed_change["request_id"] = request_id

    baseline: dict[str, Any] = {
        "selector": selector,
        "mask": mask,
        "body_fingerprint": _sha256(body),
        "mask_fingerprint": hashlib.sha256(mask.encode("utf-8")).hexdigest(),
    }
    if request_id is not None:
        baseline["request_id"] = request_id

    return {
        "tool": tool,
        "version": version,
        "generated_at_utc": _utc_now(),
        "env_fingerprint": env_fingerprint,
        "command": command,
        "selector": selector,
        "risk_level": risk_level,
        "risk_reasons": risk_reasons,
        "preconditions": preconditions,
        "proposed_changes": [proposed_change],
        "verification_plan": verification_plan,
        "rollback": {
            "supported": False,
            "notes": "No automated rollback is generated. Use the reviewed plan, receipt, and provider history for manual recovery.",
        },
        "before_state": {
            "required": True,
            "supported": False,
            "status": "no_snapshot_available",
            "approval_required": "--ack-no-snapshot",
            "statement": (
                "This Google Business Profile command has no reliable generic before-state snapshot. "
                "Apply may continue only after explicit no-snapshot approval."
            ),
        },
        "baseline": baseline,
    }


def _write_plan_if_needed(path: object, plan: dict[str, Any]) -> str | None:
    if not path:
        return None
    return str(write_json_file(str(path), plan))


def _write_receipt_if_needed(path: object, receipt: dict[str, Any]) -> str | None:
    if not path:
        return None
    return str(write_json_file(str(path), receipt))


def _require_matching_plan_in(
    *,
    plan_in: str,
    operation: str,
    selector: str,
    body: dict[str, Any],
    mask: str,
    request_id: str | None = None,
    plan_in_label: str = "--plan-in",
) -> None:
    plan = read_json_file(plan_in)
    if not isinstance(plan, dict):
        raise SafetyError(f"{plan_in_label} file is not a JSON object: {Path(plan_in)}")

    planned_operation = str(plan.get("operation") or "").strip()
    planned_selector = str(plan.get("selector") or "").strip()
    planned_baseline = plan.get("baseline")
    proposed_changes = plan.get("proposed_changes")
    if not planned_operation:
        if isinstance(proposed_changes, list) and proposed_changes:
            first_change = proposed_changes[0]
            if isinstance(first_change, dict):
                planned_operation = str(first_change.get("operation") or "").strip()
    if not planned_selector:
        if isinstance(proposed_changes, list) and proposed_changes:
            first_change = proposed_changes[0]
            if isinstance(first_change, dict):
                planned_selector = str(first_change.get("selector") or "").strip()

    if planned_operation != operation:
        raise SafetyError(
            f"Plan operation mismatch: expected {operation}, got {planned_operation} from {plan_in_label}."
        )

    if planned_selector != selector:
        raise SafetyError(
            f"Plan selector mismatch: expected {selector}, got {planned_selector} from {plan_in_label}."
        )

    baseline = planned_baseline
    if not isinstance(baseline, dict):
        if isinstance(plan.get("proposed_changes"), list) and plan["proposed_changes"]:
            first_change = plan["proposed_changes"][0]
            if isinstance(first_change, dict):
                baseline = {"mask": str(first_change.get("mask") or "").strip()}
    if not isinstance(baseline, dict):
        raise SafetyError(f"Plan missing baseline in {plan_in_label}: {plan_in}")

    baseline_body_fingerprint = baseline.get("body_fingerprint")
    if not isinstance(baseline_body_fingerprint, str):
        first_change = None
        if isinstance(plan.get("proposed_changes"), list) and plan["proposed_changes"]:
            maybe_change = plan["proposed_changes"][0]
            if isinstance(maybe_change, dict):
                first_change = maybe_change
        if isinstance(first_change, dict):
            baseline_body_fingerprint = first_change.get("body_fingerprint")
    if baseline_body_fingerprint != _sha256(body):
        raise SafetyError(f"Plan body fingerprint mismatch from {plan_in_label}: {plan_in}")

    expected_mask_fp = hashlib.sha256(mask.encode("utf-8")).hexdigest()
    mask_fingerprint = baseline.get("mask_fingerprint")
    if not isinstance(mask_fingerprint, str):
        plan_mask = str(baseline.get("mask") or "").strip()
        if plan_mask:
            mask_fingerprint = hashlib.sha256(plan_mask.encode("utf-8")).hexdigest()
    if mask_fingerprint != expected_mask_fp:
        raise SafetyError(f"Plan mask fingerprint mismatch from {plan_in_label}: {plan_in}")

    expected_request_id = str(request_id or "").strip()
    planned_request_id = str(baseline.get("request_id") or "").strip()
    if not planned_request_id:
        first_change = None
        if isinstance(plan.get("proposed_changes"), list) and plan["proposed_changes"]:
            maybe_change = plan["proposed_changes"][0]
            if isinstance(maybe_change, dict):
                first_change = maybe_change
        if isinstance(first_change, dict):
            planned_request_id = str(first_change.get("request_id") or "").strip()
    if planned_request_id != expected_request_id:
        raise SafetyError(f"Plan request-id mismatch from {plan_in_label}: {plan_in}")


def _build_receipt(
    *,
    command: str,
    selector: str,
    tool: str,
    version: str,
    env_fingerprint: str,
    changed: bool,
    verification: dict[str, Any],
    diff_applied: list[str],
) -> dict[str, Any]:
    return {
        "tool": tool,
        "version": version,
        "applied_at_utc": _utc_now(),
        "env_fingerprint": env_fingerprint,
        "command": command,
        "selector": selector,
        "before_state": {
            "required": True,
            "supported": False,
            "status": "no_snapshot_available",
            "approval_required": "--ack-no-snapshot",
            "statement": "No reliable generic before-state snapshot is available for this Google Business Profile command.",
        },
        "no_snapshot_approval": {
            "acknowledged": True,
            "flag": "--ack-no-snapshot",
            "reason": "No reliable generic before-state snapshot is available for this Google Business Profile command.",
        },
        "changed": changed,
        "verification": verification,
        "diff_applied": diff_applied,
        "backups": [],
        "rollback_plan": None,
    }


def _delete_verification(
    client: GoogleBusinessProfileApiClient,
    name: str,
) -> tuple[dict[str, Any], bool]:
    request = {
        "method": "GET",
        "host": BUSINESS_INFORMATION_HOST,
        "path": f"v1/{name}",
        "params": {"readMask": "name"},
    }
    try:
        verify_response, verify_request = client.get_location(name=name, read_mask="name")
        request = verify_request
        return {
            "ok": False,
            "operation": "business-info.locations.get",
            "request": request,
            "response": verify_response,
            "note": "Delete request succeeded but the location is still readable.",
        }, False
    except RuntimeError as exc:
        message = str(exc)
        if "HTTP 404" in message:
            return {
                "ok": True,
                "operation": "business-info.locations.get",
                "request": request,
                "response": {
                    "not_found": True,
                    "status": 404,
                    "message": message,
                },
            }, True
        return {
            "ok": False,
            "operation": "business-info.locations.get",
            "request": request,
            "response": {
                "request_error": True,
                "error_type": "RuntimeError",
                "message": message,
            },
            "note": "Delete request succeeded but follow-up check could not confirm not-found.",
        }, False


def _emit_write_output(
    ctx: dict[str, Any],
    *,
    operation: str,
    dry_run: bool,
    payload_obj: dict[str, Any],
    artifact_path: str | None,
) -> int:
    payload = {
        "ok": True,
        "dry_run": dry_run,
        "operation": operation,
    }
    payload["plan" if dry_run else "receipt"] = payload_obj
    if artifact_path:
        payload["plan_path" if dry_run else "receipt_path"] = artifact_path
    payload_key = "plan" if dry_run else "receipt"
    ctx["audit"].write(f"api.{operation}.{payload_key}", payload_obj)
    ctx["out"].emit(payload)
    return 0


def _client_for_ctx(ctx: dict[str, Any]) -> GoogleBusinessProfileApiClient:
    return GoogleBusinessProfileApiClient(
        cfg=ctx["cfg"],
        env_file=ctx["env_file"],
        timeout_s=float(ctx["timeout_s"]),
        verbose=bool(ctx["verbose"]),
        ack_no_snapshot=bool(ctx.get("ack_no_snapshot")),
    )


def _emit(ctx: dict[str, Any], operation: str, request: dict[str, Any], response: dict[str, Any]) -> int:
    payload = {
        "ok": True,
        "operation": operation,
        "request": request,
        "response": response,
    }
    ctx["audit"].write(f"api.{operation}", payload)
    ctx["out"].emit(payload)
    return 0


def _require_resource(value: object, *, arg_name: str) -> str:
    text = str(value or "").strip()
    if not text:
        raise ValidationError(f"{arg_name} is required and must not be blank.")
    return text


def _optional_text(value: object) -> str | None:
    text = str(value or "").strip()
    return text or None


def _require_resource_list(values: object | None, *, arg_name: str) -> list[str]:
    if values is None:
        raise ValidationError(f"{arg_name} is required and must include at least one value.")
    if not isinstance(values, list) or len(values) == 0:
        raise ValidationError(f"{arg_name} is required and must include at least one value.")

    out: list[str] = []
    for value in values:
        text = str(value or "").strip()
        if not text:
            raise ValidationError(f"{arg_name} values must not be blank.")
        out.append(text)
    return out


def _read_location_object(path: str) -> dict[str, Any]:
    p = Path(path)
    if not p.exists():
        raise ValidationError(f"Location file not found: {p}")
    return _validate_json_object(str(p), label="Location")


def _validate_attributes_query_mode(args: Any) -> dict[str, Any]:
    parent = str(args.parent).strip() if getattr(args, "parent", None) else None
    category_name = str(args.category_name).strip() if getattr(args, "category_name", None) else None
    show_all = bool(args.show_all)
    region_code = str(args.region_code).strip() if getattr(args, "region_code", None) else None
    language_code = str(args.language_code).strip() if getattr(args, "language_code", None) else None

    modes = sum(1 for value in [parent, category_name, show_all] if value)
    if modes != 1:
        raise ValidationError(
            "Use exactly one of --parent, --category-name, or --show-all."
        )

    if not parent and (not region_code or not language_code):
        raise ValidationError("--region-code and --language-code are required when using --category-name or --show-all.")
    if parent and (region_code or language_code):
        raise ValidationError("--region-code and --language-code are not used with --parent mode.")

    return {
        "parent": parent,
        "category_name": category_name,
        "show_all": show_all,
        "region_code": region_code,
        "language_code": language_code,
    }


def cmd_accounts_locations_list(args: Any, ctx: dict[str, Any]) -> int:
    parent = _require_resource(args.parent, arg_name="--parent")
    read_mask = _require_resource(args.read_mask, arg_name="--read-mask")
    client = _client_for_ctx(ctx)
    response, request = client.list_business_info_locations(
        parent=parent,
        read_mask=read_mask,
        page_size=args.page_size,
        page_token=args.page_token,
        filter=_optional_text(args.filter),
        order_by=_optional_text(args.order_by),
    )
    return _emit(ctx, "business-info.accounts.locations.list", request, response)


def cmd_accounts_locations_create(args: Any, ctx: dict[str, Any]) -> int:
    parent = _require_resource(args.parent, arg_name="--parent")
    location_file = _require_resource(args.location_file, arg_name="--location-file")
    location_body = _validate_json_object(location_file, label="Location")

    validate_only = bool(args.validate_only)
    if validate_only and bool(ctx.get("apply")):
        raise ValidationError("--validate-only cannot be used with --apply.")

    operation = "business-info.accounts.locations.create"
    client = _client_for_ctx(ctx)
    request_id = _optional_text(args.request_id)
    selector = parent

    plan = _build_plan(
        operation=operation,
        command=str(ctx.get("command_str") or ""),
        selector=selector,
        tool=str(ctx["tool"]),
        version=str(ctx["tool_version"]),
        env_fingerprint=str(ctx["cfg"].base_url),
        body=location_body,
        mask="name",
        risk_level="medium",
        risk_reasons=["Location create"],
        preconditions=["OAuth access"],
        verification_plan=["Read the created location with locations get and readMask=name."],
        request_id=request_id,
    )

    if bool(ctx.get("apply")):
        plan_in = _optional_text(ctx.get("plan_in"))
        if not plan_in:
            raise SafetyError("--apply requires --plan-in for create.")
        _require_matching_plan_in(
            plan_in=plan_in,
            operation=operation,
            selector=selector,
            body=location_body,
            mask="name",
            request_id=request_id,
        )

        create_response, _ = client.create_location(
            parent=parent,
            body=location_body,
            validate_only=False,
            request_id=request_id,
        )
        created_name = str(create_response.get("name") or "").strip()
        if not created_name:
            raise ValidationError("Create response did not return a location name.")

        verify_response, verify_request = client.get_location(name=created_name, read_mask="name")
        verification = {
            "ok": True,
            "operation": "business-info.locations.get",
            "request": verify_request,
            "response": verify_response,
        }
        receipt = _build_receipt(
            command=str(ctx.get("command_str") or ""),
            selector=created_name,
            tool=str(ctx["tool"]),
            version=str(ctx["tool_version"]),
            env_fingerprint=str(ctx["cfg"].base_url),
            changed=True,
            verification=verification,
            diff_applied=["name"],
        )
        receipt_path = _write_receipt_if_needed(ctx.get("receipt_out"), receipt)
        return _emit_write_output(
            ctx,
            operation=operation,
            dry_run=False,
            payload_obj=receipt,
            artifact_path=receipt_path,
        )

    if validate_only:
        client.create_location(
            parent=parent,
            body=location_body,
            validate_only=True,
            request_id=request_id,
        )

    plan_path = _write_plan_if_needed(ctx.get("plan_out"), plan)
    return _emit_write_output(
        ctx,
        operation=operation,
        dry_run=True,
        payload_obj=plan,
        artifact_path=plan_path,
    )


def cmd_locations_get(args: Any, ctx: dict[str, Any]) -> int:
    name = _require_resource(args.name, arg_name="--name")
    read_mask = _require_resource(args.read_mask, arg_name="--read-mask")
    client = _client_for_ctx(ctx)
    response, request = client.get_location(name=name, read_mask=read_mask)
    return _emit(ctx, "business-info.locations.get", request, response)


def cmd_locations_get_attributes(args: Any, ctx: dict[str, Any]) -> int:
    name = _require_resource(args.name, arg_name="--name")
    client = _client_for_ctx(ctx)
    response, request = client.get_location_attributes(name=name)
    return _emit(ctx, "business-info.locations.get-attributes", request, response)


def cmd_locations_get_google_updated(args: Any, ctx: dict[str, Any]) -> int:
    name = _require_resource(args.name, arg_name="--name")
    read_mask = _require_resource(args.read_mask, arg_name="--read-mask")
    client = _client_for_ctx(ctx)
    response, request = client.get_location_google_updated(
        name=name,
        read_mask=read_mask,
    )
    return _emit(ctx, "business-info.locations.get-google-updated", request, response)


def cmd_attributes_list(args: Any, ctx: dict[str, Any]) -> int:
    mode = _validate_attributes_query_mode(args)
    client = _client_for_ctx(ctx)
    response, request = client.list_attributes(
        parent=mode["parent"],
        category_name=mode["category_name"],
        region_code=mode["region_code"],
        language_code=mode["language_code"],
        show_all=mode["show_all"],
        page_size=args.page_size,
        page_token=args.page_token,
    )
    return _emit(ctx, "business-info.attributes.list", request, response)


def cmd_categories_list(args: Any, ctx: dict[str, Any]) -> int:
    region_code = _require_resource(args.region_code, arg_name="--region-code")
    language_code = _require_resource(args.language_code, arg_name="--language-code")
    view = _require_resource(args.view, arg_name="--view").upper()
    client = _client_for_ctx(ctx)
    response, request = client.list_categories(
        region_code=region_code,
        language_code=language_code,
        view=view,
        filter=_optional_text(args.filter),
        page_size=args.page_size,
        page_token=args.page_token,
    )
    return _emit(ctx, "business-info.categories.list", request, response)


def cmd_categories_batch_get(args: Any, ctx: dict[str, Any]) -> int:
    names = _require_resource_list(args.names, arg_name="--names")
    region_code = _optional_text(args.region_code)
    language_code = _require_resource(args.language_code, arg_name="--language-code")
    view = _require_resource(args.view, arg_name="--view").upper()
    client = _client_for_ctx(ctx)
    response, request = client.batch_get_categories(
        names=names,
        language_code=language_code,
        view=view,
        region_code=region_code,
    )
    return _emit(ctx, "business-info.categories.batch-get", request, response)


def cmd_chains_search(args: Any, ctx: dict[str, Any]) -> int:
    chain_name = _require_resource(args.chain_name, arg_name="--chain-name")
    client = _client_for_ctx(ctx)
    response, request = client.search_chains(
        chain_name=chain_name,
        page_size=args.page_size,
    )
    return _emit(ctx, "business-info.chains.search", request, response)


def cmd_chains_get(args: Any, ctx: dict[str, Any]) -> int:
    name = _require_resource(args.name, arg_name="--name")
    client = _client_for_ctx(ctx)
    response, request = client.get_chain(name=name)
    return _emit(ctx, "business-info.chains.get", request, response)


def cmd_locations_attributes_get_google_updated(args: Any, ctx: dict[str, Any]) -> int:
    name = _require_resource(args.name, arg_name="--name")
    client = _client_for_ctx(ctx)
    response, request = client.get_location_attributes_google_updated(name=name)
    return _emit(ctx, "business-info.locations.attributes.get-google-updated", request, response)


def cmd_google_locations_search(args: Any, ctx: dict[str, Any]) -> int:
    query = _optional_text(args.query)
    location = _read_location_object(args.location_file) if args.location_file else None
    if query is None and location is None:
        raise ValidationError("Use exactly one of --query or --location-file.")
    if query is not None and location is not None:
        raise ValidationError("Use exactly one of --query or --location-file.")

    client = _client_for_ctx(ctx)
    response, request = client.search_google_locations(
        page_size=args.page_size,
        query=query,
        location=location,
    )
    return _emit(ctx, "business-info.google-locations.search", request, response)


def cmd_locations_patch(args: Any, ctx: dict[str, Any]) -> int:
    name = _require_resource(args.name, arg_name="--name")
    update_mask = _normalize_mask(_require_resource(args.update_mask, arg_name="--update-mask"))
    if not update_mask:
        raise ValidationError("--update-mask must contain at least one field.")

    location_file = _require_resource(args.location_file, arg_name="--location-file")
    location_body = _validate_json_object(location_file, label="Location")

    validate_only = bool(args.validate_only)
    if validate_only and bool(ctx.get("apply")):
        raise ValidationError("--validate-only cannot be used with --apply.")

    operation = "business-info.locations.patch"
    client = _client_for_ctx(ctx)

    plan = _build_plan(
        operation=operation,
        command=str(ctx.get("command_str") or ""),
        selector=name,
        tool=str(ctx["tool"]),
        version=str(ctx["tool_version"]),
        env_fingerprint=str(ctx["cfg"].base_url),
        body=location_body,
        mask=update_mask,
        risk_level="medium",
        risk_reasons=["Location metadata update"],
        preconditions=["OAuth access"],
        verification_plan=[
            "Read back the location using locations get and readMask if verification is practical."
        ],
    )

    if bool(ctx.get("apply")):
        plan_in = _optional_text(ctx.get("plan_in"))
        if plan_in:
            _require_matching_plan_in(
                plan_in=plan_in,
                operation=operation,
                selector=name,
                body=location_body,
                mask=update_mask,
            )

        _, _ = client.patch_location(
            name=name,
            update_mask=update_mask,
            body=location_body,
            validate_only=False,
        )
        verify_response, verify_request = client.get_location(name=name, read_mask=update_mask)
        verification = {
            "ok": True,
            "operation": "business-info.locations.get",
            "request": verify_request,
            "response": verify_response,
        }
        receipt = _build_receipt(
            command=str(ctx.get("command_str") or ""),
            selector=name,
            tool=str(ctx["tool"]),
            version=str(ctx["tool_version"]),
            env_fingerprint=str(ctx["cfg"].base_url),
            changed=True,
            verification=verification,
            diff_applied=[field.strip() for field in update_mask.split(",") if field.strip()],
        )
        receipt_path = _write_receipt_if_needed(ctx.get("receipt_out"), receipt)
        return _emit_write_output(
            ctx,
            operation=operation,
            dry_run=False,
            payload_obj=receipt,
            artifact_path=receipt_path,
        )

    if validate_only:
        _, _ = client.patch_location(
            name=name,
            update_mask=update_mask,
            body=location_body,
            validate_only=True,
        )

    plan_path = _write_plan_if_needed(ctx.get("plan_out"), plan)
    return _emit_write_output(
        ctx,
        operation=operation,
        dry_run=True,
        payload_obj=plan,
        artifact_path=plan_path,
    )


def cmd_locations_update_attributes(args: Any, ctx: dict[str, Any]) -> int:
    name = _require_resource(args.name, arg_name="--name")
    attribute_mask = _normalize_mask(
        _require_resource(args.attribute_mask, arg_name="--attribute-mask")
    )
    if not attribute_mask:
        raise ValidationError("--attribute-mask must contain at least one field.")

    attributes_file = _require_resource(args.attributes_file, arg_name="--attributes-file")
    attributes_body = _validate_json_object(attributes_file, label="Attributes")

    operation = "business-info.locations.update-attributes"
    client = _client_for_ctx(ctx)

    plan = _build_plan(
        operation=operation,
        command=str(ctx.get("command_str") or ""),
        selector=name,
        tool=str(ctx["tool"]),
        version=str(ctx["tool_version"]),
        env_fingerprint=str(ctx["cfg"].base_url),
        body=attributes_body,
        mask=attribute_mask,
        risk_level="medium",
        risk_reasons=["Location attributes update"],
        preconditions=["OAuth access"],
        verification_plan=["Read back the attributes with locations get-attributes."],
    )

    if bool(ctx.get("apply")):
        plan_in = _optional_text(ctx.get("plan_in"))
        if plan_in:
            _require_matching_plan_in(
                plan_in=plan_in,
                operation=operation,
                selector=name,
                body=attributes_body,
                mask=attribute_mask,
            )

        _, _ = client.update_attributes(
            name=name,
            attribute_mask=attribute_mask,
            body=attributes_body,
        )
        verify_response, verify_request = client.get_location_attributes(name=name)
        verification = {
            "ok": True,
            "operation": "business-info.locations.get-attributes",
            "request": verify_request,
            "response": verify_response,
        }
        receipt = _build_receipt(
            command=str(ctx.get("command_str") or ""),
            selector=name,
            tool=str(ctx["tool"]),
            version=str(ctx["tool_version"]),
            env_fingerprint=str(ctx["cfg"].base_url),
            changed=True,
            verification=verification,
            diff_applied=[field.strip() for field in attribute_mask.split(",") if field.strip()],
        )
        receipt_path = _write_receipt_if_needed(ctx.get("receipt_out"), receipt)
        return _emit_write_output(
            ctx,
            operation=operation,
            dry_run=False,
            payload_obj=receipt,
            artifact_path=receipt_path,
        )

    plan_path = _write_plan_if_needed(ctx.get("plan_out"), plan)
    return _emit_write_output(
        ctx,
        operation=operation,
        dry_run=True,
        payload_obj=plan,
        artifact_path=plan_path,
    )


def cmd_locations_delete(args: Any, ctx: dict[str, Any]) -> int:
    name = _require_resource(args.name, arg_name="--name")

    operation = "business-info.locations.delete"
    client = _client_for_ctx(ctx)

    plan = _build_plan(
        operation=operation,
        command=str(ctx.get("command_str") or ""),
        selector=name,
        tool=str(ctx["tool"]),
        version=str(ctx["tool_version"]),
        env_fingerprint=str(ctx["cfg"].base_url),
        body={},
        mask="name",
        risk_level="high",
        risk_reasons=["Location deletion is irreversible."],
        preconditions=["OAuth access"],
        verification_plan=[
            "Read the location with locations get and readMask=name; expected result is HTTP 404 (not found)."
        ],
    )

    if bool(ctx.get("apply")):
        plan_in = _optional_text(ctx.get("plan_in"))
        if not plan_in:
            raise SafetyError("--apply requires --plan-in for location delete.")
        if not bool(ctx.get("yes")):
            raise SafetyError("--apply requires --yes for location delete.")
        if not bool(ctx.get("ack_irreversible")):
            raise SafetyError("--apply requires --ack-irreversible for location delete.")

        _require_matching_plan_in(
            plan_in=plan_in,
            operation=operation,
            selector=name,
            body={},
            mask="name",
            plan_in_label="--plan-in",
        )

        _, _ = client.delete_location(name=name)
        verification, changed = _delete_verification(client=client, name=name)
        receipt = _build_receipt(
            command=str(ctx.get("command_str") or ""),
            selector=name,
            tool=str(ctx["tool"]),
            version=str(ctx["tool_version"]),
            env_fingerprint=str(ctx["cfg"].base_url),
            changed=changed,
            verification=verification,
            diff_applied=["name"],
        )
        receipt_path = _write_receipt_if_needed(ctx.get("receipt_out"), receipt)
        return _emit_write_output(
            ctx,
            operation=operation,
            dry_run=False,
            payload_obj=receipt,
            artifact_path=receipt_path,
        )

    plan_path = _write_plan_if_needed(ctx.get("plan_out"), plan)
    return _emit_write_output(
        ctx,
        operation=operation,
        dry_run=True,
        payload_obj=plan,
        artifact_path=plan_path,
    )
