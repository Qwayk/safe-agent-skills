from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from .errors import ValidationError
from .state import read_json_object, write_private_json

REGIONS = {"AU", "NZ", "UK", "US", "GLOBAL"}


class TenantStore:
    def __init__(self, path: str | Path):
        self.path = Path(path).expanduser().resolve()

    @staticmethod
    def _validate(tenant: dict[str, Any]) -> dict[str, Any]:
        required = {"connection_id", "tenant_id", "tenant_name", "tenant_type", "region"}
        missing = sorted(required - set(tenant))
        if missing:
            raise ValidationError(f"Selected tenant is missing fields: {', '.join(missing)}")
        empty = sorted(
            key for key in required - {"region"} if not str(tenant.get(key) or "").strip()
        )
        if empty:
            raise ValidationError(f"Selected tenant has empty fields: {', '.join(empty)}")
        if str(tenant.get("tenant_type") or "") != "ORGANISATION":
            raise ValidationError("This tool supports organisation tenants only")
        region = str(tenant["region"]).upper()
        if region not in REGIONS:
            raise ValidationError("Tenant region must be AU, NZ, UK, US, or GLOBAL")
        fingerprint = tenant.get("credential_fingerprint")
        if fingerprint is not None and not re.fullmatch(r"[0-9a-f]{64}", str(fingerprint)):
            raise ValidationError("Selected tenant credential fingerprint is invalid")
        return {**tenant, "region": region}

    def write(self, tenant: dict[str, Any]) -> None:
        write_private_json(self.path, self._validate(tenant))

    def read(self) -> dict[str, Any]:
        if not self.path.exists():
            raise ValidationError(
                "No Xero tenant is selected. Run tenant list, then tenant select with the exact tenant ID."
            )
        try:
            return self._validate(read_json_object(self.path))
        except Exception as exc:  # noqa: BLE001
            if isinstance(exc, ValidationError):
                raise
            raise ValidationError(f"Selected Xero tenant file is invalid: {type(exc).__name__}") from None

    def select(
        self, connections: list[dict[str, Any]], *, tenant_id: str, region: str
    ) -> dict[str, Any]:
        match = next(
            (item for item in connections if str(item.get("tenantId") or "") == tenant_id),
            None,
        )
        if match is None:
            raise ValidationError("Requested tenant ID is not present in discovered connections")
        tenant_type = str(match.get("tenantType") or "")
        if tenant_type != "ORGANISATION":
            raise ValidationError(
                "This tool supports organisation tenants only; Practice Manager and Xero HQ "
                "need separate access-gated contracts"
            )
        selected = {
            "connection_id": str(match.get("id") or ""),
            "tenant_id": str(match.get("tenantId") or ""),
            "tenant_name": str(match.get("tenantName") or ""),
            "tenant_type": tenant_type,
            "region": region.upper(),
        }
        self.write(selected)
        return selected

    def select_custom(
        self, organisation: dict[str, Any], *, credential_fingerprint: str
    ) -> dict[str, Any]:
        organisation_id = str(organisation.get("OrganisationID") or "")
        name = str(organisation.get("Name") or "")
        if not organisation_id or not name:
            raise ValidationError(
                "Custom Connection Organisation response has no OrganisationID or Name"
            )
        country = str(organisation.get("CountryCode") or "").upper()
        region = {"AU": "AU", "NZ": "NZ", "GB": "UK", "UK": "UK", "US": "US"}.get(country)
        if region is None:
            raise ValidationError(
                "Custom Connections support only AU, NZ, UK, or US organisations"
            )
        selected = {
            "connection_id": "custom-connection",
            "tenant_id": organisation_id,
            "tenant_name": name,
            "tenant_type": "ORGANISATION",
            "region": region,
            "credential_fingerprint": credential_fingerprint,
        }
        self.write(selected)
        return selected
