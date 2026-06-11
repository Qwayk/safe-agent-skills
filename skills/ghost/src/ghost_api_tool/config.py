from __future__ import annotations

import dataclasses
import os
import re
from pathlib import Path

from .errors import ValidationError


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
    admin_api_url: str
    admin_api_key: str
    accept_version: str
    timeout_s: float


@dataclasses.dataclass(frozen=True)
class ContentConfig:
    content_api_url: str
    content_api_key: str
    accept_version: str
    timeout_s: float


def _load_accept_version_and_timeout(env: dict[str, str]) -> tuple[str, float]:
    accept_version = _get(env, "GHOST_ACCEPT_VERSION")
    timeout_s_raw = _get(env, "GHOST_TIMEOUT_S")

    if not accept_version:
        raise ValidationError(
            "Missing GHOST_ACCEPT_VERSION (example: v5.0). Usually you can keep the default from .env.example."
        )
    if not re.fullmatch(r"v\d+\.\d+", accept_version):
        raise ValidationError("GHOST_ACCEPT_VERSION must look like v{major}.{minor} (e.g. v5.0)")

    timeout_s = 30.0
    if timeout_s_raw:
        try:
            timeout_s = float(timeout_s_raw)
        except Exception:
            raise ValidationError("GHOST_TIMEOUT_S must be a number (seconds)") from None
    if timeout_s <= 0:
        raise ValidationError("GHOST_TIMEOUT_S must be > 0")

    return accept_version, timeout_s


def load_config(env_file: str | None) -> Config:
    env = _parse_env_file(Path(env_file or ".env"))

    admin_api_url = _get(env, "GHOST_ADMIN_API_URL")
    admin_api_key = _get(env, "GHOST_ADMIN_API_KEY")
    accept_version, timeout_s = _load_accept_version_and_timeout(env)

    if not admin_api_url:
        raise ValidationError(
            "Missing GHOST_ADMIN_API_URL. Create a local .env (copy .env.example) and set GHOST_ADMIN_API_URL to the "
            "exact Admin API base URL (must include /ghost/api/admin/).\n\n"
            "Example:\n"
            "- GHOST_ADMIN_API_URL=https://example.com/ghost/api/admin/\n\n"
            "Tip: in Ghost Admin → Settings → Integrations → your custom integration, copy the “API URL” value "
            "(it can differ from your public website domain) and use that domain.\n\n"
            "Quick help: run `ghost-api-tool onboarding`."
        )
    if not (admin_api_url.startswith("https://") or admin_api_url.startswith("http://")):
        raise ValidationError(
            "GHOST_ADMIN_API_URL must start with https:// or http:// "
            "(example: https://YOUR_DOMAIN/ghost/api/admin/)."
        )
    admin_api_url = admin_api_url.rstrip("/") + "/"

    if "/ghost/api/admin/" not in admin_api_url:
        raise ValidationError("GHOST_ADMIN_API_URL must include /ghost/api/admin/ (full base URL)")

    if not admin_api_key:
        raise ValidationError(
            "Missing GHOST_ADMIN_API_KEY. In Ghost Admin: Settings → Integrations → Add custom integration → "
            "copy the Admin API Key (it looks like id:secret) and paste it into your local .env."
        )
    if ":" not in admin_api_key:
        raise ValidationError("GHOST_ADMIN_API_KEY must be in id:secret format")

    return Config(
        admin_api_url=admin_api_url,
        admin_api_key=admin_api_key,
        accept_version=accept_version,
        timeout_s=timeout_s,
    )


def load_content_config(env_file: str | None) -> ContentConfig:
    env = _parse_env_file(Path(env_file or ".env"))

    content_api_url = _get(env, "GHOST_CONTENT_API_URL")
    content_api_key = _get(env, "GHOST_CONTENT_API_KEY")
    accept_version, timeout_s = _load_accept_version_and_timeout(env)

    if not content_api_url:
        raise ValidationError(
            "Missing GHOST_CONTENT_API_URL. Create a local .env (copy .env.example) and set GHOST_CONTENT_API_URL to the "
            "exact Content API base URL (must include /ghost/api/content/).\n\n"
            "Example:\n"
            "- GHOST_CONTENT_API_URL=https://example.com/ghost/api/content/\n\n"
            "Tip: in Ghost Admin → Settings → Integrations → your custom integration, copy the “API URL” value "
            "(it can differ from your public website domain) and use that domain.\n\n"
            "Quick help: run `ghost-api-tool onboarding`."
        )
    if not (content_api_url.startswith("https://") or content_api_url.startswith("http://")):
        raise ValidationError(
            "GHOST_CONTENT_API_URL must start with https:// or http:// "
            "(example: https://YOUR_DOMAIN/ghost/api/content/)."
        )
    content_api_url = content_api_url.rstrip("/") + "/"
    if "/ghost/api/content/" not in content_api_url:
        raise ValidationError("GHOST_CONTENT_API_URL must include /ghost/api/content/ (full base URL)")

    if not content_api_key:
        raise ValidationError(
            "Missing GHOST_CONTENT_API_KEY. In Ghost Admin: Settings → Integrations → Add custom integration → "
            "copy the Content API Key and paste it into your local .env."
        )

    return ContentConfig(
        content_api_url=content_api_url,
        content_api_key=content_api_key,
        accept_version=accept_version,
        timeout_s=timeout_s,
    )
