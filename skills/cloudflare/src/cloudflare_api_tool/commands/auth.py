from __future__ import annotations

import concurrent.futures
import time
from typing import Any

from ..cloudflare import CloudflareClient
from ..errors import ValidationError
from ..state import get_default_account_id


def _safe_count_list(value: Any) -> int | None:
    if isinstance(value, list):
        return len(value)
    return None


def _run_check(fn, *, error_hint: str | None = None) -> dict[str, Any]:
    try:
        return {"ok": True, "result": fn()}
    except Exception as e:  # noqa: BLE001
        out: dict[str, Any] = {"ok": False, "error": str(e)}
        if error_hint:
            out["hint"] = error_hint
        return out


def _resolve_account_id(args, ctx) -> tuple[str | None, str | None]:
    requested_account_id = str(getattr(args, "account_id", "") or "").strip() or None
    default_account_id = get_default_account_id(ctx["env_file"], fingerprint=ctx.get("env_fingerprint")) or None
    account_id = requested_account_id or (default_account_id.strip() if default_account_id else None)
    account_id_source = "arg" if requested_account_id else ("default" if default_account_id else None)
    if account_id:
        return account_id, account_id_source
    try:
        res = ctx["cf"].get_json("/accounts", params={"page": 1, "per_page": 50})
        items = res.result or []
        if isinstance(items, list) and len(items) == 1 and isinstance(items[0], dict):
            account_id = str(items[0].get("id") or "").strip() or None
            if account_id:
                return account_id, "accounts_list_single"
    except Exception:
        pass
    return None, account_id_source


def _extract_error_summary(resp_obj: Any) -> list[dict[str, Any]]:
    if not isinstance(resp_obj, dict):
        return []
    errors = resp_obj.get("errors")
    if not isinstance(errors, list):
        return []
    out: list[dict[str, Any]] = []
    for item in errors[:10]:
        if not isinstance(item, dict):
            continue
        out.append(
            {
                "code": item.get("code"),
                "message": item.get("message"),
            }
        )
    return out


_AUTH_EXPLAIN_MAP: dict[str, dict[str, Any]] = {
    "observability speed availabilities": {
        "summary": "Read Cloudflare Observatory quota/availability for a zone.",
        "required_permissions": ["Zone Settings Read"],
        "also_works_with": ["Zone Settings Write"],
        "optional_permissions": [],
        "notes": ["This is a read-only observability check."],
    },
    "observability speed pages list": {
        "summary": "List Cloudflare Observatory-tested pages for a zone.",
        "required_permissions": ["Zone Settings Read"],
        "also_works_with": ["Zone Settings Write"],
        "optional_permissions": [],
        "notes": ["Useful for discovering the exact Cloudflare page identifiers before running page-level speed commands."],
    },
    "observability speed page latest": {
        "summary": "Show the latest saved Cloudflare Observatory test for one page URL.",
        "required_permissions": ["Zone Settings Read"],
        "also_works_with": ["Zone Settings Write"],
        "optional_permissions": [],
        "notes": ["The CLI now normalizes a normal URL to Cloudflare's internal Observatory page identifier."],
    },
    "observability speed page trend": {
        "summary": "Read the Core Web Vitals / trend series for one page from Cloudflare Observatory.",
        "required_permissions": ["Zone Settings Read"],
        "also_works_with": ["Zone Settings Write"],
        "optional_permissions": [],
        "notes": ["This is read-only and does not expose request logs or business conversion data."],
    },
    "observability speed page history": {
        "summary": "List saved Cloudflare Observatory test history for one page.",
        "required_permissions": ["Zone Settings Read"],
        "also_works_with": ["Zone Settings Write"],
        "optional_permissions": [],
        "notes": ["This is useful for saved performance tests, not for live request history."],
    },
    "observability web-analytics status": {
        "summary": "Check whether Cloudflare RUM/Web Analytics is wired up for a zone.",
        "required_permissions": ["Zone Settings Read", "Account Settings Read"],
        "also_works_with": ["Zone Settings Write"],
        "optional_permissions": ["Zone Read"],
        "notes": [
            "Zone Read helps the CLI resolve the zone name and match the right Web Analytics site.",
            "Ruleset detail may still fail if Cloudflare rejects that endpoint for the current auth scheme.",
        ],
    },
    "observability audit": {
        "summary": "Run the bundled Cloudflare observability audit for one zone.",
        "required_permissions": ["Zone Settings Read", "Account Settings Read"],
        "also_works_with": ["Zone Settings Write"],
        "optional_permissions": ["Zone Read", "Logs Read", "Logs Write"],
        "notes": [
            "Logs permissions only help the log-status part of the audit.",
            "Cloudflare Free still will not expose full historical request logs even with read access.",
        ],
    },
    "observability rum zone-settings get": {
        "summary": "Read the zone-level RUM toggle directly.",
        "required_permissions": ["Zone Settings Read"],
        "also_works_with": ["Zone Settings Write"],
        "optional_permissions": [],
        "notes": [],
    },
    "observability rum zone-settings toggle": {
        "summary": "Turn RUM on or off for the zone.",
        "required_permissions": ["Zone Settings Write"],
        "also_works_with": [],
        "optional_permissions": [],
        "notes": ["This is a real write and still needs --apply --yes in the CLI."],
    },
}


def _normalize_auth_explain_target(parts: list[str] | None) -> str:
    raw = " ".join([str(p or "").strip() for p in (parts or []) if str(p or "").strip()]).strip().lower()
    if not raw:
        raise ValidationError("Missing --for <command words>")
    return " ".join(raw.split())


def cmd_auth_check(args, ctx) -> int:
    _ = args
    cfg = ctx["cfg"]
    if not cfg.token:
        raise ValidationError("Missing CLOUDFLARE_API_TOKEN")

    res = ctx["cf"].get_json("/user/tokens/verify")
    out = {"ok": True, "command": "auth.check", "base_url": cfg.base_url, "token_present": True, "result": res.result}
    ctx["audit"].write("auth.check", out)
    ctx["out"].emit(out)
    return 0


def cmd_auth_explain(args, ctx) -> int:
    _ = ctx
    target = _normalize_auth_explain_target(getattr(args, "for_command", None))
    data = _AUTH_EXPLAIN_MAP.get(target)
    if not data:
        out = {
            "ok": True,
            "command": "auth.explain",
            "target": target,
            "known": False,
            "notes": [
                "No exact explainer is built in for that command yet.",
                "Try one of the observability speed, web-analytics status, or observability audit commands.",
            ],
        }
        ctx["audit"].write("auth.explain", {"target": target, "known": False})
        ctx["out"].emit(out)
        return 0

    out = {
        "ok": True,
        "command": "auth.explain",
        "target": target,
        "known": True,
        "summary": data["summary"],
        "required_permissions": data["required_permissions"],
        "also_works_with": data["also_works_with"],
        "optional_permissions": data["optional_permissions"],
        "notes": data["notes"],
    }
    ctx["audit"].write("auth.explain", {"target": target, "known": True})
    ctx["out"].emit(out)
    return 0


def cmd_auth_probe(args, ctx) -> int:
    """
    Run a small set of read-only API calls to confirm the token works for common workflows.

    This is intentionally conservative:
    - no external writes
    - no sensitive content reads
    - returns counts + boolean status, not full objects
    """
    cfg = ctx["cfg"]
    if not cfg.token:
        raise ValidationError("Missing CLOUDFLARE_API_TOKEN")

    account_id, _account_id_source = _resolve_account_id(args, ctx)

    checks: dict[str, Any] = {}

    def token_verify():
        res = ctx["cf"].get_json("/user/tokens/verify")
        if isinstance(res.result, dict):
            return {"status": res.result.get("status"), "id": res.result.get("id")}
        return res.result

    checks["token_verify"] = _run_check(token_verify)

    def accounts_list():
        res = ctx["cf"].get_json("/accounts", params={"page": 1, "per_page": 50})
        return {"count": _safe_count_list(res.result)}

    checks["accounts_list"] = _run_check(accounts_list)

    if account_id:
        def workers_scripts_list():
            res = ctx["cf"].get_json(f"/accounts/{account_id}/workers/scripts")
            return {"count": _safe_count_list(res.result)}

        checks["workers_scripts_list"] = _run_check(workers_scripts_list)

        def workers_kv_namespaces_list():
            res = ctx["cf"].get_json(f"/accounts/{account_id}/storage/kv/namespaces")
            return {"count": _safe_count_list(res.result)}

        checks["workers_kv_namespaces_list"] = _run_check(workers_kv_namespaces_list)

        def d1_databases_list():
            res = ctx["cf"].get_json(f"/accounts/{account_id}/d1/database")
            return {"count": _safe_count_list(res.result)}

        checks["d1_databases_list"] = _run_check(
            d1_databases_list,
            error_hint="If auth.check succeeds but this fails, your token likely lacks D1 permissions.",
        )

        def zones_list():
            # We only need a count; keep the page size small.
            res = ctx["cf"].get_json("/zones", params={"account.id": account_id, "page": 1, "per_page": 5})
            return {"count": _safe_count_list(res.result)}

        checks["zones_list"] = _run_check(
            zones_list,
            error_hint="If you expect zones but count is 0, your token may lack Zone read permissions (or the account has no zones).",
        )
    else:
        checks["account_scoped"] = {
            "ok": False,
            "error": "Missing --account-id and no default is set. Run: cloudflare-api-tool accounts set-default --account-id <id>",
        }

    out = {
        "ok": True,
        "command": "auth.probe",
        "base_url": cfg.base_url,
        "account_id": account_id,
        "checks": checks,
    }
    ctx["audit"].write("auth.probe", {"account_id": account_id, "checks_ok": {k: bool(v.get("ok")) for k, v in checks.items()}})
    ctx["out"].emit(out)
    return 0


def cmd_auth_zone_create_check(args, ctx) -> int:
    cfg = ctx["cfg"]
    if not cfg.token:
        raise ValidationError("Missing CLOUDFLARE_API_TOKEN")

    account_id, account_id_source = _resolve_account_id(args, ctx)
    if not account_id:
        raise ValidationError("Missing --account-id and no default is set. Run: cloudflare-api-tool accounts set-default --account-id <id>")

    # Safe permission probe: send an intentionally invalid create-zone request.
    # A validation error proves the token reached the create-zone endpoint.
    # A permission error proves the token still cannot create zones.
    invalid_body = {
        "account": {"id": account_id},
        "name": "",
        "type": "full",
    }
    raw = ctx["cf"].request_raw_allow_errors("POST", "/zones", json_body=invalid_body, retries=0)
    response_obj: Any
    try:
        response_obj = raw.json()
    except Exception:
        response_obj = None
    errors = _extract_error_summary(response_obj)
    error_text = " ".join([str(item.get("message") or "") for item in errors]).strip().lower()

    permission_ok: bool | None
    result: str
    notes: list[str] = [
        "This check sends an intentionally invalid create-zone payload, so it should not create anything.",
        "Use this before a bulk zone onboarding run.",
    ]
    if raw.status == 403 or "permission" in error_text or "forbidden" in error_text:
        permission_ok = False
        result = "forbidden"
        notes.append("Cloudflare accepted the auth path but refused zone creation for this token/account.")
    elif raw.status in {400, 422}:
        permission_ok = True
        result = "allowed"
        notes.append("Cloudflare rejected the payload for validation reasons, which means the token reached the zone-create endpoint.")
    else:
        permission_ok = None
        result = "unclear"
        notes.append("Cloudflare returned an unexpected response. Review the errors before a bulk run.")

    out = {
        "ok": True,
        "command": "auth.zone_create_check",
        "account_id": account_id,
        "account_id_source": account_id_source,
        "required_permissions": ["Zone Zone Edit", "Zone DNS Edit"],
        "permission_ok": permission_ok,
        "result": result,
        "http_status": int(raw.status),
        "errors": errors,
        "notes": notes,
    }
    ctx["audit"].write(
        "auth.zone_create_check",
        {
            "account_id": account_id,
            "account_id_source": account_id_source,
            "permission_ok": permission_ok,
            "result": result,
            "http_status": int(raw.status),
        },
    )
    ctx["out"].emit(out)
    return 0


def cmd_auth_doctor(args, ctx) -> int:
    """
    Read-only latency/permissions doctor.

    Purpose: make "it feels hung" troubleshooting faster without introducing any project-specific logic.
    """
    cfg = ctx["cfg"]
    if not cfg.token:
        raise ValidationError("Missing CLOUDFLARE_API_TOKEN")

    requested_account_id = str(getattr(args, "account_id", "") or "").strip() or None
    default_account_id = get_default_account_id(ctx["env_file"], fingerprint=ctx.get("env_fingerprint")) or None
    account_id, auto_account_source = _resolve_account_id(args, ctx)

    def make_client() -> CloudflareClient:
        return CloudflareClient(
            base_url=cfg.base_url,
            token=cfg.token,
            connect_timeout_s=float(ctx.get("connect_timeout_s") or 30.0),
            read_timeout_s=float(ctx.get("read_timeout_s") or 30.0),
            verbose=bool(ctx.get("verbose")),
            progress=bool(ctx.get("progress")),
            cache=None,
            user_agent=str((ctx.get("tool") or "cloudflare-api-tool")) + "/" + str(ctx.get("tool_version") or ""),
        )

    probes: list[dict[str, Any]] = [
        {"name": "token_verify", "method": "GET", "path": "/user/tokens/verify", "params": None, "cacheable": False},
        {"name": "accounts_list", "method": "GET", "path": "/accounts", "params": {"page": 1, "per_page": 1}, "cacheable": False},
    ]
    if account_id:
        probes.extend(
            [
                {"name": "workers_scripts_list", "method": "GET", "path": f"/accounts/{account_id}/workers/scripts", "params": None, "cacheable": False},
                {"name": "tunnels_list", "method": "GET", "path": f"/accounts/{account_id}/cfd_tunnel", "params": None, "cacheable": False},
                {"name": "zero_trust_access_apps_list", "method": "GET", "path": f"/accounts/{account_id}/access/apps", "params": None, "cacheable": False},
            ]
        )

    parallel = int(ctx.get("parallel") or 1)
    parallel = max(1, min(parallel, 8))

    def run_probe(p: dict[str, Any]) -> dict[str, Any]:
        cf = make_client()
        name = str(p["name"])
        method = str(p["method"])
        path = str(p["path"])
        params = p.get("params")
        start = time.time()
        try:
            if method.upper() == "GET":
                res = cf.get_json(path, params=params)
            else:
                raise AssertionError("doctor only supports GET probes")
            elapsed_ms = int((time.time() - start) * 1000)
            return {
                "name": name,
                "ok": True,
                "http": res.http,
                "duration_ms": int((res.http or {}).get("duration_ms") or elapsed_ms),
            }
        except Exception as e:  # noqa: BLE001
            elapsed_ms = int((time.time() - start) * 1000)
            return {"name": name, "ok": False, "error": str(e), "duration_ms": elapsed_ms}

    results: list[dict[str, Any]] = []
    if parallel == 1 or len(probes) <= 1:
        results = [run_probe(p) for p in probes]
    else:
        with concurrent.futures.ThreadPoolExecutor(max_workers=parallel) as ex:
            futs = [ex.submit(run_probe, p) for p in probes]
            for fut in concurrent.futures.as_completed(futs):
                results.append(fut.result())

    # Keep output stable and readable.
    results.sort(key=lambda x: str(x.get("name") or ""))

    suggestions: list[str] = []
    read_timeout_s = float(ctx.get("read_timeout_s") or 30.0)
    slow = [r for r in results if isinstance(r.get("duration_ms"), int) and int(r["duration_ms"]) > int(read_timeout_s * 800)]
    if slow:
        suggestions.append("Some endpoints are slower than your current read timeout; consider using --timeout-profile slow or increasing --read-timeout-s.")
    failed = [str(r.get("name") or "") for r in results if not bool(r.get("ok")) and str(r.get("name") or "").strip()]
    if failed:
        failed_preview = ", ".join(failed[:6])
        tail = "" if len(failed) <= 6 else f" (+{len(failed) - 6} more)"
        suggestions.append(
            "Some probes failed: "
            f"{failed_preview}{tail}. This usually means the token lacks permissions for those product areas (or the account has them disabled)."
        )
    if any(r.get("name") == "zero_trust_access_apps_list" and not r.get("ok") for r in results):
        suggestions.append("Zero Trust Access inventory probe failed; verify the token has Zero Trust permissions (Access: Apps and Policies, Zero Trust, Cloudflare Tunnel).")
    if not account_id:
        suggestions.append("Set a default account id to unlock account-scoped probes: cloudflare-api-tool accounts set-default --account-id <id>.")

    out = {
        "ok": True,
        "command": "auth.doctor",
        "base_url": cfg.base_url,
        "account_id": account_id,
        "account_id_source": ("arg" if requested_account_id else ("default" if default_account_id else auto_account_source)),
        "parallel": parallel,
        "connect_timeout_s": float(ctx.get("connect_timeout_s") or 30.0),
        "read_timeout_s": read_timeout_s,
        "results": results,
        "suggestions": suggestions,
    }
    ctx["audit"].write("auth.doctor", {"account_id": account_id, "results_ok": {r.get("name"): bool(r.get("ok")) for r in results}})
    ctx["out"].emit(out)
    return 0
