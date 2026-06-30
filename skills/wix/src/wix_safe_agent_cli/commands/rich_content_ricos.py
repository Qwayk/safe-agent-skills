from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ..authz import resolve_auth_mode
from ..errors import SafetyError, ValidationError
from ..http import HttpClient


COMMAND_FAMILY = "rich-content-ricos"
CONVERT_FROM_RICOS_PATH = "/ricos/v1/ricos-document/convert/from-ricos"
CONVERT_TO_RICOS_PATH = "/ricos/v1/ricos-document/convert/to-ricos"
VALIDATE_PATH = "/ricos/v1/ricos-document/validate"


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


def _resolve_auth(ctx: dict[str, Any]) -> dict[str, Any]:
    return resolve_auth_mode(
        cfg=ctx["cfg"],
        env_file=str(ctx["env_file"]),
        verbose=bool(ctx.get("verbose")),
        command_family=COMMAND_FAMILY,
    )


def _request_json(*, path: str, headers: dict[str, str], body: dict[str, Any], ctx: dict[str, Any]) -> dict[str, Any]:
    request_headers = dict(headers)
    request_headers["Content-Type"] = "application/json"
    client = HttpClient(timeout_s=float(ctx["cfg"].timeout_s), verbose=bool(ctx.get("verbose")), user_agent="wix-safe-agent-cli")
    response = client.request(
        method="POST",
        url=ctx["cfg"].base_url.rstrip("/") + "/" + path.lstrip("/"),
        headers=request_headers,
        params=None,
        json_body=body,
    )
    payload = response.json()
    if not isinstance(payload, dict):
        raise ValidationError("Wix API returned a non-object JSON response")
    return payload


def _emit_error(ctx: dict[str, Any], *, method: str, exc: Exception) -> int:
    if isinstance(exc, SafetyError):
        ctx["out"].emit({"ok": True, "dry_run": False, "refused": True, "reasons": [str(exc)], "refusal_type": "SafetyError", "method": method})
        return 0
    if isinstance(exc, ValidationError):
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError", "method": method})
        return 1
    ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__, "method": method})
    return 1


def _emit_helper(*, args: Any, ctx: dict[str, Any], method: str, path: str, field: str) -> int:
    try:
        body = _read_json_arg(getattr(args, field.replace("-", "_"), None), field=field)
        auth = _resolve_auth(ctx)
        response = _request_json(path=path, headers=auth["headers"], body=body, ctx=ctx)
        out = {
            "ok": True,
            "method": method,
            "auth_mode": auth["mode"],
            "request": {"method": "POST", "path": path, "body": body},
            "response": response,
        }
        ctx["audit"].write(method, out)
        ctx["out"].emit(out)
        return 0
    except Exception as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_rich_content_ricos_convert_from(args, ctx) -> int:
    return _emit_helper(
        args=args,
        ctx=ctx,
        method=f"{COMMAND_FAMILY}.convert-from",
        path=CONVERT_FROM_RICOS_PATH,
        field="convert-json",
    )


def cmd_rich_content_ricos_convert_to(args, ctx) -> int:
    return _emit_helper(
        args=args,
        ctx=ctx,
        method=f"{COMMAND_FAMILY}.convert-to",
        path=CONVERT_TO_RICOS_PATH,
        field="convert-json",
    )


def cmd_rich_content_ricos_validate(args, ctx) -> int:
    return _emit_helper(
        args=args,
        ctx=ctx,
        method=f"{COMMAND_FAMILY}.validate",
        path=VALIDATE_PATH,
        field="validate-json",
    )
