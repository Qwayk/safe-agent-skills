from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Config:
    api_host: str
    api_key: str
    secret_api_key: str
    timeout_s: float


_HOSTS = {
    "default": "https://api.porkbun.com/api/json/v3",
    "ipv4": "https://api-ipv4.porkbun.com/api/json/v3",
}


def _read_env(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export ") :].strip()
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip("\"'")

    return values


def load_config(env_file: str = ".env") -> Config:
    env_values = _read_env(Path(env_file))

    def env_or(key: str, fallback: str = "") -> str:
        if key in os.environ:
            return os.environ[key].strip()
        return env_values.get(key, fallback).strip()

    host_mode = env_or("PORKBUN_API_HOST", "default")
    if host_mode not in _HOSTS:
        raise ValueError("PORKBUN_API_HOST must be 'default' or 'ipv4'")

    api_key = env_or("PORKBUN_API_KEY")
    secret_api_key = env_or("PORKBUN_SECRET_API_KEY")
    timeout_raw = env_or("PORKBUN_TIMEOUT_S", "30")
    try:
        timeout_s = float(timeout_raw)
    except Exception as exc:  # noqa: BLE001
        raise ValueError("PORKBUN_TIMEOUT_S must be a number") from exc
    if timeout_s <= 0:
        raise ValueError("PORKBUN_TIMEOUT_S must be > 0")

    return Config(api_host=_HOSTS[host_mode], api_key=api_key, secret_api_key=secret_api_key, timeout_s=timeout_s)
