from __future__ import annotations

from typing import Any, Final

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


def _build_add_plan(cfg, normalized_domains: list[str], *, duplicates: list[str]) -> dict[str, Any]:
    request_domains = [{"name": domain} for domain in normalized_domains]
    request_body = {"domains": request_domains}
    safety = {
        "max_domains": DOMAINS_ADD_MAX_DOMAINS,
        "duplicates_removed": sorted(set(duplicates)),
    }
    generated_plan_id = plan_id(
        DOMAINS_ADD_OPERATION,
        cfg.host.rstrip("/"),
        DOMAINS_ADD_PATH,
        normalized_domains,
        safety=safety,
    )
    return {
        "operation": DOMAINS_ADD_OPERATION,
        "host": cfg.host.rstrip("/"),
        "endpoint": DOMAINS_ADD_PATH,
        "plan_id": generated_plan_id,
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
    plan_in: str,
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

    expected_plan_id = plan_id(
        DOMAINS_ADD_OPERATION,
        host,
        DOMAINS_ADD_PATH,
        sorted(planned_normalized),
        safety=safety,
    )
    if plan_obj.get("plan_id") != expected_plan_id:
        raise ValidationError(
            f"Refused: plan {plan_in} is invalid or has drifted (plan_id mismatch)"
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

    plan = _build_add_plan(cfg, normalized_domains, duplicates=duplicates)

    if not getattr(args, "apply", False):
        plan_out = args.plan_out or default_plan_path(plan["plan_id"], env_file=env_file)
        try:
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

    try:
        validated = _validate_plan(
            plan_obj,
            host=cfg.host.rstrip("/"),
            normalized_domains=normalized_domains,
            plan_in=args.plan_in,
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

    if not cfg.token or config_mod.is_placeholder_token(cfg.token):
        out.emit(
            {
                "ok": False,
                "error": "GIANTPANDA_API_TOKEN is required for domains add",
                "error_type": "AuthenticationError",
            }
        )
        return 1

    headers = {"Authorization": f"Token {cfg.token}", "Accept": "application/json"}
    client = HttpClient(timeout_s=cfg.timeout_s, verbose=bool(args.verbose))
    endpoint = cfg.host.rstrip("/") + DOMAINS_ADD_PATH
    body = validated["request_body"]
    try:
        response = client.request("POST", endpoint, headers=headers, json_body=body)
    except HttpError:
        out.emit(
            {
                "ok": False,
                "error": "Provider request failed",
                "command": "domains add",
                "error_type": "ProviderError",
            }
        )
        return 1

    receipt_out = args.receipt_out or default_receipt_path(
        plan["plan_id"],
        env_file=env_file,
        unique=True,
    )
    provider = {
        "host": cfg.host.rstrip("/"),
        "endpoint": DOMAINS_ADD_PATH,
        "status": response.status,
        "url": response.url,
    }
    receipt = {
        "command": "domains add",
        "tool": "giantpanda",
        "version": __version__,
        "plan_id": validated["plan_id"],
        "request": body,
        "provider": provider,
        "snapshot_available": False,
        "rollback_supported": False,
    }

    try:
        verification = response.json()
        receipt["verification"] = verification
        receipt["verification_available"] = True
    except Exception:
        receipt["verification_available"] = False
        receipt["verification"] = {"available": False, "reason": "Provider response is not valid JSON"}
        receipt["applied_may_have_occurred"] = True
        failure_message = (
            "Provider response is not valid JSON; request may have occurred, but verification is unavailable."
        )
        try:
            write_private_json(receipt_out, receipt)
        except OSError as exc:
            out.emit(
                {
                    "ok": False,
                    "error": (
                        "Provider response is not valid JSON and receipt write failed; request may "
                        "have occurred."
                    ),
                    "error_type": "ResponseParseError",
                    "command": "domains add",
                    "applied_may_have_occurred": True,
                    "receipt_save_error": str(exc),
                    "provider": provider,
                    "receipt": receipt,
                    "receipt_out": receipt_out,
                }
            )
            return 1
        out.emit(
            {
                "ok": False,
                "error": failure_message,
                "error_type": "ResponseParseError",
                "command": "domains add",
                "applied_may_have_occurred": True,
                "verification_available": False,
                "provider": provider,
                "receipt": receipt,
                "receipt_out": receipt_out,
            }
        )
        return 1

    try:
        write_private_json(receipt_out, receipt)
    except OSError as exc:
        out.emit(
            {
                "ok": False,
                "error": "Receipt write failed after provider success",
                "error_type": "ReceiptWriteError",
                "command": "domains add",
                "applied": True,
                "provider": {
                    **provider,
                    "verification": verification,
                },
                "verification": verification,
                "receipt_out": receipt_out,
                "receipt_save_error": str(exc),
            }
        )
        return 1

    out.emit(
        {
            "ok": True,
            "command": "domains add",
            "plan_id": validated["plan_id"],
            "provider": {
                **provider,
                "verification": verification,
            },
            "receipt": receipt,
            "applied": True,
            "receipt_out": receipt_out,
        }
    )
    return 0

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
