from __future__ import annotations

import json
import time
from dataclasses import asdict
from pathlib import Path
from typing import Any
from urllib.parse import quote

from ..command_naming import param_name_to_dest
from ..discovery import load_methods
from ..errors import SafetyError, ToolError, ValidationError
from ..gsc_http import GscHttpClient, redact_http_response_for_receipt
from ..google_auth import load_credentials_from_config
from ..json_files import read_json_file, write_json_file


READ_LIKE_POST_METHOD_IDS = {
    "webmasters.searchanalytics.query",
    "searchconsole.urlInspection.index.inspect",
    "searchconsole.urlTestingTools.mobileFriendlyTest.run",
}

def is_write_capable(method_id: str, http_method: str) -> bool:
    """
    Safe-by-default classifier:
    - GET is read-only.
    - POST is write-capable unless explicitly allowlisted as read-like.
    - PUT/PATCH/DELETE are write-capable.
    - Unknown verbs are treated as write-capable.
    """
    verb = str(http_method or "").strip().upper()
    if verb == "GET":
        return False
    if verb == "POST":
        return method_id not in READ_LIKE_POST_METHOD_IDS
    if verb in {"PUT", "PATCH", "DELETE"}:
        return True
    return True


def is_irreversible_delete(http_method: str) -> bool:
    return str(http_method or "").strip().upper() == "DELETE"


def _build_write_recovery(*, method_id: str, request_path: str) -> dict[str, Any]:
    if method_id == "webmasters.sites.add":
        return {
            "end_state": "rollback_by_inverse_action",
            "strategy": "sites.delete",
            "rollback_ready": True,
            "rollback_plan": {
                "method_id": "webmasters.sites.delete",
                "http_method": "DELETE",
                "path": request_path,
            },
        }

    if method_id == "webmasters.sitemaps.submit":
        return {
            "end_state": "rollback_by_inverse_action",
            "strategy": "sitemaps.delete",
            "rollback_ready": True,
            "rollback_plan": {
                "method_id": "webmasters.sitemaps.delete",
                "http_method": "DELETE",
                "path": request_path,
            },
        }

    # Deleting resources from this CLI family is not safely reversible here.
    return {
        "end_state": "irreversible_and_clearly_labeled",
        "strategy": "no_inverse",
        "rollback_ready": False,
        "rollback_plan": None,
    }


def _selector_for_plan(method_id: str, params: dict[str, Any]) -> str | None:
    if method_id.startswith("webmasters.sites."):
        site_url = params.get("siteUrl")
        return f"siteUrl={site_url}" if isinstance(site_url, str) and site_url else None
    if method_id.startswith("webmasters.sitemaps."):
        site_url = params.get("siteUrl")
        feedpath = params.get("feedpath")
        if isinstance(site_url, str) and site_url and isinstance(feedpath, str) and feedpath:
            return f"siteUrl={site_url} feedpath={feedpath}"
    return None


def _utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _find_site_entry(resp_json: Any, *, site_url: str) -> dict[str, Any] | None:
    if not isinstance(resp_json, dict):
        return None
    entries = resp_json.get("siteEntry")
    if not isinstance(entries, list):
        return None
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        if str(entry.get("siteUrl") or "") == str(site_url):
            return entry
    return None


def _find_sitemap_entry(resp_json: Any, *, feedpath: str) -> dict[str, Any] | None:
    if not isinstance(resp_json, dict):
        return None
    entries = resp_json.get("sitemap")
    if not isinstance(entries, list):
        return None
    target = str(feedpath)
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        candidate = str(entry.get("path") or entry.get("feedpath") or "")
        if str(candidate) == target:
            return entry
    return None


def _capture_before_state(
    *,
    ctx: dict,
    method_id: str,
    params: dict[str, Any],
    http: GscHttpClient,
) -> tuple[dict[str, Any] | None, str | None]:
    target = _selector_for_plan(method_id, params)

    if method_id == "webmasters.sites.add":
        site_url = str(params.get("siteUrl") or "").strip()
        state_resp = http.request_json(http_method="GET", path="webmasters/v3/sites", query=None, body=None)
        entry = _find_site_entry(state_resp.json, site_url=site_url)
        before_state = {
            "resource": "site",
            "target": {"site_url": site_url},
            "present": entry is not None,
            "entry": entry,
            "snapshot": state_resp.json if isinstance(state_resp.json, dict) else None,
        }

    elif method_id == "webmasters.sites.delete":
        site_url = str(params.get("siteUrl") or "").strip()
        state_resp = http.request_json(http_method="GET", path="webmasters/v3/sites", query=None, body=None)
        entry = _find_site_entry(state_resp.json, site_url=site_url)
        before_state = {
            "resource": "site",
            "target": {"site_url": site_url},
            "present": entry is not None,
            "entry": entry,
            "snapshot": state_resp.json if isinstance(state_resp.json, dict) else None,
        }

    elif method_id == "webmasters.sitemaps.submit":
        site_url = str(params.get("siteUrl") or "").strip()
        feedpath = str(params.get("feedpath") or "").strip()
        path = "webmasters/v3/sites/" + quote(site_url, safe="") + "/sitemaps"
        state_resp = http.request_json(http_method="GET", path=path, query=None, body=None)
        entry = _find_sitemap_entry(state_resp.json, feedpath=feedpath)
        before_state = {
            "resource": "sitemap",
            "target": {"site_url": site_url, "feedpath": feedpath},
            "present": entry is not None,
            "entry": entry,
            "snapshot": state_resp.json if isinstance(state_resp.json, dict) else None,
        }

    elif method_id == "webmasters.sitemaps.delete":
        site_url = str(params.get("siteUrl") or "").strip()
        feedpath = str(params.get("feedpath") or "").strip()
        path = "webmasters/v3/sites/" + quote(site_url, safe="") + "/sitemaps"
        state_resp = http.request_json(http_method="GET", path=path, query=None, body=None)
        entry = _find_sitemap_entry(state_resp.json, feedpath=feedpath)
        before_state = {
            "resource": "sitemap",
            "target": {"site_url": site_url, "feedpath": feedpath},
            "present": entry is not None,
            "entry": entry,
            "snapshot": state_resp.json if isinstance(state_resp.json, dict) else None,
        }
    else:
        return None, None

    record = {
        "method_id": method_id,
        "captured_at_utc": _utc_now(),
        "selector": target,
        "before_state": before_state,
    }

    artifacts_dir = ctx.get("artifacts_dir")
    if not isinstance(artifacts_dir, Path):
        return record, None

    before_state_path = Path(artifacts_dir) / "before_state.json"
    return record, str(write_json_file(before_state_path, record))


def _extract_params(args: Any, method_params: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for pname in method_params.keys():
        dest = param_name_to_dest(pname)
        v = getattr(args, dest, None)
        if v is None:
            continue
        out[pname] = v
    return out


def _substitute_path(path: str, params: dict[str, Any]) -> str:
    out = str(path or "")
    for k, v in params.items():
        if "{" + k + "}" in out:
            out = out.replace("{" + k + "}", quote(str(v), safe=""))
    return out


def _load_body(args: Any, *, required: bool) -> Any | None:
    body_json = getattr(args, "body_json", None)
    body_file = getattr(args, "body_file", None)
    if body_json and body_file:
        raise ValidationError("Pass exactly one of --body-json or --body-file")
    if not body_json and not body_file:
        if required:
            raise ValidationError("Missing request body. Pass --body-json or --body-file")
        return None
    if body_json:
        try:
            return json.loads(str(body_json))
        except Exception as e:  # noqa: BLE001
            raise ValidationError(f"Invalid --body-json: {type(e).__name__}: {e}") from None
    return read_json_file(str(body_file))


def _write_plan_if_requested(ctx: dict, plan: dict) -> str | None:
    plan_out = str(ctx.get("plan_out") or "").strip() or None
    if not plan_out:
        return None
    return write_json_file(plan_out, plan)


def _write_receipt_if_requested(ctx: dict, receipt: dict) -> str | None:
    receipt_out = str(ctx.get("receipt_out") or "").strip() or None
    if not receipt_out:
        return None
    return write_json_file(receipt_out, receipt)


def _validate_plan_in(ctx: dict, *, expected_method_id: str, expected_selector: str | None) -> dict:
    plan_in = str(ctx.get("plan_in") or "").strip()
    if not plan_in:
        raise SafetyError("Missing --plan-in (required for this apply)")
    plan = read_json_file(plan_in)
    if not isinstance(plan, dict):
        raise SafetyError("Invalid plan file: must be a JSON object")

    if str(plan.get("method_id") or "") != expected_method_id:
        raise SafetyError("Plan drift: method_id mismatch")
    if expected_selector and str(plan.get("selector") or "") != expected_selector:
        raise SafetyError("Plan drift: selector mismatch")

    env_fp = str(plan.get("env_fingerprint") or "").strip()
    if env_fp and str(ctx["cfg"].base_url) != env_fp:
        raise SafetyError("Plan drift: env_fingerprint mismatch")
    return plan


def _verify_after_write(ctx: dict, http: GscHttpClient, *, method_id: str, params: dict[str, Any]) -> dict[str, Any]:
    """
    Best-effort verification using list endpoints. Returns a small structured object.
    """
    if method_id in {"webmasters.sites.add", "webmasters.sites.delete"}:
        site_url = params.get("siteUrl")
        resp = http.request_json(http_method="GET", path="webmasters/v3/sites", query=None, body=None)
        sites = []
        if isinstance(resp.json, dict) and isinstance(resp.json.get("siteEntry"), list):
            sites = [x.get("siteUrl") for x in resp.json["siteEntry"] if isinstance(x, dict)]
        present = str(site_url) in [str(s) for s in sites]
        return {"verification_method_id": "webmasters.sites.list", "site_present": present}

    if method_id in {"webmasters.sitemaps.submit", "webmasters.sitemaps.delete"}:
        site_url = params.get("siteUrl")
        if not site_url:
            return {"verification_method_id": "webmasters.sitemaps.list", "ok": False, "error": "Missing siteUrl"}
        path = "webmasters/v3/sites/" + quote(str(site_url), safe="") + "/sitemaps"
        resp = http.request_json(http_method="GET", path=path, query=None, body=None)
        return {"verification_method_id": "webmasters.sitemaps.list", "ok": bool(resp.status < 400)}

    return {"ok": True, "skipped": True}


def cmd_discovery_method(args: Any, ctx: dict) -> int:
    method_id = str(getattr(args, "method_id", "") or "").strip()
    if not method_id:
        raise ToolError("Internal error: missing method_id on args")

    methods = load_methods()
    spec = methods.get(method_id)
    if not spec:
        raise ValidationError(f"Unknown method id: {method_id}")

    params = _extract_params(args, {k: asdict(v) for k, v in spec.parameters.items()})
    path_params = {k: v for k, v in params.items() if spec.parameters.get(k) and spec.parameters[k].location == "path"}
    query_params = {k: v for k, v in params.items() if spec.parameters.get(k) and spec.parameters[k].location == "query"}
    path = _substitute_path(spec.path, path_params)
    body = _load_body(args, required=bool(spec.has_request_body))

    selector = _selector_for_plan(method_id, params)
    write_capable = is_write_capable(method_id, spec.http_method)
    is_delete = is_irreversible_delete(spec.http_method)
    before_state = None
    before_state_path = None
    http = None

    plan = {
        "tool": "gsc-api-tool",
        "method_id": method_id,
        "http_method": spec.http_method,
        "path": path,
        "query": query_params or None,
        "has_body": body is not None,
        "selector": selector,
        "env_fingerprint": ctx["cfg"].base_url,
        "params": params,
    }

    if not write_capable and bool(ctx.get("apply")):
        # Apply has no meaning for read-like methods.
        ctx["audit"].write("method.apply_ignored", {"method_id": method_id})

    if write_capable and not bool(ctx.get("apply")):
        creds, _info = load_credentials_from_config(
            env_file=ctx["env_file"],
            oauth_client_secrets_file=ctx["cfg"].oauth_client_secrets_file,
            service_account_file=ctx["cfg"].service_account_file,
            scopes=ctx["cfg"].oauth_scopes,
        )
        if creds is None:
            raise ValidationError("Missing credentials. Run: gsc-api-tool auth login")

        http = GscHttpClient(
            base_url=ctx["cfg"].base_url,
            timeout_s=ctx["timeout_s"],
            verbose=bool(ctx.get("verbose")),
            creds=creds,
        )
        before_state, before_state_path = _capture_before_state(ctx=ctx, method_id=method_id, params=params, http=http)
        recovery = _build_write_recovery(method_id=method_id, request_path=path)
        plan["recovery"] = recovery
        plan["before_state"] = before_state
        if before_state_path:
            plan["before_state_path"] = before_state_path
        plan_path = _write_plan_if_requested(ctx, plan)
        out = {"ok": True, "dry_run": True, "plan": plan, "plan_path": plan_path, "write_capable": True}
        ctx["audit"].write("method.plan", {"method_id": method_id, "plan_path": plan_path})
        ctx["out"].emit(out)
        return 0

    if write_capable and bool(ctx.get("apply")) and is_delete:
        if not bool(ctx.get("yes")):
            raise SafetyError("Refusing delete without --yes")
        if not bool(ctx.get("ack_irreversible")):
            raise SafetyError("Refusing delete without --ack-irreversible")
        _ = _validate_plan_in(ctx, expected_method_id=method_id, expected_selector=selector)

    if write_capable:
        creds, _info = load_credentials_from_config(
            env_file=ctx["env_file"],
            oauth_client_secrets_file=ctx["cfg"].oauth_client_secrets_file,
            service_account_file=ctx["cfg"].service_account_file,
            scopes=ctx["cfg"].oauth_scopes,
        )
        if creds is None:
            raise ValidationError("Missing credentials. Run: gsc-api-tool auth login")

        http = GscHttpClient(
            base_url=ctx["cfg"].base_url,
            timeout_s=ctx["timeout_s"],
            verbose=bool(ctx.get("verbose")),
            creds=creds,
        )
        before_state, before_state_path = _capture_before_state(ctx=ctx, method_id=method_id, params=params, http=http)

    resp = http.request_json(http_method=spec.http_method, path=path, query=query_params or None, body=body)
    verification = None
    if write_capable and bool(ctx.get("apply")):
        try:
            verification = _verify_after_write(ctx, http, method_id=method_id, params=params)
        except Exception as e:  # noqa: BLE001
            verification = {"ok": False, "error": f"{type(e).__name__}: {e}"}

    recovery = _build_write_recovery(method_id=method_id, request_path=path)
    receipt = {
        "ok": True,
        "tool": "gsc-api-tool",
        "method_id": method_id,
        "applied": bool(write_capable and bool(ctx.get("apply"))),
        "request": {"http_method": spec.http_method, "path": path, "query": query_params or None, "has_body": body is not None},
        "response": redact_http_response_for_receipt(resp),
        "recovery": recovery,
        "verification": verification,
    }
    if write_capable:
        receipt["before_state"] = before_state
        if before_state_path:
            receipt["before_state_path"] = before_state_path
    receipt_path = _write_receipt_if_requested(ctx, receipt) if write_capable and bool(ctx.get("apply")) else None

    out = {"ok": True, "method_id": method_id, "response": receipt["response"], "verification": verification}
    if receipt_path:
        out["receipt_path"] = receipt_path
    ctx["audit"].write("method.call", {"method_id": method_id, "write": bool(write_capable), "apply": bool(ctx.get("apply"))})
    ctx["out"].emit(out)
    return 0
