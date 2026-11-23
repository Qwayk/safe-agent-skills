from __future__ import annotations

import dataclasses
import os
from pathlib import Path

CORE_API_HOST = "https://api.awin.com"
ENV_TEMPLATE = f"AWIN_API_BASE_URL={CORE_API_HOST}\nAWIN_API_TOKEN=\nAWIN_ADVERTISER_ID=\n"


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


@dataclasses.dataclass(frozen=True)
class Config:
    base_url: str
    token: str | None
    advertiser_id: str | None
    timeout_s: float


def load_config(env_file: str | None) -> Config:
    env = settings_values(env_file)

    base_url = (env.get("AWIN_API_BASE_URL") or CORE_API_HOST).rstrip("/")
    token = env.get("AWIN_API_TOKEN") or None
    advertiser_id = env.get("AWIN_ADVERTISER_ID") or None

    timeout_s_raw = env.get("AWIN_API_TIMEOUT_S") or "30"
    try:
        timeout_s = float(timeout_s_raw)
    except Exception:
        raise RuntimeError("AWIN_API_TIMEOUT_S must be a number (seconds)") from None

    if timeout_s <= 0:
        raise RuntimeError("AWIN_API_TIMEOUT_S must be > 0")

    return Config(base_url=base_url, token=token, advertiser_id=advertiser_id, timeout_s=timeout_s)


def settings_values(env_file: str | None) -> dict[str, str]:
    values = _parse_env_file(Path(env_file or ".env"))
    if env_file is None:
        values.update((key, value.strip()) for key, value in os.environ.items() if key.startswith("AWIN_"))
    return values
