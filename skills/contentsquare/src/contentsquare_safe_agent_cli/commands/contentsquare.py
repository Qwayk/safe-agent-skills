from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ..catalog import EndpointSpec
from ..contentsquare_client import ContentsquareClient, read_json_body
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


def _plan(spec: EndpointSpec, args: Any, ctx: dict, body: dict[str, Any]) -> dict[str, Any]:
    selector = {
        "command": " ".join(spec.command),
        "path": spec.path,
        "body_keys": sorted(body.keys()),
    }
    risk = "irreversible" if "ack_irreversible" in spec.safety or "enrichment" in spec.family else "high"
    return {
        "tool": ctx.get("tool"),
        "version": ctx.get("tool_version"),
        "command": ctx.get("command_str"),
        "operation": spec.name,
        "method": spec.method,
        "path": spec.path,
        "selector": selector,
        "risk_level": risk,
        "risk_reasons": [
            "This Contentsquare operation can change server-side state.",
            "No automatic rollback or safe before/after snapshot is documented for this operation.",
        ],
        "preconditions": [
            "The reviewer confirmed the JSON body belongs to the intended Contentsquare project or integration.",
            "The reviewer confirmed the target account and scope are correct.",
        ],
        "proposed_changes": body,
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
    obj = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(obj, dict):
        raise SafetyError("Plan file must contain one JSON object")
    return obj


def _run_files(run: Any) -> list[dict[str, Any]]:
    payload = run.get("payload") if isinstance(run, dict) else None
    source = payload if isinstance(payload, dict) else run
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


def cmd_endpoint(args: Any, ctx: dict) -> int:
    spec: EndpointSpec = args.endpoint_spec
    path = _fill_path(spec.path, args)
    body = read_json_body(getattr(args, "body_json", None))
    scope, integration_id = _scope_for_family(spec, args)

    if spec.safety.startswith("plan_apply"):
        if not bool(ctx.get("apply")):
            plan = _plan(spec, args, ctx, body)
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
        body = plan.get("proposed_changes") if isinstance(plan.get("proposed_changes"), dict) else body

    result = _client(ctx).request(
        spec.method,
        path,
        params=_params(args),
        body=body,
        scope=scope,
        integration_id=integration_id,
    )
    payload = {
        "ok": True,
        "operation": spec.name,
        "method": spec.method,
        "path": path,
        "dry_run": False,
        "changed": spec.safety.startswith("plan_apply"),
        "verified": None if spec.safety.startswith("plan_apply") else True,
        "result": result,
    }
    if spec.safety.startswith("plan_apply"):
        receipt = {
            "tool": ctx.get("tool"),
            "version": ctx.get("tool_version"),
            "command": ctx.get("command_str"),
            "operation": spec.name,
            "changed": True,
            "verification": {"ok": None, "details": "No safe universal read-back is documented for this operation."},
            "response": result,
            "rollback_plan": None,
        }
        payload["receipt"] = receipt
        _write_json(ctx.get("receipt_out"), receipt)
        payload["receipt_path"] = ctx.get("receipt_out")
    ctx["out"].emit(payload)
    return 0


def cmd_download_run_file(args: Any, ctx: dict) -> int:
    run = _client(ctx).request(
        "GET",
        f"/v1/exports/{args.job_id}/runs/{args.run_id_value}",
        params={},
        body={},
        scope=getattr(args, "scope", None) or "data-export",
    )
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
    import requests

    resp = requests.get(url, timeout=float(ctx.get("timeout_s") or 30))
    if resp.status_code >= 400:
        raise RuntimeError(f"Download failed with HTTP {resp.status_code}")
    out_path.write_bytes(resp.content)
    ctx["out"].emit(
        {
            "ok": True,
            "operation": "download-run-file",
            "changed": True,
            "verified": out_path.exists(),
            "output_file": str(out_path),
            "bytes_written": len(resp.content),
            "file": {
                "file_index": getattr(args, "file_index", None),
                "part_id": selected_file.get("partId"),
                "expiration_date": selected_file.get("expirationDate"),
            },
        }
    )
    return 0
