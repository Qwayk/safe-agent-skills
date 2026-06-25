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
    timeout_s: float
    quota_project: str | None
    allowed_projects: tuple[str, ...]
    allowed_folders: tuple[str, ...]
    allowed_organizations: tuple[str, ...]
    allowed_billing_accounts: tuple[str, ...]
    allowed_regions: tuple[str, ...]

    def redaction_values(self) -> tuple[str, ...]:
        values: list[str] = []
        for item in (
            self.quota_project,
            *self.allowed_projects,
            *self.allowed_folders,
            *self.allowed_organizations,
            *self.allowed_billing_accounts,
            *self.allowed_regions,
        ):
            if item and item not in values:
                values.append(item)
        return tuple(values)


def load_config(env_file: str | None) -> Config:
    env = _parse_env_file(Path(env_file or ".env"))

    quota_project = _get(env, "GCP_QUOTA_PROJECT") or None
    allowed_projects = _split_csv(_get(env, "GCP_ALLOWED_PROJECTS"))
    allowed_folders = _split_csv(_get(env, "GCP_ALLOWED_FOLDERS"))
    allowed_organizations = _split_csv(_get(env, "GCP_ALLOWED_ORGANIZATIONS"))
    allowed_billing_accounts = _split_csv(_get(env, "GCP_ALLOWED_BILLING_ACCOUNTS"))
    allowed_regions = _split_csv(_get(env, "GCP_ALLOWED_REGIONS"))

    timeout_s_raw = _get(env, "GCP_TIMEOUT_S") or "30"
    try:
        timeout_s = float(timeout_s_raw)
    except Exception:
        raise RuntimeError("GCP_TIMEOUT_S must be a number (seconds)") from None

    if timeout_s <= 0:
        raise RuntimeError("GCP_TIMEOUT_S must be > 0")

    return Config(
        timeout_s=timeout_s,
        quota_project=quota_project,
        allowed_projects=allowed_projects,
        allowed_folders=allowed_folders,
        allowed_organizations=allowed_organizations,
        allowed_billing_accounts=allowed_billing_accounts,
        allowed_regions=allowed_regions,
    )
