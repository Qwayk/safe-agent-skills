from __future__ import annotations

import dataclasses
import hashlib
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
        key, value = line.split("=", 1)
        out[key.strip()] = value.strip().strip("'").strip('"')
    return out


def _get(env: dict[str, str], key: str) -> str:
    return (os.environ.get(key) if key in os.environ else env.get(key) or "").strip()


def _fingerprint_secret(kind: str, value: str) -> str:
    digest = hashlib.sha256(value.encode("utf-8")).hexdigest()[:16]
    return f"{kind}:sha256:{digest}"


@dataclasses.dataclass(frozen=True)
class Config:
    base_url: str
    ai_actions_base_url: str
    trigger_inbox_base_url: str
    access_token: str | None
    client_id: str | None
    client_secret: str | None
    jwt: str | None
    timeout_s: float

    def auth_fingerprint(self) -> str:
        if self.access_token:
            return _fingerprint_secret("access-token", self.access_token)
        if self.jwt:
            return _fingerprint_secret("jwt", self.jwt)
        if self.client_id and self.client_secret:
            return _fingerprint_secret("client-credentials", f"{self.client_id}:{self.client_secret}")
        return "none"


def load_config(env_file: str | None) -> Config:
    env = _parse_env_file(Path(env_file or ".env"))

    base_url = (_get(env, "ZAPIER_BASE_URL") or "https://api.zapier.com").rstrip("/")
    ai_actions_base_url = _get(env, "ZAPIER_AI_ACTIONS_BASE_URL") or "https://actions.zapier.com"
    trigger_inbox_base_url = _get(env, "ZAPIER_TRIGGER_INBOX_BASE_URL") or base_url
    timeout_raw = _get(env, "ZAPIER_TIMEOUT_S") or "30"
    try:
        timeout_s = float(timeout_raw)
    except Exception:
        raise RuntimeError("ZAPIER_TIMEOUT_S must be a number (seconds)") from None

    if timeout_s <= 0:
        raise RuntimeError("ZAPIER_TIMEOUT_S must be > 0")

    access_token = _get(env, "ZAPIER_ACCESS_TOKEN") or None
    client_id = _get(env, "ZAPIER_CLIENT_ID") or None
    client_secret = _get(env, "ZAPIER_CLIENT_SECRET") or None
    jwt = _get(env, "ZAPIER_JWT") or None

    return Config(
        base_url=base_url,
        ai_actions_base_url=ai_actions_base_url.rstrip("/"),
        trigger_inbox_base_url=trigger_inbox_base_url.rstrip("/"),
        access_token=access_token,
        client_id=client_id,
        client_secret=client_secret,
        jwt=jwt,
        timeout_s=timeout_s,
    )
