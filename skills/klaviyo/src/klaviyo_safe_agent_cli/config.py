from __future__ import annotations

import json
import hashlib
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
    base_url: str
    api_key: str | None
    company_id: str | None
    api_revision: str
    timeout_s: float


def _safe_key_fingerprint(api_key: str | None) -> str:
    if not api_key:
        return ""
    raw = api_key.strip()
    if not raw:
        return ""
    return hashlib.sha256(raw.encode("utf-8").rstrip(b"\n")).hexdigest()[:12]


def build_env_fingerprint(cfg: Config) -> str:
    material = {
        "base_url": cfg.base_url,
        "api_revision": cfg.api_revision,
        "api_key_fingerprint": _safe_key_fingerprint(cfg.api_key),
        "company_id": cfg.company_id or "",
    }
    blob = json.dumps(material, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def load_config(env_file: str | None) -> Config:
    env = _parse_env_file(Path(env_file or ".env"))

    base_url = _get(env, "KLAVIYO_API_BASE_URL").rstrip("/")
    api_key = _get(env, "KLAVIYO_API_KEY") or None
    company_id = _get(env, "KLAVIYO_COMPANY_ID") or None
    api_revision = _get(env, "KLAVIYO_API_REVISION") or "2026-04-15"

    timeout_s_raw = _get(env, "KLAVIYO_TIMEOUT_S") or "30"
    try:
        timeout_s = float(timeout_s_raw)
    except Exception:
        raise RuntimeError("KLAVIYO_TIMEOUT_S must be a number (seconds)") from None

    if not base_url:
        raise RuntimeError("Missing KLAVIYO_API_BASE_URL")
    if timeout_s <= 0:
        raise RuntimeError("KLAVIYO_TIMEOUT_S must be > 0")

    return Config(
        base_url=base_url,
        api_key=api_key,
        company_id=company_id,
        api_revision=api_revision,
        timeout_s=timeout_s,
    )
