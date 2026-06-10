from __future__ import annotations

import dataclasses
import json
import os
from pathlib import Path
from typing import Any


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


def _parse_config_file(path: Path | None) -> dict[str, Any]:
    if path is None:
        return {}
    if not path.exists():
        raise RuntimeError(f"Config file not found: {path}")

    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        raise RuntimeError(f"Invalid JSON in config file {path}: {type(e).__name__}: {e}") from None

    if not isinstance(raw, dict):
        raise RuntimeError(f"Config file must be a JSON object: {path}")

    allowed = {"base_url", "api_domain", "timeout_s"}
    unknown = [str(k) for k in raw.keys() if str(k) not in allowed]
    if unknown:
        raise RuntimeError(f"Config file has unknown keys: {', '.join(sorted(unknown))}")
    return raw


def _get(env: dict[str, str], key: str) -> str:
    # OS env overrides env-file.
    return (os.environ.get(key) if key in os.environ else env.get(key) or "").strip()


def _normalize_api_domain(value: str) -> str:
    value = (value or "").strip().rstrip("/")
    if not value:
        return ""
    if "://" in value:
        return value
    if "." in value:
        return f"https://{value}"
    return f"https://{value}.pipedrive.com"


def _strip_api_prefix(url: str) -> str:
    root = url.rstrip("/")
    lower = root.lower()
    for suffix in ("/api/v1", "/api/v2", "/v1", "/v2"):
        if lower.endswith(suffix):
            return root[: -len(suffix)]
    return root


@dataclasses.dataclass(frozen=True)
class Config:
    base_url: str
    api_domain: str
    token: str | None
    timeout_s: float

    @property
    def api_root(self) -> str:
        if self.base_url:
            base = _strip_api_prefix(self.base_url).rstrip("/")
            if "://" not in base:
                base = f"https://{base}"
            return base
        domain = self.api_domain.strip()
        if not domain:
            raise RuntimeError("Missing PIPEDRIVE_API_DOMAIN and PIPEDRIVE_BASE_URL")
        return _normalize_api_domain(domain).rstrip("/")


def endpoint_url(*, cfg: Config, api_version: str, path: str) -> str:
    version = str(api_version or "v1").strip().lstrip("/")
    return f"{cfg.api_root}/api/{version}/{path.lstrip('/')}"


def load_config(env_file: str | None, *, config_file: str | None = None) -> Config:
    env = _parse_env_file(Path(env_file or ".env"))
    cfg = _parse_config_file(Path(config_file) if config_file else None)

    base_url = _get(env, "PIPEDRIVE_BASE_URL") or str(cfg.get("base_url") or "").strip()
    api_domain = _get(env, "PIPEDRIVE_API_DOMAIN") or str(cfg.get("api_domain") or "").strip()
    token = _get(env, "PIPEDRIVE_API_TOKEN") or None
    if not base_url and not api_domain:
        # Keep both vars to support both old and new environment styles.
        raise RuntimeError("Missing PIPEDRIVE_BASE_URL and PIPEDRIVE_API_DOMAIN")

    timeout_s_raw = (_get(env, "PIPEDRIVE_TIMEOUT_S") or str(cfg.get("timeout_s") or "") or "30").strip()
    try:
        timeout_s = float(timeout_s_raw)
    except Exception:
        raise RuntimeError("PIPEDRIVE_TIMEOUT_S must be a number (seconds)") from None

    if timeout_s <= 0:
        raise RuntimeError("PIPEDRIVE_TIMEOUT_S must be > 0")

    return Config(base_url=base_url, api_domain=api_domain, token=token, timeout_s=timeout_s)
