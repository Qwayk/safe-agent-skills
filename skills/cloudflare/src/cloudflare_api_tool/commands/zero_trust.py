from __future__ import annotations

from typing import Any

from ..errors import ValidationError
from ..state import get_default_account_id


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


def _require_token(ctx) -> None:
    cfg = ctx["cfg"]
    if not cfg.token:
        raise ValidationError("Missing CLOUDFLARE_API_TOKEN")


def cmd_zero_trust_org_get(args, ctx) -> int:
    _require_token(ctx)
    account_id = _resolve_account_id(args, ctx)
    res = ctx["cf"].get_json(f"/accounts/{account_id}/access/organizations")
    ctx["out"].emit({"ok": True, "command": "zero_trust.org.get", "account_id": account_id, "result": res.result})
    return 0


def cmd_zero_trust_gateway_account_get(args, ctx) -> int:
    _require_token(ctx)
    account_id = _resolve_account_id(args, ctx)
    res = ctx["cf"].get_json(f"/accounts/{account_id}/gateway")
    ctx["out"].emit({"ok": True, "command": "zero_trust.gateway.account.get", "account_id": account_id, "result": res.result})
    return 0


def cmd_zero_trust_gateway_configuration_get(args, ctx) -> int:
    _require_token(ctx)
    account_id = _resolve_account_id(args, ctx)
    res = ctx["cf"].get_json(f"/accounts/{account_id}/gateway/configuration")
    ctx["out"].emit(
        {"ok": True, "command": "zero_trust.gateway.configuration.get", "account_id": account_id, "result": res.result}
    )
    return 0


def cmd_zero_trust_gateway_logging_get(args, ctx) -> int:
    _require_token(ctx)
    account_id = _resolve_account_id(args, ctx)
    res = ctx["cf"].get_json(f"/accounts/{account_id}/gateway/logging")
    ctx["out"].emit({"ok": True, "command": "zero_trust.gateway.logging.get", "account_id": account_id, "result": res.result})
    return 0


def cmd_zero_trust_gateway_rules_list(args, ctx) -> int:
    _require_token(ctx)
    account_id = _resolve_account_id(args, ctx)
    res = ctx["cf"].get_json(f"/accounts/{account_id}/gateway/rules")
    items = res.result or []
    ctx["out"].emit(
        {
            "ok": True,
            "command": "zero_trust.gateway.rules.list",
            "account_id": account_id,
            "count": len(items) if isinstance(items, list) else None,
            "result": items,
            "result_info": res.result_info,
        }
    )
    return 0


def cmd_zero_trust_gateway_rules_get(args, ctx) -> int:
    _require_token(ctx)
    account_id = _resolve_account_id(args, ctx)
    rule_id = str(getattr(args, "rule_id", "") or "").strip()
    if not rule_id:
        raise ValidationError("Missing --rule-id")
    res = ctx["cf"].get_json(f"/accounts/{account_id}/gateway/rules/{rule_id}")
    ctx["out"].emit(
        {"ok": True, "command": "zero_trust.gateway.rules.get", "account_id": account_id, "rule_id": rule_id, "result": res.result}
    )
    return 0


def cmd_zero_trust_gateway_lists_list(args, ctx) -> int:
    _require_token(ctx)
    account_id = _resolve_account_id(args, ctx)
    res = ctx["cf"].get_json(f"/accounts/{account_id}/gateway/lists")
    items = res.result or []
    ctx["out"].emit(
        {
            "ok": True,
            "command": "zero_trust.gateway.lists.list",
            "account_id": account_id,
            "count": len(items) if isinstance(items, list) else None,
            "result": items,
            "result_info": res.result_info,
        }
    )
    return 0


def cmd_zero_trust_gateway_lists_get(args, ctx) -> int:
    _require_token(ctx)
    account_id = _resolve_account_id(args, ctx)
    list_id = str(getattr(args, "list_id", "") or "").strip()
    if not list_id:
        raise ValidationError("Missing --list-id")
    res = ctx["cf"].get_json(f"/accounts/{account_id}/gateway/lists/{list_id}")
    ctx["out"].emit(
        {"ok": True, "command": "zero_trust.gateway.lists.get", "account_id": account_id, "list_id": list_id, "result": res.result}
    )
    return 0


def cmd_zero_trust_gateway_lists_items_list(args, ctx) -> int:
    _require_token(ctx)
    account_id = _resolve_account_id(args, ctx)
    list_id = str(getattr(args, "list_id", "") or "").strip()
    if not list_id:
        raise ValidationError("Missing --list-id")
    res = ctx["cf"].get_json(f"/accounts/{account_id}/gateway/lists/{list_id}/items")
    items = res.result or []
    ctx["out"].emit(
        {
            "ok": True,
            "command": "zero_trust.gateway.lists.items.list",
            "account_id": account_id,
            "list_id": list_id,
            "count": len(items) if isinstance(items, list) else None,
            "result": items,
            "result_info": res.result_info,
        }
    )
    return 0


def cmd_zero_trust_devices_list(args, ctx) -> int:
    _require_token(ctx)
    account_id = _resolve_account_id(args, ctx)
    res = ctx["cf"].get_json(f"/accounts/{account_id}/devices")
    items = res.result or []
    ctx["out"].emit(
        {
            "ok": True,
            "command": "zero_trust.devices.list",
            "account_id": account_id,
            "count": len(items) if isinstance(items, list) else None,
            "result": items,
            "result_info": res.result_info,
        }
    )
    return 0


def cmd_zero_trust_devices_get(args, ctx) -> int:
    _require_token(ctx)
    account_id = _resolve_account_id(args, ctx)
    device_id = str(getattr(args, "device_id", "") or "").strip()
    if not device_id:
        raise ValidationError("Missing --device-id")
    res = ctx["cf"].get_json(f"/accounts/{account_id}/devices/{device_id}")
    ctx["out"].emit(
        {"ok": True, "command": "zero_trust.devices.get", "account_id": account_id, "device_id": device_id, "result": res.result}
    )
    return 0


def cmd_zero_trust_access_apps_list(args, ctx) -> int:
    _require_token(ctx)
    account_id = _resolve_account_id(args, ctx)
    params: dict[str, Any] = {}
    for key in ["name", "domain", "aud", "target_attributes", "search"]:
        v = str(getattr(args, key, "") or "").strip()
        if v:
            params[key] = v
    exact = getattr(args, "exact", None)
    if exact is True:
        params["exact"] = True
    # Safe short-TTL cache: app inventory objects do not contain secret-bearing values.
    res = ctx["cf"].get_json(f"/accounts/{account_id}/access/apps", params=params or None, cacheable=True)
    items = res.result or []
    ctx["out"].emit(
        {
            "ok": True,
            "command": "zero_trust.access.apps.list",
            "account_id": account_id,
            "count": len(items) if isinstance(items, list) else None,
            "result": items,
            "result_info": res.result_info,
        }
    )
    return 0


def cmd_zero_trust_access_apps_get(args, ctx) -> int:
    _require_token(ctx)
    account_id = _resolve_account_id(args, ctx)
    app_id = str(getattr(args, "app_id", "") or "").strip()
    if not app_id:
        raise ValidationError("Missing --app-id")
    res = ctx["cf"].get_json(f"/accounts/{account_id}/access/apps/{app_id}")
    ctx["out"].emit(
        {"ok": True, "command": "zero_trust.access.apps.get", "account_id": account_id, "app_id": app_id, "result": res.result}
    )
    return 0


def cmd_zero_trust_access_apps_resolve(args, ctx) -> int:
    """
    Resolve one Access application by exact name or domain.

    This is a convenience helper for scripting and avoids copying IDs by hand.
    """
    _require_token(ctx)
    account_id = _resolve_account_id(args, ctx)
    name = str(getattr(args, "name", "") or "").strip()
    domain = str(getattr(args, "domain", "") or "").strip()
    aud = str(getattr(args, "aud", "") or "").strip()
    if not (name or domain or aud):
        raise ValidationError("Missing selector: provide at least one of --name, --domain, or --aud")

    params: dict[str, Any] = {}
    if name:
        params["name"] = name
    if domain:
        params["domain"] = domain
    if aud:
        params["aud"] = aud
    if bool(getattr(args, "exact", False)):
        params["exact"] = True

    res = ctx["cf"].get_json(f"/accounts/{account_id}/access/apps", params=params or None, cacheable=True)
    items = res.result or []
    if not isinstance(items, list):
        raise ValidationError("Unexpected response shape for Access apps resolve")

    if len(items) == 0:
        ctx["out"].emit(
            {
                "ok": False,
                "command": "zero_trust.access.apps.resolve",
                "error_type": "NotFound",
                "error": "No Access apps matched the selector.",
                "selector": {"name": name or None, "domain": domain or None, "aud": aud or None, "exact": bool(getattr(args, 'exact', False))},
            }
        )
        return 1

    if len(items) > 1:
        shortlist = []
        for x in items[:10]:
            if not isinstance(x, dict):
                continue
            shortlist.append({"id": x.get("id"), "name": x.get("name"), "domain": x.get("domain"), "aud": x.get("aud")})
        ctx["out"].emit(
            {
                "ok": False,
                "command": "zero_trust.access.apps.resolve",
                "error_type": "Ambiguous",
                "error": "Multiple Access apps matched the selector.",
                "selector": {"name": name or None, "domain": domain or None, "aud": aud or None, "exact": bool(getattr(args, 'exact', False))},
                "match_count": len(items),
                "matches": shortlist,
            }
        )
        return 1

    app = items[0]
    if not isinstance(app, dict):
        raise ValidationError("Unexpected response shape for Access apps resolve")
    app_id = str(app.get("id") or "").strip()
    if not app_id:
        raise ValidationError("Resolved Access app is missing an id in the API response")
    ctx["out"].emit(
        {
            "ok": True,
            "command": "zero_trust.access.apps.resolve",
            "account_id": account_id,
            "selector": {"name": name or None, "domain": domain or None, "aud": aud or None, "exact": bool(getattr(args, 'exact', False))},
            "app": {"id": app_id, "name": app.get("name"), "domain": app.get("domain"), "aud": app.get("aud")},
            "result": app,
        }
    )
    return 0


def cmd_zero_trust_access_policies_list(args, ctx) -> int:
    _require_token(ctx)
    account_id = _resolve_account_id(args, ctx)
    app_id = str(getattr(args, "app_id", "") or "").strip()
    if not app_id:
        raise ValidationError("Missing --app-id")
    res = ctx["cf"].get_json(f"/accounts/{account_id}/access/apps/{app_id}/policies")
    items = res.result or []
    ctx["out"].emit(
        {
            "ok": True,
            "command": "zero_trust.access.policies.list",
            "account_id": account_id,
            "app_id": app_id,
            "count": len(items) if isinstance(items, list) else None,
            "result": items,
            "result_info": res.result_info,
        }
    )
    return 0


def cmd_zero_trust_access_policies_get(args, ctx) -> int:
    _require_token(ctx)
    account_id = _resolve_account_id(args, ctx)
    app_id = str(getattr(args, "app_id", "") or "").strip()
    policy_id = str(getattr(args, "policy_id", "") or "").strip()
    if not app_id:
        raise ValidationError("Missing --app-id")
    if not policy_id:
        raise ValidationError("Missing --policy-id")
    res = ctx["cf"].get_json(f"/accounts/{account_id}/access/apps/{app_id}/policies/{policy_id}")
    ctx["out"].emit(
        {
            "ok": True,
            "command": "zero_trust.access.policies.get",
            "account_id": account_id,
            "app_id": app_id,
            "policy_id": policy_id,
            "result": res.result,
        }
    )
    return 0
