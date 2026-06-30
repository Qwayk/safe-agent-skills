from __future__ import annotations

from typing import Any

from ..authz import resolve_auth_mode
from ..errors import ValidationError
from ..http import HttpClient


def _coerce_required_dns_propagation_id(raw: Any) -> str:
    if raw is None:
        raise ValidationError("Missing --dns-propagation-id")
    if not isinstance(raw, str):
        raise ValidationError("--dns-propagation-id must be a string")
    value = raw.strip()
    if not value:
        raise ValidationError("Missing --dns-propagation-id")
    if "." not in value:
        raise ValidationError("--dns-propagation-id must include a TLD (for example, example.com)")
    if value.startswith(".") or value.endswith("."):
        raise ValidationError("--dns-propagation-id must not start or end with a dot")
    return value


def _request_json(
    *,
    method: str,
    base_url: str,
    path: str,
    headers: dict[str, str],
    timeout_s: float,
    verbose: bool,
) -> dict[str, Any]:
    client = HttpClient(timeout_s=timeout_s, verbose=verbose, user_agent="wix-safe-agent-cli")
    response = client.request(
        method=method,
        url=base_url.rstrip("/") + "/" + path.lstrip("/"),
        headers=dict(headers),
        params=None,
        json_body=None,
    )
    payload = response.json()
    if not isinstance(payload, dict):
        raise ValidationError("Wix API returned a non-object JSON response")
    return payload


def cmd_dns_propagation_get(args, ctx) -> int:
    try:
        dns_propagation_id = _coerce_required_dns_propagation_id(getattr(args, "dns_propagation_id", None))
        auth = resolve_auth_mode(
            cfg=ctx["cfg"],
            env_file=str(ctx["env_file"]),
            verbose=bool(ctx.get("verbose")),
            command_family="dns-propagation",
        )
        request_path = f"/premium/domains/v1/dns-propagations/{dns_propagation_id}"
        payload = _request_json(
            method="GET",
            base_url=ctx["cfg"].base_url,
            path=request_path,
            headers=auth["headers"],
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        propagation = payload.get("dnsPropagation")
        if not isinstance(propagation, dict):
            raise ValidationError("dns-propagation.get response did not include a dnsPropagation object")
        out = {
            "ok": True,
            "method": "dns-propagation.get",
            "auth_mode": auth["mode"],
            "request": {"method": "GET", "path": request_path},
            "response": payload,
            "dnsPropagation": propagation,
        }
        ctx["audit"].write("dns-propagation.get", out)
        ctx["out"].emit(out)
        return 0
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError"})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__})
        return 1
