from __future__ import annotations

import dataclasses
import os
from pathlib import Path

DEFAULT_BASE_URL = "https://api.cloudflare.com/client/v4/"


def _parse_env_file(path: Path, *, required: bool = False) -> dict[str, str]:
    if required and not path.is_file():
        raise RuntimeError(f"Explicit env file must exist and be a regular file: {path}")
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


def _get(env: dict[str, str], key: str, *, env_file_only: bool = False) -> str:
    if env_file_only:
        return (env.get(key) or "").strip()
    # OS env overrides the default env file when no explicit path was selected.
    return (os.environ.get(key) if key in os.environ else env.get(key) or "").strip()


@dataclasses.dataclass(frozen=True)
class Config:
    base_url: str
    token: str | None
    account_id: str | None
    connect_timeout_s: float
    read_timeout_s: float

    @property
    def token_owner(self) -> str:
        token = str(self.token or "").lower()
        if token.startswith("cfat_"):
            return "account"
        if token.startswith("cfut_"):
            return "user"
        if self.account_id:
            return "account"
        return "unknown"

    @property
    def token_fingerprint(self) -> str:
        """
        A stable, non-secret identifier for local state keys.

        We never store the raw token in any state key. This is a short SHA-256 prefix.
        """
        import hashlib

        if not self.token:
            return "no-token"
        h = hashlib.sha256(self.token.encode("utf-8")).hexdigest()
        return h[:12]


def load_config(
    env_file: str | None,
    *,
    require_env_file: bool = False,
    env_file_only: bool = False,
) -> Config:
    env = _parse_env_file(Path(env_file or ".env"), required=require_env_file)

    base_url = (_get(env, "CLOUDFLARE_API_BASE_URL", env_file_only=env_file_only) or DEFAULT_BASE_URL).rstrip("/")
    token = _get(env, "CLOUDFLARE_API_TOKEN", env_file_only=env_file_only) or None
    account_id = _get(env, "CLOUDFLARE_ACCOUNT_ID", env_file_only=env_file_only) or None

    timeout_s_raw = _get(env, "CLOUDFLARE_TIMEOUT_S", env_file_only=env_file_only) or "30"
    try:
        timeout_s = float(timeout_s_raw)
    except Exception:
        raise RuntimeError("CLOUDFLARE_TIMEOUT_S must be a number (seconds)") from None

    if not base_url:
        raise RuntimeError("Missing CLOUDFLARE_API_BASE_URL")
    if timeout_s <= 0:
        raise RuntimeError("CLOUDFLARE_TIMEOUT_S must be > 0")

    connect_raw = _get(env, "CLOUDFLARE_CONNECT_TIMEOUT_S", env_file_only=env_file_only) or ""
    read_raw = _get(env, "CLOUDFLARE_READ_TIMEOUT_S", env_file_only=env_file_only) or ""

    def _maybe_float(s: str) -> float | None:
        s = str(s or "").strip()
        if not s:
            return None
        try:
            return float(s)
        except Exception:
            return None

    connect_timeout_s = _maybe_float(connect_raw) or float(timeout_s)
    read_timeout_s = _maybe_float(read_raw) or float(timeout_s)

    if connect_timeout_s <= 0:
        raise RuntimeError("CLOUDFLARE_CONNECT_TIMEOUT_S must be > 0")
    if read_timeout_s <= 0:
        raise RuntimeError("CLOUDFLARE_READ_TIMEOUT_S must be > 0")

    return Config(
        base_url=base_url,
        token=token,
        account_id=account_id,
        connect_timeout_s=connect_timeout_s,
        read_timeout_s=read_timeout_s,
    )
