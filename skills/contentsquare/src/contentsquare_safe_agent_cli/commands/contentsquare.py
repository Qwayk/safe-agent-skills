from __future__ import annotations

import hashlib
import json
import os
import shlex
import tempfile
from pathlib import Path
from typing import Any

import requests

from ..catalog import EndpointSpec
from ..contentsquare_client import ContentsquareClient, UncertainWrite, read_json_body
from ..errors import SafetyError, ValidationError


def _client(ctx: dict) -> ContentsquareClient:
    return ContentsquareClient(
        cfg=ctx["cfg"],
        timeout_s=float(ctx.get("timeout_s") or 30),
        verbose=bool(ctx.get("verbose")),
        oauth_project_id=ctx.get("oauth_project_id"),
    )


def _params(args: Any) -> dict[str, Any]:
    out: dict[str, Any] = {}
    mapping = {
        "project_id": "projectId",
        "start_date": "startDate",
        "end_date": "endDate",
        "segment_id": "segmentIds",
        "segment_ids": "segmentIds",
        "goal_id": "goalId",
        "ids": "ids",
        "state": "state",
        "order": "order",
        "format": "format",
        "frequency": "frequency",
        "scope_filter": "scope",
        "from_date": "from",
        "to_date": "to",
        "page": "page",
        "limit": "limit",
        "device": "device",
        "period": "period",
    }
    for key, api_name in mapping.items():
        value = getattr(args, key, None)
        if value is not None and value != "":
            out[api_name] = value
    return out


def _fill_path(path: str, args: Any) -> str:
    replacements = {
        "{jobId}": getattr(args, "job_id", None),
        "{runId}": getattr(args, "run_id_value", None),
        "{mappingId}": getattr(args, "mapping_id", None),
        "{pageGroupId}": getattr(args, "page_group_id", None),
        "{zoningId}": getattr(args, "zoning_id", None),
        "{zoneId}": getattr(args, "zone_id", None),
    }
    filled = path
    for marker, value in replacements.items():
        if marker in filled:
            if not value:
                raise RuntimeError(f"Missing required path value for {marker}")
            filled = filled.replace(marker, str(value))
    return filled


def _scope_for_family(spec: EndpointSpec, args: Any) -> tuple[str | None, str | None]:
    override = getattr(args, "scope", None)
    if override and "enrichment" in str(override).split() and str(override).strip() != "enrichment":
        raise ValidationError("Contentsquare enrichment OAuth scope cannot be combined with other scopes")
    if spec.family == "enrichment":
        return override or "enrichment", getattr(args, "integration_id", None)
    if spec.family == "data-export":
        return override or "data-export", None
    if spec.family == "metrics":
        return override or "metrics", None
    if spec.family == "speed-analysis":
        return override or "speed-analysis", None
    return override, None


def _fingerprint(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


def _selector(
    spec: EndpointSpec, args: Any, ctx: dict, path: str, scope: str | None, integration_id: str | None
) -> dict[str, Any]:
    cfg = ctx["cfg"]
    return {
        "command": " ".join(spec.command),
        "path": path,
        "query": _params(args),
        "oauth_project_id": ctx.get("oauth_project_id") or cfg.oauth_project_id,
        "scope": scope,
        "integration_id": integration_id,
        "auth_base_url": cfg.auth_base_url,
        "api_base_url": cfg.api_base_url,
        "connection_fingerprint": _fingerprint([cfg.client_id, cfg.client_secret]),
    }


def _approved_request(spec: EndpointSpec, selector: dict, body: dict) -> dict:
    return {
        "operation": spec.name,
        "method": spec.method,
        "path": selector["path"],
        "selector": selector,
        "proposed_changes": body,
    }


def _plan(spec: EndpointSpec, ctx: dict, request: dict) -> dict[str, Any]:
    risk = "irreversible" if "ack_irreversible" in spec.safety or "enrichment" in spec.family else "high"
    return {
        "tool": ctx.get("tool"),
        "version": ctx.get("tool_version"),
        "command": ctx.get("command_str"),
        **request,
        "request_fingerprint": _fingerprint(request),
        "risk_level": risk,
        "risk_reasons": [
            "This Contentsquare operation can change server-side state.",
            "No automatic rollback or safe before/after snapshot is documented for this operation.",
        ],
        "preconditions": [
            "The reviewer confirmed the JSON body belongs to the intended Contentsquare project or integration.",
            "The reviewer confirmed the target account and scope are correct.",
        ],
        "verification_plan": "Use the returned Contentsquare response and any provider-side IDs. Run a follow-up read command when the API exposes one.",
        "rollback": {"supported": False, "notes": "Contentsquare docs do not document a universal rollback for this operation."},
    }


def _write_json(path: str | None, obj: dict[str, Any]) -> None:
    if not path:
        return
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _load_plan(path: str | None) -> dict[str, Any]:
    if not path:
        raise SafetyError("Live write requires --plan-in from a reviewed dry-run plan")
    try:
        obj = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise SafetyError("Could not read the saved plan. Check the path or make a fresh preview.") from exc
    if not isinstance(obj, dict):
        raise SafetyError("Plan file must contain one JSON object")
    return obj


def _apply_body(plan: dict, spec: EndpointSpec, selector: dict, body: dict | None) -> dict:
    saved_body = plan.get("proposed_changes")
    if not isinstance(saved_body, dict) or "request_fingerprint" not in plan:
        raise SafetyError("This saved plan is missing the request checks. Make a fresh preview.")
    request = _approved_request(spec, selector, saved_body if body is None else body)
    saved_request = {key: plan.get(key) for key in request}
    if _fingerprint(request) != plan["request_fingerprint"] or request != saved_request:
        raise SafetyError("The request or Contentsquare connection changed. Make a fresh preview.")
    return saved_body


def _provider_payload(result: Any) -> Any:
    return result.get("payload", result) if isinstance(result, dict) else result


def _provider_rejected(result: Any) -> bool:
    return isinstance(result, dict) and result.get("success") is False


def _run_files(run: Any) -> list[dict[str, Any]]:
    source = _provider_payload(run)
    files = source.get("files") if isinstance(source, dict) else None
    if not isinstance(files, list):
        return []
    return [item for item in files if isinstance(item, dict)]


def _select_run_file(files: list[dict[str, Any]], *, file_index: int | None, part_id: str | None) -> dict[str, Any]:
    if not files:
        raise RuntimeError("Run response did not include any documented files[].url values")
    if file_index is not None and part_id is not None:
        raise ValidationError("Choose either --file-index or --part-id, not both")
    if part_id is not None:
        matches = [item for item in files if str(item.get("partId")) == str(part_id)]
        if not matches:
            raise ValidationError(f"No run file matched partId {part_id}")
        if len(matches) > 1:
            raise ValidationError(f"More than one run file matched partId {part_id}; use --file-index")
        selected = matches[0]
    elif file_index is not None:
        if file_index < 0 or file_index >= len(files):
            raise ValidationError(f"--file-index must be between 0 and {len(files) - 1}")
        selected = files[file_index]
    elif len(files) == 1:
        selected = files[0]
    else:
        raise SafetyError("Run has multiple files; pass --file-index or --part-id so the tool does not guess")
    if not isinstance(selected.get("url"), str) or not selected["url"]:
        raise RuntimeError("Selected run file did not include a documented files[].url value")
    return selected


def _follow_up(args: Any, ctx: dict, *command: str) -> str:
    parts = ["contentsquare-safe-cli"]
    for flag, value in (
        ("--env-file", ctx.get("env_file")),
        ("--oauth-project-id", ctx.get("oauth_project_id")),
    ):
        if value:
            parts.extend((flag, value))
    parts.extend(command)
    if scope := getattr(args, "scope", None):
        parts.extend(("--scope", scope))
    return shlex.join(parts)


def _run_summary(run: Any) -> dict[str, Any]:
    payload = _provider_payload(run)
    state = payload.get("state") if isinstance(payload, dict) else None
    return {
        "state": state,
        "ready_to_download": (
            any(isinstance(item.get("url"), str) and item["url"] for item in _run_files(run))
        ),
    }


def cmd_endpoint(args: Any, ctx: dict) -> int:
    spec: EndpointSpec = args.endpoint_spec
    path = _fill_path(spec.path, args)
    body_file = getattr(args, "body_json", None)
    body = read_json_body(body_file)
    scope, integration_id = _scope_for_family(spec, args)
    write = spec.safety.startswith("plan_apply")

    if write:
        selector = _selector(spec, args, ctx, path, scope, integration_id)
        if not bool(ctx.get("apply")):
            plan = _plan(spec, ctx, _approved_request(spec, selector, body))
            _write_json(ctx.get("plan_out"), plan)
            ctx["out"].emit(
                {
                    "ok": True,
                    "dry_run": True,
                    "changed": False,
                    "verified": None,
                    "operation": spec.name,
                    "plan": plan,
                    "plan_path": ctx.get("plan_out"),
                    "message": "Dry run only. Review the plan, then apply with --plan-in --apply --yes.",
                }
            )
            return 0
        if not bool(ctx.get("yes")):
            raise SafetyError("Live write requires --apply --yes")
        if "ack_irreversible" in spec.safety and not bool(ctx.get("ack_irreversible")):
            raise SafetyError("This delete has no documented rollback; pass --ack-irreversible after review")
        if "no_snapshot" in spec.safety and not bool(ctx.get("ack_no_snapshot")):
            raise SafetyError("This write has no safe provider snapshot; pass --ack-no-snapshot after review")
        plan = _load_plan(ctx.get("plan_in"))
        body = _apply_body(plan, spec, selector, body if body_file else None)

    try:
        result = _client(ctx).request(
            spec.method,
            path,
            params=_params(args),
            body=body,
            scope=scope,
            integration_id=integration_id,
            write=write,
        )
        problem = None
    except UncertainWrite as exc:
        result = None
        problem = str(exc)

    rejected = _provider_rejected(result)
    response = _provider_payload(result)
    follow_up = None
    if spec.name == "create-export-job" and not rejected:
        job_id = response.get("jobId") if isinstance(response, dict) else None
        if isinstance(job_id, (int, str)) and job_id:
            follow_up = _follow_up(args, ctx, "data-export", "list-runs", "--job-id", str(job_id))
        else:
            problem = problem or "Contentsquare did not return an export job ID."
            follow_up = _follow_up(args, ctx, "data-export", "list-jobs")
    if problem:
        message = f"{problem} Check Contentsquare before trying again."
    elif rejected:
        message = "Contentsquare reported that the request failed."
    else:
        message = None
    payload = {
        "ok": not (rejected or problem),
        "operation": spec.name,
        "method": spec.method,
        "path": path,
        "dry_run": False,
        "changed": None if problem else write and not rejected,
        "verified": None if write and not rejected else not rejected,
        "result": result,
    }
    if message:
        payload["error"] = message
    if follow_up:
        payload["follow_up"] = follow_up
    if spec.name == "get-job-run" and not rejected:
        payload["export_run"] = _run_summary(result)
    if write:
        receipt = {
            "tool": ctx.get("tool"),
            "version": ctx.get("tool_version"),
            "command": ctx.get("command_str"),
            "operation": spec.name,
            "changed": payload["changed"],
            "outcome": "uncertain" if problem else "rejected" if rejected else "accepted",
            "verification": {
                "ok": payload["verified"],
                "details": message or "Contentsquare replied. Check the result separately before calling it complete.",
            },
            "response": result,
            "rollback_plan": None,
        }
        if follow_up:
            receipt["follow_up"] = follow_up
        payload["receipt"] = receipt
        _write_json(ctx.get("receipt_out"), receipt)
        payload["receipt_path"] = ctx.get("receipt_out")
    ctx["out"].emit(payload)
    return 0 if payload["ok"] else 1


def _save_download(url: str, out_path: Path, timeout: float, overwrite: bool) -> int:
    staged_path = None
    try:
        with requests.get(url, timeout=timeout, stream=True) as reply:
            if reply.status_code != 200:
                raise RuntimeError(f"Export download failed with HTTP {reply.status_code}.")
            mime = reply.headers.get("Content-Type", "").partition(";")[0].lower()
            if mime in {"text/html", "text/xml", "application/xml", "application/problem+json"}:
                raise RuntimeError("Contentsquare returned an error page instead of an export file.")
            with tempfile.NamedTemporaryFile(dir=out_path.parent, delete=False) as staged:
                staged_path = Path(staged.name)
                count = 0
                for chunk in reply.iter_content(chunk_size=1024 * 1024):
                    if not count and chunk.lstrip().lower().startswith((b"<html", b"<!doctype html", b"<?xml")):
                        raise RuntimeError("Contentsquare returned an error page instead of an export file.")
                    staged.write(chunk)
                    count += len(chunk)
            length = reply.headers.get("Content-Length", "")
            encoding = reply.headers.get("Content-Encoding", "").lower()
            if not count or (length.isdecimal() and encoding in {"", "identity"} and count != int(length)):
                raise RuntimeError("The export download was empty or incomplete.")
        if overwrite:
            staged_path.replace(out_path)
        else:
            try:
                os.link(staged_path, out_path)
            except FileExistsError as exc:
                raise SafetyError("Output file already exists; pass --overwrite to replace it.") from exc
        return count
    except requests.RequestException as exc:
        raise RuntimeError("The export download was interrupted. Check the run before trying again.") from exc
    finally:
        if staged_path is not None:
            staged_path.unlink(missing_ok=True)


def cmd_download_run_file(args: Any, ctx: dict) -> int:
    run = _client(ctx).request(
        "GET",
        f"/v1/exports/{args.job_id}/runs/{args.run_id_value}",
        params={},
        body={},
        scope=getattr(args, "scope", None) or "data-export",
    )
    if _provider_rejected(run):
        raise RuntimeError("Contentsquare rejected the export run lookup.")
    selected_file = _select_run_file(
        _run_files(run),
        file_index=getattr(args, "file_index", None),
        part_id=getattr(args, "part_id", None),
    )
    url = selected_file["url"]
    out_path = Path(args.output_file)
    if out_path.exists() and not args.overwrite:
        raise SafetyError("Output file already exists; pass --overwrite to replace it")
    if out_path.is_dir():
        raise SafetyError("Output path must be a file, not a directory")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    count = _save_download(url, out_path, float(ctx.get("timeout_s") or 30), args.overwrite)
    ctx["out"].emit(
        {
            "ok": True,
            "operation": "download-run-file",
            "changed": True,
            "verified": True,
            "output_file": str(out_path),
            "bytes_written": count,
            "file": {
                "file_index": getattr(args, "file_index", None),
                "part_id": selected_file.get("partId"),
                "expiration_date": selected_file.get("expirationDate"),
            },
        }
    )
    return 0
