from __future__ import annotations

from typing import Any

from ..errors import SafetyError, ValidationError
from ..state import get_default_account_id


def _require_token(ctx) -> None:
    cfg = ctx["cfg"]
    if not cfg.token:
        raise ValidationError("Missing CLOUDFLARE_API_TOKEN")


def _resolve_account_id(args, ctx) -> str:
    account_id = str(getattr(args, "account_id", "") or "").strip()
    if account_id:
        return account_id
    default = get_default_account_id(ctx["env_file"], fingerprint=ctx.get("env_fingerprint"))
    if default:
        return default
    raise ValidationError(
        "Missing --account-id and no default is set. "
        "Run: cloudflare-api-tool accounts set-default --account-id <id>"
    )


def cmd_tunnels_list(args, ctx) -> int:
    _require_token(ctx)
    account_id = _resolve_account_id(args, ctx)
    name = str(getattr(args, "name", "") or "").strip()
    status = str(getattr(args, "status", "") or "").strip()

    res = ctx["cf"].get_json(f"/accounts/{account_id}/cfd_tunnel", cacheable=True)
    items = res.result or []
    if isinstance(items, list):
        if name:
            items = [x for x in items if isinstance(x, dict) and str(x.get("name") or "") == name]
        if status:
            items = [x for x in items if isinstance(x, dict) and str(x.get("status") or "") == status]

    ctx["out"].emit(
        {
            "ok": True,
            "command": "tunnels.list",
            "account_id": account_id,
            "filters": {"name": name or None, "status": status or None},
            "count": len(items) if isinstance(items, list) else None,
            "result": items,
            "result_info": res.result_info,
        }
    )
    return 0


def cmd_tunnels_resolve(args, ctx) -> int:
    _require_token(ctx)
    account_id = _resolve_account_id(args, ctx)
    name = str(getattr(args, "name", "") or "").strip()
    if not name:
        raise ValidationError("Missing --name")

    res = ctx["cf"].get_json(f"/accounts/{account_id}/cfd_tunnel", cacheable=True)
    items = res.result or []
    matches: list[dict[str, Any]] = []
    if isinstance(items, list):
        for x in items:
            if not isinstance(x, dict):
                continue
            if str(x.get("name") or "") == name:
                matches.append(x)

    if len(matches) == 1:
        tunnel_id = str(matches[0].get("id") or "").strip() or None
        if not tunnel_id:
            raise SafetyError("Refusing: resolved tunnel is missing an id in the API response.")
        ctx["out"].emit(
            {
                "ok": True,
                "command": "tunnels.resolve",
                "account_id": account_id,
                "name": name,
                "tunnel_id": tunnel_id,
                "result": matches[0],
            }
        )
        return 0

    if not matches:
        raise SafetyError(f"Refusing: no tunnels matched name={name!r}. Use `tunnels list` to inspect available tunnels.")
    raise SafetyError(
        f"Refusing: multiple tunnels matched name={name!r} (count={len(matches)}). "
        "Use `tunnels list` to disambiguate."
    )


def cmd_tunnels_config_get(args, ctx) -> int:
    _require_token(ctx)
    account_id = _resolve_account_id(args, ctx)
    tunnel_id = str(getattr(args, "tunnel_id", "") or "").strip()
    if not tunnel_id:
        raise ValidationError("Missing --tunnel-id")

    res = ctx["cf"].get_json(f"/accounts/{account_id}/cfd_tunnel/{tunnel_id}/configurations", cacheable=True)
    ctx["out"].emit(
        {
            "ok": True,
            "command": "tunnels.config.get",
            "account_id": account_id,
            "tunnel_id": tunnel_id,
            "result": res.result,
            "result_info": res.result_info,
        }
    )
    return 0

