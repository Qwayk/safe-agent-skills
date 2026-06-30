from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ..authz import resolve_auth_mode
from ..errors import ValidationError
from ..http import HttpClient


def _read_json_arg(raw: Any, *, field: str) -> Any:
    if raw is None:
        return None
    if not isinstance(raw, str):
        raise ValidationError(f"--{field} must be a JSON string or @file path")

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


def _coerce_custom_params(raw: Any) -> dict[str, str] | None:
    if raw is None:
        return None
    value = _read_json_arg(raw, field="custom-params-json")
    if not isinstance(value, dict):
        raise ValidationError("--custom-params-json must be a JSON object")
    result: dict[str, str] = {}
    for key, item in value.items():
        if not isinstance(key, str) or not key.strip():
            raise ValidationError("--custom-params-json keys must be non-empty strings")
        if not isinstance(item, str):
            raise ValidationError("--custom-params-json values must be strings")
        result[key] = item
    return result


def _request_json(
    *,
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
        method="POST",
        url=base_url.rstrip("/") + "/" + path.lstrip("/"),
        headers=request_headers,
        params=None,
        json_body=json_body,
    )
    payload = response.json()
    if not isinstance(payload, dict):
        raise ValidationError("Wix API returned a non-object JSON response")
    return payload


def cmd_editor_deep_link_create(args, ctx) -> int:
    try:
        custom_params = _coerce_custom_params(getattr(args, "custom_params_json", None))

        auth = resolve_auth_mode(
            cfg=ctx["cfg"],
            env_file=str(ctx["env_file"]),
            verbose=bool(ctx.get("verbose")),
            command_family="editor-deep-link",
        )
        body: dict[str, Any] = {}
        if custom_params is not None:
            body["customParams"] = custom_params
        request_path = "/apps/v1/post-installation/editor-deep-link"
        payload = _request_json(
            base_url=ctx["cfg"].base_url,
            path=request_path,
            headers=auth["headers"],
            json_body=body,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        out = {
            "ok": True,
            "method": "editor-deep-link.create",
            "auth_mode": auth["mode"],
            "request": {
                "method": "POST",
                "path": request_path,
                "body": body,
            },
            "response": payload,
        }
        ctx["audit"].write("editor-deep-link.create", out)
        ctx["out"].emit(out)
        return 0
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError"})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__})
        return 1
