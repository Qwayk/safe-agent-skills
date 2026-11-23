from __future__ import annotations

from ..google_auth import credential_identity, load_adc_credentials
from ..redaction import sanitize_error_message


def cmd_auth_check(args, ctx) -> int:
    cfg = ctx["cfg"]
    quota_override = str(getattr(args, "quota_project", "") or "").strip()
    try:
        adc = load_adc_credentials(quota_project_id=quota_override or getattr(cfg, "quota_project", None))
        try:
            identity, _ = credential_identity(adc)
        except RuntimeError:
            identity = None
        out = {
            "ok": True,
            "adc": {
                "project_id": adc.project_id,
                "quota_project": adc.quota_project_id,
                "identity": identity,
                "can_bind_write_plan": identity is not None,
                "refreshed": adc.refreshed,
                "credentials_valid": bool(getattr(adc.credentials, "valid", False)),
            },
        }
        ctx["audit"].write("auth.check", out)
        ctx["out"].emit(out)
        return 0
    except Exception as exc:  # noqa: BLE001
        values = list(cfg.redaction_values()) if cfg is not None else []
        if quota_override:
            values.append(quota_override)
        out = {
            "ok": False,
            "error": sanitize_error_message(exc, values),
            "error_type": type(exc).__name__,
        }
        ctx["audit"].write("auth.check_error", out)
        ctx["out"].emit(out)
        return 1
