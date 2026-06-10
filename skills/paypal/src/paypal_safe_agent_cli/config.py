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
    environment: str
    base_url: str
    client_id: str | None
    client_secret: str | None
    access_token: str | None
    partner_attribution_id: str | None
    auth_assertion: str | None
    accept_language: str | None
    timeout_s: float


def _default_base_url(environment: str) -> str:
    if environment == "sandbox":
        return "https://api-m.sandbox.paypal.com"
    if environment == "live":
        return "https://api-m.paypal.com"
    raise RuntimeError("PAYPAL_ENVIRONMENT must be either sandbox or live")


def load_config(env_file: str | None) -> Config:
    env = _parse_env_file(Path(env_file or ".env"))

    environment = (_get(env, "PAYPAL_ENVIRONMENT") or "sandbox").lower()
    base_url = (_get(env, "PAYPAL_API_BASE_URL") or _default_base_url(environment)).rstrip("/")
    client_id = _get(env, "PAYPAL_CLIENT_ID") or None
    client_secret = _get(env, "PAYPAL_CLIENT_SECRET") or None
    access_token = _get(env, "PAYPAL_ACCESS_TOKEN") or None
    partner_attribution_id = _get(env, "PAYPAL_PARTNER_ATTRIBUTION_ID") or None
    auth_assertion = _get(env, "PAYPAL_AUTH_ASSERTION") or None
    accept_language = _get(env, "PAYPAL_ACCEPT_LANGUAGE") or None

    timeout_s_raw = _get(env, "PAYPAL_TIMEOUT_S") or "30"
    try:
        timeout_s = float(timeout_s_raw)
    except Exception:
        raise RuntimeError("PAYPAL_TIMEOUT_S must be a number (seconds)") from None

    if timeout_s <= 0:
        raise RuntimeError("PAYPAL_TIMEOUT_S must be > 0")
    if not access_token and (not client_id or not client_secret):
        raise RuntimeError(
            "Missing PayPal credentials. Set PAYPAL_CLIENT_ID and PAYPAL_CLIENT_SECRET, "
            "or provide PAYPAL_ACCESS_TOKEN for advanced manual use."
        )

    return Config(
        environment=environment,
        base_url=base_url,
        client_id=client_id,
        client_secret=client_secret,
        access_token=access_token,
        partner_attribution_id=partner_attribution_id,
        auth_assertion=auth_assertion,
        accept_language=accept_language,
        timeout_s=timeout_s,
    )
