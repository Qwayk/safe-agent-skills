from __future__ import annotations

from typing import Any

from ..authz import resolve_auth_mode
from ..errors import ValidationError
from ..http import HttpClient


COMMAND_FAMILY = "multilingual-machine-translation-credit-data"
BASE_PATH = "/translation-credits/v1/credit"


def _resolve_auth(*, ctx: dict[str, Any]) -> tuple[dict[str, str], str]:
    auth = resolve_auth_mode(
        cfg=ctx["cfg"],
        env_file=str(ctx["env_file"]),
        verbose=bool(ctx.get("verbose")),
        command_family=COMMAND_FAMILY,
    )
    return auth["headers"], auth["mode"]


def _request_json(
    *,
    method: str,
    base_url: str,
    path: str,
    headers: dict[str, str],
    json_body: dict[str, Any] | None,
    timeout_s: float,
    verbose: bool,
) -> dict[str, Any]:
    request_headers = dict(headers)
    if json_body is not None:
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


def _emit_success(
    *,
    method: str,
    auth_mode: str,
    request: dict[str, Any],
    response: dict[str, Any],
    ctx: dict[str, Any],
) -> None:
    payload = {
        "ok": True,
        "method": method,
        "auth_mode": auth_mode,
        "request": request,
        "response": response,
    }
    ctx["audit"].write(method, payload)
    ctx["out"].emit(payload)


def _word_count(raw: Any) -> int:
    if raw is None:
        raise ValidationError("Missing --word-count")
    try:
        value = int(raw)
    except (TypeError, ValueError) as exc:
        raise ValidationError("--word-count must be an integer") from exc
    if value < 0:
        raise ValidationError("--word-count must be at least 0")
    return value


def _emit_error(ctx: dict[str, Any], *, method: str, exc: Exception) -> int:
    ctx["out"].emit({"ok": False, "method": method, "error": str(exc), "error_type": exc.__class__.__name__})
    return 1


def cmd_multilingual_machine_translation_credit_data_get(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.get"
    try:
        _ = args
        headers, auth_mode = _resolve_auth(ctx=ctx)
        request = {"method": "GET", "path": BASE_PATH}
        response = _request_json(
            method="GET",
            base_url=ctx["cfg"].base_url,
            path=BASE_PATH,
            headers=headers,
            json_body=None,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        _emit_success(method=method, auth_mode=auth_mode, request=request, response=response, ctx=ctx)
        return 0
    except (ValidationError, RuntimeError) as exc:
        return _emit_error(ctx, method=method, exc=exc)


def cmd_multilingual_machine_translation_credit_data_check_sufficient(args, ctx) -> int:
    method = f"{COMMAND_FAMILY}.check-sufficient"
    try:
        word_count = _word_count(getattr(args, "word_count", None))
        headers, auth_mode = _resolve_auth(ctx=ctx)
        body = {"wordCount": word_count}
        path = f"{BASE_PATH}/is-eligible"
        request = {"method": "POST", "path": path, "body": body}
        response = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path=path,
            headers=headers,
            json_body=body,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        _emit_success(method=method, auth_mode=auth_mode, request=request, response=response, ctx=ctx)
        return 0
    except (ValidationError, RuntimeError) as exc:
        return _emit_error(ctx, method=method, exc=exc)
