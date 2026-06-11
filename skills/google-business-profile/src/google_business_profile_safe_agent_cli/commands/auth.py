from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ..errors import ValidationError
from ..oauth_tokens import get_token_status, read_token_json, token_path_for_env_file, write_token_data, write_token_from_file


def _parse_scopes(raw: str) -> list[str]:
    return [s for s in raw.replace(",", " ").split() if s.strip()]


def _parse_credentials(path: Path) -> dict[str, Any]:
    data = read_token_json(path)
    if data is None:
        raise ValidationError(f"OAuth credentials not found: {path}")
    if not isinstance(data, dict):
        raise ValidationError(f"OAuth credentials file is invalid: {path}")
    return data


def _scope_set(values: list[str]) -> list[str]:
    normalized = []
    for value in values:
        if value and value.strip():
            normalized.append(value.strip())
    return normalized


def _load_validated_credentials(path: Path) -> tuple[dict[str, Any], bool]:
    """
    Return the parsed credentials object and whether it looks currently valid.
    """
    data = _parse_credentials(path)
    try:
        from google.oauth2 import credentials as google_credentials  # type: ignore

        creds = google_credentials.Credentials.from_authorized_user_info(data)
        return data, bool(creds.valid)
    except Exception:
        return data, False


def _can_refresh_credentials(data: dict[str, Any]) -> bool:
    try:
        from google.auth.transport.requests import Request as GoogleAuthRequest  # type: ignore
        from google.oauth2 import credentials as google_credentials  # type: ignore

        creds = google_credentials.Credentials.from_authorized_user_info(data)
        if bool(creds.valid):
            return True
        creds.refresh(GoogleAuthRequest())
        return bool(getattr(creds, "token", None))
    except Exception:
        return False


def cmd_auth_check(args, ctx) -> int:
    # Read-only auth health check for installed-app credentials.
    _ = args
    cfg = ctx["cfg"]
    tok_path = token_path_for_env_file(ctx["env_file"])
    status = get_token_status(tok_path)

    valid = False
    needs_reauth = True
    credential_keys: list[str] = []
    reason = "No OAuth credentials file found."
    if tok_path.exists():
        data, valid = _load_validated_credentials(tok_path)
        if not valid:
            valid = _can_refresh_credentials(data)
        credential_keys = sorted([k for k in data.keys() if isinstance(k, str)])
        needs_reauth = not valid
        if valid:
            reason = "Credentials file exists and can be used to get a valid access token."
        else:
            reason = "Credentials file exists but could not be refreshed into a valid access token."

    out = {
        "ok": bool(status.exists and valid),
        "auth_mode": "installed_app",
        "auth_file": tok_path.as_posix(),
        "status": status.__dict__,
        "oauth_client_secrets_file": cfg.oauth_client_secrets_file,
        "oauth_scopes": list(cfg.oauth_scopes),
        "base_url": cfg.base_url,
        "credential_keys": credential_keys,
        "needs_reauth": needs_reauth,
        "note": reason,
    }
    ctx["audit"].write("auth.check", out)
    ctx["out"].emit(out)
    return 0


def cmd_auth_token_set(args, ctx) -> int:
    dest = token_path_for_env_file(ctx["env_file"])
    st = write_token_from_file(src_file=Path(args.file), dest_file=dest)
    out = {"ok": True, "stored_to": st.path, "token_status": st.__dict__}
    ctx["audit"].write("auth.token_set", out)
    ctx["out"].emit(out)
    return 0


def cmd_auth_login(args, ctx) -> int:
    cfg = ctx["cfg"]
    client_secrets_file = str(getattr(args, "client_secrets_file", "") or "").strip()
    if not client_secrets_file:
        client_secrets_file = str(cfg.oauth_client_secrets_file or "").strip()
    if not client_secrets_file:
        raise ValidationError(
            "Missing OAuth client secrets path. Set GBP_OAUTH_CLIENT_SECRETS_FILE in --env-file or pass --client-secrets-file."
        )

    p = Path(client_secrets_file)
    if not p.exists():
        raise ValidationError(f"OAuth client secrets file not found: {p}")

    scopes = _scope_set(_parse_scopes(str(getattr(args, "scopes", "") or "")))
    if not scopes:
        scopes = _scope_set(" ".join(cfg.oauth_scopes))
    if not scopes:
        raise ValidationError("OAuth scopes must be set before login.")

    # Keep Google deps lazy to keep import-time health checks simple.
    from google_auth_oauthlib.flow import InstalledAppFlow  # type: ignore

    flow = InstalledAppFlow.from_client_secrets_file(str(p), scopes=scopes)

    use_console = bool(getattr(args, "console", False))
    port = int(getattr(args, "port", 0) or 0)
    creds = flow.run_console() if use_console else flow.run_local_server(port=port)
    creds_data = json.loads(creds.to_json())
    st = write_token_data(dest_file=token_path_for_env_file(ctx["env_file"]), data=creds_data)

    out = {"ok": True, "stored_to": st.path, "token_status": st.__dict__, "requested_scopes": scopes}
    ctx["audit"].write("auth.login", out)
    ctx["out"].emit(out)
    return 0


def cmd_auth_token_status(args, ctx) -> int:
    _ = args
    st = get_token_status(token_path_for_env_file(ctx["env_file"]))
    out = {"ok": True, "token_status": st.__dict__}
    ctx["audit"].write("auth.token_status", out)
    ctx["out"].emit(out)
    return 0
