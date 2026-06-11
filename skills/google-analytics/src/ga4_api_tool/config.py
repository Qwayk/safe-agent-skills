from __future__ import annotations

import dataclasses
import os
from pathlib import Path
from typing import Any

from .discovery import DiscoveryDocSpec, extract_oauth_scopes, load_vendored_discovery_doc
from .oauth_tokens import read_token_json, token_path_for_env_file


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
    auth_mode: str
    scopes: tuple[str, ...]
    admin_base_url: str
    data_base_url: str
    timeout_s: float

    # oauth_refresh_token mode (never print these values)
    oauth_client_id: str | None
    oauth_client_secret: str | None
    oauth_refresh_token: str | None

    # service_account_json mode
    service_account_json: str | None


def _join_base_url(root_url: str, service_path: str) -> str:
    root = (root_url or "").strip()
    sp = (service_path or "").strip()
    if not root:
        return ""
    if not root.endswith("/"):
        root += "/"
    # servicePath is often empty; if present it usually ends with /
    if sp.startswith("/"):
        sp = sp[1:]
    return (root + sp).rstrip("/") + "/"


def _default_admin_base_url() -> str:
    doc = load_vendored_discovery_doc(
        DiscoveryDocSpec(
            expected_name="analyticsadmin",
            expected_version="v1alpha",
            vendor_filename="analyticsadmin_v1alpha_discovery.json",
        )
    )
    return _join_base_url(str(doc.get("rootUrl") or ""), str(doc.get("servicePath") or ""))


def _default_data_base_url() -> str:
    doc = load_vendored_discovery_doc(
        DiscoveryDocSpec(
            expected_name="analyticsdata",
            expected_version="v1beta",
            vendor_filename="analyticsdata_v1beta_discovery.json",
        )
    )
    return _join_base_url(str(doc.get("rootUrl") or ""), str(doc.get("servicePath") or ""))


def _default_scopes() -> list[str]:
    specs = [
        DiscoveryDocSpec(
            expected_name="analyticsadmin",
            expected_version="v1alpha",
            vendor_filename="analyticsadmin_v1alpha_discovery.json",
        ),
        DiscoveryDocSpec(
            expected_name="analyticsdata",
            expected_version="v1beta",
            vendor_filename="analyticsdata_v1beta_discovery.json",
        ),
        DiscoveryDocSpec(
            expected_name="analyticsdata",
            expected_version="v1alpha",
            vendor_filename="analyticsdata_v1alpha_discovery.json",
        ),
    ]
    scopes: set[str] = set()
    for s in specs:
        scopes.update(extract_oauth_scopes(load_vendored_discovery_doc(s)))
    out = sorted(scopes)
    return out


def _parse_scopes(raw: str) -> list[str]:
    if not raw.strip():
        return []
    # Accept comma-separated or whitespace-separated.
    parts: list[str] = []
    for chunk in raw.replace(",", " ").split():
        s = chunk.strip()
        if s:
            parts.append(s)
    # stable + unique
    out = sorted(set(parts))
    return out


def load_config(env_file: str | None) -> Config:
    env_file_str = str(env_file or ".env")
    env = _parse_env_file(Path(env_file_str))

    timeout_s_raw = _get(env, "GA4_TIMEOUT_S") or "30"
    try:
        timeout_s = float(timeout_s_raw)
    except Exception:
        raise RuntimeError("GA4_TIMEOUT_S must be a number (seconds)") from None
    if timeout_s <= 0:
        raise RuntimeError("GA4_TIMEOUT_S must be > 0")

    auth_mode = (_get(env, "GA4_AUTH_MODE") or "adc").strip().lower()
    if auth_mode not in {"adc", "oauth_refresh_token", "service_account_json"}:
        raise RuntimeError("GA4_AUTH_MODE must be one of: adc, oauth_refresh_token, service_account_json")

    # Base URLs
    legacy_base_url = _get(env, "GA4_API_BASE_URL").rstrip("/")
    admin_base_url = (_get(env, "GA4_ADMIN_BASE_URL") or "").strip()
    data_base_url = (_get(env, "GA4_DATA_BASE_URL") or "").strip()
    if legacy_base_url and not admin_base_url:
        admin_base_url = legacy_base_url
    if legacy_base_url and not data_base_url:
        data_base_url = legacy_base_url

    admin_base_url = (admin_base_url or _default_admin_base_url()).rstrip("/") + "/"
    data_base_url = (data_base_url or _default_data_base_url()).rstrip("/") + "/"

    # Scopes
    scopes_raw = _get(env, "GA4_SCOPES")
    scopes = _parse_scopes(scopes_raw) if scopes_raw else _default_scopes()
    if not scopes:
        raise RuntimeError("No GA4 scopes resolved (GA4_SCOPES empty and discovery scopes missing)")

    # Secrets (only required depending on auth_mode)
    token_json: dict[str, Any] | None = None
    try:
        token_json = read_token_json(token_path_for_env_file(env_file_str))
    except Exception:
        token_json = None

    oauth_client_id = _get(env, "GA4_OAUTH_CLIENT_ID") or (str(token_json.get("client_id")) if isinstance(token_json, dict) and token_json.get("client_id") else None)  # type: ignore[union-attr]
    oauth_client_secret = _get(env, "GA4_OAUTH_CLIENT_SECRET") or (str(token_json.get("client_secret")) if isinstance(token_json, dict) and token_json.get("client_secret") else None)  # type: ignore[union-attr]
    oauth_refresh_token = _get(env, "GA4_OAUTH_REFRESH_TOKEN") or (str(token_json.get("refresh_token")) if isinstance(token_json, dict) and token_json.get("refresh_token") else None)  # type: ignore[union-attr]

    service_account_json = _get(env, "GA4_SERVICE_ACCOUNT_JSON") or None

    if auth_mode == "oauth_refresh_token":
        if not oauth_client_id or not oauth_client_secret or not oauth_refresh_token:
            raise RuntimeError(
                "Missing OAuth refresh-token config. Provide GA4_OAUTH_CLIENT_ID, GA4_OAUTH_CLIENT_SECRET, GA4_OAUTH_REFRESH_TOKEN (or .state/token.json)."
            )
    if auth_mode == "service_account_json":
        if not service_account_json:
            raise RuntimeError("Missing GA4_SERVICE_ACCOUNT_JSON (path to service account key file)")

    return Config(
        auth_mode=auth_mode,
        scopes=tuple(scopes),
        admin_base_url=admin_base_url,
        data_base_url=data_base_url,
        timeout_s=timeout_s,
        oauth_client_id=oauth_client_id,
        oauth_client_secret=oauth_client_secret,
        oauth_refresh_token=oauth_refresh_token,
        service_account_json=service_account_json,
    )
