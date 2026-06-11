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
    shop_domain: str
    admin_access_token: str
    api_version: str
    timeout_s: float


def load_config(env_file: str | None) -> Config:
    env = _parse_env_file(Path(env_file or ".env"))

    shop_domain = _get(env, "SHOPIFY_SHOP_DOMAIN").strip()
    admin_access_token = _get(env, "SHOPIFY_ADMIN_ACCESS_TOKEN").strip()
    api_version = _get(env, "SHOPIFY_ADMIN_API_VERSION").strip()

    timeout_s_raw = _get(env, "SHOPIFY_TIMEOUT_S") or "30"
    try:
        timeout_s = float(timeout_s_raw)
    except Exception:
        raise RuntimeError("SHOPIFY_TIMEOUT_S must be a number (seconds)") from None

    if not shop_domain:
        raise RuntimeError("Missing SHOPIFY_SHOP_DOMAIN (example: your-shop.myshopify.com)")
    if not admin_access_token:
        raise RuntimeError("Missing SHOPIFY_ADMIN_ACCESS_TOKEN")
    if not api_version:
        raise RuntimeError("Missing SHOPIFY_ADMIN_API_VERSION (example: 2026-01)")
    if timeout_s <= 0:
        raise RuntimeError("SHOPIFY_TIMEOUT_S must be > 0")

    # Normalize shop domain (no scheme/path).
    shop_domain = shop_domain.removeprefix("https://").removeprefix("http://").strip().strip("/")

    return Config(
        shop_domain=shop_domain,
        admin_access_token=admin_access_token,
        api_version=api_version,
        timeout_s=timeout_s,
    )
