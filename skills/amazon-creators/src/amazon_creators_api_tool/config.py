from __future__ import annotations

import dataclasses
import hmac
import json
import os
from pathlib import Path

from .errors import ValidationError
from .token_urls import default_token_url

DEFAULT_BASE_URL = "https://creatorsapi.amazon/catalog/v1"
REQUIRED_SETTINGS = {
    "AMAZON_CREATORS_CREDENTIAL_ID": "",
    "AMAZON_CREATORS_CREDENTIAL_SECRET": "",
    "AMAZON_CREATORS_CREDENTIAL_VERSION": "",
    "AMAZON_CREATORS_LOCALE": "en_US",
    "AMAZON_CREATORS_PARTNER_TAG": "",
}


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
    # A named file selects one account. The default still accepts shell settings.
    return out if env_file is not None else {**out, **os.environ}


@dataclasses.dataclass(frozen=True)
class Config:
    base_url: str
    credential_id: str
    credential_secret: str
    credential_version: str
    locale: str
    timeout_s: float
    token_url: str | None
    partner_tag: str

    @property
    def token_endpoint(self) -> str:
        return self.token_url or default_token_url(self.credential_version, self.locale)

    @property
    def account_fingerprint(self) -> str:
        identity = json.dumps([self.credential_id, self.credential_version, self.token_endpoint])
        return hmac.digest(self.credential_secret.encode(), identity.encode(), "sha256").hex()


def load_config(env_file: str | None) -> Config:
    env = read_settings(env_file)

    def setting(name: str, default: str = "") -> str:
        return env.get(f"AMAZON_CREATORS_{name}", default).strip()

    base_url = (setting("API_BASE_URL") or DEFAULT_BASE_URL).rstrip("/")
    credential_id = setting("CREDENTIAL_ID")
    credential_secret = setting("CREDENTIAL_SECRET")
    credential_version = setting("CREDENTIAL_VERSION")
    locale = setting("LOCALE")
    token_url = setting("TOKEN_URL") or None
    partner_tag = setting("PARTNER_TAG")

    timeout_s_raw = setting("TIMEOUT_S") or "30"
    try:
        timeout_s = float(timeout_s_raw)
    except Exception:
        raise RuntimeError("AMAZON_CREATORS_TIMEOUT_S must be a number (seconds)") from None

    if not credential_id:
        raise RuntimeError("Missing AMAZON_CREATORS_CREDENTIAL_ID")
    if not credential_secret:
        raise RuntimeError("Missing AMAZON_CREATORS_CREDENTIAL_SECRET")
    if not credential_version:
        raise RuntimeError("Missing AMAZON_CREATORS_CREDENTIAL_VERSION")
    if not locale:
        raise RuntimeError("Missing AMAZON_CREATORS_LOCALE")
    if not partner_tag:
        raise RuntimeError("Missing AMAZON_CREATORS_PARTNER_TAG")
    if timeout_s <= 0:
        raise RuntimeError("AMAZON_CREATORS_TIMEOUT_S must be > 0")

    return Config(
        base_url=base_url,
        credential_id=credential_id,
        credential_secret=credential_secret,
        credential_version=credential_version,
        locale=locale,
        timeout_s=timeout_s,
        token_url=token_url,
        partner_tag=partner_tag,
    )
