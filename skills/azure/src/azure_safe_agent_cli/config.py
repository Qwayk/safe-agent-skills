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


def _split_csv(value: str) -> tuple[str, ...]:
    items = [item.strip() for item in value.split(",")]
    return tuple(item for item in items if item)


@dataclasses.dataclass(frozen=True)
class Config:
    management_endpoint: str
    data_plane_endpoint: str | None
    token: str | None
    timeout_s: float
    tenant_id: str | None
    allowed_tenants: tuple[str, ...]
    allowed_subscriptions: tuple[str, ...]
    allowed_resource_groups: tuple[str, ...]
    allowed_locations: tuple[str, ...]
    allowed_services: tuple[str, ...]

    @property
    def base_url(self) -> str:
        return self.management_endpoint

    def redaction_values(self) -> tuple[str, ...]:
        values: list[str] = []
        for item in (
            self.token,
            self.tenant_id,
            *self.allowed_tenants,
            *self.allowed_subscriptions,
            *self.allowed_resource_groups,
            *self.allowed_locations,
            *self.allowed_services,
        ):
            if item and item not in values:
                values.append(item)
        return tuple(values)


def load_config(env_file: str | None) -> Config:
    env = _parse_env_file(Path(env_file or ".env"))

    management_endpoint = (_get(env, "AZURE_MANAGEMENT_ENDPOINT") or "https://management.azure.com").rstrip("/")
    data_plane_endpoint = _get(env, "AZURE_DATA_PLANE_ENDPOINT").rstrip("/") or None
    token = _get(env, "AZURE_API_TOKEN") or None
    tenant_id = _get(env, "AZURE_TENANT_ID") or None
    allowed_tenants = _split_csv(_get(env, "AZURE_ALLOWED_TENANTS"))
    allowed_subscriptions = _split_csv(_get(env, "AZURE_ALLOWED_SUBSCRIPTIONS"))
    allowed_resource_groups = _split_csv(_get(env, "AZURE_ALLOWED_RESOURCE_GROUPS"))
    allowed_locations = _split_csv(_get(env, "AZURE_ALLOWED_LOCATIONS"))
    allowed_services = _split_csv(_get(env, "AZURE_ALLOWED_SERVICES"))

    timeout_s_raw = _get(env, "AZURE_TIMEOUT_S") or "30"
    try:
        timeout_s = float(timeout_s_raw)
    except Exception:
        raise RuntimeError("AZURE_TIMEOUT_S must be a number (seconds)") from None

    if not management_endpoint:
        raise RuntimeError("Missing AZURE_MANAGEMENT_ENDPOINT")
    if timeout_s <= 0:
        raise RuntimeError("AZURE_TIMEOUT_S must be > 0")

    return Config(
        management_endpoint=management_endpoint,
        data_plane_endpoint=data_plane_endpoint,
        token=token,
        timeout_s=timeout_s,
        tenant_id=tenant_id,
        allowed_tenants=allowed_tenants,
        allowed_subscriptions=allowed_subscriptions,
        allowed_resource_groups=allowed_resource_groups,
        allowed_locations=allowed_locations,
        allowed_services=allowed_services,
    )
