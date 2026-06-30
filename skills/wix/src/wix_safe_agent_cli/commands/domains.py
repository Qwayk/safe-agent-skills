from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ..authz import resolve_auth_mode
from ..errors import ValidationError
from ..http import HttpClient


def _read_json_arg(raw: Any, field: str) -> Any:
    if raw is None:
        return None
    if not isinstance(raw, str):
        raise ValidationError(f"--{field} must be a JSON string, JSON file path, or omitted")

    text = raw.strip()
    if not text:
        raise ValidationError(f"--{field} cannot be empty")

    if text.startswith("@"):
        path = Path(text[1:])
        if not path.exists():
            raise ValidationError(f"--{field} file not found: {path}")
        text = path.read_text(encoding="utf-8").strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValidationError(f"Invalid JSON for --{field}: {exc.msg}") from exc


def _coerce_required_text(raw: Any, *, field: str) -> str:
    if raw is None:
        raise ValidationError(f"Missing --{field}")
    if not isinstance(raw, str):
        raise ValidationError(f"--{field} must be a string")

    value = raw.strip()
    if not value:
        raise ValidationError(f"--{field} cannot be empty")
    return value


def _coerce_optional_text(raw: Any, *, field: str) -> str | None:
    if raw is None:
        return None
    if not isinstance(raw, str):
        raise ValidationError(f"--{field} must be a string")
    value = raw.strip()
    if not value:
        return None
    return value


def _coerce_text_list_without_dot(raw: Any, *, field: str) -> list[str] | None:
    if raw is None:
        return None

    value = _read_json_arg(raw, field=field)
    if not isinstance(value, list):
        raise ValidationError(f"--{field} must be a JSON array")
    if len(value) > 10:
        raise ValidationError(f"--{field} must contain at most 10 values")

    tlds: list[str] = []
    for i, item in enumerate(value):
        if not isinstance(item, str):
            raise ValidationError(f"--{field}[{i}] must be a string")
        value_i = item.strip()
        if not value_i:
            raise ValidationError(f"--{field}[{i}] cannot be empty")
        if value_i.startswith("."):
            raise ValidationError(f"--{field}[{i}] must not start with a leading dot")
        tlds.append(value_i)
    return tlds


def _coerce_int_in_range(raw: Any, *, field: str, minimum: int, maximum: int) -> int | None:
    if raw is None:
        return None
    if isinstance(raw, bool):
        raise ValidationError(f"--{field} must be an integer")
    if isinstance(raw, int):
        value = raw
    elif isinstance(raw, str):
        text = raw.strip()
        if not text:
            raise ValidationError(f"--{field} must be an integer")
        try:
            value = int(text)
        except ValueError as exc:
            raise ValidationError(f"--{field} must be an integer") from exc
    else:
        raise ValidationError(f"--{field} must be an integer")

    if value < minimum or value > maximum:
        raise ValidationError(f"--{field} must be between {minimum} and {maximum}")
    return value


def _coerce_domain(raw: Any) -> str:
    domain = _coerce_required_text(raw, field="domain")
    if "." not in domain:
        raise ValidationError("--domain must include a TLD (for example, example.com)")
    if domain.startswith(".") or domain.endswith("."):
        raise ValidationError("--domain must not start or end with a dot")
    return domain


def _build_check_params(*, domain: str) -> dict[str, Any]:
    return {"domain": domain}


def _build_suggest_params(
    *,
    query: str,
    tlds: list[str] | None,
    paging_limit: int | None,
    cursor: str | None,
    max_length: int | None,
) -> dict[str, Any]:
    params: dict[str, Any] = {"query": query}
    if tlds is not None:
        params["tlds"] = tlds
    if paging_limit is not None:
        params["paging.limit"] = paging_limit
    if cursor is not None:
        params["paging.cursor"] = cursor
    if max_length is not None:
        params["maxLength"] = max_length
    return params


def _request_json(
    *,
    method: str,
    base_url: str,
    path: str,
    headers: dict[str, str],
    params: dict[str, Any] | None,
    json_body: dict[str, Any] | None,
    timeout_s: float,
    verbose: bool,
) -> dict[str, Any]:
    request_headers = dict(headers)
    if method.upper() != "GET":
        request_headers["Content-Type"] = "application/json"

    client = HttpClient(timeout_s=timeout_s, verbose=verbose, user_agent="wix-safe-agent-cli")
    response = client.request(
        method=method,
        url=base_url.rstrip("/") + "/" + path.lstrip("/"),
        headers=request_headers,
        params=params,
        json_body=json_body,
    )

    payload = response.json()
    if not isinstance(payload, dict):
        raise ValidationError("Wix API returned a non-object JSON response")
    return payload


def cmd_domains_check_availability(args, ctx) -> int:
    try:
        domain = _coerce_domain(getattr(args, "domain", None))

        auth = resolve_auth_mode(
            cfg=ctx["cfg"],
            env_file=str(ctx["env_file"]),
            verbose=bool(ctx.get("verbose")),
            command_family="domains",
        )

        payload = _request_json(
            method="GET",
            base_url=ctx["cfg"].base_url,
            path="/domain-search/v2/check-domain-availability",
            headers=auth["headers"],
            params=_build_check_params(domain=domain),
            json_body=None,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )

        out = {
            "ok": True,
            "method": "domains.check_availability",
            "auth_mode": auth["mode"],
            "request": {
                "method": "GET",
                "path": "/domain-search/v2/check-domain-availability",
                "params": {"domain": domain},
            },
            "response": payload,
        }
        ctx["audit"].write("domains.check_availability", out)
        ctx["out"].emit(out)
        return 0
    except ValidationError as exc:
        out = {"ok": False, "error": str(exc), "error_type": "ValidationError"}
        ctx["out"].emit(out)
        return 1
    except RuntimeError as exc:
        out = {"ok": False, "error": str(exc), "error_type": exc.__class__.__name__}
        ctx["out"].emit(out)
        return 1


def cmd_domains_suggest(args, ctx) -> int:
    try:
        query = _coerce_required_text(getattr(args, "query", None), field="query")
        tlds = _coerce_text_list_without_dot(getattr(args, "tlds_json", None), field="tlds-json")
        paging_limit = _coerce_int_in_range(
            getattr(args, "paging_limit", None), field="paging-limit", minimum=1, maximum=20
        )
        cursor = _coerce_optional_text(getattr(args, "cursor", None), field="cursor")
        max_length = _coerce_int_in_range(getattr(args, "max_length", None), field="max-length", minimum=3, maximum=63)

        auth = resolve_auth_mode(
            cfg=ctx["cfg"],
            env_file=str(ctx["env_file"]),
            verbose=bool(ctx.get("verbose")),
            command_family="domains",
        )

        params = _build_suggest_params(
            query=query,
            tlds=tlds,
            paging_limit=paging_limit,
            cursor=cursor,
            max_length=max_length,
        )

        payload = _request_json(
            method="GET",
            base_url=ctx["cfg"].base_url,
            path="/domain-search/v2/suggest-domains",
            headers=auth["headers"],
            params=params,
            json_body=None,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )

        out = {
            "ok": True,
            "method": "domains.suggest",
            "auth_mode": auth["mode"],
            "request": {
                "method": "GET",
                "path": "/domain-search/v2/suggest-domains",
                "params": params,
            },
            "response": payload,
        }
        ctx["audit"].write("domains.suggest", out)
        ctx["out"].emit(out)
        return 0
    except ValidationError as exc:
        out = {"ok": False, "error": str(exc), "error_type": "ValidationError"}
        ctx["out"].emit(out)
        return 1
    except RuntimeError as exc:
        out = {"ok": False, "error": str(exc), "error_type": exc.__class__.__name__}
        ctx["out"].emit(out)
        return 1
