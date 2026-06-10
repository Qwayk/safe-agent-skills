from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ..errors import SafetyError, ToolError, ValidationError
from ..json_files import read_json_file
from ..openapi_index import OperationIndex, is_read_like_non_get_operation, load_allowlisted_operation_index
from ..plan_and_receipt import (
    load_plan_in,
    require_plan_matches,
    resolve_safe_out_path,
    sha256_of_bytes,
    utc_now,
    write_plan_if_requested,
    write_receipt_if_requested,
)


@dataclass(frozen=True)
class JobRow:
    operation_id: str | None
    method: str | None
    path_template: str | None
    path_params: dict[str, str]
    query: dict[str, str]
    body_json_file: str | None
    body_bytes_file: str | None
    multipart_spec_file: str | None
    content_type: str | None
    out: str | None
    overwrite: bool


def _require_token(ctx: dict) -> None:
    cfg = ctx.get("cfg")
    token = getattr(cfg, "token", None) if cfg else None
    if not token:
        raise ValidationError("Missing CLOUDFLARE_API_TOKEN")


def _require_apply(ctx: dict) -> None:
    if not bool(ctx.get("apply")):
        raise SafetyError("Refusing to apply: jobs are dry-run by default (pass --apply).")


def _require_yes(ctx: dict) -> None:
    if not bool(ctx.get("yes")):
        raise SafetyError("Refusing to apply: Cloudflare API writes require --yes.")


def _require_ack_irreversible(ctx: dict) -> None:
    if not bool(ctx.get("ack_irreversible")):
        raise SafetyError("Refusing: at least one job step can return or create a secret/token and requires --ack-irreversible.")


def _require_ack_no_snapshot(ctx: dict) -> None:
    if not bool(ctx.get("ack_no_snapshot")):
        raise SafetyError(
            "Refused: this Cloudflare jobs batch has write rows without saved per-row before-state snapshots. "
            "Review the dry-run plan and pass --ack-no-snapshot only when the approved batch should continue "
            "without automatic restore points."
        )


def _resolve_path(path_template: str, path_params: dict[str, str]) -> str:
    resolved = str(path_template)
    for k, v in path_params.items():
        resolved = resolved.replace("{" + str(k) + "}", str(v))
    if "{" in resolved or "}" in resolved:
        raise ValidationError(f"Missing path params for template: {path_template!r} (got: {sorted(path_params.keys())})")
    return resolved


def _parse_json_obj(s: str, *, field: str) -> dict[str, str]:
    raw = str(s or "").strip()
    if not raw:
        return {}
    try:
        obj = json.loads(raw)
    except Exception as e:  # noqa: BLE001
        raise ValidationError(f"Invalid JSON in {field}: {type(e).__name__}: {e}") from None
    if not isinstance(obj, dict):
        raise ValidationError(f"{field} must be a JSON object")
    out: dict[str, str] = {}
    for k, v in obj.items():
        out[str(k)] = str(v)
    return out


def _load_rows(csv_path: Path) -> list[JobRow]:
    if not csv_path.exists():
        raise ValidationError(f"Jobs file not found: {csv_path}")
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows: list[JobRow] = []
        for i, r in enumerate(reader, start=2):
            if not isinstance(r, dict):
                continue
            operation_id = str((r.get("operation_id") or "").strip()) or None
            method = str((r.get("method") or "").strip()).upper() or None
            path = str((r.get("path") or "").strip()) or None
            path_params = _parse_json_obj(str(r.get("path_params_json") or ""), field=f"path_params_json (line {i})")
            query = _parse_json_obj(str(r.get("query_json") or ""), field=f"query_json (line {i})")
            body_json_file = str((r.get("body_json_file") or "").strip()) or None
            body_bytes_file = str((r.get("body_bytes_file") or "").strip()) or None
            multipart_spec_file = str((r.get("multipart_spec_file") or "").strip()) or None
            content_type = str((r.get("content_type") or "").strip()) or None
            out = str((r.get("out") or "").strip()) or None
            overwrite = str((r.get("overwrite") or "").strip()).lower() in {"1", "true", "yes", "y"}

            # Skip blank rows.
            if not operation_id and not (method and path):
                continue

            rows.append(
                JobRow(
                    operation_id=operation_id,
                    method=method,
                    path_template=path,
                    path_params=path_params,
                    query=query,
                    body_json_file=body_json_file,
                    body_bytes_file=body_bytes_file,
                    multipart_spec_file=multipart_spec_file,
                    content_type=content_type,
                    out=out,
                    overwrite=overwrite,
                )
            )
    return rows


def _body_meta_for_row(row: JobRow) -> dict[str, Any]:
    picked = [bool(row.body_json_file), bool(row.body_bytes_file), bool(row.multipart_spec_file)]
    if sum(1 for x in picked if x) > 1:
        raise ValidationError("Row body inputs are mutually exclusive: choose only one of body_json_file/body_bytes_file/multipart_spec_file")
    if row.body_json_file:
        obj = read_json_file(row.body_json_file)
        raw = json.dumps(obj, ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode("utf-8")
        return {"body_kind": "json", "sha256": sha256_of_bytes(raw), "size_bytes": len(raw), "source": row.body_json_file}
    if row.body_bytes_file:
        p = Path(row.body_bytes_file)
        if not p.exists():
            raise ValidationError(f"Body file not found: {p}")
        data = p.read_bytes()
        return {"body_kind": "bytes", "sha256": sha256_of_bytes(data), "size_bytes": len(data), "source": row.body_bytes_file}
    if row.multipart_spec_file:
        spec = read_json_file(row.multipart_spec_file)
        if not isinstance(spec, dict):
            raise ValidationError("Multipart spec must be a JSON object.")
        fields = spec.get("fields") or {}
        files = spec.get("files") or []
        if fields and not isinstance(fields, dict):
            raise ValidationError("Multipart spec 'fields' must be an object.")
        if not isinstance(files, list):
            raise ValidationError("Multipart spec 'files' must be a list.")
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
        return {"body_kind": "multipart", "fields_keys": sorted([str(k) for k in (fields or {}).keys()]), "files": meta_files, "source": row.multipart_spec_file}
    return {"body_kind": "none"}


def _lookup_spec(idx: OperationIndex, row: JobRow) -> tuple[str, str, str, OperationSpec | None]:
    if row.operation_id:
        spec = idx.get(row.operation_id)
        if not spec:
            raise ValidationError(f"Operation not found in the tool's local index: {row.operation_id}")
        method = spec.method
        path_template = spec.path_template
        resolved_path = _resolve_path(path_template, row.path_params)
        return method, path_template, resolved_path, spec
    if not row.method or not row.path_template:
        raise ValidationError("Job row must include operation_id OR method+path.")
    method = row.method
    path_template = row.path_template
    resolved_path = _resolve_path(path_template, row.path_params)
    spec = idx.get_by_method_path(method=method, path_template=path_template)
    if not spec:
        raise ValidationError(
            "Operation not found in the tool's local allowlist. "
            "Use `cloudflare-api-tool operations list` to find a supported operation. "
            "This tool refuses unknown endpoints (no guessing)."
        )
    return method, path_template, resolved_path, spec


def cmd_jobs_run(args, ctx) -> int:
    idx = load_allowlisted_operation_index()
    csv_path = Path(str(getattr(args, "file", "") or "").strip())
    if not str(csv_path):
        raise ValidationError("Missing --file")
    rows = _load_rows(csv_path)
    if not rows:
        raise ValidationError("No job rows found (file is empty or missing required columns).")

    include_results = bool(getattr(args, "include_results", False))

    steps: list[dict[str, Any]] = []
    any_write = False
    any_sensitive = False
    any_sensitive_write_result = False
    for row in rows:
        method, path_template, resolved_path, spec = _lookup_spec(idx, row)
        sensitivity = spec.sensitivity if spec else "none"
        read_like_non_get = is_read_like_non_get_operation(spec)
        is_state_write = (method != "GET") and (not read_like_non_get)
        any_write = any_write or is_state_write
        any_sensitive = any_sensitive or (sensitivity != "none")
        any_sensitive_write_result = any_sensitive_write_result or (sensitivity == "sensitive_write_result")
        steps.append(
            {
                "operation_id": row.operation_id or (spec.operation_id if spec else None),
                "method": method,
                "path_template": path_template,
                "path_resolved": resolved_path,
                "tags": spec.tags if spec else None,
                "sensitivity": sensitivity,
                "query": row.query,
                "body_meta": _body_meta_for_row(row),
                "content_type": row.content_type,
                "out": row.out,
                "overwrite": bool(row.overwrite),
            }
        )

    selector = {"file": str(csv_path), "steps": len(steps)}
    plan = {
        "tool": str(ctx.get("tool") or "cloudflare-api-tool"),
        "version": str(ctx.get("tool_version") or ""),
        "generated_at_utc": utc_now(),
        "env_fingerprint": str(getattr(ctx.get("cfg"), "base_url", None) or ""),
        "command": str(ctx.get("command_str") or ""),
        "selector": selector,
        "risk_level": "high" if any_write else ("medium" if any_sensitive else "low"),
        "risk_reasons": (
            ["Batch includes Cloudflare API writes."] if any_write else (["Batch includes sensitive reads/outputs."] if any_sensitive else ["Read-only batch."])
        ),
        "preconditions": [
            "API token has least-privilege permissions needed for all steps.",
            "Review this plan before applying.",
            "For sensitive outputs: ensure each step has an 'out' file path under --project-dir.",
        ],
        "steps": steps,
        "verification_plan": [
            "Best-effort verification per step: when a matching GET exists, attempt read-back; otherwise record API response success.",
        ],
        "notes": [],
    }
    if any_write:
        plan["before_state"] = {
            "required": True,
            "supported": False,
            "status": "no_snapshot_available",
            "reason": "Cloudflare jobs.run is a mixed batch runner and does not save per-row before-state snapshots.",
        }
        plan["notes"].append("Write rows have no saved per-row before-state snapshot. Apply requires explicit --ack-no-snapshot approval.")

    if not bool(ctx.get("apply")):
        _ = write_plan_if_requested(ctx, plan)
        ctx["audit"].write("plan", {"selector": selector, "steps": len(steps), "any_write": any_write, "any_sensitive": any_sensitive})
        ctx["out"].emit({"ok": True, "dry_run": True, "command": "jobs.run", "plan": plan})
        return 0

    _require_apply(ctx)
    _require_token(ctx)
    if any_write:
        _require_yes(ctx)
        _require_ack_no_snapshot(ctx)
    if any_sensitive_write_result:
        _require_ack_irreversible(ctx)

    provided = load_plan_in(ctx)
    if provided is not None:
        require_plan_matches(expected_plan=plan, provided_plan=provided)

    # Preflight: fail fast on safety/output constraints before making any API calls.
    for i, row in enumerate(rows):
        method, path_template, resolved_path, spec = _lookup_spec(idx, row)
        _ = method, path_template, resolved_path
        sensitivity = spec.sensitivity if spec else "none"
        if sensitivity != "none":
            if not row.out:
                raise SafetyError(f"Missing out for sensitive step index={i}. Provide an 'out' column value under --project-dir.")
            _ = resolve_safe_out_path(
                project_dir=Path(ctx["project_dir"]),
                out_path=row.out,
                allow_overwrite=bool(row.overwrite),
            )

    receipts: list[dict[str, Any]] = []
    changed_any = False
    for i, row in enumerate(rows):
        method, path_template, resolved_path, spec = _lookup_spec(idx, row)
        sensitivity = spec.sensitivity if spec else "none"
        read_like_non_get = is_read_like_non_get_operation(spec)
        is_state_write = (method != "GET") and (not read_like_non_get)
        changed_any = changed_any or is_state_write

        headers: dict[str, str] = {}
        if row.content_type:
            headers["content-type"] = row.content_type

        step_selector = {
            "index": i,
            "operation_id": row.operation_id or (spec.operation_id if spec else None),
            "method": method,
            "path_template": path_template,
            "path_resolved": resolved_path,
            "tags": spec.tags if spec else None,
            "sensitivity": sensitivity,
        }
        ctx["audit"].write("apply", {"selector": step_selector})

        wrote_file: dict[str, Any] | None = None
        result: Any | None = None
        try:
            if sensitivity != "none":
                safe = resolve_safe_out_path(
                    project_dir=Path(ctx["project_dir"]),
                    out_path=row.out or "",
                    allow_overwrite=bool(row.overwrite),
                )
                send_json = None
                send_data = None
                send_files = None
                if row.body_json_file:
                    send_json = read_json_file(row.body_json_file)
                elif row.body_bytes_file:
                    send_data = Path(row.body_bytes_file).read_bytes()
                elif row.multipart_spec_file:
                    spec_obj = read_json_file(row.multipart_spec_file)
                    if not isinstance(spec_obj, dict):
                        raise ValidationError("Multipart spec must be a JSON object.")
                    fields = spec_obj.get("fields") or {}
                    files = spec_obj.get("files") or []
                    if fields and not isinstance(fields, dict):
                        raise ValidationError("Multipart spec 'fields' must be an object.")
                    if not isinstance(files, list):
                        raise ValidationError("Multipart spec 'files' must be a list.")
                    req_files: dict[str, Any] = {}
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
                        req_files[name] = (filename, data, content_type) if content_type else (filename, data)
                    send_data = fields
                    send_files = req_files

                resp = ctx["cf"].request_raw(
                    method,
                    resolved_path,
                    params=row.query or None,
                    json_body=send_json,
                    data=send_data,
                    files=send_files,
                    headers=headers or None,
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
            else:
                # Non-sensitive: allow JSON response.
                if row.body_json_file:
                    body = read_json_file(row.body_json_file)
                    result = ctx["cf"].request_json(
                        method,
                        resolved_path,
                        params=row.query or None,
                        json_body=body,
                        headers=headers or None,
                    ).result
                elif row.body_bytes_file:
                    data = Path(row.body_bytes_file).read_bytes()
                    result = ctx["cf"].request_json(
                        method,
                        resolved_path,
                        params=row.query or None,
                        data=data,
                        headers=headers or None,
                    ).result
                elif row.multipart_spec_file:
                    spec_obj = read_json_file(row.multipart_spec_file)
                    if not isinstance(spec_obj, dict):
                        raise ValidationError("Multipart spec must be a JSON object.")
                    fields = spec_obj.get("fields") or {}
                    files = spec_obj.get("files") or []
                    if fields and not isinstance(fields, dict):
                        raise ValidationError("Multipart spec 'fields' must be an object.")
                    if not isinstance(files, list):
                        raise ValidationError("Multipart spec 'files' must be a list.")
                    req_files: dict[str, Any] = {}
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
                        req_files[name] = (filename, data, content_type) if content_type else (filename, data)
                    result = ctx["cf"].request_json(
                        method,
                        resolved_path,
                        params=row.query or None,
                        data=fields,
                        files=req_files,
                        headers=headers or None,
                    ).result
                else:
                    result = ctx["cf"].request_json(method, resolved_path, params=row.query or None, headers=headers or None).result
        except (ValidationError, ToolError) as e:
            ctx["out"].emit(
                {
                    "ok": False,
                    "dry_run": False,
                    "command": "jobs.run",
                    "error_type": type(e).__name__,
                    "error": str(e),
                    "failed_step": step_selector,
                    "steps_completed": len(receipts),
                    "receipt": {
                        "selector": selector,
                        "applied_at_utc": utc_now(),
                        "changed": bool(changed_any),
                        "steps_completed": len(receipts),
                        "steps_total": len(steps),
                        "steps": receipts,
                    },
                }
            )
            return 1

        # Best-effort verification: same-path GET if present.
        verification: dict[str, Any] = {"ok": True, "method": "api_response_success", "details": {}}
        if method in {"PUT", "PATCH", "DELETE"} and idx.get_by_method_path(method="GET", path_template=path_template):
            resp = ctx["cf"].request_raw_allow_errors("GET", resolved_path)
            if method == "DELETE":
                verification = {"ok": resp.status >= 400, "method": "read_back_get_same_path_expected_missing", "http_status": int(resp.status), "details": {}}
            else:
                verification = {"ok": resp.status < 400, "method": "read_back_get_same_path", "http_status": int(resp.status), "details": {}}

        step_receipt = {
            "selector": step_selector,
            "changed": bool(is_state_write),
            "output_file": wrote_file,
            "verification": verification,
        }
        if is_state_write:
            step_receipt["before_state"] = {
                "required": True,
                "supported": False,
                "status": "no_snapshot_available",
                "reason": "Cloudflare jobs.run does not save per-row before-state snapshots.",
            }
            step_receipt["no_snapshot_approval"] = {
                "approved": bool(ctx.get("ack_no_snapshot")),
                "reason": "No saved per-row before-state snapshot was available for this Cloudflare jobs step.",
            }
        if include_results and sensitivity == "none":
            step_receipt["result"] = result
        receipts.append(step_receipt)

    receipt = {
        "tool": str(ctx.get("tool") or "cloudflare-api-tool"),
        "version": str(ctx.get("tool_version") or ""),
        "applied_at_utc": utc_now(),
        "env_fingerprint": str(getattr(ctx.get("cfg"), "base_url", None) or ""),
        "command": str(ctx.get("command_str") or ""),
        "selector": selector,
        "changed": bool(changed_any),
        "steps_total": len(steps),
        "steps": receipts,
        "notes": [],
    }
    if any_write:
        receipt["before_state"] = {
            "required": True,
            "supported": False,
            "status": "no_snapshot_available",
            "reason": "Cloudflare jobs.run is a mixed batch runner and does not save per-row before-state snapshots.",
        }
        receipt["no_snapshot_approval"] = {
            "approved": bool(ctx.get("ack_no_snapshot")),
            "reason": "No saved per-row before-state snapshots were available for this Cloudflare jobs batch.",
        }
    _ = write_receipt_if_requested(ctx, receipt)
    ctx["audit"].write("receipt", {"selector": selector, "changed": bool(changed_any), "steps": len(receipts)})
    ctx["out"].emit({"ok": True, "dry_run": False, "command": "jobs.run", "changed": bool(changed_any), "receipt": receipt})
    return 0
