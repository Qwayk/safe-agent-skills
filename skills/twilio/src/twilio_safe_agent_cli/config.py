from __future__ import annotations

import dataclasses
import hashlib
import os
from pathlib import Path

from .errors import ValidationError


def _parse_env_file(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    values: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[7:].strip()
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip("'").strip('"')
    return values


def _value(values: dict[str, str], key: str) -> str | None:
    raw = os.environ.get(key, values.get(key, "")).strip()
    return raw or None


@dataclasses.dataclass(frozen=True)
class Config:
    account_sid: str
    api_key_sid: str | None
    api_key_secret: str | None
    auth_token: str | None
    oauth_access_token: str | None
    region: str | None
    edge: str | None
    timeout_s: float

    @property
    def fingerprint(self) -> str:
        material = "|".join(
            (
                self.account_sid,
                self.region or "us1",
                self.edge or "auto",
                self.api_key_sid or "",
                self.oauth_access_token or "",
            )
        )
        return hashlib.sha256(material.encode("utf-8")).hexdigest()

    def redaction_values(self) -> list[str]:
        return [
            value
            for value in (
                self.account_sid,
                self.api_key_sid,
                self.api_key_secret,
                self.auth_token,
                self.oauth_access_token,
            )
            if value
        ]


def load_config(
    env_file: str | Path = ".env",
    *,
    require_account: bool = True,
    require_credentials: bool = True,
) -> Config:
    values = _parse_env_file(Path(env_file).expanduser())
    configured_account_sid = _value(values, "TWILIO_ACCOUNT_SID")
    if require_account and not configured_account_sid:
        raise ValidationError("Missing TWILIO_ACCOUNT_SID")
    if configured_account_sid and (
        not configured_account_sid.startswith("AC") or len(configured_account_sid) != 34
    ):
        raise ValidationError("TWILIO_ACCOUNT_SID must be a 34-character Account SID")
    account_sid = configured_account_sid or "UNSCOPED"

    key_sid = _value(values, "TWILIO_API_KEY_SID")
    key_secret = _value(values, "TWILIO_API_KEY_SECRET")
    auth_token = _value(values, "TWILIO_AUTH_TOKEN")
    oauth_token = _value(values, "TWILIO_OAUTH_ACCESS_TOKEN")
    if bool(key_sid) != bool(key_secret):
        raise ValidationError("TWILIO_API_KEY_SID and TWILIO_API_KEY_SECRET must be set together")
    if key_sid and (not key_sid.startswith("SK") or len(key_sid) != 34):
        raise ValidationError("TWILIO_API_KEY_SID must be a 34-character API key SID")
    if require_credentials and not (key_sid and key_secret) and not auth_token and not oauth_token:
        raise ValidationError(
            "Missing Twilio credentials: use an API key SID and secret, or the warned Auth Token fallback"
        )

    region = _value(values, "TWILIO_REGION")
    edge = _value(values, "TWILIO_EDGE")
    if bool(region) != bool(edge):
        raise ValidationError("TWILIO_REGION and TWILIO_EDGE must be set together")

    raw_timeout = _value(values, "TWILIO_TIMEOUT_S") or "30"
    try:
        timeout_s = float(raw_timeout)
    except ValueError:
        raise ValidationError("TWILIO_TIMEOUT_S must be a number") from None
    if timeout_s <= 0:
        raise ValidationError("TWILIO_TIMEOUT_S must be greater than zero")

    return Config(
        account_sid=account_sid,
        api_key_sid=key_sid,
        api_key_secret=key_secret,
        auth_token=auth_token,
        oauth_access_token=oauth_token,
        region=region,
        edge=edge,
        timeout_s=timeout_s,
    )
