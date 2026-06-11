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
    raw = os.environ.get(key) if key in os.environ else env.get(key)
    return (raw or "").strip()


@dataclasses.dataclass(frozen=True)
class Config:
    commerce_secret_key: str | None
    commerce_site_api_key: str | None
    advertising_api_key: str | None
    advertising_publisher_id: str | None
    timeout_s: float

    @property
    def env_fingerprint(self) -> str:
        parts = [
            f"commerce_secret={int(bool(self.commerce_secret_key))}",
            f"commerce_site_key={int(bool(self.commerce_site_api_key))}",
            f"advertising_key={int(bool(self.advertising_api_key))}",
            f"advertising_publisher={int(bool(self.advertising_publisher_id))}",
        ]
        return "|".join(parts)


def load_config(env_file: str | None) -> Config:
    env = _parse_env_file(Path(env_file or ".env"))

    commerce_secret_key = _get(env, "SOVRN_COMMERCE_SECRET_KEY") or None
    commerce_site_api_key = _get(env, "SOVRN_COMMERCE_SITE_API_KEY") or None
    advertising_api_key = _get(env, "SOVRN_ADVERTISING_API_KEY") or None
    advertising_publisher_id = _get(env, "SOVRN_ADVERTISING_PUBLISHER_ID") or None

    timeout_s_raw = _get(env, "SOVRN_TIMEOUT_S") or "30"
    try:
        timeout_s = float(timeout_s_raw)
    except Exception:
        raise RuntimeError("SOVRN_TIMEOUT_S must be a number (seconds)") from None

    if timeout_s <= 0:
        raise RuntimeError("SOVRN_TIMEOUT_S must be > 0")

    return Config(
        commerce_secret_key=commerce_secret_key,
        commerce_site_api_key=commerce_site_api_key,
        advertising_api_key=advertising_api_key,
        advertising_publisher_id=advertising_publisher_id,
        timeout_s=timeout_s,
    )
