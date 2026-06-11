from __future__ import annotations

from typing import Any

from ..errors import ValidationError
from ..locale_data import LocaleInfo, list_locales, locale_info
from ..token_urls import token_endpoints_for_locale


def _describe_locale(info: LocaleInfo) -> dict[str, Any]:
    endpoints = token_endpoints_for_locale(info.locale_tag)
    language = info.locale_tag.split("_", 1)[0]
    version_map = {
        key: value
        for key, value in endpoints.items()
        if key.startswith("v2.") or key.startswith("v3.")
    }
    return {
        "marketplace": info.marketplace,
        "region": info.region,
        "language": language,
        "notes": info.name,
        "token_endpoint_v2": endpoints.get("v2"),
        "token_endpoint_v3": endpoints.get("v3"),
        "token_endpoints": version_map,
    }


def cmd_locales_list(args: Any, ctx: dict[str, Any]) -> int:  # noqa: ARG002
    out = ctx["out"]
    rows = [
        {"locale": info.locale_tag, **_describe_locale(info)}
        for info in sorted(list_locales(), key=lambda obj: obj.locale_tag)
    ]
    out.emit({"ok": True, "locales": rows})
    return 0


def cmd_locales_show(args: Any, ctx: dict[str, Any]) -> int:
    out = ctx["out"]
    code = (args.locale or "").strip()
    if not code:
        raise ValidationError("--locale is required")
    info = locale_info(code)
    if not info:
        raise ValidationError(f"Locale not tracked: {code}")
    out.emit({"ok": True, "locale": info.locale_tag, "mapping": _describe_locale(info)})
    return 0
