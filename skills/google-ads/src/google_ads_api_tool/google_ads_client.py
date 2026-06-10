from __future__ import annotations

import importlib
from typing import Any

from .config import Config
from .errors import ToolError


SUPPORTED_API_VERSION = "v22"


def _missing_dependency_error() -> ToolError:
    return ToolError(
        "Google Ads client library is not installed. Install it with `python -m pip install google-ads` and retry."
    )


try:
    from google.ads.googleads.client import GoogleAdsClient as _GoogleAdsClient
except ModuleNotFoundError:

    class _MissingGoogleAdsClient:
        @staticmethod
        def load_from_dict(*args: Any, **kwargs: Any) -> Any:
            raise _missing_dependency_error()

    _GoogleAdsClient = _MissingGoogleAdsClient

GoogleAdsClient = _GoogleAdsClient


def ensure_supported_api_version_available() -> None:
    try:
        importlib.import_module("google.ads.googleads")
    except ModuleNotFoundError:
        raise _missing_dependency_error()
    try:
        importlib.import_module(f"google.ads.googleads.{SUPPORTED_API_VERSION}")
    except ModuleNotFoundError:
        raise ToolError(
            f"Installed google-ads package does not include {SUPPORTED_API_VERSION}. "
            "Install a compatible google-ads version and retry."
        )


def build_google_ads_client(cfg: Config) -> Any:
    """
    Build a GoogleAdsClient from env-backed config.

    IMPORTANT:
    - Never print or log the underlying config dict.
    - Exceptions must be surfaced without leaking secret values.
    """
    ensure_supported_api_version_available()
    d: dict[str, Any] = {
        "developer_token": cfg.developer_token,
        "client_id": cfg.client_id,
        "client_secret": cfg.client_secret,
        "refresh_token": cfg.refresh_token,
        "use_proto_plus": True,
    }
    if cfg.login_customer_id:
        d["login_customer_id"] = cfg.login_customer_id
    return GoogleAdsClient.load_from_dict(d)


def _load_message_to_dict() -> Any:
    try:
        from google.protobuf.json_format import MessageToDict
    except ModuleNotFoundError:
        raise _missing_dependency_error()
    return MessageToDict


def protobuf_to_dict(msg: Any) -> dict[str, Any]:
    pb = getattr(msg, "_pb", msg)
    if isinstance(pb, dict):
        return pb
    MessageToDict = _load_message_to_dict()
    kwargs = {
        "preserving_proto_field_name": True,
        "use_integers_for_enums": False,
    }
    try:
        out = MessageToDict(pb, including_default_value_fields=False, **kwargs)
    except TypeError:
        # Protobuf json_format signature changed; keep output stable by opting out of printing defaults
        # when supported, otherwise fall back to the default behavior.
        try:
            out = MessageToDict(pb, always_print_fields_with_no_presence=False, **kwargs)
        except TypeError:
            out = MessageToDict(pb, **kwargs)
    return out if isinstance(out, dict) else {"value": out}


def parse_customer_id_from_resource_name(resource_name: str) -> str | None:
    s = (resource_name or "").strip()
    if not s:
        return None
    if "/" in s:
        tail = s.rsplit("/", 1)[-1]
    else:
        tail = s
    digits = "".join(ch for ch in tail if ch.isdigit())
    return digits or None
