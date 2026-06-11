from __future__ import annotations

from ..inventory import OperationSpec, load_operation_specs, require_operation


def _matches(spec: OperationSpec, *, contains: str, tag: str, method: str, area: str, include_deprecated: bool, include_sensitive: bool) -> bool:
    if area and spec.area != area:
        return False
    if method and spec.method != method:
        return False
    if (not include_deprecated) and spec.deprecated:
        return False
    if (not include_sensitive) and spec.sensitivity != "none":
        return False
    if tag and tag not in spec.summary.lower() and tag not in spec.api_group.lower():
        return False
    if contains:
        hay = " ".join(
            [
                spec.area,
                spec.op_key,
                spec.operation_id,
                spec.method,
                spec.path_template,
                spec.summary,
                spec.api_group,
                spec.source_doc,
            ]
        ).lower()
        if contains not in hay:
            return False
    return True


def cmd_operations_list(args, ctx) -> int:
    contains = str(getattr(args, "contains", "") or "").strip().lower()
    tag = str(getattr(args, "tag", "") or "").strip().lower()
    method = str(getattr(args, "method", "") or "").strip().upper()
    area = str(getattr(args, "area", "") or "").strip()
    include_deprecated = bool(getattr(args, "include_deprecated", False))
    include_sensitive = bool(getattr(args, "include_sensitive", False))
    limit = int(getattr(args, "limit", 200) or 200)

    matches: list[dict[str, object]] = []
    for spec in load_operation_specs():
        if not _matches(
            spec,
            contains=contains,
            tag=tag,
            method=method,
            area=area,
            include_deprecated=include_deprecated,
            include_sensitive=include_sensitive,
        ):
            continue
        matches.append(
            {
                "area": spec.area,
                "op_key": spec.op_key,
                "command": spec.command,
                "operation_id": spec.operation_id,
                "method": spec.method,
                "path_template": spec.path_template,
                "summary": spec.summary,
                "api_group": spec.api_group,
                "auth_scope": spec.auth_scope,
                "input_style": spec.input_style,
                "sensitivity": spec.sensitivity,
                "read_like": spec.read_like,
                "body_required": spec.body_required,
                "beta": spec.beta,
                "gated": spec.gated,
                "deprecated": spec.deprecated,
            }
        )
        if len(matches) >= limit:
            break

    ctx["out"].emit({"ok": True, "count": len(matches), "operations": matches})
    return 0


def cmd_operations_show(args, ctx) -> int:
    spec = require_operation(
        area=str(getattr(args, "area", "") or "").strip(),
        op_key=str(getattr(args, "op", "") or "").strip(),
    )
    ctx["out"].emit(
        {
            "ok": True,
            "operation": {
                "area": spec.area,
                "op_key": spec.op_key,
                "command": spec.command,
                "operation_id": spec.operation_id,
                "method": spec.method,
                "path_template": spec.path_template,
                "summary": spec.summary,
                "api_group": spec.api_group,
                "source_doc": spec.source_doc,
                "auth_scope": spec.auth_scope,
                "input_style": spec.input_style,
                "sensitivity": spec.sensitivity,
                "read_like": spec.read_like,
                "body_required": spec.body_required,
                "beta": spec.beta,
                "gated": spec.gated,
                "deprecated": spec.deprecated,
                "fixed_form_fields": dict(spec.fixed_form_fields),
                "fixed_query": dict(spec.fixed_query),
                "path_defaults": dict(spec.path_defaults),
                "notes": spec.notes,
            },
        }
    )
    return 0
