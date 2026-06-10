from __future__ import annotations

from ..errors import ValidationError
from ..operation_keys import OperationCommand, load_allowlisted_operation_commands


def _find_by_area_key(*, area: str, op_key: str) -> OperationCommand | None:
    a = str(area or "").strip()
    k = str(op_key or "").strip()
    if not a or not k:
        return None
    for c in load_allowlisted_operation_commands():
        if c.area == a and c.op_key == k:
            return c
    return None


def cmd_operations_list(args, ctx) -> int:
    contains = str(getattr(args, "contains", None) or "").strip().lower()
    tag = str(getattr(args, "tag", None) or "").strip().lower()
    method = str(getattr(args, "method", None) or "").strip().upper()
    area = str(getattr(args, "area", None) or "").strip()
    include_deprecated = bool(getattr(args, "include_deprecated", False))
    include_sensitive = bool(getattr(args, "include_sensitive", False))
    limit = int(getattr(args, "limit", 200) or 200)

    out: list[OperationCommand] = []
    for c in load_allowlisted_operation_commands():
        if area and c.area != area:
            continue
        if method and c.method != method:
            continue
        if (not include_deprecated) and bool(c.deprecated):
            continue
        if (not include_sensitive) and str(c.sensitivity) != "none":
            continue
        if tag and tag not in str(c.tags or "").lower():
            continue
        if contains:
            hay = " ".join(
                [
                    c.area,
                    c.op_key,
                    c.operation_id or "",
                    c.method,
                    c.path_template,
                    c.summary,
                    c.tags,
                ]
            ).lower()
            if contains not in hay:
                continue
        out.append(c)
        if len(out) >= limit:
            break

    ctx["out"].emit(
        {
            "ok": True,
            "count": len(out),
            "operations": [
                {
                    "area": c.area,
                    "op_key": c.op_key,
                    "command": c.command,
                    "operation_id": c.operation_id,
                    "method": c.method,
                    "path_template": c.path_template,
                    "summary": c.summary,
                    "tags": c.tags,
                    "deprecated": c.deprecated,
                    "api_token_groups": c.api_token_groups,
                    "sensitivity": c.sensitivity,
                }
                for c in out
            ],
        }
    )
    return 0


def cmd_operations_show(args, ctx) -> int:
    area = str(getattr(args, "area", "") or "").strip()
    op_key = str(getattr(args, "op", "") or "").strip()
    if not area:
        raise ValidationError("Missing --area")
    if not op_key:
        raise ValidationError("Missing --op")
    c = _find_by_area_key(area=area, op_key=op_key)
    if not c:
        raise ValidationError(f"Operation not found in local allowlist: area={area!r} op={op_key!r}")
    ctx["out"].emit(
        {
            "ok": True,
            "operation": {
                "area": c.area,
                "op_key": c.op_key,
                "command": c.command,
                "operation_id": c.operation_id,
                "method": c.method,
                "path_template": c.path_template,
                "summary": c.summary,
                "tags": c.tags,
                "deprecated": c.deprecated,
                "api_token_groups": c.api_token_groups,
                "sensitivity": c.sensitivity,
            },
        }
    )
    return 0

