from __future__ import annotations

import secrets
import sys
import threading
import time
from pathlib import Path
from urllib.parse import parse_qs, urlparse, urlencode

from ..api import PinterestApi, refresh_access_token, resolve_access_token
from ..oauth_tokens import (
    get_token_status,
    redact_token_dict,
    token_path_for_env_file,
    write_token_dict,
    write_token_from_file,
)
from .write_safety import before_state_contract


def _token_local_state(ctx: dict) -> dict:
    return {
        "kind": "token_state",
        "env_file": str(ctx.get("env_file") or ""),
        "token_path": str(token_path_for_env_file(ctx["env_file"])),
        "env_refresh_token_key": "PINTEREST_REFRESH_TOKEN",
    }


def _require_token_write_allowed(ctx: dict) -> None:
    missing: list[str] = []
    if not bool(ctx.get("yes")):
        missing.append("--yes")
    if not bool(ctx.get("ack_no_snapshot")):
        missing.append("--ack-no-snapshot")
    if missing:
        raise RuntimeError(f"Refusing to write local Pinterest token state: missing required flag(s): {', '.join(missing)}")


def _token_no_snapshot_fields(ctx: dict, *, action: str, operations: list[dict] | None = None) -> dict:
    reason = "No automatic before-state snapshot is available for this local Pinterest token-state write."
    return {
        "before_state": before_state_contract(
            reason=reason,
            provider_write={"service": "Pinterest API", "action": action, "operations": operations} if operations else None,
            local_state=_token_local_state(ctx),
        ),
        "no_snapshot_approval": {
            "acknowledged": True,
            "flag": "--ack-no-snapshot",
            "reason": reason,
        },
    }


def _upsert_env_var(env_file: str, key: str, value: str) -> None:
    """
    Update or append KEY=VALUE in the env file (best-effort; preserves other lines).
    """
    p = Path(env_file)
    lines = []
    if p.exists():
        lines = p.read_text(encoding="utf-8").splitlines()
    out = []
    replaced = False
    for line in lines:
        raw = line
        s = line.strip()
        if s.startswith("#") or "=" not in s:
            out.append(raw)
            continue
        if s.startswith("export "):
            s2 = s[len("export ") :].strip()
        else:
            s2 = s
        k, _ = s2.split("=", 1)
        if k.strip() == key:
            out.append(f"{key}={value}")
            replaced = True
        else:
            out.append(raw)
    if not replaced:
        if out and out[-1].strip():
            out.append("")
        out.append(f"{key}={value}")
    p.write_text("\n".join(out) + "\n", encoding="utf-8")


def cmd_auth_check(args, ctx) -> int:
    _ = args
    cfg = ctx["cfg"]
    tok_path = token_path_for_env_file(ctx["env_file"])
    status = get_token_status(tok_path)

    api = PinterestApi(
        base_url=cfg.base_url,
        http=ctx["http"],
        access_token=resolve_access_token(
            env_file=ctx["env_file"],
            env_access_token=cfg.access_token,
            env_refresh_token=cfg.refresh_token,
            app_id=cfg.app_id,
            app_secret=cfg.app_secret,
            base_url=cfg.base_url,
            http=ctx["http"],
        ),
    )
    user = api.get("/user_account")
    out = {
        "ok": True,
        "base_url": cfg.base_url,
        "oauth_token": {"exists": status.exists, "path": status.path, "updated_at_utc": status.updated_at_utc},
        "user_account": user,
    }
    ctx["audit"].write(
        "auth.check",
        {"base_url": cfg.base_url, "oauth_token": {"exists": status.exists, "path": status.path}},
    )
    ctx["out"].emit(out)
    return 0


def cmd_auth_token_set(args, ctx) -> int:
    _require_token_write_allowed(ctx)
    dest = token_path_for_env_file(ctx["env_file"])
    st = write_token_from_file(src_file=Path(args.file), dest_file=dest)
    out = {
        "ok": True,
        "stored_to": st.path,
        "token_status": st.__dict__,
        **_token_no_snapshot_fields(ctx, action="auth.token.set"),
    }
    ctx["audit"].write("auth.token_set", out)
    ctx["out"].emit(out)
    return 0


def cmd_auth_token_status(args, ctx) -> int:
    _ = args
    st = get_token_status(token_path_for_env_file(ctx["env_file"]))
    out = {"ok": True, "token_status": st.__dict__}
    ctx["audit"].write("auth.token_status", out)
    ctx["out"].emit(out)
    return 0


def cmd_auth_code_exchange(args, ctx) -> int:
    """
    Exchange an OAuth authorization code for access+refresh tokens and store them under `.state/token.json`.
    """
    cfg = ctx["cfg"]
    if not cfg.app_id or not cfg.app_secret:
        raise RuntimeError("Missing PINTEREST_APP_ID or PINTEREST_APP_SECRET in .env")

    code = str(args.code).strip()
    if not code:
        raise RuntimeError("--code must not be empty")

    redirect_uri = str(args.redirect_uri).strip()
    if not redirect_uri:
        raise RuntimeError("--redirect-uri must not be empty")

    _require_token_write_allowed(ctx)

    data = _exchange_authorization_code(
        base_url=cfg.base_url,
        http=ctx["http"],
        app_id=str(cfg.app_id),
        app_secret=str(cfg.app_secret),
        code=code,
        redirect_uri=redirect_uri,
        continuous_refresh=bool(args.continuous_refresh),
    )

    if not isinstance(data, dict):
        raise RuntimeError("Unexpected token exchange response (not an object)")

    if not isinstance(data.get("access_token"), str) or not data["access_token"].strip():
        raise RuntimeError("Token exchange response missing access_token")
    if not isinstance(data.get("refresh_token"), str) or not data["refresh_token"].strip():
        raise RuntimeError("Token exchange response missing refresh_token")

    # Best-effort: compute expires_at if expires_in exists.
    if isinstance(data.get("expires_in"), (int, float)):
        import time

        data["expires_at"] = int(time.time()) + int(data["expires_in"])

    dest = token_path_for_env_file(ctx["env_file"])
    st = write_token_dict(
        data={
            "access_token": data.get("access_token"),
            "refresh_token": data.get("refresh_token"),
            "expires_at": data.get("expires_at"),
            "scope": data.get("scope"),
            "token_type": data.get("token_type"),
        },
        dest_file=dest,
    )

    # Optional: keep refresh token in `.env` for long-term use (user requested).
    # This file is gitignored.
    _upsert_env_var(ctx["env_file"], "PINTEREST_REFRESH_TOKEN", str(data.get("refresh_token")))
    _upsert_env_var(ctx["env_file"], "PINTEREST_APP_ID", str(cfg.app_id))

    out = {
        "ok": True,
        "stored_to": st.path,
        "token_status": st.__dict__,
        "token_safe": redact_token_dict(data),
        "env_updated": True,
        **_token_no_snapshot_fields(
            ctx,
            action="auth.code.exchange",
            operations=[{"method": "POST", "path": "/oauth/token"}],
        ),
    }
    ctx["audit"].write("auth.code_exchange", {"stored_to": st.path, "env_updated": True})
    ctx["out"].emit(out)
    return 0


def _exchange_authorization_code(
    *,
    base_url: str,
    http,
    app_id: str,
    app_secret: str,
    code: str,
    redirect_uri: str,
    continuous_refresh: bool,
) -> dict:
    """
    Exchange an OAuth authorization code for access+refresh tokens.

    We keep this logic shared between `auth code exchange` and `auth login`.
    """
    from base64 import b64encode  # local import to keep module load simple

    basic = b64encode(f"{app_id}:{app_secret}".encode("utf-8")).decode("utf-8")
    data = http.request(
        "POST",
        f"{base_url.rstrip('/')}/oauth/token",
        headers={
            "Accept": "application/json",
            "Authorization": f"Basic {basic}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
        data={
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri,
            "continuous_refresh": "true" if bool(continuous_refresh) else "false",
        },
        retries=2,
    ).json()
    if not isinstance(data, dict):
        raise RuntimeError("Unexpected token exchange response (not an object)")
    return data


def _build_oauth_authorize_url(*, app_id: str, redirect_uri: str, scopes: list[str], state: str) -> str:
    """
    Build the Pinterest OAuth authorization URL (user consent screen).
    """
    cleaned_scopes = ",".join([s.strip() for s in scopes if (s or "").strip()])
    if not cleaned_scopes:
        raise RuntimeError("At least one OAuth scope is required")
    q = urlencode(
        {
            "client_id": app_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": cleaned_scopes,
            "state": state,
        }
    )
    return f"https://www.pinterest.com/oauth/?{q}"


def cmd_auth_login(args, ctx) -> int:
    """
    Run a local localhost OAuth flow:
    - start a local HTTP server
    - open browser (optional) to Pinterest consent screen
    - capture the `code` from redirect
    - exchange it and store `.state/token.json`
    - run an auth check as proof
    """
    cfg = ctx["cfg"]
    if not cfg.app_id or not cfg.app_secret:
        raise RuntimeError("Missing PINTEREST_APP_ID or PINTEREST_APP_SECRET in .env")

    redirect_uri = str(args.redirect_uri).strip()
    if not redirect_uri:
        raise RuntimeError("--redirect-uri must not be empty")

    u = urlparse(redirect_uri)
    if u.scheme != "http":
        raise RuntimeError("--redirect-uri must use http:// for localhost redirect")
    if u.hostname not in {"localhost", "127.0.0.1"}:
        raise RuntimeError("--redirect-uri host must be localhost or 127.0.0.1")
    if u.port is None:
        raise RuntimeError("--redirect-uri must include an explicit port, e.g. http://localhost:8765/")
    path = u.path or "/"
    if not path.startswith("/"):
        path = f"/{path}"

    scopes = [s.strip() for s in str(args.scopes or "").split(",") if s.strip()]
    if not scopes:
        raise RuntimeError("--scopes must not be empty")

    state = str(args.state).strip() if args.state else secrets.token_urlsafe(12)

    oauth_url = _build_oauth_authorize_url(
        app_id=str(cfg.app_id),
        redirect_uri=redirect_uri,
        scopes=scopes,
        state=state,
    )

    _require_token_write_allowed(ctx)

    # Local HTTP handler to capture the redirect.
    code_event = threading.Event()
    captured: dict[str, str] = {}

    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, fmt: str, *a) -> None:  # noqa: ANN001
            # Silence default noisy HTTP server logs (keep CLI output clean for demos).
            return

        def do_GET(self) -> None:  # noqa: N802
            try:
                if urlparse(self.path).path != path:
                    self.send_response(404)
                    self.end_headers()
                    self.wfile.write(b"Not found")
                    return
                qs = parse_qs(urlparse(self.path).query)
                if "error" in qs:
                    captured["error"] = (qs.get("error") or [""])[0]
                    captured["error_description"] = (qs.get("error_description") or [""])[0]
                    self.send_response(400)
                    self.send_header("Content-Type", "text/plain; charset=utf-8")
                    self.end_headers()
                    self.wfile.write(b"Authorization failed. You can close this window.\n")
                    code_event.set()
                    return
                code = (qs.get("code") or [""])[0].strip()
                st = (qs.get("state") or [""])[0].strip()
                if not code:
                    self.send_response(400)
                    self.send_header("Content-Type", "text/plain; charset=utf-8")
                    self.end_headers()
                    self.wfile.write(b"Missing code. You can close this window.\n")
                    return
                if st != state:
                    self.send_response(400)
                    self.send_header("Content-Type", "text/plain; charset=utf-8")
                    self.end_headers()
                    self.wfile.write(b"State mismatch. You can close this window.\n")
                    captured["error"] = "state_mismatch"
                    captured["error_description"] = "OAuth state did not match expected value"
                    code_event.set()
                    return
                captured["code"] = code
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write(
                    b"<!doctype html><meta charset='utf-8'><title>OK</title>"
                    b"<h2>Authorization received</h2>"
                    b"<p>You can close this window and return to the terminal.</p>"
                )
                code_event.set()
            finally:
                # Shutdown the server shortly after handling the callback.
                threading.Thread(target=server.shutdown, daemon=True).start()

    server = ThreadingHTTPServer((u.hostname, u.port), Handler)

    # Start server thread.
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()

    print(f"[auth] Listening on {redirect_uri} ...", file=sys.stderr)
    print(f"[auth] Open this URL to authorize: {oauth_url}", file=sys.stderr)
    if not bool(args.no_open_browser):
        try:
            import webbrowser

            webbrowser.open(oauth_url)
        except Exception:
            # If opening fails (headless), user can still copy/paste the URL.
            pass

    if not code_event.wait(timeout=float(args.wait_timeout_s)):
        raise RuntimeError("Timed out waiting for OAuth redirect; re-run and try again")

    if "error" in captured:
        raise RuntimeError(f"OAuth failed: {captured.get('error')}: {captured.get('error_description')}".strip(": "))

    code = captured.get("code", "").strip()
    if not code:
        raise RuntimeError("OAuth failed: missing authorization code")

    data = _exchange_authorization_code(
        base_url=cfg.base_url,
        http=ctx["http"],
        app_id=str(cfg.app_id),
        app_secret=str(cfg.app_secret),
        code=code,
        redirect_uri=redirect_uri,
        continuous_refresh=bool(args.continuous_refresh),
    )

    if not isinstance(data.get("access_token"), str) or not data["access_token"].strip():
        raise RuntimeError("Token exchange response missing access_token")
    if not isinstance(data.get("refresh_token"), str) or not data["refresh_token"].strip():
        raise RuntimeError("Token exchange response missing refresh_token")

    # Best-effort: compute expires_at if expires_in exists.
    if isinstance(data.get("expires_in"), (int, float)):
        data["expires_at"] = int(time.time()) + int(data["expires_in"])

    dest = token_path_for_env_file(ctx["env_file"])
    st = write_token_dict(
        data={
            "access_token": data.get("access_token"),
            "refresh_token": data.get("refresh_token"),
            "expires_at": data.get("expires_at"),
            "scope": data.get("scope"),
            "token_type": data.get("token_type"),
        },
        dest_file=dest,
    )

    # Keep refresh token in `.env` for long-term use (gitignored).
    _upsert_env_var(ctx["env_file"], "PINTEREST_REFRESH_TOKEN", str(data.get("refresh_token")))
    _upsert_env_var(ctx["env_file"], "PINTEREST_APP_ID", str(cfg.app_id))

    # Proof of Pinterest integration: fetch user account after login.
    api = PinterestApi(
        base_url=cfg.base_url,
        http=ctx["http"],
        access_token=resolve_access_token(
            env_file=ctx["env_file"],
            env_access_token=cfg.access_token,
            env_refresh_token=cfg.refresh_token,
            app_id=cfg.app_id,
            app_secret=cfg.app_secret,
            base_url=cfg.base_url,
            http=ctx["http"],
        ),
    )
    user = api.get("/user_account")

    out = {
        "ok": True,
        "oauth_url": oauth_url,
        "redirect_uri": redirect_uri,
        "token_status": st.__dict__,
        "token_safe": redact_token_dict(data),
        "user_account": user,
        **_token_no_snapshot_fields(
            ctx,
            action="auth.login",
            operations=[{"method": "POST", "path": "/oauth/token"}, {"method": "GET", "path": "/user_account"}],
        ),
    }
    ctx["audit"].write("auth.login", {"redirect_uri": redirect_uri, "stored_to": st.path})
    ctx["out"].emit(out)
    return 0
