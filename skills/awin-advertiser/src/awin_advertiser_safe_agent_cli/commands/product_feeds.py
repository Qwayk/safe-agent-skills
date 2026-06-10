from __future__ import annotations

import hashlib
import json
import re
import time
from pathlib import Path
from typing import Any

from ..errors import SafetyError, ValidationError
from ..json_files import read_json_file, write_json_file
from .read_api import redact_error, require_read_context


_MAX_PRODUCTS = 2_000_000
_REQUIRED_FIELDS = ("id", "title", "description", "link", "image_link")
_LOCALE_RE = re.compile(r"^[a-z]{2}_[A-Z]{2}$")


def _utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _sha256_of_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _validate_feed_row(*, row: dict[str, Any], row_num: int) -> None:
    if not isinstance(row, dict):
        raise ValidationError(f"Product feed row #{row_num} must be a JSON object")

    missing = [field for field in _REQUIRED_FIELDS if field not in row]
    if missing:
        raise ValidationError(
            f"Product feed row #{row_num} is missing required field(s): {', '.join(missing)}"
        )


def _load_feed_payload(path_raw: str | None) -> tuple[str, Path, int]:
    source_path = Path(path_raw) if path_raw else Path("")

    if not source_path.exists():
        raise ValidationError(f"Feed file not found: {source_path}")

    try:
        body_text = source_path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise ValidationError(f"Failed to read --feed-file as UTF-8: {exc}") from None

    if not body_text.strip():
        raise ValidationError("--feed-file must contain at least one JSONL row")

    rows = body_text.splitlines()
    if not rows:
        raise ValidationError("--feed-file must contain at least one JSONL row")

    parsed: list[dict[str, Any]] = []
    for idx, raw in enumerate(rows, start=1):
        line = raw.strip()
        if not line:
            raise ValidationError(f"Product feed line {idx} is empty")
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValidationError(f"Product feed line {idx} is not valid JSONL: {exc}") from None
        _validate_feed_row(row=row, row_num=idx)
        if not isinstance(row, dict):
            raise ValidationError(f"Product feed line {idx} is not a JSON object")
        parsed.append(row)

    if len(parsed) > _MAX_PRODUCTS:
        raise ValidationError(f"Product feed exceeds maximum supported rows: {_MAX_PRODUCTS}")

    return body_text, source_path, len(parsed)


def _has_errors(payload: Any) -> list[str]:
    messages: list[str] = []

    def walk(obj: Any) -> None:
        if isinstance(obj, dict):
            for key, value in obj.items():
                lower = str(key).lower()
                if lower in {"errors", "error"}:
                    if isinstance(value, list) and value:
                        for item in value:
                            messages.append(str(item))
                    elif value:
                        messages.append(str(value))
                if isinstance(value, (dict, list)):
                    walk(value)
            status = str(obj.get("status") or "").strip().lower()
            if status in {"error", "failed", "validation_failed", "validation failed"}:
                messages.append(f"status={status}")
            success = obj.get("success")
            if success is False:
                messages.append("success=false")
            return

        if isinstance(obj, list):
            for item in obj:
                walk(item)

    walk(payload)
    return messages


def _build_plan(
    *,
    ctx: dict[str, Any],
    advertiser_id: str,
    source_path: Path,
    vertical: str,
    locale: str,
    product_count: int,
) -> dict[str, Any]:
    return {
        "tool": ctx.get("tool"),
        "version": ctx.get("tool_version"),
        "generated_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str"),
        "selector": {
            "advertiser_id": advertiser_id,
            "endpoint": "advertisers/{advertiser_id}/awinfeeds/{vertical}/{locale}/products".format(
                advertiser_id=advertiser_id,
                vertical=vertical,
                locale=locale,
            ),
            "vertical": vertical,
            "locale": locale,
        },
        "risk_level": "high",
        "risk_reasons": ["product-feeds upload"],
        "preconditions": ["Dry-run only by default", "Apply requires --apply --yes --ack-irreversible"],
        "baseline": {
            "env_fingerprint": ctx["cfg"].base_url,
            "feed_file": str(source_path),
            "feed_file_sha256": _sha256_of_file(source_path),
            "product_count": product_count,
            "vertical": vertical,
            "locale": locale,
        },
        "proposed_changes": [
            {
                "resource": "product_feeds",
                "action": "upload",
                "advertiser_id": advertiser_id,
                "vertical": vertical,
                "locale": locale,
            }
        ],
        "verification_plan": {
            "type": "provider-response",
            "notes": "Refuse on transport or payload-validation failure; review response body for validation errors",
        },
        "rollback": {
            "supported": False,
            "notes": "No rollback endpoint is defined in current product-feed docs",
        },
    }


def _validate_plan(
    *,
    advertiser_id: str,
    plan_obj: Any,
    source_path: Path,
    ctx: dict[str, Any],
    vertical: str,
    locale: str,
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
    if str(selector.get("vertical") or "") != vertical:
        raise SafetyError("Refused: --plan-in vertical does not match")
    if str(selector.get("locale") or "") != locale:
        raise SafetyError("Refused: --plan-in locale does not match")

    expected_endpoint = selector.get("endpoint")
    if not isinstance(expected_endpoint, str) or not expected_endpoint:
        raise ValidationError("--plan-in is missing endpoint")

    expected_endpoint = f"advertisers/{advertiser_id}/awinfeeds/{vertical}/{locale}/products"
    if expected_endpoint not in str(selector.get("endpoint") or ""):
        raise SafetyError("Refused: --plan-in selector does not match requested endpoint")

    expected_sha = str(baseline.get("feed_file_sha256") or "")
    if not expected_sha:
        raise ValidationError("--plan-in is missing feed_file_sha256")
    if expected_sha != _sha256_of_file(source_path):
        raise SafetyError("Refused: feed file changed since --plan-in was created")


def _build_receipt(*, ctx: dict[str, Any], advertiser_id: str, response_status: int, product_count: int) -> dict[str, Any]:
    return {
        "tool": ctx.get("tool"),
        "version": ctx.get("tool_version"),
        "applied_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str"),
        "selector": {
            "advertiser_id": advertiser_id,
            "endpoint": "advertisers/{advertiser_id}/awinfeeds/{vertical}/{locale}/products".format(
                advertiser_id=advertiser_id,
                vertical=ctx["vertical"],
                locale=ctx["locale"],
            ),
        },
        "changed": True,
        "verification": {
            "ok": 200 <= int(response_status) < 300,
            "details": {
                "response_status": response_status,
                "product_count": product_count,
            },
        },
        "diff_applied": [
            {
                "resource": "product_feeds",
                "action": "uploaded",
                "advertiser_id": advertiser_id,
                "product_count": product_count,
            }
        ],
        "backups": [],
        "rollback_plan": None,
    }


def cmd_product_feeds_upload(args, ctx) -> int:
    cfg = require_read_context(ctx["out"], ctx["cfg"])
    if cfg is None:
        return 1

    advertiser_id = str(getattr(args, "advertiser_id", "") or "").strip()
    if not advertiser_id:
        raise ValidationError("Missing --advertiser-id")

    vertical = str(getattr(args, "vertical", "") or "").strip()
    if not vertical:
        raise ValidationError("Missing --vertical")
    if vertical != "retail":
        raise ValidationError("vertical must be retail")

    locale = str(getattr(args, "locale", "") or "").strip()
    if not locale:
        raise ValidationError("Missing --locale")
    if not _LOCALE_RE.match(locale):
        raise ValidationError("locale must be a token like en_GB")

    body_text, source_path, product_count = _load_feed_payload(getattr(args, "feed_file", None))

    plan = _build_plan(
        ctx=ctx,
        advertiser_id=advertiser_id,
        source_path=source_path,
        vertical=vertical,
        locale=locale,
        product_count=product_count,
    )

    if not bool(ctx.get("apply")):
        plan_path = None
        if isinstance(ctx.get("plan_out"), str):
            plan_path = write_json_file(ctx["plan_out"], plan)

        out = {
            "ok": True,
            "dry_run": True,
            "operation": "product-feeds upload",
            "advertiser_id": advertiser_id,
            "endpoint": f"/advertisers/{advertiser_id}/awinfeeds/{vertical}/{locale}/products",
            "method": "POST",
            "product_count": product_count,
            "plan": plan,
            "plan_out": plan_path if isinstance(ctx.get("plan_out"), str) else None,
        }
        ctx["out"].emit(out)
        ctx["audit"].write("product_feeds.upload.plan", out)
        return 0

    if not ctx.get("plan_in"):
        raise SafetyError("Refused: product-feeds upload requires --apply with --plan-in")

    if not bool(ctx.get("yes")):
        raise SafetyError("Refused: product-feeds upload requires --apply --yes")

    if not bool(ctx.get("ack_irreversible", False)):
        raise SafetyError("Refused: product-feeds upload requires --apply --yes --ack-irreversible")

    _validate_plan(
        advertiser_id=advertiser_id,
        plan_obj=read_json_file(str(ctx["plan_in"])),
        source_path=source_path,
        ctx=ctx,
        vertical=vertical,
        locale=locale,
    )

    headers = {
        "Authorization": f"Bearer {cfg.token}",
        "content-type": "application/x-ndjson",
    }
    endpoint = f"advertisers/{advertiser_id}/awinfeeds/{vertical}/{locale}/products"
    http = ctx["http_client"]
    try:
        response = http.request(
            "POST",
            f"{cfg.base_url.rstrip('/')}/{endpoint}",
            headers=headers,
            params={},
            data=body_text,
        )
    except Exception as exc:  # noqa: BLE001
        message = redact_error(str(exc), cfg.token)
        raise ValidationError(f"product-feeds upload request failed: {message}") from exc

    try:
        payload = response.json()
    except Exception as exc:  # noqa: BLE001
        raise ValidationError(f"product-feeds upload response was not JSON: {exc}") from exc

    errors = _has_errors(payload)
    if errors:
        raise ValidationError(f"product-feeds upload validation failed: {', '.join(sorted(set(errors)))}")

    receipt = _build_receipt(
        ctx={**ctx, "vertical": vertical, "locale": locale},
        advertiser_id=advertiser_id,
        response_status=response.status,
        product_count=product_count,
    )

    if bool(ctx.get("receipt_out")):
        receipt_out = write_json_file(ctx["receipt_out"], receipt)
    else:
        receipt_out = None

    result = {
        "ok": True,
        "dry_run": False,
        "operation": "product-feeds upload",
        "advertiser_id": advertiser_id,
        "endpoint": f"/advertisers/{advertiser_id}/awinfeeds/{vertical}/{locale}/products",
        "method": "POST",
        "status": response.status,
        "product_count": product_count,
        "result": {"response_status": response.status},
        "receipt": receipt,
        "receipt_out": receipt_out,
    }
    ctx["audit"].write("product_feeds.upload.apply", result)
    ctx["out"].emit(result)
    return 0
