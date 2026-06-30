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


def _read_json_arg(raw: Any, field: str) -> Any:
    if raw is None:
        return None
    if not isinstance(raw, str):
        raise ValidationError(f"--{field} must be a JSON string, JSON file path, or omitted")
    text = raw.strip()
    if not text:
        raise ValidationError(f"--{field} cannot be empty")
    if text.startswith("@"):
        path = Path(text[1:])
        if not path.exists():
            raise ValidationError(f"--{field} file not found: {path}")
        text = path.read_text(encoding="utf-8").strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValidationError(f"Invalid JSON for --{field}: {exc.msg}") from exc


def _required_text(raw: Any, *, field: str) -> str:
    if raw is None:
        raise ValidationError(f"Missing --{field}")
    if not isinstance(raw, str):
        raise ValidationError(f"--{field} must be a string")
    value = raw.strip()
    if not value:
        raise ValidationError(f"--{field} cannot be empty")
    return value


def _object_arg(raw: Any, *, field: str) -> dict[str, Any]:
    value = _read_json_arg(raw, field)
    if not isinstance(value, dict):
        raise ValidationError(f"--{field} must be a JSON object")
    if not value:
        raise ValidationError(f"--{field} cannot be empty")
    return value


def _array_arg(raw: Any, *, field: str, max_items: int = 1000) -> list[Any]:
    value = _read_json_arg(raw, field)
    if not isinstance(value, list):
        raise ValidationError(f"--{field} must be a JSON array")
    if not value:
        raise ValidationError(f"--{field} cannot be empty")
    if len(value) > max_items:
        raise ValidationError(f"--{field} supports at most {max_items} items")
    return value


def _validate_languages(source_language: str, target_language: str) -> None:
    if source_language.upper() == target_language.upper():
        raise ValidationError("--source-language and --target-language must be different")


def _validate_translatable_content(content: dict[str, Any], *, field: str) -> None:
    content_id = str(content.get("id") or "").strip()
    if not content_id:
        raise ValidationError(f"--{field} items must include id")
    format_value = str(content.get("format") or "").strip()
    if not format_value:
        raise ValidationError(f"--{field} items must include format")
    if not any(key in content for key in ("plainTextContent", "htmlContent", "richContent")):
        raise ValidationError(f"--{field} items must include plainTextContent, htmlContent, or richContent")


def _resolve_auth(*, ctx: dict[str, Any]) -> tuple[dict[str, str], str]:
    auth = resolve_auth_mode(
        cfg=ctx["cfg"],
        env_file=str(ctx["env_file"]),
        verbose=bool(ctx.get("verbose")),
        command_family="multilingual-machine-translation",
    )
    return auth["headers"], auth["mode"]


def _request_json(
    *,
    method: str,
    base_url: str,
    path: str,
    headers: dict[str, str],
    json_body: dict[str, Any],
    timeout_s: float,
    verbose: bool,
) -> dict[str, Any]:
    request_headers = dict(headers)
    request_headers["Content-Type"] = "application/json"
    client = HttpClient(timeout_s=timeout_s, verbose=verbose, user_agent="wix-safe-agent-cli")
    response = client.request(
        method=method,
        url=base_url.rstrip("/") + "/" + path.lstrip("/"),
        headers=request_headers,
        params=None,
        json_body=json_body,
    )
    payload = response.json()
    if not isinstance(payload, dict):
        raise ValidationError("Wix API returned a non-object JSON response")
    return payload


def _build_plan(*, method: str, request: dict[str, Any], selector: dict[str, Any], ctx: dict[str, Any], item_count: int) -> dict[str, Any]:
    return {
        "tool": ctx.get("tool") or "wix-safe-agent-cli",
        "version": ctx.get("tool_version") or None,
        "generated_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "method": method,
        "risk_level": "critical",
        "risk_reasons": ["machine-translation", "translation-credit-spend", "external-translation-service"],
        "preconditions": [
            "env_fingerprint must match",
            "selector must match",
            "apply requires --apply and --yes",
            "apply requires --ack-irreversible because successful translation consumes word credits",
        ],
        "selector": selector,
        "request": request,
        "baseline": {"env_fingerprint": ctx["cfg"].base_url, "selector": selector},
        "proposed_changes": [{"operation": selector.get("operation"), "item_count": item_count, "source_language": selector.get("source_language"), "target_language": selector.get("target_language")}],
        "verification_plan": {
            "type": "provider-response",
            "notes": "Verify translatedContent/results in the provider response. For credit planning, run the Credit Data commands before and after translation.",
        },
        "rollback": {"supported": False, "notes": "Successful machine translation consumes credits and cannot be undone by this CLI."},
    }


def _load_plan(*, plan_in: str | None, expected_method: str, expected_selector: dict[str, Any], ctx: dict[str, Any]) -> dict[str, Any]:
    if not plan_in:
        raise ValidationError("Missing --plan-in")
    plan = read_json_file(plan_in)
    if not isinstance(plan, dict):
        raise ValidationError("Plan file must be a JSON object")
    if plan.get("method") != expected_method:
        raise SafetyError("Refused: plan method does not match current command")
    baseline = plan.get("baseline")
    if not isinstance(baseline, dict):
        raise SafetyError("Refused: plan missing baseline")
    if str(baseline.get("env_fingerprint") or "") != str(ctx["cfg"].base_url):
        raise SafetyError("Refused: plan env_fingerprint does not match current environment")
    if baseline.get("selector") != expected_selector:
        raise SafetyError("Refused: plan selector does not match current command")
    return plan


def _plan_out_if_needed(ctx: dict[str, Any], *, plan: dict[str, Any]) -> str | None:
    plan_out = ctx.get("plan_out")
    if plan_out and not bool(ctx.get("apply")):
        return write_json_file(plan_out, plan)
    return None


def _receipt_out_if_needed(ctx: dict[str, Any], *, receipt: dict[str, Any]) -> str | None:
    receipt_out = ctx.get("receipt_out")
    if receipt_out:
        return write_json_file(receipt_out, receipt)
    return None


def _build_receipt(*, method: str, request: dict[str, Any], response: dict[str, Any], selector: dict[str, Any], plan: dict[str, Any], ctx: dict[str, Any]) -> dict[str, Any]:
    verification = {"ok": True, "type": "provider-response", "notes": "Provider returned an object response.", "response": response}
    return {
        "tool": ctx.get("tool") or "wix-safe-agent-cli",
        "version": ctx.get("tool_version") or None,
        "applied_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "method": method,
        "selector": selector,
        "request": request,
        "response": response,
        "changed": True,
        "verification": verification,
        "diff_applied": plan.get("proposed_changes") or [],
        "backups": [],
        "rollback_plan": None,
    }


def _write_command(*, method: str, request: dict[str, Any], selector: dict[str, Any], ctx: dict[str, Any], item_count: int) -> int:
    auth_headers, auth_mode = _resolve_auth(ctx=ctx)
    plan_in = ctx.get("plan_in")
    if plan_in:
        plan = _load_plan(plan_in=str(plan_in), expected_method=method, expected_selector=selector, ctx=ctx)
    else:
        plan = _build_plan(method=method, request=request, selector=selector, ctx=ctx, item_count=item_count)
    if not reviewed_plan_apply_requested(ctx, requires_ack=True, command_label="multilingual-machine-translation"):
        ctx["out"].emit({"ok": True, "dry_run": True, "method": method, "auth_mode": auth_mode, "plan": plan, "plan_out": _plan_out_if_needed(ctx, plan=plan)})
        return 0
    loaded_plan = _load_plan(plan_in=str(plan_in), expected_method=method, expected_selector=selector, ctx=ctx) if plan_in else plan
    response = _request_json(method=request["method"], base_url=ctx["cfg"].base_url, path=request["path"], headers=auth_headers, json_body=request["body"], timeout_s=float(ctx["cfg"].timeout_s), verbose=bool(ctx.get("verbose")))
    receipt = _build_receipt(method=method, request=request, response=response, selector=selector, plan=loaded_plan, ctx=ctx)
    ctx["out"].emit({"ok": True, "dry_run": False, "method": method, "auth_mode": auth_mode, "receipt": receipt, "receipt_out": _receipt_out_if_needed(ctx, receipt=receipt)})
    return 0


def cmd_multilingual_machine_translation_translate(args, ctx) -> int:
    try:
        source_language = _required_text(getattr(args, "source_language", None), field="source-language")
        target_language = _required_text(getattr(args, "target_language", None), field="target-language")
        _validate_languages(source_language, target_language)
        content = _object_arg(getattr(args, "content_json", None), field="content-json")
        _validate_translatable_content(content, field="content-json")
        body = {"sourceLanguage": source_language, "targetLanguage": target_language, "contentToTranslate": content}
        request = {"method": "POST", "path": "/machine-translation/v3/machine-translate", "body": body}
        selector = {"kind": "wix-multilingual-machine-translation", "operation": "translate", "source_language": source_language, "target_language": target_language, "content_id": content["id"]}
        return _write_command(method="multilingual-machine-translation.translate", request=request, selector=selector, ctx=ctx, item_count=1)
    except SafetyError as exc:
        ctx["out"].emit({"ok": True, "dry_run": False, "refused": True, "reasons": [str(exc)], "refusal_type": "SafetyError", "method": "multilingual-machine-translation.translate"})
        return 0
    except (ValidationError, RuntimeError) as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "multilingual-machine-translation.translate"})
        return 1


def cmd_multilingual_machine_translation_bulk_translate(args, ctx) -> int:
    try:
        source_language = _required_text(getattr(args, "source_language", None), field="source-language")
        target_language = _required_text(getattr(args, "target_language", None), field="target-language")
        _validate_languages(source_language, target_language)
        contents = _array_arg(getattr(args, "contents_json", None), field="contents-json", max_items=1000)
        for item in contents:
            if not isinstance(item, dict):
                raise ValidationError("--contents-json items must be objects")
            _validate_translatable_content(item, field="contents-json")
        body = {"sourceLanguage": source_language, "targetLanguage": target_language, "contentToTranslate": contents}
        request = {"method": "POST", "path": "/machine-translation/v3/bulk-machine-translate", "body": body}
        selector = {"kind": "wix-multilingual-machine-translation", "operation": "bulk-translate", "source_language": source_language, "target_language": target_language, "count": len(contents)}
        return _write_command(method="multilingual-machine-translation.bulk-translate", request=request, selector=selector, ctx=ctx, item_count=len(contents))
    except SafetyError as exc:
        ctx["out"].emit({"ok": True, "dry_run": False, "refused": True, "reasons": [str(exc)], "refusal_type": "SafetyError", "method": "multilingual-machine-translation.bulk-translate"})
        return 0
    except (ValidationError, RuntimeError) as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": "multilingual-machine-translation.bulk-translate"})
        return 1
