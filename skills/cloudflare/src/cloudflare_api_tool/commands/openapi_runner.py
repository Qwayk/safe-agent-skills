from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ..errors import SafetyError, ToolError, ValidationError
from ..json_files import read_json_file, write_json_file
from ..openapi_index import OperationIndex, OperationSpec, is_read_like_non_get_operation, load_allowlisted_operation_index
from ..plan_and_receipt import (
    load_plan_in,
    require_plan_matches,
    resolve_safe_out_path,
    sha256_of_bytes,
    utc_now,
    write_plan_if_requested,
    write_receipt_if_requested,
)


def _require_token(ctx: dict) -> None:
    cfg = ctx.get("cfg")
    token = getattr(cfg, "token", None) if cfg else None
    if not token:
        raise ValidationError("Missing CLOUDFLARE_API_TOKEN")


def _require_apply(ctx: dict) -> None:
    if not bool(ctx.get("apply")):
        raise SafetyError("Refusing to apply: this command is dry-run by default (pass --apply).")


def _require_yes(ctx: dict) -> None:
    if not bool(ctx.get("yes")):
        raise SafetyError("Refusing to apply: Cloudflare API writes require --yes.")


def _require_ack_irreversible(ctx: dict) -> None:
    if not bool(ctx.get("ack_irreversible")):
        raise SafetyError("Refusing: this operation is irreversible-ish or can return/create a secret and requires --ack-irreversible.")


def _requires_ack_irreversible(spec: OperationSpec | None) -> bool:
    """
    Extra safety gate for operations that are irreversible even if they are not classified as secret-bearing.

    Keep this list explicit and small.
    """
    if spec is None:
        return False
    # Conservative: require explicit acknowledgement for destructive operations on high-blast-radius top-level
    # surfaces (user/org/system). These can impact access control, governance, or secrets.
    if str(spec.method or "").upper().strip() == "DELETE":
        p = str(spec.path_template or "").strip()
        if p.startswith(("/user", "/organizations", "/memberships", "/system", "/certificates", "/destinations")):
            return True
    op_id = str(spec.operation_id or "").strip()
    if op_id in {
        # Phase 25: Zone deletion is destructive and irreversible-ish.
        "zones-0-delete",
        # Phase 9: Pages deployment rollback is a state-changing rollback action.
        "pages-deployment-rollback-deployment",
        # Phase 10: Images signing keys operations can return key material and should be explicitly acknowledged.
        "cloudflare-images-keys-list-signing-keys",
        "cloudflare-images-keys-add-signing-key",
        "cloudflare-images-keys-delete-signing-key",
        # Phase 23: Accounts writes — reviewed irreversible-ish actions (beyond DELETE /accounts*).
        "purgeBuildCache",
        "custom-indicator-feeds-remove-permission",
    }:
        return True
    return False


def _is_account_write_operation(*, method: str, path_template: str) -> bool:
    m = str(method or "").upper().strip()
    p = str(path_template or "").strip()
    if m not in {"POST", "PUT", "PATCH", "DELETE"}:
        return False
    return p == "/accounts" or p.startswith("/accounts/")


def _parse_kv_list(items: list[str] | None) -> dict[str, str]:
    out: dict[str, str] = {}
    for s in items or []:
        raw = str(s or "")
        if "=" not in raw:
            raise ValidationError(f"Invalid key=value: {raw!r}")
        k, v = raw.split("=", 1)
        k = k.strip()
        if not k:
            raise ValidationError(f"Invalid key=value (empty key): {raw!r}")
        out[k] = v
    return out


def _resolve_path(path_template: str, path_params: dict[str, str]) -> str:
    resolved = str(path_template)
    for k, v in path_params.items():
        resolved = resolved.replace("{" + str(k) + "}", str(v))
    if "{" in resolved or "}" in resolved:
        # Likely missing params.
        raise ValidationError(f"Missing path params for template: {path_template!r} (got: {sorted(path_params.keys())})")
    return resolved


def _load_body(
    *,
    body_json_file: str | None,
    body_bytes_file: str | None,
    multipart_spec_file: str | None,
) -> tuple[str, Any | None, bytes | None, Any | None, dict[str, Any]]:
    """
    Returns: (kind, json_body, bytes_body, files, meta)

    - kind: "none" | "json" | "bytes" | "multipart"
    - files: passed through to requests; format is validated lightly here.
    - meta: safe metadata only (hashes, sizes, filenames), never content.
    """
    picked = [bool(body_json_file), bool(body_bytes_file), bool(multipart_spec_file)]
    if sum(1 for x in picked if x) > 1:
        raise ValidationError("Body inputs are mutually exclusive: choose only one of --body-json-file/--body-bytes-file/--multipart-spec-file")

    if body_json_file:
        obj = read_json_file(body_json_file)
        raw = json.dumps(obj, ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode("utf-8")
        return (
            "json",
            obj if isinstance(obj, dict) else obj,
            None,
            None,
            {"body_kind": "json", "sha256": sha256_of_bytes(raw), "size_bytes": len(raw), "source": str(body_json_file)},
        )

    if body_bytes_file:
        p = Path(body_bytes_file)
        if not p.exists():
            raise ValidationError(f"Body file not found: {p}")
        data = p.read_bytes()
        return (
            "bytes",
            None,
            data,
            None,
            {"body_kind": "bytes", "sha256": sha256_of_bytes(data), "size_bytes": len(data), "source": str(body_bytes_file)},
        )

    if multipart_spec_file:
        spec = read_json_file(multipart_spec_file)
        if not isinstance(spec, dict):
            raise ValidationError("Multipart spec must be a JSON object.")
        fields = spec.get("fields") or {}
        files = spec.get("files") or []
        if fields and not isinstance(fields, dict):
            raise ValidationError("Multipart spec 'fields' must be an object.")
        if not isinstance(files, list):
            raise ValidationError("Multipart spec 'files' must be a list.")

        req_files: dict[str, Any] = {}
        meta_files: list[dict[str, Any]] = []
        for entry in files:
            if not isinstance(entry, dict):
                raise ValidationError("Multipart spec 'files' entries must be objects.")
            name = str(entry.get("name") or "").strip()
            path = str(entry.get("path") or "").strip()
            if not name or not path:
                raise ValidationError("Multipart spec file entry must include 'name' and 'path'.")
            p = Path(path)
            if not p.exists():
                raise ValidationError(f"Multipart file not found: {p}")
            filename = str(entry.get("filename") or p.name)
            content_type = str(entry.get("content_type") or "").strip() or None
            data = p.read_bytes()
            # requests accepts (filename, bytes, content_type)
            req_files[name] = (filename, data, content_type) if content_type else (filename, data)
            meta_files.append(
                {
                    "name": name,
                    "filename": filename,
                    "source": str(p),
                    "size_bytes": len(data),
                    "sha256": sha256_of_bytes(data),
                    "content_type": content_type,
                }
            )

        meta = {"body_kind": "multipart", "fields_keys": sorted([str(k) for k in (fields or {}).keys()]), "files": meta_files, "source": str(multipart_spec_file)}
        return ("multipart", None, None, {"fields": fields, "files": req_files}, meta)

    return ("none", None, None, None, {"body_kind": "none"})


def _best_effort_verify(
    *,
    idx: OperationIndex,
    ctx: dict,
    spec: OperationSpec | None,
    method: str,
    path_template: str,
    resolved_path: str,
    path_params: dict[str, str],
    response_result: Any,
) -> dict[str, Any]:
    """
    Verification rules (best-effort):
    - PUT/PATCH: if GET same template exists, GET it and consider success verification.
    - DELETE: if GET same template exists, GET should fail (404 or success=false).
    - POST: try to infer an id from response_result and GET the most plausible GET endpoint.
    - Otherwise: verification is based on API response success only.
    """
    cf = ctx["cf"]
    method_u = str(method).upper()

    def _try_get(path_t: str, params_for_path: dict[str, str]) -> tuple[bool, Any, int]:
        p = _resolve_path(path_t, params_for_path)
        resp = cf.request_raw_allow_errors("GET", p)
        if resp.status >= 400:
            return (False, None, int(resp.status))
        try:
            obj = json.loads(resp.body.decode("utf-8"))
        except Exception:
            return (True, None, int(resp.status))
        # Cloudflare envelope success may exist
        if isinstance(obj, dict) and "success" in obj and obj.get("success") is False:
            return (False, obj, int(resp.status))
        return (True, obj, int(resp.status))

    if method_u in {"PUT", "PATCH"}:
        get_spec = idx.get_by_method_path(method="GET", path_template=path_template)
        if get_spec:
            ok, obj, status = _try_get(path_template, path_params)
            return {"ok": ok, "method": "read_back_get_same_path", "http_status": status, "details": {"get_operation_id": get_spec.operation_id, "get_tags": get_spec.tags}, "evidence": obj if ok else None}
        return {"ok": True, "method": "api_response_success", "details": {"note": "No GET endpoint found for read-back in snapshot."}}

    if method_u == "DELETE":
        get_spec = idx.get_by_method_path(method="GET", path_template=path_template)
        if get_spec:
            ok, _obj, status = _try_get(path_template, path_params)
            # For delete, not-found is expected.
            return {"ok": (not ok), "method": "read_back_get_same_path_expected_missing", "http_status": status, "details": {"get_operation_id": get_spec.operation_id, "get_tags": get_spec.tags}}
        return {"ok": True, "method": "api_response_success", "details": {"note": "No GET endpoint found for read-back in snapshot."}}

    # Phase 9: Pages retry/rollback endpoints can be verified via a read-back GET of the deployment
    # using the already-known deployment_id path param (no need to parse a response body).
    if method_u == "POST" and path_template in {
        "/accounts/{account_id}/pages/projects/{project_name}/deployments/{deployment_id}/retry",
        "/accounts/{account_id}/pages/projects/{project_name}/deployments/{deployment_id}/rollback",
    }:
        get_template = "/accounts/{account_id}/pages/projects/{project_name}/deployments/{deployment_id}"
        get_spec = idx.get_by_method_path(method="GET", path_template=get_template)
        if get_spec:
            ok, obj, status = _try_get(get_template, path_params)
            return {
                "ok": ok,
                "method": "read_back_get_pages_deployment",
                "http_status": status,
                "details": {"get_operation_id": get_spec.operation_id, "get_tags": get_spec.tags},
                "evidence": obj if ok else None,
            }
        return {"ok": True, "method": "api_response_success", "details": {"note": "No GET endpoint found for Pages deployment read-back in snapshot."}}

    if method_u == "POST" and isinstance(response_result, dict):
        rid = None
        for key in ["id", "uuid", "tunnel_id", "rule_id", "app_id", "policy_id", "list_id", "device_id"]:
            v = response_result.get(key)
            if v is not None and str(v).strip():
                rid = str(v).strip()
                break
        if rid:
            # Prefer GET endpoints with same tag prefix and exactly one extra path param.
            candidates: list[OperationSpec] = []
            for s in idx.all_specs():
                if s.method != "GET":
                    continue
                if spec and s.area != spec.area:
                    continue
                if spec and s.tags and spec.tags and s.tags != spec.tags:
                    continue
                if not s.path_template.startswith(path_template.rstrip("/") + "/"):
                    continue
                if s.path_template.count("{") != path_template.count("{") + 1:
                    continue
                candidates.append(s)
            for c in candidates[:8]:
                # Fill all known params plus guess last param name from template.
                params_for_path = dict(path_params)
                # Find the extra param name in candidate.
                import re

                names = re.findall(r"\{([^}]+)\}", c.path_template)
                for name in names:
                    if name not in params_for_path and name not in {"account_id", "zone_id"}:
                        params_for_path[name] = rid
                ok, obj, status = _try_get(c.path_template, params_for_path)
                if ok:
                    return {"ok": True, "method": "read_back_get_inferred", "http_status": status, "details": {"get_operation_id": c.operation_id, "get_path_template": c.path_template, "get_tags": c.tags}, "evidence": obj}
            return {"ok": True, "method": "api_response_success", "details": {"note": "Could not infer a read-back GET path from snapshot."}}

    return {"ok": True, "method": "api_response_success", "details": {"note": "No write performed or no read-back rule applied."}}


def _best_effort_verify_redacted(
    *,
    idx: OperationIndex,
    ctx: dict,
    spec: OperationSpec | None,
    method: str,
    path_template: str,
    resolved_path: str,
    path_params: dict[str, str],
    response_result: Any,
) -> dict[str, Any]:
    """
    Sensitive-write verification: do best-effort read-back without embedding response bodies in receipts.

    Evidence is recorded only as (http_status, size_bytes, sha256) of any verification GET response body.
    """
    cf = ctx["cf"]
    method_u = str(method).upper()

    def _try_get_digest(path_t: str, params_for_path: dict[str, str]) -> tuple[bool, int, dict[str, Any] | None]:
        p = _resolve_path(path_t, params_for_path)
        resp = cf.request_raw_allow_errors("GET", p)
        status = int(resp.status)
        body = resp.body or b""
        ok = status < 400
        try:
            obj = json.loads(body.decode("utf-8"))
            if isinstance(obj, dict) and "success" in obj and obj.get("success") is False:
                ok = False
        except Exception:
            pass
        digest = {"http_status": status, "size_bytes": len(body), "sha256": sha256_of_bytes(body)} if body else {"http_status": status, "size_bytes": 0}
        return (ok, status, digest)

    if method_u in {"PUT", "PATCH"}:
        get_spec = idx.get_by_method_path(method="GET", path_template=path_template)
        if get_spec:
            ok, _status, digest = _try_get_digest(path_template, path_params)
            return {
                "ok": ok,
                "method": "read_back_get_same_path_redacted",
                "http_status": int((digest or {}).get("http_status") or 0),
                "details": {"get_operation_id": get_spec.operation_id, "get_tags": get_spec.tags},
                "evidence": digest,
            }
        return {"ok": True, "method": "api_response_success", "details": {"note": "No GET endpoint found for read-back in snapshot."}}

    if method_u == "DELETE":
        get_spec = idx.get_by_method_path(method="GET", path_template=path_template)
        if get_spec:
            ok, status, _digest = _try_get_digest(path_template, path_params)
            # For delete, not-found (or envelope success=false) is expected.
            return {
                "ok": (not ok),
                "method": "read_back_get_same_path_expected_missing",
                "http_status": int(status),
                "details": {"get_operation_id": get_spec.operation_id, "get_tags": get_spec.tags},
            }
        return {"ok": True, "method": "api_response_success", "details": {"note": "No GET endpoint found for read-back in snapshot."}}

    # Phase 9: Pages retry/rollback endpoints can be verified via a read-back GET of the deployment
    # using the already-known deployment_id path param (no need to parse a response body).
    if method_u == "POST" and path_template in {
        "/accounts/{account_id}/pages/projects/{project_name}/deployments/{deployment_id}/retry",
        "/accounts/{account_id}/pages/projects/{project_name}/deployments/{deployment_id}/rollback",
    }:
        get_template = "/accounts/{account_id}/pages/projects/{project_name}/deployments/{deployment_id}"
        get_spec = idx.get_by_method_path(method="GET", path_template=get_template)
        if get_spec:
            ok, _status, digest = _try_get_digest(get_template, path_params)
            return {
                "ok": ok,
                "method": "read_back_get_pages_deployment",
                "http_status": int((digest or {}).get("http_status") or 0),
                "details": {"get_operation_id": get_spec.operation_id, "get_tags": get_spec.tags},
                "evidence": digest,
            }
        return {"ok": True, "method": "api_response_success", "details": {"note": "No GET endpoint found for Pages deployment read-back in snapshot."}}

    if method_u == "POST" and isinstance(response_result, dict):
        rid = None
        for key in ["id", "uuid", "tunnel_id", "rule_id", "app_id", "policy_id", "list_id", "device_id", "name"]:
            v = response_result.get(key)
            if v is not None and str(v).strip():
                rid = str(v).strip()
                break
        if rid:
            candidates: list[OperationSpec] = []
            for s in idx.all_specs():
                if s.method != "GET":
                    continue
                if spec and s.area != spec.area:
                    continue
                if spec and s.tags and spec.tags and s.tags != spec.tags:
                    continue
                if not s.path_template.startswith(path_template.rstrip("/") + "/"):
                    continue
                if s.path_template.count("{") != path_template.count("{") + 1:
                    continue
                candidates.append(s)
            for c in candidates[:8]:
                params_for_path = dict(path_params)
                import re

                names = re.findall(r"\{([^}]+)\}", c.path_template)
                for name in names:
                    if name not in params_for_path and name not in {"account_id", "zone_id"}:
                        params_for_path[name] = rid
                ok, _status, digest = _try_get_digest(c.path_template, params_for_path)
                if ok:
                    return {
                        "ok": True,
                        "method": "read_back_get_inferred_redacted",
                        "http_status": int((digest or {}).get("http_status") or 0),
                        "details": {"get_operation_id": c.operation_id, "get_path_template": c.path_template, "get_tags": c.tags},
                        "evidence": digest,
                    }
            return {"ok": True, "method": "api_response_success", "details": {"note": "Could not infer a read-back GET path from snapshot."}}

    _ = resolved_path
    return {"ok": True, "method": "api_response_success", "details": {"note": "No read-back rule applied."}}


def _capture_before_state(
    *,
    idx: OperationIndex,
    ctx: dict,
    spec: OperationSpec | None,
    method: str,
    path_template: str,
    resolved_path: str,
    path_params: dict[str, str],
) -> tuple[dict[str, Any], str | None]:
    if str(method).upper() == "GET":
        return {"saved": False, "reason": "Read-only operation."}, None
    get_spec, before_path = _before_state_read_target(
        idx=idx,
        method=method,
        path_template=path_template,
        path_params=path_params,
    )
    if get_spec is None or not before_path:
        return {
            "saved": False,
            "reason": "No matching GET endpoint exists in the local allowlist for this write family.",
            "path_template": path_template,
            "path_resolved": resolved_path,
        }, None
    resp = ctx["cf"].request_raw_allow_errors("GET", before_path)
    body = resp.body or b""
    content_type = ""
    headers = getattr(resp, "headers", None)
    if isinstance(headers, dict):
        content_type = str(headers.get("content-type") or "")
    body_kind = "json" if body[:1] in {b"{", b"["} else "bytes"
    record: dict[str, Any] = {
        "saved": True,
        "captured_at_utc": utc_now(),
        "method": "GET",
        "operation_id": get_spec.operation_id,
        "path_template": get_spec.path_template,
        "path_resolved": before_path,
        "http_status": int(resp.status),
        "size_bytes": len(body),
        "sha256": sha256_of_bytes(body),
        "body_kind": body_kind,
        "content_type": content_type or None,
        "restore_note": "Use the saved before-state file as the source for a deliberate restore command or manual fix if you need to undo this change later.",
    }

    artifacts_dir = ctx.get("artifacts_dir")
    if not isinstance(artifacts_dir, Path):
        return record, None

    body_suffix = ".json" if body_kind == "json" else ".bin"
    snapshot_path = Path(artifacts_dir) / f"before_state_body{body_suffix}"
    snapshot_path.parent.mkdir(parents=True, exist_ok=True)
    snapshot_path.write_bytes(body)
    record["snapshot_file"] = str(snapshot_path)

    meta_path = Path(artifacts_dir) / "before_state.json"
    return record, write_json_file(meta_path, record)


def _require_saved_before_state_or_ack(*, ctx: dict, before_state: dict[str, Any] | None) -> None:
    if isinstance(before_state, dict) and bool(before_state.get("saved")):
        return
    if bool(ctx.get("ack_no_snapshot")):
        return
    reason = None
    if isinstance(before_state, dict):
        reason = str(before_state.get("reason") or "").strip() or None
    detail = f" {reason}" if reason else ""
    raise SafetyError(
        "Refused: this Cloudflare write has no saved before-state snapshot. Review the dry-run plan "
        "and pass --ack-no-snapshot only when the approved change should continue without an automatic "
        f"restore point.{detail}"
    )


def _before_state_read_target(
    *,
    idx: OperationIndex,
    method: str,
    path_template: str,
    path_params: dict[str, str],
) -> tuple[OperationSpec | None, str | None]:
    method_u = str(method).upper()
    if method_u == "GET":
        return None, None

    get_spec = idx.get_by_method_path(method="GET", path_template=path_template)
    if get_spec is not None:
        return get_spec, _resolve_path(get_spec.path_template, path_params)

    if method_u == "POST" and path_template in {
        "/accounts/{account_id}/pages/projects/{project_name}/deployments/{deployment_id}/retry",
        "/accounts/{account_id}/pages/projects/{project_name}/deployments/{deployment_id}/rollback",
    }:
        get_template = "/accounts/{account_id}/pages/projects/{project_name}/deployments/{deployment_id}"
        get_spec = idx.get_by_method_path(method="GET", path_template=get_template)
        if get_spec is not None:
            return get_spec, _resolve_path(get_spec.path_template, path_params)

    return None, None


def _requires_saved_before_state(
    *,
    idx: OperationIndex,
    method: str,
    path_template: str,
    path_params: dict[str, str],
) -> bool:
    method_u = str(method).upper()
    _ = idx, path_template, path_params
    return method_u in {"POST", "PUT", "PATCH", "DELETE"}


def cmd_openapi_list(args, ctx) -> int:
    idx = load_allowlisted_operation_index()
    contains = str(getattr(args, "contains", None) or "").strip() or None
    tag = str(getattr(args, "tag", None) or "").strip() or None
    method = str(getattr(args, "method", None) or "").strip() or None
    limit = int(getattr(args, "limit", 200) or 200)
    include_deprecated = bool(getattr(args, "include_deprecated", False))
    include_sensitive = bool(getattr(args, "include_sensitive", False))

    hits = idx.find(
        contains=contains,
        tag=tag,
        method=method,
        include_deprecated=include_deprecated,
        include_sensitive=include_sensitive,
        limit=limit,
    )
    ctx["out"].emit(
        {
            "ok": True,
            "count": len(hits),
            "operations": [
                {
                    "area": h.area,
                    "operation_id": h.operation_id,
                    "method": h.method,
                    "path_template": h.path_template,
                    "summary": h.summary,
                    "tags": h.tags,
                    "deprecated": h.deprecated,
                    "api_token_groups": h.api_token_groups,
                    "sensitivity": h.sensitivity,
                }
                for h in hits
            ],
        }
    )
    return 0


def cmd_openapi_show(args, ctx) -> int:
    idx = load_allowlisted_operation_index()
    operation_id = str(getattr(args, "operation_id", "") or "").strip()
    if not operation_id:
        raise ValidationError("Missing --operation-id")
    spec = idx.get(operation_id)
    if not spec:
        raise ValidationError(f"Operation not found in local snapshot extracts: {operation_id}")
    ctx["out"].emit(
        {
            "ok": True,
            "operation": {
                "area": spec.area,
                "operation_id": spec.operation_id,
                "method": spec.method,
                "path_template": spec.path_template,
                "summary": spec.summary,
                "tags": spec.tags,
                "deprecated": spec.deprecated,
                "api_token_groups": spec.api_token_groups,
                "sensitivity": spec.sensitivity,
            },
        }
    )
    return 0


def cmd_openapi_call(args, ctx) -> int:
    idx = load_allowlisted_operation_index()

    operation_id = str(getattr(args, "operation_id", "") or "").strip() or None
    method = str(getattr(args, "method", "") or "").strip().upper() or None
    path_template = str(getattr(args, "path", "") or "").strip() or None

    spec: OperationSpec | None = None
    if operation_id:
        spec = idx.get(operation_id)
        if not spec:
            raise ValidationError(f"Operation not found in local snapshot extracts: {operation_id}")
        method = spec.method
        path_template = spec.path_template
    else:
        if not method or not path_template:
            raise ValidationError("Provide either --operation-id OR both --method and --path.")
        spec = idx.get_by_method_path(method=method, path_template=path_template)
        if not spec:
            raise ValidationError(
                "Operation not found in the tool's local allowlist. "
                "Use `cloudflare-api-tool operations list` to find a supported operation. "
                "This tool refuses unknown endpoints (no guessing)."
            )

    assert method is not None
    assert path_template is not None

    path_params = _parse_kv_list(getattr(args, "path_param", None))
    query = _parse_kv_list(getattr(args, "query", None))

    # Convenience: default account_id from local default when needed.
    if "{account_id}" in path_template and "account_id" not in path_params:
        from ..state import get_default_account_id

        default = get_default_account_id(ctx["env_file"], fingerprint=ctx.get("env_fingerprint"))
        if default:
            path_params["account_id"] = str(default)
    if "{zone_id}" in path_template and "zone_id" not in path_params:
        # no default zone id; caller must provide it
        pass

    resolved_path = _resolve_path(path_template, path_params)

    kind, json_body, bytes_body, multipart_payload, body_meta = _load_body(
        body_json_file=str(getattr(args, "body_json_file", "") or "").strip() or None,
        body_bytes_file=str(getattr(args, "body_bytes_file", "") or "").strip() or None,
        multipart_spec_file=str(getattr(args, "multipart_spec_file", "") or "").strip() or None,
    )

    content_type = str(getattr(args, "content_type", "") or "").strip() or None
    out_path = str(getattr(args, "out", "") or "").strip() or None
    overwrite = bool(getattr(args, "overwrite", False))

    sensitivity = spec.sensitivity if spec else "none"
    read_like_non_get = is_read_like_non_get_operation(spec)
    is_account_write_op = _is_account_write_operation(method=method, path_template=path_template)

    is_state_write = (method != "GET") and (not read_like_non_get)
    wants_file_output = bool(out_path)
    risk_level = "high" if is_state_write else ("medium" if sensitivity != "none" or wants_file_output else "low")
    risk_reasons = []
    if is_state_write:
        risk_reasons.append("This is a Cloudflare API write.")
    if read_like_non_get and method != "GET":
        risk_reasons.append("This endpoint uses a non-GET read-like operation (no state changes expected).")
    if sensitivity == "sensitive_read":
        risk_reasons.append("This endpoint may return code/values/tokens; output must be written to a file.")
    if sensitivity == "sensitive_write_result":
        risk_reasons.append("This endpoint may return a secret/token (often shown once).")
    if wants_file_output and sensitivity == "none":
        risk_reasons.append("This operation writes the raw response to a local file.")
    if not risk_reasons:
        risk_reasons = ["Read-only operation."]

    selector = {
        "operation_id": spec.operation_id if spec else operation_id,
        "method": method,
        "path_template": path_template,
        "path_resolved": resolved_path,
        "tags": spec.tags if spec else None,
    }
    plan = {
        "tool": str(ctx.get("tool") or "cloudflare-api-tool"),
        "version": str(ctx.get("tool_version") or ""),
        "generated_at_utc": utc_now(),
        "env_fingerprint": str(getattr(ctx.get("cfg"), "base_url", None) or ""),
        "command": str(ctx.get("command_str") or ""),
        "selector": selector,
        "risk_level": risk_level,
        "risk_reasons": risk_reasons,
        "preconditions": [
            "API token has least-privilege permissions needed for this operation.",
            "Path params and request body (if any) are correct.",
            "For non-GET operations and file-only outputs: review the plan output before applying.",
        ],
        "request": {
            "operation_id": spec.operation_id if spec else None,
            "method": method,
            "path_template": path_template,
            "path_resolved": resolved_path,
            "query": query,
            "body_meta": body_meta,
            "content_type": content_type,
            "sensitivity": sensitivity,
            "out": out_path,
        },
        "proposed_changes": [
            {
                "resource": "openapi_operation",
                "action": "call",
                "method": method,
                "path": resolved_path,
                "operation_id": spec.operation_id if spec else None,
                "sensitivity": sensitivity,
            }
        ],
        "verification_plan": [
            "Best-effort verification: for many writes, the tool attempts a read-back GET when a matching endpoint exists in the snapshot. Otherwise it records API response success.",
        ],
        "notes": [],
    }
    before_state = None
    before_state_path = None
    requires_saved_before_state = _requires_saved_before_state(
        idx=idx,
        method=method,
        path_template=path_template,
        path_params=path_params,
    )

    # For non-sensitive GET operations, execute immediately (no --apply required), matching the tool's read-first UX.
    if method == "GET" and sensitivity == "none" and not wants_file_output and not bool(ctx.get("apply")):
        _require_token(ctx)
        res = ctx["cf"].request_json(
            method,
            resolved_path,
            params=query or None,
            headers={"content-type": content_type} if content_type else None,
            cacheable=True,
        )
        ctx["out"].emit(
            {
                "ok": True,
                "command": "operations.call",
                "operation": selector,
                "result": res.result,
                "result_info": res.result_info,
            }
        )
        return 0

    if not bool(ctx.get("apply")):
        if is_state_write:
            get_spec, before_read_path = _before_state_read_target(
                idx=idx,
                method=method,
                path_template=path_template,
                path_params=path_params,
            )
            if get_spec is not None and before_read_path:
                _require_token(ctx)
            before_state, before_state_path = _capture_before_state(
                idx=idx,
                ctx=ctx,
                spec=spec,
                method=method,
                path_template=path_template,
                resolved_path=resolved_path,
                path_params=path_params,
            )
            plan["before_state"] = before_state
            if before_state_path:
                plan["before_state_path"] = before_state_path
            if requires_saved_before_state and not bool((before_state or {}).get("saved")):
                plan["notes"].append(
                    "No saved before-state snapshot is available for this write family. Apply requires explicit --ack-no-snapshot approval."
                )
        if wants_file_output:
            plan["notes"].append("This request will write the raw response body to a local file under --project-dir.")
        _ = write_plan_if_requested(ctx, plan)
        ctx["audit"].write(
            "plan",
            {"selector": selector, "request": {k: plan["request"].get(k) for k in ["method", "path_template", "path_resolved", "operation_id", "sensitivity", "out"]}},
        )
        ctx["out"].emit({"ok": True, "dry_run": True, "command": "operations.call", "plan": plan})
        return 0

    _require_apply(ctx)
    _require_token(ctx)
    if is_state_write:
        _require_yes(ctx)
    if is_account_write_op and method == "DELETE":
        _require_ack_irreversible(ctx)
    if _requires_ack_irreversible(spec):
        _require_ack_irreversible(ctx)
    if is_account_write_op and not out_path:
        raise SafetyError("Refusing: applied /accounts write operations require file-only output. Provide --out.")
    if wants_file_output and not out_path:
        raise ValidationError("Missing --out")
    if wants_file_output and not bool(ctx.get("apply")):
        raise SafetyError("Refusing: writing an output file requires --apply.")
    if sensitivity == "sensitive_read":
        if not out_path:
            raise SafetyError("Refusing: this endpoint is a sensitive read. Provide --out.")
    if sensitivity == "sensitive_write_result":
        if not out_path:
            raise SafetyError("Refusing: this endpoint may return a secret/token. Provide --out.")
        _require_ack_irreversible(ctx)

    provided = load_plan_in(ctx)
    if provided is not None:
        require_plan_matches(expected_plan=plan, provided_plan=provided)
        before_state = provided.get("before_state") if isinstance(provided.get("before_state"), dict) else None
        before_state_path = str(provided.get("before_state_path") or "").strip() or None
    elif is_state_write:
        before_state, before_state_path = _capture_before_state(
            idx=idx,
            ctx=ctx,
            spec=spec,
            method=method,
            path_template=path_template,
            resolved_path=resolved_path,
            path_params=path_params,
        )
    if is_state_write and requires_saved_before_state:
        _require_saved_before_state_or_ack(ctx=ctx, before_state=before_state)

    headers: dict[str, str] = {}
    if content_type:
        headers["content-type"] = content_type

    response_result: Any | None = None
    wrote_file: dict[str, Any] | None = None
    changed = bool(is_state_write)

    ctx["audit"].write("apply", {"selector": selector, "method": method, "path": resolved_path})

    if wants_file_output or sensitivity in {"sensitive_read", "sensitive_write_result"}:
        safe = resolve_safe_out_path(project_dir=Path(ctx["project_dir"]), out_path=out_path or "", allow_overwrite=overwrite)
        send_json = None
        send_data = None
        send_files = None
        if kind == "json":
            send_json = json_body
        elif kind == "bytes":
            send_data = bytes_body
        elif kind == "multipart":
            mp_fields = (multipart_payload or {}).get("fields") or {}
            mp_files = (multipart_payload or {}).get("files") or {}
            send_data = mp_fields
            send_files = mp_files

        resp = ctx["cf"].request_raw(
            method,
            resolved_path,
            params=query or None,
            json_body=send_json,
            data=send_data,
            files=send_files,
            headers=headers or None,
            retries=3,
        )
        safe.abs_path.parent.mkdir(parents=True, exist_ok=True)
        safe.abs_path.write_bytes(resp.body)
        wrote_file = {
            "out_path": str(safe.abs_path),
            "out_rel": safe.rel_to_project,
            "size_bytes": len(resp.body),
            "sha256": sha256_of_bytes(resp.body),
            "http_status": int(resp.status),
        }
        if is_state_write and resp.body and len(resp.body) <= 2_000_000:
            try:
                # If it's JSON, parse for verification inference only (never printed or embedded in receipts).
                obj = json.loads(resp.body.decode("utf-8"))
                if isinstance(obj, dict) and obj.get("success") is True:
                    response_result = obj.get("result")
            except Exception:
                response_result = None
    else:
        files = None
        data = None
        if kind == "json":
            response_result = ctx["cf"].request_json(method, resolved_path, params=query or None, json_body=json_body, retries=3).result
        elif kind == "bytes":
            data = bytes_body
            response_result = ctx["cf"].request_json(method, resolved_path, params=query or None, data=data, headers=headers or None, retries=3).result
        elif kind == "multipart":
            mp_fields = (multipart_payload or {}).get("fields") or {}
            mp_files = (multipart_payload or {}).get("files") or {}
            files = mp_files
            data = mp_fields
            response_result = ctx["cf"].request_json(method, resolved_path, params=query or None, data=data, files=files, headers=headers or None, retries=3).result
        else:
            response_result = ctx["cf"].request_json(method, resolved_path, params=query or None, headers=headers or None, retries=3).result

    if sensitivity in {"sensitive_read", "sensitive_write_result"}:
        if is_state_write:
            if is_account_write_op:
                verification = _best_effort_verify_redacted(
                    idx=idx,
                    ctx=ctx,
                    spec=spec,
                    method=method,
                    path_template=path_template,
                    resolved_path=resolved_path,
                    path_params=path_params,
                    response_result=response_result,
                )
            else:
                verification = _best_effort_verify(
                    idx=idx,
                    ctx=ctx,
                    spec=spec,
                    method=method,
                    path_template=path_template,
                    resolved_path=resolved_path,
                    path_params=path_params,
                    response_result=None,
                )
                if isinstance(verification, dict):
                    verification.pop("evidence", None)
                    if "http_status" not in verification and isinstance(wrote_file, dict) and "http_status" in wrote_file:
                        verification["http_status"] = int(wrote_file["http_status"])
        else:
            # Sensitive reads (file-only output) do not embed any response bodies in receipts; verification is skipped.
            verification = {
                "ok": True,
                "method": "skipped_sensitive",
                "details": {"note": "Verification skipped: this endpoint is classified as sensitive (file-only output)."},
            }
    else:
        if is_account_write_op and is_state_write:
            verification = _best_effort_verify_redacted(
                idx=idx,
                ctx=ctx,
                spec=spec,
                method=method,
                path_template=path_template,
                resolved_path=resolved_path,
                path_params=path_params,
                response_result=response_result,
            )
        else:
            verification = _best_effort_verify(
                idx=idx,
                ctx=ctx,
                spec=spec,
                method=method,
                path_template=path_template,
                resolved_path=resolved_path,
                path_params=path_params,
                response_result=response_result,
            )

    receipt = {
        "tool": str(ctx.get("tool") or "cloudflare-api-tool"),
        "version": str(ctx.get("tool_version") or ""),
        "applied_at_utc": utc_now(),
        "env_fingerprint": str(getattr(ctx.get("cfg"), "base_url", None) or ""),
        "command": str(ctx.get("command_str") or ""),
        "selector": selector,
        "changed": bool(changed),
        "diff_applied": [
            {
                "resource": "openapi_operation",
                "action": "called",
                "method": method,
                "path": resolved_path,
                "operation_id": spec.operation_id if spec else None,
            }
        ],
        "verification": verification,
        "output_file": wrote_file,
        "notes": [],
    }
    if is_state_write:
        receipt["before_state"] = before_state
        if before_state_path:
            receipt["before_state_path"] = before_state_path
        if not bool((before_state or {}).get("saved")):
            receipt["no_snapshot_approval"] = {
                "approved": bool(ctx.get("ack_no_snapshot")),
                "reason": "No saved before-state snapshot was available for this Cloudflare write.",
            }
    _ = write_receipt_if_requested(ctx, receipt)
    ctx["audit"].write(
        "receipt",
        {
            "selector": selector,
            "changed": bool(receipt.get("changed")),
            "verification_ok": bool((receipt.get("verification") or {}).get("ok")),
            "output_file": {"out_rel": (wrote_file or {}).get("out_rel")} if wrote_file else None,
        },
    )

    out_obj: dict[str, Any] = {"ok": True, "dry_run": False, "command": "operations.call", "changed": bool(changed), "receipt": receipt}
    if sensitivity == "none" and not wants_file_output:
        out_obj["result"] = response_result
    else:
        out_obj["file"] = wrote_file
    ctx["out"].emit(out_obj)
    return 0
