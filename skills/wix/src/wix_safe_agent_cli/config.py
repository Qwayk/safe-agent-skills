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
    app_id: str | None
    app_secret: str | None
    instance_id: str | None
    access_token: str | None
    api_key: str | None
    account_id: str | None
    timeout_s: float

    @property
    def has_official_app_auth(self) -> bool:
        return bool(self.app_id and self.app_secret and self.instance_id)

    @property
    def has_account_api_auth(self) -> bool:
        return bool(self.api_key and self.account_id)


def load_config(env_file: str | None) -> Config:
    env = _parse_env_file(Path(env_file or ".env"))

    base_url = (_get(env, "WIX_API_BASE_URL") or "https://www.wixapis.com").rstrip("/")
    app_id = _get(env, "WIX_APP_ID") or None
    app_secret = _get(env, "WIX_APP_SECRET") or None
    instance_id = _get(env, "WIX_INSTANCE_ID") or None
    access_token = _get(env, "WIX_ACCESS_TOKEN") or None
    api_key = _get(env, "WIX_API_KEY") or None
    account_id = _get(env, "WIX_ACCOUNT_ID") or None

    timeout_s_raw = _get(env, "WIX_TIMEOUT_S") or "30"
    try:
        timeout_s = float(timeout_s_raw)
    except Exception:
        raise RuntimeError("WIX_TIMEOUT_S must be a number (seconds)") from None

    if timeout_s <= 0:
        raise RuntimeError("WIX_TIMEOUT_S must be > 0")

    return Config(
        base_url=base_url,
        app_id=app_id,
        app_secret=app_secret,
        instance_id=instance_id,
        access_token=access_token,
        api_key=api_key,
        account_id=account_id,
        timeout_s=timeout_s,
    )
