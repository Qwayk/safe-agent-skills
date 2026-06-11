from __future__ import annotations

import datetime
import json
import secrets
import time
import urllib.parse
from pathlib import Path
from typing import Any

import requests

from ..errors import SafetyError, ValidationError
from ..http import HttpClient
from ..oauth_tokens import (
    get_token_status,
    read_token_json,
    token_path_for_env_file,
    write_token_from_file,
)


def _utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _parse_expiry_timestamp(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        value_f = float(value)
        if value_f < 0:
            return None
        if value_f > 10_000_000_000:
            value_f = value_f / 1000
        return value_f
    if isinstance(value, str):
        raw = value.strip()
        if not raw:
            return None
        try:
            value_f = float(raw)
            if value_f < 0:
                return None
            if value_f > 10_000_000_000:
                value_f = value_f / 1000
            return value_f
        except ValueError:
            pass
        try:
            dt = datetime.datetime.fromisoformat(raw.replace("Z", "+00:00"))
            if dt.tzinfo is not None:
                return dt.timestamp()
            return time.mktime(dt.timetuple())
        except ValueError:
            return None
    return None


def _extract_expiry_time(token_obj: dict[str, Any]) -> float | None:
    for key in ("expires_at", "expiry", "expires", "expiration"):
        if key in token_obj:
            ts = _parse_expiry_timestamp(token_obj.get(key))
            if ts is not None:
                return ts

    expires_in = token_obj.get("expires_in")
    if isinstance(expires_in, (int, float, str)):
        value = _parse_expiry_timestamp(expires_in)
        if value is not None:
            return time.time() + value
    return None


def _require_live_reddit_call(ctx: dict[str, Any], command_name: str) -> None:
    if not bool(ctx.get("live")):
        raise SafetyError(f"Refused: --live is required for {command_name} because it calls Reddit")


def _oauth_state_path(env_file: str) -> Path:
    root = Path(env_file).resolve().parent
    return root / ".state" / "oauth_start.json"


def _token_request_auth(cfg: Any) -> tuple[str, str]:
    client_id = str(cfg.client_id or "").strip()
    if not client_id:
        raise ValidationError("Missing REDDIT_CLIENT_ID")
    client_secret = str(cfg.client_secret or "")
    return client_id, client_secret


def _compute_expires_at(token_obj: dict[str, Any]) -> dict[str, Any]:
    out = dict(token_obj)
    expires_in = out.get("expires_in")
    if isinstance(expires_in, (int, float)):
        out["expires_at"] = int(time.time() + float(expires_in))
    out["saved_at_utc"] = _utc_now()
    return out


def _write_token_json(env_file: str, token_obj: dict[str, Any]) -> None:
    dest = token_path_for_env_file(env_file)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(_compute_expires_at(token_obj), ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _is_token_fresh(token_obj: dict[str, Any], *, skew_s: int = 60) -> bool:
    expires_at = _extract_expiry_time(token_obj)
    if expires_at is None:
        return False
    return float(expires_at) > (time.time() + skew_s)


def _refresh_token(cfg: Any, refresh_token: str, timeout_s: float) -> dict[str, Any]:
    auth = _token_request_auth(cfg)
    response = requests.post(
        cfg.token_url,
        auth=auth,
        data={"grant_type": "refresh_token", "refresh_token": refresh_token},
        headers={"User-Agent": cfg.user_agent},
        timeout=timeout_s,
    )
    if response.status_code >= 400:
        raise RuntimeError(f"Token refresh failed: HTTP {response.status_code}")
    payload = response.json()
    if not isinstance(payload, dict):
        raise RuntimeError("Token refresh response must be a JSON object")
    if "refresh_token" not in payload:
        payload["refresh_token"] = refresh_token
    return payload


def ensure_access_token(*, cfg: Any, env_file: str, timeout_s: float, verbose: bool) -> tuple[str, str]:
    env_token = str(cfg.bearer_token or "").strip()
    if env_token:
        return env_token, "env"

    token_path = token_path_for_env_file(env_file)
    token_obj = read_token_json(token_path) if token_path.exists() else None
    if token_obj and _is_token_fresh(token_obj):
        access_token = str(token_obj.get("access_token") or "").strip()
        if access_token:
            return access_token, "token_file"

    refresh_token = str((token_obj or {}).get("refresh_token") or "").strip()
    if refresh_token:
        refreshed = _refresh_token(cfg, refresh_token, timeout_s)
        _write_token_json(env_file, refreshed)
        access_token = str(refreshed.get("access_token") or "").strip()
        if access_token:
            return access_token, "refreshed_token"

    raise ValidationError(
        "Missing usable Reddit OAuth token. Run `qwayk-reddit-safe-agent-cli auth login` then `--live auth exchange-code`, or use `auth token set`."
    )


def cmd_auth_check(args: Any, ctx: dict[str, Any]) -> int:
    cfg = ctx["cfg"]
    token_path = token_path_for_env_file(ctx["env_file"])
    status = get_token_status(token_path)
    live_allowed = bool(ctx.get("live"))
    out: dict[str, Any] = {
        "ok": True,
        "base_url": cfg.base_url,
        "client_id_present": bool(cfg.client_id),
        "client_secret_present": bool(cfg.client_secret),
        "redirect_uri_present": bool(cfg.redirect_uri),
        "env_access_token_present": bool(cfg.bearer_token),
        "oauth_scopes": cfg.oauth_scopes.split(),
        "oauth_token": {"exists": status.exists, "path": status.path, "has_refresh_token": status.has_refresh_token, "expires_at_utc": status.expires_at_utc},
        "live_allowed": live_allowed,
        "live_checked": False,
    }

    if live_allowed:
        access_token, source = ensure_access_token(
            cfg=cfg,
            env_file=str(ctx["env_file"]),
            timeout_s=float(ctx["timeout_s"]),
            verbose=bool(ctx.get("verbose")),
        )
        client = HttpClient(timeout_s=float(ctx["timeout_s"]), verbose=bool(ctx.get("verbose")), user_agent=cfg.user_agent)
        response = client.request(
            "GET",
            cfg.base_url.rstrip("/") + "/api/v1/me",
            headers={"Authorization": f"Bearer {access_token}", "Accept": "application/json"},
        )
        out["live_checked"] = True
        out["token_source"] = source
        out["live_status_code"] = response.status
        try:
            body = response.json()
            if isinstance(body, dict):
                out["live_response_keys"] = sorted(k for k in body.keys() if isinstance(k, str))
                out["live_account_name"] = body.get("name")
        except Exception:
            out["live_response_keys"] = None

    ctx["audit"].write("auth.check", out)
    ctx["out"].emit(out)
    return 0


def cmd_auth_login(args: Any, ctx: dict[str, Any]) -> int:
    cfg = ctx["cfg"]
    if not cfg.client_id:
        raise ValidationError("Missing REDDIT_CLIENT_ID")
    if not cfg.redirect_uri:
        raise ValidationError("Missing REDDIT_REDIRECT_URI")

    scopes = str(getattr(args, "scopes", "") or cfg.oauth_scopes).strip()
    if not scopes:
        raise ValidationError("Missing OAuth scopes")
    duration = str(getattr(args, "duration", "") or "permanent").strip() or "permanent"
    state = str(getattr(args, "state", "") or "").strip() or secrets.token_urlsafe(24)

    params = {
        "client_id": cfg.client_id,
        "response_type": "code",
        "state": state,
        "redirect_uri": cfg.redirect_uri,
        "duration": duration,
        "scope": scopes,
    }
    authorize_url = cfg.authorize_url + ("&" if "?" in cfg.authorize_url else "?") + urllib.parse.urlencode(params)

    state_path = _oauth_state_path(ctx["env_file"])
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_obj = {
        "saved_at_utc": _utc_now(),
        "state": state,
        "duration": duration,
        "scopes": scopes,
        "authorize_url": cfg.authorize_url,
        "token_url": cfg.token_url,
        "redirect_uri": cfg.redirect_uri,
        "client_id": cfg.client_id,
    }
    state_path.write_text(json.dumps(state_obj, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    out = {
        "ok": True,
        "login": {
            "authorize_url": authorize_url,
            "state_path": str(state_path),
            "next_command": "qwayk-reddit-safe-agent-cli --live auth exchange-code --redirect-url '<paste redirect url>'",
        }
    }
    ctx["audit"].write("auth.login", {"state_path": str(state_path)})
    ctx["out"].emit(out)
    return 0


def _parse_redirect_url(redirect_url: str) -> tuple[str | None, str | None, str | None]:
    parsed = urllib.parse.urlsplit(redirect_url)
    query = dict(urllib.parse.parse_qsl(parsed.query, keep_blank_values=True))
    return query.get("code"), query.get("state"), query.get("error")


def cmd_auth_exchange_code(args: Any, ctx: dict[str, Any]) -> int:
    _require_live_reddit_call(ctx, "auth exchange-code")
    cfg = ctx["cfg"]
    code = str(getattr(args, "code", "") or "").strip()
    state = str(getattr(args, "state", "") or "").strip()
    redirect_url = str(getattr(args, "redirect_url", "") or "").strip()
    if redirect_url:
        parsed_code, parsed_state, parsed_error = _parse_redirect_url(redirect_url)
        if parsed_error:
            raise ValidationError(f"OAuth redirect returned error: {parsed_error}")
        code = code or (parsed_code or "")
        state = state or (parsed_state or "")
    if not code:
        raise ValidationError("Missing authorization code. Provide --code or --redirect-url.")

    state_path = _oauth_state_path(ctx["env_file"])
    if not state_path.exists():
        raise ValidationError(f"Missing saved OAuth state: {state_path}")
    state_obj = json.loads(state_path.read_text(encoding="utf-8"))
    if not isinstance(state_obj, dict):
        raise ValidationError("OAuth state file must be a JSON object")
    expected_state = str(state_obj.get("state") or "").strip()
    if expected_state and state and state != expected_state:
        raise ValidationError("OAuth state mismatch")

    auth = _token_request_auth(cfg)
    redirect_uri = str(state_obj.get("redirect_uri") or cfg.redirect_uri or "").strip()
    response = requests.post(
        cfg.token_url,
        auth=auth,
        data={"grant_type": "authorization_code", "code": code, "redirect_uri": redirect_uri},
        headers={"User-Agent": cfg.user_agent},
        timeout=float(ctx["timeout_s"]),
    )
    if response.status_code >= 400:
        raise RuntimeError(f"Token exchange failed: HTTP {response.status_code}")
    token_obj = response.json()
    if not isinstance(token_obj, dict):
        raise RuntimeError("Token exchange response must be a JSON object")
    _write_token_json(str(ctx["env_file"]), token_obj)

    status = get_token_status(token_path_for_env_file(str(ctx["env_file"])))
    out = {"ok": True, "stored_to": status.path, "token_status": status.__dict__}
    ctx["audit"].write("auth.exchange_code", {"stored_to": status.path, "fields": status.fields})
    ctx["out"].emit(out)
    return 0


def cmd_auth_refresh(args: Any, ctx: dict[str, Any]) -> int:
    _ = args
    _require_live_reddit_call(ctx, "auth refresh")
    cfg = ctx["cfg"]
    token_path = token_path_for_env_file(str(ctx["env_file"]))
    token_obj = read_token_json(token_path) if token_path.exists() else None
    refresh_token = str((token_obj or {}).get("refresh_token") or "").strip()
    if not refresh_token:
        raise ValidationError("Missing refresh token in .state/token.json")
    refreshed = _refresh_token(cfg, refresh_token, float(ctx["timeout_s"]))
    _write_token_json(str(ctx["env_file"]), refreshed)
    status = get_token_status(token_path_for_env_file(str(ctx["env_file"])))
    out = {"ok": True, "stored_to": status.path, "token_status": status.__dict__}
    ctx["audit"].write("auth.refresh", {"stored_to": status.path, "fields": status.fields})
    ctx["out"].emit(out)
    return 0


def cmd_auth_token_set(args: Any, ctx: dict[str, Any]) -> int:
    dest = token_path_for_env_file(ctx["env_file"])
    status = write_token_from_file(src_file=Path(args.file), dest_file=dest)
    out = {"ok": True, "stored_to": status.path, "token_status": status.__dict__}
    ctx["audit"].write("auth.token_set", out)
    ctx["out"].emit(out)
    return 0


def cmd_auth_token_status(args: Any, ctx: dict[str, Any]) -> int:
    _ = args
    status = get_token_status(token_path_for_env_file(ctx["env_file"]))
    out = {"ok": True, "token_status": status.__dict__}
    ctx["audit"].write("auth.token_status", out)
    ctx["out"].emit(out)
    return 0
