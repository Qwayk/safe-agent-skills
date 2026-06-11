from __future__ import annotations

import csv
import json
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from . import report_jobs
from ..write_framework import require_write_allowed
from .write_safety import before_state_contract


@dataclass(frozen=True)
class JobRow:
    action: str
    data: dict[str, Any]


def _iter_jobs(path: str) -> Iterator[JobRow]:
    path = str(path)
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


def _receipt_path(out_dir: str, row_num: int) -> str:
    d = Path(out_dir) / "receipts"
    d.mkdir(parents=True, exist_ok=True)
    return str((d / f"row-{row_num:04d}.json").resolve())


def _write_json_file(path: str, data: dict[str, Any]) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write("\n")


def _require_apply_yes_ack_volume(ctx: dict[str, Any], *, reason: str) -> None:
    _ = reason
    require_write_allowed(ctx, acks_required=["ack-volume"])


def _no_snapshot_fields(*, action: str) -> dict[str, Any]:
    reason = "No reliable before-state snapshot is available for this Pinterest batch report write."
    return {
        "before_state": before_state_contract(
            reason=reason,
            provider_write={
                "service": "Pinterest API",
                "action": action,
                "operations": [{"method": "POST", "path": "/ad_accounts/{ad_account_id}/reports"}],
            },
            local_state={"kind": "jobs_output", "writes_receipts": True, "writes_summary": True},
        ),
        "no_snapshot_approval": {
            "acknowledged": True,
            "flag": "--ack-no-snapshot",
            "reason": reason,
        },
    }


def _get_str(d: dict[str, Any], *keys: str) -> str | None:
    for k in keys:
        if k in d and d[k] is not None:
            s = str(d[k]).strip()
            if s:
                return s
    return None


def _get_int(d: dict[str, Any], key: str, default: int) -> int:
    v = d.get(key)
    if v is None or (isinstance(v, str) and not v.strip()):
        return int(default)
    try:
        return int(v)
    except Exception as e:
        raise RuntimeError(f"Invalid int for {key}: {v}") from e


def _get_float(d: dict[str, Any], key: str, default: float) -> float:
    v = d.get(key)
    if v is None or (isinstance(v, str) and not v.strip()):
        return float(default)
    try:
        return float(v)
    except Exception as e:
        raise RuntimeError(f"Invalid float for {key}: {v}") from e


def _run_ads_reports_run(job: JobRow, ctx: dict[str, Any], *, out_dir: str) -> dict[str, Any]:
    _require_apply_yes_ack_volume(ctx, reason="ads.reports.run")

    ad_account_id = _get_str(job.data, "ad_account_id", "ad-account-id")
    body_file = _get_str(job.data, "body_file", "body-file")
    if not ad_account_id:
        raise RuntimeError("ads.reports.run missing ad_account_id")
    if not body_file:
        raise RuntimeError("ads.reports.run missing body_file")

    max_poll_attempts = _get_int(job.data, "max_poll_attempts", 60)
    max_poll_seconds = _get_float(job.data, "max_poll_seconds", 600.0)
    poll_interval_s = _get_float(job.data, "poll_interval_s", 10.0)
    max_download_bytes = _get_int(job.data, "max_download_bytes", 100 * 1024 * 1024)

    api = report_jobs.api_from_ctx(ctx)
    body = report_jobs.read_json_file(body_file)
    created = report_jobs.create_report_job(api, ad_account_id=ad_account_id, request_body=body)
    token = report_jobs.extract_report_token(created)
    if not token:
        raise RuntimeError("Report create response missing token")

    def _get(tok: str) -> dict[str, Any]:
        return report_jobs.get_report_job(api, ad_account_id=ad_account_id, token=tok)

    final = report_jobs.poll_report_status(
        _get,
        token=token,
        max_attempts=max_poll_attempts,
        max_seconds=max_poll_seconds,
        poll_interval_s=poll_interval_s,
    )
    status = report_jobs.extract_report_status(final) or "UNKNOWN"
    url = report_jobs.extract_report_url(final)
    if status != "FINISHED":
        return {
            "ok": False,
            "token": token,
            "report_status": status,
            "download_url": url,
            "download_path": None,
            **_no_snapshot_fields(action="ads.reports.run"),
        }
    if not url:
        return {
            "ok": False,
            "token": token,
            "report_status": status,
            "download_url": None,
            "download_path": None,
            "error": "Report finished but response did not include a download URL",
            **_no_snapshot_fields(action="ads.reports.run"),
        }

    fmt_hint = report_jobs.format_hint_from_url(url)
    filename = report_jobs.safe_filename_for_report(token, fmt_hint)
    download_path = str((Path(out_dir) / filename).resolve())
    dl = report_jobs.download_report(url, http=ctx["http"], dest_path=download_path, max_bytes=max_download_bytes)
    return {
        "ok": True,
        "token": token,
        "report_status": status,
        "download_url": url,
        "download_path": download_path,
        "download": dl,
        **_no_snapshot_fields(action="ads.reports.run"),
    }


def cmd_jobs_run(args: Any, ctx: dict[str, Any]) -> int:
    jobs = list(_iter_jobs(str(args.file)))
    limit = int(args.limit) if getattr(args, "limit", None) is not None else None
    if limit is not None and limit < 1:
        raise RuntimeError("--limit must be >= 1")
    if limit is not None:
        jobs = jobs[:limit]

    # Safety gates: refuse early if the batch contains any remote-write actions.
    remote_write_actions = {"ads.reports.run"}
    if any(j.action in remote_write_actions for j in jobs):
        _require_apply_yes_ack_volume(ctx, reason="batch jobs containing remote writes")

    out_dir = report_jobs.ensure_dir(str(args.out_dir))

    receipts: list[dict[str, Any]] = []
    errors = 0
    processed = 0

    for row_num, job in enumerate(jobs, start=1):
        processed += 1
        receipt_path = _receipt_path(out_dir, row_num)
        row_receipt: dict[str, Any] = {"row": row_num, "action": job.action, "input": job.data, "ok": False}
        try:
            if job.action == "ads.reports.run":
                result = _run_ads_reports_run(job, ctx, out_dir=out_dir)
                row_receipt["result"] = result
                row_receipt["ok"] = bool(result.get("ok"))
            else:
                raise RuntimeError(f"Unknown action: {job.action}")
        except Exception as e:  # noqa: BLE001
            errors += 1
            row_receipt["error"] = str(e)
            row_receipt["error_type"] = type(e).__name__
            _write_json_file(receipt_path, row_receipt)
            receipts.append({"row": row_num, "path": receipt_path, "ok": False})
            break

        _write_json_file(receipt_path, row_receipt)
        receipts.append({"row": row_num, "path": receipt_path, "ok": bool(row_receipt.get("ok"))})
        if not bool(row_receipt.get("ok")):
            errors += 1
            break

    summary_path = str((Path(out_dir) / "summary.json").resolve())
    summary: dict[str, Any] = {
        "ok": errors == 0,
        "apply": bool(ctx.get("apply")),
        "count": processed,
        "errors": errors,
        "receipts": receipts,
        "out_dir": out_dir,
        "summary_path": summary_path,
    }
    if any(j.action in remote_write_actions for j in jobs):
        summary.update(_no_snapshot_fields(action="jobs.run"))
    _write_json_file(summary_path, summary)

    ctx["audit"].write("jobs.run", {"count": processed, "errors": errors})
    ctx["out"].emit(summary)
    return 1 if errors else 0
