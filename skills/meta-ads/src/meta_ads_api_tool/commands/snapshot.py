from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Callable

from ..assets import AssetResult, download_assets
from ..audit_log import AuditLogger, CompositeAuditLogger
from ..chunking import ChunkFailure, chunk_list, ensure_field, merge_rows_by_id, parse_fields_csv
from ..creative_anatomy import extract_asset_urls, extract_creative_anatomy
from ..errors import ToolError, ValidationError
from ..graph import GraphClient
from ..graph import _parse_kv_pairs
from ..http import HttpClient
from ..presets import get_preset
from ..snapshot.manifest import TableInventoryItem, build_manifest, utc_now_iso
from ..snapshot.writer import write_json, write_jsonl
from ._ad_account_edge_helpers import _required_ad_account_id


_EDGE_BY_SURFACE = {
    "campaigns": "campaigns",
    "ad_sets": "adsets",
    "ads": "ads",
    "creatives": "adcreatives",
    "insights": "insights",
}


def _time_range_json(*, since: str, until: str) -> str:
    s = str(since or "").strip()
    u = str(until or "").strip()
    if not s or not u:
        raise ValidationError("Use both --since and --until (YYYY-MM-DD) or omit both")
    return json.dumps({"since": s, "until": u}, separators=(",", ":"))


def _sanitize_table_suffix(name: str) -> str:
    safe = "".join(c.lower() if c.isalnum() or c in {"-", "_"} else "_" for c in str(name or "").strip())
    safe = safe.strip("._-")
    return safe


def _generate_run_id() -> str:
    # Time-based; caller can override via --run-id for deterministic packs.
    return time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())


def _sanitize_pack_dir_name(name: str) -> str:
    safe = "".join(c if c.isalnum() or c in {"-", "_", "."} else "_" for c in name.strip())
    safe = safe.strip("._-")
    return safe or "snapshot"


def _append_jsonl(path: Path, obj: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:  # noqa: SIM115
        f.write(json.dumps(obj, ensure_ascii=False, sort_keys=True) + "\n")


def _merge_rows_by_key(
    passes: list[list[dict[str, Any]]],
    *,
    key_fn: Callable[[dict[str, Any]], str] | None,
) -> list[dict[str, Any]]:
    if key_fn is None:
        return merge_rows_by_id(passes, id_key="id")
    out: list[dict[str, Any]] = []
    by_key: dict[str, dict[str, Any]] = {}
    order: list[str] = []
    for rows in passes:
        for row in rows:
            if not isinstance(row, dict):
                continue
            k = key_fn(row)
            if not k:
                continue
            if k not in by_key:
                by_key[k] = dict(row)
                order.append(k)
            else:
                by_key[k].update(row)
    for k in order:
        out.append(by_key[k])
    return out


def _chunked_list_edge(
    *,
    surface: str,
    graph: GraphClient,
    object_id: str,
    edge: str,
    fields_csv: str,
    params: dict[str, Any],
    fields_chunk_size: int,
    max_pages: int | None,
    max_items: int | None,
    strict: bool,
    merge_key_fn: Callable[[dict[str, Any]], str] | None,
    request_summaries: list[dict[str, Any]],
    errors: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], bool]:
    fields = parse_fields_csv(fields_csv)
    if surface != "insights":
        fields = ensure_field(fields, "id")
    else:
        fields = ensure_field(fields, "ad_id")
        fields = ensure_field(fields, "date_start")
        fields = ensure_field(fields, "date_stop")
    chunks = chunk_list(fields, max_chunk_size=fields_chunk_size) if fields else [[]]
    passes: list[list[dict[str, Any]]] = []
    had_error = False

    for idx, chunk in enumerate(chunks):
        params2 = dict(params)
        if chunk:
            params2["fields"] = ",".join(chunk)
        try:
            res = graph.list_edge(
                object_id=object_id,
                edge=edge,
                params=params2,
                max_pages=max_pages,
                max_items=max_items,
            )
            rows = [x for x in res.data if isinstance(x, dict)]
            passes.append(rows)
            request_summaries.append(
                {
                    "surface": surface,
                    "path": f"{object_id}/{edge}",
                    "object_id": object_id,
                    "edge": edge,
                    "fields_count": len(chunk),
                    "chunk_index": idx,
                    "chunks_total": len(chunks),
                    "params_keys": sorted([k for k in params2.keys() if k != "access_token"]),
                }
            )
        except Exception as e:  # noqa: BLE001
            had_error = True
            fail = ChunkFailure(
                surface=surface,
                chunk_index=idx,
                fields=tuple(chunk),
                error_type=type(e).__name__,
                error=HttpClient.redact_url(str(e)),
            )
            errors.append({"type": "chunk_fetch_failed", **fail.to_public_dict()})
            if strict:
                return ([], True)

    merged = _merge_rows_by_key(passes, key_fn=merge_key_fn)
    return (merged, had_error)


def _insights_key(row: dict[str, Any]) -> str:
    aid = str(row.get("ad_id") or "").strip()
    ds = str(row.get("date_start") or "").strip()
    de = str(row.get("date_stop") or "").strip()
    if not aid or not ds or not de:
        return ""
    return f"{aid}:{ds}:{de}"


def _normalize_rows(*, table: str, ad_account_id: str, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        base = {"ad_account_id": ad_account_id}
        if table == "campaigns":
            base["campaign_id"] = row.get("id")
        elif table == "ad_sets":
            base["adset_id"] = row.get("id")
            base["campaign_id"] = row.get("campaign_id")
        elif table == "ads":
            base["ad_id"] = row.get("id")
            base["adset_id"] = row.get("adset_id")
            base["campaign_id"] = row.get("campaign_id")
            creative = row.get("creative")
            if isinstance(creative, dict):
                base["creative_id"] = creative.get("id")
            else:
                base["creative_id"] = None
        elif table == "creatives":
            base["creative_id"] = row.get("id")
        elif table == "insights":
            base["ad_id"] = row.get("ad_id")
            base["date_start"] = row.get("date_start")
            base["date_stop"] = row.get("date_stop")
        out.append({**base, **row})
    return out


def cmd_snapshot_export(args, ctx) -> int:
    out = ctx["out"]
    cfg = ctx["cfg"]
    graph = ctx["graph"]
    base_audit = ctx["audit"]
    http = ctx.get("http")

    ad_account_id = _required_ad_account_id(args, ctx)
    preset_id = str(getattr(args, "preset", "") or "").strip()
    if not preset_id:
        raise ValidationError("Missing --preset")

    out_dir = str(getattr(args, "out_dir", "") or "").strip()
    if not out_dir:
        raise ValidationError("Missing --out-dir")

    strict = bool(getattr(args, "strict", False))
    since = str(getattr(args, "since", "") or "").strip()
    until = str(getattr(args, "until", "") or "").strip()
    date_preset = str(getattr(args, "date_preset", "") or "").strip()
    if date_preset and (since or until):
        raise ValidationError("Use either --date-preset or --since/--until (not both)")
    if (since and not until) or (until and not since):
        raise ValidationError("Use --since and --until together (or omit both)")

    insights_time_increment = str(getattr(args, "insights_time_increment", "") or "").strip()
    insights_breakdowns = getattr(args, "insights_breakdown", None) or []
    insights_action_breakdowns = getattr(args, "insights_action_breakdown", None) or []
    insights_action_windows = getattr(args, "insights_action_attribution_window", None) or []

    extra_insights_breakdown_tables_raw = getattr(args, "extra_insights_breakdown_table", None) or []
    extra_insights_breakdown_tables: list[tuple[str, str]] = []
    seen_suffixes: set[str] = set()
    for raw in extra_insights_breakdown_tables_raw:
        s = str(raw or "").strip()
        if not s:
            continue
        if ":" not in s:
            raise ValidationError("Invalid --extra-insights-breakdown-table (expected suffix:breakdowns_csv)")
        suffix_raw, breakdowns_csv = s.split(":", 1)
        suffix = _sanitize_table_suffix(suffix_raw)
        breakdowns_csv = str(breakdowns_csv or "").strip()
        if not suffix:
            raise ValidationError("Invalid --extra-insights-breakdown-table suffix (empty)")
        if not breakdowns_csv:
            raise ValidationError("Invalid --extra-insights-breakdown-table breakdowns (empty)")
        if suffix in seen_suffixes:
            raise ValidationError(f"Duplicate --extra-insights-breakdown-table suffix: {suffix}")
        seen_suffixes.add(suffix)
        extra_insights_breakdown_tables.append((suffix, breakdowns_csv))

    download_assets_enabled = bool(getattr(args, "download_assets", False))
    assets_overwrite = str(getattr(args, "assets_overwrite", "") or "if_missing").strip() or "if_missing"
    max_pages = getattr(args, "max_pages", None)
    max_items = getattr(args, "max_items", None)
    limit = int(getattr(args, "limit", 100) or 100)
    fields_chunk_size = int(getattr(args, "fields_chunk_size", 20) or 20)
    if limit <= 0:
        raise ValidationError("--limit must be > 0")

    run_id = str(getattr(args, "run_id", "") or "").strip() or _generate_run_id()
    pack_name = _sanitize_pack_dir_name(f"meta_ads_snapshot_{run_id}")
    pack_dir = Path(out_dir).expanduser().resolve() / pack_name
    if pack_dir.exists():
        raise ValidationError(f"Refusing to overwrite existing pack dir: {pack_dir}")

    run_dir = Path(".state") / "runs" / run_id
    audit_path = run_dir / "audit.jsonl"
    runs_index_path = Path(".state") / "runs" / "index.jsonl"
    run_audit = AuditLogger(path=str(audit_path), enabled=True)
    audit = CompositeAuditLogger([base_audit, run_audit])

    started_at = utc_now_iso()
    errors: list[dict[str, Any]] = []
    request_summaries: list[dict[str, Any]] = []
    tables_written: list[TableInventoryItem] = []
    asset_results: list[AssetResult] = []
    partial_success = False

    audit.bind_context(
        {
            "tool": "meta-ads-api-tool",
            "version": str(ctx.get("version", "") or ""),
            "command": "snapshot export",
            "run_id": run_id,
            "ad_account_id": ad_account_id,
            "preset_id": preset_id,
        }
    )

    preset_payload = get_preset(preset_id)
    preset_schema_version = str(preset_payload.get("schema_version") or "")
    preset = preset_payload.get("preset") or {}
    surfaces = preset.get("surfaces") or {}
    if not isinstance(surfaces, dict):
        raise ValidationError("Invalid preset surfaces")

    fields_override: dict[str, str] = {}
    for surface_name, arg_name in (
        ("campaigns", "fields_campaigns"),
        ("ad_sets", "fields_ad_sets"),
        ("ads", "fields_ads"),
        ("creatives", "fields_creatives"),
        ("insights", "fields_insights"),
    ):
        v = str(getattr(args, arg_name, "") or "").strip()
        if v:
            fields_override[surface_name] = v

    pack_dir.mkdir(parents=True, exist_ok=False)
    (pack_dir / "tables").mkdir(parents=True, exist_ok=True)

    ok = True
    try:
        for surface_name in ("campaigns", "ad_sets", "ads", "creatives", "insights"):
            surface_cfg = surfaces.get(surface_name, None)
            if not isinstance(surface_cfg, dict):
                continue
            edge = _EDGE_BY_SURFACE.get(surface_name)
            if not edge:
                continue

            fields_csv = fields_override.get(surface_name) or str(surface_cfg.get("fields") or "").strip()
            params: dict[str, Any] = {}
            if surface_name == "insights":
                level = str(surface_cfg.get("level") or "").strip()
                if not level:
                    errors.append(
                        {
                            "type": "surface_config_invalid",
                            "surface": surface_name,
                            "error": "Missing insights.level in preset",
                        }
                    )
                    if strict:
                        ok = False
                        break
                    partial_success = True
                    continue
                params["level"] = level

            preset_params = surface_cfg.get("params") or {}
            if isinstance(preset_params, dict):
                for k, v in preset_params.items():
                    if k == "access_token":
                        continue
                    params[str(k)] = v

            extra = _parse_kv_pairs(getattr(args, "param", None))
            if "access_token" in extra:
                extra.pop("access_token", None)
            for k, v in extra.items():
                params[k] = v

            if surface_name == "insights":
                # Typed, structured overrides (highest precedence).
                if date_preset:
                    params["date_preset"] = date_preset
                    params.pop("time_range", None)
                if since and until:
                    params["time_range"] = _time_range_json(since=since, until=until)
                    params.pop("date_preset", None)
                if insights_time_increment:
                    params["time_increment"] = insights_time_increment
                if insights_breakdowns:
                    vals = [str(b).strip() for b in insights_breakdowns if str(b).strip()]
                    if vals:
                        params["breakdowns"] = ",".join(vals)
                if insights_action_breakdowns:
                    vals = [str(b).strip() for b in insights_action_breakdowns if str(b).strip()]
                    if vals:
                        params["action_breakdowns"] = ",".join(vals)
                if insights_action_windows:
                    vals = [str(w).strip() for w in insights_action_windows if str(w).strip()]
                    if vals:
                        params["action_attribution_windows"] = ",".join(vals)

            # Always enforce the explicit --limit flag as the request page size.
            params["limit"] = str(limit)

            merge_key_fn = _insights_key if surface_name == "insights" else None
            rows, had_error = _chunked_list_edge(
                surface=surface_name,
                graph=graph,
                object_id=ad_account_id,
                edge=edge,
                fields_csv=fields_csv,
                params=params,
                fields_chunk_size=fields_chunk_size,
                max_pages=max_pages,
                max_items=max_items,
                strict=strict,
                merge_key_fn=merge_key_fn,
                request_summaries=request_summaries,
                errors=errors,
            )
            if had_error:
                partial_success = True
                if strict:
                    ok = False
                    break

            table_name = surface_name
            norm = _normalize_rows(table=table_name, ad_account_id=ad_account_id, rows=rows)
            table_path = pack_dir / "tables" / f"{table_name}.jsonl"
            rows_written = write_jsonl(table_path, norm)
            tables_written.append(TableInventoryItem(table=table_name, relpath=str(Path("tables") / f"{table_name}.jsonl"), rows=rows_written))
            audit.write(
                "snapshot.table_written",
                {"table": table_name, "rows": rows_written, "path": str(table_path)},
            )

            if surface_name == "creatives":
                anatomy_rows: list[dict[str, Any]] = []
                asset_url_rows: list[dict[str, Any]] = []
                for row in rows:
                    if not isinstance(row, dict):
                        continue
                    anatomy = extract_creative_anatomy(row)
                    anatomy_rows.append({"ad_account_id": ad_account_id, **anatomy})
                    for it in extract_asset_urls(row):
                        if not isinstance(it, dict):
                            continue
                        it2 = dict(it)
                        it2["url"] = HttpClient.redact_url(str(it2.get("url") or "").strip())
                        asset_url_rows.append({"ad_account_id": ad_account_id, **it2})

                anatomy_path = pack_dir / "tables" / "creative_anatomy.jsonl"
                anatomy_written = write_jsonl(anatomy_path, anatomy_rows)
                tables_written.append(
                    TableInventoryItem(
                        table="creative_anatomy",
                        relpath=str(Path("tables") / "creative_anatomy.jsonl"),
                        rows=anatomy_written,
                    )
                )
                audit.write(
                    "snapshot.table_written",
                    {"table": "creative_anatomy", "rows": anatomy_written, "path": str(anatomy_path)},
                )

                asset_urls_path = pack_dir / "tables" / "asset_urls.jsonl"
                asset_urls_written = write_jsonl(asset_urls_path, asset_url_rows)
                tables_written.append(
                    TableInventoryItem(
                        table="asset_urls",
                        relpath=str(Path("tables") / "asset_urls.jsonl"),
                        rows=asset_urls_written,
                    )
                )
                audit.write(
                    "snapshot.table_written",
                    {"table": "asset_urls", "rows": asset_urls_written, "path": str(asset_urls_path)},
                )

            if surface_name == "insights" and extra_insights_breakdown_tables:
                for suffix, breakdowns_csv in extra_insights_breakdown_tables:
                    table2 = f"insights_{suffix}"
                    params2 = dict(params)
                    params2["breakdowns"] = breakdowns_csv
                    rows2, had_error2 = _chunked_list_edge(
                        surface=table2,
                        graph=graph,
                        object_id=ad_account_id,
                        edge=edge,
                        fields_csv=fields_csv,
                        params=params2,
                        fields_chunk_size=fields_chunk_size,
                        max_pages=max_pages,
                        max_items=max_items,
                        strict=strict,
                        merge_key_fn=_insights_key,
                        request_summaries=request_summaries,
                        errors=errors,
                    )
                    if had_error2:
                        partial_success = True
                        if strict:
                            ok = False
                            break

                    norm2 = _normalize_rows(table="insights", ad_account_id=ad_account_id, rows=rows2)
                    path2 = pack_dir / "tables" / f"{table2}.jsonl"
                    rows2_written = write_jsonl(path2, norm2)
                    tables_written.append(
                        TableInventoryItem(
                            table=table2,
                            relpath=str(Path("tables") / f"{table2}.jsonl"),
                            rows=rows2_written,
                        )
                    )
                    audit.write(
                        "snapshot.table_written",
                        {"table": table2, "rows": rows2_written, "path": str(path2)},
                    )
                if strict and not ok:
                    break

            if surface_name == "creatives" and download_assets_enabled:
                if http is None:
                    raise ValidationError("Missing http client in context (required for --download-assets)")
                candidates: list[dict[str, Any]] = []
                for row in rows:
                    if isinstance(row, dict):
                        candidates.extend(extract_asset_urls(row))
                candidates = [c for c in candidates if str(c.get("kind") or "") in {"image_url"}]
                if candidates:
                    assets_dir = pack_dir / "assets"
                    asset_results = download_assets(
                        http=http,
                        items=candidates,
                        out_dir=assets_dir,
                        overwrite=assets_overwrite,
                        errors=errors,
                    )
                    assets_table_path = pack_dir / "tables" / "assets.jsonl"
                    assets_rows = [{"ad_account_id": ad_account_id, **r.to_public_dict()} for r in asset_results]
                    assets_written = write_jsonl(assets_table_path, assets_rows)
                    tables_written.append(
                        TableInventoryItem(
                            table="assets",
                            relpath=str(Path("tables") / "assets.jsonl"),
                            rows=assets_written,
                        )
                    )
                    audit.write(
                        "snapshot.assets_written",
                        {
                            "rows": assets_written,
                            "downloaded": sum(1 for r in asset_results if r.status == "downloaded"),
                            "failed": sum(1 for r in asset_results if r.status == "failed"),
                            "skipped_exists": sum(1 for r in asset_results if r.status == "skipped_exists"),
                            "assets_dir": str(assets_dir),
                        },
                    )

        if download_assets_enabled and not any(t.table == "assets" for t in tables_written):
            assets_table_path = pack_dir / "tables" / "assets.jsonl"
            assets_written = write_jsonl(assets_table_path, [])
            tables_written.append(
                TableInventoryItem(
                    table="assets",
                    relpath=str(Path("tables") / "assets.jsonl"),
                    rows=assets_written,
                )
            )

        finished_at = utc_now_iso()
        assets_rows = next((t.rows for t in tables_written if t.table == "assets"), 0)
        assets_manifest: dict[str, Any] = {"enabled": bool(download_assets_enabled), "overwrite": assets_overwrite}
        if download_assets_enabled:
            assets_manifest = {
                **assets_manifest,
                "table": {"relpath": str(Path("tables") / "assets.jsonl"), "rows": int(assets_rows)},
                "downloaded": sum(1 for r in asset_results if r.status == "downloaded"),
                "failed": sum(1 for r in asset_results if r.status == "failed"),
                "skipped_exists": sum(1 for r in asset_results if r.status == "skipped_exists"),
            }
        manifest = build_manifest(
            tool="meta-ads-api-tool",
            version=str(ctx.get("version", "") or ""),
            run_id=run_id,
            started_at_utc=started_at,
            finished_at_utc=finished_at,
            base_url=cfg.base_url,
            api_version=cfg.api_version,
            ad_account_id=ad_account_id,
            preset_id=preset_id,
            preset_schema_version=preset_schema_version,
            tables=tables_written,
            assets=assets_manifest,
            request_summaries=request_summaries,
            errors=errors,
        )
        manifest_path = pack_dir / "manifest.json"
        write_json(manifest_path, manifest)
        audit.write("snapshot.manifest_written", {"path": str(manifest_path), "errors_count": len(errors)})

        _append_jsonl(
            runs_index_path,
            {
                "ts": finished_at,
                "run_id": run_id,
                "command": "snapshot export",
                "ad_account_id": ad_account_id,
                "preset_id": preset_id,
                "pack_dir": str(pack_dir),
                "manifest_path": str(manifest_path),
                "audit_log": str(audit_path),
                "ok": ok,
                "partial_success": partial_success,
                "errors_count": len(errors),
            },
        )

        tables_obj = {t.table: {"path": str(pack_dir / t.relpath), "rows": t.rows} for t in tables_written}
        out.emit(
            {
                "ok": ok,
                "snapshot_export": {
                    "run_id": run_id,
                    "ad_account_id": ad_account_id,
                    "preset_id": preset_id,
                    "out_dir": str(pack_dir),
                    "manifest_path": str(manifest_path),
                    "tables": tables_obj,
                    "assets_enabled": bool(download_assets_enabled),
                    "errors_count": len(errors),
                    "partial_success": partial_success,
                    "artifacts": {
                        "run_dir": str(run_dir),
                        "audit_log": str(audit_path),
                        "runs_index": str(runs_index_path),
                    },
                },
            }
        )
        return 0 if ok else 1
    except ToolError as e:
        ok = False
        errors.append({"type": "snapshot_export_failed", "error_type": type(e).__name__, "error": str(e)})
        partial_success = True
        out.emit(
            {
                "ok": False,
                "snapshot_export": {
                    "run_id": run_id,
                    "ad_account_id": ad_account_id,
                    "preset_id": preset_id,
                    "out_dir": str(pack_dir),
                    "errors_count": len(errors),
                    "partial_success": partial_success,
                    "error": str(e),
                    "artifacts": {
                        "run_dir": str(run_dir),
                        "audit_log": str(audit_path),
                        "runs_index": str(runs_index_path),
                    },
                },
            }
        )
        return 1
    finally:
        try:
            audit.close()
        except Exception:
            pass
        try:
            run_audit.close()
        except Exception:
            pass
