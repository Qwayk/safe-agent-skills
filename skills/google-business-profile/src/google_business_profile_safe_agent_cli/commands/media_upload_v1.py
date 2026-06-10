from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from ..api_client import MEDIA_UPLOAD_HOST
from ..errors import SafetyError, ValidationError
from .business_info import (
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


def _sha256(value: Any) -> str:
    payload = value if isinstance(value, (bytes, bytearray)) else str(value).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _build_file_summary(path: Path, content_type: str, data: bytes) -> dict[str, Any]:
    return {
        "mode": "file",
        "size": len(data),
        "content_type": content_type,
        "fingerprint": _sha256(data),
    }


def _infer_content_type(path: Path, content_type: str | None) -> str:
    explicit = _optional_text(content_type)
    if explicit:
        return explicit

    guessed, _ = __import__("mimetypes").guess_type(path.as_posix())
    if guessed:
        return guessed
    return "application/octet-stream"


def _verify_upload_acknowledged(response: dict[str, Any], request: dict[str, Any], resource_name: str) -> tuple[dict[str, Any], bool]:
    acknowledged = str(response.get("resourceName") or "").strip()
    if not acknowledged:
        return {
            "ok": False,
            "operation": "media-upload-v1.media.upload",
            "request": request,
            "response": response,
            "note": "No direct read-back verification is available for media upload in this slice; success is inferred from provider response `resourceName`.",
        }, False

    if acknowledged != resource_name:
        return {
            "ok": False,
            "operation": "media-upload-v1.media.upload",
            "request": request,
            "response": response,
            "note": "No direct read-back verification is available for media upload in this slice; response resourceName does not match requested resource name.",
        }, False

    return {
        "ok": True,
        "operation": "media-upload-v1.media.upload",
        "request": request,
        "response": response,
        "note": "No direct read-back verification is available for media upload in this slice; response resourceName matched requested resource name.",
    }, True


def cmd_media_upload(args: Any, ctx: dict[str, Any]) -> int:
    resource_name = _require_resource(args.resource_name, arg_name="--resource-name")
    media_file = _optional_text(args.media_file)
    media_json_file = _optional_text(args.media_json_file)

    if bool(media_file) == bool(media_json_file):
        raise ValidationError("Use exactly one of --media-file or --media-json-file.")

    operation = "media-upload-v1.media.upload"
    client = _client_for_ctx(ctx)
    selector = resource_name
    plan_or_body: dict[str, Any]
    request: dict[str, Any]
    response: dict[str, Any]

    if media_file:
        media_path = Path(media_file)
        if not media_path.exists():
            raise ValidationError(f"Media file not found: {media_path}")
        if not media_path.is_file():
            raise ValidationError(f"Media file must be a file: {media_path}")

        body_bytes = media_path.read_bytes()
        inferred_content_type = _infer_content_type(media_path, _optional_text(args.content_type))
        plan_or_body = _build_file_summary(media_path, inferred_content_type, body_bytes)

        plan = _build_plan(
            operation=operation,
            command=str(ctx.get("command_str") or ""),
            selector=selector,
            tool=str(ctx["tool"]),
            version=str(ctx["tool_version"]),
            env_fingerprint=MEDIA_UPLOAD_HOST,
            body=plan_or_body,
            mask="resourceName",
            risk_level="medium",
            risk_reasons=["Media file upload"],
            preconditions=["OAuth access"],
            verification_plan=["Upload response must include matching resourceName; no direct read-back verification is available in this slice."],
        )

        if bool(ctx.get("apply")):
            plan_in = _optional_text(ctx.get("plan_in"))
            if not plan_in:
                raise SafetyError("--apply requires --plan-in for media file upload.")
            _require_matching_plan_in(
                plan_in=plan_in,
                operation=operation,
                selector=selector,
                body=plan_or_body,
                mask="resourceName",
            )

            response, request = client.upload_media_file(
                resource_name=resource_name,
                data=body_bytes,
                content_type=inferred_content_type,
                request_body=plan_or_body,
            )
        else:
            if bool(ctx.get("dry_run", True)):
                plan_path = _write_plan_if_needed(ctx.get("plan_out"), plan)
                return _emit_write_output(
                    ctx,
                    operation=operation,
                    dry_run=True,
                    payload_obj=plan,
                    artifact_path=plan_path,
                )

    else:
        assert media_json_file is not None
        media_body = _validate_json_object(media_json_file, label="Media")
        plan_or_body = media_body

        plan = _build_plan(
            operation=operation,
            command=str(ctx.get("command_str") or ""),
            selector=selector,
            tool=str(ctx["tool"]),
            version=str(ctx["tool_version"]),
            env_fingerprint=MEDIA_UPLOAD_HOST,
            body=plan_or_body,
            mask="resourceName",
            risk_level="medium",
            risk_reasons=["Media metadata upload"],
            preconditions=["OAuth access"],
            verification_plan=["Upload response must include matching resourceName; no direct read-back verification is available in this slice."],
        )

        if bool(ctx.get("apply")):
            plan_in = _optional_text(ctx.get("plan_in"))
            if not plan_in:
                raise SafetyError("--apply requires --plan-in for media metadata upload.")
            _require_matching_plan_in(
                plan_in=plan_in,
                operation=operation,
                selector=selector,
                body=plan_or_body,
                mask="resourceName",
            )

            response, request = client.upload_media_metadata(
                resource_name=resource_name,
                body=plan_or_body,
            )
        else:
            plan_path = _write_plan_if_needed(ctx.get("plan_out"), plan)
            return _emit_write_output(
                ctx,
                operation=operation,
                dry_run=True,
                payload_obj=plan,
                artifact_path=plan_path,
            )

    verification, changed = _verify_upload_acknowledged(response=response, request=request, resource_name=resource_name)
    receipt = _build_receipt(
        command=str(ctx.get("command_str") or ""),
        selector=selector,
        tool=str(ctx["tool"]),
        version=str(ctx["tool_version"]),
        env_fingerprint=MEDIA_UPLOAD_HOST,
        changed=changed,
        verification=verification,
        diff_applied=["resourceName"],
    )
    receipt_path = _write_receipt_if_needed(ctx.get("receipt_out"), receipt)
    return _emit_write_output(
        ctx,
        operation=operation,
        dry_run=False,
        payload_obj=receipt,
        artifact_path=receipt_path,
    )
