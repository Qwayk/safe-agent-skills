from __future__ import annotations

import dataclasses
import os
from pathlib import Path

from .errors import ValidationError


def _parse_env_file(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    output: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export ") :].strip()
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        output[key.strip()] = value.strip().strip("'").strip('"')
    return output


def _get(values: dict[str, str], key: str) -> str:
    return os.environ.get(key, values.get(key, "")).strip()


@dataclasses.dataclass(frozen=True)
class Config:
    env_file: Path
    state_root: Path
    client_id: str
    redirect_uri: str
    client_secret: str | None
    custom_client_id: str | None
    custom_client_secret: str | None
    app_store_client_id: str | None
    app_store_client_secret: str | None
    timeout_s: float

    @property
    def pkce_token_path(self) -> Path:
        return self.state_root / "oauth" / "token.json"

    @property
    def custom_token_path(self) -> Path:
        return self.state_root / "oauth" / "custom-connection-token.json"

    @property
    def app_store_token_path(self) -> Path:
        return self.state_root / "oauth" / "app-store-token.json"

    @property
    def pkce_state_path(self) -> Path:
        return self.state_root / "oauth" / "pkce.json"

    @property
    def tenant_path(self) -> Path:
        return self.state_root / "tenant.json"

    @property
    def custom_tenant_path(self) -> Path:
        return self.state_root / "custom-tenant.json"


def load_config(env_file: str | Path) -> Config:
    path = Path(env_file).expanduser().resolve()
    values = _parse_env_file(path)
    timeout_raw = _get(values, "XERO_TIMEOUT_S") or "30"
    try:
        timeout_s = float(timeout_raw)
    except ValueError:
        raise ValidationError("XERO_TIMEOUT_S must be a number") from None
    if timeout_s <= 0:
        raise ValidationError("XERO_TIMEOUT_S must be greater than zero")
    state_value = _get(values, "XERO_STATE_DIR")
    state_path = Path(state_value).expanduser() if state_value else Path(".state")
    if not state_path.is_absolute():
        state_path = path.parent / state_path
    state_root = state_path.resolve()
    return Config(
        env_file=path,
        state_root=state_root,
        client_id=_get(values, "XERO_CLIENT_ID"),
        redirect_uri=_get(values, "XERO_REDIRECT_URI") or "http://localhost:8765/callback",
        client_secret=_get(values, "XERO_CLIENT_SECRET") or None,
        custom_client_id=_get(values, "XERO_CUSTOM_CLIENT_ID") or None,
        custom_client_secret=_get(values, "XERO_CUSTOM_CLIENT_SECRET") or None,
        app_store_client_id=_get(values, "XERO_APP_STORE_CLIENT_ID") or None,
        app_store_client_secret=_get(values, "XERO_APP_STORE_CLIENT_SECRET") or None,
        timeout_s=timeout_s,
    )
