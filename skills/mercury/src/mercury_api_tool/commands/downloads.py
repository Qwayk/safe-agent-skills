from __future__ import annotations
import time
from pathlib import Path
from typing import Any

from ..context import build_mercury_client
from ..errors import SafetyError, ValidationError
from ..json_files import read_json_file, write_json_file


def _utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _resolve_out_path(*, out: str | None, out_dir: str | None, default_name: str, project_dir: Path) -> Path:
    if out:
        return Path(out).expanduser()
    base = Path(out_dir).expanduser() if out_dir else project_dir
    return base / default_name


def _refuse_overwrite(path: Path, *, yes: bool) -> None:
    if path.exists() and not yes:
        raise SafetyError(f"Refused: output file exists: {path} (re-run with --yes to overwrite)")


def _build_plan(*, ctx: dict[str, Any], action: str, files: list[dict[str, Any]], request: dict[str, Any]) -> dict[str, Any]:
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
        "baseline": {"env_fingerprint": cfg.base_url, "request": request},
        "files": files,
        "verification_plan": {"type": "local_files", "notes": "Verify files exist and sizes are > 0."},
        "rollback": {"supported": False, "notes": "Delete local files to rollback."},
    }


def _load_plan(plan_in: str) -> dict[str, Any]:
    plan_obj = read_json_file(plan_in)
    if not isinstance(plan_obj, dict):
        raise ValidationError("Plan file must be a JSON object")
    return plan_obj


def _get_plan_baseline_request(plan: dict[str, Any]) -> dict[str, Any]:
    baseline = plan.get("baseline")
    if not isinstance(baseline, dict):
        raise ValidationError("Plan missing baseline dict")
    request = baseline.get("request")
    if not isinstance(request, dict):
        raise ValidationError("Plan missing baseline.request dict")
    return request


def _get_plan_out_paths(plan: dict[str, Any]) -> list[str]:
    files = plan.get("files")
    if not isinstance(files, list):
        return []
    out_paths: list[str] = []
    for f in files:
        if not isinstance(f, dict):
            continue
        p = f.get("path")
        if isinstance(p, str) and p.strip():
            out_paths.append(p)
    return out_paths


def _get_plan_primary_out_path(plan: dict[str, Any]) -> str | None:
    paths = _get_plan_out_paths(plan)
    return paths[0] if paths else None


def _validate_plan_for_apply(
    plan: dict[str, Any],
    *,
    ctx: dict[str, Any],
    expected_action: str,
    expected_request: dict[str, Any],
    expected_out_path: Path,
) -> None:
    baseline = plan.get("baseline")
    if not isinstance(baseline, dict):
        raise ValidationError("Plan missing baseline dict")
    if str(baseline.get("env_fingerprint") or "") != str(ctx["cfg"].base_url):
        raise SafetyError("Refused: plan env_fingerprint does not match current environment")

    if str(plan.get("action") or "") != expected_action:
        raise SafetyError("Refused: plan action does not match current command")

    if _get_plan_baseline_request(plan) != expected_request:
        raise SafetyError("Refused: plan request does not match current arguments")

    planned_out = _get_plan_primary_out_path(plan)
    if str(planned_out or "") != str(expected_out_path):
        raise SafetyError("Refused: plan output path does not match current arguments")


def cmd_download_statement_pdf(args: Any, ctx: dict[str, Any]) -> int:
    statement_id = str(getattr(args, "statement_id", "") or "").strip()
    if not statement_id:
        raise ValidationError("Missing --statement-id")

    plan_in = str(ctx.get("plan_in") or "").strip() or None
    plan = _load_plan(plan_in) if plan_in else None

    out_arg = str(getattr(args, "out", "") or "").strip() or None
    out_dir = str(getattr(args, "out_dir", "") or "").strip() or None
    if plan and not out_arg and not out_dir:
        planned_out = _get_plan_primary_out_path(plan)
        if not planned_out:
            raise ValidationError("Plan missing files[0].path")
        out_path = Path(planned_out)
    else:
        out_path = _resolve_out_path(
            out=out_arg,
            out_dir=out_dir,
            default_name=f"statement_{statement_id}.pdf",
            project_dir=Path(ctx["project_dir"]),
        )

    if not plan:
        plan = _build_plan(
            ctx=ctx,
            action="statements.download_pdf",
            request={"statement_id": statement_id},
            files=[{"path": str(out_path), "kind": "pdf", "source": f"/statements/{statement_id}/pdf"}],
        )

    plan_out = ctx.get("plan_out")
    plan_path = write_json_file(plan_out, plan) if plan_out else None

    if not bool(ctx.get("apply")):
        out = {"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path}
        ctx["audit"].write("statements.download_pdf.plan", {"statement_id": statement_id, "plan_out": plan_path})
        ctx["out"].emit(out)
        return 0

    _validate_plan_for_apply(
        plan,
        ctx=ctx,
        expected_action="statements.download_pdf",
        expected_request={"statement_id": statement_id},
        expected_out_path=out_path,
    )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    _refuse_overwrite(out_path, yes=bool(ctx.get("yes")))

    client = build_mercury_client(ctx)
    pdf_bytes = client.get_pdf(f"/statements/{statement_id}/pdf")
    out_path.write_bytes(pdf_bytes)

    receipt = {
        "tool": ctx.get("tool") or "mercury-api-tool",
        "version": ctx.get("tool_version") or None,
        "applied_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "action": "statements.download_pdf",
        "changed": True,
        "files_written": [{"path": str(out_path), "bytes": out_path.stat().st_size}],
        "verification": {"ok": out_path.exists() and out_path.stat().st_size > 0},
        "backups": [],
        "rollback_plan": {"supported": False, "notes": "Delete the local file to rollback."},
    }
    receipt_out = ctx.get("receipt_out")
    receipt_path = write_json_file(receipt_out, receipt) if receipt_out else None

    out = {"ok": True, "dry_run": False, "receipt": receipt, "receipt_out": receipt_path}
    ctx["audit"].write(
        "statements.download_pdf.apply",
        {"statement_id": statement_id, "out": str(out_path), "bytes": receipt["files_written"][0]["bytes"]},
    )
    ctx["out"].emit(out)
    return 0


def cmd_download_invoice_pdf(args: Any, ctx: dict[str, Any]) -> int:
    invoice_id = str(getattr(args, "invoice_id", "") or "").strip()
    if not invoice_id:
        raise ValidationError("Missing --invoice-id")

    plan_in = str(ctx.get("plan_in") or "").strip() or None
    plan = _load_plan(plan_in) if plan_in else None

    out_arg = str(getattr(args, "out", "") or "").strip() or None
    out_dir = str(getattr(args, "out_dir", "") or "").strip() or None
    if plan and not out_arg and not out_dir:
        planned_out = _get_plan_primary_out_path(plan)
        if not planned_out:
            raise ValidationError("Plan missing files[0].path")
        out_path = Path(planned_out)
    else:
        out_path = _resolve_out_path(
            out=out_arg,
            out_dir=out_dir,
            default_name=f"invoice_{invoice_id}.pdf",
            project_dir=Path(ctx["project_dir"]),
        )

    if not plan:
        plan = _build_plan(
            ctx=ctx,
            action="invoices.download_pdf",
            request={"invoice_id": invoice_id},
            files=[{"path": str(out_path), "kind": "pdf", "source": f"/ar/invoices/{invoice_id}/pdf"}],
        )

    plan_out = ctx.get("plan_out")
    plan_path = write_json_file(plan_out, plan) if plan_out else None

    if not bool(ctx.get("apply")):
        out = {"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path}
        ctx["audit"].write("invoices.download_pdf.plan", {"invoice_id": invoice_id, "plan_out": plan_path})
        ctx["out"].emit(out)
        return 0

    _validate_plan_for_apply(
        plan,
        ctx=ctx,
        expected_action="invoices.download_pdf",
        expected_request={"invoice_id": invoice_id},
        expected_out_path=out_path,
    )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    _refuse_overwrite(out_path, yes=bool(ctx.get("yes")))

    client = build_mercury_client(ctx)
    pdf_bytes = client.get_pdf(f"/ar/invoices/{invoice_id}/pdf")
    out_path.write_bytes(pdf_bytes)

    receipt = {
        "tool": ctx.get("tool") or "mercury-api-tool",
        "version": ctx.get("tool_version") or None,
        "applied_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "action": "invoices.download_pdf",
        "changed": True,
        "files_written": [{"path": str(out_path), "bytes": out_path.stat().st_size}],
        "verification": {"ok": out_path.exists() and out_path.stat().st_size > 0},
        "backups": [],
        "rollback_plan": {"supported": False, "notes": "Delete the local file to rollback."},
    }
    receipt_out = ctx.get("receipt_out")
    receipt_path = write_json_file(receipt_out, receipt) if receipt_out else None

    out = {"ok": True, "dry_run": False, "receipt": receipt, "receipt_out": receipt_path}
    ctx["audit"].write(
        "invoices.download_pdf.apply",
        {"invoice_id": invoice_id, "out": str(out_path), "bytes": receipt["files_written"][0]["bytes"]},
    )
    ctx["out"].emit(out)
    return 0


def cmd_download_invoice_attachment(args: Any, ctx: dict[str, Any]) -> int:
    attachment_id = str(getattr(args, "attachment_id", "") or "").strip()
    if not attachment_id:
        raise ValidationError("Missing --attachment-id")

    plan_in = str(ctx.get("plan_in") or "").strip() or None
    plan = _load_plan(plan_in) if plan_in else None

    out_arg = str(getattr(args, "out", "") or "").strip() or None
    out_dir = str(getattr(args, "out_dir", "") or "").strip() or None

    planned_req: dict[str, Any] | None = None
    if plan:
        planned_req = _get_plan_baseline_request(plan)

    file_name = str(getattr(args, "file_name", "") or "").strip() or None
    if not file_name and planned_req:
        planned_file_name = planned_req.get("file_name")
        if isinstance(planned_file_name, str) and planned_file_name.strip():
            file_name = planned_file_name.strip()
        else:
            raise ValidationError("Plan missing baseline.request.file_name (re-create the plan)")

    api_file_name: str | None = None
    url: str | None = None
    if not file_name:
        client = build_mercury_client(ctx)
        attachment = client.get_json(f"/ar/attachments/{attachment_id}")
        if not isinstance(attachment, dict):
            raise RuntimeError("Unexpected attachment response (expected JSON object)")
        url_val = attachment.get("url")
        api_file_name_val = attachment.get("fileName")
        if not isinstance(url_val, str) or not url_val:
            raise RuntimeError("Attachment response missing url")
        api_file_name = str(api_file_name_val or "").strip() or None
        url = url_val
        file_name = api_file_name or f"attachment_{attachment_id}"

    if plan and not out_arg and not out_dir:
        planned_out = _get_plan_primary_out_path(plan)
        if not planned_out:
            raise ValidationError("Plan missing files[0].path")
        out_path = Path(planned_out)
    else:
        out_path = _resolve_out_path(
            out=out_arg,
            out_dir=out_dir,
            default_name=str(file_name),
            project_dir=Path(ctx["project_dir"]),
        )

    expected_request = {
        "attachment_id": attachment_id,
        "file_name": str(file_name),
        "source_endpoint": f"/ar/attachments/{attachment_id}",
    }

    if not plan:
        plan = _build_plan(
            ctx=ctx,
            action="invoices.attachments.download",
            request=expected_request,
            files=[
                {
                    "path": str(out_path),
                    "kind": "binary",
                    "source": {
                        "type": "mercury_attachment",
                        "endpoint": f"/ar/attachments/{attachment_id}",
                        "attachment_id": attachment_id,
                        "url_redacted": True,
                    },
                }
            ],
        )

    plan_out = ctx.get("plan_out")
    plan_path = write_json_file(plan_out, plan) if plan_out else None

    if not bool(ctx.get("apply")):
        out = {
            "ok": True,
            "dry_run": True,
            "plan": plan,
            "plan_out": plan_path,
            "attachment": {"id": attachment_id, "fileName": api_file_name, "url_redacted": True},
        }
        ctx["audit"].write(
            "invoices.attachments.download.plan",
            {"attachment_id": attachment_id, "file_name": file_name, "out": str(out_path), "plan_out": plan_path},
        )
        ctx["out"].emit(out)
        return 0

    _validate_plan_for_apply(
        plan,
        ctx=ctx,
        expected_action="invoices.attachments.download",
        expected_request=expected_request,
        expected_out_path=out_path,
    )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    _refuse_overwrite(out_path, yes=bool(ctx.get("yes")))

    client = build_mercury_client(ctx)
    if url is None:
        attachment = client.get_json(f"/ar/attachments/{attachment_id}")
        if not isinstance(attachment, dict):
            raise RuntimeError("Unexpected attachment response (expected JSON object)")
        url_val = attachment.get("url")
        api_file_name_val = attachment.get("fileName")
        if isinstance(api_file_name_val, str) and api_file_name_val.strip():
            api_file_name = api_file_name_val.strip()
        if not isinstance(url_val, str) or not url_val:
            raise RuntimeError("Attachment response missing url")
        url = url_val

    blob = client.get_bytes_from_url(str(url))
    out_path.write_bytes(blob)

    receipt = {
        "tool": ctx.get("tool") or "mercury-api-tool",
        "version": ctx.get("tool_version") or None,
        "applied_at_utc": _utc_now(),
        "env_fingerprint": ctx["cfg"].base_url,
        "action": "invoices.attachments.download",
        "changed": True,
        "files_written": [{"path": str(out_path), "bytes": out_path.stat().st_size}],
        "verification": {"ok": out_path.exists() and out_path.stat().st_size > 0},
        "backups": [],
        "rollback_plan": {"supported": False, "notes": "Delete the local file to rollback."},
    }
    receipt_out = ctx.get("receipt_out")
    receipt_path = write_json_file(receipt_out, receipt) if receipt_out else None

    out = {
        "ok": True,
        "dry_run": False,
        "receipt": receipt,
        "receipt_out": receipt_path,
        "attachment": {"id": attachment_id, "fileName": api_file_name, "url_redacted": True},
    }
    ctx["audit"].write(
        "invoices.attachments.download.apply",
        {"attachment_id": attachment_id, "out": str(out_path), "bytes": receipt["files_written"][0]["bytes"]},
    )
    ctx["out"].emit(out)
    return 0
