from __future__ import annotations

import csv
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from .download import run_download


def _irreversible_batch_recovery_contract() -> dict[str, Any]:
    return {
        "end_state": "irreversible_and_clearly_labeled",
        "strategy": "no_inverse",
        "rollback_ready": False,
        "automatic_rollback": False,
        "backups": [],
        "snapshots": [],
        "rollback_plan": None,
        "restore_note": (
            "Licensed batch downloads and license records cannot be rolled back by this CLI. "
            "Local cleanup is manual."
        ),
    }


def cmd_jobs_run(args: Any, ctx: dict[str, Any]) -> int:
    if not ctx["apply"] or not ctx["yes"]:
        raise RuntimeError("Refused: batch jobs require --apply and --yes")

    job_file = Path(args.file)
    project_cfg = ctx.get("project_cfg") or {}
    project_dir = Path(str(ctx.get("project_dir") or Path.cwd())).expanduser().resolve()
    out_dir = (str(getattr(args, "out_dir", "") or "")).strip() or str(project_cfg.get("downloads_dir") or (project_dir / "downloads"))
    inventory = (str(getattr(args, "inventory", "") or "")).strip() or str(project_cfg.get("inventory_csv") or (project_dir / "licensed-downloads-ledger.csv"))
    if not out_dir.strip():
        raise RuntimeError("Refused: missing --out-dir (or project config `downloads_dir`)")
    if not inventory.strip():
        raise RuntimeError("Refused: missing --inventory (or project config `inventory_csv`)")
    limit = args.limit

    processed = 0
    errors = 0
    downloaded_files = 0
    results: list[dict[str, Any]] = []
    with job_file.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row_num, row in enumerate(reader, start=1):
            if limit is not None and processed >= int(limit):
                break
            processed += 1
            rid = (row.get("resource_id") or row.get("id") or "").strip()
            fmt = (row.get("format") or "").strip()
            try:
                if not rid or not fmt:
                    raise RuntimeError(f"Invalid job row (requires resource_id and format): {row}")

                result = run_download(
                    SimpleNamespace(
                        id=rid,
                        format=fmt,
                        out_dir=out_dir,
                        inventory=inventory,
                        post_slug=(row.get("post_slug") or "").strip(),
                        ghost_id=(row.get("ghost_id") or "").strip(),
                        usage_role=(row.get("usage_role") or "").strip(),
                        image_size=(row.get("image_size") or "").strip() or None,
                        download_url_jsonpath=(row.get("download_url_jsonpath") or "").strip() or None,
                        license_url_jsonpath=(row.get("license_url_jsonpath") or "").strip() or None,
                        force=(row.get("force") or "").strip().lower() in ("1", "true", "yes", "y"),
                    ),
                    ctx,
                )
                if result.get("refused"):
                    errors += 1
                    results.append(
                        {
                            "row": row_num,
                            "action": "download",
                            "input": row,
                            "refused": True,
                            "reasons": result.get("reasons") or [],
                            "result": result,
                        }
                    )
                    break
                rows = result.get("rows")
                file_paths: list[str] = []
                if isinstance(rows, list):
                    downloaded_files += len(rows)
                    file_paths = [
                        str(r.get("file_path"))
                        for r in rows
                        if isinstance(r, dict) and r.get("file_path")
                    ]
                results.append(
                    {
                        "row": row_num,
                        "action": "download",
                        "input": row,
                        "result": {"resource_id": rid, "format": fmt, "file_paths": file_paths},
                    }
                )
            except Exception as e:  # noqa: BLE001
                errors += 1
                results.append({"row": row_num, "action": "download", "input": row, "error": str(e)})
                break

    out = {
        "ok": errors == 0,
        "apply": True,
        "count": processed,
        "errors": errors,
        "downloaded_files": downloaded_files,
        "results": results,
        "recovery": _irreversible_batch_recovery_contract(),
    }
    if "audit" in ctx:
        ctx["audit"].write("jobs.run", out)
    ctx["out"].emit(out)
    return 1 if errors else 0
