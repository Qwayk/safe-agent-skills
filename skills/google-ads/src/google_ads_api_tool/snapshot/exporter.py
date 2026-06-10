from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any, Callable, Iterator

from ..errors import NotFound, SafetyError, ValidationError
from ..google_ads_client import build_google_ads_client, protobuf_to_dict
from ..json_files import write_json_file
from ..presets.loader import PresetLoader
from ..presets.validate import validate_preset_dict
from ..secrets import redact_secrets
from .creative_anatomy import write_creative_anatomy_table
from .manifest import GroupResult, TableResult, build_manifest
from .pack_writer import PackWriter


_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


@dataclass(frozen=True)
class ExportArgs:
    preset: str
    customer_id: str
    since: str
    until: str
    out_dir: Path
    overwrite: bool
    strict: bool
    segmentation: str
    page_size: int
    max_rows: int | None
    include_optional: bool = False


def _render(template: str, *, customer_id: str, since: str, until: str) -> str:
    return template.format(customer_id=customer_id, since=since, until=until)


def _validate_export_args(a: ExportArgs) -> None:
    if not a.preset.strip():
        raise ValidationError("Missing --preset")
    if not a.customer_id.strip():
        raise ValidationError("Missing --customer-id")
    if not a.customer_id.isdigit():
        raise ValidationError("--customer-id must be digits")
    if not _DATE_RE.match(a.since):
        raise ValidationError("--since must be YYYY-MM-DD")
    if not _DATE_RE.match(a.until):
        raise ValidationError("--until must be YYYY-MM-DD")
    if not str(a.segmentation or "").strip():
        raise ValidationError("--segmentation must be a non-empty string")
    if a.page_size <= 0:
        raise ValidationError("--page-size must be > 0")
    if a.max_rows is not None and a.max_rows <= 0:
        raise ValidationError("--max-rows must be > 0 if provided")


def build_export_plan(*, a: ExportArgs, preset_obj: dict[str, Any]) -> dict[str, Any]:
    groups = preset_obj.get("query_groups") or []
    plan_groups: list[dict[str, Any]] = []
    for g in groups:
        required = bool((g or {}).get("required"))
        if (not required) and (not a.include_optional):
            continue
        templates = (g or {}).get("gaql_templates") or {}
        variant = a.segmentation if a.segmentation in templates else "base"
        rendered = _render(str(templates.get(variant) or ""), customer_id=a.customer_id, since=a.since, until=a.until)
        plan_groups.append(
            {
                "group_id": g.get("group_id"),
                "required": required,
                "requires_date_range": bool((g or {}).get("requires_date_range", True)),
                "output": f"tables/{g.get('output')}",
                "join_keys": list(g.get("join_keys") or []),
                "template_variant": variant,
                "query": rendered,
            }
        )

    return {
        "tool": "google-ads-api-tool",
        "command": "snapshot export",
        "dry_run": True,
        "preset": preset_obj.get("name"),
        "customer_id": a.customer_id,
        "since": a.since,
        "until": a.until,
        "segmentation": a.segmentation,
        "include_optional": bool(a.include_optional),
        "out_dir": str(a.out_dir),
        "overwrite": bool(a.overwrite),
        "strict": bool(a.strict),
        "page_size": a.page_size,
        "max_rows": a.max_rows,
        "pack_layout": {
            "manifest": "manifest.json",
            "tables_dir": "tables/",
            "queries": "queries/queries.json",
            "errors": "errors/errors.jsonl",
        },
        "groups": plan_groups,
        "safety_gates": {"apply_required": True, "yes_required": True},
    }


def _iter_rows(it: Iterator[Any]) -> Iterator[dict[str, Any]]:
    for r in it:
        yield protobuf_to_dict(r)


def run_snapshot_export(
    *,
    a: ExportArgs,
    apply: bool,
    yes: bool,
    strict: bool,
    tool_version: str,
    env_file: str,
    timeout_s_override: float | None,
    plan_out: str | None,
    receipt_out: str | None,
    artifacts_dir: Path | None,
    audit_write: Callable[[str, dict[str, Any]], None],
    secret_values: list[str] | None,
) -> tuple[int, dict[str, Any]]:
    _validate_export_args(a)
    loader = PresetLoader()
    try:
        preset_obj = loader.load_preset(a.preset)
    except NotFound as e:
        return 1, {"ok": False, "error": str(e), "error_type": "NotFound"}

    vres = validate_preset_dict(preset_obj, source=f"{a.preset}.json")
    if not vres.ok:
        return 1, {
            "ok": False,
            "error": "Preset validation failed",
            "error_type": "ValidationError",
            "details": list(vres.errors),
        }

    plan = build_export_plan(a=a, preset_obj=preset_obj)
    if plan_out:
        write_json_file(plan_out, plan)
    if artifacts_dir:
        write_json_file(artifacts_dir / "plan.json", plan)

    if not apply:
        audit_write("snapshot_export_plan", {"ok": True, "dry_run": True, "preset": a.preset})
        return 0, {
            "ok": True,
            "dry_run": True,
            "preset": a.preset,
            "out_dir": str(a.out_dir),
            "plan_written": bool(plan_out or artifacts_dir),
        }

    if not yes:
        raise SafetyError("Snapshot export is a batch action; pass --yes to proceed.")

    # Load config only when we actually need to call the API.
    from ..config import load_config  # local import to keep dry-run independent of secrets

    cfg = load_config(env_file)
    if timeout_s_override is not None:
        cfg = replace(cfg, timeout_s=timeout_s_override)
    secrets = list(secret_values or cfg.secret_values())

    writer = PackWriter(out_dir=a.out_dir, overwrite=a.overwrite)
    writer.create_layout()

    groups_spec_all = list(preset_obj.get("query_groups") or [])
    groups_spec: list[dict[str, Any]] = []
    for g in groups_spec_all:
        required = bool((g or {}).get("required"))
        if (not required) and (not a.include_optional):
            continue
        if isinstance(g, dict):
            groups_spec.append(g)
    rendered_queries: dict[str, Any] = {
        "preset": preset_obj.get("name"),
        "customer_id": a.customer_id,
        "since": a.since,
        "until": a.until,
        "segmentation": a.segmentation,
        "include_optional": bool(a.include_optional),
        "groups": [],
    }

    default_max_rows = 100000
    group_results: list[GroupResult] = []
    table_results: list[TableResult] = []
    warnings: list[str] = []
    any_failed = False
    any_required_failed = False

    try:
        client = build_google_ads_client(cfg)
        ga_service = client.get_service("GoogleAdsService")
    except Exception as e:  # noqa: BLE001
        # Ensure failures that might include secret values are redacted and still produce auditable outputs.
        msg = redact_secrets(f"{type(e).__name__}: {e}", secrets)
        writer.append_error(
            {
                "ts_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "group_id": "__client__",
                "required": True,
                "error_type": type(e).__name__,
                "error": msg,
            }
        )
        writer.write_queries(rendered_queries)
        manifest = build_manifest(
            tool="google-ads-api-tool",
            tool_version=str(tool_version or ""),
            preset=preset_obj,
            customer_id=a.customer_id,
            since=a.since,
            until=a.until,
            segmentation=a.segmentation,
            join_map=dict(preset_obj.get("join_map") or {}),
            groups=[],
            tables=[],
            warnings=[msg],
            errors_path="errors/errors.jsonl",
            queries_path="queries/queries.json",
            schema_version=1,
        )
        writer.write_manifest(manifest)
        receipt = {
            "ok": False,
            "dry_run": False,
            "preset": a.preset,
            "out_dir": str(writer.paths.out_dir),
            "manifest_path": str(writer.paths.manifest_json),
            "errors_path": str(writer.paths.errors_jsonl),
            "queries_path": str(writer.paths.queries_json),
            "group_count": 0,
            "table_count": 0,
            "partial_success": True,
            "required_group_failed": True,
            "warnings": [msg],
        }
        if receipt_out:
            write_json_file(receipt_out, receipt)
        if artifacts_dir:
            write_json_file(artifacts_dir / "receipt.json", receipt)
        audit_write("snapshot_export_apply", {"ok": False, "error_type": type(e).__name__})
        return 1, {"ok": False, "error": msg, "error_type": type(e).__name__, "out_dir": str(writer.paths.out_dir)}

    for g in groups_spec:
        gid = str((g or {}).get("group_id") or "").strip()
        required = bool((g or {}).get("required"))
        output_filename = str((g or {}).get("output") or "").strip()
        join_keys = list((g or {}).get("join_keys") or [])
        templates = (g or {}).get("gaql_templates") or {}
        variant = a.segmentation if a.segmentation in templates else "base"
        if variant != a.segmentation and str(a.segmentation or "").strip() and a.segmentation != "base":
            warnings.append(f"Group {gid} missing template variant '{a.segmentation}'; used 'base'")
        template = str(templates.get(variant) or "")
        query = _render(template, customer_id=a.customer_id, since=a.since, until=a.until)
        rendered_queries["groups"].append({"group_id": gid, "template_variant": variant, "query": query})

        max_rows = a.max_rows
        if max_rows is None:
            try:
                max_rows = int((g or {}).get("max_rows_default") or 0) or default_max_rows
            except Exception:
                max_rows = default_max_rows

        row_count = 0
        truncated = False
        error_count = 0
        status = "ok"

        try:
            table_path, f = writer.open_table_for_write(output_filename)
            with f:
                req = client.get_type("SearchGoogleAdsRequest")
                req.customer_id = a.customer_id
                req.query = query
                it = ga_service.search(request=req)
                for row in _iter_rows(it):
                    f.write(json.dumps(row, ensure_ascii=False) + "\n")
                    row_count += 1
                    if max_rows is not None and row_count >= max_rows:
                        truncated = True
                        break
        except Exception as e:  # noqa: BLE001
            any_failed = True
            if required:
                any_required_failed = True
            status = "failed"
            error_count = 1
            msg = redact_secrets(f"{type(e).__name__}: {e}", secrets)
            writer.append_error(
                {
                    "ts_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                    "group_id": gid,
                    "required": required,
                    "error_type": type(e).__name__,
                    "error": msg,
                }
            )
        else:
            table_results.append(
                TableResult(
                    name=Path(output_filename).stem,
                    path=f"tables/{output_filename}",
                    row_count=row_count,
                    truncated=truncated,
                    join_keys=[str(x) for x in join_keys],
                    source_group_id=gid,
                )
            )
            if truncated:
                warnings.append(f"Group {gid} truncated at max_rows={max_rows}")

        group_results.append(
            GroupResult(
                group_id=gid,
                required=required,
                status=status,
                error_count=error_count,
                row_count=row_count,
                truncated=truncated,
            )
        )

    # Derived table: creative anatomy (best-effort, joinable).
    creative_join_keys: list[str] = []
    asset_group_join_keys: list[str] = []
    for g in groups_spec:
        gid = str((g or {}).get("group_id") or "")
        out = str((g or {}).get("output") or "")
        if gid == "ad_group_ads" or out == "ad_group_ads.jsonl":
            creative_join_keys = [str(x) for x in ((g or {}).get("join_keys") or [])]
        if gid == "asset_groups" or out == "asset_groups.jsonl":
            asset_group_join_keys = [str(x) for x in ((g or {}).get("join_keys") or [])]
    if asset_group_join_keys:
        seen: set[str] = set()
        combined: list[str] = []
        for x in [*creative_join_keys, *asset_group_join_keys]:
            if not x or x in seen:
                continue
            combined.append(x)
            seen.add(x)
        creative_join_keys = combined
    ca = write_creative_anatomy_table(pack_dir=writer.paths.out_dir)
    warnings.extend(list(ca.warnings))
    table_results.append(
        TableResult(
            name="creative_anatomy",
            path="tables/creative_anatomy.jsonl",
            row_count=int(ca.row_count),
            truncated=False,
            join_keys=creative_join_keys,
            source_group_id="__derived__:creative_anatomy",
        )
    )

    writer.write_queries(rendered_queries)
    manifest = build_manifest(
        tool="google-ads-api-tool",
        tool_version=str(tool_version or ""),
        preset=preset_obj,
        customer_id=a.customer_id,
        since=a.since,
        until=a.until,
        segmentation=a.segmentation,
        join_map=dict(preset_obj.get("join_map") or {}),
        groups=group_results,
        tables=table_results,
        warnings=warnings,
        errors_path="errors/errors.jsonl",
        queries_path="queries/queries.json",
        schema_version=1,
    )
    writer.write_manifest(manifest)

    receipt = {
        "ok": (not strict) or (not any_required_failed),
        "dry_run": False,
        "preset": a.preset,
        "out_dir": str(writer.paths.out_dir),
        "manifest_path": str(writer.paths.manifest_json),
        "errors_path": str(writer.paths.errors_jsonl),
        "queries_path": str(writer.paths.queries_json),
        "group_count": len(group_results),
        "table_count": len(table_results),
        "partial_success": any_failed,
        "required_group_failed": any_required_failed,
        "warnings": list(warnings),
    }
    if receipt_out:
        write_json_file(receipt_out, receipt)
    if artifacts_dir:
        write_json_file(artifacts_dir / "receipt.json", receipt)

    audit_write(
        "snapshot_export_apply",
        {
            "ok": receipt["ok"],
            "dry_run": False,
            "preset": a.preset,
            "partial_success": any_failed,
            "required_group_failed": any_required_failed,
            "out_dir": str(writer.paths.out_dir),
        },
    )

    if strict and any_required_failed:
        return 1, {
            "ok": False,
            "dry_run": False,
            "error": "Snapshot export failed in --strict mode due to required group failures",
            "error_type": "StrictModeError",
            "out_dir": str(writer.paths.out_dir),
            "manifest_path": str(writer.paths.manifest_json),
            "errors_path": str(writer.paths.errors_jsonl),
            "partial_success": any_failed,
            "required_group_failed": any_required_failed,
        }

    return 0, {
        "ok": True,
        "dry_run": False,
        "out_dir": str(writer.paths.out_dir),
        "manifest_path": str(writer.paths.manifest_json),
        "errors_path": str(writer.paths.errors_jsonl),
        "partial_success": any_failed,
        "warnings": list(warnings),
    }
