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
    timeout_s: float,
    verbose: bool,
) -> dict[str, Any]:
    request_headers = dict(headers)
    if method.upper() != "GET":
        request_headers["Content-Type"] = "application/json"

    client = HttpClient(timeout_s=timeout_s, verbose=verbose, user_agent="wix-safe-agent-cli")
    response = client.request(
        method=method,
        url=base_url.rstrip("/") + "/" + path.lstrip("/"),
        headers=request_headers,
        params=None,
        json_body=None,
    )
    payload = response.json()
    if not isinstance(payload, dict):
        raise ValidationError("Wix API returned a non-object JSON response")
    return payload


def cmd_site_plugins_get_placement_status(args, ctx) -> int:
    try:
        _ = args
        auth = resolve_auth_mode(
            cfg=ctx["cfg"],
            env_file=str(ctx["env_file"]),
            verbose=bool(ctx.get("verbose")),
            command_family="site-plugins",
        )
        payload = _request_json(
            method="GET",
            base_url=ctx["cfg"].base_url,
            path="/app-plugins/v1/site-plugins/placement-status",
            headers=auth["headers"],
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        out = {
            "ok": True,
            "method": "site-plugins.get-placement-status",
            "auth_mode": auth["mode"],
            "request": {
                "method": "GET",
                "path": "/app-plugins/v1/site-plugins/placement-status",
            },
            "response": payload,
        }
        ctx["audit"].write("site-plugins.get-placement-status", out)
        ctx["out"].emit(out)
        return 0
    except ValidationError as exc:
        out = {"ok": False, "error": str(exc), "error_type": "ValidationError"}
        ctx["out"].emit(out)
        return 1
    except RuntimeError as exc:
        out = {"ok": False, "error": str(exc), "error_type": exc.__class__.__name__}
        ctx["out"].emit(out)
        return 1
