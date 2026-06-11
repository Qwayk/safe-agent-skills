from __future__ import annotations

import dataclasses
import json
import os
from pathlib import Path

from .errors import ValidationError

_FORBIDDEN_JSON_KEYS: frozenset[str] = frozenset(
    {"WOOCOMMERCE_CONSUMER_KEY", "WOOCOMMERCE_CONSUMER_SECRET"}
)


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
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip("'").strip('"')
        if key:
            out[key] = value
    return out


def _normalize_json_value(key: str, value: object) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float, str)):
        return str(value)
    raise ValidationError(
        f"Config JSON key {key} has unsupported value type {type(value).__name__}; "
        "use string, number, or boolean only."
    )


def _load_json_config(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValidationError(f"Invalid JSON in config file: {path}") from exc
    except OSError as exc:  # noqa: BLE001
        raise ValidationError(f"Cannot read config file: {path}") from exc
    if not isinstance(raw, dict):
        raise ValidationError(f"Config file must be a JSON object: {path}")

    out: dict[str, str] = {}
    for raw_key, value in raw.items():
        key = str(raw_key).strip()
        if key in _FORBIDDEN_JSON_KEYS:
            raise ValidationError("Config JSON may include only non-secret values; remove consumer keys.")
        out[key] = _normalize_json_value(key, value)
    return out


def _get(env: dict[str, str], key: str) -> str:
    return (os.environ.get(key) if key in os.environ else env.get(key) or "").strip()


def _parse_bool(raw: str, *, key: str, default: bool) -> bool:
    text = str(raw or "").strip().lower()
    if not text:
        return default
    if text in {"1", "true", "yes", "on"}:
        return True
    if text in {"0", "false", "no", "off"}:
        return False
    raise ValidationError(f"{key} must be true/false")


def _normalize_store_url(raw_store_url: str, raw_api_base_url: str) -> tuple[str, str]:
    api_base_url = str(raw_api_base_url or "").strip().rstrip("/")
    store_url = str(raw_store_url or "").strip().rstrip("/")

    if api_base_url:
        if not api_base_url.startswith(("http://", "https://")):
            raise ValidationError("WOOCOMMERCE_API_BASE_URL must start with http:// or https://")
        if api_base_url.endswith("/wp-json/wc/v3"):
            store_url = api_base_url[: -len("/wp-json/wc/v3")].rstrip("/")
        return store_url or api_base_url, api_base_url

    if not store_url:
        raise ValidationError("Missing WOOCOMMERCE_STORE_URL")
    if not store_url.startswith(("http://", "https://")):
        raise ValidationError("WOOCOMMERCE_STORE_URL must start with http:// or https://")
    if store_url.endswith("/wp-json/wc/v3"):
        api_base_url = store_url
        store_url = store_url[: -len("/wp-json/wc/v3")].rstrip("/")
        return store_url, api_base_url
    return store_url, store_url.rstrip("/") + "/wp-json/wc/v3"


@dataclasses.dataclass(frozen=True)
class Config:
    store_url: str
    api_base_url: str
    consumer_key: str | None
    consumer_secret: str | None
    timeout_s: float
    query_string_auth: bool
    verify_ssl: bool

    @property
    def has_credentials(self) -> bool:
        return bool(self.consumer_key and self.consumer_secret)


def load_config(env_file: str | None, config_file: str | None = None) -> Config:
    env_file_path = Path(env_file or ".env")
    config_path = Path(config_file) if config_file else None
    env = _load_json_config(config_path) if config_path else {}
    env.update(_parse_env_file(env_file_path))

    store_url, api_base_url = _normalize_store_url(
        _get(env, "WOOCOMMERCE_STORE_URL"),
        _get(env, "WOOCOMMERCE_API_BASE_URL"),
    )
    consumer_key = _get(env, "WOOCOMMERCE_CONSUMER_KEY") or None
    consumer_secret = _get(env, "WOOCOMMERCE_CONSUMER_SECRET") or None

    timeout_s_raw = _get(env, "WOOCOMMERCE_TIMEOUT_S") or "30"
    try:
        timeout_s = float(timeout_s_raw)
    except Exception as exc:  # noqa: BLE001
        raise ValidationError("WOOCOMMERCE_TIMEOUT_S must be a number") from exc
    if timeout_s <= 0:
        raise ValidationError("WOOCOMMERCE_TIMEOUT_S must be > 0")

    query_string_auth = _parse_bool(
        _get(env, "WOOCOMMERCE_QUERY_STRING_AUTH"),
        key="WOOCOMMERCE_QUERY_STRING_AUTH",
        default=False,
    )
    verify_ssl = _parse_bool(
        _get(env, "WOOCOMMERCE_VERIFY_SSL"),
        key="WOOCOMMERCE_VERIFY_SSL",
        default=True,
    )

    return Config(
        store_url=store_url,
        api_base_url=api_base_url,
        consumer_key=consumer_key,
        consumer_secret=consumer_secret,
        timeout_s=timeout_s,
        query_string_auth=query_string_auth,
        verify_ssl=verify_ssl,
    )


def endpoint_url(cfg: Config, path: str) -> str:
    normalized = str(path or "").strip() or "/"
    if normalized == "/":
        return cfg.api_base_url
    if not normalized.startswith("/"):
        normalized = "/" + normalized
    return cfg.api_base_url + normalized
