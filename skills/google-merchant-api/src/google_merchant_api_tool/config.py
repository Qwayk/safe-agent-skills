from __future__ import annotations

import dataclasses
import os
from pathlib import Path


def _parse_env_file(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}

    out: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export ") :].strip()
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip("'").strip('"')
        if key:
            out[key] = value
    return out


def _looks_like_placeholder(raw: str | None) -> bool:
    text = (raw or "").strip()
    if not text:
        return True
    lowered = text.lower()
    if lowered in {"<todo>", "todo", "todo!", "replace_me", "replace-me", "replace with value", "your_value_here", "your_secret_here", "your_client_id", "your_client_secret", "your token here", "your_refresh_token"}:
        return True
    if (lowered.startswith("<") and lowered.endswith(">")) or "replace-me" in lowered or "replace_me" in lowered:
        return True
    return False


def _first_non_empty(*values: str | None) -> str:
    for value in values:
        candidate = (value or "").strip()
        if _looks_like_placeholder(candidate):
            continue
        if candidate:
            return candidate
    return ""


def _get(env: dict[str, str], key: str) -> str:
    # OS env overrides env-file.
    return (os.environ.get(key) if key in os.environ else env.get(key) or "").strip()


def _parse_scopes(raw: str | None) -> tuple[str, ...]:
    values = [item.strip() for item in (raw or "").split(",") if item.strip()]
    if not values:
        return ("https://www.googleapis.com/auth/content",)
    return tuple(dict.fromkeys(values))


@dataclasses.dataclass(frozen=True)
class Config:
    base_url: str
    auth_mode: str
    service_account_json: str | None
    oauth_refresh_token: str | None
    oauth_client_id: str | None
    oauth_client_secret: str | None
    oauth_token_uri: str | None
    oauth_scopes: tuple[str, ...]
    timeout_s: float

    @property
    def merchant_api_base_url(self) -> str:
        return self.base_url


def load_config(env_file: str | None) -> Config:
    env = _parse_env_file(Path(env_file or ".env"))

    base_url = _first_non_empty(
        _get(env, "GOOGLE_MERCHANT_API_BASE_URL"),
        _get(env, "GOOGLE_MERCHANT_API_API_BASE_URL"),
    ).rstrip("/")
    if not base_url:
        raise RuntimeError("Missing GOOGLE_MERCHANT_API_BASE_URL")

    auth_mode = _first_non_empty(_get(env, "GOOGLE_MERCHANT_API_AUTH_MODE"), "service_account_json").lower()
    service_account_json = _first_non_empty(
        _get(env, "GOOGLE_MERCHANT_API_SERVICE_ACCOUNT_JSON"),
        _get(env, "GOOGLE_MERCHANT_API_SERVICE_ACCOUNT_KEY_PATH"),
    ) or None
    oauth_refresh_token = _first_non_empty(
        _get(env, "GOOGLE_MERCHANT_API_OAUTH_REFRESH_TOKEN"),
        _get(env, "GOOGLE_MERCHANT_API_OAUTH_REFRESH_TOKEN_FILE"),
        _get(env, "GOOGLE_MERCHANT_API_TOKEN_FILE"),
    ) or None
    oauth_client_id = _first_non_empty(_get(env, "GOOGLE_MERCHANT_API_OAUTH_CLIENT_ID"), _get(env, "GOOGLE_MERCHANT_API_CLIENT_ID")) or None
    oauth_client_secret = _first_non_empty(
        _get(env, "GOOGLE_MERCHANT_API_OAUTH_CLIENT_SECRET"),
        _get(env, "GOOGLE_MERCHANT_API_CLIENT_SECRET"),
    ) or None
    oauth_token_uri = _first_non_empty(_get(env, "GOOGLE_MERCHANT_API_OAUTH_TOKEN_URI")) or None
    oauth_scopes = _parse_scopes(_get(env, "GOOGLE_MERCHANT_API_OAUTH_SCOPES"))

    timeout_s_raw = _first_non_empty(_get(env, "GOOGLE_MERCHANT_API_TIMEOUT_S"), "30")
    try:
        timeout_s = float(timeout_s_raw)
    except Exception:
        raise RuntimeError("GOOGLE_MERCHANT_API_TIMEOUT_S must be a number (seconds)") from None

    if timeout_s <= 0:
        raise RuntimeError("GOOGLE_MERCHANT_API_TIMEOUT_S must be > 0")

    return Config(
        base_url=base_url,
        auth_mode=auth_mode,
        service_account_json=service_account_json,
        oauth_refresh_token=oauth_refresh_token,
        oauth_client_id=oauth_client_id,
        oauth_client_secret=oauth_client_secret,
        oauth_token_uri=oauth_token_uri,
        oauth_scopes=oauth_scopes,
        timeout_s=timeout_s,
    )
