from __future__ import annotations

import dataclasses
import os
from pathlib import Path

from .errors import ValidationError


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
    profile_name: str | None
    region_name: str
    allowed_accounts: tuple[str, ...]
    allowed_regions: tuple[str, ...]
    timeout_s: float

    @property
    def base_url(self) -> str:
        # Backward-compatible alias for older local commands.
        return self.region_name

    @property
    def token(self) -> str | None:
        # Backward-compatible alias for older local commands.
        return self.profile_name


def _parse_csv_list(raw: str) -> tuple[str, ...]:
    items = [part.strip() for part in raw.split(",")]
    return tuple(item for item in items if item)


def load_config(env_file: str | None) -> Config:
    env = _parse_env_file(Path(env_file or ".env"))

    region_name = _get(env, "AWS_DEFAULT_REGION") or "us-east-1"
    profile_name = _get(env, "AWS_PROFILE") or None
    allowed_accounts = _parse_csv_list(_get(env, "AWS_ALLOWED_ACCOUNTS"))
    allowed_regions = _parse_csv_list(_get(env, "AWS_ALLOWED_REGIONS"))

    timeout_s_raw = _get(env, "AWS_TIMEOUT_S") or "30"
    try:
        timeout_s = float(timeout_s_raw)
    except Exception:
        raise ValidationError("AWS_TIMEOUT_S must be a number (seconds)") from None

    if timeout_s <= 0:
        raise ValidationError("AWS_TIMEOUT_S must be > 0")

    return Config(
        profile_name=profile_name,
        region_name=region_name,
        allowed_accounts=allowed_accounts,
        allowed_regions=allowed_regions,
        timeout_s=timeout_s,
    )
