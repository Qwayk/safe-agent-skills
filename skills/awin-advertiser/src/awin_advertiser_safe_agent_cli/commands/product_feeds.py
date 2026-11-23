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
from .write_api import check_plan, credential_fingerprint, finish_write, post_write, response_object


_MAX_PRODUCTS = 2_000_000
_REQUIRED_FIELDS = ("id", "title", "description", "link", "image_link")
_LOCALE_RE = re.compile(r"^[a-z]{2}_[A-Z]{2}$")


def _utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _validate_feed_row(*, row: dict[str, Any], row_num: int) -> None:
    if not isinstance(row, dict):
        raise ValidationError(f"Product feed row #{row_num} must be a JSON object")

    missing = [field for field in _REQUIRED_FIELDS if field not in row]
    if missing:
        raise ValidationError(
            f"Product feed row #{row_num} is missing required field(s): {', '.join(missing)}"
        )


def _load_feed_payload(path_raw: str | None) -> tuple[bytes, Path, int, str]:
    source_path = Path(path_raw) if path_raw else Path("")

    if not source_path.exists():
        raise ValidationError(f"Feed file not found: {source_path}")

    try:
        body_bytes = source_path.read_bytes()
        body_text = body_bytes.decode("utf-8")
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

    return body_bytes, source_path, len(parsed), hashlib.sha256(body_bytes).hexdigest()


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
    file_digest: str,
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
            "credential_fingerprint": credential_fingerprint(ctx["cfg"]),
            "feed_file": str(source_path),
            "feed_file_sha256": file_digest,
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
            "notes": "Check the received product count, feed version and any errors.",
        },
        "rollback": {
            "supported": False,
            "notes": "No rollback endpoint is defined in current product-feed docs",
        },
    }


def _build_receipt(*, ctx: dict[str, Any], advertiser_id: str, product_count: int) -> dict[str, Any]:
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
        "verification": {
            "details": {
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

    body_bytes, source_path, product_count, file_digest = _load_feed_payload(getattr(args, "feed_file", None))

    plan = _build_plan(
        ctx=ctx,
        advertiser_id=advertiser_id,
        source_path=source_path,
        file_digest=file_digest,
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

    endpoint = f"advertisers/{advertiser_id}/awinfeeds/{vertical}/{locale}/products"
    selector = check_plan(
        read_json_file(ctx["plan_in"]), cfg=cfg, advertiser_id=advertiser_id, endpoint=endpoint,
        file_field="feed_file_sha256", file_digest=file_digest, file_description="feed file",
    )
    if selector.get("vertical") != vertical or selector.get("locale") != locale:
        raise SafetyError("Refused: the plan does not match the feed type or locale.")

    response, details = post_write(
        ctx, endpoint,
        headers={"Authorization": f"Bearer {cfg.token}", "content-type": "application/jsonlines", "accept": "application/json"},
        params={}, data=body_bytes,
    )
    if response is not None:
        data = response_object(response)
        errors = _has_errors(data)
        details["state"] = "unknown"
        if errors:
            message = ", ".join(sorted(set(errors)))
            details.update(state="rejected", error=f"Product feed validation failed: {redact_error(message, cfg.token)}")
        elif data is not None:
            received, version = data.get("productsReceived"), data.get("version")
            if type(received) is int:
                details["products_received"] = received
            if type(version) is int:
                details["feed_version"] = version
            if isinstance(data.get("info"), list):
                details["warning_count"] = len(data["info"])
            if response.status == 200 and received == product_count and type(received) is int and type(version) is int:
                details["state"] = "confirmed"

    return finish_write(
        ctx, operation="product-feeds upload", event="product_feeds.upload.apply",
        receipt=_build_receipt(
            ctx={**ctx, "vertical": vertical, "locale": locale}, advertiser_id=advertiser_id,
            product_count=product_count,
        ),
        details=details,
        next_step="Check the current feed version and product count in Awin before uploading the file again.",
        fields={"product_count": product_count},
    )
