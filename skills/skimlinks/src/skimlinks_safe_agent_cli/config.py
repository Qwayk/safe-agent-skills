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
    value = os.environ[key] if key in os.environ else env.get(key, "")
    return value.strip()


@dataclasses.dataclass(frozen=True)
class Config:
    auth_url: str
    merchant_base_url: str
    reporting_base_url: str
    product_base_url: str
    link_wrapper_base_url: str
    client_id: str | None
    client_secret: str | None
    product_client_id: str | None
    product_client_secret: str | None
    publisher_id: str | None
    publisher_domain_id: str | None
    link_wrapper_id: str | None
    timeout_s: float

    @property
    def env_fingerprint(self) -> str:
        publisher = self.publisher_id or "no-publisher"
        domain = self.publisher_domain_id or "no-domain"
        return f"skimlinks:{publisher}:{domain}"


def load_config(env_file: str | None) -> Config:
    env = _parse_env_file(Path(env_file or ".env"))

    timeout_s_raw = _get(env, "SKIMLINKS_TIMEOUT_S") or "30"
    try:
        timeout_s = float(timeout_s_raw)
    except Exception:
        raise RuntimeError("SKIMLINKS_TIMEOUT_S must be a number (seconds)") from None

    if timeout_s <= 0:
        raise RuntimeError("SKIMLINKS_TIMEOUT_S must be > 0")

    return Config(
        auth_url=(
            _get(env, "SKIMLINKS_AUTH_URL") or "https://authentication.skimapis.com/access_token"
        ).rstrip("/"),
        merchant_base_url=(
            _get(env, "SKIMLINKS_MERCHANT_BASE_URL") or "https://merchants.skimapis.com"
        ).rstrip("/"),
        reporting_base_url=(
            _get(env, "SKIMLINKS_REPORTING_BASE_URL") or "https://reporting.skimapis.com"
        ).rstrip("/"),
        product_base_url=(
            _get(env, "SKIMLINKS_PRODUCT_BASE_URL") or "https://products.skimapis.com"
        ).rstrip("/"),
        link_wrapper_base_url=(
            _get(env, "SKIMLINKS_LINK_WRAPPER_BASE_URL") or "https://go.skimresources.com/"
        ),
        client_id=_get(env, "SKIMLINKS_CLIENT_ID") or None,
        client_secret=_get(env, "SKIMLINKS_CLIENT_SECRET") or None,
        product_client_id=_get(env, "SKIMLINKS_PRODUCT_CLIENT_ID") or None,
        product_client_secret=_get(env, "SKIMLINKS_PRODUCT_CLIENT_SECRET") or None,
        publisher_id=_get(env, "SKIMLINKS_PUBLISHER_ID") or None,
        publisher_domain_id=_get(env, "SKIMLINKS_PUBLISHER_DOMAIN_ID") or None,
        link_wrapper_id=_get(env, "SKIMLINKS_LINK_WRAPPER_ID") or None,
        timeout_s=timeout_s,
    )
