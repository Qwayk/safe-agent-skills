from __future__ import annotations

import dataclasses
import os
from pathlib import Path

from .errors import ValidationError


def read_settings(env_file: str | None, *, allow_missing: bool = False) -> dict[str, str]:
    path = Path(env_file or ".env")
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        if env_file is not None and not allow_missing:
            raise ValidationError(f"Settings file not found: {path}. Run onboarding for this file.") from None
        lines = []
    out: dict[str, str] = {}
    for raw in lines:
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
    # A named file selects one account. Keep the existing shell overrides for the default setup.
    return out if env_file is not None else {**out, **os.environ}


def _get(env: dict[str, str], key: str) -> str:
    return env.get(key, "").strip()


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
    def credentials(self) -> tuple[str, ...]:
        return tuple(
            value
            for value in (self.client_id, self.client_secret, self.product_client_id, self.product_client_secret)
            if value
        )

    @property
    def env_fingerprint(self) -> str:
        publisher = self.publisher_id or "no-publisher"
        domain = self.publisher_domain_id or "no-domain"
        return f"skimlinks:{publisher}:{domain}"


def load_config(env_file: str | None) -> Config:
    env = read_settings(env_file)

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
