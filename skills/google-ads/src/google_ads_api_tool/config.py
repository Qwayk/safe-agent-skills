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
    developer_token: str
    client_id: str
    client_secret: str
    refresh_token: str
    login_customer_id: str | None
    timeout_s: float
    external_writes_disabled: bool
    write_customer_id_allowlist: set[str]
    max_mutate_operations_per_request: int
    max_mutate_operations_per_run: int
    retry_max_attempts: int
    retry_base_delay_s: float

    def secret_values(self) -> list[str]:
        return [self.developer_token, self.client_secret, self.refresh_token]


def load_config(env_file: str | None) -> Config:
    env = _parse_env_file(Path(env_file or ".env"))

    developer_token = _get(env, "GOOGLE_ADS_DEVELOPER_TOKEN")
    client_id = _get(env, "GOOGLE_ADS_CLIENT_ID")
    client_secret = _get(env, "GOOGLE_ADS_CLIENT_SECRET")
    refresh_token = _get(env, "GOOGLE_ADS_REFRESH_TOKEN")
    login_customer_id = _get(env, "GOOGLE_ADS_LOGIN_CUSTOMER_ID") or None

    timeout_s_raw = _get(env, "GOOGLE_ADS_TIMEOUT_S") or "30"
    try:
        timeout_s = float(timeout_s_raw)
    except Exception:
        raise RuntimeError("GOOGLE_ADS_TIMEOUT_S must be a number (seconds)") from None

    if not developer_token:
        raise RuntimeError("Missing GOOGLE_ADS_DEVELOPER_TOKEN")
    if not client_id:
        raise RuntimeError("Missing GOOGLE_ADS_CLIENT_ID")
    if not client_secret:
        raise RuntimeError("Missing GOOGLE_ADS_CLIENT_SECRET")
    if not refresh_token:
        raise RuntimeError("Missing GOOGLE_ADS_REFRESH_TOKEN")
    if timeout_s <= 0:
        raise RuntimeError("GOOGLE_ADS_TIMEOUT_S must be > 0")
    if login_customer_id is not None:
        login_customer_id = "".join(ch for ch in login_customer_id if ch.isdigit()) or None

    external_writes_disabled_raw = _get(env, "GOOGLE_ADS_EXTERNAL_WRITES_DISABLED") or ""
    external_writes_disabled = external_writes_disabled_raw.strip().lower() in {"1", "true", "yes", "on"}

    allow_raw = _get(env, "GOOGLE_ADS_WRITE_CUSTOMER_ID_ALLOWLIST") or ""
    allow: set[str] = set()
    for part in allow_raw.split(","):
        digits = "".join(ch for ch in part if ch.isdigit())
        if digits:
            allow.add(digits)

    max_ops_req_raw = _get(env, "GOOGLE_ADS_MAX_MUTATE_OPERATIONS_PER_REQUEST") or "100"
    max_ops_run_raw = _get(env, "GOOGLE_ADS_MAX_MUTATE_OPERATIONS_PER_RUN") or "1000"
    try:
        max_ops_req = int(max_ops_req_raw)
    except Exception:
        raise RuntimeError("GOOGLE_ADS_MAX_MUTATE_OPERATIONS_PER_REQUEST must be an integer") from None
    try:
        max_ops_run = int(max_ops_run_raw)
    except Exception:
        raise RuntimeError("GOOGLE_ADS_MAX_MUTATE_OPERATIONS_PER_RUN must be an integer") from None
    if max_ops_req <= 0:
        raise RuntimeError("GOOGLE_ADS_MAX_MUTATE_OPERATIONS_PER_REQUEST must be > 0")
    if max_ops_run <= 0:
        raise RuntimeError("GOOGLE_ADS_MAX_MUTATE_OPERATIONS_PER_RUN must be > 0")

    retry_max_attempts_raw = _get(env, "GOOGLE_ADS_RETRY_MAX_ATTEMPTS") or "3"
    retry_base_delay_raw = _get(env, "GOOGLE_ADS_RETRY_BASE_DELAY_S") or "1.0"
    try:
        retry_max_attempts = int(retry_max_attempts_raw)
    except Exception:
        raise RuntimeError("GOOGLE_ADS_RETRY_MAX_ATTEMPTS must be an integer") from None
    try:
        retry_base_delay_s = float(retry_base_delay_raw)
    except Exception:
        raise RuntimeError("GOOGLE_ADS_RETRY_BASE_DELAY_S must be a number (seconds)") from None
    if retry_max_attempts <= 0:
        raise RuntimeError("GOOGLE_ADS_RETRY_MAX_ATTEMPTS must be > 0")
    if retry_base_delay_s < 0:
        raise RuntimeError("GOOGLE_ADS_RETRY_BASE_DELAY_S must be >= 0")

    return Config(
        developer_token=developer_token,
        client_id=client_id,
        client_secret=client_secret,
        refresh_token=refresh_token,
        login_customer_id=login_customer_id,
        timeout_s=timeout_s,
        external_writes_disabled=external_writes_disabled,
        write_customer_id_allowlist=allow,
        max_mutate_operations_per_request=max_ops_req,
        max_mutate_operations_per_run=max_ops_run,
        retry_max_attempts=retry_max_attempts,
        retry_base_delay_s=retry_base_delay_s,
    )
