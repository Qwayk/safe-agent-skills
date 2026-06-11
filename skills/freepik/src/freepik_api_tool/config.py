from __future__ import annotations

import dataclasses
from dataclasses import dataclass
import os
from pathlib import Path


@dataclass(frozen=True)
class Config:
    base_url: str
    api_key: str
    timeout_s: float
    auth_header: str
    auth_prefix: str
    accept_language: str | None
    image_size: str | None
    download_url_jsonpath: str | None
    license_url_jsonpath: str | None

    def with_overrides(
        self,
        *,
        accept_language: str | None = None,
        image_size: str | None = None,
    ) -> Config:
        return dataclasses.replace(
            self,
            accept_language=accept_language if accept_language is not None else self.accept_language,
            image_size=image_size if image_size is not None else self.image_size,
        )


def _parse_env_file(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    out: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        if s.startswith("export "):
            s = s[len("export ") :].strip()
        if "=" not in s:
            continue
        k, v = s.split("=", 1)
        out[k.strip()] = v.strip().strip("'").strip('"')
    return out


def _get(env: dict[str, str], key: str) -> str:
    # OS env overrides env-file.
    return (os.environ.get(key) if key in os.environ else env.get(key) or "").strip()


def load_config(env_file: str) -> Config:
    env = _parse_env_file(Path(env_file or ".env"))

    base_url = (_get(env, "FREEPIK_API_BASE_URL") or _get(env, "FREEPIK_BASE_URL") or "").rstrip("/")
    if not base_url:
        base_url = "https://api.freepik.com/v1"

    api_key = _get(env, "FREEPIK_API_KEY") or _get(env, "FREEPIK_KEY")
    timeout_s_raw = _get(env, "FREEPIK_TIMEOUT_S") or "30"
    try:
        timeout_s = float(timeout_s_raw)
    except Exception:
        raise RuntimeError("FREEPIK_TIMEOUT_S must be a number (seconds)") from None
    auth_header = _get(env, "FREEPIK_AUTH_HEADER") or "x-freepik-api-key"
    auth_prefix = _get(env, "FREEPIK_AUTH_PREFIX")
    auth_prefix = auth_prefix.strip("\n")

    if not api_key:
        raise RuntimeError("Missing FREEPIK_API_KEY")
    if timeout_s <= 0:
        raise RuntimeError("FREEPIK_TIMEOUT_S must be > 0")

    accept_language = _get(env, "FREEPIK_ACCEPT_LANGUAGE") or None
    image_size = _get(env, "FREEPIK_IMAGE_SIZE") or None

    download_url_jsonpath = _get(env, "FREEPIK_DOWNLOAD_URL_JSONPATH") or None
    license_url_jsonpath = _get(env, "FREEPIK_LICENSE_URL_JSONPATH") or None

    return Config(
        base_url=base_url,
        api_key=api_key,
        timeout_s=timeout_s,
        auth_header=auth_header,
        auth_prefix=auth_prefix,
        accept_language=accept_language,
        image_size=image_size,
        download_url_jsonpath=download_url_jsonpath,
        license_url_jsonpath=license_url_jsonpath,
    )
