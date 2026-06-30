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


COMMAND_FAMILY = "suppliers-hub-marketplace-provider-submissions"
SUBMIT_GENERATED_MOCKUPS_PATH = "/suppliershub/v2/submit-generated-mockups"


def _read_json_arg(raw: Any, *, field: str) -> dict[str, Any]:
    if raw is None:
        raise ValidationError(f"Missing --{field}")
    if not isinstance(raw, str):
        raise ValidationError(f"--{field} must be a JSON object or @file path")
    text = raw.strip()
    if not text:
        raise ValidationError(f"--{field} cannot be empty")
    if text.startswith("@"):
        path = Path(text[1:])
        if not path.exists():
            raise ValidationError(f"--{field} file not found: {path}")
        text = path.read_text(encoding="utf-8").strip()
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValidationError(f"Invalid JSON for --{field}: {exc.msg}") from exc
    if not isinstance(payload, dict):
        raise ValidationError(f"--{field} must be a JSON object")
    if not payload:
        raise ValidationError(f"--{field} cannot be empty")
    return payload


def _validate_mockups_body(body: dict[str, Any]) -> list[dict[str, Any]]:
    mockups = body.get("mockups")
    if not isinstance(mockups, list) or not mockups:
        raise ValidationError("--mockups-json must contain a non-empty mockups array")
    if len(mockups) > 100:
        raise ValidationError("--mockups-json cannot contain more than 100 mockups")
    normalized: list[dict[str, Any]] = []
    for index, raw_mockup in enumerate(mockups):
        if not isinstance(raw_mockup, dict):
            raise ValidationError(f"mockups[{index}] must be a JSON object")
        provider_product_id = raw_mockup.get("providerProductId")
        image_type = raw_mockup.get("imageType")
        status = raw_mockup.get("status")
        if not isinstance(provider_product_id, str) or not provider_product_id.strip():
            raise ValidationError(f"mockups[{index}].providerProductId must be a non-empty string")
        if not isinstance(image_type, str) or not image_type.strip():
            raise ValidationError(f"mockups[{index}].imageType must be a non-empty string")
        if status not in {"COMPLETED", "FAILED", "PENDING"}:
            raise ValidationError(f"mockups[{index}].status must be COMPLETED, FAILED, or PENDING")
        if status == "COMPLETED":
            mockup_url = raw_mockup.get("mockupUrl")
            if not isinstance(mockup_url, str) or not mockup_url.strip():
                raise ValidationError(f"mockups[{index}].mockupUrl is required when status is COMPLETED")
        normalized.append(
            {
                "providerProductId": provider_product_id.strip(),
                "imageType": image_type.strip(),
                "status": status,
            }
        )
    return normalized


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
        params=None,
        json_body=json_body,
    )
    payload = response.json()
    if not isinstance(payload, dict):
        raise ValidationError("Wix API returned a non-object JSON response")
    return payload


def _utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _build_plan(*, request: dict[str, Any], selector: dict[str, Any], proposed_changes: list[dict[str, Any]], ctx: dict[str, Any]) -> dict[str, Any]:
    return {
        "tool": ctx.get("tool") or "wix-safe-agent-cli",
        "version": ctx.get("tool_version") or None,
        "generated_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "method": f"{COMMAND_FAMILY}.submit-generated-mockups",
        "risk_level": "medium",
        "risk_reasons": ["suppliers-hub-marketplace-provider-submission", "developer-preview", "provider-backend-reporting-write"],
        "preconditions": ["env_fingerprint must match", "selector must match", "apply requires --plan-in, --apply, and --yes"],
        "selector": selector,
        "request": request,
        "baseline": {"env_fingerprint": ctx["cfg"].base_url, "selector": selector, "before_state": {}},
        "proposed_changes": proposed_changes,
        "verification_plan": {
            "type": "provider-response",
            "notes": "Verify by Wix provider response, including per-item results and bulkActionMetadata when returned.",
        },
        "rollback": {"supported": False, "notes": "No automatic rollback. Submit a corrected mockup result if provider data was wrong."},
    }


def _load_plan(*, plan_in: str | None, expected_selector: dict[str, Any], ctx: dict[str, Any]) -> dict[str, Any]:
    if not plan_in:
        raise ValidationError("Missing --plan-in")
    plan = read_json_file(plan_in)
    if not isinstance(plan, dict):
        raise ValidationError("Plan file must be a JSON object")
    if str(plan.get("method") or "") != f"{COMMAND_FAMILY}.submit-generated-mockups":
        raise SafetyError("Refused: plan method does not match current command")
    baseline = plan.get("baseline")
    if not isinstance(baseline, dict):
        raise SafetyError("Refused: plan baseline missing")
    if str(baseline.get("env_fingerprint") or "") != str(ctx["cfg"].base_url):
        raise SafetyError("Refused: plan env_fingerprint does not match current environment")
    if baseline.get("selector") != expected_selector:
        raise SafetyError("Refused: plan selector does not match current command")
    return plan


def _emit_error(ctx: dict[str, Any], *, method: str, exc: Exception) -> int:
    if isinstance(exc, SafetyError):
        ctx["out"].emit({"ok": True, "dry_run": False, "refused": True, "reasons": [str(exc)], "refusal_type": "SafetyError", "method": method})
        return 0
    if isinstance(exc, ValidationError):
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": method})
        return 1
    ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": method})
    return 1


def cmd_suppliers_hub_marketplace_provider_submissions_submit_generated_mockups(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.submit-generated-mockups"
    try:
        body = _read_json_arg(getattr(args, "mockups_json", None), field="mockups-json")
        mockups = _validate_mockups_body(body)
        selector = {"kind": COMMAND_FAMILY, "operation": "submit-generated-mockups", "mockups": mockups}
        request = {"method": "POST", "path": SUBMIT_GENERATED_MOCKUPS_PATH, "body": body}
        proposed_changes = [
            {
                "operation": "submit-generated-mockup-result",
                "provider_product_id": mockup["providerProductId"],
                "image_type": mockup["imageType"],
                "status": mockup["status"],
            }
            for mockup in mockups
        ]
        plan = _build_plan(request=request, selector=selector, proposed_changes=proposed_changes, ctx=ctx)
        if ctx.get("plan_out"):
            write_json_file(ctx["plan_out"], plan)
        if not reviewed_plan_apply_requested(ctx):
            out = {
                "ok": True,
                "dry_run": True,
                "method": method,
                "plan": plan,
                "apply_hint": "Review the plan, then rerun with --plan-in, --apply, and --yes.",
            }
            ctx["audit"].write(method, out)
            ctx["out"].emit(out)
            return 0

        _load_plan(plan_in=ctx.get("plan_in"), expected_selector=selector, ctx=ctx)
        auth = _resolve_auth(ctx)
        response = _request_json(method="POST", path=SUBMIT_GENERATED_MOCKUPS_PATH, headers=auth["headers"], json_body=body, ctx=ctx)
        receipt = {
            "method": method,
            "applied_at_utc": _utc_now(),
            "selector": selector,
            "request": request,
            "response": response,
            "verification": {"type": "provider-response", "notes": "Review results and bulkActionMetadata for per-item success or failure."},
        }
        if ctx.get("receipt_out"):
            write_json_file(ctx["receipt_out"], receipt)
        out = {"ok": True, "dry_run": False, "method": method, "auth_mode": auth["mode"], "request": request, "response": response, "receipt": receipt}
        ctx["audit"].write(method, out)
        ctx["out"].emit(out)
        return 0
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)
