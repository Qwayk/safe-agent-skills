from __future__ import annotations

import re
from typing import Any

from ..api_client import PLACE_ACTIONS_HOST, GoogleBusinessProfileApiClient
from ..errors import SafetyError
from .business_info import (
    _build_plan,
    _build_receipt,
    _client_for_ctx,
    _emit,
    _emit_write_output,
    _normalize_mask,
    _optional_text,
    _require_matching_plan_in,
    _require_resource,
    _validate_json_object,
    _write_plan_if_needed,
    _write_receipt_if_needed,
)

_UPDATE_MASK_FIELDS = frozenset({"uri", "placeActionType", "isPreferred"})
_PLACE_ACTION_TYPE_ENUM_RE = re.compile(r"^[A-Z][A-Z0-9_]*$")
_PLACE_ACTIONS_LIST_FILTER_RE = re.compile(r"^placeActionType=([A-Z][A-Z0-9_]*)$")
_META_LOCATION_FILTER_RE = re.compile(r"^location=locations/[^/\s]+$")
_META_REGION_FILTER_RE = re.compile(r"^region_code=[A-Za-z]{2}$")


def _validate_place_action_link_create_body(body: dict[str, Any]) -> None:
    missing_fields = []
    if "uri" not in body:
        missing_fields.append("uri")
    if "placeActionType" not in body:
        missing_fields.append("placeActionType")
    if missing_fields:
        missing = ", ".join(missing_fields)
        raise SafetyError(
            f"Create body must include: {missing}. "
            "Place action links require both uri and placeActionType."
        )


def _validate_place_action_links_update_mask(update_mask: str) -> None:
    requested = [part.strip() for part in update_mask.split(",") if part.strip()]
    invalid = [field for field in requested if field not in _UPDATE_MASK_FIELDS]
    if invalid:
        raise SafetyError(
            "Unsupported --update-mask fields: "
            f"{', '.join(invalid)}. "
            "Allowed fields are uri, placeActionType, isPreferred."
        )


def _validate_patch_body_name_consistency(name: str, body: dict[str, Any]) -> None:
    body_name = body.get("name")
    if body_name is not None and str(body_name).strip() != name:
        raise SafetyError(
            f"Place-action-link patch body name ({body_name}) must match --name ({name})."
        )


def _validate_place_action_links_filter(filter_value: str | None) -> str | None:
    if filter_value is None:
        return None
    if not _PLACE_ACTIONS_LIST_FILTER_RE.fullmatch(filter_value):
        raise SafetyError(
            "--filter for place-action-links list must be in the form placeActionType=<ENUM> "
            "with an official PlaceActionType enum value (for example DINING_RESERVATION)."
        )
    action_type = filter_value.split("=", 1)[1]
    if not _PLACE_ACTION_TYPE_ENUM_RE.fullmatch(action_type):
        raise SafetyError(
            f"Invalid PlaceActionType enum value: {action_type}. "
            "Use a value such as DINING_RESERVATION."
        )
    return filter_value


def _validate_place_action_type_metadata_filter(filter_value: str | None) -> str | None:
    if filter_value is None:
        return None
    if (
        _META_LOCATION_FILTER_RE.fullmatch(filter_value) is None
        and _META_REGION_FILTER_RE.fullmatch(filter_value) is None
    ):
        raise SafetyError(
            "--filter for place-action-type-metadata list must be one of: "
            "location=locations/{locationId}, region_code={CC}."
        )
    return filter_value


def _place_action_link_delete_verification(
    client: GoogleBusinessProfileApiClient,
    name: str,
) -> tuple[dict[str, Any], bool]:
    request = {
        "method": "GET",
        "host": PLACE_ACTIONS_HOST,
        "path": f"v1/{name}",
        "params": None,
    }
    try:
        verify_response, verify_request = client.get_place_action_link(name=name)
        request = verify_request
        return {
            "ok": False,
            "operation": "place-actions.locations.place-action-links.get",
            "request": request,
            "response": verify_response,
            "note": "Delete request succeeded but the place action link is still readable.",
        }, False
    except RuntimeError as exc:
        message = str(exc)
        if "HTTP 404" in message:
            return {
                "ok": True,
                "operation": "place-actions.locations.place-action-links.get",
                "request": request,
                "response": {
                    "not_found": True,
                    "status": 404,
                    "message": message,
                },
            }, True
        return {
            "ok": False,
            "operation": "place-actions.locations.place-action-links.get",
            "request": request,
            "response": {
                "request_error": True,
                "error_type": "RuntimeError",
                "message": message,
            },
            "note": "Delete request succeeded but follow-up check could not confirm non-existence.",
        }, False


def _place_action_link_patch_verification(
    client: GoogleBusinessProfileApiClient,
    name: str,
) -> tuple[dict[str, Any], bool]:
    verify_request: dict[str, Any] = {
        "method": "GET",
        "host": PLACE_ACTIONS_HOST,
        "path": f"v1/{name}",
    }
    try:
        verify_response, verify_request = client.get_place_action_link(name=name)
        returned_name = str(verify_response.get("name") or "").strip()
        if returned_name != name:
            return {
                "ok": False,
                "operation": "place-actions.locations.place-action-links.get",
                "request": verify_request,
                "response": verify_response,
                "note": f"Get response name mismatch. expected {name}, got {returned_name or '<empty>'}.",
            }, False
        return {
            "ok": True,
            "operation": "place-actions.locations.place-action-links.get",
            "request": verify_request,
            "response": verify_response,
        }, True
    except RuntimeError as exc:
        message = str(exc)
        return {
            "ok": False,
            "operation": "place-actions.locations.place-action-links.get",
            "request": verify_request,
            "response": {"request_error": True, "error_type": "RuntimeError", "message": message},
            "note": "Patch request succeeded but follow-up get could not confirm.",
        }, False


def cmd_locations_place_action_links_create(args: Any, ctx: dict[str, Any]) -> int:
    parent = _require_resource(args.parent, arg_name="--parent")
    place_action_link_file = _require_resource(
        args.place_action_link_file,
        arg_name="--place-action-link-file",
    )
    place_action_link_body = _validate_json_object(
        place_action_link_file,
        label="PlaceActionLink",
    )
    _validate_place_action_link_create_body(place_action_link_body)

    operation = "place-actions.locations.place-action-links.create"
    client = _client_for_ctx(ctx)
    plan = _build_plan(
        operation=operation,
        command=str(ctx.get("command_str") or ""),
        selector=parent,
        tool=str(ctx["tool"]),
        version=str(ctx["tool_version"]),
        env_fingerprint=PLACE_ACTIONS_HOST,
        body=place_action_link_body,
        mask="name",
        risk_level="medium",
        risk_reasons=["Place action link create"],
        preconditions=["OAuth access"],
        verification_plan=[
            "Create the place action link, then read it back by name using get.",
        ],
    )

    if bool(ctx.get("apply")):
        plan_in = _optional_text(ctx.get("plan_in"))
        if not plan_in:
            raise SafetyError("--apply requires --plan-in for place-action-links create.")
        _require_matching_plan_in(
            plan_in=plan_in,
            operation=operation,
            selector=parent,
            body=place_action_link_body,
            mask="name",
        )

        create_response, create_request = client.create_place_action_link(
            parent=parent,
            body=place_action_link_body,
        )
        created_name = str(create_response.get("name") or "").strip()
        if created_name:
            verify_response, verify_request = client.get_place_action_link(name=created_name)
            verification = {
                "ok": True,
                "operation": "place-actions.locations.place-action-links.get",
                "request": verify_request,
                "response": verify_response,
            }
            selector = created_name
            changed = True
        else:
            verification = {
                "ok": False,
                "operation": operation,
                "request": create_request,
                "response": create_response,
                "note": "Create response did not include a name; verification could not confirm.",
            }
            selector = parent
            changed = True

        receipt = _build_receipt(
            command=str(ctx.get("command_str") or ""),
            selector=selector,
            tool=str(ctx["tool"]),
            version=str(ctx["tool_version"]),
            env_fingerprint=PLACE_ACTIONS_HOST,
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


def cmd_locations_place_action_links_delete(args: Any, ctx: dict[str, Any]) -> int:
    name = _require_resource(args.name, arg_name="--name")

    operation = "place-actions.locations.place-action-links.delete"
    client = _client_for_ctx(ctx)
    plan = _build_plan(
        operation=operation,
        command=str(ctx.get("command_str") or ""),
        selector=name,
        tool=str(ctx["tool"]),
        version=str(ctx["tool_version"]),
        env_fingerprint=PLACE_ACTIONS_HOST,
        body={},
        mask="name",
        risk_level="high",
        risk_reasons=["Place action link deletion is irreversible."],
        preconditions=["OAuth access"],
        verification_plan=[
            "Read back the same place action link with get; expected result is HTTP 404 (not found).",
        ],
    )

    if bool(ctx.get("apply")):
        plan_in = _optional_text(ctx.get("plan_in"))
        if not plan_in:
            raise SafetyError("--apply requires --plan-in for place-action-links delete.")
        if not bool(ctx.get("yes")):
            raise SafetyError("--apply requires --yes for place-action-links delete.")

        _require_matching_plan_in(
            plan_in=plan_in,
            operation=operation,
            selector=name,
            body={},
            mask="name",
        )

        _, _ = client.delete_place_action_link(name=name)
        verification, changed = _place_action_link_delete_verification(client=client, name=name)
        receipt = _build_receipt(
            command=str(ctx.get("command_str") or ""),
            selector=name,
            tool=str(ctx["tool"]),
            version=str(ctx["tool_version"]),
            env_fingerprint=PLACE_ACTIONS_HOST,
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


def cmd_locations_place_action_links_get(args: Any, ctx: dict[str, Any]) -> int:
    name = _require_resource(args.name, arg_name="--name")

    operation = "place-actions.locations.place-action-links.get"
    client = _client_for_ctx(ctx)
    response, request = client.get_place_action_link(name=name)
    return _emit(ctx, operation, request, response)


def cmd_locations_place_action_links_list(args: Any, ctx: dict[str, Any]) -> int:
    parent = _require_resource(args.parent, arg_name="--parent")
    filter_value = _validate_place_action_links_filter(_optional_text(args.filter))
    client = _client_for_ctx(ctx)
    response, request = client.list_place_action_links(
        parent=parent,
        page_size=args.page_size,
        page_token=args.page_token,
        filter=filter_value,
    )
    return _emit(ctx, "place-actions.locations.place-action-links.list", request, response)


def cmd_locations_place_action_links_patch(args: Any, ctx: dict[str, Any]) -> int:
    name = _require_resource(args.name, arg_name="--name")
    update_mask = _normalize_mask(_require_resource(args.update_mask, arg_name="--update-mask"))
    if not update_mask:
        raise SafetyError("--update-mask must contain at least one field.")
    _validate_place_action_links_update_mask(update_mask)

    place_action_link_file = _require_resource(
        args.place_action_link_file,
        arg_name="--place-action-link-file",
    )
    place_action_link_body = _validate_json_object(place_action_link_file, label="PlaceActionLink")
    _validate_patch_body_name_consistency(name, place_action_link_body)

    operation = "place-actions.locations.place-action-links.patch"
    client = _client_for_ctx(ctx)
    plan = _build_plan(
        operation=operation,
        command=str(ctx.get("command_str") or ""),
        selector=name,
        tool=str(ctx["tool"]),
        version=str(ctx["tool_version"]),
        env_fingerprint=PLACE_ACTIONS_HOST,
        body=place_action_link_body,
        mask=update_mask,
        risk_level="medium",
        risk_reasons=["Place action link patch"],
        preconditions=["OAuth access"],
        verification_plan=[
            "Read back the place action link with get and require response.name equals request name.",
        ],
    )

    if bool(ctx.get("apply")):
        plan_in = _optional_text(ctx.get("plan_in"))
        if not plan_in:
            raise SafetyError("--apply requires --plan-in for place-action-links patch.")
        _require_matching_plan_in(
            plan_in=plan_in,
            operation=operation,
            selector=name,
            body=place_action_link_body,
            mask=update_mask,
        )

        _, _ = client.patch_place_action_link(
            name=name,
            update_mask=update_mask,
            body=place_action_link_body,
        )
        verification, changed = _place_action_link_patch_verification(client=client, name=name)
        receipt = _build_receipt(
            command=str(ctx.get("command_str") or ""),
            selector=name,
            tool=str(ctx["tool"]),
            version=str(ctx["tool_version"]),
            env_fingerprint=PLACE_ACTIONS_HOST,
            changed=changed,
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

    plan_path = _write_plan_if_needed(ctx.get("plan_out"), plan)
    return _emit_write_output(
        ctx,
        operation=operation,
        dry_run=True,
        payload_obj=plan,
        artifact_path=plan_path,
    )


def cmd_place_action_type_metadata_list(args: Any, ctx: dict[str, Any]) -> int:
    client = _client_for_ctx(ctx)
    filter_value = _validate_place_action_type_metadata_filter(_optional_text(args.filter))
    response, request = client.list_place_action_type_metadata(
        language_code=_optional_text(args.language_code),
        page_size=args.page_size,
        page_token=args.page_token,
        filter=filter_value,
    )
    return _emit(ctx, "place-actions.place-action-type-metadata.list", request, response)
