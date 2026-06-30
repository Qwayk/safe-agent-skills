from __future__ import annotations

from dataclasses import asdict
from pathlib import Path

from ..errors import ValidationError
from ..oauth_tokens import (
    create_access_token,
    get_token_status,
    inspect_access_token,
    metadata_view,
    read_access_token_from_file,
    read_refresh_token_from_file,
    read_token_json,
    request_access_token,
    refresh_access_token,
    token_path_for_env_file,
    write_token_from_dict,
    write_token_from_file,
)


def _safe_token_metadata(data: dict, *, source: str) -> dict:
    safe = metadata_view(data)
    if "source" in safe:
        safe["source"] = source
    else:
        safe.update({"source": source})
    return safe


def _missing_app_inputs(cfg) -> list[str]:
    missing: list[str] = []
    if not cfg.app_id:
        missing.append("WIX_APP_ID")
    if not cfg.app_secret:
        missing.append("WIX_APP_SECRET")
    if not cfg.instance_id:
        missing.append("WIX_INSTANCE_ID")
    return missing


def _missing_refresh_inputs(cfg) -> list[str]:
    missing: list[str] = []
    if not cfg.app_id:
        missing.append("WIX_APP_ID")
    if not cfg.app_secret:
        missing.append("WIX_APP_SECRET")
    return missing


def _missing_request_inputs(cfg) -> list[str]:
    missing: list[str] = []
    if not cfg.app_id:
        missing.append("WIX_APP_ID")
    if not cfg.app_secret:
        missing.append("WIX_APP_SECRET")
    return missing


def _pick_token_for_inspect(cfg, token_path: Path, provided_token: str | None) -> tuple[str | None, str | None]:
    if provided_token and provided_token.strip():
        return provided_token.strip(), "provided"

    if getattr(cfg, "access_token", None):
        return str(cfg.access_token), "env"

    token = read_access_token_from_file(token_path)
    if token:
        return token, "stored"

    return None, None


def _pick_refresh_token(token_path: Path, provided_refresh_token: str | None) -> tuple[str | None, str | None]:
    if provided_refresh_token and provided_refresh_token.strip():
        return provided_refresh_token.strip(), "provided"

    refresh_token = read_refresh_token_from_file(token_path)
    if refresh_token:
        return refresh_token, "stored"

    return None, None


def cmd_auth_check(args, ctx) -> int:
    cfg = ctx["cfg"]
    token_path = token_path_for_env_file(ctx["env_file"])
    token_status = get_token_status(token_path)

    readiness = {
        "base_url": bool(cfg.base_url),
        "app_auth_inputs": bool(cfg.has_official_app_auth),
        "manual_access_token": bool(getattr(cfg, "access_token", None)),
        "stored_access_token": bool(token_status.exists and token_status.has_access_token),
    }

    out = {
        "ok": True,
        "base_url": cfg.base_url,
        "readiness": readiness,
        "missing": _missing_app_inputs(cfg) if not readiness["app_auth_inputs"] else [],
        "token_status": asdict(token_status),
    }

    if readiness["app_auth_inputs"]:
        try:
            token_response = create_access_token(
                base_url=cfg.base_url,
                app_id=str(cfg.app_id),
                app_secret=str(cfg.app_secret),
                instance_id=str(cfg.instance_id),
                timeout_s=float(cfg.timeout_s),
                verbose=bool(ctx.get("verbose")),
            )
            safe_token = _safe_token_metadata(token_response, source="app_credentials")
            out["token_endpoint"] = {"path": cfg.base_url.rstrip("/") + "/oauth2/token", "result": safe_token}
            out["checked_with"] = "app_credentials"
        except Exception as exc:
            ctx["audit"].write("auth.check", {"error": str(exc), "error_type": type(exc).__name__})
            out = {
                "ok": False,
                "error": str(exc),
                "error_type": type(exc).__name__,
                "base_url": cfg.base_url,
                "readiness": readiness,
                "token_status": asdict(token_status),
            }
            ctx["out"].emit(out)
            return 1
    elif cfg.access_token or token_status.exists:
        token, source = _pick_token_for_inspect(cfg, token_path, None)
        if not token:
            ctx["out"].emit(
                {
                    "ok": False,
                    "error": "Missing token value",
                    "error_type": "ValidationError",
                    "base_url": cfg.base_url,
                    "readiness": readiness,
                    "token_status": asdict(token_status),
                }
            )
            return 1

        try:
            info = inspect_access_token(
                base_url=cfg.base_url,
                token=token,
                timeout_s=float(cfg.timeout_s),
                verbose=bool(ctx.get("verbose")),
            )
            out["token_info"] = _safe_token_metadata(info, source=source or "stored")
            out["checked_with"] = "token_info"
        except Exception as exc:
            ctx["audit"].write("auth.check", {"error": str(exc), "error_type": type(exc).__name__})
            out = {
                "ok": False,
                "error": str(exc),
                "error_type": type(exc).__name__,
                "base_url": cfg.base_url,
                "readiness": readiness,
                "token_status": asdict(token_status),
            }
            ctx["out"].emit(out)
            return 1
    else:
        out = {
            "ok": False,
            "error": "Missing official Wix credentials and no local token source",
            "error_type": "ValidationError",
            "base_url": cfg.base_url,
            "readiness": readiness,
            "missing": _missing_app_inputs(cfg),
            "token_status": asdict(token_status),
        }
        ctx["out"].emit(out)
        return 1

    ctx["audit"].write("auth.check", out)
    ctx["out"].emit(out)
    return 0


def cmd_auth_token_create(args, ctx) -> int:
    cfg = ctx["cfg"]
    if not cfg.has_official_app_auth:
        missing = _missing_app_inputs(cfg)
        raise ValidationError(f"Missing credentials for token create: {', '.join(missing)}")

    token_response = create_access_token(
        base_url=cfg.base_url,
        app_id=cfg.app_id,
        app_secret=cfg.app_secret,
        instance_id=cfg.instance_id,
        timeout_s=cfg.timeout_s,
        verbose=bool(ctx.get("verbose")),
    )
    dest = token_path_for_env_file(ctx["env_file"])
    token_status = write_token_from_dict(token_payload=token_response, dest_file=dest)

    if not token_response.get("access_token"):
        raise ValidationError("No access_token returned from token endpoint")

    out = {
        "ok": True,
        "stored_to": token_status.path,
        "token_status": asdict(token_status),
        "oauth_token": _safe_token_metadata(token_response, source="created"),
    }
    ctx["audit"].write("auth.token_create", out)
    ctx["out"].emit(out)
    return 0


def cmd_auth_token_request(args, ctx) -> int:
    cfg = ctx["cfg"]
    missing = _missing_request_inputs(cfg)
    if missing:
        raise ValidationError(f"Missing credentials for token request: {', '.join(missing)}")

    code = getattr(args, "code", None)
    if not isinstance(code, str) or not code.strip():
        raise ValidationError("Missing --code")

    token_response = request_access_token(
        base_url=cfg.base_url,
        app_id=str(cfg.app_id),
        app_secret=str(cfg.app_secret),
        code=code.strip(),
        timeout_s=float(cfg.timeout_s),
        verbose=bool(ctx.get("verbose")),
    )
    dest = token_path_for_env_file(ctx["env_file"])
    token_status = write_token_from_dict(token_payload=token_response, dest_file=dest)

    if not token_response.get("access_token"):
        raise ValidationError("No access_token returned from token endpoint")

    out = {
        "ok": True,
        "stored_to": token_status.path,
        "token_status": asdict(token_status),
        "oauth_token": _safe_token_metadata(token_response, source="requested"),
        "notes": [
            "This uses the legacy custom-auth request-access-token flow from official Wix docs.",
            "Wix marks this method deprecated for new apps and keeps it only for existing legacy custom-auth apps.",
        ],
    }
    ctx["audit"].write("auth.token_request", out)
    ctx["out"].emit(out)
    return 0


def cmd_auth_token_refresh(args, ctx) -> int:
    cfg = ctx["cfg"]
    token_path = token_path_for_env_file(ctx["env_file"])
    current_token = read_token_json(token_path) or {}
    refresh_token, source = _pick_refresh_token(token_path, getattr(args, "refresh_token", None))

    if not refresh_token:
        raise ValidationError("No refresh token provided and no refresh_token found in local token state")

    missing = _missing_refresh_inputs(cfg)
    if missing:
        raise ValidationError(f"Missing credentials for token refresh: {', '.join(missing)}")

    token_response = refresh_access_token(
        base_url=cfg.base_url,
        app_id=str(cfg.app_id),
        app_secret=str(cfg.app_secret),
        refresh_token=refresh_token,
        timeout_s=float(cfg.timeout_s),
        verbose=bool(ctx.get("verbose")),
    )
    if not token_response.get("access_token"):
        raise ValidationError("No access_token returned from refresh endpoint")

    stored_payload = dict(current_token) if isinstance(current_token, dict) else {}
    stored_payload.update(token_response)
    if not stored_payload.get("refresh_token"):
        stored_payload["refresh_token"] = refresh_token

    token_status = write_token_from_dict(token_payload=stored_payload, dest_file=token_path)
    out = {
        "ok": True,
        "stored_to": token_status.path,
        "source": source,
        "token_status": asdict(token_status),
        "oauth_token": _safe_token_metadata(stored_payload, source="refreshed"),
        "notes": [
            "This uses the legacy custom-auth refresh flow from official Wix docs.",
            "Wix marks this method deprecated for new apps.",
        ],
    }
    ctx["audit"].write("auth.token_refresh", out)
    ctx["out"].emit(out)
    return 0


def cmd_auth_token_inspect(args, ctx) -> int:
    cfg = ctx["cfg"]
    token_path = token_path_for_env_file(ctx["env_file"])
    provided_token = getattr(args, "token", None)
    token, source = _pick_token_for_inspect(cfg, token_path, provided_token)

    if not token:
        raise ValidationError("No token provided and no token available from WIX_ACCESS_TOKEN or state")

    token_status = get_token_status(token_path)
    info = inspect_access_token(
        base_url=cfg.base_url,
        token=token,
        timeout_s=cfg.timeout_s,
        verbose=bool(ctx.get("verbose")),
    )
    out = {
        "ok": True,
        "source": source,
        "token_status": asdict(token_status),
        "token_info": _safe_token_metadata(info, source=source or "unknown"),
    }
    ctx["audit"].write("auth.token_inspect", out)
    ctx["out"].emit(out)
    return 0


def cmd_auth_token_set(args, ctx) -> int:
    dest = token_path_for_env_file(ctx["env_file"])
    token_status = write_token_from_file(src_file=Path(args.file), dest_file=dest)
    token_data = read_token_json(dest)
    safe_token = _safe_token_metadata(token_data or {}, source="file")

    out = {"ok": True, "stored_to": str(dest), "token_status": asdict(token_status), "oauth_token": safe_token}
    ctx["audit"].write("auth.token_set", out)
    ctx["out"].emit(out)
    return 0


def cmd_auth_token_status(args, ctx) -> int:
    _ = args
    token_status = get_token_status(token_path_for_env_file(ctx["env_file"]))
    out = {"ok": True, "token_status": asdict(token_status)}
    ctx["audit"].write("auth.token_status", out)
    ctx["out"].emit(out)
    return 0
