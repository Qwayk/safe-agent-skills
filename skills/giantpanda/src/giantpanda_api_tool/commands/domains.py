from __future__ import annotations

from pathlib import Path
from typing import Any, Final
from uuid import uuid4

from .. import __version__
from .. import config as config_mod
from ..errors import ValidationError
from ..http import HttpClient, HttpError
from ..safety_state import (
    default_plan_path,
    default_receipt_path,
    plan_id,
    read_json_file,
    write_private_json,
)

DOMAINS_STATS_PATH = "/api/v1/domains/stats/"
DOMAINS_ADD_PATH = "/api/v1/domains/add/"
DOMAINS_ADD_OPERATION = "domains add"
DOMAINS_ADD_MAX_DOMAINS = 100
DOMAINS_ADD_NO_SNAPSHOT_WARNING: Final = (
    "No snapshot, rollback, restore, or undo is available for this operation."
)
_DOMAINS_ADD_APPLY_REQUIREMENTS: Final = {
    "apply": "--apply required",
    "plan_in": "--plan-in required",
    "approve_plan": "--approve-plan with exact plan id required",
    "ack_no_snapshot": "--ack-no-snapshot required",
    "snapshot_available": False,
    "rollback_supported": False,
    "safety_warning": DOMAINS_ADD_NO_SNAPSHOT_WARNING,
}


def _requires_no_safety_bypass() -> dict[str, Any]:
    return dict(_DOMAINS_ADD_APPLY_REQUIREMENTS)


def _is_ipv4(value: str) -> bool:
    parts = value.split(".")
    if len(parts) != 4:
        return False
    for part in parts:
        if not part.isdigit():
            return False
        if len(part) > 1 and part.startswith("0") and len(part) > 1:
            return False
        try:
            number = int(part)
        except ValueError:  # pragma: no cover - guard for python int edges
            return False
        if number < 0 or number > 255:
            return False
    return True


def _normalize_domain(value: str) -> str:
    if not isinstance(value, str):
        raise ValidationError("Domain must be a non-empty text value")
    raw = value.strip()
    if not raw:
        raise ValidationError("Domain must be a non-empty text value")
    if not raw.isascii():
        raise ValidationError("Domain must contain only ASCII characters")
    if ":" in raw:
        raise ValidationError(f"Invalid domain '{value}': port or scheme is not allowed")
    lowered = raw.lower()
    if " " in lowered or "\t" in lowered or "\n" in lowered or "\r" in lowered:
        raise ValidationError(f"Invalid domain '{value}': whitespace is not allowed")
    if any(ch.isspace() for ch in lowered):
        raise ValidationError(f"Invalid domain '{value}': whitespace is not allowed")
    if "://" in lowered:
        raise ValidationError(f"Invalid domain '{value}': scheme is not allowed")
    if "/" in lowered or "\\" in lowered:
        raise ValidationError(f"Invalid domain '{value}': path separators are not allowed")
    if "@" in lowered:
        raise ValidationError(f"Invalid domain '{value}': email-like value is not allowed")
    if "*" in lowered:
        raise ValidationError(f"Invalid domain '{value}': wildcard is not allowed")
    if lowered.startswith(".") or lowered.endswith("."):
        raise ValidationError(f"Invalid domain '{value}': leading/trailing dots are not allowed")

    if len(lowered) > 253:
        raise ValidationError(f"Invalid domain '{value}': hostname is too long")

    if "." not in lowered:
        raise ValidationError(f"Invalid domain '{value}': must include a dot")
    if _is_ipv4(lowered):
        raise ValidationError(f"Invalid domain '{value}': IP addresses are not allowed")

    labels = lowered.split(".")
    if labels[-1].isdigit():
        raise ValidationError(f"Invalid domain '{value}': numeric public suffix is not allowed")
    for label in labels:
        if not label:
            raise ValidationError(f"Invalid domain '{value}': empty label is not allowed")
        if len(label) > 63:
            raise ValidationError(f"Invalid domain '{value}': label too long")
        if label.startswith("-") or label.endswith("-"):
            raise ValidationError(f"Invalid domain '{value}': edge hyphens are not allowed")
        if not all(ch.isalnum() or ch == "-" for ch in label):
            raise ValidationError(f"Invalid domain '{value}': label has invalid characters")
        if not (label[0].isalnum() and label[-1].isalnum()):
            raise ValidationError(f"Invalid domain '{value}': edge hyphens are not allowed")
    return lowered


def _normalize_domains(raw_domains: list[str]) -> tuple[list[str], list[str]]:
    if not raw_domains:
        raise ValidationError("At least one --domain is required")
    if len(raw_domains) > DOMAINS_ADD_MAX_DOMAINS:
        raise ValidationError(
            f"Too many --domain values: {len(raw_domains)} (max {DOMAINS_ADD_MAX_DOMAINS})"
        )

    normalized: list[str] = []
    for raw_domain in raw_domains:
        normalized.append(_normalize_domain(raw_domain))
    uniques_seen: set[str] = set()
    unique_ordered: list[str] = []
    removed: list[str] = []
    for domain in normalized:
        if domain in uniques_seen:
            removed.append(domain)
            continue
        uniques_seen.add(domain)
        unique_ordered.append(domain)
    unique_domains = sorted(unique_ordered)
    if len(unique_domains) > DOMAINS_ADD_MAX_DOMAINS:
        raise ValidationError(
            f"Too many unique domains after dedupe: {len(unique_domains)} (max {DOMAINS_ADD_MAX_DOMAINS})"
        )
    return unique_domains, removed


def _build_add_plan(
    cfg: config_mod.Config,
    normalized_domains: list[str],
    *,
    duplicates: list[str],
    env_file: str,
) -> dict[str, Any]:
    request_domains = [{"name": domain} for domain in normalized_domains]
    request_body = {"domains": request_domains}
    safety = {
        "max_domains": DOMAINS_ADD_MAX_DOMAINS,
        "duplicates_removed": sorted(set(duplicates)),
    }
    nonce = uuid4().hex
    token = None if config_mod.is_placeholder_token(cfg.token or "") else cfg.token
    generated_plan_id = plan_id(
        DOMAINS_ADD_OPERATION,
        cfg.host.rstrip("/"),
        DOMAINS_ADD_PATH,
        normalized_domains,
        safety=safety,
        nonce=nonce,
        token=token,
        env_file=env_file,
    )
    return {
        "operation": DOMAINS_ADD_OPERATION,
        "host": cfg.host.rstrip("/"),
        "endpoint": DOMAINS_ADD_PATH,
        "plan_id": generated_plan_id,
        "approval_nonce": nonce,
        "account_bound": token is not None,
        "request_body": request_body,
        "apply_requirements": _requires_no_safety_bypass(),
        "snapshot_available": False,
        "rollback_supported": False,
        "safety_warning": DOMAINS_ADD_NO_SNAPSHOT_WARNING,
        "safety": safety,
    }


def _load_plan(plan_in: str) -> dict[str, Any]:
    plan_obj = read_json_file(plan_in)
    if not isinstance(plan_obj, dict):
        raise ValidationError("Plan file must be a JSON object")
    return plan_obj


def _validate_plan(
    plan_obj: dict[str, Any],
    *,
    host: str,
    normalized_domains: list[str],
    token: str,
    env_file: str,
) -> dict[str, Any]:
    if plan_obj.get("operation") != DOMAINS_ADD_OPERATION:
        raise ValidationError("Refused: plan operation does not match domains add")
    if plan_obj.get("host") != host:
        raise ValidationError("Refused: plan host does not match tool host")
    if plan_obj.get("endpoint") != DOMAINS_ADD_PATH:
        raise ValidationError("Refused: plan endpoint does not match tool endpoint")
    if plan_obj.get("snapshot_available") is not False:
        raise ValidationError("Refused: plan snapshot availability has drifted or changed")
    if plan_obj.get("rollback_supported") is not False:
        raise ValidationError("Refused: plan rollback support has drifted or changed")
    if plan_obj.get("safety_warning") != DOMAINS_ADD_NO_SNAPSHOT_WARNING:
        raise ValidationError("Refused: plan safety warning has drifted or changed")

    apply_requirements = plan_obj.get("apply_requirements")
    if not isinstance(apply_requirements, dict):
        raise ValidationError("Refused: plan apply_requirements must be an object")
    expected_requirements = _requires_no_safety_bypass()
    for key, expected in expected_requirements.items():
        if apply_requirements.get(key) != expected:
            raise ValidationError("Refused: plan apply_requirements must be unchanged since generation")

    body = plan_obj.get("request_body")
    if not isinstance(body, dict):
        raise ValidationError("Refused: plan request_body must be an object")
    domains_payload = body.get("domains")
    if not isinstance(domains_payload, list):
        raise ValidationError("Refused: plan request_body.domains must be a list")

    planned_normalized: list[str] = []
    for index, item in enumerate(domains_payload):
        if not isinstance(item, dict) or "name" not in item or not isinstance(item["name"], str):
            raise ValidationError(f"Refused: invalid item in plan request_body.domains[{index}]")
        planned_name = _normalize_domain(item["name"])
        if planned_name != item["name"]:
            raise ValidationError("Refused: plan domain names must already be normalized")
        planned_normalized.append(planned_name)

    if sorted(set(planned_normalized)) != sorted(planned_normalized):
        raise ValidationError("Refused: plan request_body.domains contains duplicates")

    safety = plan_obj.get("safety")
    if not isinstance(safety, dict):
        raise ValidationError("Refused: plan safety must be an object")
    if safety.get("max_domains") != DOMAINS_ADD_MAX_DOMAINS:
        raise ValidationError("Refused: plan safety.max_domains has drifted or changed")
    duplicates_removed = safety.get("duplicates_removed")
    if not isinstance(duplicates_removed, list):
        raise ValidationError("Refused: plan safety.duplicates_removed has drifted or changed")
    if not all(isinstance(item, str) for item in duplicates_removed):
        raise ValidationError("Refused: plan safety.duplicates_removed has drifted or changed")

    nonce = plan_obj.get("approval_nonce")
    if plan_obj.get("account_bound") is not True or not isinstance(nonce, str):
        raise ValidationError("Prepare a new plan with the GiantPanda token before asking for approval.")
    expected_plan_id = plan_id(
        DOMAINS_ADD_OPERATION,
        host,
        DOMAINS_ADD_PATH,
        sorted(planned_normalized),
        safety=safety,
        nonce=nonce,
        token=token,
        env_file=env_file,
    )
    if plan_obj.get("plan_id") != expected_plan_id:
        raise ValidationError(
            "Plan ID mismatch. Use the original token and settings folder, or prepare a new plan."
        )

    if sorted(normalized_domains) != sorted(planned_normalized):
        raise ValidationError("Refused: provided --domain arguments do not match prepared plan")

    return {
        "request_body": {"domains": [{"name": domain} for domain in sorted(planned_normalized)]},
        "plan_id": expected_plan_id,
    }


def cmd_domains_add(args, ctx) -> int:
    cfg = ctx["cfg"]
    out = ctx["out"]
    env_file = ctx["env_file"]

    if getattr(args, "dry_run", False) and getattr(args, "apply", False):
        out.emit(
            {
                "ok": False,
                "error": "Cannot set both --dry-run and --apply",
                "error_type": "ValidationError",
            }
        )
        return 1

    try:
        normalized_domains, duplicates = _normalize_domains(args.domain or [])
    except ValidationError as exc:
        out.emit({"ok": False, "error": str(exc), "error_type": "ValidationError"})
        return 1

    if not args.apply:
        plan = _build_add_plan(cfg, normalized_domains, duplicates=duplicates, env_file=env_file)
        plan_out = args.plan_out or default_plan_path(plan["plan_id"], env_file=env_file)
        try:
            _check_output_path(plan_out, env_file=env_file)
            write_private_json(plan_out, plan)
        except OSError as exc:
            out.emit(
                {
                    "ok": False,
                    "error": f"Failed to write plan file: {exc}",
                    "error_type": "PlanWriteError",
                }
            )
            return 1
        out.emit(
            {
                "ok": True,
                "command": "domains add",
                "dry_run": True,
                "plan": plan,
                "plan_out": plan_out,
            }
        )
        return 0

    if not args.plan_in:
        out.emit(
            {
                "ok": False,
                "error": "Apply requires --plan-in",
                "error_type": "SafetyRequirementError",
            }
        )
        return 1
    if not args.approve_plan:
        out.emit(
            {
                "ok": False,
                "error": "Apply requires --approve-plan <plan_id>",
                "error_type": "SafetyRequirementError",
            }
        )
        return 1
    if not args.ack_no_snapshot:
        out.emit(
            {
                "ok": False,
                "error": "Apply requires --ack-no-snapshot",
                "error_type": "SafetyRequirementError",
            }
        )
        return 1
    try:
        plan_obj = _load_plan(args.plan_in)
    except ValidationError as exc:
        out.emit({"ok": False, "error": str(exc), "error_type": "InvalidPlanError"})
        return 1

    if not cfg.token or config_mod.is_placeholder_token(cfg.token):
        out.emit(
            {
                "ok": False,
                "error": "GIANTPANDA_API_TOKEN is required for domains add",
                "error_type": "AuthenticationError",
            }
        )
        return 1

    try:
        validated = _validate_plan(
            plan_obj,
            host=cfg.host.rstrip("/"),
            normalized_domains=normalized_domains,
            token=cfg.token,
            env_file=env_file,
        )
    except ValidationError as exc:
        out.emit({"ok": False, "error": str(exc), "error_type": "InvalidPlanError"})
        return 1

    if args.approve_plan != validated["plan_id"]:
        out.emit(
            {
                "ok": False,
                "error": "Plan approval id does not match prepared plan",
                "error_type": "SafetyRequirementError",
            }
        )
        return 1

    return _send_add(args, cfg, out, validated, env_file=env_file, domains=normalized_domains)


def _check_output_path(path: str, *, env_file: str, plan_in: str | None = None) -> None:
    output = Path(path).resolve()
    receipt_dir = Path(default_receipt_path("", env_file=env_file)).parent.resolve()
    protected = {Path(env_file).resolve()}
    if plan_in:
        protected.add(Path(plan_in).resolve())
    protected_file = output in protected or (
        output.exists() and any(file.exists() and file.samefile(output) for file in protected)
    )
    reserved_folder = output.is_relative_to(receipt_dir) or (
        receipt_dir.exists()
        and any(parent.exists() and parent.samefile(receipt_dir) for parent in output.parents)
    )
    if protected_file or reserved_folder:
        raise ValidationError("Choose an output file separate from the settings, plan, and saved receipts.")


def _add_result(data: Any, domains: list[str]) -> dict[str, list[str]]:
    if isinstance(data, dict):
        created = data.get("created")
        existing = data.get("existing")
        if (
            isinstance(created, list)
            and isinstance(existing, list)
            and all(isinstance(name, str) for name in created + existing)
            and type(data.get("created_count")) is int
            and type(data.get("existing_count")) is int
            and data["created_count"] == len(created)
            and data["existing_count"] == len(existing)
        ):
            reported = created + existing
            if len(set(reported)) == len(reported) and set(reported) <= set(domains):
                return {
                    "created": sorted(created),
                    "existing": sorted(existing),
                    "needs_check": sorted(set(domains) - set(reported)),
                }
    return {"created": [], "existing": [], "needs_check": domains}


def _send_add(args, cfg: config_mod.Config, out, plan, *, env_file: str, domains: list[str]) -> int:
    plan_id_value = plan["plan_id"]
    canonical_path = default_receipt_path(plan_id_value, env_file=env_file)
    receipt_out = args.receipt_out or canonical_path
    if args.receipt_out and Path(receipt_out).absolute() != Path(canonical_path):
        _check_output_path(receipt_out, env_file=env_file, plan_in=args.plan_in)
        if Path(receipt_out).exists():
            raise ValidationError("Choose a new file for the receipt copy.")
    receipt = {
        "command": DOMAINS_ADD_OPERATION,
        "tool": "giantpanda",
        "version": __version__,
        "plan_id": plan_id_value,
        "request": plan["request_body"],
        "provider": {"host": cfg.host, "endpoint": DOMAINS_ADD_PATH},
        "snapshot_available": False,
        "rollback_supported": False,
        "status": "pending",
        "verification_available": False,
        "verification": _add_result(None, domains),
        "applied_may_have_occurred": True,
    }
    try:
        write_private_json(canonical_path, receipt, exclusive=True)
    except FileExistsError:
        out.emit({
            "ok": False,
            "error": "This approval was already used. Open the saved receipt before sending anything again.",
            "error_type": "ApprovalAlreadyUsed",
            "receipt_out": canonical_path,
        })
        return 1
    except OSError:
        out.emit({
            "ok": False,
            "error": "Could not save the receipt before sending. No request was sent.",
            "error_type": "ReceiptWriteError",
            "receipt_out": canonical_path,
        })
        return 1

    client = HttpClient(timeout_s=cfg.timeout_s, verbose=bool(args.verbose))
    endpoint = cfg.host + DOMAINS_ADD_PATH
    headers = {"Authorization": f"Token {cfg.token}", "Accept": "application/json"}
    error_type = None
    error = None
    try:
        response = client.request("POST", endpoint, headers=headers, json_body=plan["request_body"])
    except HttpError as exc:
        if exc.status is not None:
            receipt["provider"]["status"] = exc.status
        if exc.status in {400, 401, 403}:
            receipt["status"] = "rejected"
            receipt["applied_may_have_occurred"] = False
            receipt["verification"]["needs_check"] = []
            error = f"GiantPanda refused the request (HTTP {exc.status}). Fix the cause and review a fresh plan."
        else:
            receipt["status"] = "needs_check"
            error = "GiantPanda did not confirm the result. Check the domains in the dashboard before sending again."
        error_type = "ProviderError"
    else:
        receipt["provider"].update(status=response.status, url=endpoint)
        try:
            data = response.json()
        except ValueError:
            data = None
            error_type = "ResponseParseError"
        result = _add_result(data, domains) if response.status == 200 else _add_result(None, domains)
        receipt["verification"] = result
        confirmed = not result["needs_check"]
        receipt["verification_available"] = confirmed
        receipt["status"] = "confirmed" if confirmed else "needs_check"
        receipt["applied_may_have_occurred"] = not confirmed
        if not confirmed:
            error = "GiantPanda did not confirm every domain. Check the remaining domains in the dashboard."
            error_type = error_type or "UnconfirmedResult"

    result_payload = {
        "ok": error is None,
        "command": DOMAINS_ADD_OPERATION,
        "plan_id": plan_id_value,
        "provider": {**receipt["provider"], "verification": receipt["verification"]},
        "receipt": receipt,
        "receipt_out": canonical_path,
        "verification_available": receipt["verification_available"],
        "applied": receipt["status"] == "confirmed",
        "applied_may_have_occurred": receipt["applied_may_have_occurred"],
    }
    if error:
        result_payload.update(error=error, error_type=error_type)
    try:
        write_private_json(canonical_path, receipt)
        if Path(receipt_out).absolute() != Path(canonical_path):
            write_private_json(receipt_out, receipt, exclusive=True)
            result_payload["receipt_out"] = receipt_out
    except OSError:
        result_payload.update(
            ok=False,
            error="Could not finish saving the receipt. Use the saved receipt and check the dashboard if needed.",
            error_type="ReceiptWriteError",
        )
    out.emit(result_payload)
    return 0 if result_payload["ok"] else 1


def cmd_domains_stats(args, ctx) -> int:
    cfg = ctx["cfg"]
    out = ctx["out"]

    if not cfg.token or config_mod.is_placeholder_token(cfg.token):
        out.emit(
            {
                "ok": False,
                "error": "GIANTPANDA_API_TOKEN is required for domains stats",
                "error_type": "AuthenticationError",
            }
        )
        return 1

    query: dict[str, Any] = {
        "start_date": args.start_date,
        "end_date": args.end_date,
    }
    if args.page is not None:
        query["page"] = args.page
    if args.page_size is not None:
        query["page_size"] = args.page_size

    client = HttpClient(timeout_s=cfg.timeout_s, verbose=bool(args.verbose))
    headers = {"Authorization": f"Token {cfg.token}", "Accept": "application/json"}
    try:
        resp = client.request("GET", cfg.host.rstrip("/") + DOMAINS_STATS_PATH, headers=headers, params=query)
    except HttpError:
        out.emit(
            {
                "ok": False,
                "error": "Provider request failed",
                "command": "domains stats",
                "error_type": "ProviderError",
            }
        )
        return 1
    try:
        payload = resp.json()
    except Exception:  # noqa: BLE001
        out.emit(
            {
                "ok": False,
                "error": "Provider response is not valid JSON",
                "command": "domains stats",
                "error_type": "ResponseParseError",
            }
        )
        return 1

    out.emit(
        {
            "ok": True,
            "command": "domains stats",
            "provider": {
                "host": cfg.host,
                "endpoint": DOMAINS_STATS_PATH,
                "status": resp.status,
                "url": resp.url,
                "json": payload,
            },
        }
    )
    return 0
