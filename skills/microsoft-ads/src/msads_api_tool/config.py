from __future__ import annotations

import dataclasses
import os
from pathlib import Path

_KNOWN_SERVICES: tuple[str, ...] = (
    "campaign-management",
    "bulk",
    "reporting",
    "ad-insight",
    "customer-management",
)


def _default_endpoints(environment: str) -> dict[str, str]:
    env = environment.strip().lower()
    if env not in {"prod", "sandbox"}:
        raise RuntimeError("MSADS_ENVIRONMENT must be 'prod' or 'sandbox'")

    # Source: docs/official_web_service_addresses_bingads-13_2026-03-04.md
    if env == "prod":
        return {
            "ad-insight": "https://adinsight.api.bingads.microsoft.com/Api/Advertiser/AdInsight/v13/AdInsightService.svc",
            "bulk": "https://bulk.api.bingads.microsoft.com/Api/Advertiser/CampaignManagement/v13/BulkService.svc",
            "campaign-management": "https://campaign.api.bingads.microsoft.com/Api/Advertiser/CampaignManagement/v13/CampaignManagementService.svc",
            "customer-management": "https://clientcenter.api.bingads.microsoft.com/Api/CustomerManagement/v13/CustomerManagementService.svc",
            "reporting": "https://reporting.api.bingads.microsoft.com/Api/Advertiser/Reporting/v13/ReportingService.svc",
        }
    return {
        "ad-insight": "https://adinsight.api.sandbox.bingads.microsoft.com/Api/Advertiser/AdInsight/v13/AdInsightService.svc",
        "bulk": "https://bulk.api.sandbox.bingads.microsoft.com/Api/Advertiser/CampaignManagement/v13/BulkService.svc",
        "campaign-management": "https://campaign.api.sandbox.bingads.microsoft.com/Api/Advertiser/CampaignManagement/v13/CampaignManagementService.svc",
        "customer-management": "https://clientcenter.api.sandbox.bingads.microsoft.com/Api/CustomerManagement/v13/CustomerManagementService.svc",
        "reporting": "https://reporting.api.sandbox.bingads.microsoft.com/Api/Advertiser/Reporting/v13/ReportingService.svc",
    }


def _override_endpoints(env: dict[str, str], defaults: dict[str, str]) -> dict[str, str]:
    overrides = {
        "campaign-management": _get(env, "MSADS_CAMPAIGN_MANAGEMENT_URL").rstrip("/"),
        "bulk": _get(env, "MSADS_BULK_URL").rstrip("/"),
        "reporting": _get(env, "MSADS_REPORTING_URL").rstrip("/"),
        "ad-insight": _get(env, "MSADS_AD_INSIGHT_URL").rstrip("/"),
        "customer-management": _get(env, "MSADS_CUSTOMER_MANAGEMENT_URL").rstrip("/"),
    }
    out = dict(defaults)
    for service, url in overrides.items():
        if url:
            out[service] = url
    # Ensure we never accidentally drop a service.
    missing = [s for s in _KNOWN_SERVICES if s not in out]
    if missing:
        raise RuntimeError(f"Missing endpoint defaults for: {', '.join(missing)}")
    return out


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
    environment: str
    developer_token: str | None
    customer_id: str | None
    customer_account_id: str | None
    oauth_client_id: str | None
    oauth_client_secret: str | None
    oauth_redirect_uri: str | None
    oauth_tenant: str
    oauth_scope: str
    timeout_s: float
    endpoints: dict[str, str]

    @property
    def env_fingerprint(self) -> str:
        # Intentionally non-secret: used only for provenance in local artifacts.
        return f"msads:{self.environment}"


def load_config(env_file: str | None) -> Config:
    env = _parse_env_file(Path(env_file or ".env"))

    environment = (_get(env, "MSADS_ENVIRONMENT") or "prod").strip().lower()
    endpoints = _override_endpoints(env, _default_endpoints(environment))

    developer_token = _get(env, "MSADS_DEVELOPER_TOKEN") or None
    customer_id = _get(env, "MSADS_CUSTOMER_ID") or None
    customer_account_id = _get(env, "MSADS_CUSTOMER_ACCOUNT_ID") or None

    oauth_client_id = _get(env, "MSADS_OAUTH_CLIENT_ID") or None
    oauth_client_secret = _get(env, "MSADS_OAUTH_CLIENT_SECRET") or None
    oauth_redirect_uri = _get(env, "MSADS_OAUTH_REDIRECT_URI") or None
    oauth_tenant = (_get(env, "MSADS_OAUTH_TENANT") or "common").strip() or "common"
    oauth_scope = (
        (_get(env, "MSADS_OAUTH_SCOPE") or "https://ads.microsoft.com/msads.manage offline_access").strip()
        or "https://ads.microsoft.com/msads.manage offline_access"
    )

    timeout_s_raw = _get(env, "MSADS_TIMEOUT_S") or "30"
    try:
        timeout_s = float(timeout_s_raw)
    except Exception:
        raise RuntimeError("MSADS_TIMEOUT_S must be a number (seconds)") from None
    if timeout_s <= 0:
        raise RuntimeError("MSADS_TIMEOUT_S must be > 0")

    return Config(
        environment=environment,
        developer_token=developer_token,
        customer_id=customer_id,
        customer_account_id=customer_account_id,
        oauth_client_id=oauth_client_id,
        oauth_client_secret=oauth_client_secret,
        oauth_redirect_uri=oauth_redirect_uri,
        oauth_tenant=oauth_tenant,
        oauth_scope=oauth_scope,
        timeout_s=timeout_s,
        endpoints=endpoints,
    )
