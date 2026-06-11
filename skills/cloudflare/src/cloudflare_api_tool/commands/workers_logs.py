from __future__ import annotations

import json
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from ..errors import SafetyError, ValidationError
from ._storage_db_common import (
    base_plan,
    base_receipt,
    build_json_body_meta,
    emit_plan,
    emit_receipt,
    require_apply,
    require_token,
    resolve_account_id,
    verify_and_require_plan,
    write_raw_response_to_file,
)


def _opt_str(v) -> str | None:  # noqa: ANN001
    s = str(v or "").strip()
    return s or None


def _parse_time_arg_ms(value: str | None, *, flag: str) -> int | None:
    """
    Parse either:
    - unix-ms integer string, or
    - RFC3339 timestamp (best-effort; naive timestamps treated as UTC).
    """
    s = str(value or "").strip()
    if not s:
        return None

    if s.isdigit():
        try:
            return int(s)
        except Exception:
            raise ValidationError(f"Invalid {flag}: expected unix-ms integer or RFC3339") from None

    t = s
    if t.endswith("Z"):
        t = t[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(t)
    except Exception:
        raise ValidationError(f"Invalid {flag}: expected unix-ms integer or RFC3339") from None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return int(dt.timestamp() * 1000)


@dataclass(frozen=True)
class _Timeframe:
    from_ms: int
    to_ms: int


def _resolve_timeframe(args) -> _Timeframe:  # noqa: ANN001
    from_ms = _parse_time_arg_ms(_opt_str(getattr(args, "from_ts", None)), flag="--from")
    to_ms = _parse_time_arg_ms(_opt_str(getattr(args, "to_ts", None)), flag="--to")
    now_ms = int(time.time() * 1000)
    if to_ms is None:
        to_ms = now_ms
    if from_ms is None:
        from_ms = to_ms - 24 * 60 * 60 * 1000
    if from_ms > to_ms:
        raise ValidationError("--from must be <= --to")
    return _Timeframe(from_ms=int(from_ms), to_ms=int(to_ms))


def _needle_obj(value: str, *, is_regex: bool = False, match_case: bool = False) -> dict[str, Any]:
    v = str(value or "")
    if not v.strip():
        raise ValidationError("Needle value must be non-empty")
    return {"value": v, "isRegex": bool(is_regex), "matchCase": bool(match_case)}


def _extract_key_names(result: Any) -> list[str]:
    keys: list[str] = []
    if isinstance(result, list):
        for it in result:
            if isinstance(it, str):
                k = it.strip()
                if k:
                    keys.append(k)
                continue
            if isinstance(it, dict):
                for cand in ("key", "name", "value", "field"):
                    v = it.get(cand)
                    if v is not None and str(v).strip():
                        keys.append(str(v).strip())
                        break
    elif isinstance(result, dict):
        for cand in ("keys", "result", "data"):
            v = result.get(cand)
            if isinstance(v, list):
                keys.extend(_extract_key_names(v))
                break
    # Preserve order, de-dupe.
    out: list[str] = []
    seen: set[str] = set()
    for k in keys:
        if k not in seen:
            out.append(k)
            seen.add(k)
    return out


def _score_request_id_key(key: str) -> int:
    raw = str(key or "").strip()
    k = raw.lower()
    if not raw:
        return 0

    # Prefer the most direct / user-facing request id fields first.
    # In our apps, UI "Error ID" typically maps to a top-level `requestId`
    # emitted by structured logs (not `$metadata.requestId`).
    if k in {"x-request-id", "x_request_id"}:
        return 2000
    if k in {"requestid", "request_id"}:
        return 1900
    if k.endswith(".requestid") or k.endswith(".request_id"):
        # Prefer worker/runtime request ids over metadata.
        if k.startswith("$workers."):
            return 1850
        if k.startswith("$metadata."):
            return 1200
        return 1500

    if "x-request-id" in k:
        return 1000
    if "x_request_id" in k:
        return 995
    if "request_id" in k:
        return 900
    if "requestid" in k:
        return 850
    if "request.id" in k:
        return 830
    if k.endswith("request"):
        return 200
    return 0


def _pick_best_key(keys: list[str], *, scorer) -> str | None:  # noqa: ANN001
    best: tuple[int, str] | None = None
    for raw in keys:
        k = str(raw or "").strip()
        if not k:
            continue
        score = int(scorer(k))
        if score <= 0:
            continue
        t = (score, k)
        if best is None:
            best = t
            continue
        if t[0] > best[0]:
            best = t
            continue
        if t[0] == best[0] and t[1] < best[1]:
            best = t
    return best[1] if best else None


def _score_script_name_key(key: str) -> int:
    k = str(key or "").strip().lower()
    if not k:
        return 0
    if "script_name" in k:
        return 1000
    if "scriptname" in k:
        return 950
    if "script" in k and "name" in k:
        return 900
    if k == "script":
        return 400
    return 0


def _telemetry_keys_body(
    *,
    tf: _Timeframe,
    datasets: list[str],
    limit: int | None,
    key_needle: str | None,
    needle: str | None,
) -> dict[str, Any]:
    body: dict[str, Any] = {
        "datasets": list(datasets),
        "filters": [],
        "timeframe": {"from": int(tf.from_ms), "to": int(tf.to_ms)},
    }
    if limit is not None:
        body["limit"] = int(limit)
    if key_needle:
        body["keyNeedle"] = _needle_obj(key_needle)
    if needle:
        body["needle"] = _needle_obj(needle)
    return body


def _telemetry_path(*, account_id: str, endpoint: str) -> str:
    return f"/accounts/{account_id}/workers/observability/telemetry/{endpoint}"


def _telemetry_values_body(
    *,
    tf: _Timeframe,
    datasets: list[str],
    key: str,
    value_type: str,
    limit: int | None,
    needle: str | None,
) -> dict[str, Any]:
    vt = str(value_type or "").strip()
    if vt not in {"string", "number", "boolean"}:
        raise ValidationError("--type must be one of: string, number, boolean")
    body: dict[str, Any] = {
        "datasets": list(datasets),
        "filters": [],
        "timeframe": {"from": int(tf.from_ms), "to": int(tf.to_ms)},
        "key": str(key),
        "type": vt,
    }
    if limit is not None:
        body["limit"] = int(limit)
    if needle:
        body["needle"] = _needle_obj(needle)
    return body


def _telemetry_query_body(
    *,
    tf: _Timeframe,
    datasets: list[str],
    filters: list[dict[str, Any]],
    limit: int | None,
    needle: dict[str, Any] | None,
) -> dict[str, Any]:
    params: dict[str, Any] = {
        "datasets": list(datasets),
        "filters": list(filters),
        "filterCombination": "and",
    }
    if limit is not None:
        params["limit"] = int(limit)
    if needle is not None:
        params["needle"] = needle
    return {
        # OpenAPI schema requires queryId. Use a conventional temporary value and rely on parameters for the actual query.
        "queryId": "temporary",
        "timeframe": {"from": int(tf.from_ms), "to": int(tf.to_ms)},
        "view": "events",
        "parameters": params,
    }


def _post_telemetry_and_write(
    *,
    ctx: dict,
    account_id: str,
    endpoint: str,
    body: dict[str, Any],
    out_path: str,
    overwrite: bool,
) -> tuple[dict[str, Any], Any]:
    path = _telemetry_path(account_id=account_id, endpoint=endpoint)
    resp = ctx["cf"].request_raw(
        "POST",
        path,
        json_body=body,
        headers={"content-type": "application/json"},
        retries=3,
    )
    wrote = write_raw_response_to_file(
        ctx=ctx,
        out_path=out_path,
        overwrite=overwrite,
        method="POST",
        http_status=int(resp.status),
        body=resp.body,
    )
    try:
        obj = json.loads(resp.body.decode("utf-8"))
    except Exception:
        obj = None
    return wrote, obj


def cmd_workers_logs_keys(args, ctx) -> int:
    """
    List available telemetry keys for Workers Observability Telemetry (sensitive; file-only).
    """
    require_token(ctx)
    account_id = resolve_account_id(args, ctx)
    out_path = str(getattr(args, "out", "") or "").strip()
    overwrite = bool(getattr(args, "overwrite", False))
    if not out_path:
        raise ValidationError("Missing --out")

    datasets = [str(s).strip() for s in (getattr(args, "dataset", None) or []) if str(s).strip()]
    tf = _resolve_timeframe(args)
    limit = getattr(args, "limit", None)
    limit_i = int(limit) if limit is not None else None
    key_needle = _opt_str(getattr(args, "key_needle", None))
    needle = _opt_str(getattr(args, "needle", None))

    body = _telemetry_keys_body(tf=tf, datasets=datasets, limit=limit_i, key_needle=key_needle, needle=needle)

    selector = {
        "account_id": account_id,
        "datasets": datasets,
        "timeframe": {"from_ms": tf.from_ms, "to_ms": tf.to_ms},
        "limit": limit_i,
        "out": out_path,
        "overwrite": overwrite,
    }
    plan = base_plan(
        ctx,
        selector=selector,
        risk_level="high",
        risk_reasons=[
            "This queries stored telemetry key metadata (may correlate to event fields).",
            "This writes the raw API response to a local file; results are never printed.",
            "This is a read-like POST (no Cloudflare state changes expected).",
        ],
    )
    plan["request"] = {
        "method": "POST",
        "path": _telemetry_path(account_id=account_id, endpoint="keys"),
        "sensitivity": "sensitive_read",
        "body_meta": build_json_body_meta(body, source="workers.logs.keys"),
        "out": out_path,
    }
    plan["proposed_changes"] = [{"resource": "local_file", "action": "write", "path": out_path, "reason": "workers_logs_keys"}]
    plan["verification_plan"] = ["Confirm output file exists and record size/sha256 locally."]
    plan["notes"].append("Results may include or correlate to PII; output is file-only and never printed.")

    if not bool(ctx.get("apply")):
        return emit_plan(ctx, command="workers.logs.keys", plan=plan)

    require_apply(ctx)
    verify_and_require_plan(ctx, plan=plan)

    wrote, obj = _post_telemetry_and_write(
        ctx=ctx, account_id=account_id, endpoint="keys", body=body, out_path=out_path, overwrite=overwrite
    )

    key_count: int | None = None
    try:
        if isinstance(obj, dict) and obj.get("success") is True:
            keys = _extract_key_names(obj.get("result"))
            key_count = len(keys)
    except Exception:
        key_count = None

    receipt = base_receipt(ctx, selector=selector, changed=False)
    receipt["output_file"] = wrote
    receipt["verification"] = {"ok": True, "method": "file_written", "details": {"keys_count": key_count}}
    receipt["notes"].append("Telemetry keys response is sensitive; body written to file only.")

    return emit_receipt(
        ctx,
        command="workers.logs.keys",
        receipt=receipt,
        extra={"keys_count": key_count, "out": wrote.get("out_rel") or wrote.get("out_path")},
    )


def cmd_workers_logs_values(args, ctx) -> int:
    """
    List telemetry values for a given key (sensitive; file-only).
    """
    require_token(ctx)
    account_id = resolve_account_id(args, ctx)
    out_path = str(getattr(args, "out", "") or "").strip()
    overwrite = bool(getattr(args, "overwrite", False))
    if not out_path:
        raise ValidationError("Missing --out")
    key = str(getattr(args, "key", "") or "").strip()
    value_type = str(getattr(args, "type", "") or "").strip()
    if not key:
        raise ValidationError("Missing --key")
    if not value_type:
        raise ValidationError("Missing --type")

    datasets = [str(s).strip() for s in (getattr(args, "dataset", None) or []) if str(s).strip()]
    tf = _resolve_timeframe(args)
    limit = getattr(args, "limit", None)
    limit_i = int(limit) if limit is not None else None
    needle = _opt_str(getattr(args, "needle", None))

    body = _telemetry_values_body(tf=tf, datasets=datasets, key=key, value_type=value_type, limit=limit_i, needle=needle)

    selector = {
        "account_id": account_id,
        "datasets": datasets,
        "key": key,
        "type": value_type,
        "timeframe": {"from_ms": tf.from_ms, "to_ms": tf.to_ms},
        "limit": limit_i,
        "out": out_path,
        "overwrite": overwrite,
    }
    plan = base_plan(
        ctx,
        selector=selector,
        risk_level="high",
        risk_reasons=[
            "This lists telemetry values for a key; values may include PII.",
            "This writes the raw API response to a local file; results are never printed.",
            "This is a read-like POST (no Cloudflare state changes expected).",
        ],
    )
    plan["request"] = {
        "method": "POST",
        "path": _telemetry_path(account_id=account_id, endpoint="values"),
        "sensitivity": "sensitive_read",
        "body_meta": build_json_body_meta(body, source="workers.logs.values"),
        "out": out_path,
    }
    plan["proposed_changes"] = [{"resource": "local_file", "action": "write", "path": out_path, "reason": "workers_logs_values"}]
    plan["verification_plan"] = ["Confirm output file exists and record size/sha256 locally."]
    plan["notes"].append("Values may include PII; output is file-only and never printed.")

    if not bool(ctx.get("apply")):
        return emit_plan(ctx, command="workers.logs.values", plan=plan)

    require_apply(ctx)
    verify_and_require_plan(ctx, plan=plan)

    wrote, obj = _post_telemetry_and_write(
        ctx=ctx, account_id=account_id, endpoint="values", body=body, out_path=out_path, overwrite=overwrite
    )

    values_count: int | None = None
    try:
        if isinstance(obj, dict) and obj.get("success") is True and isinstance(obj.get("result"), list):
            values_count = len(obj.get("result") or [])
    except Exception:
        values_count = None

    receipt = base_receipt(ctx, selector=selector, changed=False)
    receipt["output_file"] = wrote
    receipt["verification"] = {"ok": True, "method": "file_written", "details": {"values_count": values_count}}
    receipt["notes"].append("Telemetry values response is sensitive; body written to file only.")

    return emit_receipt(
        ctx,
        command="workers.logs.values",
        receipt=receipt,
        extra={"values_count": values_count, "out": wrote.get("out_rel") or wrote.get("out_path")},
    )


def cmd_workers_logs_search(args, ctx) -> int:
    """
    Search stored logs/events by Error ID (x-request-id) using Workers Observability Telemetry.
    """
    require_token(ctx)
    account_id = resolve_account_id(args, ctx)
    out_path = str(getattr(args, "out", "") or "").strip()
    overwrite = bool(getattr(args, "overwrite", False))
    if not out_path:
        raise ValidationError("Missing --out")
    error_id = str(getattr(args, "error_id", "") or "").strip()
    if not error_id:
        raise ValidationError("Missing --error-id")

    script_name = _opt_str(getattr(args, "script_name", None))
    request_id_key_override = _opt_str(getattr(args, "request_id_key", None))
    datasets = [str(s).strip() for s in (getattr(args, "dataset", None) or []) if str(s).strip()]
    tf = _resolve_timeframe(args)

    limit = getattr(args, "limit", None)
    limit_i = int(limit) if limit is not None else None
    if limit_i is not None:
        if limit_i < 0:
            raise ValidationError("--limit must be >= 0")
        if limit_i > 2000:
            raise ValidationError("--limit must be <= 2000")

    selector = {
        "account_id": account_id,
        "datasets": datasets,
        "error_id": error_id,
        "script_name": script_name,
        "request_id_key": request_id_key_override,
        "timeframe": {"from_ms": tf.from_ms, "to_ms": tf.to_ms},
        "limit": limit_i,
        "out": out_path,
        "overwrite": overwrite,
    }

    plan = base_plan(
        ctx,
        selector=selector,
        risk_level="high",
        risk_reasons=[
            "This queries stored logs/events; results may include PII.",
            "This writes the raw API response to a local file; results are never printed.",
            "This is a read-like POST (no Cloudflare state changes expected).",
        ],
    )
    plan["request"] = {
        "keys_discovery": {
            "method": "POST",
            "path": _telemetry_path(account_id=account_id, endpoint="keys"),
            "sensitivity": "sensitive_read",
            "notes": "Used to auto-discover the request-id key when --request-id-key is not provided.",
        },
        "query": {
            "method": "POST",
            "path": _telemetry_path(account_id=account_id, endpoint="query"),
            "sensitivity": "sensitive_read",
            "notes": "Uses queryId='temporary' with filters + timeframe (see OpenAPI snapshot schema).",
            "out": out_path,
        },
    }
    plan["proposed_changes"] = [{"resource": "local_file", "action": "write", "path": out_path, "reason": "workers_logs_search"}]
    plan["verification_plan"] = ["Confirm output file exists and record size/sha256 locally."]
    plan["notes"].append("Results may contain PII; output is file-only and never printed.")
    if request_id_key_override:
        plan["notes"].append("Using user-provided --request-id-key (no key auto-discovery).")
    else:
        plan["notes"].append("On apply, the tool will auto-discover a request-id key via telemetry keys; it may refuse if none is found.")

    if not bool(ctx.get("apply")):
        return emit_plan(ctx, command="workers.logs.search", plan=plan)

    require_apply(ctx)
    verify_and_require_plan(ctx, plan=plan)

    # Determine request-id key
    discovered_keys: list[str] | None = None
    request_id_key = request_id_key_override
    if not request_id_key:
        keys_body = _telemetry_keys_body(tf=tf, datasets=datasets, limit=None, key_needle=None, needle=None)
        resp = ctx["cf"].post_json(_telemetry_path(account_id=account_id, endpoint="keys"), json_body=keys_body)
        discovered_keys = _extract_key_names(resp.result)
        picked = _pick_best_key(discovered_keys, scorer=_score_request_id_key)
        if not picked:
            raise SafetyError(
                "Could not auto-discover a request-id key from telemetry keys. "
                "Run: cloudflare-api-tool workers logs keys --out <file> --apply "
                "and retry with --request-id-key <KEY>."
            )
        request_id_key = picked

    filters: list[dict[str, Any]] = [
        {"key": request_id_key, "operation": "eq", "type": "string", "value": error_id},
    ]

    script_name_key_used: str | None = None
    script_name_filter_mode: str | None = None
    needle_obj: dict[str, Any] | None = None
    if script_name:
        if discovered_keys is None:
            # Fetch keys only when needed to avoid extra API calls when overridden.
            keys_body = _telemetry_keys_body(tf=tf, datasets=datasets, limit=None, key_needle=None, needle=None)
            resp = ctx["cf"].post_json(_telemetry_path(account_id=account_id, endpoint="keys"), json_body=keys_body)
            discovered_keys = _extract_key_names(resp.result)
        picked_script = _pick_best_key(discovered_keys or [], scorer=_score_script_name_key)
        if picked_script and _score_script_name_key(picked_script) >= 900:
            script_name_key_used = picked_script
            script_name_filter_mode = "filter"
            filters.append({"key": picked_script, "operation": "eq", "type": "string", "value": script_name})
        else:
            script_name_filter_mode = "needle"
            needle_obj = _needle_obj(script_name)

    query_body = _telemetry_query_body(
        tf=tf,
        datasets=datasets,
        filters=filters,
        limit=limit_i,
        needle=needle_obj,
    )

    plan["request"]["query"]["body_meta"] = build_json_body_meta(query_body, source="workers.logs.search")
    plan["request"]["query"]["selected_request_id_key"] = request_id_key
    plan["request"]["query"]["script_name_filter_mode"] = script_name_filter_mode
    plan["request"]["query"]["script_name_key_used"] = script_name_key_used

    wrote, obj = _post_telemetry_and_write(
        ctx=ctx, account_id=account_id, endpoint="query", body=query_body, out_path=out_path, overwrite=overwrite
    )

    best_effort_rows: int | None = None
    try:
        if isinstance(obj, dict) and obj.get("success") is True:
            result = obj.get("result")
            if isinstance(result, dict):
                stats = result.get("statistics")
                if isinstance(stats, dict) and isinstance(stats.get("rows_read"), (int, float)):
                    best_effort_rows = int(stats.get("rows_read"))
    except Exception:
        best_effort_rows = None

    receipt = base_receipt(ctx, selector=selector, changed=False)
    receipt["output_file"] = wrote
    receipt["verification"] = {
        "ok": True,
        "method": "file_written",
        "details": {
            "request_id_key": request_id_key,
            "script_name_filter_mode": script_name_filter_mode,
            "script_name_key_used": script_name_key_used,
            "rows_read": best_effort_rows,
        },
    }
    receipt["notes"].append("Telemetry query response is sensitive; body written to file only.")
    if script_name_filter_mode == "needle":
        receipt["notes"].append("Script name filter used full-text needle (field name not guessed).")

    return emit_receipt(
        ctx,
        command="workers.logs.search",
        receipt=receipt,
        extra={
            "out": wrote.get("out_rel") or wrote.get("out_path"),
            "request_id_key": request_id_key,
            "script_name_filter_mode": script_name_filter_mode,
            "rows_read": best_effort_rows,
        },
    )
