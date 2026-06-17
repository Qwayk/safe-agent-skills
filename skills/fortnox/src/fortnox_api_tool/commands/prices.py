from __future__ import annotations

import hashlib
import time
from pathlib import Path
from typing import Any

from .. import api_runtime
from ..errors import SafetyError, ValidationError
from ..json_files import read_json_file, write_json_file

get_json = api_runtime.get_json
request_json = api_runtime.request_json


def _utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _load_payload_file(path_str: str) -> tuple[Path, dict[str, Any], dict[str, Any]]:
    path = Path(path_str)
    if not path.exists():
        raise ValidationError(f"JSON file not found: {path}")
    obj = read_json_file(path)
    if not isinstance(obj, dict):
        raise ValidationError("JSON file must contain a top-level object")
    price = obj.get("Price")
    if not isinstance(price, dict):
        raise ValidationError("JSON file must contain a top-level Price object")
    return path, obj, price


def _string_field(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _extract_price_key_from_payload(price: dict[str, Any]) -> dict[str, str | None]:
    return {
        "price_list": _string_field(price.get("PriceList")),
        "article_number": _string_field(price.get("ArticleNumber")),
        "from_quantity": _string_field(price.get("FromQuantity")),
    }


def _extract_price_key_from_response(body: dict[str, Any] | None) -> dict[str, str | None]:
    if not isinstance(body, dict):
        return {"price_list": None, "article_number": None, "from_quantity": None}
    price = body.get("Price")
    if not isinstance(price, dict):
        return {"price_list": None, "article_number": None, "from_quantity": None}
    return _extract_price_key_from_payload(price)


def _resolve_full_price_key(*, response_body: dict[str, Any] | None, payload_price: dict[str, Any]) -> dict[str, str]:
    response_key = _extract_price_key_from_response(response_body)
    payload_key = _extract_price_key_from_payload(payload_price)
    resolved = {
        "price_list": response_key["price_list"] or payload_key["price_list"],
        "article_number": response_key["article_number"] or payload_key["article_number"],
        "from_quantity": response_key["from_quantity"] or payload_key["from_quantity"],
    }
    if not all(resolved.values()):
        raise ValidationError("Could not determine full price key for create verification")
    return {
        "price_list": str(resolved["price_list"]),
        "article_number": str(resolved["article_number"]),
        "from_quantity": str(resolved["from_quantity"]),
    }


def _build_plan(
    *,
    action: str,
    selector: dict[str, Any],
    payload_file: Path | None,
    payload_obj: dict[str, Any] | None,
    risk_level: str,
    risk_reasons: list[str],
    verification_plan: dict[str, Any],
    rollback_notes: str,
    ctx: dict[str, Any],
) -> dict[str, Any]:
    baseline: dict[str, Any] = {
        "env_fingerprint": ctx["cfg"].base_url,
        "action": action,
        "selector": selector,
    }
    if payload_file is not None:
        payload_sha256 = _sha256_file(payload_file)
        baseline["payload_sha256"] = payload_sha256
        baseline["json_file_sha256"] = payload_sha256
        baseline["payload_file"] = str(payload_file)
    return {
        "tool": ctx.get("tool") or "fortnox-api-tool",
        "version": ctx.get("tool_version") or None,
        "generated_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "selector": selector,
        "risk_level": risk_level,
        "risk_reasons": risk_reasons,
        "preconditions": [
            "env_fingerprint must match",
            "selector must match",
        ] + (["payload_sha256 must match"] if payload_file is not None else []),
        "baseline": baseline,
        "proposed_changes": [
            {
                "action": action,
                "selector": selector,
                "payload": payload_obj,
            }
        ],
        "verification_plan": verification_plan,
        "rollback": {"supported": False, "notes": rollback_notes},
    }


def _validate_plan_for_apply(
    plan: dict[str, Any],
    *,
    action: str,
    selector: dict[str, Any],
    payload_file: Path | None,
    ctx: dict[str, Any],
) -> None:
    baseline = plan.get("baseline")
    if not isinstance(baseline, dict):
        raise ValidationError("Plan missing baseline dict")
    if str(baseline.get("env_fingerprint") or "") != str(ctx["cfg"].base_url):
        raise SafetyError("Refused: plan env_fingerprint does not match current environment")
    if baseline.get("action") != action:
        raise SafetyError("Refused: plan action does not match the current command")
    if baseline.get("selector") != selector:
        raise SafetyError("Refused: plan selector does not match the current command")
    expected = str(baseline.get("payload_sha256") or "").strip()
    if payload_file is None:
        if expected:
            raise SafetyError("Refused: plan expects the original JSON payload file, but no --json-file was provided")
    else:
        actual = _sha256_file(payload_file)
        if not expected or expected != actual:
            raise SafetyError("Refused: payload file hash changed since plan creation (sha256 mismatch)")


def _load_plan_from_ctx(ctx: dict[str, Any]) -> dict[str, Any]:
    plan_in = str(ctx.get("plan_in") or "").strip()
    if not plan_in:
        raise SafetyError("Refused: this write command must be applied from a reviewed plan via --plan-in")
    plan = read_json_file(plan_in)
    if not isinstance(plan, dict):
        raise ValidationError("Plan file must be a JSON object")
    return plan


def _write_plan_if_requested(ctx: dict[str, Any], plan: dict[str, Any]) -> str | None:
    plan_out = str(ctx.get("plan_out") or "").strip()
    if not plan_out:
        return None
    return write_json_file(plan_out, plan)


def _write_receipt_if_requested(ctx: dict[str, Any], receipt: dict[str, Any]) -> str | None:
    receipt_out = str(ctx.get("receipt_out") or "").strip()
    if not receipt_out:
        return None
    return write_json_file(receipt_out, receipt)


def _validate_price_selector_match(
    price: dict[str, Any],
    *,
    price_list: str | None = None,
    article_number: str | None = None,
    from_quantity: str | None = None,
) -> None:
    payload_key = _extract_price_key_from_payload(price)
    if price_list and payload_key["price_list"] and payload_key["price_list"] != price_list:
        raise ValidationError("Price.PriceList in the JSON file must match --price-list")
    if article_number and payload_key["article_number"] and payload_key["article_number"] != article_number:
        raise ValidationError("Price.ArticleNumber in the JSON file must match --article-number")
    if from_quantity and payload_key["from_quantity"] and payload_key["from_quantity"] != from_quantity:
        raise ValidationError("Price.FromQuantity in the JSON file must match --from-quantity")


def _verify_present(*, ctx: dict[str, Any], path: str) -> dict[str, Any]:
    try:
        payload = request_json(ctx=ctx, method="GET", path=path, expect_json=True)
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "path": path, "error": str(e)}
    return {
        "ok": True,
        "path": path,
        "http_status": payload["status"],
        "data": payload["body"],
    }


def _verify_absent(*, ctx: dict[str, Any], path: str) -> dict[str, Any]:
    try:
        payload = request_json(ctx=ctx, method="GET", path=path, expect_json=True)
    except Exception as e:  # noqa: BLE001
        if "HTTP 404" in str(e):
            return {"ok": True, "path": path, "expected_http_status": 404}
        return {"ok": False, "path": path, "error": str(e)}
    if payload["status"] == 404:
        return {"ok": True, "path": path, "expected_http_status": 404}
    return {
        "ok": False,
        "path": path,
        "http_status": payload["status"],
        "data": payload["body"],
        "error": "Expected price to be absent after delete verification",
    }


def cmd_prices_create(args: Any, ctx: dict[str, Any]) -> int:
    payload_file, payload_obj, price = _load_payload_file(str(getattr(args, "json_file", "") or "").strip())
    selector = {"kind": "price", "action": "create", "path": "/prices"}
    plan = _build_plan(
        action="create",
        selector=selector,
        payload_file=payload_file,
        payload_obj=payload_obj,
        risk_level="medium",
        risk_reasons=["fortnox-write", "price-create"],
        verification_plan={"type": "read-after-write", "path_template": "/prices/{PriceList}/{ArticleNumber}/{FromQuantity}"},
        rollback_notes="No generic rollback. Recreate or delete the price explicitly if you need to revert.",
        ctx=ctx,
    )
    plan_path = _write_plan_if_requested(ctx, plan)
    if not bool(ctx.get("apply")):
        out = {"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path}
        ctx["audit"].write("prices.create.plan", {"plan_out": plan_path})
        ctx["out"].emit(out)
        return 0

    plan = _load_plan_from_ctx(ctx)
    _validate_plan_for_apply(plan, action="create", selector=selector, payload_file=payload_file, ctx=ctx)
    payload = request_json(ctx=ctx, method="POST", path="/prices", json_body=payload_obj, expect_json=True)
    resolved = _resolve_full_price_key(response_body=payload.get("body"), payload_price=price)
    verify_path = f"/prices/{resolved['price_list']}/{resolved['article_number']}/{resolved['from_quantity']}"
    verification = _verify_present(ctx=ctx, path=verify_path)
    receipt = {
        "tool": ctx.get("tool") or "fortnox-api-tool",
        "version": ctx.get("tool_version") or None,
        "applied_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "selector": selector,
        "changed": True,
        "http_status": payload["status"],
        "target_price_key": resolved,
        "verification": verification,
        "diff_applied": plan.get("proposed_changes") or [],
        "backups": [],
        "rollback_plan": None,
    }
    receipt_path = _write_receipt_if_requested(ctx, receipt)
    out = {"ok": bool(verification.get("ok")), "dry_run": False, "receipt": receipt, "receipt_out": receipt_path}
    ctx["audit"].write("prices.create.apply", {"receipt_out": receipt_path, "verified": verification.get("ok")})
    ctx["out"].emit(out)
    return 0 if bool(verification.get("ok")) else 1


def cmd_prices_update(args: Any, ctx: dict[str, Any]) -> int:
    price_list = str(getattr(args, "price_list", "") or "").strip()
    article_number = str(getattr(args, "article_number", "") or "").strip()
    payload_file, payload_obj, price = _load_payload_file(str(getattr(args, "json_file", "") or "").strip())
    _validate_price_selector_match(price, price_list=price_list, article_number=article_number)
    selector = {
        "kind": "price",
        "action": "update",
        "path": f"/prices/{price_list}/{article_number}",
        "price_list": price_list,
        "article_number": article_number,
    }
    plan = _build_plan(
        action="update",
        selector=selector,
        payload_file=payload_file,
        payload_obj=payload_obj,
        risk_level="medium",
        risk_reasons=["fortnox-write", "price-update"],
        verification_plan={"type": "read-after-write", "path": f"/prices/{price_list}/{article_number}"},
        rollback_notes="No generic rollback. Re-run update with the prior values if you need to revert.",
        ctx=ctx,
    )
    plan_path = _write_plan_if_requested(ctx, plan)
    if not bool(ctx.get("apply")):
        out = {"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path}
        ctx["audit"].write(
            "prices.update.plan",
            {"plan_out": plan_path, "price_list": price_list, "article_number": article_number},
        )
        ctx["out"].emit(out)
        return 0

    plan = _load_plan_from_ctx(ctx)
    _validate_plan_for_apply(plan, action="update", selector=selector, payload_file=payload_file, ctx=ctx)
    payload = request_json(
        ctx=ctx,
        method="PUT",
        path=f"/prices/{price_list}/{article_number}",
        json_body=payload_obj,
        expect_json=True,
    )
    verify_path = f"/prices/{price_list}/{article_number}"
    verification = _verify_present(ctx=ctx, path=verify_path)
    receipt = {
        "tool": ctx.get("tool") or "fortnox-api-tool",
        "version": ctx.get("tool_version") or None,
        "applied_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "selector": selector,
        "changed": True,
        "http_status": payload["status"],
        "target_price_key": {"price_list": price_list, "article_number": article_number},
        "verification": verification,
        "diff_applied": plan.get("proposed_changes") or [],
        "backups": [],
        "rollback_plan": None,
    }
    receipt_path = _write_receipt_if_requested(ctx, receipt)
    out = {"ok": bool(verification.get("ok")), "dry_run": False, "receipt": receipt, "receipt_out": receipt_path}
    ctx["audit"].write("prices.update.apply", {"receipt_out": receipt_path, "verified": verification.get("ok")})
    ctx["out"].emit(out)
    return 0 if bool(verification.get("ok")) else 1


def cmd_prices_update_by_from_quantity(args: Any, ctx: dict[str, Any]) -> int:
    price_list = str(getattr(args, "price_list", "") or "").strip()
    article_number = str(getattr(args, "article_number", "") or "").strip()
    from_quantity = str(getattr(args, "from_quantity", "") or "").strip()
    payload_file, payload_obj, price = _load_payload_file(str(getattr(args, "json_file", "") or "").strip())
    _validate_price_selector_match(
        price,
        price_list=price_list,
        article_number=article_number,
        from_quantity=from_quantity,
    )
    selector = {
        "kind": "price",
        "action": "update-by-from-quantity",
        "path": f"/prices/{price_list}/{article_number}/{from_quantity}",
        "price_list": price_list,
        "article_number": article_number,
        "from_quantity": from_quantity,
    }
    plan = _build_plan(
        action="update-by-from-quantity",
        selector=selector,
        payload_file=payload_file,
        payload_obj=payload_obj,
        risk_level="medium",
        risk_reasons=["fortnox-write", "price-update-by-from-quantity"],
        verification_plan={"type": "read-after-write", "path": f"/prices/{price_list}/{article_number}/{from_quantity}"},
        rollback_notes="No generic rollback. Re-run update with the prior values if you need to revert.",
        ctx=ctx,
    )
    plan_path = _write_plan_if_requested(ctx, plan)
    if not bool(ctx.get("apply")):
        out = {"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path}
        ctx["audit"].write(
            "prices.update_by_from_quantity.plan",
            {
                "plan_out": plan_path,
                "price_list": price_list,
                "article_number": article_number,
                "from_quantity": from_quantity,
            },
        )
        ctx["out"].emit(out)
        return 0

    plan = _load_plan_from_ctx(ctx)
    _validate_plan_for_apply(plan, action="update-by-from-quantity", selector=selector, payload_file=payload_file, ctx=ctx)
    payload = request_json(
        ctx=ctx,
        method="PUT",
        path=f"/prices/{price_list}/{article_number}/{from_quantity}",
        json_body=payload_obj,
        expect_json=True,
    )
    verify_path = f"/prices/{price_list}/{article_number}/{from_quantity}"
    verification = _verify_present(ctx=ctx, path=verify_path)
    receipt = {
        "tool": ctx.get("tool") or "fortnox-api-tool",
        "version": ctx.get("tool_version") or None,
        "applied_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "selector": selector,
        "changed": True,
        "http_status": payload["status"],
        "target_price_key": {
            "price_list": price_list,
            "article_number": article_number,
            "from_quantity": from_quantity,
        },
        "verification": verification,
        "diff_applied": plan.get("proposed_changes") or [],
        "backups": [],
        "rollback_plan": None,
    }
    receipt_path = _write_receipt_if_requested(ctx, receipt)
    out = {"ok": bool(verification.get("ok")), "dry_run": False, "receipt": receipt, "receipt_out": receipt_path}
    ctx["audit"].write(
        "prices.update_by_from_quantity.apply",
        {"receipt_out": receipt_path, "verified": verification.get("ok")},
    )
    ctx["out"].emit(out)
    return 0 if bool(verification.get("ok")) else 1


def cmd_prices_delete(args: Any, ctx: dict[str, Any]) -> int:
    price_list = str(getattr(args, "price_list", "") or "").strip()
    article_number = str(getattr(args, "article_number", "") or "").strip()
    from_quantity = str(getattr(args, "from_quantity", "") or "").strip()
    selector = {
        "kind": "price",
        "action": "delete",
        "path": f"/prices/{price_list}/{article_number}/{from_quantity}",
        "price_list": price_list,
        "article_number": article_number,
        "from_quantity": from_quantity,
    }
    plan = _build_plan(
        action="delete",
        selector=selector,
        payload_file=None,
        payload_obj=None,
        risk_level="irreversible",
        risk_reasons=["fortnox-write", "price-delete", "irreversible"],
        verification_plan={
            "type": "absence-check",
            "path": f"/prices/{price_list}/{article_number}/{from_quantity}",
            "expect_http_status": 404,
        },
        rollback_notes="No generic rollback. Recreate the deleted price explicitly if needed.",
        ctx=ctx,
    )
    plan_path = _write_plan_if_requested(ctx, plan)
    if not bool(ctx.get("apply")):
        out = {"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path}
        ctx["audit"].write(
            "prices.delete.plan",
            {
                "plan_out": plan_path,
                "price_list": price_list,
                "article_number": article_number,
                "from_quantity": from_quantity,
            },
        )
        ctx["out"].emit(out)
        return 0

    if not bool(ctx.get("yes")):
        raise SafetyError("Refused: deleting a price requires --apply --yes")
    if not bool(ctx.get("ack_irreversible")):
        raise SafetyError("Refused: deleting a price requires --ack-irreversible")

    plan = _load_plan_from_ctx(ctx)
    _validate_plan_for_apply(plan, action="delete", selector=selector, payload_file=None, ctx=ctx)
    payload = request_json(
        ctx=ctx,
        method="DELETE",
        path=f"/prices/{price_list}/{article_number}/{from_quantity}",
        expect_json=False,
    )
    verify_path = f"/prices/{price_list}/{article_number}/{from_quantity}"
    verification = _verify_absent(ctx=ctx, path=verify_path)
    receipt = {
        "tool": ctx.get("tool") or "fortnox-api-tool",
        "version": ctx.get("tool_version") or None,
        "applied_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "selector": selector,
        "changed": True,
        "http_status": payload["status"],
        "target_price_key": {
            "price_list": price_list,
            "article_number": article_number,
            "from_quantity": from_quantity,
        },
        "verification": verification,
        "diff_applied": plan.get("proposed_changes") or [],
        "backups": [],
        "rollback_plan": None,
    }
    receipt_path = _write_receipt_if_requested(ctx, receipt)
    out = {"ok": bool(verification.get("ok")), "dry_run": False, "receipt": receipt, "receipt_out": receipt_path}
    ctx["audit"].write("prices.delete.apply", {"receipt_out": receipt_path, "verified": verification.get("ok")})
    ctx["out"].emit(out)
    return 0 if bool(verification.get("ok")) else 1
