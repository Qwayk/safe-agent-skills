from __future__ import annotations

from hashlib import sha256
from typing import Any

from ..config import Config
from ..errors import SafetyError, ValidationError
from ..http import HttpResponse, HttpStatusError
from ..json_files import write_json_file
from .read_api import redact_error


def credential_fingerprint(cfg: Config) -> str:
    return sha256((cfg.token or "").encode("utf-8")).hexdigest()


def check_plan(
    plan: Any, *, cfg: Config, advertiser_id: str, endpoint: str,
    file_field: str, file_digest: str, file_description: str,
) -> dict[str, Any]:
    if not isinstance(plan, dict):
        raise ValidationError("--plan-in must contain a JSON object")
    baseline, selector = plan.get("baseline"), plan.get("selector")
    if not isinstance(baseline, dict) or not isinstance(selector, dict):
        raise ValidationError("--plan-in must contain a baseline and selector")
    if baseline.get("env_fingerprint") != cfg.base_url:
        raise SafetyError("Refused: the Awin API URL changed. Make a fresh plan.")
    if str(selector.get("advertiser_id") or "") != advertiser_id or selector.get("endpoint") != endpoint:
        raise SafetyError("Refused: the plan does not match the requested advertiser or endpoint.")
    if baseline.get("credential_fingerprint") != credential_fingerprint(cfg):
        raise SafetyError("Refused: the plan does not match the Awin token. Make a fresh plan.")
    if baseline.get(file_field) != file_digest:
        raise SafetyError(f"Refused: {file_description} changed since --plan-in was created")
    return selector


def post_write(ctx: dict, endpoint: str, **request: Any) -> tuple[HttpResponse | None, dict[str, Any]]:
    cfg = ctx["cfg"]
    try:
        response = ctx["http_client"].request("POST", f"{cfg.base_url}/{endpoint}", **request)
        return response, {"response_status": response.status}
    except HttpStatusError as exc:
        state = "rejected" if 400 <= exc.status < 500 and exc.status != 408 else "unknown"
        return None, {"state": state, "response_status": exc.status, "error": redact_error(str(exc), cfg.token)}
    except RuntimeError as exc:
        return None, {"state": "unknown", "response_status": None, "error": redact_error(str(exc), cfg.token)}


def response_object(response: HttpResponse) -> dict | None:
    try:
        result = response.json()
    except (ValueError, UnicodeError):
        return None
    return result if isinstance(result, dict) else None


def finish_write(
    ctx: dict, *, operation: str, event: str, receipt: dict,
    details: dict, next_step: str, fields: dict,
) -> int:
    state = details["state"]
    completed = state in {"confirmed", "unchanged"}
    ok = completed or state == "pending"
    receipt["changed"] = {"confirmed": True, "partial": True, "rejected": False, "unchanged": False}.get(state)
    receipt["verification"]["ok"] = completed
    receipt["verification"]["details"].update(details)
    if state != "confirmed":
        receipt["diff_applied"] = []
    if not completed:
        receipt["next_step"] = next_step

    result = {
        **fields,
        "ok": ok,
        "dry_run": False,
        "operation": operation,
        "advertiser_id": receipt["selector"]["advertiser_id"],
        "endpoint": "/" + receipt["selector"]["endpoint"],
        "method": "POST",
        "status": details["response_status"],
        "result": details,
        "receipt": receipt,
        "receipt_out": None,
    }
    if not completed:
        result["next_step"] = next_step
    if not ok:
        result["error"] = details.get("error") or f"Awin result: {state}"
        result["error_type"] = "ValidationError" if state == "rejected" else "UnconfirmedWrite"
    if ctx.get("receipt_out"):
        try:
            result["receipt_out"] = write_json_file(ctx["receipt_out"], receipt)
        except OSError as exc:
            result["receipt_error"] = f"Could not save the receipt: {exc}"
    try:
        ctx["audit"].write(event, result)
    except OSError as exc:
        result["audit_error"] = f"Could not save the audit log: {exc}"
    ctx["out"].emit(result)
    return 0 if ok and "receipt_error" not in result else 1
