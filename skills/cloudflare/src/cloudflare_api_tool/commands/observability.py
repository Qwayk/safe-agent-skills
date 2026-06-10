from __future__ import annotations

import argparse
from datetime import datetime, timezone
from typing import Any
from urllib.parse import quote, urlparse

from . import openapi_runner as openapi_runner_cmd
from ..errors import ToolError, ValidationError
from ..state import get_default_account_id


def _opt_str(v) -> str | None:  # noqa: ANN001
    s = str(v or "").strip()
    return s or None


def _delegate_openapi_call(
    *,
    ctx: dict,
    method: str,
    path_template: str,
    path_params: dict[str, str] | None = None,
    query: list[str] | None = None,
    body_json_file: str | None = None,
    content_type: str | None = None,
    out: str | None = None,
    overwrite: bool = False,
) -> int:
    ns = argparse.Namespace(
        operation_id=None,
        method=str(method or "").upper().strip(),
        path=str(path_template or "").strip(),
        path_param=[f"{k}={v}" for k, v in sorted((path_params or {}).items())],
        query=list(query or []),
        body_json_file=body_json_file,
        body_bytes_file=None,
        multipart_spec_file=None,
        content_type=content_type,
        out=out,
        overwrite=bool(overwrite),
    )
    return int(openapi_runner_cmd.cmd_openapi_call(ns, ctx))


def _require(value: str | None, *, flag: str) -> str:
    if value is None:
        raise ValidationError(f"Missing {flag}")
    return value


def _kv_list(values: list[str] | None) -> list[str]:
    out: list[str] = []
    for s in values or []:
        raw = str(s or "").strip()
        if not raw:
            continue
        if "=" not in raw:
            raise ValidationError(f"Invalid key=value: {raw!r}")
        out.append(raw)
    return out


def _emit_read_result(ctx: dict, *, command: str, payload: dict[str, Any]) -> int:
    out_obj: dict[str, Any] = {"ok": True, "command": command}
    out_obj.update(payload)
    ctx["audit"].write("read", {"command": command})
    ctx["out"].emit(out_obj)
    return 0


def _resolve_account_id_optional(args, ctx) -> str | None:
    account_id = _opt_str(getattr(args, "account_id", None))
    if account_id:
        return account_id
    default = get_default_account_id(ctx["env_file"], fingerprint=ctx.get("env_fingerprint"))
    return _opt_str(default)


def _safe_get_json(ctx: dict, path: str, *, params: dict[str, Any] | None = None) -> dict[str, Any]:
    try:
        res = ctx["cf"].get_json(path, params=params)
        return {"ok": True, "result": res.result, "result_info": res.result_info, "http": res.http}
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "error": str(e), "error_type": type(e).__name__}


def _normalize_observatory_url(raw: str | None) -> str:
    value = str(raw or "").strip()
    if not value:
        raise ValidationError("Missing --url")
    if "://" in value:
        parsed = urlparse(value)
        host = str(parsed.netloc or "").strip().lower()
        path = parsed.path or "/"
    else:
        trimmed = value.split("?", 1)[0].split("#", 1)[0].strip()
        if not trimmed:
            raise ValidationError("Missing --url")
        if "/" in trimmed:
            host, rest = trimmed.split("/", 1)
            path = "/" + rest
        else:
            host, path = trimmed, "/"
        host = host.strip().lower()
    if not host:
        raise ValidationError("Invalid --url: missing host")
    if not path.startswith("/"):
        path = "/" + path
    return host + (path or "/")


def _canonical_page_url(raw: str | None) -> str | None:
    value = str(raw or "").strip()
    if not value:
        return None
    try:
        return _normalize_observatory_url(value)
    except ValidationError:
        return None


def _encode_observatory_url(raw: str) -> str:
    return quote(str(raw), safe="")


def _parse_utc(value: str | None) -> datetime:
    raw = str(value or "").strip()
    if not raw:
        return datetime.fromtimestamp(0, tz=timezone.utc)
    if raw.endswith("Z"):
        raw = raw[:-1] + "+00:00"
    try:
        return datetime.fromisoformat(raw)
    except Exception:
        return datetime.fromtimestamp(0, tz=timezone.utc)


def _sorted_regions(entries: list[dict[str, Any]]) -> list[str]:
    labels = {
        str(((entry.get("region") or {}) if isinstance(entry.get("region"), dict) else {}).get("label") or "").strip()
        for entry in entries
    }
    return sorted([label for label in labels if label])


def _report_metrics(report: dict[str, Any] | None) -> dict[str, Any] | None:
    if not isinstance(report, dict):
        return None
    metrics: dict[str, Any] = {
        "performance_score": report.get("performanceScore"),
        "ttfb_ms": report.get("ttfb"),
        "fcp_ms": report.get("fcp"),
        "lcp_ms": report.get("lcp"),
        "tti_ms": report.get("tti"),
        "tbt_ms": report.get("tbt"),
        "si_ms": report.get("si"),
        "cls": report.get("cls"),
        "state": report.get("state"),
    }
    ranked: list[dict[str, Any]] = []
    for key in ["lcp", "tti", "tbt", "fcp", "ttfb", "si"]:
        value = report.get(key)
        if isinstance(value, (int, float)):
            ranked.append({"metric": f"{key}_ms", "value": value})
    metrics["slowest_metrics_ms"] = sorted(ranked, key=lambda item: float(item["value"]), reverse=True)[:3]
    return metrics


def _summarize_test(test: dict[str, Any] | None) -> dict[str, Any] | None:
    if not isinstance(test, dict):
        return None
    region = test.get("region") if isinstance(test.get("region"), dict) else {}
    return {
        "id": test.get("id"),
        "date": test.get("date"),
        "url": test.get("url"),
        "region": region.get("label") if isinstance(region, dict) else None,
        "mobile": _report_metrics(test.get("mobileReport") if isinstance(test.get("mobileReport"), dict) else None),
        "desktop": _report_metrics(test.get("desktopReport") if isinstance(test.get("desktopReport"), dict) else None),
    }


def _all_tests(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    tests: list[dict[str, Any]] = []
    for entry in entries:
        maybe_tests = entry.get("tests")
        if isinstance(maybe_tests, list):
            for test in maybe_tests:
                if isinstance(test, dict):
                    tests.append(test)
    return tests


def _latest_test(entries: list[dict[str, Any]]) -> dict[str, Any] | None:
    tests = _all_tests(entries)
    if not tests:
        return None
    return sorted(tests, key=lambda item: _parse_utc(str(item.get("date") or "")), reverse=True)[0]


def _find_speed_page_entries(*, pages: list[dict[str, Any]], raw_url: str) -> tuple[str, list[dict[str, Any]]]:
    target = _normalize_observatory_url(raw_url)
    matches = [entry for entry in pages if _canonical_page_url(entry.get("url")) == target]
    if matches:
        return target, matches
    candidates = sorted({str(entry.get("url") or "").strip() for entry in pages if str(entry.get("url") or "").strip()})
    preview = candidates[:10]
    tail = "" if len(candidates) <= 10 else f" (+{len(candidates) - 10} more)"
    raise ValidationError(f"No Observatory page matched {raw_url!r}. Known tested pages: {', '.join(preview)}{tail}")


def _summarize_pages_inventory(pages: list[dict[str, Any]]) -> dict[str, Any]:
    urls = sorted({str(page.get("url") or "").strip() for page in pages if str(page.get("url") or "").strip()})
    latest = _latest_test(pages)
    return {
        "page_entries": len(pages),
        "unique_urls": len(urls),
        "tested_urls": urls,
        "regions": _sorted_regions(pages),
        "latest_test": _summarize_test(latest),
    }


def _summarize_history_items(items: list[dict[str, Any]]) -> dict[str, Any]:
    if not items:
        return {"count": 0}
    ordered = sorted(items, key=lambda item: _parse_utc(str(item.get("date") or "")), reverse=True)
    return {
        "count": len(items),
        "latest": _summarize_test(ordered[0]),
        "earliest": _summarize_test(ordered[-1]),
    }


def _summarize_trend_result(result: Any) -> dict[str, Any]:
    if isinstance(result, list):
        dates = [str(item.get("date") or "") for item in result if isinstance(item, dict) and str(item.get("date") or "").strip()]
        return {
            "shape": "list",
            "points": len(result),
            "first_date": min(dates) if dates else None,
            "last_date": max(dates) if dates else None,
            "sample_keys": sorted([str(k) for k in result[0].keys()]) if result and isinstance(result[0], dict) else [],
        }
    if isinstance(result, dict):
        series_counts = {str(k): len(v) for k, v in result.items() if isinstance(v, list)}
        return {
            "shape": "object",
            "series": sorted(series_counts.keys()),
            "series_counts": series_counts,
        }
    return {"shape": type(result).__name__}


def _find_site_for_zone(*, sites: list[dict[str, Any]], zone_id: str, zone_name: str | None) -> dict[str, Any] | None:
    def _normalize_site_value(raw: Any) -> str | None:
        value = str(raw or "").strip().lower()
        if not value:
            return None
        if value.startswith("//"):
            parsed = urlparse(f"https:{value}")
            host = str(parsed.netloc or "").strip().lower()
            return host or None
        if "://" in value:
            parsed = urlparse(value)
            host = str(parsed.netloc or "").strip().lower()
            return host or None
        return value.rstrip("/") or None

    for site in sites:
        if not isinstance(site, dict):
            continue
        for key in ["zone_tag", "zoneTag"]:
            if str(site.get(key) or "").strip() == zone_id:
                return site
        ruleset = site.get("ruleset") if isinstance(site.get("ruleset"), dict) else {}
        for key in ["zone_tag", "zoneTag"]:
            if str((ruleset if isinstance(ruleset, dict) else {}).get(key) or "").strip() == zone_id:
                return site
    zone_name_value = str(zone_name or "").strip().lower()
    if not zone_name_value:
        return None
    site_keys = ["host", "name", "site_tag", "siteTag", "domain", "zone_name", "zoneName"]
    for site in sites:
        if not isinstance(site, dict):
            continue
        for key in site_keys:
            value = _normalize_site_value(site.get(key))
            if not value:
                continue
            if value == zone_name_value:
                return site
        ruleset = site.get("ruleset") if isinstance(site.get("ruleset"), dict) else {}
        for key in ["zone_name", "zoneName"]:
            value = _normalize_site_value((ruleset if isinstance(ruleset, dict) else {}).get(key))
            if value == zone_name_value:
                return site
    return None


def _ruleset_summary(result: dict[str, Any]) -> dict[str, Any]:
    if not result.get("ok"):
        return {"ok": False, "error": result.get("error"), "error_type": result.get("error_type")}
    rules = result.get("result")
    count = len(rules) if isinstance(rules, list) else None
    return {"ok": True, "rules_count": count}


def _build_web_analytics_status(args, ctx) -> dict[str, Any]:
    zone_id = _require(_opt_str(getattr(args, "zone_id", None)), flag="--zone-id")
    account_id = _resolve_account_id_optional(args, ctx)

    zone_result = _safe_get_json(ctx, f"/zones/{zone_id}")
    zone_name = None
    if zone_result.get("ok") and isinstance(zone_result.get("result"), dict):
        zone_name = _opt_str((zone_result.get("result") or {}).get("name"))

    rum_result = _safe_get_json(ctx, f"/zones/{zone_id}/settings/rum")

    sites_result: dict[str, Any] = {"ok": False, "error": "Missing account id", "error_type": "ValidationError"}
    matched_site: dict[str, Any] | None = None
    rules_result: dict[str, Any] = {"ok": False, "error": "No ruleset lookup attempted", "error_type": "NotAttempted"}
    if account_id:
        sites_result = _safe_get_json(ctx, f"/accounts/{account_id}/rum/site_info/list")
        if sites_result.get("ok") and isinstance(sites_result.get("result"), list):
            matched_site = _find_site_for_zone(sites=sites_result.get("result") or [], zone_id=zone_id, zone_name=zone_name)
        ruleset = ((matched_site or {}).get("ruleset") if isinstance(matched_site, dict) else None) or {}
        ruleset_id = _opt_str((ruleset if isinstance(ruleset, dict) else {}).get("id"))
        if ruleset_id:
            rules_result = _safe_get_json(ctx, f"/accounts/{account_id}/rum/v2/{ruleset_id}/rules")

    rum_summary = None
    if rum_result.get("ok") and isinstance(rum_result.get("result"), dict):
        rum = rum_result.get("result") or {}
        rum_summary = {
            "editable": rum.get("editable"),
            "value": rum.get("value"),
            "enabled": str(rum.get("value") or "").strip().lower() == "on",
            "zone_name": rum.get("zone_name"),
            "site_tag_present": bool(_opt_str(rum.get("site_tag"))),
        }

    site_summary = None
    if matched_site:
        ruleset = matched_site.get("ruleset") if isinstance(matched_site.get("ruleset"), dict) else {}
        site_summary = {
            "id": matched_site.get("id"),
            "host": matched_site.get("host") or matched_site.get("name") or matched_site.get("domain"),
            "auto_install": matched_site.get("auto_install"),
            "ruleset_id": ruleset.get("id") if isinstance(ruleset, dict) else None,
            "ruleset_enabled": ruleset.get("enabled") if isinstance(ruleset, dict) else None,
        }

    return {
        "zone_id": zone_id,
        "zone_name": zone_name,
        "account_id": account_id,
        "summary": {
            "rum_enabled": (rum_summary or {}).get("enabled"),
            "site_lookup_ok": bool(sites_result.get("ok")),
            "site_found": matched_site is not None,
            "auto_install": (site_summary or {}).get("auto_install"),
            "ruleset_enabled": (site_summary or {}).get("ruleset_enabled"),
            "rules_lookup": _ruleset_summary(rules_result),
        },
        "zone": zone_result,
        "rum": {"ok": rum_result.get("ok"), "summary": rum_summary, "error": rum_result.get("error")},
        "site": {
            "lookup_ok": bool(sites_result.get("ok")),
            "matched": matched_site is not None,
            "summary": site_summary,
            "error": sites_result.get("error"),
        },
        "rules": _ruleset_summary(rules_result),
    }


# ---- Logpush (account) ----


def cmd_logpush_account_datasets_fields(args, ctx) -> int:
    dataset_id = _require(_opt_str(getattr(args, "dataset_id", None)), flag="--dataset-id")
    account_id = _opt_str(getattr(args, "account_id", None))
    return _delegate_openapi_call(
        ctx=ctx,
        method="GET",
        path_template="/accounts/{account_id}/logpush/datasets/{dataset_id}/fields",
        path_params={k: v for k, v in {"account_id": account_id, "dataset_id": dataset_id}.items() if v},
        query=_kv_list(getattr(args, "query", None)),
        out=_opt_str(getattr(args, "out", None)),
        overwrite=bool(getattr(args, "overwrite", False)),
    )


def cmd_logpush_account_datasets_jobs(args, ctx) -> int:
    dataset_id = _require(_opt_str(getattr(args, "dataset_id", None)), flag="--dataset-id")
    account_id = _opt_str(getattr(args, "account_id", None))
    return _delegate_openapi_call(
        ctx=ctx,
        method="GET",
        path_template="/accounts/{account_id}/logpush/datasets/{dataset_id}/jobs",
        path_params={k: v for k, v in {"account_id": account_id, "dataset_id": dataset_id}.items() if v},
        query=_kv_list(getattr(args, "query", None)),
        out=_opt_str(getattr(args, "out", None)),
        overwrite=bool(getattr(args, "overwrite", False)),
    )


def cmd_logpush_account_jobs_list(args, ctx) -> int:
    account_id = _opt_str(getattr(args, "account_id", None))
    return _delegate_openapi_call(
        ctx=ctx,
        method="GET",
        path_template="/accounts/{account_id}/logpush/jobs",
        path_params={k: v for k, v in {"account_id": account_id}.items() if v},
        query=_kv_list(getattr(args, "query", None)),
        out=_opt_str(getattr(args, "out", None)),
        overwrite=bool(getattr(args, "overwrite", False)),
    )


def cmd_logpush_account_jobs_create(args, ctx) -> int:
    account_id = _opt_str(getattr(args, "account_id", None))
    body = _require(_opt_str(getattr(args, "body_json_file", None)), flag="--body-json-file")
    return _delegate_openapi_call(
        ctx=ctx,
        method="POST",
        path_template="/accounts/{account_id}/logpush/jobs",
        path_params={k: v for k, v in {"account_id": account_id}.items() if v},
        query=_kv_list(getattr(args, "query", None)),
        body_json_file=body,
        content_type=_opt_str(getattr(args, "content_type", None)),
        out=_opt_str(getattr(args, "out", None)),
        overwrite=bool(getattr(args, "overwrite", False)),
    )


def cmd_logpush_account_jobs_get(args, ctx) -> int:
    job_id = _require(_opt_str(getattr(args, "job_id", None)), flag="--job-id")
    account_id = _opt_str(getattr(args, "account_id", None))
    return _delegate_openapi_call(
        ctx=ctx,
        method="GET",
        path_template="/accounts/{account_id}/logpush/jobs/{job_id}",
        path_params={k: v for k, v in {"account_id": account_id, "job_id": job_id}.items() if v},
        query=_kv_list(getattr(args, "query", None)),
        out=_opt_str(getattr(args, "out", None)),
        overwrite=bool(getattr(args, "overwrite", False)),
    )


def cmd_logpush_account_jobs_update(args, ctx) -> int:
    job_id = _require(_opt_str(getattr(args, "job_id", None)), flag="--job-id")
    account_id = _opt_str(getattr(args, "account_id", None))
    body = _require(_opt_str(getattr(args, "body_json_file", None)), flag="--body-json-file")
    return _delegate_openapi_call(
        ctx=ctx,
        method="PUT",
        path_template="/accounts/{account_id}/logpush/jobs/{job_id}",
        path_params={k: v for k, v in {"account_id": account_id, "job_id": job_id}.items() if v},
        query=_kv_list(getattr(args, "query", None)),
        body_json_file=body,
        content_type=_opt_str(getattr(args, "content_type", None)),
        out=_opt_str(getattr(args, "out", None)),
        overwrite=bool(getattr(args, "overwrite", False)),
    )


def cmd_logpush_account_jobs_delete(args, ctx) -> int:
    job_id = _require(_opt_str(getattr(args, "job_id", None)), flag="--job-id")
    account_id = _opt_str(getattr(args, "account_id", None))
    return _delegate_openapi_call(
        ctx=ctx,
        method="DELETE",
        path_template="/accounts/{account_id}/logpush/jobs/{job_id}",
        path_params={k: v for k, v in {"account_id": account_id, "job_id": job_id}.items() if v},
        query=_kv_list(getattr(args, "query", None)),
        out=_opt_str(getattr(args, "out", None)),
        overwrite=bool(getattr(args, "overwrite", False)),
    )


def cmd_logpush_account_ownership_challenge(args, ctx) -> int:
    account_id = _opt_str(getattr(args, "account_id", None))
    body = _require(_opt_str(getattr(args, "body_json_file", None)), flag="--body-json-file")
    return _delegate_openapi_call(
        ctx=ctx,
        method="POST",
        path_template="/accounts/{account_id}/logpush/ownership",
        path_params={k: v for k, v in {"account_id": account_id}.items() if v},
        body_json_file=body,
        content_type=_opt_str(getattr(args, "content_type", None)),
        out=_opt_str(getattr(args, "out", None)),
        overwrite=bool(getattr(args, "overwrite", False)),
    )


def cmd_logpush_account_ownership_validate(args, ctx) -> int:
    account_id = _opt_str(getattr(args, "account_id", None))
    body = _require(_opt_str(getattr(args, "body_json_file", None)), flag="--body-json-file")
    return _delegate_openapi_call(
        ctx=ctx,
        method="POST",
        path_template="/accounts/{account_id}/logpush/ownership/validate",
        path_params={k: v for k, v in {"account_id": account_id}.items() if v},
        body_json_file=body,
        content_type=_opt_str(getattr(args, "content_type", None)),
        out=_opt_str(getattr(args, "out", None)),
        overwrite=bool(getattr(args, "overwrite", False)),
    )


def cmd_logpush_account_validate_destination(args, ctx) -> int:
    account_id = _opt_str(getattr(args, "account_id", None))
    body = _require(_opt_str(getattr(args, "body_json_file", None)), flag="--body-json-file")
    return _delegate_openapi_call(
        ctx=ctx,
        method="POST",
        path_template="/accounts/{account_id}/logpush/validate/destination",
        path_params={k: v for k, v in {"account_id": account_id}.items() if v},
        body_json_file=body,
        content_type=_opt_str(getattr(args, "content_type", None)),
        out=_opt_str(getattr(args, "out", None)),
        overwrite=bool(getattr(args, "overwrite", False)),
    )


def cmd_logpush_account_validate_destination_exists(args, ctx) -> int:
    account_id = _opt_str(getattr(args, "account_id", None))
    body = _require(_opt_str(getattr(args, "body_json_file", None)), flag="--body-json-file")
    return _delegate_openapi_call(
        ctx=ctx,
        method="POST",
        path_template="/accounts/{account_id}/logpush/validate/destination/exists",
        path_params={k: v for k, v in {"account_id": account_id}.items() if v},
        body_json_file=body,
        content_type=_opt_str(getattr(args, "content_type", None)),
        out=_opt_str(getattr(args, "out", None)),
        overwrite=bool(getattr(args, "overwrite", False)),
    )


def cmd_logpush_account_validate_origin(args, ctx) -> int:
    account_id = _opt_str(getattr(args, "account_id", None))
    body = _require(_opt_str(getattr(args, "body_json_file", None)), flag="--body-json-file")
    return _delegate_openapi_call(
        ctx=ctx,
        method="POST",
        path_template="/accounts/{account_id}/logpush/validate/origin",
        path_params={k: v for k, v in {"account_id": account_id}.items() if v},
        body_json_file=body,
        content_type=_opt_str(getattr(args, "content_type", None)),
        out=_opt_str(getattr(args, "out", None)),
        overwrite=bool(getattr(args, "overwrite", False)),
    )


# ---- Logpush (zone + instant logs jobs) ----


def cmd_logpush_zone_datasets_fields(args, ctx) -> int:
    dataset_id = _require(_opt_str(getattr(args, "dataset_id", None)), flag="--dataset-id")
    zone_id = _require(_opt_str(getattr(args, "zone_id", None)), flag="--zone-id")
    return _delegate_openapi_call(
        ctx=ctx,
        method="GET",
        path_template="/zones/{zone_id}/logpush/datasets/{dataset_id}/fields",
        path_params={"zone_id": zone_id, "dataset_id": dataset_id},
        query=_kv_list(getattr(args, "query", None)),
        out=_opt_str(getattr(args, "out", None)),
        overwrite=bool(getattr(args, "overwrite", False)),
    )


def cmd_logpush_zone_datasets_jobs(args, ctx) -> int:
    dataset_id = _require(_opt_str(getattr(args, "dataset_id", None)), flag="--dataset-id")
    zone_id = _require(_opt_str(getattr(args, "zone_id", None)), flag="--zone-id")
    return _delegate_openapi_call(
        ctx=ctx,
        method="GET",
        path_template="/zones/{zone_id}/logpush/datasets/{dataset_id}/jobs",
        path_params={"zone_id": zone_id, "dataset_id": dataset_id},
        query=_kv_list(getattr(args, "query", None)),
        out=_opt_str(getattr(args, "out", None)),
        overwrite=bool(getattr(args, "overwrite", False)),
    )


def cmd_logpush_zone_jobs_list(args, ctx) -> int:
    zone_id = _require(_opt_str(getattr(args, "zone_id", None)), flag="--zone-id")
    return _delegate_openapi_call(
        ctx=ctx,
        method="GET",
        path_template="/zones/{zone_id}/logpush/jobs",
        path_params={"zone_id": zone_id},
        query=_kv_list(getattr(args, "query", None)),
        out=_opt_str(getattr(args, "out", None)),
        overwrite=bool(getattr(args, "overwrite", False)),
    )


def cmd_logpush_zone_jobs_create(args, ctx) -> int:
    zone_id = _require(_opt_str(getattr(args, "zone_id", None)), flag="--zone-id")
    body = _require(_opt_str(getattr(args, "body_json_file", None)), flag="--body-json-file")
    return _delegate_openapi_call(
        ctx=ctx,
        method="POST",
        path_template="/zones/{zone_id}/logpush/jobs",
        path_params={"zone_id": zone_id},
        query=_kv_list(getattr(args, "query", None)),
        body_json_file=body,
        content_type=_opt_str(getattr(args, "content_type", None)),
        out=_opt_str(getattr(args, "out", None)),
        overwrite=bool(getattr(args, "overwrite", False)),
    )


def cmd_logpush_zone_jobs_get(args, ctx) -> int:
    zone_id = _require(_opt_str(getattr(args, "zone_id", None)), flag="--zone-id")
    job_id = _require(_opt_str(getattr(args, "job_id", None)), flag="--job-id")
    return _delegate_openapi_call(
        ctx=ctx,
        method="GET",
        path_template="/zones/{zone_id}/logpush/jobs/{job_id}",
        path_params={"zone_id": zone_id, "job_id": job_id},
        query=_kv_list(getattr(args, "query", None)),
        out=_opt_str(getattr(args, "out", None)),
        overwrite=bool(getattr(args, "overwrite", False)),
    )


def cmd_logpush_zone_jobs_update(args, ctx) -> int:
    zone_id = _require(_opt_str(getattr(args, "zone_id", None)), flag="--zone-id")
    job_id = _require(_opt_str(getattr(args, "job_id", None)), flag="--job-id")
    body = _require(_opt_str(getattr(args, "body_json_file", None)), flag="--body-json-file")
    return _delegate_openapi_call(
        ctx=ctx,
        method="PUT",
        path_template="/zones/{zone_id}/logpush/jobs/{job_id}",
        path_params={"zone_id": zone_id, "job_id": job_id},
        query=_kv_list(getattr(args, "query", None)),
        body_json_file=body,
        content_type=_opt_str(getattr(args, "content_type", None)),
        out=_opt_str(getattr(args, "out", None)),
        overwrite=bool(getattr(args, "overwrite", False)),
    )


def cmd_logpush_zone_jobs_delete(args, ctx) -> int:
    zone_id = _require(_opt_str(getattr(args, "zone_id", None)), flag="--zone-id")
    job_id = _require(_opt_str(getattr(args, "job_id", None)), flag="--job-id")
    return _delegate_openapi_call(
        ctx=ctx,
        method="DELETE",
        path_template="/zones/{zone_id}/logpush/jobs/{job_id}",
        path_params={"zone_id": zone_id, "job_id": job_id},
        query=_kv_list(getattr(args, "query", None)),
        out=_opt_str(getattr(args, "out", None)),
        overwrite=bool(getattr(args, "overwrite", False)),
    )


def cmd_logpush_zone_instant_jobs_list(args, ctx) -> int:
    zone_id = _require(_opt_str(getattr(args, "zone_id", None)), flag="--zone-id")
    return _delegate_openapi_call(
        ctx=ctx,
        method="GET",
        path_template="/zones/{zone_id}/logpush/edge/jobs",
        path_params={"zone_id": zone_id},
        query=_kv_list(getattr(args, "query", None)),
        out=_opt_str(getattr(args, "out", None)),
        overwrite=bool(getattr(args, "overwrite", False)),
    )


def cmd_logpush_zone_instant_jobs_create(args, ctx) -> int:
    zone_id = _require(_opt_str(getattr(args, "zone_id", None)), flag="--zone-id")
    body = _require(_opt_str(getattr(args, "body_json_file", None)), flag="--body-json-file")
    return _delegate_openapi_call(
        ctx=ctx,
        method="POST",
        path_template="/zones/{zone_id}/logpush/edge/jobs",
        path_params={"zone_id": zone_id},
        query=_kv_list(getattr(args, "query", None)),
        body_json_file=body,
        content_type=_opt_str(getattr(args, "content_type", None)),
        out=_opt_str(getattr(args, "out", None)),
        overwrite=bool(getattr(args, "overwrite", False)),
    )


def cmd_logpush_zone_ownership_challenge(args, ctx) -> int:
    zone_id = _require(_opt_str(getattr(args, "zone_id", None)), flag="--zone-id")
    body = _require(_opt_str(getattr(args, "body_json_file", None)), flag="--body-json-file")
    return _delegate_openapi_call(
        ctx=ctx,
        method="POST",
        path_template="/zones/{zone_id}/logpush/ownership",
        path_params={"zone_id": zone_id},
        body_json_file=body,
        content_type=_opt_str(getattr(args, "content_type", None)),
        out=_opt_str(getattr(args, "out", None)),
        overwrite=bool(getattr(args, "overwrite", False)),
    )


def cmd_logpush_zone_ownership_validate(args, ctx) -> int:
    zone_id = _require(_opt_str(getattr(args, "zone_id", None)), flag="--zone-id")
    body = _require(_opt_str(getattr(args, "body_json_file", None)), flag="--body-json-file")
    return _delegate_openapi_call(
        ctx=ctx,
        method="POST",
        path_template="/zones/{zone_id}/logpush/ownership/validate",
        path_params={"zone_id": zone_id},
        body_json_file=body,
        content_type=_opt_str(getattr(args, "content_type", None)),
        out=_opt_str(getattr(args, "out", None)),
        overwrite=bool(getattr(args, "overwrite", False)),
    )


def cmd_logpush_zone_validate_destination(args, ctx) -> int:
    zone_id = _require(_opt_str(getattr(args, "zone_id", None)), flag="--zone-id")
    body = _require(_opt_str(getattr(args, "body_json_file", None)), flag="--body-json-file")
    return _delegate_openapi_call(
        ctx=ctx,
        method="POST",
        path_template="/zones/{zone_id}/logpush/validate/destination",
        path_params={"zone_id": zone_id},
        body_json_file=body,
        content_type=_opt_str(getattr(args, "content_type", None)),
        out=_opt_str(getattr(args, "out", None)),
        overwrite=bool(getattr(args, "overwrite", False)),
    )


def cmd_logpush_zone_validate_destination_exists(args, ctx) -> int:
    zone_id = _require(_opt_str(getattr(args, "zone_id", None)), flag="--zone-id")
    body = _require(_opt_str(getattr(args, "body_json_file", None)), flag="--body-json-file")
    return _delegate_openapi_call(
        ctx=ctx,
        method="POST",
        path_template="/zones/{zone_id}/logpush/validate/destination/exists",
        path_params={"zone_id": zone_id},
        body_json_file=body,
        content_type=_opt_str(getattr(args, "content_type", None)),
        out=_opt_str(getattr(args, "out", None)),
        overwrite=bool(getattr(args, "overwrite", False)),
    )


def cmd_logpush_zone_validate_origin(args, ctx) -> int:
    zone_id = _require(_opt_str(getattr(args, "zone_id", None)), flag="--zone-id")
    body = _require(_opt_str(getattr(args, "body_json_file", None)), flag="--body-json-file")
    return _delegate_openapi_call(
        ctx=ctx,
        method="POST",
        path_template="/zones/{zone_id}/logpush/validate/origin",
        path_params={"zone_id": zone_id},
        body_json_file=body,
        content_type=_opt_str(getattr(args, "content_type", None)),
        out=_opt_str(getattr(args, "out", None)),
        overwrite=bool(getattr(args, "overwrite", False)),
    )


# ---- Zone logs ----


def cmd_logs_received_get(args, ctx) -> int:
    zone_id = _require(_opt_str(getattr(args, "zone_id", None)), flag="--zone-id")
    return _delegate_openapi_call(
        ctx=ctx,
        method="GET",
        path_template="/zones/{zone_id}/logs/received",
        path_params={"zone_id": zone_id},
        query=_kv_list(getattr(args, "query", None)),
        out=_opt_str(getattr(args, "out", None)),
        overwrite=bool(getattr(args, "overwrite", False)),
    )


def cmd_logs_received_fields(args, ctx) -> int:
    zone_id = _require(_opt_str(getattr(args, "zone_id", None)), flag="--zone-id")
    return _delegate_openapi_call(
        ctx=ctx,
        method="GET",
        path_template="/zones/{zone_id}/logs/received/fields",
        path_params={"zone_id": zone_id},
        query=_kv_list(getattr(args, "query", None)),
        out=_opt_str(getattr(args, "out", None)),
        overwrite=bool(getattr(args, "overwrite", False)),
    )


def cmd_logs_rayid_get(args, ctx) -> int:
    zone_id = _require(_opt_str(getattr(args, "zone_id", None)), flag="--zone-id")
    ray_id = _require(_opt_str(getattr(args, "ray_id", None)), flag="--ray-id")
    return _delegate_openapi_call(
        ctx=ctx,
        method="GET",
        path_template="/zones/{zone_id}/logs/rayids/{ray_id}",
        path_params={"zone_id": zone_id, "ray_id": ray_id},
        query=_kv_list(getattr(args, "query", None)),
        out=_opt_str(getattr(args, "out", None)),
        overwrite=bool(getattr(args, "overwrite", False)),
    )


# ---- Audit logs (sensitive read; file-only) ----


def cmd_audit_logs_account_list(args, ctx) -> int:
    account_id = _opt_str(getattr(args, "account_id", None))
    return _delegate_openapi_call(
        ctx=ctx,
        method="GET",
        path_template="/accounts/{account_id}/audit_logs",
        path_params={k: v for k, v in {"account_id": account_id}.items() if v},
        query=_kv_list(getattr(args, "query", None)),
        out=_opt_str(getattr(args, "out", None)),
        overwrite=bool(getattr(args, "overwrite", False)),
    )


def cmd_audit_logs_account_list_v2(args, ctx) -> int:
    account_id = _opt_str(getattr(args, "account_id", None))
    return _delegate_openapi_call(
        ctx=ctx,
        method="GET",
        path_template="/accounts/{account_id}/logs/audit",
        path_params={k: v for k, v in {"account_id": account_id}.items() if v},
        query=_kv_list(getattr(args, "query", None)),
        out=_opt_str(getattr(args, "out", None)),
        overwrite=bool(getattr(args, "overwrite", False)),
    )


def cmd_audit_logs_user_list(args, ctx) -> int:
    return _delegate_openapi_call(
        ctx=ctx,
        method="GET",
        path_template="/user/audit_logs",
        query=_kv_list(getattr(args, "query", None)),
        out=_opt_str(getattr(args, "out", None)),
        overwrite=bool(getattr(args, "overwrite", False)),
    )


# ---- Logs control (CMB config) ----


def cmd_logs_control_cmb_get(args, ctx) -> int:
    account_id = _opt_str(getattr(args, "account_id", None))
    return _delegate_openapi_call(
        ctx=ctx,
        method="GET",
        path_template="/accounts/{account_id}/logs/control/cmb/config",
        path_params={k: v for k, v in {"account_id": account_id}.items() if v},
        query=_kv_list(getattr(args, "query", None)),
    )


def cmd_logs_control_cmb_update(args, ctx) -> int:
    account_id = _opt_str(getattr(args, "account_id", None))
    body = _require(_opt_str(getattr(args, "body_json_file", None)), flag="--body-json-file")
    return _delegate_openapi_call(
        ctx=ctx,
        method="POST",
        path_template="/accounts/{account_id}/logs/control/cmb/config",
        path_params={k: v for k, v in {"account_id": account_id}.items() if v},
        body_json_file=body,
        content_type=_opt_str(getattr(args, "content_type", None)),
    )


def cmd_logs_control_cmb_delete(args, ctx) -> int:
    account_id = _opt_str(getattr(args, "account_id", None))
    return _delegate_openapi_call(
        ctx=ctx,
        method="DELETE",
        path_template="/accounts/{account_id}/logs/control/cmb/config",
        path_params={k: v for k, v in {"account_id": account_id}.items() if v},
    )


# ---- Request Tracer (sensitive read-like POST) ----


def cmd_request_tracer_trace(args, ctx) -> int:
    account_id = _opt_str(getattr(args, "account_id", None))
    body = _require(_opt_str(getattr(args, "body_json_file", None)), flag="--body-json-file")
    return _delegate_openapi_call(
        ctx=ctx,
        method="POST",
        path_template="/accounts/{account_id}/request-tracer/trace",
        path_params={k: v for k, v in {"account_id": account_id}.items() if v},
        query=_kv_list(getattr(args, "query", None)),
        body_json_file=body,
        content_type=_opt_str(getattr(args, "content_type", None)),
        out=_opt_str(getattr(args, "out", None)),
        overwrite=bool(getattr(args, "overwrite", False)),
    )


# ---- Observatory speed / web analytics summaries ----


def cmd_speed_availabilities(args, ctx) -> int:
    zone_id = _require(_opt_str(getattr(args, "zone_id", None)), flag="--zone-id")
    res = ctx["cf"].get_json(f"/zones/{zone_id}/speed_api/availabilities")
    summary = {"fields": sorted([str(k) for k in res.result.keys()])} if isinstance(res.result, dict) else {"shape": type(res.result).__name__}
    return _emit_read_result(
        ctx,
        command="observability.speed.availabilities",
        payload={"zone_id": zone_id, "summary": summary, "result": res.result, "result_info": res.result_info, "http": res.http},
    )


def cmd_speed_pages_list(args, ctx) -> int:
    zone_id = _require(_opt_str(getattr(args, "zone_id", None)), flag="--zone-id")
    res = ctx["cf"].get_json(f"/zones/{zone_id}/speed_api/pages")
    pages = res.result if isinstance(res.result, list) else []
    summary = _summarize_pages_inventory(pages)
    return _emit_read_result(
        ctx,
        command="observability.speed.pages.list",
        payload={"zone_id": zone_id, "summary": summary, "pages": pages, "result_info": res.result_info, "http": res.http},
    )


def cmd_speed_page_latest(args, ctx) -> int:
    zone_id = _require(_opt_str(getattr(args, "zone_id", None)), flag="--zone-id")
    raw_url = _require(_opt_str(getattr(args, "url", None)), flag="--url")
    res = ctx["cf"].get_json(f"/zones/{zone_id}/speed_api/pages")
    pages = res.result if isinstance(res.result, list) else []
    normalized_url, matches = _find_speed_page_entries(pages=pages, raw_url=raw_url)
    latest = _latest_test(matches)
    return _emit_read_result(
        ctx,
        command="observability.speed.page.latest",
        payload={
            "zone_id": zone_id,
            "requested_url": raw_url,
            "normalized_url": normalized_url,
            "match_count": len(matches),
            "regions": _sorted_regions(matches),
            "latest_test": _summarize_test(latest),
            "matched_pages": matches,
        },
    )


def cmd_speed_page_history(args, ctx) -> int:
    zone_id = _require(_opt_str(getattr(args, "zone_id", None)), flag="--zone-id")
    raw_url = _require(_opt_str(getattr(args, "url", None)), flag="--url")
    pages_res = ctx["cf"].get_json(f"/zones/{zone_id}/speed_api/pages")
    pages = pages_res.result if isinstance(pages_res.result, list) else []
    normalized_url, matches = _find_speed_page_entries(pages=pages, raw_url=raw_url)
    encoded = _encode_observatory_url(normalized_url)
    res = ctx["cf"].get_json(f"/zones/{zone_id}/speed_api/pages/{encoded}/tests")
    items = res.result if isinstance(res.result, list) else []
    summary = _summarize_history_items(items)
    summary["regions"] = _sorted_regions(matches)
    return _emit_read_result(
        ctx,
        command="observability.speed.page.history",
        payload={
            "zone_id": zone_id,
            "requested_url": raw_url,
            "normalized_url": normalized_url,
            "summary": summary,
            "history": items,
            "http": res.http,
        },
    )


def cmd_speed_page_trend(args, ctx) -> int:
    zone_id = _require(_opt_str(getattr(args, "zone_id", None)), flag="--zone-id")
    raw_url = _require(_opt_str(getattr(args, "url", None)), flag="--url")
    pages_res = ctx["cf"].get_json(f"/zones/{zone_id}/speed_api/pages")
    pages = pages_res.result if isinstance(pages_res.result, list) else []
    normalized_url, _matches = _find_speed_page_entries(pages=pages, raw_url=raw_url)
    encoded = _encode_observatory_url(normalized_url)
    res = ctx["cf"].get_json(f"/zones/{zone_id}/speed_api/pages/{encoded}/trend")
    return _emit_read_result(
        ctx,
        command="observability.speed.page.trend",
        payload={
            "zone_id": zone_id,
            "requested_url": raw_url,
            "normalized_url": normalized_url,
            "summary": _summarize_trend_result(res.result),
            "trend": res.result,
            "http": res.http,
        },
    )


def cmd_web_analytics_status(args, ctx) -> int:
    payload = _build_web_analytics_status(args, ctx)
    return _emit_read_result(ctx, command="observability.web_analytics.status", payload=payload)


def cmd_observability_audit(args, ctx) -> int:
    zone_id = _require(_opt_str(getattr(args, "zone_id", None)), flag="--zone-id")
    account_id = _resolve_account_id_optional(args, ctx)
    status_payload = _build_web_analytics_status(args, ctx)
    availabilities = _safe_get_json(ctx, f"/zones/{zone_id}/speed_api/availabilities")
    pages = _safe_get_json(ctx, f"/zones/{zone_id}/speed_api/pages")
    zone_name = _opt_str(status_payload.get("zone_name"))
    homepage_guess = _opt_str(getattr(args, "url", None)) or (f"https://{zone_name}/" if zone_name else None)

    speed_homepage: dict[str, Any] = {"ok": False, "error": "No homepage URL available"}
    if pages.get("ok") and homepage_guess and isinstance(pages.get("result"), list):
        try:
            normalized_url, matches = _find_speed_page_entries(pages=pages.get("result") or [], raw_url=homepage_guess)
            speed_homepage = {
                "ok": True,
                "requested_url": homepage_guess,
                "normalized_url": normalized_url,
                "regions": _sorted_regions(matches),
                "latest_test": _summarize_test(_latest_test(matches)),
            }
        except Exception as e:  # noqa: BLE001
            speed_homepage = {"ok": False, "error": str(e)}

    instant_logs = _safe_get_json(ctx, f"/zones/{zone_id}/logpush/edge/jobs")
    zone_logpush = _safe_get_json(ctx, f"/zones/{zone_id}/logpush/jobs")
    summary = {
        "rum_enabled": ((status_payload.get("summary") or {}).get("rum_enabled")),
        "web_analytics_site_found": ((status_payload.get("summary") or {}).get("site_found")),
        "speed_pages_ok": bool(pages.get("ok")),
        "speed_page_entries": len(pages.get("result") or []) if isinstance(pages.get("result"), list) else None,
        "instant_logs_access": bool(instant_logs.get("ok")),
        "zone_logpush_access": bool(zone_logpush.get("ok")),
    }
    return _emit_read_result(
        ctx,
        command="observability.audit",
        payload={
            "zone_id": zone_id,
            "account_id": account_id,
            "summary": summary,
            "web_analytics": status_payload,
            "speed_availabilities": availabilities,
            "speed_pages": {"ok": pages.get("ok"), "summary": _summarize_pages_inventory(pages.get("result") or []) if isinstance(pages.get("result"), list) else None, "error": pages.get("error")},
            "speed_homepage": speed_homepage,
            "logs": {
                "instant_logs": {"ok": instant_logs.get("ok"), "count": len(instant_logs.get("result") or []) if isinstance(instant_logs.get("result"), list) else None, "error": instant_logs.get("error")},
                "zone_logpush_jobs": {"ok": zone_logpush.get("ok"), "count": len(zone_logpush.get("result") or []) if isinstance(zone_logpush.get("result"), list) else None, "error": zone_logpush.get("error")},
            },
        },
    )


# ---- RUM / Web Analytics ----


def cmd_rum_sites_list(args, ctx) -> int:
    account_id = _opt_str(getattr(args, "account_id", None))
    return _delegate_openapi_call(
        ctx=ctx,
        method="GET",
        path_template="/accounts/{account_id}/rum/site_info/list",
        path_params={k: v for k, v in {"account_id": account_id}.items() if v},
        query=_kv_list(getattr(args, "query", None)),
    )


def cmd_rum_sites_create(args, ctx) -> int:
    account_id = _opt_str(getattr(args, "account_id", None))
    body = _require(_opt_str(getattr(args, "body_json_file", None)), flag="--body-json-file")
    return _delegate_openapi_call(
        ctx=ctx,
        method="POST",
        path_template="/accounts/{account_id}/rum/site_info",
        path_params={k: v for k, v in {"account_id": account_id}.items() if v},
        body_json_file=body,
        content_type=_opt_str(getattr(args, "content_type", None)),
    )


def cmd_rum_sites_get(args, ctx) -> int:
    account_id = _opt_str(getattr(args, "account_id", None))
    site_id = _require(_opt_str(getattr(args, "site_id", None)), flag="--site-id")
    return _delegate_openapi_call(
        ctx=ctx,
        method="GET",
        path_template="/accounts/{account_id}/rum/site_info/{site_id}",
        path_params={k: v for k, v in {"account_id": account_id, "site_id": site_id}.items() if v},
        query=_kv_list(getattr(args, "query", None)),
    )


def cmd_rum_sites_update(args, ctx) -> int:
    account_id = _opt_str(getattr(args, "account_id", None))
    site_id = _require(_opt_str(getattr(args, "site_id", None)), flag="--site-id")
    body = _require(_opt_str(getattr(args, "body_json_file", None)), flag="--body-json-file")
    return _delegate_openapi_call(
        ctx=ctx,
        method="PUT",
        path_template="/accounts/{account_id}/rum/site_info/{site_id}",
        path_params={k: v for k, v in {"account_id": account_id, "site_id": site_id}.items() if v},
        body_json_file=body,
        content_type=_opt_str(getattr(args, "content_type", None)),
    )


def cmd_rum_sites_delete(args, ctx) -> int:
    account_id = _opt_str(getattr(args, "account_id", None))
    site_id = _require(_opt_str(getattr(args, "site_id", None)), flag="--site-id")
    return _delegate_openapi_call(
        ctx=ctx,
        method="DELETE",
        path_template="/accounts/{account_id}/rum/site_info/{site_id}",
        path_params={k: v for k, v in {"account_id": account_id, "site_id": site_id}.items() if v},
    )


def cmd_rum_rules_list(args, ctx) -> int:
    account_id = _opt_str(getattr(args, "account_id", None))
    ruleset_id = _require(_opt_str(getattr(args, "ruleset_id", None)), flag="--ruleset-id")
    return _delegate_openapi_call(
        ctx=ctx,
        method="GET",
        path_template="/accounts/{account_id}/rum/v2/{ruleset_id}/rules",
        path_params={k: v for k, v in {"account_id": account_id, "ruleset_id": ruleset_id}.items() if v},
        query=_kv_list(getattr(args, "query", None)),
    )


def cmd_rum_rules_bulk_update(args, ctx) -> int:
    account_id = _opt_str(getattr(args, "account_id", None))
    ruleset_id = _require(_opt_str(getattr(args, "ruleset_id", None)), flag="--ruleset-id")
    body = _require(_opt_str(getattr(args, "body_json_file", None)), flag="--body-json-file")
    return _delegate_openapi_call(
        ctx=ctx,
        method="POST",
        path_template="/accounts/{account_id}/rum/v2/{ruleset_id}/rules",
        path_params={k: v for k, v in {"account_id": account_id, "ruleset_id": ruleset_id}.items() if v},
        body_json_file=body,
        content_type=_opt_str(getattr(args, "content_type", None)),
    )


def cmd_rum_rule_create(args, ctx) -> int:
    account_id = _opt_str(getattr(args, "account_id", None))
    ruleset_id = _require(_opt_str(getattr(args, "ruleset_id", None)), flag="--ruleset-id")
    body = _require(_opt_str(getattr(args, "body_json_file", None)), flag="--body-json-file")
    return _delegate_openapi_call(
        ctx=ctx,
        method="POST",
        path_template="/accounts/{account_id}/rum/v2/{ruleset_id}/rule",
        path_params={k: v for k, v in {"account_id": account_id, "ruleset_id": ruleset_id}.items() if v},
        body_json_file=body,
        content_type=_opt_str(getattr(args, "content_type", None)),
    )


def cmd_rum_rule_update(args, ctx) -> int:
    account_id = _opt_str(getattr(args, "account_id", None))
    ruleset_id = _require(_opt_str(getattr(args, "ruleset_id", None)), flag="--ruleset-id")
    rule_id = _require(_opt_str(getattr(args, "rule_id", None)), flag="--rule-id")
    body = _require(_opt_str(getattr(args, "body_json_file", None)), flag="--body-json-file")
    return _delegate_openapi_call(
        ctx=ctx,
        method="PUT",
        path_template="/accounts/{account_id}/rum/v2/{ruleset_id}/rule/{rule_id}",
        path_params={k: v for k, v in {"account_id": account_id, "ruleset_id": ruleset_id, "rule_id": rule_id}.items() if v},
        body_json_file=body,
        content_type=_opt_str(getattr(args, "content_type", None)),
    )


def cmd_rum_rule_delete(args, ctx) -> int:
    account_id = _opt_str(getattr(args, "account_id", None))
    ruleset_id = _require(_opt_str(getattr(args, "ruleset_id", None)), flag="--ruleset-id")
    rule_id = _require(_opt_str(getattr(args, "rule_id", None)), flag="--rule-id")
    return _delegate_openapi_call(
        ctx=ctx,
        method="DELETE",
        path_template="/accounts/{account_id}/rum/v2/{ruleset_id}/rule/{rule_id}",
        path_params={k: v for k, v in {"account_id": account_id, "ruleset_id": ruleset_id, "rule_id": rule_id}.items() if v},
    )


def cmd_rum_zone_settings_get(args, ctx) -> int:
    zone_id = _require(_opt_str(getattr(args, "zone_id", None)), flag="--zone-id")
    return _delegate_openapi_call(
        ctx=ctx,
        method="GET",
        path_template="/zones/{zone_id}/settings/rum",
        path_params={"zone_id": zone_id},
        query=_kv_list(getattr(args, "query", None)),
    )


def cmd_rum_zone_settings_toggle(args, ctx) -> int:
    zone_id = _require(_opt_str(getattr(args, "zone_id", None)), flag="--zone-id")
    body = _require(_opt_str(getattr(args, "body_json_file", None)), flag="--body-json-file")
    return _delegate_openapi_call(
        ctx=ctx,
        method="PATCH",
        path_template="/zones/{zone_id}/settings/rum",
        path_params={"zone_id": zone_id},
        body_json_file=body,
        content_type=_opt_str(getattr(args, "content_type", None)),
    )
