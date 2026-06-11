from __future__ import annotations

from pathlib import Path
from typing import Any

from ..api_client import BUSINESS_INFORMATION_HOST
from ..api_client import LEGACY_V49_HOST
from ..errors import SafetyError, ValidationError
from .business_info import (
    _emit,
    _build_plan,
    _build_receipt,
    _client_for_ctx,
    _emit_write_output,
    _optional_text,
    _require_matching_plan_in,
    _require_resource,
    _validate_json_object,
    _write_plan_if_needed,
    _write_receipt_if_needed,
)

_LEGACY_LOCATION_TRANSFER_READ_MASK = "name"
_LEGACY_LOCATION_TRANSFER_PAGE_SIZE = 200
_LEGACY_LOCATION_TRANSFER_PLAN_MASK = "name,to_account"
_LEGACY_REVIEW_REPLY_PLAN_MASK = "reviewReply"
_LEGACY_VERIFICATION_PLAN_MASK = "name"
_LEGACY_REVIEW_LIST_MAX_PAGE_SIZE = 50
_LEGACY_REVIEW_LIST_ALLOWED_ORDER_BY = {"rating", "rating desc", "updateTime desc"}
_LEGACY_VERIFICATION_PLAN_PIN_MASK = "[redacted]"


def _normalize_legacy_location_name(value: str) -> str:
    parts = [part.strip() for part in value.strip().strip("/").split("/") if part.strip()]
    if len(parts) != 4 or parts[0] != "accounts" or parts[2] != "locations":
        raise ValidationError("--name must be in accounts/{account}/locations/{location} format.")
    return f"{parts[0]}/{parts[1]}/{parts[2]}/{parts[3]}"


def _normalize_legacy_review_name(value: str) -> str:
    parts = [part.strip() for part in value.strip().strip("/").split("/") if part.strip()]
    if (
        len(parts) != 6
        or parts[0] != "accounts"
        or parts[2] != "locations"
        or parts[4] != "reviews"
    ):
        raise ValidationError("--name must be in accounts/{account}/locations/{location}/reviews/{review} format.")
    return f"{parts[0]}/{parts[1]}/{parts[2]}/{parts[3]}/{parts[4]}/{parts[5]}"


def _normalize_legacy_verification_name(value: str) -> str:
    parts = [part.strip() for part in value.strip().strip("/").split("/") if part.strip()]
    if (
        len(parts) != 6
        or parts[0] != "accounts"
        or parts[2] != "locations"
        or parts[4] != "verifications"
    ):
        raise ValidationError(
            "--name must be in accounts/{account}/locations/{location}/verifications/{verification} format."
        )
    return f"{parts[0]}/{parts[1]}/{parts[2]}/{parts[3]}/{parts[4]}/{parts[5]}"


def _read_secret_file(path: str, *, label: str) -> str:
    pin_path = Path(path)
    if not pin_path.exists():
        raise ValidationError(f"{label} file not found: {pin_path}")
    text = pin_path.read_text(encoding="utf-8").strip()
    if not text:
        raise ValidationError(f"{label} file must not be empty: {pin_path}")
    return text


def _legacy_verification_parent(value: str) -> str:
    parts = [part.strip() for part in value.strip().strip("/").split("/") if part.strip()]
    return f"{parts[0]}/{parts[1]}/{parts[2]}/{parts[3]}"


def _find_legacy_verification(
    list_response: dict[str, Any],
    verification_name: str,
) -> dict[str, Any] | None:
    verifications = list_response.get("verifications")
    if not isinstance(verifications, list):
        return None
    for verification in verifications:
        if not isinstance(verification, dict):
            continue
        if str(verification.get("name") or "").strip() == verification_name:
            return verification
    return None


def _normalize_review_order_by(value: str | None) -> str | None:
    order_by = str(value or "").strip()
    if not order_by:
        return None
    if order_by not in _LEGACY_REVIEW_LIST_ALLOWED_ORDER_BY:
        options = ", ".join(sorted(_LEGACY_REVIEW_LIST_ALLOWED_ORDER_BY))
        raise ValidationError(f"--order-by must be one of: {options}.")
    return order_by


def _normalize_review_page_size(value: int | None) -> int | None:
    if value is None:
        return None
    if value < 1:
        raise ValidationError("--page-size must be >= 1.")
    if value > _LEGACY_REVIEW_LIST_MAX_PAGE_SIZE:
        raise ValidationError("--page-size must be <= 50 for legacy-v49 reviews list.")
    return value


def _validate_review_reply(path: str) -> dict[str, Any]:
    reply = _validate_json_object(path, label="Review reply")
    if set(reply.keys()) != {"comment"}:
        raise ValidationError('Review reply file must contain only {"comment": "..."}.')
    comment = reply.get("comment")
    if not isinstance(comment, str) or not comment.strip():
        raise ValidationError('Review reply file must contain a non-empty string at "comment".')
    if len(comment.encode("utf-8")) > 4096:
        raise ValidationError('Review reply "comment" must be 4096 bytes or fewer.')
    return {"comment": comment}


def _normalize_account_resource(value: str, *, arg_name: str) -> str:
    parts = [part.strip() for part in value.strip().strip("/").split("/") if part.strip()]
    if len(parts) != 2 or parts[0] != "accounts":
        raise ValidationError(f"{arg_name} must be in accounts/{{account}} format.")
    return f"{parts[0]}/{parts[1]}"


def _source_account_from_legacy_location_name(name: str) -> str:
    parts = [part.strip() for part in name.strip().strip("/").split("/") if part.strip()]
    return f"{parts[0]}/{parts[1]}"


def _business_info_location_name_from_legacy_location_name(name: str) -> str:
    parts = [part.strip() for part in name.strip().strip("/").split("/") if part.strip()]
    return f"locations/{parts[3]}"


def _location_present_in_account(
    *,
    client,
    account_name: str,
    location_name: str,
) -> tuple[dict[str, Any], bool | None]:
    page_token = None
    request = {
        "operation": "business-info.accounts.locations.list",
        "method": "GET",
        "host": BUSINESS_INFORMATION_HOST,
        "path": f"v1/{account_name}/locations",
        "params": {
            "readMask": _LEGACY_LOCATION_TRANSFER_READ_MASK,
            "pageSize": _LEGACY_LOCATION_TRANSFER_PAGE_SIZE,
        },
    }

    while True:
        try:
            response, request = client.list_business_info_locations(
                parent=account_name,
                read_mask=_LEGACY_LOCATION_TRANSFER_READ_MASK,
                page_size=_LEGACY_LOCATION_TRANSFER_PAGE_SIZE,
                page_token=page_token,
                filter=None,
                order_by=None,
            )
        except Exception as exc:  # noqa: BLE001
            return (
                {
                    "ok": False,
                    "operation": "business-info.accounts.locations.list",
                    "request": request,
                    "response": {
                        "request_error": True,
                        "error_type": type(exc).__name__,
                        "message": str(exc),
                    },
                    "note": f"Could not read location list for {account_name}.",
                },
                None,
            )

        items = response.get("locations")
        if not isinstance(items, list):
            return (
                {
                    "ok": False,
                    "operation": "business-info.accounts.locations.list",
                    "request": request,
                    "response": response,
                    "note": f"Could not verify location presence because {account_name} location list is malformed.",
                },
                None,
            )

        for item in items:
            if not isinstance(item, dict):
                continue
            if str(item.get("name") or "").strip() == location_name:
                return (
                    {
                        "ok": True,
                        "operation": "business-info.accounts.locations.list",
                        "request": request,
                        "response": response,
                    },
                    True,
                )

        page_token = str(response.get("nextPageToken") or "").strip() or None
        if not page_token:
            return (
                {
                    "ok": True,
                    "operation": "business-info.accounts.locations.list",
                    "request": request,
                    "response": response,
                },
                False,
            )


def _verify_legacy_location_transfer(
    *,
    client,
    legacy_location_name: str,
    to_account: str,
    transfer_response: dict[str, Any],
) -> tuple[dict[str, Any], bool]:
    source_account = _source_account_from_legacy_location_name(legacy_location_name)
    location_name = _business_info_location_name_from_legacy_location_name(legacy_location_name)
    expected_legacy_name = f"{to_account}/locations/{location_name.split('/', 1)[1]}"

    source_result, source_has = _location_present_in_account(
        client=client,
        account_name=source_account,
        location_name=location_name,
    )
    if source_has is None:
        source_result["note"] = source_result.get("note") or (
            f"Could not verify transfer because source account {source_account} list check failed."
        )
        return source_result, False

    destination_result, destination_has = _location_present_in_account(
        client=client,
        account_name=to_account,
        location_name=location_name,
    )
    if destination_has is None:
        destination_result["note"] = destination_result.get("note") or (
            f"Could not verify transfer because destination account {to_account} list check failed."
        )
        return destination_result, False

    verification = {
        "ok": False,
        "operation": "legacy-v49.accounts.locations.transfer",
        "request": {
            "source": source_result.get("request"),
            "destination": destination_result.get("request"),
        },
        "response": {
            "transfer": transfer_response,
            "source": {
                "contains": source_has,
                "operation": "business-info.accounts.locations.list",
                "request": source_result.get("request"),
                "response": source_result.get("response"),
            },
            "destination": {
                "contains": destination_has,
                "operation": "business-info.accounts.locations.list",
                "request": destination_result.get("request"),
                "response": destination_result.get("response"),
            },
        },
    }

    response_name = str(transfer_response.get("name") or "").strip()
    if response_name and response_name != expected_legacy_name:
        verification["note"] = (
            f"Transfer response name {response_name} did not match expected destination resource {expected_legacy_name}."
        )
        return verification, False
    if source_has:
        verification["note"] = (
            f"Transfer did not remove location {location_name} from source account {source_account}."
        )
        return verification, False
    if not destination_has:
        verification["note"] = (
            f"Transfer did not place location {location_name} in destination account {to_account}."
        )
        return verification, False

    verification["ok"] = True
    verification["note"] = (
        "Legacy v4.9 transfer read-back verification succeeded: source account no longer lists "
        "the location and destination now lists it."
    )
    return verification, True


def _get_media_reference(response: dict[str, Any], fallback_to_source_url: bool = False) -> str:
    media_ref = response.get("mediaItemDataRef")
    if isinstance(media_ref, dict):
        name = media_ref.get("resourceName")
        if isinstance(name, str):
            return name.strip()

    media_ref = response.get("dataRef")
    if isinstance(media_ref, dict):
        name = media_ref.get("resourceName")
        if isinstance(name, str):
            return name.strip()

    if fallback_to_source_url:
        resource_name = response.get("resourceName")
        if isinstance(resource_name, str):
            return resource_name.strip()
        source_url = response.get("sourceUrl")
        if isinstance(source_url, str):
            return source_url.strip()

    return ""


def _get_media_item_reference(media_item: dict[str, Any]) -> str:
    candidate = media_item.get("mediaItemDataRef")
    if isinstance(candidate, dict):
        name = candidate.get("resourceName")
        if isinstance(name, str):
            return name.strip()

    candidate = media_item.get("dataRef")
    if isinstance(candidate, dict):
        name = candidate.get("resourceName")
        if isinstance(name, str):
            return name.strip()

    return ""


def _build_verification_for_start_upload(response: dict[str, Any]) -> tuple[dict[str, Any], bool]:
    media_ref = _get_media_reference(response, fallback_to_source_url=True)
    if not media_ref:
        return {
            "ok": False,
            "operation": "legacy-v49.accounts.locations.media.start-upload",
            "request": {
                "method": "POST",
                "host": LEGACY_V49_HOST,
                "path": "n/a",
            },
            "response": response,
            "note": (
                "No direct read-back verification is available for this legacy media start-upload; response did not "
                "contain mediaItemDataRef.resourceName, dataRef.resourceName, resourceName, or sourceUrl."
            ),
        }, False

    return {
        "ok": True,
        "operation": "legacy-v49.accounts.locations.media.start-upload",
        "request": {
            "method": "POST",
            "host": LEGACY_V49_HOST,
            "path": "n/a",
            },
            "response": response,
            "note": (
                "No direct read-back verification is available for this legacy media start-upload; response returned a "
                "media reference as mediaItemDataRef.resourceName, dataRef.resourceName, resourceName, or sourceUrl."
            ),
        }, True


def _build_verification_for_create(response: dict[str, Any], media_item: dict[str, Any]) -> tuple[dict[str, Any], bool]:
    request_data_ref = _get_media_item_reference(media_item)
    response_data_ref = _get_media_reference(response)
    if request_data_ref and response_data_ref and response_data_ref != request_data_ref:
        return {
            "ok": False,
            "operation": "legacy-v49.accounts.locations.media.create",
            "request": {
                "method": "POST",
                "host": LEGACY_V49_HOST,
                "path": "n/a",
                "body": media_item,
            },
            "response": response,
            "note": (
                "Create response returned a media reference, but it did not match the requested media item sourceUrl "
                "or mediaItemDataRef.resourceName/dataRef.resourceName."
            ),
        }, False

    request_source_url = media_item.get("sourceUrl")
    if isinstance(request_source_url, str):
        response_source_url = response.get("sourceUrl")
        if isinstance(response_source_url, str) and response_source_url != request_source_url:
            return {
                "ok": False,
                "operation": "legacy-v49.accounts.locations.media.create",
                "request": {
                    "method": "POST",
                    "host": LEGACY_V49_HOST,
                    "path": "n/a",
                    "body": media_item,
                },
                "response": response,
                "note": (
                    "Create response returned sourceUrl, but it did not match the requested media item source URL."
                ),
            }, False

    if not _get_media_reference(response, fallback_to_source_url=True):
        return {
            "ok": False,
            "operation": "legacy-v49.accounts.locations.media.create",
            "request": {
                "method": "POST",
                "host": LEGACY_V49_HOST,
                "path": "n/a",
                "body": media_item,
            },
            "response": response,
            "note": "No direct read-back verification is available for this legacy media create; response did not contain "
            "mediaItemDataRef.resourceName, dataRef.resourceName, resourceName, or sourceUrl.",
        }, False

    return {
        "ok": True,
        "operation": "legacy-v49.accounts.locations.media.create",
        "request": {
            "method": "POST",
            "host": LEGACY_V49_HOST,
            "path": "n/a",
            "body": media_item,
            },
            "response": response,
            "note": (
                "No direct read-back verification is available for this legacy media create; response returned a "
                "matching mediaItemDataRef.resourceName, dataRef.resourceName, resourceName, or sourceUrl."
            ),
        }, True


def _verify_legacy_review_reply_update(
    *,
    client,
    name: str,
    expected_comment: str,
) -> tuple[dict[str, Any], bool]:
    follow_up_request: dict[str, Any] = {
        "method": "GET",
        "host": LEGACY_V49_HOST,
        "path": f"v4/{name}",
    }
    try:
        follow_up_response, request = client.get_legacy_review(name=name)
        follow_up_request = request
    except Exception as exc:  # noqa: BLE001
        return {
            "ok": False,
            "operation": "legacy-v49.accounts.locations.reviews.update-reply",
            "request": follow_up_request,
            "response": {
                "request_error": True,
                "error_type": type(exc).__name__,
                "message": str(exc),
            },
            "note": "Review reply follow-up get failed after update-reply.",
        }, False

    reply = follow_up_response.get("reviewReply")
    if not isinstance(reply, dict):
        return {
            "ok": False,
            "operation": "legacy-v49.accounts.locations.reviews.update-reply",
            "request": follow_up_request,
            "response": follow_up_response,
            "note": "Review follow-up get did not contain a reviewReply object after update-reply.",
        }, False

    review_comment = str(reply.get("comment") or "").strip()
    if review_comment != expected_comment.strip():
        return {
            "ok": False,
            "operation": "legacy-v49.accounts.locations.reviews.update-reply",
            "request": follow_up_request,
            "response": follow_up_response,
            "note": "Review follow-up get returned a different reviewReply.comment than expected.",
        }, False

    return {
        "ok": True,
        "operation": "legacy-v49.accounts.locations.reviews.update-reply",
        "request": follow_up_request,
        "response": follow_up_response,
        "note": "Legacy review reply follow-up verification succeeded: reviewReply.comment matches expected value.",
    }, True


def _verify_legacy_review_reply_delete(*, client, name: str) -> tuple[dict[str, Any], bool]:
    follow_up_request: dict[str, Any] = {
        "method": "GET",
        "host": LEGACY_V49_HOST,
        "path": f"v4/{name}",
    }
    try:
        follow_up_response, request = client.get_legacy_review(name=name)
        follow_up_request = request
    except Exception as exc:  # noqa: BLE001
        return {
            "ok": False,
            "operation": "legacy-v49.accounts.locations.reviews.delete-reply",
            "request": follow_up_request,
            "response": {
                "request_error": True,
                "error_type": type(exc).__name__,
                "message": str(exc),
            },
            "note": "Review reply follow-up get failed after delete-reply.",
        }, False

    if "reviewReply" in follow_up_response:
        return {
            "ok": False,
            "operation": "legacy-v49.accounts.locations.reviews.delete-reply",
            "request": follow_up_request,
            "response": follow_up_response,
            "note": "Review follow-up get still contains reviewReply after delete-reply.",
        }, False

    return {
        "ok": True,
        "operation": "legacy-v49.accounts.locations.reviews.delete-reply",
        "request": follow_up_request,
        "response": follow_up_response,
        "note": "Legacy review reply follow-up verification succeeded: reviewReply is absent.",
    }, True


def _redact_request_pin(request: dict[str, Any]) -> dict[str, Any]:
    request_copy = dict(request)
    body = request_copy.get("body")
    if isinstance(body, dict) and "pin" in body:
        safe_body = dict(body)
        safe_body["pin"] = _LEGACY_VERIFICATION_PLAN_PIN_MASK
        request_copy["body"] = safe_body
    return request_copy


def _legacy_verification_name_from_response(response: dict[str, Any]) -> str:
    verification = response.get("verification")
    if isinstance(verification, dict):
        name = verification.get("name")
    else:
        name = response.get("name")
    return str(name or "").strip()


def _verify_legacy_verification_complete(
    *,
    client,
    response: dict[str, Any],
    complete_request: dict[str, Any],
) -> tuple[dict[str, Any], bool]:
    verification_name = _legacy_verification_name_from_response(response)
    if not verification_name:
        return {
            "ok": False,
            "operation": "legacy-v49.accounts.locations.verifications.complete",
            "request": _redact_request_pin(complete_request),
            "response": response,
            "note": "Complete response did not include verification.name; verification could not confirm.",
        }, False

    parent = _legacy_verification_parent(verification_name)
    if not parent:
        return {
            "ok": False,
            "operation": "legacy-v49.accounts.locations.verifications.complete",
            "request": _redact_request_pin(complete_request),
            "response": response,
            "note": "Could not derive parent location from returned verification.name.",
        }, False

    try:
        list_response, list_request = client.list_legacy_verifications(parent=parent)
    except Exception as exc:  # noqa: BLE001
        return {
            "ok": False,
            "operation": "legacy-v49.accounts.locations.verifications.list",
            "request": _redact_request_pin(complete_request),
            "response": {
                "request_error": True,
                "error_type": type(exc).__name__,
                "message": str(exc),
            },
            "note": "Could not run legacy verifications list follow-up; marking result as uncertain.",
        }, False

    found = _find_legacy_verification(list_response, verification_name)
    if not isinstance(found, dict):
        return {
            "ok": False,
            "operation": "legacy-v49.accounts.locations.verifications.list",
            "request": list_request,
            "response": list_response,
            "note": "Completed verification name was not found in legacy verifications list follow-up.",
        }, False

    state = str(found.get("state") or "").strip().upper()
    if state != "COMPLETED":
        return {
            "ok": False,
            "operation": "legacy-v49.accounts.locations.verifications.list",
            "request": list_request,
            "response": list_response,
            "note": f"Verification state was {state or 'UNKNOWN'}; expected COMPLETED.",
        }, False

    return {
        "ok": True,
        "operation": "legacy-v49.accounts.locations.verifications.list",
        "request": list_request,
        "response": list_response,
    }, True


def cmd_accounts_locations_media_start_upload(args: Any, ctx: dict[str, Any]) -> int:
    parent = _require_resource(args.parent, arg_name="--parent")
    operation = "legacy-v49.accounts.locations.media.start-upload"
    selector = parent
    client = _client_for_ctx(ctx)
    media_item: dict[str, Any] = {}
    verification_mask = "mediaItemDataRef"

    plan = _build_plan(
        operation=operation,
        command=str(ctx.get("command_str") or ""),
        selector=selector,
        tool=str(ctx["tool"]),
        version=str(ctx["tool_version"]),
        env_fingerprint=LEGACY_V49_HOST,
        body=media_item,
        mask=verification_mask,
        risk_level="medium",
        risk_reasons=["Media upload start marker"],
        preconditions=["OAuth access"],
        verification_plan=[
            "No direct read-back verification is available for this legacy media start-upload; success is inferred from "
            "response mediaItemDataRef.resourceName, dataRef.resourceName, resourceName, or sourceUrl."
        ],
    )

    if bool(ctx.get("apply")):
        plan_in = _optional_text(ctx.get("plan_in"))
        if not plan_in:
            raise SafetyError("--apply requires --plan-in for legacy media start-upload.")
        _require_matching_plan_in(
            plan_in=plan_in,
            operation=operation,
            selector=selector,
            body=media_item,
            mask=verification_mask,
        )

        response, _ = client.start_upload_location_media(parent=parent)
        verification, changed = _build_verification_for_start_upload(response=response)
        receipt = _build_receipt(
            command=str(ctx.get("command_str") or ""),
            selector=selector,
            tool=str(ctx["tool"]),
            version=str(ctx["tool_version"]),
            env_fingerprint=LEGACY_V49_HOST,
            changed=changed,
            verification=verification,
            diff_applied=[verification_mask],
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


def cmd_accounts_locations_media_create(args: Any, ctx: dict[str, Any]) -> int:
    parent = _require_resource(args.parent, arg_name="--parent")
    media_item_file = _require_resource(args.media_item_file, arg_name="--media-item-file")
    media_item = _validate_json_object(media_item_file, label="MediaItem")
    if not media_item:
        raise ValidationError("MediaItem file must not be empty.")

    operation = "legacy-v49.accounts.locations.media.create"
    selector = parent
    client = _client_for_ctx(ctx)
    verification_mask = "mediaItemDataRef"

    plan = _build_plan(
        operation=operation,
        command=str(ctx.get("command_str") or ""),
        selector=selector,
        tool=str(ctx["tool"]),
        version=str(ctx["tool_version"]),
        env_fingerprint=LEGACY_V49_HOST,
        body=media_item,
        mask=verification_mask,
        risk_level="medium",
        risk_reasons=["Media item metadata write"],
        preconditions=["OAuth access"],
        verification_plan=[
            "No direct read-back verification is available for this legacy media create; response should include "
            "mediaItemDataRef.resourceName, dataRef.resourceName, resourceName, or sourceUrl."
        ],
    )

    if bool(ctx.get("apply")):
        plan_in = _optional_text(ctx.get("plan_in"))
        if not plan_in:
            raise SafetyError("--apply requires --plan-in for legacy media create.")
        _require_matching_plan_in(
            plan_in=plan_in,
            operation=operation,
            selector=selector,
            body=media_item,
            mask=verification_mask,
        )

        response, _ = client.create_location_media(parent=parent, media_item=media_item)
        verification, changed = _build_verification_for_create(response=response, media_item=media_item)
        receipt = _build_receipt(
            command=str(ctx.get("command_str") or ""),
            selector=selector,
            tool=str(ctx["tool"]),
            version=str(ctx["tool_version"]),
            env_fingerprint=LEGACY_V49_HOST,
            changed=changed,
            verification=verification,
            diff_applied=[verification_mask],
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


def cmd_accounts_locations_transfer(args: Any, ctx: dict[str, Any]) -> int:
    operation = "legacy-v49.accounts.locations.transfer"
    name = _normalize_legacy_location_name(_require_resource(args.name, arg_name="--name"))
    to_account = _normalize_account_resource(_require_resource(args.to_account, arg_name="--to-account"), arg_name="--to-account")
    source_account = _source_account_from_legacy_location_name(name)
    if source_account == to_account:
        raise ValidationError("--name source account and --to-account must be different accounts.")

    body = {
        "name": name,
        "to_account": to_account,
    }
    plan = _build_plan(
        operation=operation,
        command=str(ctx.get("command_str") or ""),
        selector=name,
        tool=str(ctx["tool"]),
        version=str(ctx["tool_version"]),
        env_fingerprint=LEGACY_V49_HOST,
        body=body,
        mask=_LEGACY_LOCATION_TRANSFER_PLAN_MASK,
        risk_level="high",
        risk_reasons=["Legacy v4.9 location transfer changes account ownership for a location."],
        preconditions=["OAuth access", "Google still permits this deprecated v4.9 method for the target account."],
        verification_plan=[
            "List source and destination account locations with readMask=name. Transfer succeeds only if the business-info location disappears from source and appears in destination.",
        ],
    )

    if bool(ctx.get("apply")):
        plan_in = _optional_text(ctx.get("plan_in"))
        if not plan_in:
            raise SafetyError("--apply requires --plan-in for legacy-v49 accounts locations transfer.")
        if not bool(ctx.get("yes")):
            raise SafetyError("--apply requires --yes for legacy-v49 accounts locations transfer.")
        if not bool(ctx.get("ack_irreversible")):
            raise SafetyError("--apply requires --ack-irreversible for legacy-v49 accounts locations transfer.")
        _require_matching_plan_in(
            plan_in=plan_in,
            operation=operation,
            selector=name,
            body=body,
            mask=_LEGACY_LOCATION_TRANSFER_PLAN_MASK,
        )

        client = _client_for_ctx(ctx)
        response, _ = client.transfer_legacy_location(name=name, to_account=to_account)
        verification, changed = _verify_legacy_location_transfer(
            client=client,
            legacy_location_name=name,
            to_account=to_account,
            transfer_response=response,
        )
        receipt = _build_receipt(
            command=str(ctx.get("command_str") or ""),
            selector=name,
            tool=str(ctx["tool"]),
            version=str(ctx["tool_version"]),
            env_fingerprint=LEGACY_V49_HOST,
            changed=changed,
            verification=verification,
            diff_applied=["name", "to_account"],
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


def cmd_accounts_locations_verifications_list(args: Any, ctx: dict[str, Any]) -> int:
    parent = _normalize_legacy_location_name(_require_resource(args.parent, arg_name="--parent"))
    client = _client_for_ctx(ctx)
    response, request = client.list_legacy_verifications(
        parent=parent,
        page_size=args.page_size,
        page_token=_optional_text(args.page_token),
    )
    return _emit(ctx, "legacy-v49.accounts.locations.verifications.list", request, response)


def cmd_accounts_locations_verifications_complete(args: Any, ctx: dict[str, Any]) -> int:
    operation = "legacy-v49.accounts.locations.verifications.complete"
    name = _normalize_legacy_verification_name(_require_resource(args.name, arg_name="--name"))
    pin = _read_secret_file(_require_resource(args.pin_file, arg_name="--pin-file"), label="PIN")
    request_body = {"pin": pin}

    plan = _build_plan(
        operation=operation,
        command=str(ctx.get("command_str") or ""),
        selector=name,
        tool=str(ctx["tool"]),
        version=str(ctx["tool_version"]),
        env_fingerprint=LEGACY_V49_HOST,
        body=request_body,
        mask=_LEGACY_VERIFICATION_PLAN_MASK,
        risk_level="high",
        risk_reasons=["Legacy verification completion mutates verification state."],
        preconditions=["OAuth access"],
        verification_plan=[
            "Call legacy verifications list on the parent location and confirm completed verification has state COMPLETED.",
        ],
    )

    if bool(ctx.get("apply")):
        plan_in = _optional_text(ctx.get("plan_in"))
        if not plan_in:
            raise SafetyError(
                "--apply requires --plan-in for legacy-v49 accounts locations verifications complete."
            )
        _require_matching_plan_in(
            plan_in=plan_in,
            operation=operation,
            selector=name,
            body=request_body,
            mask=_LEGACY_VERIFICATION_PLAN_MASK,
        )

        client = _client_for_ctx(ctx)
        response, complete_request = client.complete_legacy_verification(name=name, pin=pin)
        verification, changed = _verify_legacy_verification_complete(
            client=client,
            response=response,
            complete_request=complete_request,
        )
        verification["request"] = _redact_request_pin(verification.get("request", {}))
        receipt = _build_receipt(
            command=str(ctx.get("command_str") or ""),
            selector=name,
            tool=str(ctx["tool"]),
            version=str(ctx["tool_version"]),
            env_fingerprint=LEGACY_V49_HOST,
            changed=changed,
            verification=verification,
            diff_applied=["state"],
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


def cmd_accounts_locations_reviews_list(args: Any, ctx: dict[str, Any]) -> int:
    parent = _normalize_legacy_location_name(_require_resource(args.parent, arg_name="--parent"))
    page_size = _normalize_review_page_size(args.page_size)
    page_token = _optional_text(args.page_token)
    order_by = _normalize_review_order_by(_optional_text(args.order_by))

    client = _client_for_ctx(ctx)
    response, request = client.list_legacy_reviews(
        parent=parent,
        page_size=page_size,
        page_token=page_token,
        order_by=order_by,
    )
    return _emit(ctx, "legacy-v49.accounts.locations.reviews.list", request, response)


def cmd_accounts_locations_reviews_get(args: Any, ctx: dict[str, Any]) -> int:
    name = _normalize_legacy_review_name(_require_resource(args.name, arg_name="--name"))
    client = _client_for_ctx(ctx)
    response, request = client.get_legacy_review(name=name)
    return _emit(ctx, "legacy-v49.accounts.locations.reviews.get", request, response)


def cmd_accounts_locations_reviews_update_reply(args: Any, ctx: dict[str, Any]) -> int:
    operation = "legacy-v49.accounts.locations.reviews.update-reply"
    name = _normalize_legacy_review_name(_require_resource(args.name, arg_name="--name"))
    reply_file = _require_resource(args.reply_file, arg_name="--reply-file")
    review_reply = _validate_review_reply(reply_file)
    expected_comment = str(review_reply.get("comment") or "").strip()

    plan = _build_plan(
        operation=operation,
        command=str(ctx.get("command_str") or ""),
        selector=name,
        tool=str(ctx["tool"]),
        version=str(ctx["tool_version"]),
        env_fingerprint=LEGACY_V49_HOST,
        body=review_reply,
        mask=_LEGACY_REVIEW_REPLY_PLAN_MASK,
        risk_level="medium",
        risk_reasons=["Review reply write"],
        preconditions=["OAuth access"],
        verification_plan=["Get the review and verify reviewReply.comment equals the requested comment."],
    )

    if bool(ctx.get("apply")):
        plan_in = _optional_text(ctx.get("plan_in"))
        if not plan_in:
            raise SafetyError("--apply requires --plan-in for legacy-v49 accounts locations reviews update-reply.")
        _require_matching_plan_in(
            plan_in=plan_in,
            operation=operation,
            selector=name,
            body=review_reply,
            mask=_LEGACY_REVIEW_REPLY_PLAN_MASK,
        )

        client = _client_for_ctx(ctx)
        _, _ = client.update_review_reply(name=name, review_reply=review_reply)
        verification, changed = _verify_legacy_review_reply_update(
            client=client,
            name=name,
            expected_comment=expected_comment,
        )
        receipt = _build_receipt(
            command=str(ctx.get("command_str") or ""),
            selector=name,
            tool=str(ctx["tool"]),
            version=str(ctx["tool_version"]),
            env_fingerprint=LEGACY_V49_HOST,
            changed=changed,
            verification=verification,
            diff_applied=["reviewReply.comment"],
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


def cmd_accounts_locations_reviews_delete_reply(args: Any, ctx: dict[str, Any]) -> int:
    operation = "legacy-v49.accounts.locations.reviews.delete-reply"
    name = _normalize_legacy_review_name(_require_resource(args.name, arg_name="--name"))
    plan = _build_plan(
        operation=operation,
        command=str(ctx.get("command_str") or ""),
        selector=name,
        tool=str(ctx["tool"]),
        version=str(ctx["tool_version"]),
        env_fingerprint=LEGACY_V49_HOST,
        body={},
        mask=_LEGACY_REVIEW_REPLY_PLAN_MASK,
        risk_level="high",
        risk_reasons=["Review reply deletion"],
        preconditions=["OAuth access"],
        verification_plan=["Get the review and verify reviewReply is absent."],
    )

    if bool(ctx.get("apply")):
        plan_in = _optional_text(ctx.get("plan_in"))
        if not plan_in:
            raise SafetyError("--apply requires --plan-in for legacy-v49 accounts locations reviews delete-reply.")
        if not bool(ctx.get("yes")):
            raise SafetyError("--apply requires --yes for legacy-v49 accounts locations reviews delete-reply.")
        _require_matching_plan_in(
            plan_in=plan_in,
            operation=operation,
            selector=name,
            body={},
            mask=_LEGACY_REVIEW_REPLY_PLAN_MASK,
        )

        client = _client_for_ctx(ctx)
        _, _ = client.delete_review_reply(name=name)
        verification, changed = _verify_legacy_review_reply_delete(client=client, name=name)
        receipt = _build_receipt(
            command=str(ctx.get("command_str") or ""),
            selector=name,
            tool=str(ctx["tool"]),
            version=str(ctx["tool_version"]),
            env_fingerprint=LEGACY_V49_HOST,
            changed=changed,
            verification=verification,
            diff_applied=["reviewReply"],
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
