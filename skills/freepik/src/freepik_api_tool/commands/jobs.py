from __future__ import annotations

import csv
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from .download import (
    apply_download,
    download_request,
    prepare_download,
    require_reviewed_plan,
    save_plan,
)


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


def _job_requests(args: Any, ctx: dict[str, Any]) -> list[dict[str, Any]]:
    requests = []
    with Path(args.file).expanduser().open(newline="", encoding="utf-8") as stream:
        for number, row in enumerate(csv.DictReader(stream), start=1):
            if args.limit is not None and number > args.limit:
                break
            rid = (row.get("resource_id") or row.get("id") or "").strip()
            fmt = (row.get("format") or "").strip()
            if not rid or not fmt:
                raise RuntimeError(f"Job row {number} needs a resource_id and format.")
            job = SimpleNamespace(
                id=rid,
                format=fmt,
                out_dir=args.out_dir,
                inventory=args.inventory,
                post_slug=row.get("post_slug"),
                ghost_id=row.get("ghost_id"),
                usage_role=row.get("usage_role"),
                image_size=row.get("image_size"),
                download_url_jsonpath=(row.get("download_url_jsonpath") or "").strip() or None,
                license_url_jsonpath=(row.get("license_url_jsonpath") or "").strip() or None,
                force=(row.get("force") or "").strip().lower() in {"1", "true", "yes", "y"},
            )
            requests.append(download_request(job, ctx))
    return requests


def cmd_jobs_run(args: Any, ctx: dict[str, Any]) -> int:
    apply = bool(ctx["apply"])
    if apply and not ctx["yes"]:
        raise RuntimeError("Applying batch downloads requires --yes.")
    if apply and not ctx.get("ack_no_snapshot"):
        raise RuntimeError("Applying batch downloads requires --ack-no-snapshot after approval.")

    requests = _job_requests(args, ctx)
    if apply:
        require_reviewed_plan(ctx, kind="batch-download", requests=requests)
    prepared = [prepare_download(req, ctx) for req in requests]
    recovery = _irreversible_batch_recovery_contract()
    if not apply:
        plan = {"kind": "batch-download", "plans": [p for p, _ in prepared]}
        ctx["out"].emit({
            "ok": True, "dry_run": True, "count": len(prepared), "plan": plan,
            "plan_out": save_plan(ctx.get("plan_out"), plan), "recovery": recovery,
        })
        return 0

    files = 0
    results = []
    for num, (plan, data) in enumerate(prepared, start=1):
        try:
            result = apply_download(plan, data, ctx)
        except (RuntimeError, OSError, ValueError) as exc:
            result = {"ok": False, "provider_status": "not_sent", "error": str(exc), "rows": [], "file_paths": []}
        files += len(result.get("file_paths", []))
        results.append({"row": num, "action": "download", "input": plan["request"], "result": result})
        if not result["ok"]:
            break
    errors = int(bool(results) and not results[-1]["result"]["ok"])
    out = {
        "ok": errors == 0,
        "apply": True,
        "count": len(results),
        "remaining": len(prepared) - len(results),
        "errors": errors,
        "downloaded_files": files,
        "results": results,
        "recovery": recovery,
    }
    if "audit" in ctx:
        ctx["audit"].write("jobs.run", out)
    ctx["out"].emit(out)
    return errors
