from __future__ import annotations

import argparse
import base64
import hashlib
import json
import re
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from .config import Config
from .errors import SafetyError, ValidationError
from .http import HttpClient
from .json_files import read_json_file, write_json_file
from .openapi_ops import OperationSpec, load_operation_specs, operation_command_line
from .openapi_snapshot import OpenApiSnapshot, load_pinned_openapi_snapshot
from .redaction import redact_headers, redact_obj
from .risk import RiskClassification, classify_operation


_READ_METHODS = {"get", "head", "options"}


def _utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _json_canonical_dumps(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256_json(obj: Any) -> str:
    return hashlib.sha256(_json_canonical_dumps(obj).encode("utf-8")).hexdigest()


def _sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def _recovery_contract() -> dict[str, Any]:
    return {
        "automatic_rollback": False,
        "backups": [],
        "snapshots": [],
        "rollback_plan": None,
        "restore_note": "No automatic rollback, snapshots, or backups are created. If a restore action is available, run a separate explicit restore command as its own command.",
    }


def _before_state_contract(*, method: str) -> dict[str, Any]:
    if method.lower().strip() in _READ_METHODS:
        return {"required": False, "supported": False, "statement": "Read operation; no before-state capture required."}
    return {
        "required": True,
        "supported": False,
        "status": "no_snapshot_available",
        "approval_required": "--ack-no-snapshot",
        "statement": (
            "No useful before-state snapshot is captured for this Zendesk write. "
            "The write may still run after the reviewed plan and explicit no-snapshot approval."
        ),
    }


def _write_refusal_message() -> str:
    return (
        "Refused: this Zendesk write has no saved before-state snapshot. "
        "Review the plan, confirm the recovery limit, then re-run with --ack-no-snapshot."
    )


def _normalize_flag_fragment(name: str) -> str:
    s = str(name or "").strip().lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = re.sub(r"-{2,}", "-", s).strip("-")
    return s


def _ref_path_segments(ref: str) -> list[str] | None:
    r = str(ref or "").strip()
    if not r.startswith("#/"):
        return None
    return [seg for seg in r[2:].split("/") if seg]


def _resolve_local_ref(root: dict[str, Any], ref: str) -> Any:
    segs = _ref_path_segments(ref)
    if not segs:
        raise ValidationError(f"Unsupported $ref (expected local #/...): {ref!r}")
    cur: Any = root
    for seg in segs:
        if not isinstance(cur, dict) or seg not in cur:
            raise ValidationError(f"Could not resolve $ref: {ref!r}")
        cur = cur[seg]
    return cur


def _deref(root: dict[str, Any], obj: Any) -> Any:
    if not isinstance(obj, dict):
        return obj
    ref = obj.get("$ref")
    if not isinstance(ref, str) or not ref.strip():
        return obj
    resolved = _resolve_local_ref(root, ref)
    if not isinstance(resolved, dict):
        return resolved
    # OpenAPI allows siblings next to $ref. Best-effort merge with overrides.
    merged = dict(resolved)
    for k, v in obj.items():
        if k == "$ref":
            continue
        merged[k] = v
    return merged


def _paths_obj(snapshot: OpenApiSnapshot) -> dict[str, Any]:
    paths = snapshot.obj.get("paths") or {}
    if not isinstance(paths, dict):
        raise ValidationError("OpenAPI snapshot missing paths object")
    return paths


def _get_operation_obj(snapshot: OpenApiSnapshot, spec: OperationSpec) -> tuple[dict[str, Any], dict[str, Any]]:
    """
    Return (path_item_obj, op_obj) for the spec.
    """
    root = snapshot.obj
    paths = _paths_obj(snapshot)
    path_item = paths.get(spec.path_template)
    if not isinstance(path_item, dict):
        raise ValidationError(f"OpenAPI path not found: {spec.path_template!r}")
    op_obj_raw = path_item.get(spec.method.lower())
    if not isinstance(op_obj_raw, dict):
        raise ValidationError(f"OpenAPI operation not found: {spec.method.upper()} {spec.path_template}")
    return _deref(root, path_item), _deref(root, op_obj_raw)


@dataclass(frozen=True)
class OperationIo:
    query_params: tuple[tuple[str, bool], ...]  # (name, required)
    has_request_body: bool
    body_supports_json: bool
    body_supports_multipart: bool
    body_supports_binary: bool

    @property
    def supports_file_upload(self) -> bool:
        return self.body_supports_multipart or self.body_supports_binary


def _collect_parameters(root: dict[str, Any], path_item: dict[str, Any], op_obj: dict[str, Any]) -> list[dict[str, Any]]:
    params: list[Any] = []
    for src in (path_item.get("parameters"), op_obj.get("parameters")):
        if isinstance(src, list):
            params.extend(src)

    out: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for p in params:
        po = _deref(root, p)
        if not isinstance(po, dict):
            continue
        name = str(po.get("name") or "").strip()
        loc = str(po.get("in") or "").strip()
        if not name or not loc:
            continue
        key = (loc, name)
        if key in seen:
            continue
        seen.add(key)
        out.append(po)
    return out


def _request_body_obj(root: dict[str, Any], op_obj: dict[str, Any]) -> dict[str, Any] | None:
    rb = op_obj.get("requestBody")
    if rb is None:
        return None
    rb2 = _deref(root, rb)
    return rb2 if isinstance(rb2, dict) else None


def _content_types(request_body: dict[str, Any]) -> list[str]:
    content = request_body.get("content") or {}
    if not isinstance(content, dict):
        return []
    return sorted([str(k).strip().lower() for k in content.keys() if isinstance(k, str) and str(k).strip()])


def _operation_io(snapshot: OpenApiSnapshot, spec: OperationSpec) -> OperationIo:
    root = snapshot.obj
    path_item, op_obj = _get_operation_obj(snapshot, spec)
    params = _collect_parameters(root, path_item, op_obj)

    q: list[tuple[str, bool]] = []
    for p in params:
        if str(p.get("in") or "").strip() != "query":
            continue
        name = str(p.get("name") or "").strip()
        if not name:
            continue
        required = bool(p.get("required"))
        q.append((name, required))

    rb = _request_body_obj(root, op_obj)
    if not rb:
        return OperationIo(
            query_params=tuple(sorted(q, key=lambda x: x[0])),
            has_request_body=False,
            body_supports_json=False,
            body_supports_multipart=False,
            body_supports_binary=False,
        )

    cts = _content_types(rb)
    supports_json = any(ct in {"application/json", "application/*+json"} or ct.endswith("+json") for ct in cts)
    supports_multipart = any(ct == "multipart/form-data" for ct in cts)
    supports_binary = any(ct in {"application/octet-stream"} for ct in cts)
    return OperationIo(
        query_params=tuple(sorted(q, key=lambda x: x[0])),
        has_request_body=True,
        body_supports_json=supports_json,
        body_supports_multipart=supports_multipart,
        body_supports_binary=supports_binary,
    )


def _auth_mode(cfg: Config) -> str | None:
    if cfg.oauth_access_token:
        return "oauth_bearer"
    if cfg.email and cfg.api_token:
        return "api_token_basic"
    return None


def _build_headers_for_live(*, cfg: Config) -> dict[str, str]:
    mode = _auth_mode(cfg)
    if mode == "oauth_bearer":
        return {"Authorization": f"Bearer {cfg.oauth_access_token}"}
    if mode == "api_token_basic":
        raw = f"{cfg.email}/token:{cfg.api_token}".encode("utf-8")
        b64 = base64.b64encode(raw).decode("ascii")
        return {"Authorization": f"Basic {b64}"}
    raise SafetyError("Missing Zendesk credentials: set ZENDESK_EMAIL + ZENDESK_API_TOKEN or ZENDESK_OAUTH_ACCESS_TOKEN")


def _build_headers_for_plan(*, cfg: Config) -> dict[str, str]:
    mode = _auth_mode(cfg)
    if mode:
        # Redaction happens later; keep a stable key in the plan so users can tell auth is configured.
        return {"Authorization": "configured"}
    return {}


def _extract_rate_limit_headers(headers: dict[str, str]) -> dict[str, str]:
    keep: dict[str, str] = {}
    for k, v in (headers or {}).items():
        lk = str(k).lower().strip()
        if lk in {"retry-after"} or "rate" in lk or "ratelimit" in lk:
            keep[lk] = v
    return keep


@dataclass(frozen=True)
class _PlannedRequest:
    method: str
    url: str
    path: str
    query: tuple[tuple[str, str], ...]
    json_body: Any | None
    json_body_sha256: str | None
    body_file: dict[str, Any] | None
    file_upload: dict[str, Any] | None


def _read_body_file(path: str) -> tuple[bytes, dict[str, Any]]:
    fp = Path(path)
    if not fp.exists() or not fp.is_file():
        raise ValidationError(f"Body file not found: {fp}")
    b = fp.read_bytes()
    meta = {
        "path": str(fp),
        "filename": fp.name,
        "size_bytes": len(b),
        "sha256": _sha256_bytes(b),
    }
    return b, meta


def _read_upload_file(path: str) -> tuple[bytes, dict[str, Any]]:
    fp = Path(path)
    if not fp.exists() or not fp.is_file():
        raise ValidationError(f"File not found: {fp}")
    b = fp.read_bytes()
    meta = {
        "path": str(fp),
        "filename": fp.name,
        "size_bytes": len(b),
        "sha256": _sha256_bytes(b),
    }
    return b, meta


def _build_request(
    *,
    spec: OperationSpec,
    op_io: OperationIo,
    args: argparse.Namespace,
    ctx: dict[str, Any],
) -> _PlannedRequest:
    path = spec.path_template
    for p in spec.path_params:
        attr = f"path_{p}"
        v = str(getattr(args, attr, "") or "").strip()
        if not v:
            raise ValidationError(f"Missing required path param: --{p}")
        path = path.replace("{" + p + "}", v)

    query_pairs: list[tuple[str, str]] = []
    query_map: list[tuple[str, str]] = list(getattr(args, "_api_query_map", []) or [])
    for param_name, dest in query_map:
        raw = getattr(args, dest, None)
        if raw is None:
            continue
        if isinstance(raw, bool):
            if raw:
                query_pairs.append((param_name, "true"))
            continue
        s = str(raw).strip()
        if s != "":
            query_pairs.append((param_name, s))

    base_url = str(ctx["cfg"].base_url).rstrip("/")
    url = base_url + path

    json_body = None
    json_body_sha = None
    body_file_meta = None
    if op_io.has_request_body and op_io.body_supports_json:
        body_json_raw = getattr(args, "body_json", None)
        body_file_raw = getattr(args, "body_file", None)
        if body_json_raw and body_file_raw:
            raise ValidationError("Provide exactly one of --body-json or --body-file")
        if body_json_raw:
            try:
                json_body = json.loads(str(body_json_raw))
            except Exception as e:  # noqa: BLE001
                raise ValidationError(f"Invalid --body-json: {type(e).__name__}: {e}") from None
            json_body_sha = _sha256_json(json_body)
        elif body_file_raw:
            b, meta = _read_body_file(str(body_file_raw))
            try:
                json_body = json.loads(b.decode("utf-8"))
            except Exception as e:  # noqa: BLE001
                raise ValidationError(f"Invalid JSON in --body-file: {meta['path']}: {type(e).__name__}: {e}") from None
            body_file_meta = meta
            json_body_sha = meta["sha256"]

    file_upload_meta = None
    if op_io.supports_file_upload:
        upload_path = str(getattr(args, "file", "") or "").strip()
        if upload_path:
            _b, meta = _read_upload_file(upload_path)
            meta = dict(meta)
            meta["field"] = str(getattr(args, "file_field", "") or "file").strip() or "file"
            file_upload_meta = meta

    return _PlannedRequest(
        method=spec.method.upper(),
        url=url,
        path=path,
        query=tuple(sorted(query_pairs)),
        json_body=json_body,
        json_body_sha256=json_body_sha,
        body_file=body_file_meta,
        file_upload=file_upload_meta,
    )


def _build_plan(
    *,
    spec: OperationSpec,
    risk: RiskClassification,
    request: _PlannedRequest,
    ctx: dict[str, Any],
) -> dict[str, Any]:
    cfg: Config = ctx["cfg"]
    headers = _build_headers_for_plan(cfg=cfg)
    plan_obj: dict[str, Any] = {
        "kind": "zendesk.http_plan.v1",
        "tool": ctx.get("tool") or "zendesk-api-tool",
        "version": ctx.get("tool_version") or None,
        "generated_at_utc": _utc_now(),
        "env_fingerprint": cfg.base_url,
        "command": ctx.get("command_str") or None,
        "auth": {"mode": _auth_mode(cfg), "configured": bool(_auth_mode(cfg))},
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
            "json_body": request.json_body,
            "json_body_sha256": request.json_body_sha256,
            "body_file": request.body_file,
            "file_upload": request.file_upload,
        },
        "headers": redact_headers(headers),
        "risk": {"level": risk.level, "reasons": list(risk.reasons), "requirements": asdict(risk.requirements)},
        "before_state": _before_state_contract(method=request.method),
        "recovery": _recovery_contract(),
    }
    stable_hash_input = {
        "env_fingerprint": plan_obj["env_fingerprint"],
        "auth_mode": plan_obj["auth"]["mode"],
        "operation": plan_obj["operation"],
        "request": {
            "method": request.method,
            "path": request.path,
            "query": list(request.query),
            "json_body_sha256": request.json_body_sha256,
            "body_file": request.body_file,
            "file_upload": request.file_upload,
        },
        "risk": plan_obj["risk"],
    }
    plan_obj["stable_hash"] = _sha256_json(stable_hash_input)
    return plan_obj


def _risk_enforce(*, risk: RiskClassification, ctx: dict[str, Any]) -> None:
    req = risk.requirements
    if req.apply and not bool(ctx.get("apply")):
        raise SafetyError("Refused: --apply is required for this operation")
    if req.yes and not bool(ctx.get("yes")):
        raise SafetyError("Refused: --yes is required for this high-risk operation")
    if req.plan_in and not bool(ctx.get("plan_in")):
        raise SafetyError("Refused: --plan-in is required for this high-risk operation")
    if req.ack_irreversible and not bool(ctx.get("ack_irreversible")):
        raise SafetyError("Refused: --ack-irreversible is required for irreversible operations")


def _load_plan_in(path: str) -> dict[str, Any]:
    plan_obj = read_json_file(path)
    if not isinstance(plan_obj, dict):
        raise ValidationError("--plan-in file must be a JSON object")
    return plan_obj


def _validate_plan_for_apply(*, plan: dict[str, Any], current_plan: dict[str, Any], ctx: dict[str, Any]) -> None:
    if str(plan.get("kind") or "") != "zendesk.http_plan.v1":
        raise ValidationError("Plan kind mismatch (expected zendesk.http_plan.v1)")
    if str(plan.get("env_fingerprint") or "") != str(ctx["cfg"].base_url):
        raise SafetyError("Refused: plan env_fingerprint does not match current environment")
    if str(plan.get("stable_hash") or "") != str(current_plan.get("stable_hash") or ""):
        raise SafetyError("Refused: current request does not match --plan-in (drift detected)")
    op = plan.get("operation")
    cur_op = current_plan.get("operation")
    if not isinstance(op, dict) or not isinstance(cur_op, dict):
        raise ValidationError("Plan missing operation object")
    if str(op.get("id") or "") != str(cur_op.get("id") or ""):
        raise SafetyError("Refused: plan operation id does not match current operation")


def _execute_live(
    *,
    plan: dict[str, Any],
    ctx: dict[str, Any],
    headers: dict[str, str],
) -> dict[str, Any]:
    client = HttpClient(timeout_s=float(ctx["timeout_s"]), verbose=bool(ctx.get("verbose")), user_agent="zendesk-api-tool")
    req = plan.get("request") or {}
    if not isinstance(req, dict):
        raise ValidationError("Plan request missing")

    method = str(req.get("method") or "").strip()
    url = str(req.get("url") or "").strip()
    query = req.get("query") or []
    json_body = req.get("json_body")
    file_upload = req.get("file_upload")

    params = dict(query) if isinstance(query, list) else None

    files: dict[str, tuple[str, bytes]] | None = None
    if isinstance(file_upload, dict) and str(file_upload.get("path") or "").strip():
        field = str(file_upload.get("field") or "file").strip() or "file"
        path = str(file_upload.get("path") or "").strip()
        filename = str(file_upload.get("filename") or "").strip() or "upload"
        b = Path(path).read_bytes()
        files = {field: (filename, b)}

    resp = client.request(
        method=method,
        url=url,
        headers=headers,
        params=params,
        json_body=json_body if isinstance(json_body, (dict, list)) else None,
        files=files,
        retries=3,
    )

    resp_json: Any = None
    try:
        resp_json = resp.json()
    except Exception:
        resp_json = {"raw_text": resp.text()}

    return {
        "status": resp.status,
        "url": resp.url,
        "rate_limit": _extract_rate_limit_headers(resp.headers),
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
    if not isinstance(response_json, dict):
        return {"ok": False, "best_effort": True, "notes": "No JSON object response to verify against"}

    # Zendesk often uses { "ticket": { "id": ... } } shapes.
    rid = None
    if isinstance(response_json.get("id"), (int, str)):
        rid = str(response_json.get("id"))
    if not rid:
        for k in ("ticket", "user", "organization", "group", "comment", "attachment"):
            v = response_json.get(k)
            if isinstance(v, dict) and isinstance(v.get("id"), (int, str)):
                rid = str(v.get("id"))
                break
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
    params = re.findall(r"{([^}]+)}", tpl)
    if not params:
        return {"ok": False, "best_effort": True, "notes": "GET verify path has no path params"}
    last = params[-1]
    path = tpl.replace("{" + last + "}", rid)
    if len(params) > 1:
        return {
            "ok": False,
            "best_effort": True,
            "notes": "GET verify requires additional path params; refusing best-effort guess",
            "path_template": tpl,
        }

    base_url = str(ctx["cfg"].base_url).rstrip("/")
    url = base_url + path
    client = HttpClient(timeout_s=float(ctx["timeout_s"]), verbose=bool(ctx.get("verbose")), user_agent="zendesk-api-tool")
    try:
        resp = client.request(method="GET", url=url, headers=headers, retries=2)
        data = resp.json()
        ok = isinstance(data, dict)
        return {"ok": bool(ok), "best_effort": True, "path": path, "matched_id": rid if ok else None}
    except Exception as e:
        return {"ok": False, "best_effort": True, "path": path, "error": str(e)}


def cmd_api_operation(args: argparse.Namespace, ctx: dict[str, Any]) -> int:
    spec: OperationSpec = getattr(args, "_api_spec")
    op_io: OperationIo = getattr(args, "_api_io")

    risk = classify_operation(operation_id=spec.operation_id, method=spec.method, path_template=spec.path_template)
    request = _build_request(spec=spec, op_io=op_io, args=args, ctx=ctx)
    plan = _build_plan(spec=spec, risk=risk, request=request, ctx=ctx)

    plan_out = ctx.get("plan_out")
    plan_path = write_json_file(str(plan_out), plan) if plan_out else None

    if spec.method.lower().strip() in _READ_METHODS:
        if not bool(getattr(args, "live", False)):
            out = {"ok": True, "dry_run": True, "live_required": True, "plan": plan, "plan_out": plan_path}
            ctx["audit"].write("api.read.plan", {"operation_id": spec.operation_id, "plan_out": plan_path})
            ctx["out"].emit(out)
            return 0

        headers = _build_headers_for_live(cfg=ctx["cfg"])
        response = _execute_live(plan=plan, ctx=ctx, headers=headers)
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
        raise SafetyError("Refused: --live is required to execute Zendesk API calls")
    if not bool(ctx.get("ack_no_snapshot")):
        raise SafetyError(
            "Refused: this Zendesk write has no saved before-state snapshot. "
            "Review the plan, confirm the recovery limit, then re-run with --ack-no-snapshot."
        )

    headers = _build_headers_for_live(cfg=ctx["cfg"])
    response = _execute_live(plan=plan, ctx=ctx, headers=headers)
    verification = _best_effort_verify(spec=spec, response_json=response.get("json"), ctx=ctx, headers=headers)
    receipt = {
        "kind": "zendesk.http_receipt.v1",
        "tool": ctx.get("tool") or "zendesk-api-tool",
        "version": ctx.get("tool_version") or None,
        "applied_at_utc": _utc_now(),
        "operation": plan.get("operation"),
        "request": plan.get("request"),
        "risk": plan.get("risk"),
        "before_state": plan.get("before_state"),
        "no_snapshot_approval": {"approved": True, "flag": "--ack-no-snapshot"},
        "recovery": plan.get("recovery"),
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
    api = sub.add_parser("api", help="Pinned per-operation Zendesk Ticketing API commands (explicit)")
    api.add_argument(
        "--live",
        action="store_true",
        help="Actually execute the API call (default is plan-only, even for reads)",
    )
    api_sub = api.add_subparsers(dest="api_cmd", required=True)

    snapshot = load_pinned_openapi_snapshot()
    specs = load_operation_specs(snapshot)

    # Build per-operation command parsers (explicit; no generic bridge).
    for s in specs:
        op_io = _operation_io(snapshot, s)
        p = api_sub.add_parser(s.command_name, help=f"{s.method.upper()} {s.path_template}")

        for param in s.path_params:
            p.add_argument(f"--{param}", required=True, dest=f"path_{param}", help=f"Path param: {param}")

        query_map: list[tuple[str, str]] = []
        used_query_opts: set[str] = set()
        used_query_dests: set[str] = set()
        for name, required in op_io.query_params:
            base_frag = _normalize_flag_fragment(name)
            if not base_frag:
                continue
            frag = base_frag
            i = 2
            while f"--q-{frag}" in used_query_opts:
                frag = f"{base_frag}-{i}"
                i += 1
            opt = f"--q-{frag}"
            used_query_opts.add(opt)

            base_dest = f"q_{base_frag.replace('-', '_')}"
            dest = base_dest
            j = 2
            while dest in used_query_dests:
                dest = f"{base_dest}_{j}"
                j += 1
            used_query_dests.add(dest)
            p.add_argument(opt, required=bool(required), dest=dest, default=None, help=f"Query param: {name}")
            query_map.append((name, dest))

        # Attach a stable mapping so runtime can build the correct query names.
        p.set_defaults(_api_query_map=tuple(query_map))

        if op_io.has_request_body and op_io.body_supports_json:
            p.add_argument("--body-json", default=None, help="Request body JSON string")
            p.add_argument("--body-file", default=None, help="Request body JSON file path")

        if op_io.supports_file_upload:
            p.add_argument("--file", default=None, help="Upload file path (multipart/binary operations)")
            p.add_argument("--file-field", default="file", help="Multipart field name (default: file)")

        write_capable = s.method.lower().strip() not in _READ_METHODS
        p.set_defaults(func=cmd_api_operation, write_capable=write_capable, _api_spec=s, _api_io=op_io)


def generate_official_commands_inventory() -> list[str]:
    snapshot = load_pinned_openapi_snapshot()
    specs = load_operation_specs(snapshot)
    return [operation_command_line(s) for s in specs]
