from __future__ import annotations

import csv
import json
import time
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from ..context import build_mercury_client
from ..errors import SafetyError, ValidationError
from ..json_files import read_json_file, write_json_file


def _utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _clean_params(params: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for k, v in params.items():
        if v is None:
            continue
        if isinstance(v, list):
            vv = [x for x in v if x is not None and str(x).strip() != ""]
            if not vv:
                continue
            out[k] = vv
            continue
        if isinstance(v, str) and not v.strip():
            continue
        out[k] = v
    return out


def _resolve_out_path(*, out: str | None, out_dir: str | None, default_name: str, project_dir: Path) -> Path:
    if out:
        return Path(out).expanduser()
    base = Path(out_dir).expanduser() if out_dir else project_dir
    return base / default_name


def _refuse_overwrite(path: Path, *, yes: bool) -> None:
    if path.exists() and not yes:
        raise SafetyError(f"Refused: output file exists: {path} (re-run with --yes to overwrite)")


def _build_plan(*, ctx: dict[str, Any], action: str, out_file: Path, request: dict[str, Any]) -> dict[str, Any]:
    cfg = ctx["cfg"]
    return {
        "tool": ctx.get("tool") or "mercury-api-tool",
        "version": ctx.get("tool_version") or None,
        "generated_at_utc": _utc_now(),
        "env_fingerprint": cfg.base_url,
        "command": ctx.get("command_str") or None,
        "action": action,
        "risk_level": "low",
        "risk_reasons": ["local_file_write"],
        "baseline": {"env_fingerprint": cfg.base_url, "request": request, "out": str(out_file)},
        "files": [{"path": str(out_file), "kind": "export"}],
        "verification_plan": {"type": "local_files", "notes": "Verify file exists and is non-empty."},
        "rollback": {"supported": False, "notes": "Delete local files to rollback."},
    }


def _load_plan(plan_in: str) -> dict[str, Any]:
    plan_obj = read_json_file(plan_in)
    if not isinstance(plan_obj, dict):
        raise ValidationError("Plan file must be a JSON object")
    return plan_obj


def _get_plan_baseline(plan: dict[str, Any]) -> dict[str, Any]:
    baseline = plan.get("baseline")
    if not isinstance(baseline, dict):
        raise ValidationError("Plan missing baseline dict")
    return baseline


def _get_plan_primary_out_path(plan: dict[str, Any]) -> str | None:
    baseline = plan.get("baseline")
    if isinstance(baseline, dict):
        out = baseline.get("out")
        if isinstance(out, str) and out.strip():
            return out.strip()
    files = plan.get("files")
    if isinstance(files, list) and files:
        first = files[0]
        if isinstance(first, dict):
            p = first.get("path")
            if isinstance(p, str) and p.strip():
                return p.strip()
    return None


def _validate_plan_for_apply(
    plan: dict[str, Any],
    *,
    ctx: dict[str, Any],
    expected_action: str,
    expected_request: dict[str, Any],
    expected_out_path: Path,
) -> None:
    baseline = _get_plan_baseline(plan)
    if str(baseline.get("env_fingerprint") or "") != str(ctx["cfg"].base_url):
        raise SafetyError("Refused: plan env_fingerprint does not match current environment")

    if str(plan.get("action") or "") != expected_action:
        raise SafetyError("Refused: plan action does not match current command")

    request = baseline.get("request")
    if not isinstance(request, dict):
        raise ValidationError("Plan missing baseline.request dict")
    if request != expected_request:
        raise SafetyError("Refused: plan request does not match current arguments")

    planned_out = _get_plan_primary_out_path(plan)
    if str(planned_out or "") != str(expected_out_path):
        raise SafetyError("Refused: plan output path does not match current arguments")


@dataclass(frozen=True)
class _TransactionsPage:
    transactions: list[dict[str, Any]]
    next_page: str | None


def _extract_transactions_page(obj: Any) -> _TransactionsPage:
    if not isinstance(obj, dict):
        raise RuntimeError("Unexpected transactions response (expected JSON object)")
    txns = obj.get("transactions")
    if not isinstance(txns, list):
        raise RuntimeError("Unexpected transactions response: missing transactions[]")
    txns_dicts: list[dict[str, Any]] = [t for t in txns if isinstance(t, dict)]
    page = obj.get("page")
    next_page = None
    if isinstance(page, dict):
        np = page.get("nextPage")
        if isinstance(np, str) and np.strip():
            next_page = np.strip()
    return _TransactionsPage(transactions=txns_dicts, next_page=next_page)


def _iter_transactions(
    *,
    client,
    params: dict[str, Any],
    max_pages: int,
) -> Iterable[dict[str, Any]]:
    seen_pages = 0
    next_page: str | None = None
    current_params = dict(params)
    while True:
        if next_page:
            current_params["start_after"] = next_page
        obj = client.get_json("/transactions", params=current_params)
        page = _extract_transactions_page(obj)
        for t in page.transactions:
            yield t
        seen_pages += 1
        if seen_pages >= max_pages:
            return
        if not page.next_page:
            return
        next_page = page.next_page


def _write_transactions_csv(path: Path, txns: list[dict[str, Any]]) -> None:
    fields = [
        "id",
        "accountId",
        "amount",
        "createdAt",
        "postedAt",
        "status",
        "kind",
        "counterpartyName",
        "mercuryCategory",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for t in txns:
            w.writerow({k: t.get(k) for k in fields})


def cmd_export_transactions(args: Any, ctx: dict[str, Any]) -> int:
    fmt = str(getattr(args, "format", "json") or "json").strip().lower()
    if fmt not in {"json", "csv"}:
        raise ValidationError("--format must be json or csv")

    params = _clean_params(
        {
            "status": getattr(args, "status", None),
            "search": getattr(args, "search", None),
            "start": getattr(args, "start", None),
            "end": getattr(args, "end", None),
            "postedStart": getattr(args, "posted_start", None),
            "postedEnd": getattr(args, "posted_end", None),
            "accountId": getattr(args, "account_id", None),
            "mercuryCategory": getattr(args, "mercury_category", None),
            "categoryId": getattr(args, "category_id", None),
            "start_at": getattr(args, "start_at", None),
            "start_after": getattr(args, "start_after", None),
            "end_before": getattr(args, "end_before", None),
            "limit": getattr(args, "limit", None),
            "order": getattr(args, "order", None),
        }
    )

    max_pages = int(getattr(args, "max_pages", 10) or 10)
    if max_pages <= 0:
        raise ValidationError("--max-pages must be > 0")

    plan_in = str(ctx.get("plan_in") or "").strip() or None
    plan = _load_plan(plan_in) if plan_in else None

    out_arg = str(getattr(args, "out", "") or "").strip() or None
    out_dir = str(getattr(args, "out_dir", "") or "").strip() or None
    if plan and not out_arg and not out_dir:
        planned_out = _get_plan_primary_out_path(plan)
        if not planned_out:
            raise ValidationError("Plan missing baseline.out (or files[0].path)")
        out_path = Path(planned_out)
    else:
        out_path = _resolve_out_path(
            out=out_arg,
            out_dir=out_dir,
            default_name=f"transactions_export_{time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())}.{fmt}",
            project_dir=Path(ctx["project_dir"]),
        )

    expected_request = {"format": fmt, "params": params, "max_pages": max_pages}

    if not plan:
        plan = _build_plan(
            ctx=ctx,
            action="transactions.export",
            out_file=out_path,
            request=expected_request,
        )

    plan_out = ctx.get("plan_out")
    plan_path = write_json_file(plan_out, plan) if plan_out else None

    if not bool(ctx.get("apply")):
        out = {"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path}
        ctx["audit"].write(
            "transactions.export.plan",
            {"format": fmt, "out": str(out_path), "plan_out": plan_path, "max_pages": max_pages},
        )
        ctx["out"].emit(out)
        return 0

    _validate_plan_for_apply(
        plan,
        ctx=ctx,
        expected_action="transactions.export",
        expected_request=expected_request,
        expected_out_path=out_path,
    )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    _refuse_overwrite(out_path, yes=bool(ctx.get("yes")))

    client = build_mercury_client(ctx)
    txns = list(_iter_transactions(client=client, params=params, max_pages=max_pages))

    if fmt == "json":
        out_path.write_text(
            json.dumps(txns, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    else:
        _write_transactions_csv(out_path, txns)

    receipt = {
        "tool": ctx.get("tool") or "mercury-api-tool",
        "version": ctx.get("tool_version") or None,
        "applied_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "action": "transactions.export",
        "changed": True,
        "files_written": [{"path": str(out_path), "bytes": out_path.stat().st_size}],
        "counts": {"transactions": len(txns)},
        "verification": {"ok": out_path.exists() and out_path.stat().st_size > 0},
        "backups": [],
        "rollback_plan": {"supported": False, "notes": "Delete local files to rollback."},
    }
    receipt_out = ctx.get("receipt_out")
    receipt_path = write_json_file(receipt_out, receipt) if receipt_out else None

    out = {"ok": True, "dry_run": False, "receipt": receipt, "receipt_out": receipt_path}
    ctx["audit"].write(
        "transactions.export.apply",
        {
            "format": fmt,
            "out": str(out_path),
            "count": len(txns),
            "bytes": receipt["files_written"][0]["bytes"],
            "max_pages": max_pages,
        },
    )
    ctx["out"].emit(out)
    return 0


def cmd_report_transactions_summary(args: Any, ctx: dict[str, Any]) -> int:
    params = _clean_params(
        {
            "status": getattr(args, "status", None),
            "search": getattr(args, "search", None),
            "start": getattr(args, "start", None),
            "end": getattr(args, "end", None),
            "postedStart": getattr(args, "posted_start", None),
            "postedEnd": getattr(args, "posted_end", None),
            "accountId": getattr(args, "account_id", None),
            "mercuryCategory": getattr(args, "mercury_category", None),
            "categoryId": getattr(args, "category_id", None),
            "start_at": getattr(args, "start_at", None),
            "start_after": getattr(args, "start_after", None),
            "end_before": getattr(args, "end_before", None),
            "limit": getattr(args, "limit", None),
            "order": getattr(args, "order", None),
        }
    )

    max_pages = int(getattr(args, "max_pages", 10) or 10)
    if max_pages <= 0:
        raise ValidationError("--max-pages must be > 0")

    client = build_mercury_client(ctx)
    txns = list(_iter_transactions(client=client, params=params, max_pages=max_pages))

    by_kind: dict[str, dict[str, Any]] = defaultdict(lambda: {"count": 0, "amount_sum": 0.0})
    by_mercury_category: dict[str, dict[str, Any]] = defaultdict(lambda: {"count": 0, "amount_sum": 0.0})

    for t in txns:
        kind = str(t.get("kind") or "<unknown>")
        cat = str(t.get("mercuryCategory") or "<none>")
        amt = t.get("amount")
        try:
            amount = float(amt) if amt is not None else 0.0
        except Exception:
            amount = 0.0
        by_kind[kind]["count"] += 1
        by_kind[kind]["amount_sum"] += amount
        by_mercury_category[cat]["count"] += 1
        by_mercury_category[cat]["amount_sum"] += amount

    out = {
        "ok": True,
        "report": {
            "type": "transactions_summary",
            "generated_at_utc": _utc_now(),
            "filters": params,
            "max_pages": max_pages,
            "counts": {"transactions": len(txns)},
            "by_kind": dict(sorted(by_kind.items())),
            "by_mercury_category": dict(sorted(by_mercury_category.items())),
        },
    }
    ctx["audit"].write("transactions.report.summary", {"filters": params, "count": len(txns), "max_pages": max_pages})
    ctx["out"].emit(out)
    return 0
