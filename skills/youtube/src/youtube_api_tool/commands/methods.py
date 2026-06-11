from __future__ import annotations

from typing import Any

from ..youtube_discovery import extract_official_method_names, load_official_discovery_doc


def cmd_methods_list(args: Any, ctx: dict[str, Any]) -> int:
    resource_filter = str(getattr(args, "resource", "") or "").strip()

    discovery = load_official_discovery_doc()
    methods = extract_official_method_names(discovery_obj=discovery)

    if resource_filter:
        prefix = resource_filter + "."
        methods = [m for m in methods if m.startswith(prefix)]

    ctx["out"].emit(
        {
            "ok": True,
            "resource_filter": resource_filter or None,
            "count": len(methods),
            "methods": methods,
        }
    )
    return 0

