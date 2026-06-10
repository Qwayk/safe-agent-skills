from __future__ import annotations

import asyncio
import errno
import time
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

from ..errors import SafetyError, ToolError, ValidationError
from ..plan_and_receipt import resolve_safe_out_path, sha256_of_file
from ._storage_db_common import (
    base_plan,
    base_receipt,
    emit_plan,
    emit_receipt,
    require_apply,
    require_token,
    require_yes,
    resolve_account_id,
    verify_and_require_plan,
)


def _append_redaction_secret(ctx: dict, secret: str) -> None:
    secrets = ctx.get("redaction_secrets")
    if not isinstance(secrets, list):
        return
    s = str(secret or "")
    if s and s not in secrets:
        secrets.append(s)


def _append_ws_url_redactions(ctx: dict, url: str) -> None:
    u = str(url or "").strip()
    if not u:
        return
    _append_redaction_secret(ctx, u)
    try:
        parsed = urlparse(u)
        qs = parse_qs(parsed.query or "")
        for values in qs.values():
            for v in values:
                _append_redaction_secret(ctx, str(v))
    except Exception:
        return


def _ws_exception_summary(exc: BaseException) -> str:
    name = type(exc).__name__

    status = getattr(exc, "status_code", None)
    if isinstance(status, int) and status > 0:
        return f"{name} (status_code={status})"

    errno_val = getattr(exc, "errno", None)
    if isinstance(errno_val, int):
        try:
            errno_name = errno.errorcode.get(errno_val)
        except Exception:
            errno_name = None
        if errno_name:
            return f"{name} (errno={errno_name})"
        return f"{name} (errno={errno_val})"

    return name


async def _stream_ws_to_file(*, url: str, duration_s: float, fp) -> dict[str, Any]:  # noqa: ANN001
    try:
        import websockets  # type: ignore
    except Exception as e:  # noqa: BLE001
        raise ToolError(f"Missing dependency: websockets ({type(e).__name__})") from None

    conn_closed_exc = None
    try:
        conn_closed_exc = getattr(getattr(websockets, "exceptions", None), "ConnectionClosed", None)
    except Exception:
        conn_closed_exc = None

    start = time.monotonic()
    messages = 0
    bytes_written = 0
    stop_reason = "duration_elapsed"

    # Cloudflare tail WebSocket can reject extension negotiation; disable compression. Also request
    # the expected subprotocol to avoid handshake failures (some endpoints return HTTP 406
    # otherwise).
    async with websockets.connect(  # type: ignore[attr-defined]
        url,
        close_timeout=1,
        compression=None,
        subprotocols=["trace-v1"],
    ) as ws:
        while True:
            remaining = float(duration_s) - (time.monotonic() - start)
            if remaining <= 0:
                stop_reason = "duration_elapsed"
                break
            try:
                msg = await asyncio.wait_for(ws.recv(), timeout=remaining)
            except asyncio.TimeoutError:
                stop_reason = "duration_elapsed"
                break
            except Exception as e:  # noqa: BLE001
                if conn_closed_exc is None or isinstance(e, conn_closed_exc):
                    stop_reason = "socket_closed"
                    break
                raise
            if msg is None:
                stop_reason = "socket_closed"
                break
            if isinstance(msg, bytes):
                s = msg.decode("utf-8", errors="replace")
            else:
                s = str(msg)

            # Guarantee one line per message to keep the file stream-friendly.
            s = s.replace("\r\n", "\n").replace("\r", "\n").replace("\n", "\\n")
            data = (s + "\n").encode("utf-8", errors="replace")
            fp.write(data)
            messages += 1
            bytes_written += len(data)

    return {
        "messages": messages,
        "bytes_written": bytes_written,
        "elapsed_s": time.monotonic() - start,
        "stop_reason": stop_reason,
    }


def cmd_workers_tails_stream(args, ctx) -> int:
    """
    Stream Worker tail logs to a local file (PII-risk; file-only output).

    Dry-run emits a deterministic plan. Apply requires --apply --yes and writes events to --out.
    """
    require_token(ctx)
    account_id = resolve_account_id(args, ctx)
    script_name = str(getattr(args, "script_name", "") or "").strip()
    out_path = str(getattr(args, "out", "") or "").strip()
    overwrite = bool(getattr(args, "overwrite", False))
    duration_s = getattr(args, "duration_s", 60)

    if not script_name:
        raise ValidationError("Missing --script-name")
    if not out_path:
        raise ValidationError("Missing --out")
    try:
        duration_s_f = float(duration_s)
    except Exception:
        raise ValidationError("--duration-s must be a number") from None
    if duration_s_f <= 0:
        raise ValidationError("--duration-s must be > 0")

    safe = resolve_safe_out_path(project_dir=Path(ctx["project_dir"]), out_path=out_path, allow_overwrite=overwrite)

    selector = {
        "account_id": account_id,
        "script_name": script_name,
        "duration_s": duration_s_f,
        "out": out_path,
        "overwrite": overwrite,
    }
    plan = base_plan(
        ctx,
        selector=selector,
        risk_level="high",
        risk_reasons=[
            "This operation starts and deletes a tail (Cloudflare API write).",
            "This operation writes tail events to a local file (may contain PII).",
            "The Start Tail API returns a secret-bearing WebSocket URL; it must not be printed.",
        ],
    )
    plan["request"] = {
        "start_tail": {
            "method": "POST",
            "path": f"/accounts/{account_id}/workers/scripts/{script_name}/tails",
            "sensitivity": "sensitive_write_result",
        },
        "delete_tail": {
            "method": "DELETE",
            "path_template": f"/accounts/{account_id}/workers/scripts/{script_name}/tails/{{id}}",
        },
        "stream": {"duration_s": duration_s_f},
        "out": safe.rel_to_project,
    }
    plan["proposed_changes"] = [
        {"resource": "workers_tail", "action": "start", "account_id": account_id, "script_name": script_name},
        {"resource": "local_file", "action": "write", "path": safe.rel_to_project, "reason": "workers_tails_stream"},
        {"resource": "workers_tail", "action": "delete", "account_id": account_id, "script_name": script_name},
    ]
    plan["verification_plan"] = [
        "Confirm output file exists and record size/sha256 locally.",
        "Best-effort cleanup: attempt DELETE tail id in finally (even on errors).",
    ]
    plan["notes"].append("Tail event contents are never printed to stdout/stderr; they are written only to the output file.")

    if not bool(ctx.get("apply")):
        return emit_plan(ctx, command="workers.tails.stream", plan=plan)

    require_apply(ctx)
    require_yes(ctx)
    verify_and_require_plan(ctx, plan=plan)

    tail_id: str | None = None
    cleanup_attempted = False
    cleanup_ok: bool | None = None
    stream_meta: dict[str, Any] = {"messages": 0, "bytes_written": 0, "elapsed_s": 0.0, "stop_reason": "not_started"}
    file_sha256: str | None = None

    safe.abs_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        start_res = ctx["cf"].post_json(f"/accounts/{account_id}/workers/scripts/{script_name}/tails", json_body=None)
        if not isinstance(start_res.result, dict):
            raise ToolError("Start tail: unexpected API response shape (missing result object).")
        tail_id = str(start_res.result.get("id") or "").strip() or None
        ws_url = str(start_res.result.get("url") or "").strip()
        if not tail_id:
            raise ToolError("Start tail: missing tail id in response.")
        if not ws_url:
            raise ToolError("Start tail: missing WebSocket url in response.")

        _append_ws_url_redactions(ctx, ws_url)

        file_mode = "wb" if overwrite else "xb"
        with open(safe.abs_path, file_mode) as fp:
            try:
                stream_meta = asyncio.run(_stream_ws_to_file(url=ws_url, duration_s=duration_s_f, fp=fp))
            except KeyboardInterrupt:
                stream_meta = {**stream_meta, "stop_reason": "interrupted"}
                raise
            except Exception as e:  # noqa: BLE001
                raise ToolError(f"WebSocket streaming failed ({_ws_exception_summary(e)}).") from None
    finally:
        if tail_id:
            cleanup_attempted = True
            try:
                resp = ctx["cf"].request_raw_allow_errors(
                    "DELETE",
                    f"/accounts/{account_id}/workers/scripts/{script_name}/tails/{tail_id}",
                    retries=0,
                )
                cleanup_ok = bool(resp.status < 400)
            except Exception:
                cleanup_ok = False

        try:
            if safe.abs_path.exists():
                file_sha256 = sha256_of_file(safe.abs_path)
        except Exception:
            file_sha256 = None

    receipt = base_receipt(ctx, selector=selector, changed=False)
    receipt["diff_applied"] = [
        {"resource": "workers_tail", "action": "started", "tail_id": tail_id, "account_id": account_id, "script_name": script_name},
        {"resource": "workers_tail", "action": "deleted", "tail_id": tail_id, "account_id": account_id, "script_name": script_name, "ok": cleanup_ok},
    ]
    receipt["output_file"] = {
        "out_path": str(safe.abs_path),
        "out_rel": safe.rel_to_project,
        "size_bytes": safe.abs_path.stat().st_size if safe.abs_path.exists() else None,
        "sha256": file_sha256,
    }
    receipt["verification"] = {
        "ok": bool(cleanup_ok),
        "method": "cleanup_delete_tail",
        "details": {
            "cleanup_attempted": cleanup_attempted,
            "cleanup_ok": cleanup_ok,
            "stream": {"duration_s": duration_s_f, **stream_meta},
        },
    }

    return emit_receipt(
        ctx,
        command="workers.tails.stream",
        receipt=receipt,
        extra={
            "tail_id": tail_id,
            "out": safe.rel_to_project,
            "stream": {"duration_s": duration_s_f, **stream_meta},
            "cleanup": {"attempted": cleanup_attempted, "ok": cleanup_ok},
        },
    )
