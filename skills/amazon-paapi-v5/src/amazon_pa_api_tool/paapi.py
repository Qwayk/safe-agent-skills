from __future__ import annotations

import dataclasses
import datetime as dt
import hashlib
import hmac
import json
from typing import Any

from .config import Config
from .http import HttpClient


class PaApiError(RuntimeError):
    def __init__(self, message: str, *, status: int | None = None, errors: list[dict[str, Any]] | None = None):
        super().__init__(message)
        self.status = status
        self.errors = errors or []


def _sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _hmac_sha256(key: bytes, msg: str) -> bytes:
    return hmac.new(key, msg.encode("utf-8"), hashlib.sha256).digest()


def _signing_key(*, secret_access_key: str, date_stamp: str, region: str, service: str) -> bytes:
    k_date = _hmac_sha256(("AWS4" + secret_access_key).encode("utf-8"), date_stamp)
    k_region = hmac.new(k_date, region.encode("utf-8"), hashlib.sha256).digest()
    k_service = hmac.new(k_region, service.encode("utf-8"), hashlib.sha256).digest()
    return hmac.new(k_service, b"aws4_request", hashlib.sha256).digest()


def sign_paapi_request(
    *,
    access_key_id: str,
    secret_access_key: str,
    region: str,
    host: str,
    target: str,
    canonical_uri: str,
    body: bytes,
    now_utc: dt.datetime | None = None,
) -> dict[str, str]:
    """
    Create headers for a signed PA-API v5 POST request (SigV4).

    `body` must be the exact bytes sent to the server.
    """
    service = "ProductAdvertisingAPI"
    now = now_utc or dt.datetime.now(dt.timezone.utc)
    amz_date = now.strftime("%Y%m%dT%H%M%SZ")
    date_stamp = now.strftime("%Y%m%d")

    headers = {
        "content-encoding": "amz-1.0",
        "content-type": "application/json; charset=UTF-8",
        "host": host,
        "x-amz-date": amz_date,
        "x-amz-target": target,
    }

    signed_headers = ";".join(sorted(headers.keys()))
    canonical_headers = "".join(f"{k}:{headers[k]}\n" for k in sorted(headers.keys()))
    payload_hash = _sha256_hex(body)

    canonical_request = "\n".join(
        [
            "POST",
            canonical_uri,
            "",
            canonical_headers,
            signed_headers,
            payload_hash,
        ]
    )

    credential_scope = f"{date_stamp}/{region}/{service}/aws4_request"
    string_to_sign = "\n".join(
        [
            "AWS4-HMAC-SHA256",
            amz_date,
            credential_scope,
            _sha256_hex(canonical_request.encode("utf-8")),
        ]
    )

    signing_key = _signing_key(
        secret_access_key=secret_access_key,
        date_stamp=date_stamp,
        region=region,
        service=service,
    )
    signature = hmac.new(signing_key, string_to_sign.encode("utf-8"), hashlib.sha256).hexdigest()

    headers["authorization"] = (
        "AWS4-HMAC-SHA256 "
        f"Credential={access_key_id}/{credential_scope}, "
        f"SignedHeaders={signed_headers}, "
        f"Signature={signature}"
    )
    return headers


@dataclasses.dataclass(frozen=True)
class PaApiResponse:
    status: int
    request_id: str | None
    data: dict[str, Any]


class PaApiClient:
    def __init__(self, *, cfg: Config, http: HttpClient):
        self._cfg = cfg
        self._http = http

    def search_items(
        self,
        *,
        keywords: str,
        search_index: str = "All",
        item_count: int = 10,
        item_page: int = 1,
        resources: list[str] | None = None,
    ) -> PaApiResponse:
        payload: dict[str, Any] = {
            "Keywords": keywords,
            "SearchIndex": search_index,
            "ItemCount": item_count,
            "ItemPage": item_page,
            "PartnerTag": self._cfg.partner_tag,
            "PartnerType": self._cfg.partner_type,
            "Marketplace": self._cfg.marketplace,
        }
        if resources:
            payload["Resources"] = resources
        return self._call(operation="SearchItems", canonical_uri="/paapi5/searchitems", payload=payload)

    def get_items(self, *, item_ids: list[str], resources: list[str] | None = None) -> PaApiResponse:
        payload: dict[str, Any] = {
            "ItemIds": item_ids,
            "PartnerTag": self._cfg.partner_tag,
            "PartnerType": self._cfg.partner_type,
            "Marketplace": self._cfg.marketplace,
        }
        if resources:
            payload["Resources"] = resources
        return self._call(operation="GetItems", canonical_uri="/paapi5/getitems", payload=payload)

    def get_browse_nodes(self, *, browse_node_ids: list[str], resources: list[str] | None = None) -> PaApiResponse:
        payload: dict[str, Any] = {
            "BrowseNodeIds": browse_node_ids,
            "PartnerTag": self._cfg.partner_tag,
            "PartnerType": self._cfg.partner_type,
            "Marketplace": self._cfg.marketplace,
        }
        if resources:
            payload["Resources"] = resources
        return self._call(operation="GetBrowseNodes", canonical_uri="/paapi5/getbrowsenodes", payload=payload)

    def get_variations(
        self,
        *,
        asin: str,
        variation_page: int = 1,
        variation_count: int = 10,
        resources: list[str] | None = None,
    ) -> PaApiResponse:
        payload: dict[str, Any] = {
            "ASIN": asin,
            "VariationPage": variation_page,
            "VariationCount": variation_count,
            "PartnerTag": self._cfg.partner_tag,
            "PartnerType": self._cfg.partner_type,
            "Marketplace": self._cfg.marketplace,
        }
        if resources:
            payload["Resources"] = resources
        return self._call(operation="GetVariations", canonical_uri="/paapi5/getvariations", payload=payload)

    def _call(self, *, operation: str, canonical_uri: str, payload: dict[str, Any]) -> PaApiResponse:
        target = f"com.amazon.paapi5.v1.ProductAdvertisingAPIv1.{operation}"
        body = (json.dumps(payload, ensure_ascii=False, separators=(",", ":"), sort_keys=True) + "\n").encode(
            "utf-8"
        )
        headers = sign_paapi_request(
            access_key_id=self._cfg.access_key_id,
            secret_access_key=self._cfg.secret_access_key,
            region=self._cfg.region,
            host=self._cfg.host,
            target=target,
            canonical_uri=canonical_uri,
            body=body,
        )
        url = f"https://{self._cfg.host}{canonical_uri}"
        resp = self._http.request(
            "POST",
            url,
            headers=headers,
            data=body,
            retries=2,
            allow_error=True,
        )

        request_id = resp.headers.get("x-amzn-requestid") or resp.headers.get("x-amzn-request-id")
        try:
            data = resp.json()
        except Exception:
            raise PaApiError(f"PA-API returned non-JSON response (HTTP {resp.status})", status=resp.status) from None

        if resp.status >= 400:
            errors = data.get("Errors") if isinstance(data, dict) else None
            if not isinstance(errors, list):
                errors = []
            msg = "PA-API error"
            if errors:
                parts = []
                for e in errors:
                    if not isinstance(e, dict):
                        continue
                    code = (e.get("Code") or "").strip()
                    m = (e.get("Message") or "").strip()
                    if code and m:
                        parts.append(f"{code}: {m}")
                    elif code:
                        parts.append(code)
                    elif m:
                        parts.append(m)
                if parts:
                    msg = "PA-API error: " + " | ".join(parts)
            raise PaApiError(msg, status=resp.status, errors=errors)

        if not isinstance(data, dict):
            raise PaApiError("PA-API returned unexpected JSON shape (expected object)", status=resp.status)
        return PaApiResponse(status=resp.status, request_id=request_id, data=data)
