from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from ..api_client import VERIFICATIONS_HOST
from ..errors import SafetyError, ValidationError
from ..json_files import read_json_file, write_json_file
from .business_info import (
    _build_plan,
    _build_receipt,
    _client_for_ctx,
    _emit,
    _emit_write_output,
    _optional_text,
    _require_matching_plan_in,
    _require_resource,
    _validate_json_object,
    _write_plan_if_needed,
    _write_receipt_if_needed,
)

TRUSTED_VERIFICATION_METHODS = frozenset(
    {"ADDRESS", "EMAIL", "PHONE_CALL", "SMS", "AUTO", "TRUSTED_PARTNER"}
)


def _validate_context_file(path: str) -> dict:
    data = read_json_file(path)
    if not isinstance(data, dict):
        raise ValidationError(f"--context-file must be a JSON object: {Path(path)}")
    return data


def _validate_verification_token_file(path: str) -> dict[str, object]:
    token = _validate_json_object(path, label="Verification token")
    token_string = token.get("tokenString")
    if not isinstance(token_string, str) or not token_string.strip():
        raise ValidationError(
            "--verification-token-file must be a JSON object with non-empty tokenString."
        )
    if set(token.keys()) != {"tokenString"}:
        raise ValidationError(
            "--verification-token-file must be a JSON object with only tokenString."
        )
    return token


def _read_text_file(path: str, *, label: str) -> str:
    token_path = Path(path)
    if not token_path.exists():
        raise ValidationError(f"{label} file not found: {token_path}")
    text = token_path.read_text(encoding="utf-8").strip()
    if not text:
        raise ValidationError(f"{label} file must not be empty: {token_path}")
    return text


def _validate_verification_method(value: object) -> str:
    method = str(value or "").strip().upper()
    if not method:
        raise ValidationError("--method is required and must not be blank.")
    if method not in TRUSTED_VERIFICATION_METHODS:
        methods = ", ".join(sorted(TRUSTED_VERIFICATION_METHODS))
        raise ValidationError(f"--method must be one of: {methods}.")
    return method


def _redact_request_body(request: dict[str, object], *, redact_keys: set[str]) -> dict[str, object]:
    request_body = dict(request)
    body = request_body.get("body")
    if isinstance(body, dict):
        safe_body = dict(body)
        for key in redact_keys:
            if key in safe_body:
                safe_body[key] = "[redacted]"
        request_body["body"] = safe_body
    return request_body


def _redact_response_body(response: dict[str, object], *, redact_keys: set[str]) -> dict[str, object]:
    def _redact(value: object) -> object:
        if isinstance(value, dict):
            out: dict[str, object] = {}
            for key, nested in value.items():
                if key in redact_keys:
                    out[key] = "[redacted]"
                else:
                    out[key] = _redact(nested)
            return out
        if isinstance(value, list):
            return [_redact(item) for item in value]
        return value

    return dict(_redact(response))


def _write_verification_token_output(path: str, token: str) -> str:
    return str(write_json_file(path, {"tokenString": token}))


def _extract_verification_name(response: dict[str, object]) -> str:
    verification = response.get("verification")
    if isinstance(verification, dict):
        name = verification.get("name")
    else:
        name = response.get("name")
    return str(name or "").strip()


def _extract_verification_parent(name: str) -> str:
    marker = "/verifications/"
    if marker not in name:
        return ""
    parent, _ = name.split(marker, 1)
    return parent.strip("/")


def _extract_verification_state(response: dict[str, object]) -> str:
    verification = response.get("verification")
    if isinstance(verification, dict):
        return str(verification.get("state") or "").strip().upper()
    return str(response.get("state") or "").strip().upper()


def _find_verification_in_list(
    list_response: dict[str, object],
    verification_name: str,
) -> dict[str, object] | None:
    items = list_response.get("verifications")
    if not isinstance(items, list):
        return None
    for item in items:
        if not isinstance(item, dict):
            continue
        if str(item.get("name") or "").strip() == verification_name:
            return item
    return None

def cmd_locations_fetch_verification_options(args, ctx: dict) -> int:
    location = _require_resource(args.location, arg_name="--location")
    language_code = _require_resource(args.language_code, arg_name="--language-code")

    context_file = _optional_text(args.context_file)
    context = _validate_context_file(context_file) if context_file else None

    client = _client_for_ctx(ctx)
    response, request = client.fetch_verification_options(
        location=location,
        language_code=language_code,
        context=context,
    )
    return _emit(ctx, "verifications.locations.fetch-verification-options", request, response)


def cmd_locations_get_voice_of_merchant_state(args, ctx: dict) -> int:
    name = _require_resource(args.name, arg_name="--name")
    client = _client_for_ctx(ctx)
    response, request = client.get_voice_of_merchant_state(name=name)
    return _emit(ctx, "verifications.locations.get-voice-of-merchant-state", request, response)


def cmd_locations_verifications_list(args, ctx: dict) -> int:
    parent = _require_resource(args.parent, arg_name="--parent")

    client = _client_for_ctx(ctx)
    response, request = client.list_verifications(
        parent=parent,
        page_size=args.page_size,
        page_token=args.page_token,
    )
    return _emit(ctx, "verifications.locations.verifications.list", request, response)


def _build_verification_request_body(args) -> dict:
    body: dict[str, object] = {
        "method": _validate_verification_method(args.method),
    }
    language_code = _optional_text(args.language_code)
    if language_code:
        body["languageCode"] = language_code
    mailer_contact = _optional_text(args.mailer_contact)
    if mailer_contact:
        body["mailerContact"] = mailer_contact
    phone_number = _optional_text(args.phone_number)
    if phone_number:
        body["phoneNumber"] = phone_number
    email_address = _optional_text(args.email_address)
    if email_address:
        body["emailAddress"] = email_address

    context_file = _optional_text(args.context_file)
    if context_file:
        body["context"] = _validate_context_file(context_file)

    token_file = _optional_text(args.verification_token_file)
    if token_file:
        body["token"] = _validate_verification_token_file(token_file)

    trusted_partner_token_file = _optional_text(args.trusted_partner_token_file)
    if trusted_partner_token_file:
        body["trustedPartnerToken"] = _read_text_file(
            trusted_partner_token_file,
            label="Trusted partner token",
        )
    return body


def _verify_verification_by_listing(
    *,
    client: Any,
    response: dict[str, object],
    verify_request: dict,
    require_state: str | None = None,
) -> tuple[dict[str, object], bool]:
    verification_name = _extract_verification_name(response)
    if not verification_name:
        return (
            {
                "ok": False,
                "operation": "verifications.locations.verify",
                "request": _redact_request_body(verify_request, redact_keys={"token", "trustedPartnerToken"}),
                "response": response,
                "note": "Verify/complete response did not include verification.name; verification could not confirm.",
            },
            False,
        )

    parent = _extract_verification_parent(verification_name)
    if not parent:
        return (
            {
                "ok": False,
                "operation": "verifications.locations.verify",
                "request": _redact_request_body(verify_request, redact_keys={"token", "trustedPartnerToken"}),
                "response": response,
                "note": "Could not derive parent location from returned verification.name.",
            },
            False,
        )

    try:
        list_response, list_request = client.list_verifications(parent=parent)
    except Exception as exc:  # noqa: BLE001
        return (
            {
                "ok": False,
                "operation": "verifications.locations.verifications.list",
                "request": _redact_request_body(verify_request, redact_keys={"token", "trustedPartnerToken"}),
                "response": {
                    "request_error": True,
                    "error_type": type(exc).__name__,
                    "message": str(exc),
                },
                "note": "Could not run verifications list follow-up; marking result as uncertain.",
            },
            False,
        )

    found = _find_verification_in_list(list_response, verification_name)
    if not found:
        return (
            {
                "ok": False,
                "operation": "verifications.locations.verifications.list",
                "request": list_request,
                "response": list_response,
                "note": "Created verification name was not found in verification list follow-up.",
            },
            False,
        )

    if require_state is None:
        return (
            {
                "ok": True,
                "operation": "verifications.locations.verifications.list",
                "request": list_request,
                "response": list_response,
            },
            True,
        )

    state = _extract_verification_state(found)
    if state != require_state:
        return (
            {
                "ok": False,
                "operation": "verifications.locations.verifications.list",
                "request": list_request,
                "response": list_response,
                "note": f"Verification state was {state or 'UNKNOWN'}; expected {require_state}.",
            },
            False,
        )

    return (
        {
            "ok": True,
            "operation": "verifications.locations.verifications.list",
            "request": list_request,
            "response": list_response,
        },
        True,
    )


def _read_pin_from_file(path: str) -> str:
    return _read_text_file(path, label="PIN")


def cmd_locations_verify(args, ctx: dict) -> int:
    location_name = _require_resource(args.name, arg_name="--name")
    request_body = _build_verification_request_body(args)
    request_kwargs = {
        "method": request_body["method"],
        "language_code": request_body.get("languageCode"),
        "mailer_contact": request_body.get("mailerContact"),
        "phone_number": request_body.get("phoneNumber"),
        "email_address": request_body.get("emailAddress"),
        "context": request_body.get("context"),
        "token": request_body.get("token"),
        "trusted_partner_token": request_body.get("trustedPartnerToken"),
    }
    request_kwargs = {k: v for k, v in request_kwargs.items() if v is not None}

    operation = "verifications.locations.verify"
    plan = _build_plan(
        operation=operation,
        command=str(ctx.get("command_str") or ""),
        selector=location_name,
        tool=str(ctx["tool"]),
        version=str(ctx["tool_version"]),
        env_fingerprint=VERIFICATIONS_HOST,
        body=request_body,
        mask="name",
        risk_level="medium",
        risk_reasons=["Location verification initiation"],
        preconditions=["OAuth access"],
        verification_plan=[
            "Call verifications list on the parent location and confirm returned verifications include the created verification name.",
        ],
    )

    if bool(ctx.get("apply")):
        client = _client_for_ctx(ctx)
        plan_in = _optional_text(ctx.get("plan_in"))
        if not plan_in:
            raise SafetyError("--apply requires --plan-in for verifications locations verify.")
        _require_matching_plan_in(
            plan_in=plan_in,
            operation=operation,
            selector=location_name,
            body=request_body,
            mask="name",
        )

        response, verify_request = client.verify_location(name=location_name, **request_kwargs)
        verification, changed = _verify_verification_by_listing(
            client=client,
            response=response,
            verify_request=verify_request,
        )
        # Keep request secrets redacted before they can reach receipts.
        verification["request"] = _redact_request_body(
            verification.get("request", {}),
            redact_keys={"token", "trustedPartnerToken", "pin"},
        )
        receipt = _build_receipt(
            command=str(ctx.get("command_str") or ""),
            selector=location_name,
            tool=str(ctx["tool"]),
            version=str(ctx["tool_version"]),
            env_fingerprint=VERIFICATIONS_HOST,
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


def cmd_locations_verifications_complete(args, ctx: dict) -> int:
    verification_name = _require_resource(
        args.name,
        arg_name="--name",
    )
    pin = _read_pin_from_file(_require_resource(args.pin_file, arg_name="--pin-file"))

    operation = "verifications.locations.verifications.complete"
    request_body = {"pin": pin}
    plan = _build_plan(
        operation=operation,
        command=str(ctx.get("command_str") or ""),
        selector=verification_name,
        tool=str(ctx["tool"]),
        version=str(ctx["tool_version"]),
        env_fingerprint=VERIFICATIONS_HOST,
        body=request_body,
        mask="name",
        risk_level="high",
        risk_reasons=["Verification completion mutates verification state."],
        preconditions=["OAuth access"],
        verification_plan=[
            "Call verifications list on the parent location and confirm completed verification has state COMPLETED.",
        ],
    )

    if bool(ctx.get("apply")):
        client = _client_for_ctx(ctx)
        plan_in = _optional_text(ctx.get("plan_in"))
        if not plan_in:
            raise SafetyError("--apply requires --plan-in for verifications locations verifications complete.")
        _require_matching_plan_in(
            plan_in=plan_in,
            operation=operation,
            selector=verification_name,
            body=request_body,
            mask="name",
        )

        response, complete_request = client.complete_verification(name=verification_name, pin=pin)
        verification, changed = _verify_verification_by_listing(
            client=client,
            response=response,
            verify_request=complete_request,
            require_state="COMPLETED",
        )
        verification["request"] = _redact_request_body(
            verification.get("request", {}),
            redact_keys={"pin", "token", "trustedPartnerToken"},
        )
        # Keep pin out of plan/receipt payloads; use response-derived confirmation only.
        receipt = _build_receipt(
            command=str(ctx.get("command_str") or ""),
            selector=verification_name,
            tool=str(ctx["tool"]),
            version=str(ctx["tool_version"]),
            env_fingerprint=VERIFICATIONS_HOST,
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


def cmd_verification_tokens_generate(args, ctx: dict) -> int:
    location_id = _require_resource(args.location_id, arg_name="--location-id")
    request_body = {"locationId": location_id}

    operation = "verifications.verification-tokens.generate"
    plan = _build_plan(
        operation=operation,
        command=str(ctx.get("command_str") or ""),
        selector=location_id,
        tool=str(ctx["tool"]),
        version=str(ctx["tool_version"]),
        env_fingerprint=VERIFICATIONS_HOST,
        body=request_body,
        mask="locationId",
        risk_level="low",
        risk_reasons=["Generate instant verification token for a location."],
        preconditions=["OAuth access"],
        verification_plan=[
            "No direct read-back API is exposed for this method in this slice.",
            "Apply is considered successful only when result is SUCCEEDED and token is present in response.",
        ],
    )

    if bool(ctx.get("apply")):
        client = _client_for_ctx(ctx)
        plan_in = _optional_text(ctx.get("plan_in"))
        if not plan_in:
            raise SafetyError("--apply requires --plan-in for verifications verification-tokens generate.")
        verification_token_out = _optional_text(getattr(args, "verification_token_out", None))
        if not verification_token_out:
            raise SafetyError(
                "--apply requires --verification-token-out for verifications verification-tokens generate."
            )
        _require_matching_plan_in(
            plan_in=plan_in,
            operation=operation,
            selector=location_id,
            body=request_body,
            mask="locationId",
            plan_in_label="--plan-in",
        )

        response, generate_request = client.generate_verification_token(location_id=location_id)
        sanitized_response = _redact_response_body(
            response,
            redact_keys={"instantVerificationToken", "tokenString", "trustedPartnerToken"},
        )
        verification = {
            "ok": False,
            "operation": operation,
            "request": _redact_request_body(generate_request, redact_keys={"token"}),
            "response": sanitized_response,
        }
        result = str(response.get("result") or "").strip().upper()
        token_written = False
        if result == "SUCCEEDED":
            raw_token = response.get("instantVerificationToken")
            if isinstance(raw_token, str) and raw_token.strip():
                token_written = True
                token_path = _write_verification_token_output(verification_token_out, raw_token.strip())
                verification["token_output_path"] = token_path
                verification["token_output_sha256"] = hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
                verification["ok"] = True
            else:
                verification["note"] = "Provider reported SUCCEEDED but did not return instantVerificationToken."
        else:
            verification["result"] = result or "UNKNOWN"
            verification["note"] = "Provider result is not SUCCEEDED; token was not written."

        if not token_written:
            verification["token_written"] = False

        receipt = _build_receipt(
            command=str(ctx.get("command_str") or ""),
            selector=location_id,
            tool=str(ctx["tool"]),
            version=str(ctx["tool_version"]),
            env_fingerprint=VERIFICATIONS_HOST,
            changed=token_written,
            verification=verification,
            diff_applied=["result"],
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
