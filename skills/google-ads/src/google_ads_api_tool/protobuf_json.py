from __future__ import annotations

import importlib
import re
from typing import Any

from google.protobuf.json_format import ParseDict

from .errors import ValidationError

_CAMEL_BOUNDARY_RE = re.compile(r"(?<=[a-z0-9])(?=[A-Z])")


def _service_to_types_module(service: str) -> str:
    # Match the naming used by the google-ads python package:
    #   google.ads.googleads.v22.services.types.<service_snake>
    parts = _CAMEL_BOUNDARY_RE.split(service.strip())
    snake = "_".join(p.lower() for p in parts if p)
    return f"google.ads.googleads.v22.services.types.{snake}"


def _digits_only(s: str) -> str:
    return "".join(ch for ch in (s or "") if ch.isdigit())


def parse_request_json(
    *,
    service: str,
    request_type: str,
    obj: Any,
    customer_id_override: str | None = None,
) -> Any:
    """
    Parse a JSON object into a google-ads proto-plus request message.

    Guarantees:
    - Rejects unknown fields (strict).
    - Rejects non-object JSON.
    - Applies `customer_id_override` (digits only) when the request has `customer_id`.
    - Performs lightweight structural validation for common required fields.
    """
    if not isinstance(obj, dict):
        raise ValidationError("Request JSON must be an object")

    mod_name = _service_to_types_module(service)
    try:
        mod = importlib.import_module(mod_name)
    except ModuleNotFoundError:
        raise ValidationError(f"Request types module not found for service: {service}") from None

    cls = getattr(mod, request_type, None)
    if cls is None:
        raise ValidationError(f"Request type not found: {request_type} (service: {service})")

    msg = cls()
    try:
        ParseDict(obj, msg._pb, ignore_unknown_fields=False)  # type: ignore[attr-defined]
    except Exception as e:  # noqa: BLE001
        raise ValidationError(f"Invalid request JSON for {service}.{request_type}: {type(e).__name__}: {e}") from None

    if customer_id_override:
        v = _digits_only(customer_id_override)
        if not v:
            raise ValidationError("--customer-id must contain digits")
        if hasattr(msg, "customer_id"):
            setattr(msg, "customer_id", v)

    _validate_common_required_fields(service=service, request_type=request_type, msg=msg)
    return msg


def _validate_common_required_fields(*, service: str, request_type: str, msg: Any) -> None:
    # Google Ads API protos are proto3; "Required" is often documented but not encoded as a
    # descriptor-level requiredness. We enforce a deterministic, conservative subset.
    missing: list[str] = []

    def _has_attr(name: str) -> bool:
        return hasattr(msg, name)

    def _get(name: str) -> Any:
        return getattr(msg, name)

    if _has_attr("customer_id") and not str(_get("customer_id") or "").strip():
        missing.append("customer_id")
    if _has_attr("query") and not str(_get("query") or "").strip():
        missing.append("query")
    if _has_attr("resource_name") and not str(_get("resource_name") or "").strip():
        missing.append("resource_name")
    if _has_attr("operations"):
        try:
            if len(_get("operations")) <= 0:
                missing.append("operations")
        except Exception:
            pass

    if missing:
        raise ValidationError(
            f"Missing required field(s) for {service}.{request_type}: " + ", ".join(sorted(set(missing)))
        )
