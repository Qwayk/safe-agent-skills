from __future__ import annotations

from ..google_auth import load_adc_credentials
from ..redaction import sanitize_error_message


def cmd_auth_check(args, ctx) -> int:
    _ = args
    cfg = ctx["cfg"]
    try:
        adc = load_adc_credentials(quota_project_id=getattr(cfg, "quota_project", None))
        out = {
            "ok": True,
            "adc": {
                "project_id": adc.project_id,
                "quota_project": adc.quota_project_id,
                "refreshed": adc.refreshed,
                "credentials_valid": bool(getattr(adc.credentials, "valid", False)),
            },
        }
        ctx["audit"].write("auth.check", out)
        ctx["out"].emit(out)
        return 0
    except Exception as exc:  # noqa: BLE001
        values = list(cfg.redaction_values()) if cfg is not None else []
        out = {
            "ok": False,
            "error": sanitize_error_message(exc, values),
            "error_type": type(exc).__name__,
        }
        ctx["audit"].write("auth.check_error", out)
        ctx["out"].emit(out)
        return 1
