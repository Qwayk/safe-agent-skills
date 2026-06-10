from __future__ import annotations

import dataclasses
import json
from pathlib import Path
from typing import Any, Iterable


@dataclasses.dataclass(frozen=True)
class SecurityAlternative:
    """
    One alternative in an OpenAPI `security` requirement list.
    Example: {"OAuth2UserToken": ["tweet.read", "users.read"]}.
    """

    scheme: str
    scopes: tuple[str, ...]


@dataclasses.dataclass(frozen=True)
class OperationSpec:
    operation_id: str
    method: str
    path: str
    tags: tuple[str, ...]
    security: tuple[tuple[SecurityAlternative, ...], ...]
    required_path_params: tuple[str, ...]
    required_request_body: bool

    def security_repr(self) -> str:
        if not self.security:
            return "none"
        alts: list[str] = []
        for alt in self.security:
            parts: list[str] = []
            for req in alt:
                # Must not contain `]` because official inventory lines use `[...]` wrappers.
                scopes = ",".join(req.scopes)
                parts.append(f"{req.scheme}{{{scopes}}}")
            alts.append("+".join(parts))
        return "||".join(alts)


def load_openapi_snapshot(path: Path) -> dict[str, Any]:
    obj = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(obj, dict):
        raise RuntimeError("OpenAPI snapshot must be a JSON object")
    return obj


def _merge_parameters(*param_lists: Iterable[Any]) -> list[dict[str, Any]]:
    merged: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for raw_list in param_lists:
        if not raw_list:
            continue
        if not isinstance(raw_list, list):
            continue
        for p in raw_list:
            if not isinstance(p, dict):
                continue
            name = str(p.get("name") or "").strip()
            loc = str(p.get("in") or "").strip()
            if not name or not loc:
                continue
            key = (loc, name)
            if key in seen:
                continue
            seen.add(key)
            merged.append(p)
    return merged


def _extract_security(
    *,
    operation_obj: dict[str, Any],
    global_security: Any,
) -> tuple[tuple[SecurityAlternative, ...], ...]:
    sec_raw = operation_obj.get("security")
    if sec_raw is None:
        sec_raw = global_security

    if sec_raw is None:
        return ()
    if not isinstance(sec_raw, list):
        return ()

    out: list[tuple[SecurityAlternative, ...]] = []
    for alt in sec_raw:
        if not isinstance(alt, dict):
            continue
        reqs: list[SecurityAlternative] = []
        for scheme, scopes_raw in alt.items():
            scheme_name = str(scheme or "").strip()
            if not scheme_name:
                continue
            scopes: list[str] = []
            if isinstance(scopes_raw, list):
                for s in scopes_raw:
                    if isinstance(s, str) and s.strip():
                        scopes.append(s.strip())
            reqs.append(SecurityAlternative(scheme=scheme_name, scopes=tuple(sorted(scopes))))
        reqs_sorted = tuple(sorted(reqs, key=lambda r: (r.scheme, r.scopes)))
        out.append(reqs_sorted)
    return tuple(out)


def extract_operations(openapi_obj: dict[str, Any]) -> list[OperationSpec]:
    paths = openapi_obj.get("paths")
    if not isinstance(paths, dict):
        raise RuntimeError("OpenAPI snapshot missing paths")

    global_security = openapi_obj.get("security")

    out: list[OperationSpec] = []
    for path, path_item in paths.items():
        if not isinstance(path_item, dict):
            continue
        path_level_params = path_item.get("parameters")

        for method, op in path_item.items():
            ml = str(method).lower()
            if ml not in {"get", "post", "put", "patch", "delete", "head"}:
                continue
            if not isinstance(op, dict):
                continue
            operation_id = str(op.get("operationId") or "").strip()
            if not operation_id:
                continue

            tags_raw = op.get("tags") or []
            tags = tuple(sorted([t.strip() for t in tags_raw if isinstance(t, str) and t.strip()]))

            params = _merge_parameters(path_level_params, op.get("parameters"))
            required_path_params: list[str] = []
            for p in params:
                if str(p.get("in") or "") != "path":
                    continue
                name = str(p.get("name") or "").strip()
                if not name:
                    continue
                if bool(p.get("required")):
                    required_path_params.append(name)
            required_path_params_sorted = tuple(sorted(set(required_path_params)))

            request_body = op.get("requestBody")
            required_request_body = False
            if isinstance(request_body, dict):
                required_request_body = bool(request_body.get("required"))

            sec = _extract_security(operation_obj=op, global_security=global_security)

            out.append(
                OperationSpec(
                    operation_id=operation_id,
                    method=ml.upper(),
                    path=str(path),
                    tags=tags,
                    security=sec,
                    required_path_params=required_path_params_sorted,
                    required_request_body=required_request_body,
                )
            )

    out_sorted = sorted(out, key=lambda o: (o.operation_id, o.method, o.path))
    return out_sorted


def official_operations_lines(ops: list[OperationSpec]) -> list[str]:
    lines: list[str] = []
    for op in ops:
        tags = ",".join(op.tags) if op.tags else ""
        sec = op.security_repr()
        line = f"{op.method} {op.path} {op.operation_id} [tags={tags}] [security={sec}]"
        lines.append(line)
    return lines


def parse_official_operations_text(text: str) -> list[str]:
    """
    Returns normalized, non-empty lines (no trailing whitespace).
    """
    out: list[str] = []
    for raw in (text or "").splitlines():
        line = raw.rstrip()
        if not line:
            continue
        out.append(line)
    return out


def auth_mode_for_operation(op: OperationSpec) -> str:
    """
    Returns: none | bearer | oauth2 | oauth1 | unknown

    Notes:
    - The pinned X OpenAPI snapshot includes `BearerToken`, `OAuth2UserToken`, and `UserToken`.
    - `UserToken` is treated as OAuth 1.0a (unsupported by this tool as of v0.1.x).
    """
    if not op.security:
        return "none"
    schemes: set[str] = set()
    for alt in op.security:
        for req in alt:
            schemes.add(req.scheme)
    if "OAuth2UserToken" in schemes:
        return "oauth2"
    if "BearerToken" in schemes:
        return "bearer"
    if "UserToken" in schemes:
        return "oauth1"
    return "unknown"
