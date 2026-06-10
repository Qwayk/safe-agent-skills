from __future__ import annotations

import dataclasses
import json
import re
import time
from pathlib import Path
from typing import Any

from .errors import SafetyError, ValidationError
from .http import redact_headers, redact_query_params, redact_url
from .openapi_inventory import OperationSpec, extract_operations, load_openapi_snapshot
from .oauth_tokens import read_token_json, token_path_for_env_file
from .commands.write_safety import before_state_refusal_verification_plan, blocked_before_state, rollback_contract


def _utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def tool_root_path() -> Path:
    # .../src/x_api_tool/api_dispatch.py -> tool root is 3 levels up
    return Path(__file__).resolve().parents[2]


def openapi_snapshot_path() -> Path:
    return tool_root_path() / "docs" / "official_openapi_x_api_v2.json"


def load_operations_from_pinned_snapshot() -> list[OperationSpec]:
    snap = openapi_snapshot_path()
    if not snap.exists():
        raise RuntimeError(f"Missing pinned OpenAPI snapshot: {snap}")
    obj = load_openapi_snapshot(snap)
    return extract_operations(obj)


def operations_by_id(ops: list[OperationSpec]) -> dict[str, OperationSpec]:
    out: dict[str, OperationSpec] = {}
    for o in ops:
        out[o.operation_id] = o
    return out


_PATH_PARAM_RE = re.compile(r"{([a-zA-Z0-9_\\-]+)}")


def _parse_kv_pairs(pairs: list[str] | None) -> dict[str, str]:
    out: dict[str, str] = {}
    for raw in pairs or []:
        s = str(raw or "").strip()
        if not s:
            continue
        if "=" not in s:
            raise ValidationError(f"Invalid key=value pair: {s}")
        k, v = s.split("=", 1)
        k = k.strip()
        v = v.strip()
        if not k:
            raise ValidationError(f"Invalid key=value pair (empty key): {s}")
        out[k] = v
    return out


def _load_json_arg(value: str | None) -> Any:
    if value is None:
        return None
    s = str(value).strip()
    if not s:
        return None
    p = Path(s)
    if p.exists() and p.is_file():
        return json.loads(p.read_text(encoding="utf-8"))
    return json.loads(s)


def _deep_merge_dicts(a: dict[str, Any], b: dict[str, Any]) -> dict[str, Any]:
    out = dict(a)
    for k, v in b.items():
        out[k] = v
    return out


def substitute_path_params(path_template: str, values: dict[str, str]) -> tuple[str, list[str]]:
    missing: list[str] = []

    def repl(m: re.Match[str]) -> str:
        name = m.group(1)
        if name in values:
            return str(values[name])
        missing.append(name)
        return "{" + name + "}"

    filled = _PATH_PARAM_RE.sub(repl, path_template)
    missing_sorted = sorted(set(missing))
    return filled, missing_sorted


def join_base_url_and_path(base_url: str, path_with_leading_slash: str) -> str:
    """
    Joins a configured base URL and an OpenAPI path safely.

    The pinned X OpenAPI snapshot uses paths prefixed with `/2/...`. Many users/configs prefer
    base URLs like `https://api.x.com/2`. This helper avoids producing `.../2/2/...`.
    """
    base = str(base_url or "").rstrip("/")
    path = str(path_with_leading_slash or "")
    if not path.startswith("/"):
        path = "/" + path

    if base.endswith("/2") and path.startswith("/2/"):
        path = path[len("/2") :]
    return base + path


@dataclasses.dataclass(frozen=True)
class AuthSelection:
    mode: str  # none|bearer|oauth2|unsupported
    scheme: str | None
    token_present: bool


def _token_from_oauth_state(env_file: str) -> str | None:
    tok_path = token_path_for_env_file(env_file)
    data = read_token_json(tok_path)
    if not data:
        return None
    tok = data.get("access_token")
    if isinstance(tok, str) and tok.strip():
        return tok.strip()
    return None


def select_auth_for_operation(
    *,
    op: OperationSpec,
    requested: str,
    env_file: str,
    env_bearer_token: str | None,
    oauth2_token_present: bool,
) -> AuthSelection:
    requested = (requested or "auto").strip()
    if requested not in {"auto", "app", "user", "none"}:
        raise ValidationError("Invalid --auth (must be auto|app|user|none)")

    allowed_schemes: set[str] = set()
    for alt in op.security:
        for req in alt:
            allowed_schemes.add(req.scheme)

    if not op.security:
        return AuthSelection(mode="none", scheme=None, token_present=False)

    def allow(scheme: str) -> bool:
        return scheme in allowed_schemes

    if requested == "none":
        return AuthSelection(mode="none", scheme=None, token_present=False)

    if requested == "app":
        if not allow("BearerToken"):
            return AuthSelection(mode="unsupported", scheme="BearerToken", token_present=bool(env_bearer_token))
        return AuthSelection(mode="bearer", scheme="BearerToken", token_present=bool(env_bearer_token))

    if requested == "user":
        if allow("OAuth2UserToken"):
            return AuthSelection(mode="oauth2", scheme="OAuth2UserToken", token_present=oauth2_token_present)
        # Some operations list `UserToken` as an alternative. Treat it as unsupported (OAuth 1.0a).
        if allow("UserToken"):
            return AuthSelection(mode="unsupported", scheme="UserToken", token_present=False)
        return AuthSelection(mode="unsupported", scheme=None, token_present=False)

    # auto
    if allow("OAuth2UserToken") and oauth2_token_present:
        return AuthSelection(mode="oauth2", scheme="OAuth2UserToken", token_present=True)
    if allow("BearerToken") and env_bearer_token:
        return AuthSelection(mode="bearer", scheme="BearerToken", token_present=True)
    if allow("OAuth2UserToken"):
        return AuthSelection(mode="oauth2", scheme="OAuth2UserToken", token_present=False)
    if allow("BearerToken"):
        return AuthSelection(mode="bearer", scheme="BearerToken", token_present=bool(env_bearer_token))
    if allow("UserToken"):
        return AuthSelection(mode="unsupported", scheme="UserToken", token_present=False)
    return AuthSelection(mode="unsupported", scheme=None, token_present=False)


def build_api_call_plan(
    *,
    tool: str,
    tool_version: str,
    env_fingerprint: str,
    op: OperationSpec,
    base_url: str,
    env_file: str,
    env_bearer_token: str | None,
    auth: str,
    path_json: str | None,
    query_json: str | None,
    body_json: str | None,
    path_pairs: list[str] | None,
    query_pairs: list[str] | None,
    file_pairs: list[str] | None,
) -> dict[str, Any]:
    path_dict_from_json = _load_json_arg(path_json)
    query_dict_from_json = _load_json_arg(query_json)
    body_obj = _load_json_arg(body_json)

    if path_dict_from_json is None:
        path_dict_from_json = {}
    if query_dict_from_json is None:
        query_dict_from_json = {}

    if not isinstance(path_dict_from_json, dict):
        raise ValidationError("--path-json must be a JSON object (or a path to one)")
    if not isinstance(query_dict_from_json, dict):
        raise ValidationError("--query-json must be a JSON object (or a path to one)")
    if body_obj is not None and not isinstance(body_obj, dict):
        raise ValidationError("--body-json must be a JSON object (or a path to one)")

    path_dict = _deep_merge_dicts(
        {str(k): str(v) for k, v in path_dict_from_json.items()},
        _parse_kv_pairs(path_pairs),
    )
    query_dict = _deep_merge_dicts({str(k): v for k, v in query_dict_from_json.items()}, _parse_kv_pairs(query_pairs))

    files: dict[str, str] = {}
    for raw in file_pairs or []:
        s = str(raw or "").strip()
        if not s:
            continue
        if "=" not in s:
            raise ValidationError(f"Invalid file pair (field=path): {s}")
        field, path = s.split("=", 1)
        field = field.strip()
        path = path.strip()
        if not field or not path:
            raise ValidationError(f"Invalid file pair (field=path): {s}")
        files[field] = path

    filled_path, missing_path = substitute_path_params(op.path, path_dict)
    url = join_base_url_and_path(base_url, filled_path)

    oauth2_token_present = bool(_token_from_oauth_state(env_file))
    sel = select_auth_for_operation(
        op=op,
        requested=auth,
        env_file=env_file,
        env_bearer_token=env_bearer_token,
        oauth2_token_present=oauth2_token_present,
    )

    required_missing: list[dict[str, Any]] = []
    for name in op.required_path_params:
        if name not in path_dict:
            required_missing.append({"in": "path", "name": name})
    if op.required_request_body and body_obj is None:
        required_missing.append({"in": "body", "name": "requestBody"})

    required_missing_sorted = sorted(required_missing, key=lambda x: (x.get("in", ""), x.get("name", "")))

    headers: dict[str, str] = {}
    if sel.mode in {"bearer", "oauth2"}:
        headers["Authorization"] = "Bearer ***REDACTED***"

    plan = {
        "tool": tool,
        "version": tool_version,
        "generated_at_utc": _utc_now(),
        "env_fingerprint": env_fingerprint,
        "operation": {
            "operation_id": op.operation_id,
            "method": op.method,
            "path_template": op.path,
            "path_filled": filled_path,
            "url": redact_url(url),
            "tags": list(op.tags),
            "security": op.security_repr(),
        },
        "auth": {
            "requested": auth,
            "mode": sel.mode,
            "scheme": sel.scheme,
            "token_present": sel.token_present,
        },
        "inputs": {
            "path": dict(sorted(path_dict.items())),
            "query": dict(sorted((redact_query_params(query_dict) or {}).items())) if query_dict else {},
            "body": body_obj,
            "files": dict(sorted(files.items())),
        },
        "headers": redact_headers(headers) or {},
        "missing_required": required_missing_sorted,
        "dry_run": True,
        "safety_gates": {
            "get_requires_live": True,
            "write_requires_apply_yes": True,
            "delete_requires_ack_irreversible": True,
        },
    }
    if op.method.upper() not in {"GET", "HEAD"}:
        plan["before_state"] = blocked_before_state(
            action=f"api.{op.operation_id}",
            provider_write={
                "service": "X API",
                "operation_id": op.operation_id,
                "method": op.method,
                "path": op.path,
            },
        )
        plan["verification_plan"] = before_state_refusal_verification_plan()
        plan["rollback"] = rollback_contract(requires_ack_irreversible=op.method.upper() == "DELETE")
    return plan


def validate_plan_for_apply(plan: dict[str, Any], *, op_id: str, ctx_base_url: str) -> None:
    if not isinstance(plan, dict):
        raise ValidationError("Plan file must be a JSON object")
    env = plan.get("env_fingerprint")
    if str(env or "") != str(ctx_base_url):
        raise SafetyError("Refused: plan env_fingerprint does not match current environment")
    op = plan.get("operation") if isinstance(plan.get("operation"), dict) else {}
    plan_op_id = str(op.get("operation_id") or "").strip()
    if plan_op_id != op_id:
        raise SafetyError("Refused: plan operation_id does not match requested operation")
