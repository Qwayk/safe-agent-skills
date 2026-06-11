from __future__ import annotations

from ..errors import ValidationError
from ..google_auth import (
    credentials_path_for_env_file,
    load_credentials_from_config,
    login_installed_app,
)


def cmd_auth_check(args, ctx) -> int:
    _ = args
    cfg = ctx["cfg"]
    creds, info = load_credentials_from_config(
        env_file=ctx["env_file"],
        oauth_client_secrets_file=cfg.oauth_client_secrets_file,
        service_account_file=cfg.service_account_file,
        scopes=cfg.oauth_scopes,
    )

    if creds is None and not info.exists:
        raise ValidationError(
            "Missing OAuth credentials. Run: gsc-api-tool auth login "
            f"(expected credentials at {credentials_path_for_env_file(ctx['env_file'])})"
        )

    out = {"ok": True, "base_url": cfg.base_url, "credentials": info.__dict__}
    ctx["audit"].write("auth.check", out)
    ctx["out"].emit(out)
    return 0


def cmd_auth_login(args, ctx) -> int:
    _ = args
    cfg = ctx["cfg"]

    if cfg.service_account_file:
        raise ValidationError("Service account auth does not use `auth login` (set GSC_SERVICE_ACCOUNT_FILE)")
    if not cfg.oauth_client_secrets_file:
        raise ValidationError("Missing GSC_OAUTH_CLIENT_SECRETS_FILE (client secrets JSON)")

    dest = credentials_path_for_env_file(ctx["env_file"])
    info = login_installed_app(
        client_secrets_file=cfg.oauth_client_secrets_file,
        scopes=cfg.oauth_scopes,
        dest_path=dest,
    )

    out = {"ok": True, "stored_to": str(dest), "credentials": info.__dict__}
    ctx["audit"].write("auth.login", out)
    ctx["out"].emit(out)
    return 0

