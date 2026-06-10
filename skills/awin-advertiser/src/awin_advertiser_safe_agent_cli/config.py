from __future__ import annotations

import dataclasses
import os
from pathlib import Path

CORE_API_HOST = "https://api.awin.com"


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
    base_url: str
    token: str | None
    advertiser_id: str | None
    timeout_s: float



def load_config(env_file: str | None) -> Config:
    env = _parse_env_file(Path(env_file or ".env"))

    base_url = (_get(env, "AWIN_API_BASE_URL") or CORE_API_HOST).rstrip("/")
    token = _get(env, "AWIN_API_TOKEN") or None
    advertiser_id = _get(env, "AWIN_ADVERTISER_ID") or None

    timeout_s_raw = _get(env, "AWIN_API_TIMEOUT_S") or "30"
    try:
        timeout_s = float(timeout_s_raw)
    except Exception:
        raise RuntimeError("AWIN_API_TIMEOUT_S must be a number (seconds)") from None

    if timeout_s <= 0:
        raise RuntimeError("AWIN_API_TIMEOUT_S must be > 0")

    return Config(base_url=base_url, token=token, advertiser_id=advertiser_id, timeout_s=timeout_s)
