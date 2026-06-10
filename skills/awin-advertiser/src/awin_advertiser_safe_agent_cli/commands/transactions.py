from __future__ import annotations

import hashlib
import time
from pathlib import Path
from typing import Any

from ..errors import SafetyError, ValidationError
from ..json_files import read_json_file, write_json_file
from .read_api import extract_list, parse_iso8601, read_request, redact_error, require_read_context

_MAX_BATCH_ACTIONS = 40000
_ALLOWED_BATCH_ACTIONS = {"approve", "decline", "amend", "amendTrackingParameters"}


def _utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _sha256_of_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _strip(value: Any) -> str:
    return str(value or "").strip()


def _count_batch_actions(actions: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for action in actions:
        action_name = _strip(action.get("action"))
        if not action_name:
            continue
        counts[action_name] = counts.get(action_name, 0) + 1
    return counts


def _build_list_query(args) -> dict[str, object]:
    params: dict[str, object] = {
        "startDate": parse_iso8601(str(getattr(args, "start_date")), field="--start-date"),
        "endDate": parse_iso8601(str(getattr(args, "end_date")), field="--end-date"),
    }

    date_type = str(getattr(args, "date_type", "") or "").strip()
    if date_type:
        if date_type not in {"transaction", "validation", "amendment"}:
            raise ValidationError("Invalid --date-type (expected transaction|validation|amendment)")
        params["dateType"] = date_type

    publisher_ids = getattr(args, "publisher_id") or []
    if publisher_ids:
        cleaned = [str(x).strip() for x in publisher_ids if str(x).strip()]
        if cleaned:
            params["publisherId"] = ",".join(cleaned)

    status = str(getattr(args, "status") or "").strip()
    if status:
        if status not in {"pending", "approved", "declined", "deleted"}:
            raise ValidationError("Invalid --status (expected pending|approved|declined|deleted)")
        params["status"] = status

    timezone = str(getattr(args, "timezone") or "").strip()
    if timezone:
        params["timezone"] = timezone

    if bool(getattr(args, "show_basket_products", False)):
        params["showBasketProducts"] = "true"

    return params


def _build_ids_query(args) -> dict[str, object]:
    raw_ids = str(getattr(args, "ids") or "").strip()
    if not raw_ids:
        raise ValidationError("Missing --ids")

    ids = [x.strip() for x in raw_ids.split(",") if x.strip()]
    if not ids:
        raise ValidationError("Missing --ids")

    params: dict[str, object] = {"ids": ",".join(ids)}

    timezone = str(getattr(args, "timezone") or "").strip()
    if timezone:
        params["timezone"] = timezone

    if bool(getattr(args, "show_basket_products", False)):
        params["showBasketProducts"] = "true"

    return params


def _build_reports_query(
    args,
    *,
    supports_campaign: bool = False,
    supports_publisher_filter: bool = True,
    supports_date_type: bool = True,
) -> dict[str, object]:
    params: dict[str, object] = {
        "startDate": parse_iso8601(str(getattr(args, "start_date")), field="--start-date"),
        "endDate": parse_iso8601(str(getattr(args, "end_date")), field="--end-date"),
    }

    date_type = str(getattr(args, "date_type", None) or "").strip()
    if date_type and supports_date_type:
        if date_type not in {"transaction", "validation"}:
            raise ValidationError("Invalid --date-type (expected transaction|validation)")
        params["dateType"] = date_type
    elif date_type and not supports_date_type:
        raise ValidationError("Campaign report command does not support --date-type")

    timezone = str(getattr(args, "timezone") or "").strip()
    if timezone:
        params["timezone"] = timezone

    interval = str(getattr(args, "interval", None) or "").strip()
    if interval:
        params["interval"] = interval

    if supports_campaign:
        campaign = str(getattr(args, "campaign", None) or "").strip()
        if campaign:
            params["campaign"] = campaign
            if len(campaign) < 3 or len(campaign) > 128:
                raise ValidationError("--campaign must be 3-128 characters")

        if bool(getattr(args, "include_numbers_without_campaign", False)):
            params["includeNumbersWithoutCampaign"] = "true"

    if supports_publisher_filter:
        publisher_ids = getattr(args, "publisher_id") or []
        if publisher_ids:
            cleaned = [str(x).strip() for x in publisher_ids if str(x).strip()]
            if cleaned:
                params["publisherIds"] = ",".join(cleaned)

    return params


def _build_job_show_query(args) -> dict[str, object]:
    params: dict[str, object] = {}
    job_output = str(getattr(args, "job_output") or "").strip()
    if job_output:
        if job_output not in {"errors", "all"}:
            raise ValidationError("Invalid --job-output (expected errors|all)")
        params["output"] = job_output
    return params


def _do_transactions_request(
    args,
    ctx,
    *,
    query: dict[str, object],
    command_name: str,
    endpoint: str,
    payload_key: str,
    include_access_token: bool,
    list_response: bool = True,
) -> int:
    cfg = require_read_context(ctx["out"], ctx["cfg"])
    if cfg is None:
        return 1

    advertiser_id = str(getattr(args, "advertiser_id", "") or "").strip()
    if not advertiser_id:
        out = {
            "ok": False,
            "error": "Missing --advertiser-id",
            "error_type": "ValidationError",
            "blocked": False,
        }
        ctx["out"].emit(out)
        return 1

    token = cfg.token
    http = ctx["http_client"]
    try:
        resp = read_request(
            http=http,
            base_url=cfg.base_url,
            token=token,
            endpoint=endpoint,
            params=query,
            include_access_token=include_access_token,
        )
    except Exception as exc:  # noqa: BLE001
        message = redact_error(str(exc), token)
        raise ValidationError(f"{command_name} request failed: {message}") from exc

    try:
        payload = resp.json()
    except Exception as exc:  # noqa: BLE001
        raise ValidationError(f"{command_name} response was not JSON: {exc}") from exc

    if list_response:
        rows = extract_list(payload, keys=("rows", "transactions", "jobs", "publishers", "items", "data", "results"))
    else:
        rows = payload

    out_data = {
        "ok": True,
        "command": command_name,
        "advertiser_id": advertiser_id,
        "endpoint": f"/{endpoint}",
        "method": "GET",
        "status": resp.status,
    }

    if bool(payload_key):
        out_data[payload_key] = rows
    if isinstance(rows, list):
        out_data["count"] = len(rows)
    if query:
        out_data["query"] = query
    if not list_response and isinstance(rows, dict):
        out_data[payload_key] = rows

    ctx["out"].emit(out_data)
    return 0


def _do_report_request(args, ctx, *, query: dict[str, object], command_name: str, endpoint: str, payload_key: str) -> int:
    return _do_transactions_request(
        args,
        ctx,
        query=query,
        command_name=command_name,
        endpoint=endpoint,
        payload_key=payload_key,
        include_access_token=True,
        list_response=True,
    )


def _validate_batch_action(*, action_payload: object, action_num: int) -> None:
    if not isinstance(action_payload, dict):
        raise ValidationError(f"Item #{action_num} must be a JSON object")

    action = _strip(action_payload.get("action"))
    if action not in _ALLOWED_BATCH_ACTIONS:
        raise ValidationError(f"Item #{action_num} action must be one of approve|decline|amend|amendTrackingParameters")

    transaction = action_payload.get("transaction")
    if not isinstance(transaction, dict):
        raise ValidationError(f"Item #{action_num} must include transaction object")

    _validate_transaction_target(transaction=transaction, action_num=action_num)

    if action == "decline":
        _validate_decline_action(action_payload=action_payload, action_num=action_num)
    elif action == "amend":
        _validate_amend_action(action_payload=action_payload, action_num=action_num)
    elif action == "amendTrackingParameters":
        _validate_amend_tracking_parameters_action(action_payload=action_payload, action_num=action_num)


def _validate_batch_payload(*, batch_payload: list[dict[str, Any]]) -> None:
    if not batch_payload:
        raise ValidationError("--batch-file must contain at least one action")

    if len(batch_payload) > _MAX_BATCH_ACTIONS:
        raise ValidationError(f"Maximum supported batch size is {_MAX_BATCH_ACTIONS}")

    for idx, item in enumerate(batch_payload, start=1):
        _validate_batch_action(action_payload=item, action_num=idx)


def _validate_transaction_target(*, transaction: dict[str, Any], action_num: int) -> None:
    transaction_id = _strip(transaction.get("transactionId"))
    order_ref = _strip(transaction.get("orderRef"))
    transaction_date = _strip(transaction.get("transactionDate"))
    timezone = _strip(transaction.get("timezone"))

    if transaction_date:
        parse_iso8601(transaction_date, field=f"item #{action_num} transaction.transactionDate")

    if transaction_id:
        return

    if order_ref and transaction_date and timezone:
        return

    if order_ref or transaction_date or timezone:
        raise ValidationError(
            f"Item #{action_num} must include either transactionId OR orderRef + transactionDate + timezone"
        )

    raise ValidationError(f"Item #{action_num} must include either transactionId OR orderRef + transactionDate + timezone")


def _validate_decline_action(*, action_payload: dict[str, Any], action_num: int) -> None:
    transaction = action_payload.get("transaction")
    if not isinstance(transaction, dict):
        raise ValidationError(f"Item #{action_num} must include transaction object")
    if not _strip(transaction.get("declineReason")):
        raise ValidationError(f"Item #{action_num} decline action requires declineReason")


def _validate_amend_action(*, action_payload: dict[str, Any], action_num: int) -> None:
    transaction = action_payload.get("transaction")
    if not isinstance(transaction, dict):
        raise ValidationError(f"Item #{action_num} must include transaction object")

    if "approve" in action_payload and not isinstance(action_payload.get("approve"), bool):
        raise ValidationError(f"Item #{action_num} amend action approve must be true or false when provided")

    if not _strip(transaction.get("amendReason")):
        raise ValidationError(f"Item #{action_num} amend action requires amendReason")

    if not _strip(transaction.get("currency")):
        raise ValidationError(f"Item #{action_num} amend action requires currency")

    if "saleAmount" not in transaction:
        raise ValidationError(f"Item #{action_num} amend action requires saleAmount")

    transaction_parts = transaction.get("transactionParts")
    if not isinstance(transaction_parts, list) or not transaction_parts:
        raise ValidationError(f"Item #{action_num} amend action requires transactionParts array")

    for idx, part in enumerate(transaction_parts, start=1):
        if not isinstance(part, dict):
            raise ValidationError(f"Item #{action_num} transactionParts[{idx}] must be an object")
        if "amount" not in part:
            raise ValidationError(f"Item #{action_num} transactionParts[{idx}] is missing amount")
        if not _strip(part.get("commissionGroupCode")):
            raise ValidationError(
                f"Item #{action_num} transactionParts[{idx}] is missing commissionGroupCode"
            )


def _validate_amend_tracking_parameters_action(*, action_payload: dict[str, Any], action_num: int) -> None:
    transaction = action_payload.get("transaction")
    if not isinstance(transaction, dict):
        raise ValidationError(f"Item #{action_num} must include transaction object")

    if not _strip(transaction.get("amendReason")):
        raise ValidationError(f"Item #{action_num} amendTrackingParameters action requires amendReason")

    custom_parameters = transaction.get("customParameters")
    if not isinstance(custom_parameters, dict):
        raise ValidationError(f"Item #{action_num} amendTrackingParameters action requires customParameters object")

    put_values = custom_parameters.get("put")
    if not isinstance(put_values, dict):
        raise ValidationError(
            f"Item #{action_num} amendTrackingParameters action requires customParameters.put object"
        )

    if not put_values:
        raise ValidationError(
            f"Item #{action_num} amendTrackingParameters action requires customParameters.put not empty"
        )

    for key, value in put_values.items():
        if not _strip(key):
            raise ValidationError(f"Item #{action_num} customParameters.put has blank parameter key")
        if not _strip(value):
            raise ValidationError(f"Item #{action_num} customParameters.put value for '{key}' cannot be blank")


def _load_batch_payload(path_raw: str | None) -> tuple[list[dict[str, Any]], Path, int]:
    source_path = Path(path_raw) if path_raw else Path("")
    payload_obj = read_json_file(source_path)

    if not isinstance(payload_obj, list):
        raise ValidationError("--batch-file must be a JSON array of actions")

    payload = [item for item in payload_obj]
    _validate_batch_payload(batch_payload=payload)
    return payload, source_path, len(payload)


def _build_batch_plan(*, ctx: dict[str, Any], advertiser_id: str, batch_payload: list[dict[str, Any]], source_path: Path) -> dict[str, Any]:
    action_breakdown = _count_batch_actions(batch_payload)

    return {
        "tool": ctx.get("tool"),
        "version": ctx.get("tool_version"),
        "generated_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str"),
        "selector": {
            "advertiser_id": advertiser_id,
            "endpoint": f"advertisers/{advertiser_id}/transactions/batch",
        },
        "risk_level": "high",
        "risk_reasons": ["transactions batch validate"],
        "preconditions": ["Dry-run only by default", "Apply requires --apply --yes --ack-irreversible"],
        "baseline": {
            "env_fingerprint": ctx["cfg"].base_url,
            "batch_file": str(source_path),
            "batch_file_sha256": _sha256_of_file(source_path),
            "batch_action_count": len(batch_payload),
            "action_breakdown": action_breakdown,
        },
        "proposed_changes": [
            {
                "resource": "transactions",
                "action": "batch_validate",
                "advertiser_id": advertiser_id,
                "batch_action_count": len(batch_payload),
                "action_breakdown": action_breakdown,
            }
        ],
        "verification_plan": {
            "type": "provider-response",
            "notes": "Refuse on transport or provider rejection; review response for rejected actions",
        },
        "rollback": {
            "supported": False,
            "notes": "No rollback endpoint is defined in current transaction batch docs",
        },
    }


def _validate_plan(
    *,
    advertiser_id: str,
    plan_obj: object,
    source_path: Path,
    ctx: dict[str, Any],
) -> None:
    if not isinstance(plan_obj, dict):
        raise ValidationError("--plan-in must contain a JSON object")

    baseline = plan_obj.get("baseline")
    if not isinstance(baseline, dict):
        raise ValidationError("--plan-in is missing baseline")

    expected_env = str(baseline.get("env_fingerprint") or "")
    if expected_env != ctx["cfg"].base_url:
        raise SafetyError("Refused: --plan-in env_fingerprint does not match the current environment")

    selector = plan_obj.get("selector")
    if not isinstance(selector, dict):
        raise ValidationError("--plan-in is missing selector")

    if str(selector.get("advertiser_id") or "") != advertiser_id:
        raise SafetyError("Refused: --plan-in selector does not match requested advertiser id")

    expected_endpoint = f"advertisers/{advertiser_id}/transactions/batch"
    if str(selector.get("endpoint") or "") != expected_endpoint:
        raise SafetyError("Refused: --plan-in selector does not match requested endpoint")

    expected_sha = str(baseline.get("batch_file_sha256") or "")
    if not expected_sha:
        raise ValidationError("--plan-in is missing batch_file_sha256")
    if expected_sha != _sha256_of_file(source_path):
        raise SafetyError("Refused: batch file changed since --plan-in was created")


def _build_receipt(
    *,
    ctx: dict[str, Any],
    advertiser_id: str,
    response_status: int,
    batch_count: int,
    action_breakdown: dict[str, int],
) -> dict[str, Any]:
    return {
        "tool": ctx.get("tool"),
        "version": ctx.get("tool_version"),
        "applied_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str"),
        "selector": {
            "advertiser_id": advertiser_id,
            "endpoint": f"advertisers/{advertiser_id}/transactions/batch",
        },
        "changed": True,
        "verification": {
            "ok": 200 <= int(response_status) < 300,
            "details": {
                "response_status": response_status,
                "batch_action_count": batch_count,
                "action_breakdown": action_breakdown,
            },
        },
        "diff_applied": [
            {
                "resource": "transactions",
                "action": "batch_validate",
                "advertiser_id": advertiser_id,
                "batch_action_count": batch_count,
                "action_breakdown": action_breakdown,
            }
        ],
        "backups": [],
        "rollback_plan": None,
    }


def _extract_batch_rejections(payload: object) -> list[str]:
    messages: list[str] = []

    def walk(obj: object) -> None:
        if isinstance(obj, dict):
            status = _strip(obj.get("status")).lower()
            if status in {"error", "failed", "validation_failed", "validation failed", "rejected"}:
                messages.append(f"status={status}")

            for field in ("error", "validationError", "validationErrors"):
                value = obj.get(field)
                if isinstance(value, str):
                    messages.append(value)
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, str):
                            messages.append(item)
                        elif isinstance(item, dict):
                            walk(item)
                elif isinstance(value, dict):
                    walk(value)

            for value in obj.values():
                walk(value)
            return

        if isinstance(obj, list):
            for item in obj:
                walk(item)

    walk(payload)
    return messages


def cmd_transactions_list(args, ctx) -> int:
    try:
        query = _build_list_query(args)
    except Exception as exc:  # noqa: BLE001
        if isinstance(exc, ValidationError):
            raise
        raise ValidationError(str(exc)) from exc
    endpoint = f"advertisers/{args.advertiser_id}/transactions/"
    return _do_transactions_request(
        args,
        ctx,
        query=query,
        command_name="transactions list",
        endpoint=endpoint,
        payload_key="transactions",
        include_access_token=True,
    )


def cmd_transactions_by_ids(args, ctx) -> int:
    try:
        query = _build_ids_query(args)
    except Exception as exc:  # noqa: BLE001
        if isinstance(exc, ValidationError):
            raise
        raise ValidationError(str(exc)) from exc
    endpoint = f"advertisers/{args.advertiser_id}/transactions"
    return _do_transactions_request(
        args,
        ctx,
        query=query,
        command_name="transactions by-ids",
        endpoint=endpoint,
        payload_key="transactions",
        include_access_token=True,
    )


def cmd_transactions_jobs_list(args, ctx) -> int:
    query: dict[str, object] = {}
    endpoint = f"advertisers/{args.advertiser_id}/transactions/jobs"
    return _do_transactions_request(
        args,
        ctx,
        query=query,
        command_name="transactions jobs list",
        endpoint=endpoint,
        payload_key="jobs",
        include_access_token=False,
    )


def cmd_transactions_jobs_show(args, ctx) -> int:
    try:
        query = _build_job_show_query(args)
    except Exception as exc:  # noqa: BLE001
        if isinstance(exc, ValidationError):
            raise
        raise ValidationError(str(exc)) from exc

    endpoint = f"advertisers/{args.advertiser_id}/transactions/jobs/{args.job_id}"
    return _do_transactions_request(
        args,
        ctx,
        query=query,
        command_name="transactions jobs show",
        endpoint=endpoint,
        payload_key="job",
        include_access_token=False,
        list_response=False,
    )


def cmd_transactions_batch_validate(args, ctx) -> int:
    cfg = require_read_context(ctx["out"], ctx["cfg"])
    if cfg is None:
        return 1

    advertiser_id = str(getattr(args, "advertiser_id", "") or "").strip()
    if not advertiser_id:
        raise ValidationError("Missing --advertiser-id")

    batch_payload, source_path, action_count = _load_batch_payload(getattr(args, "batch_file", None))
    action_breakdown = _count_batch_actions(batch_payload)
    plan = _build_batch_plan(
        ctx=ctx,
        advertiser_id=advertiser_id,
        batch_payload=batch_payload,
        source_path=source_path,
    )

    if not bool(ctx.get("apply")):
        plan_path = None
        if isinstance(ctx.get("plan_out"), str):
            plan_path = write_json_file(ctx["plan_out"], plan)

        out = {
            "ok": True,
            "dry_run": True,
            "operation": "transactions batch validate",
            "advertiser_id": advertiser_id,
            "endpoint": f"/advertisers/{advertiser_id}/transactions/batch",
            "method": "POST",
            "action_count": action_count,
            "action_breakdown": action_breakdown,
            "plan": plan,
            "plan_out": plan_path if isinstance(ctx.get("plan_out"), str) else None,
        }
        ctx["out"].emit(out)
        ctx["audit"].write("transactions.batch.validate.plan", out)
        return 0

    if not ctx.get("plan_in"):
        raise SafetyError("Refused: transactions batch validate requires --apply with --plan-in")

    if not bool(ctx.get("yes")):
        raise SafetyError("Refused: transactions batch validate requires --apply --yes")

    if not bool(ctx.get("ack_irreversible", False)):
        raise SafetyError("Refused: transactions batch validate requires --apply --yes --ack-irreversible")

    _validate_plan(
        advertiser_id=advertiser_id,
        plan_obj=read_json_file(str(ctx["plan_in"])),
        source_path=source_path,
        ctx=ctx,
    )

    headers = {
        "Authorization": f"Bearer {cfg.token}",
        "content-type": "application/json",
    }
    endpoint = f"advertisers/{advertiser_id}/transactions/batch"
    http = ctx["http_client"]
    try:
        response = http.request(
            "POST",
            f"{cfg.base_url.rstrip('/')}/{endpoint}",
            headers=headers,
            params={"accessToken": cfg.token},
            json_body=batch_payload,
        )
    except Exception as exc:  # noqa: BLE001
        message = redact_error(str(exc), cfg.token)
        raise ValidationError(f"transactions batch validate request failed: {message}") from exc

    try:
        payload = response.json()
    except Exception as exc:  # noqa: BLE001
        raise ValidationError(f"transactions batch validate response was not JSON: {exc}") from exc

    validation_messages = _extract_batch_rejections(payload)
    if validation_messages:
        raise ValidationError(
            "transactions batch validate rejected by provider: "
            f"{', '.join(sorted(set(validation_messages)))}"
        )

    receipt = _build_receipt(
        ctx=ctx,
        advertiser_id=advertiser_id,
        response_status=response.status,
        batch_count=action_count,
        action_breakdown=action_breakdown,
    )

    if bool(ctx.get("receipt_out")):
        receipt_out = write_json_file(ctx["receipt_out"], receipt)
    else:
        receipt_out = None

    out = {
        "ok": True,
        "dry_run": False,
        "operation": "transactions batch validate",
        "advertiser_id": advertiser_id,
        "endpoint": f"/advertisers/{advertiser_id}/transactions/batch",
        "method": "POST",
        "status": response.status,
        "action_count": action_count,
        "action_breakdown": action_breakdown,
        "result": {"response_status": response.status},
        "receipt": receipt,
        "receipt_out": receipt_out,
    }
    ctx["audit"].write("transactions.batch.validate.apply", out)
    ctx["out"].emit(out)
    return 0


def cmd_reports_publisher(args, ctx) -> int:
    try:
        query = _build_reports_query(args, supports_campaign=False, supports_publisher_filter=False, supports_date_type=True)
    except Exception as exc:  # noqa: BLE001
        if isinstance(exc, ValidationError):
            raise
        raise ValidationError(str(exc)) from exc
    endpoint = f"advertisers/{args.advertiser_id}/reports/publisher"
    return _do_report_request(
        args,
        ctx,
        query=query,
        command_name="reports publisher",
        endpoint=endpoint,
        payload_key="report",
    )


def cmd_reports_campaign(args, ctx) -> int:
    try:
        query = _build_reports_query(args, supports_campaign=True, supports_publisher_filter=True, supports_date_type=False)
    except Exception as exc:  # noqa: BLE001
        if isinstance(exc, ValidationError):
            raise
        raise ValidationError(str(exc)) from exc
    endpoint = f"advertisers/{args.advertiser_id}/reports/campaign"
    return _do_report_request(
        args,
        ctx,
        query=query,
        command_name="reports campaign",
        endpoint=endpoint,
        payload_key="report",
    )
