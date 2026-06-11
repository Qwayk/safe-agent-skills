from __future__ import annotations

from pathlib import Path
from typing import Any

from ..errors import SafetyError, ValidationError
from ..snapshot.analyze import AnalyzeArgs, run_snapshot_analyze_optimize
from ..snapshot.compare import CompareArgs, run_compare
from ..snapshot.diagnose import DiagnoseArgs, run_snapshot_analyze_diagnose
from ..snapshot.exporter import ExportArgs, run_snapshot_export


def cmd_snapshot_export(args: Any, ctx: dict[str, Any]) -> int:
    if getattr(args, "plan_in", None):
        raise ValidationError("--plan-in is not supported for snapshot export")

    preset = str(getattr(args, "preset", "") or "").strip()
    customer_id = str(getattr(args, "customer_id", "") or "").strip()
    since = str(getattr(args, "since", "") or "").strip()
    until = str(getattr(args, "until", "") or "").strip()
    out_dir = Path(str(getattr(args, "out_dir", "") or "").strip())
    overwrite = bool(getattr(args, "overwrite", False))
    strict = bool(getattr(args, "strict", False))
    segmentation = str(getattr(args, "segmentation", "") or "base").strip()
    include_optional = bool(getattr(args, "include_optional", False))

    try:
        page_size = int(getattr(args, "page_size", 1000))
    except Exception:
        raise ValidationError("--page-size must be an integer") from None
    max_rows_raw = getattr(args, "max_rows", None)
    max_rows: int | None
    if max_rows_raw is None:
        max_rows = None
    else:
        try:
            max_rows = int(max_rows_raw)
        except Exception:
            raise ValidationError("--max-rows must be an integer") from None

    apply = bool(getattr(args, "apply", False))
    yes = bool(getattr(args, "yes", False))

    export_args = ExportArgs(
        preset=preset,
        customer_id=customer_id,
        since=since,
        until=until,
        out_dir=out_dir,
        overwrite=overwrite,
        strict=strict,
        segmentation=segmentation,
        page_size=page_size,
        max_rows=max_rows,
        include_optional=include_optional,
    )

    if apply and not yes:
        raise SafetyError("Snapshot export is a batch action; pass --yes to proceed.")

    rc, payload = run_snapshot_export(
        a=export_args,
        apply=apply,
        yes=yes,
        strict=strict,
        tool_version=str(ctx.get("tool_version") or ""),
        env_file=str(ctx.get("env_file") or ".env"),
        timeout_s_override=ctx.get("timeout_s"),
        plan_out=ctx.get("plan_out"),
        receipt_out=ctx.get("receipt_out"),
        artifacts_dir=ctx.get("artifacts_dir"),
        audit_write=ctx["audit"].write,
        secret_values=None,
    )
    ctx["out"].emit(payload)
    return int(rc)


def cmd_snapshot_compare(args: Any, ctx: dict[str, Any]) -> int:
    if getattr(args, "plan_in", None):
        raise ValidationError("--plan-in is not supported for snapshot compare")

    pack_a = Path(str(getattr(args, "pack_a", "") or "").strip())
    pack_b = Path(str(getattr(args, "pack_b", "") or "").strip())
    out_dir = Path(str(getattr(args, "out_dir", "") or "").strip())
    overwrite = bool(getattr(args, "overwrite", False))

    apply = bool(getattr(args, "apply", False))
    cmp_args = CompareArgs(pack_a=pack_a, pack_b=pack_b, out_dir=out_dir, overwrite=overwrite)
    rc, payload = run_compare(a=cmp_args, apply=apply)
    ctx["audit"].write("snapshot_compare", {"ok": bool(payload.get("ok")), "dry_run": bool(payload.get("dry_run"))})
    ctx["out"].emit(payload)
    return int(rc)


def cmd_snapshot_analyze_optimize(args: Any, ctx: dict[str, Any]) -> int:
    if getattr(args, "plan_in", None):
        raise ValidationError("--plan-in is not supported for snapshot analysis")

    pack_dir = Path(str(getattr(args, "pack_dir", "") or "").strip())
    top_n = int(getattr(args, "top_n", 50) or 50)
    min_cost = int(getattr(args, "min_negative_cost_micros", 5000000) or 5000000)
    min_clicks = int(getattr(args, "min_negative_clicks", 3) or 3)
    min_impr = int(getattr(args, "min_negative_impressions", 100) or 100)

    if top_n < 0 or top_n > 1000:
        raise ValidationError("--top-n must be between 0 and 1000")
    if min_cost < 0:
        raise ValidationError("--min-negative-cost-micros must be >= 0")
    if min_clicks < 0:
        raise ValidationError("--min-negative-clicks must be >= 0")
    if min_impr < 0:
        raise ValidationError("--min-negative-impressions must be >= 0")

    a = AnalyzeArgs(
        pack_dir=pack_dir,
        top_n=top_n,
        min_negative_cost_micros=min_cost,
        min_negative_clicks=min_clicks,
        min_negative_impressions=min_impr,
    )
    payload = run_snapshot_analyze_optimize(a)
    ctx["audit"].write("snapshot_analyze_optimize", {"ok": True})
    ctx["out"].emit(payload)
    return 0


def cmd_snapshot_analyze_diagnose(args: Any, ctx: dict[str, Any]) -> int:
    if getattr(args, "plan_in", None):
        raise ValidationError("--plan-in is not supported for snapshot analysis")

    pack_dir = Path(str(getattr(args, "pack_dir", "") or "").strip())
    payload = run_snapshot_analyze_diagnose(DiagnoseArgs(pack_dir=pack_dir))
    ctx["audit"].write("snapshot_analyze_diagnose", {"ok": True})
    ctx["out"].emit(payload)
    return 0
