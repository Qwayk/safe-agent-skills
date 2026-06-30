from __future__ import annotations

from typing import Any

from ..authz import resolve_auth_mode
from ..errors import ValidationError
from ..http import HttpClient


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
    client = HttpClient(timeout_s=timeout_s, verbose=verbose, user_agent="wix-safe-agent-cli")
    response = client.request(
        method=method,
        url=base_url.rstrip("/") + "/" + path.lstrip("/"),
        headers=dict(headers),
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
    out = {
        "ok": True,
        "method": method,
        "auth_mode": auth_mode,
        "request": request,
        "response": response,
    }
    ctx["audit"].write(method, out)
    ctx["out"].emit(out)


def cmd_ai_credits_get_balance(args, ctx) -> int:
    try:
        _ = args
        auth = resolve_auth_mode(
            cfg=ctx["cfg"],
            env_file=str(ctx["env_file"]),
            verbose=bool(ctx.get("verbose")),
            command_family="ai-credits",
        )

        request_path = "/appmarket/credittransactions/v1/credit-transactions/balance"
        payload = _request_json(
            method="POST",
            base_url=ctx["cfg"].base_url,
            path=request_path,
            headers=auth["headers"],
            json_body={},
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        _emit_success(
            method="ai-credits.get-balance",
            auth_mode=auth["mode"],
            request={"method": "POST", "path": request_path, "body": {}},
            response=payload,
            ctx=ctx,
        )
        return 0
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError"})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__})
        return 1
