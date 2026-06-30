from __future__ import annotations

from typing import Any

from ..authz import resolve_auth_mode
from ..errors import ValidationError
from ..http import HttpClient

_ALLOWED_ORDERS = {"date:asc", "date:desc"}


def _coerce_optional_string(raw: Any, *, field: str) -> str | None:
    if raw is None:
        return None
    if not isinstance(raw, str):
        raise ValidationError(f"--{field} must be a string")
    value = raw.strip()
    if not value:
        raise ValidationError(f"--{field} cannot be empty")
    return value


def _coerce_optional_int(raw: Any, *, field: str, minimum: int | None = None, maximum: int | None = None) -> int | None:
    if raw is None:
        return None
    try:
        value = int(raw)
    except (TypeError, ValueError) as exc:
        raise ValidationError(f"--{field} must be an integer") from exc
    if minimum is not None and value < minimum:
        raise ValidationError(f"--{field} must be at least {minimum}")
    if maximum is not None and value > maximum:
        raise ValidationError(f"--{field} must be at most {maximum}")
    return value


def _coerce_optional_bool(raw: Any, *, field: str) -> bool | None:
    if raw is None:
        return None
    if isinstance(raw, bool):
        return raw
    raise ValidationError(f"--{field} must be a boolean flag")


def _coerce_statuses(raw: Any) -> list[str] | None:
    if raw is None:
        return None
    if not isinstance(raw, list):
        raise ValidationError("--status must be supplied as repeated string flags")
    normalized: list[str] = []
    seen: set[str] = set()
    for item in raw:
        if not isinstance(item, str):
            raise ValidationError("--status values must be strings")
        value = item.strip()
        if not value:
            raise ValidationError("--status values cannot be empty")
        if value in seen:
            continue
        seen.add(value)
        normalized.append(value)
    return normalized or None


def _build_params(args) -> dict[str, Any]:
    params: dict[str, Any] = {}
    for attr, param_name, field in (
        ("from_created", "from", "from-created"),
        ("to_created", "to", "to-created"),
        ("payment_method", "paymentMethod", "payment-method"),
        ("payment_provider", "paymentProvider", "payment-provider"),
        ("currency", "currency", "currency"),
        ("from_updated", "fromUpdated", "from-updated"),
        ("to_updated", "toUpdated", "to-updated"),
        ("app_id", "appId", "app-id"),
    ):
        value = _coerce_optional_string(getattr(args, attr, None), field=field)
        if value is not None:
            params[param_name] = value

    limit = _coerce_optional_int(getattr(args, "limit", None), field="limit", minimum=0, maximum=1000)
    if limit is not None:
        params["limit"] = limit

    offset = _coerce_optional_int(getattr(args, "offset", None), field="offset", minimum=0)
    if offset is not None:
        params["offset"] = offset

    order = _coerce_optional_string(getattr(args, "order", None), field="order")
    if order is not None:
        if order not in _ALLOWED_ORDERS:
            raise ValidationError("--order must be date:asc or date:desc")
        params["order"] = order

    statuses = _coerce_statuses(getattr(args, "status", None))
    if statuses is not None:
        params["status"] = statuses

    include_refunds = _coerce_optional_bool(getattr(args, "include_refunds", None), field="include-refunds")
    if include_refunds is not None:
        params["includeRefunds"] = include_refunds

    ignore_totals = _coerce_optional_bool(getattr(args, "ignore_totals", None), field="ignore-totals")
    if ignore_totals is not None:
        params["ignoreTotals"] = ignore_totals

    return params


def _request_json(
    *,
    method: str,
    base_url: str,
    path: str,
    headers: dict[str, str],
    params: dict[str, Any],
    timeout_s: float,
    verbose: bool,
) -> dict[str, Any]:
    client = HttpClient(timeout_s=timeout_s, verbose=verbose, user_agent="wix-safe-agent-cli")
    response = client.request(
        method=method,
        url=base_url.rstrip("/") + "/" + path.lstrip("/"),
        headers=dict(headers),
        params=params,
        json_body=None,
    )
    payload = response.json()
    if not isinstance(payload, dict):
        raise ValidationError("Wix API returned a non-object JSON response")
    return payload


def _emit_success(
    *,
    method: str,
    auth_mode: str,
    request: dict[str, Any],
    response: dict[str, Any],
    ctx: dict[str, Any],
) -> None:
    out = {
        "ok": True,
        "method": method,
        "auth_mode": auth_mode,
        "request": request,
        "response": response,
    }
    ctx["audit"].write(method, out)
    ctx["out"].emit(out)


def cmd_payments_transactions_list(args, ctx) -> int:
    try:
        params = _build_params(args)
        auth = resolve_auth_mode(
            cfg=ctx["cfg"],
            env_file=str(ctx["env_file"]),
            verbose=bool(ctx.get("verbose")),
            command_family="payments",
        )
        request_path = "/payments/v2/transactions"
        payload = _request_json(
            method="GET",
            base_url=ctx["cfg"].base_url,
            path=request_path,
            headers=auth["headers"],
            params=params,
            timeout_s=float(ctx["cfg"].timeout_s),
            verbose=bool(ctx.get("verbose")),
        )
        _emit_success(
            method="payments.transactions-list",
            auth_mode=auth["mode"],
            request={"method": "GET", "path": request_path, "params": params},
            response=payload,
            ctx=ctx,
        )
        return 0
    except ValidationError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": "ValidationError"})
        return 1
    except RuntimeError as exc:
        ctx["out"].emit({"ok": False, "error": str(exc), "error_type": exc.__class__.__name__})
        return 1
