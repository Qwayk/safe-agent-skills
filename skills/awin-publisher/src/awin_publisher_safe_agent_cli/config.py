from __future__ import annotations

import dataclasses
import os
from pathlib import Path

from .errors import ValidationError


CORE_API_HOST = "https://api.awin.com"
LEGACY_FEED_HOST = "https://productdata.awin.com"


def _parse_env_file(path: Path, *, required: bool) -> dict[str, str]:
    if (required or path.exists()) and not path.is_file():
        raise ValidationError(f"Settings file must be an existing regular file: {path}")
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


@dataclasses.dataclass(frozen=True)
class Config:
    token: str | None
    proof_of_purchase_api_key: str | None
    feed_api_key: str | None
    timeout_s: float

    @property
    def api_host(self) -> str:
        return CORE_API_HOST

    @property
    def legacy_feed_host(self) -> str:
        return LEGACY_FEED_HOST

    def proof_of_purchase_api_key_or_token(self) -> str | None:
        return self.proof_of_purchase_api_key or self.token


def load_config(env_file: str | None, *, file_only: bool = False, require_file: bool = False) -> Config:
    env = _parse_env_file(Path(env_file or ".env").expanduser(), required=require_file)
    if not file_only:
        env.update({key: value.strip() for key, value in os.environ.items() if key.startswith("AWIN_")})

    token = env.get("AWIN_API_TOKEN") or None
    proof_of_purchase_api_key = env.get("AWIN_PROOF_OF_PURCHASE_API_KEY") or None
    feed_api_key = env.get("AWIN_FEED_API_KEY") or None

    timeout_s_raw = env.get("AWIN_TIMEOUT_S") or "30"
    try:
        timeout_s = float(timeout_s_raw)
    except Exception:
        raise RuntimeError("AWIN_TIMEOUT_S must be a number (seconds)") from None

    if timeout_s <= 0:
        raise RuntimeError("AWIN_TIMEOUT_S must be > 0")

    return Config(
        token=token,
        proof_of_purchase_api_key=proof_of_purchase_api_key,
        feed_api_key=feed_api_key,
        timeout_s=timeout_s,
    )
