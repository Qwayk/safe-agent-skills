from __future__ import annotations

import csv
import json
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ..http import HttpClient
from ..wp_api import WordPressApi
from .. import v2 as v2util
from .media import media_set_core
from .post import post_set_image_captions_core


@dataclass(frozen=True)
class JobRow:
    action: str
    data: dict[str, Any]


def _iter_jobs(path: str) -> Iterator[JobRow]:
    if path.lower().endswith(".json"):
        with open(path, encoding="utf-8") as f:
            doc = json.load(f)
        items = doc["jobs"] if isinstance(doc, dict) and "jobs" in doc else doc
        if not isinstance(items, list):
            raise RuntimeError("JSON job file must be a list or an object with 'jobs': [...]")
        for row in items:
            if not isinstance(row, dict) or "action" not in row:
                raise RuntimeError("Each JSON job must be an object with an 'action' key.")
            action = str(row["action"]).strip()
            data = {k: v for k, v in row.items() if k != "action"}
            yield JobRow(action=action, data=data)
        return

    if path.lower().endswith(".csv"):
        with open(path, encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if not row:
                    continue
                action = (row.get("action") or "").strip()
                if not action:
                    raise RuntimeError("CSV job row missing 'action' column.")
                data = {k: v for k, v in row.items() if k != "action"}
                yield JobRow(action=action, data=data)
        return

    raise RuntimeError("Unsupported job file type. Use .csv or .json")


def cmd_jobs_run(args, ctx) -> int:
    if ctx["apply"] and not ctx["yes"]:
        raise RuntimeError("Refused: batch jobs require both --apply and --yes")
    if ctx["apply"] and not bool(ctx.get("ack_no_snapshot")):
        raise RuntimeError(
            "Refused: jobs apply has no saved live per-row before-state snapshot. Review the dry-run plan and pass "
            "--ack-no-snapshot only when the approved batch should continue without automatic restore points."
        )

    api = WordPressApi.from_config(
        ctx["cfg"], HttpClient(timeout_s=ctx["timeout_s"], verbose=ctx["verbose"])
    )

    jobs = list(_iter_jobs(str(args.file)))
    job_file_snapshot = v2util.save_before_state(
        env_file=str(ctx["env_file"]),
        run_id=str(ctx["before_state_run_id"]),
        family="jobs.run.input",
        selector=f"file-{Path(str(args.file)).stem}",
        payload={
            "file": str(args.file),
            "limit": args.limit,
            "jobs": [{"row": idx, "action": job.action, "data": job.data} for idx, job in enumerate(jobs, start=1)],
        },
    )
    before_state = {
        "required": True,
        "supported": False,
        "status": "no_snapshot_available",
        "reason": "WordPress jobs.run is a mixed batch runner and does not save live per-row before-state snapshots.",
        "job_file_snapshot": job_file_snapshot,
    }

    results = []
    processed = 0
    errors = 0
    for row_num, job in enumerate(jobs, start=1):
        if args.limit is not None and processed >= int(args.limit):
            break
        processed += 1

        try:
            if job.action == "media.set":
                res = media_set_core(
                    api,
                    media_id=int(job.data["id"]),
                    caption=_none_if_empty(job.data.get("caption")),
                    alt_text=_none_if_empty(job.data.get("alt_text")),
                    title=_none_if_empty(job.data.get("title")),
                    apply=bool(ctx["apply"]),
                )
                results.append(
                    {"row": row_num, "action": job.action, "input": job.data, "result": res}
                )
            elif job.action == "post.set_image_captions":
                res = post_set_image_captions_core(
                    api,
                    post_type=str(job.data.get("post_type") or "posts"),
                    slug=str(job.data["slug"]),
                    caption=_none_if_empty(job.data.get("caption")),
                    caption_html=_none_if_empty(job.data.get("caption_html")),
                    alt_text=_none_if_empty(job.data.get("alt_text")),
                    captions_file=_none_if_empty(job.data.get("captions_file")),
                    only_ids_csv=_none_if_empty(job.data.get("only_ids")),
                    include_diff=bool(_truthy(job.data.get("diff"))),
                    apply=bool(ctx["apply"]),
                )
                results.append(
                    {"row": row_num, "action": job.action, "input": job.data, "result": res}
                )
            else:
                raise RuntimeError(f"Unknown action: {job.action}")
        except Exception as e:
            errors += 1
            results.append({"row": row_num, "action": job.action, "input": job.data, "error": str(e)})
            break

    out = {
        "ok": errors == 0,
        "apply": bool(ctx["apply"]),
        "count": processed,
        "errors": errors,
        "results": results,
    }

    def _row_changed(item: dict[str, Any]) -> bool:
        res = item.get("result")
        if isinstance(res, dict):
            if "changed" in res:
                return bool(res.get("changed"))
            rep = res.get("report")
            if isinstance(rep, dict) and isinstance(rep.get("updated_blocks"), int):
                return int(rep.get("updated_blocks") or 0) > 0
        return False

    def _row_verified(item: dict[str, Any]) -> bool | None:
        res = item.get("result")
        if isinstance(res, dict) and "verified" in res:
            return bool(res.get("verified"))
        return None

    changed_any = any(isinstance(r, dict) and _row_changed(r) for r in results)
    if not ctx["apply"]:
        plan = {
            **v2util.plan_common_fields(cfg=ctx["cfg"], argv=ctx.get("argv") or []),
            "selector": {"file": str(args.file), "limit": args.limit},
            "risk_level": "high",
            "risk_reasons": ["Batch job run (may edit many resources)"],
            "preconditions": [
                "Review the plan and proposed changes carefully before applying",
                "For apply, use --apply --yes --ack-no-snapshot (jobs enforce this)",
            ],
            "proposed_changes": out.get("results") or [],
            "before_state": before_state,
            "verification_plan": "After apply, each write action is verified via read-back or idempotence checks.",
            "rollback": {
                "supported": False,
                "notes": (
                    "No automatic rollback for mixed job runs. Use each per-row result and run inverse actions "
                    "individually when possible."
                ),
            },
        }
        out["dry_run"] = True
        out["changed"] = changed_any
        out["risk_level"] = plan["risk_level"]
        out["plan"] = plan
        if ctx.get("plan_out"):
            v2util.write_json_file(str(ctx["plan_out"]), plan)
    else:
        verified_ok = errors == 0
        for r in results:
            if not isinstance(r, dict):
                continue
            if not _row_changed(r):
                continue
            v = _row_verified(r)
            if v is False:
                verified_ok = False
                break
        receipt = {
            **v2util.receipt_common_fields(cfg=ctx["cfg"], argv=ctx.get("argv") or []),
            "selector": {"file": str(args.file), "limit": args.limit},
            "changed": changed_any and errors == 0,
            "verification": {"ok": bool(verified_ok), "details": {"errors": errors}},
            "diff_applied": out.get("results") or [],
            "before_state": before_state,
            "no_snapshot_approval": {
                "approved": bool(ctx.get("ack_no_snapshot")),
                "reason": "No saved live per-row before-state snapshot was available for this WordPress jobs batch.",
            },
            "backups": [job_file_snapshot],
            "rollback_plan": None,
        }
        out["changed"] = changed_any and errors == 0
        out["receipt"] = receipt
        if ctx.get("receipt_out"):
            v2util.write_json_file(str(ctx["receipt_out"]), receipt)

    ctx["audit"].write("jobs.run", out)
    ctx["out"].emit(out)
    return 1 if errors else 0


def _none_if_empty(v: Any) -> str | None:
    if v is None:
        return None
    s = str(v).strip()
    return s if s else None


def _truthy(v: Any) -> bool:
    if v is None:
        return False
    if isinstance(v, bool):
        return v
    s = str(v).strip().lower()
    return s in {"1", "true", "yes", "y", "on"}
