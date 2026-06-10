from __future__ import annotations


def cmd_auth_check(args, ctx) -> int:
    _ = args
    cfg = ctx["cfg"]
    configured = {
        "commerce_secret_key": bool(cfg.commerce_secret_key),
        "commerce_site_api_key": bool(cfg.commerce_site_api_key),
        "advertising_api_key": bool(cfg.advertising_api_key),
        "advertising_publisher_id": bool(cfg.advertising_publisher_id),
    }
    command_bundles = {
        "commerce_secret_commands": configured["commerce_secret_key"],
        "commerce_site_key_commands": configured["commerce_site_api_key"],
        "mixed_commerce_commands": configured["commerce_secret_key"] and configured["commerce_site_api_key"],
        "advertising_reporting_commands": configured["advertising_api_key"] and configured["advertising_publisher_id"],
    }
    ready_for_any = any(command_bundles.values())
    ready_for_full_coverage = all(configured.values())
    missing_recommended = [name for name, present in configured.items() if not present]
    out = {
        "ok": True,
        "auth_check": {
            "mode": "local-config-only",
            "configured": configured,
            "command_bundles": command_bundles,
            "ready_for_any_sovrn_commands": ready_for_any,
            "ready_for_full_coverage": ready_for_full_coverage,
            "missing_recommended": missing_recommended,
            "env_fingerprint": cfg.env_fingerprint,
            "notes": [
                "This check only validates local Sovrn config presence.",
                "Advertising commands need both SOVRN_ADVERTISING_API_KEY and SOVRN_ADVERTISING_PUBLISHER_ID.",
                "Mixed Commerce commands need both the Commerce secret key and the Commerce site API key.",
                "Use the real commerce or advertising read commands for live vendor proof.",
            ],
        },
    }
    ctx["audit"].write("auth.check", out)
    ctx["out"].emit(out)
    return 0
