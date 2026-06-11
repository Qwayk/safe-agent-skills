from __future__ import annotations

import argparse
import hashlib
import json
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable, Sequence

from .errors import SafetyError, ValidationError
from .http import HttpClient
from .json_files import read_json_file, write_json_file
from .openapi_ops import OperationSpec, load_operation_specs, operation_command_line
from .redaction import redact_headers, redact_obj
from .risk import RiskClassification, classify_operation


_READ_METHODS = {"get", "head", "options"}


def _utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _parse_kv_list(items: Sequence[str] | None, *, flag_name: str) -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    for raw in (items or []):
        s = str(raw or "").strip()
        if not s:
            continue
        if "=" not in s:
            raise ValidationError(f"Expected {flag_name} in k=v form, got: {s!r}")
        k, v = s.split("=", 1)
        k = k.strip()
        if not k:
            raise ValidationError(f"Expected {flag_name} key in k=v, got: {s!r}")
        out.append((k, v))
    return out


@dataclass(frozen=True)
class _PlannedRequest:
    method: str
    url: str
    path: str
    query: tuple[tuple[str, str], ...]
    data: tuple[tuple[str, str], ...]
    files: tuple[dict[str, Any], ...]


def _json_canonical_dumps(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256_json(obj: Any) -> str:
    return hashlib.sha256(_json_canonical_dumps(obj).encode("utf-8")).hexdigest()


def _build_headers(
    *,
    ctx: dict[str, Any],
    stripe_account: str | None,
    idempotency_key: str | None,
) -> dict[str, str]:
    cfg = ctx["cfg"]
    headers: dict[str, str] = {
        "Authorization": f"Bearer {cfg.api_key}",
    }
    if cfg.stripe_version:
        headers["Stripe-Version"] = cfg.stripe_version

    if stripe_account:
        allow = cfg.stripe_account_allowlist
        if allow and stripe_account not in allow:
            raise SafetyError(
                "Refused: --stripe-account is not in STRIPE_ACCOUNT_ALLOWLIST "
                f"(got {stripe_account!r})"
            )
        headers["Stripe-Account"] = stripe_account

    if idempotency_key:
        headers["Idempotency-Key"] = idempotency_key

    return headers


def _build_request(
    *,
    spec: OperationSpec,
    args: argparse.Namespace,
    ctx: dict[str, Any],
    idempotency_key: str | None,
) -> _PlannedRequest:
    path = spec.path_template
    for p in spec.path_params:
        attr = f"path_{p}"
        v = str(getattr(args, attr, "") or "").strip()
        if not v:
            raise ValidationError(f"Missing required path param: --{p}")
        path = path.replace("{" + p + "}", v)

    query_kv = _parse_kv_list(getattr(args, "query", None), flag_name="--query")
    expands = [str(x).strip() for x in (getattr(args, "expand", None) or []) if str(x).strip()]
    for e in expands:
        query_kv.append(("expand[]", e))
    data_kv = _parse_kv_list(getattr(args, "data", None), flag_name="--data")

    files_meta: list[dict[str, Any]] = []
    for raw in (getattr(args, "upload", None) or []):
        s = str(raw or "").strip()
        if not s:
            continue
        if "=" not in s:
            raise ValidationError(f"Expected --file in field=path form, got: {s!r}")
        field, path_raw = s.split("=", 1)
        field = field.strip()
        path_raw = path_raw.strip()
        if not field or not path_raw:
            raise ValidationError(f"Expected --file in field=path form, got: {s!r}")
        fp = Path(path_raw)
        if not fp.exists() or not fp.is_file():
            raise ValidationError(f"File not found: {fp}")
        b = fp.read_bytes()
        files_meta.append(
            {
                "field": field,
                "path": str(fp),
                "filename": fp.name,
                "size_bytes": len(b),
                "sha256": hashlib.sha256(b).hexdigest(),
            }
        )

    base_url = str(ctx["cfg"].base_url).rstrip("/")
    url = base_url + path

    _ = idempotency_key  # used in headers, not part of URL
    return _PlannedRequest(
        method=spec.method.upper(),
        url=url,
        path=path,
        query=tuple(query_kv),
        data=tuple(data_kv),
        files=tuple(files_meta),
    )


def _build_plan(
    *,
    spec: OperationSpec,
    args: argparse.Namespace,
    ctx: dict[str, Any],
    risk: RiskClassification,
    request: _PlannedRequest,
    stripe_account: str | None,
    idempotency_key: str | None,
) -> dict[str, Any]:
    headers = _build_headers(ctx=ctx, stripe_account=stripe_account, idempotency_key=idempotency_key)
    headers_redacted = redact_headers({k: v for k, v in headers.items()})
    plan_obj: dict[str, Any] = {
        "kind": "stripe.http_plan.v1",
        "tool": ctx.get("tool") or "stripe-api-tool",
        "version": ctx.get("tool_version") or None,
        "generated_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "command": ctx.get("command_str") or None,
        "operation": {
            "id": spec.operation_id,
            "command": operation_command_line(spec),
            "method": request.method,
            "path_template": spec.path_template,
            "path": request.path,
        },
        "request": {
            "method": request.method,
            "url": request.url,
            "path": request.path,
            "query": list(request.query),
            "data": list(request.data),
            "files": list(request.files),
        },
        "headers": headers_redacted,
        "risk": {
            "level": risk.level,
            "reasons": list(risk.reasons),
            "requirements": asdict(risk.requirements),
        },
        "stripe_account": stripe_account,
        "stripe_version": ctx["cfg"].stripe_version,
        "idempotency_key": idempotency_key,
        "rollback": {
            "supported": False,
            "notes": "No before-state snapshot is taken; no automatic rollback is available from this plan.",
        },
    }
    if request.method.lower().strip() not in _READ_METHODS:
        plan_obj["before_state"] = {
            "required": True,
            "supported": False,
            "status": "no_snapshot_available",
            "approval_required": "--ack-no-snapshot",
            "notes": (
                "No useful before-state snapshot or provider backup is captured for this Stripe write. "
                "The write may still run after the reviewed plan and explicit no-snapshot approval."
            ),
        }
    stable_hash_input = {
        "env_fingerprint": plan_obj["env_fingerprint"],
        "stripe_version": plan_obj["stripe_version"],
        "stripe_account": plan_obj["stripe_account"],
        "operation": plan_obj["operation"],
        "request": plan_obj["request"],
        "risk": plan_obj["risk"],
    }
    plan_obj["stable_hash"] = _sha256_json(stable_hash_input)
    return plan_obj


def _validate_plan_for_apply(*, plan: dict[str, Any], current_plan: dict[str, Any], ctx: dict[str, Any]) -> None:
    if str(plan.get("kind") or "") != "stripe.http_plan.v1":
        raise ValidationError("Plan kind mismatch (expected stripe.http_plan.v1)")
    if str(plan.get("env_fingerprint") or "") != str(ctx["cfg"].base_url):
        raise SafetyError("Refused: plan env_fingerprint does not match current environment")
    if str(plan.get("stable_hash") or "") != str(current_plan.get("stable_hash") or ""):
        raise SafetyError("Refused: current request does not match --plan-in (drift detected)")
    if str(plan.get("idempotency_key") or "") != str(current_plan.get("idempotency_key") or ""):
        raise SafetyError("Refused: idempotency_key does not match --plan-in (drift detected)")
    op = plan.get("operation")
    cur_op = current_plan.get("operation")
    if not isinstance(op, dict) or not isinstance(cur_op, dict):
        raise ValidationError("Plan missing operation object")
    if str(op.get("id") or "") != str(cur_op.get("id") or ""):
        raise SafetyError("Refused: plan operation id does not match current operation")


def _risk_enforce(
    *,
    risk: RiskClassification,
    ctx: dict[str, Any],
) -> None:
    req = risk.requirements
    if req.apply and not bool(ctx.get("apply")):
        raise SafetyError("Refused: --apply is required for this operation")
    if req.yes and not bool(ctx.get("yes")):
        raise SafetyError("Refused: --yes is required for this high-risk operation")
    if req.plan_in and not bool(ctx.get("plan_in")):
        raise SafetyError("Refused: --plan-in is required for this high-risk operation")
    if req.ack_spend_money and not bool(ctx.get("ack_spend_money")):
        raise SafetyError("Refused: --ack-spend-money is required for money-moving operations")
    if req.ack_irreversible and not bool(ctx.get("ack_irreversible")):
        raise SafetyError("Refused: --ack-irreversible is required for irreversible operations")


def _load_plan_in(path: str) -> dict[str, Any]:
    plan_obj = read_json_file(path)
    if not isinstance(plan_obj, dict):
        raise ValidationError("--plan-in file must be a JSON object")
    return plan_obj


def _files_for_request(files_meta: Iterable[dict[str, Any]]) -> dict[str, tuple[str, bytes]]:
    out: dict[str, tuple[str, bytes]] = {}
    for meta in files_meta:
        field = str(meta.get("field") or "").strip()
        path = str(meta.get("path") or "").strip()
        filename = str(meta.get("filename") or "").strip() or "upload"
        if not field or not path:
            continue
        b = Path(path).read_bytes()
        out[field] = (filename, b)
    return out


def _execute_live(
    *,
    spec: OperationSpec,
    plan: dict[str, Any],
    ctx: dict[str, Any],
    headers: dict[str, str],
) -> dict[str, Any]:
    client = HttpClient(timeout_s=float(ctx["timeout_s"]), verbose=bool(ctx.get("verbose")), user_agent="stripe-api-tool")
    req = plan.get("request") or {}
    if not isinstance(req, dict):
        raise ValidationError("Plan request missing")

    method = str(req.get("method") or "").strip()
    url = str(req.get("url") or "").strip()
    query = req.get("query") or []
    data = req.get("data") or []
    files_meta = req.get("files") or []

    params = dict(query) if isinstance(query, list) else None
    body = data if isinstance(data, list) else None
    files = _files_for_request(files_meta) if isinstance(files_meta, list) else None

    resp = client.request(
        method=method,
        url=url,
        headers=headers,
        params=params,
        data=body,
        files=files,
        retries=2,
    )
    resp_json: Any = None
    try:
        resp_json = resp.json()
    except Exception:
        resp_json = {"raw_text": resp.text()}

    return {
        "status": resp.status,
        "url": resp.url,
        "headers": redact_headers(resp.headers),
        "json": redact_obj(resp_json),
    }


def _best_effort_verify(
    *,
    spec: OperationSpec,
    response_json: Any,
    ctx: dict[str, Any],
    headers: dict[str, str],
) -> dict[str, Any]:
    # Best effort:
    # 1) If GET exists for the same path template, call it.
    # 2) Else, if we can infer a GET by appending "/{id}" to the base path, try it.
    if not isinstance(response_json, dict):
        return {"ok": False, "best_effort": True, "notes": "No JSON object response to verify against"}
    rid = str(response_json.get("id") or "").strip()
    if not rid:
        return {"ok": False, "best_effort": True, "notes": "Response missing id; cannot infer read-back"}

    specs = load_operation_specs()
    by_path: dict[str, set[str]] = {}
    for s in specs:
        by_path.setdefault(s.path_template, set()).add(s.method)

    candidate_templates: list[str] = []
    if "get" in by_path.get(spec.path_template, set()):
        candidate_templates.append(spec.path_template)
    if "get" not in by_path.get(spec.path_template, set()):
        # Try find a GET path that is base + "/{...}"
        base = spec.path_template.rstrip("/")
        for t, methods in by_path.items():
            if "get" not in methods:
                continue
            if t.startswith(base + "/{") and t.endswith("}"):
                candidate_templates.append(t)
        candidate_templates = sorted(set(candidate_templates))

    if len(candidate_templates) != 1:
        return {
            "ok": False,
            "best_effort": True,
            "notes": "Could not infer a single read-back GET endpoint",
            "candidates": candidate_templates,
        }

    tpl = candidate_templates[0]
    # Fill the last path param with the returned id.
    path = tpl
    import re as _re

    params = _re.findall(r"{([^}]+)}", tpl)
    if not params:
        return {"ok": False, "best_effort": True, "notes": "GET verify path has no path params"}
    last = params[-1]
    path = path.replace("{" + last + "}", rid)
    # Fill any remaining params with placeholders (can't infer safely).
    for p in params[:-1]:
        return {
            "ok": False,
            "best_effort": True,
            "notes": "GET verify requires additional path params; refusing best-effort guess",
            "path_template": tpl,
        }

    base_url = str(ctx["cfg"].base_url).rstrip("/")
    url = base_url + path
    client = HttpClient(timeout_s=float(ctx["timeout_s"]), verbose=bool(ctx.get("verbose")), user_agent="stripe-api-tool")
    try:
        resp = client.request(method="GET", url=url, headers=headers, retries=1)
        data = resp.json()
        ok = isinstance(data, dict) and str(data.get("id") or "").strip() == rid
        return {"ok": bool(ok), "best_effort": True, "path": path, "matched_id": rid if ok else None}
    except Exception as e:
        return {"ok": False, "best_effort": True, "path": path, "error": str(e)}


def cmd_api_operation(args: argparse.Namespace, ctx: dict[str, Any]) -> int:
    spec: OperationSpec = getattr(args, "_api_spec")

    stripe_account = str(getattr(args, "stripe_account", "") or "").strip() or None
    idempotency_key_user = str(getattr(args, "idempotency_key", "") or "").strip() or None
    risk = classify_operation(operation_id=spec.operation_id, method=spec.method, path_template=spec.path_template)

    # Build plan (and derived idempotency) deterministically from the request contents.
    derived_idempotency = None
    request = _build_request(
        spec=spec,
        args=args,
        ctx=ctx,
        idempotency_key=None,
    )
    plan = _build_plan(
        spec=spec,
        args=args,
        ctx=ctx,
        risk=risk,
        request=request,
        stripe_account=stripe_account,
        idempotency_key=idempotency_key_user,
    )
    if spec.method.lower().strip() not in _READ_METHODS and not idempotency_key_user:
        derived_idempotency = f"plan_{str(plan.get('stable_hash') or '')[:32]}"
        plan["idempotency_key"] = derived_idempotency
        headers = dict(plan.get("headers") or {})
        headers["idempotency-key"] = derived_idempotency
        plan["headers"] = headers

    plan_out = ctx.get("plan_out")
    if plan_out:
        plan_path = write_json_file(str(plan_out), plan)
    else:
        plan_path = None

    if spec.method.lower().strip() in _READ_METHODS:
        if not bool(getattr(args, "live", False)):
            out = {
                "ok": True,
                "dry_run": True,
                "live_required": True,
                "plan": plan,
                "plan_out": plan_path,
            }
            ctx["audit"].write("api.read.plan", {"operation_id": spec.operation_id, "plan_out": plan_path})
            ctx["out"].emit(out)
            return 0

        headers = _build_headers(ctx=ctx, stripe_account=stripe_account, idempotency_key=None)
        response = _execute_live(spec=spec, plan=plan, ctx=ctx, headers=headers)
        out = {"ok": True, "dry_run": False, "plan": plan, "response": response, "plan_out": plan_path}
        ctx["audit"].write("api.read.live", {"operation_id": spec.operation_id})
        ctx["out"].emit(out)
        return 0

    if not bool(ctx.get("apply")):
        out = {"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path}
        ctx["audit"].write("api.write.plan", {"operation_id": spec.operation_id, "plan_out": plan_path})
        ctx["out"].emit(out)
        return 0

    _risk_enforce(risk=risk, ctx=ctx)
    if ctx.get("plan_in"):
        plan_in_obj = _load_plan_in(str(ctx["plan_in"]))
        _validate_plan_for_apply(plan=plan_in_obj, current_plan=plan, ctx=ctx)

    if not bool(getattr(args, "live", False)):
        raise SafetyError("Refused: --live is required to execute Stripe API calls")

    if not bool(ctx.get("ack_no_snapshot")):
        raise SafetyError(
            "Refused: this Stripe write has no saved before-state snapshot or provider backup. "
            "Review the plan, confirm the recovery limit, then re-run with --ack-no-snapshot."
        )

    headers = _build_headers(
        ctx=ctx,
        stripe_account=stripe_account,
        idempotency_key=str(plan.get("idempotency_key") or "") or None,
    )
    response = _execute_live(spec=spec, plan=plan, ctx=ctx, headers=headers)
    verification = _best_effort_verify(
        spec=spec,
        response_json=response.get("json"),
        ctx=ctx,
        headers=headers,
    )
    receipt = {
        "kind": "stripe.http_receipt.v1",
        "tool": ctx.get("tool") or "stripe-api-tool",
        "version": ctx.get("tool_version") or None,
        "applied_at_utc": _utc_now(),
        "operation": plan.get("operation"),
        "request": plan.get("request"),
        "risk": plan.get("risk"),
        "before_state": plan.get("before_state"),
        "no_snapshot_approval": {"approved": True, "flag": "--ack-no-snapshot"},
        "rollback": plan.get("rollback"),
        "response": response,
        "verification": verification,
    }
    receipt_out = ctx.get("receipt_out")
    receipt_path = write_json_file(str(receipt_out), receipt) if receipt_out else None
    out = {"ok": True, "dry_run": False, "plan": plan, "receipt": receipt, "receipt_out": receipt_path}
    ctx["audit"].write(
        "api.write.apply",
        {
            "operation_id": spec.operation_id,
            "response_status": response.get("status"),
            "receipt_out": receipt_path,
            "no_snapshot_approval": True,
        },
    )
    ctx["out"].emit(out)
    return 0


def register_api_commands(sub: argparse._SubParsersAction) -> None:
    api = sub.add_parser("api", help="Pinned per-operation Stripe API commands (explicit)")
    api.add_argument(
        "--stripe-account",
        default=None,
        help="Optional connected account id (Stripe-Account header; allowlisted when configured)",
    )
    api.add_argument(
        "--live",
        action="store_true",
        help="Actually execute the API call (default is plan-only, even for reads)",
    )
    api_sub = api.add_subparsers(dest="api_cmd", required=True)

    specs = load_operation_specs()
    for s in specs:
        p = api_sub.add_parser(s.command_name, help=f"{s.method.upper()} {s.path_template}")
        for param in s.path_params:
            # Avoid collisions with argparse internals by namespacing dests.
            p.add_argument(f"--{param}", required=True, dest=f"path_{param}", help=f"Path param: {param}")
        p.add_argument("--query", action="append", default=[], help="Query param in k=v form (repeatable)")
        p.add_argument("--expand", action="append", default=[], help="Stripe expand field (repeatable; uses expand[])")
        p.add_argument("--data", action="append", default=[], help="Form body param in k=v form (repeatable)")
        p.add_argument("--upload", action="append", default=[], help="Multipart upload field in field=path form (repeatable)")
        p.add_argument(
            "--idempotency-key",
            default=None,
            help="Optional Idempotency-Key for writes (default is derived from the plan hash)",
        )
        p.set_defaults(func=cmd_api_operation, write_capable=(s.method.lower() not in _READ_METHODS), _api_spec=s)


def generate_official_commands_inventory() -> list[str]:
    specs = load_operation_specs()
    return [operation_command_line(s) for s in specs]
