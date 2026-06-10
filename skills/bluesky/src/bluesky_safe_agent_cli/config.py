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
        k, v = line.split("=", 1)
        k = k.strip()
        v = v.strip().strip("'").strip('"')
        if k:
            out[k] = v
    return out


def _get(env: dict[str, str], key: str) -> str:
    # OS env overrides env-file.
    return (os.environ.get(key) if key in os.environ else env.get(key) or "").strip()


@dataclasses.dataclass(frozen=True)
class Config:
    base_url: str
    token: str | None
    timeout_s: float
    entryway_url: str
    public_api_url: str
    appview_url: str
    chat_url: str
    ozone_url: str
    relay_url: str
    labeler_url: str
    default_pds_url: str | None
    identifier: str | None
    app_password: str | None
    access_jwt: str | None
    refresh_jwt: str | None
    admin_token: str | None


def load_config(env_file: str | None) -> Config:
    env = _parse_env_file(Path(env_file or ".env"))

    entryway_url = (_get(env, "BLUESKY_ENTRYWAY_URL") or "https://bsky.social").rstrip("/")
    public_api_url = (_get(env, "BLUESKY_PUBLIC_API_URL") or "https://public.api.bsky.app").rstrip("/")
    appview_url = (_get(env, "BLUESKY_APPVIEW_URL") or "https://api.bsky.app").rstrip("/")
    chat_url = (_get(env, "BLUESKY_CHAT_URL") or "https://api.bsky.chat").rstrip("/")
    ozone_url = (_get(env, "BLUESKY_OZONE_URL") or "https://mod.bsky.app").rstrip("/")
    relay_url = (_get(env, "BLUESKY_RELAY_URL") or "https://bsky.network").rstrip("/")
    labeler_url = (_get(env, "BLUESKY_LABELER_URL") or ozone_url).rstrip("/")
    default_pds_url = _get(env, "BLUESKY_PDS_URL").rstrip("/") or None
    identifier = _get(env, "BLUESKY_IDENTIFIER") or None
    app_password = _get(env, "BLUESKY_APP_PASSWORD") or None
    access_jwt = _get(env, "BLUESKY_ACCESS_JWT") or None
    refresh_jwt = _get(env, "BLUESKY_REFRESH_JWT") or None
    admin_token = _get(env, "BLUESKY_ADMIN_TOKEN") or None

    timeout_s_raw = _get(env, "BLUESKY_TIMEOUT_S") or "30"
    try:
        timeout_s = float(timeout_s_raw)
    except Exception:
        raise RuntimeError("BLUESKY_TIMEOUT_S must be a number (seconds)") from None

    if timeout_s <= 0:
        raise RuntimeError("BLUESKY_TIMEOUT_S must be > 0")

    return Config(
        base_url=entryway_url,
        token=access_jwt or admin_token,
        timeout_s=timeout_s,
        entryway_url=entryway_url,
        public_api_url=public_api_url,
        appview_url=appview_url,
        chat_url=chat_url,
        ozone_url=ozone_url,
        relay_url=relay_url,
        labeler_url=labeler_url,
        default_pds_url=default_pds_url,
        identifier=identifier,
        app_password=app_password,
        access_jwt=access_jwt,
        refresh_jwt=refresh_jwt,
        admin_token=admin_token,
    )
