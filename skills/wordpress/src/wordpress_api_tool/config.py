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
        key, val = line.split("=", 1)
        key = key.strip()
        val = val.strip().strip("'").strip('"')
        if key:
            out[key] = val
    return out


def _get(env: dict[str, str], key: str) -> str:
    # OS env overrides env-file.
    return (os.environ.get(key) if key in os.environ else env.get(key) or "").strip()


@dataclasses.dataclass(frozen=True)
class Config:
    base_url: str
    username: str
    app_password: str


def load_config(env_file: str | None) -> Config:
    env = _parse_env_file(Path(env_file or ".env"))

    base_url = _get(env, "WP_BASE_URL").rstrip("/")
    username = _get(env, "WP_USERNAME")
    app_password = _get(env, "WP_APP_PASSWORD")

    if not base_url:
        raise RuntimeError("Missing WP_BASE_URL (e.g. https://example.com)")
    if "/wp-json" in base_url:
        # Allow users to paste a full API URL; normalize back to the site root.
        base_url = base_url.split("/wp-json", 1)[0].rstrip("/")
    if not (base_url.startswith("https://") or base_url.startswith("http://")):
        raise RuntimeError("WP_BASE_URL must start with https:// or http:// (e.g. https://example.com)")
    if not username:
        raise RuntimeError("Missing WP_USERNAME")
    if not app_password:
        raise RuntimeError("Missing WP_APP_PASSWORD (WordPress Application Password)")

    # Application passwords are often shown with spaces; normalize.
    app_password = app_password.replace(" ", "")

    return Config(base_url=base_url, username=username, app_password=app_password)
