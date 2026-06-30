from __future__ import annotations

import json
from datetime import datetime, date, timedelta
from typing import Any

from ..authz import resolve_auth_mode
from ..errors import ValidationError
from ..http import HttpClient

_ALLOWED_MEASUREMENT_TYPES = {
    "TOTAL_SALES",
    "TOTAL_ORDERS",
    "CLICKS_TO_CONTACT",
    "TOTAL_SESSIONS",
    "TOTAL_FORMS_SUBMITTED",
    "TOTAL_UNIQUE_VISITORS",
}


def _coerce_local_date(raw: Any, *, field: str) -> tuple[str, date]:
    if raw is None:
        raise ValidationError(f"Missing --{field}")
    if not isinstance(raw, str):
        raise ValidationError(f"--{field} must be in YYYY-MM-DD format")

    value = raw.strip()
    if not value:
        raise ValidationError(f"Missing --{field}")

    try:
        parsed = datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError as exc:
        raise ValidationError(f"--{field} must be in YYYY-MM-DD format") from exc

    if field == "start-date":
        today = date.today()
        if parsed < today - timedelta(days=61):
            raise ValidationError("start-date cannot be more than 61 days before today")
    return value, parsed


def _coerce_measurement_types(raw: Any) -> list[str]:
    if raw is None:
        raise ValidationError("Missing --measurement-types-json")
    if not isinstance(raw, str):
        raise ValidationError("--measurement-types-json must be a JSON array")

    text = raw.strip()
    if not text:
        raise ValidationError("--measurement-types-json cannot be empty")

    try:
        values = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValidationError(f"Invalid JSON for --measurement-types-json: {exc.msg}") from exc

    if not isinstance(values, list):
        raise ValidationError("--measurement-types-json must be a JSON array")
    if not values:
        raise ValidationError("--measurement-types-json must include at least one measurement type")

    normalized: list[str] = []
    seen: set[str] = set()
    for raw_value in values:
        if not isinstance(raw_value, str):
            raise ValidationError("All measurement type values must be strings")
        value = raw_value.strip()
        if not value:
            raise ValidationError("Measurement type values cannot be empty")
        if value not in _ALLOWED_MEASUREMENT_TYPES:
            raise ValidationError(
                f"Invalid measurement type '{value}'. Allowed: {', '.join(sorted(_ALLOWED_MEASUREMENT_TYPES))}"
            )
        if value in seen:
            continue
        seen.add(value)
        normalized.append(value)

    return normalized


def _coerce_optional_time_zone(raw: Any) -> str | None:
    if raw is None:
        return None
    if not isinstance(raw, str):
        raise ValidationError("--time-zone must be a string")
    value = raw.strip()
    if not value:
        raise ValidationError("--time-zone cannot be empty")
    return value


def _coerce_request_params(
    *,
    start_date: str,
    end_date: str,
    measurement_types: list[str],
    time_zone: str | None,
) -> dict[str, Any]:
    params: dict[str, Any] = {
        "dateRange.startDate": start_date,
        "dateRange.endDate": end_date,
        "measurementTypes": measurement_types,
    }
    if time_zone is not None:
        params["timeZone"] = time_zone
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


def cmd_analytics_data_get(args, ctx) -> int:
    try:
        start_date, start_date_parsed = _coerce_local_date(getattr(args, "start_date", None), field="start-date")
        end_date, end_date_parsed = _coerce_local_date(getattr(args, "end_date", None), field="end-date")
        if end_date_parsed < start_date_parsed:
            raise ValidationError("--end-date must be the same as or after --start-date")

        measurement_types = _coerce_measurement_types(getattr(args, "measurement_types_json", None))
        time_zone = _coerce_optional_time_zone(getattr(args, "time_zone", None))

        params = _coerce_request_params(
            start_date=start_date,
            end_date=end_date,
            measurement_types=measurement_types,
            time_zone=time_zone,
        )

        auth = resolve_auth_mode(
            cfg=ctx["cfg"],
            env_file=str(ctx["env_file"]),
            verbose=bool(ctx.get("verbose")),
            command_family="analytics-data",
        )
        request_path = "/analytics/v2/site-analytics/data"
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
            method="analytics-data.get",
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
