from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any, BinaryIO

from ..errors import SafetyError, ToolError, ValidationError
from ..operations import Operation, OPERATIONS
from ..plans import (
    BEFORE_STATE_REFUSAL_REASON,
    build_receipt,
    build_before_state_refusal_verification_plan,
    default_verification,
    summarize_request,
    write_receipt_to_file,
)
from ._helpers import (
    ensure_json_output_file,
    ensure_output_file,
    plan_for_operation,
    plan_from_file_for_apply,
    write_binary_file,
    write_json_file,
)

READ_ONLY_METHODS = {"GET", "WEBSOCKET", "DOC"}
POST_READ_OVERRIDE = "post_read"


def register_operation_commands(
    subparsers: argparse._SubparsersAction,
    parser_class: type[argparse.ArgumentParser],
    *,
    skip_commands: set[str] | None = None,
    existing_subparsers: dict[tuple[str, ...], argparse._SubparsersAction] | None = None,
) -> None:
    nodes: dict[tuple[str, ...], argparse._SubparsersAction] = {(): subparsers}
    skip = {cmd.lower() for cmd in (skip_commands or ())}
    if existing_subparsers:
        for path, action in existing_subparsers.items():
            nodes[path] = action
    for op in sorted(OPERATIONS, key=lambda item: item.cli_command):
        tokens = op.cli_command.split()
        if op.cli_command.lower() in skip:
            continue
        parent_path: tuple[str, ...] = ()
        for token in tokens[:-1]:
            parent_path = parent_path + (token,)
            if parent_path not in nodes:
                parent = nodes[parent_path[:-1]]
                parser = parent.add_parser(token, help=f"{token} commands")
                child_subparsers = parser.add_subparsers(
                    dest=f"{'_'.join(parent_path)}_cmd",
                    required=True,
                    parser_class=parser_class,
                )
                nodes[parent_path] = child_subparsers
        parent = nodes[parent_path]
        parser = parent.add_parser(tokens[-1], help=op.description)
        parser.set_defaults(func=cmd_operation, operation=op, write_capable='write' in op.safety)
        configure_operation_parser(parser, op)


def configure_operation_parser(parser: argparse.ArgumentParser, op: Operation) -> None:
    placeholders = _extract_path_placeholders(op.path)
    for placeholder in placeholders:
        parser.add_argument(
            f"--{placeholder.replace('_', '-')}",
            required=True,
            dest=placeholder,
            help=f"Path parameter {placeholder}",
        )
    parser.add_argument("--param", action="append", default=[], help="Query parameter (key=value)")
    parser.add_argument("--body", help="JSON body string")
    parser.add_argument("--body-file", help="Path to JSON body file")
    parser.add_argument("--file", action="append", default=[], help="Upload file (format key=@path)")
    method = op.method.upper()
    out_required = (
        ("binary_output" in op.safety or "sensitive_output" in op.safety)
        and method != "WEBSOCKET"
    )
    parser.add_argument("--out", required=out_required, help="Output file path")
    parser.add_argument("--overwrite", action="store_true", help="Allow overwriting the --out file")


def cmd_operation(args: argparse.Namespace, ctx: dict[str, Any]) -> int:
    op: Operation = args.operation
    live = bool(ctx.get("live"))
    apply_flag = bool(ctx.get("apply"))
    write_operation = _operation_requires_apply(op)
    will_execute = live and (apply_flag or not write_operation)
    if live and not apply_flag and write_operation:
        raise SafetyError("Refused: --live requires --apply for write operations")

    path_params = _collect_path_params(op.path, args)
    params = _parse_key_value(args.param or [], "--param")
    body = _load_json_body(
        getattr(args, "body", None),
        getattr(args, "body_file", None),
        allow_file_read=will_execute,
    )
    files_for_plan = _parse_file_args(args.file or [], allow_exists=False)
    request = summarize_request(op=op, params=params, body=body, files=files_for_plan)
    plan, plan_path = plan_for_operation(
        ctx=ctx,
        op=op,
        selector={
            "kind": op.name,
            "value": next((val for val in path_params.values() if val), "workspace"),
        },
        request=request,
    )

    ctx["audit"].write(f"{op.name}.plan", {"plan_out": plan_path})

    applied_plan = plan_from_file_for_apply(ctx=ctx, op=op) if apply_flag else None
    if applied_plan:
        plan = applied_plan

    if not will_execute:
        ctx["out"].emit({"ok": True, "dry_run": True, "plan": plan, "plan_out": plan_path})
        return 0

    if apply_flag:
        _enforce_apply_requirements(op, ctx)
    if op.method.upper() == "WEBSOCKET":
        raise SafetyError("Refused: WebSocket operations must stay plan-only")
    if write_operation and not bool(ctx.get("ack_no_snapshot")):
        ctx["audit"].write(
            f"{op.name}.refused",
            {"reason": BEFORE_STATE_REFUSAL_REASON, "before_state": plan.get("before_state")},
        )
        ctx["out"].emit(
            {
                "ok": True,
                "dry_run": False,
                "refused": True,
                "reasons": [BEFORE_STATE_REFUSAL_REASON],
                "refusal_type": "SafetyError",
                "plan": plan,
                "plan_out": plan_path,
                "verification_plan": build_before_state_refusal_verification_plan(),
            }
        )
        return 0
    if not ctx["cfg"].token:
        raise ValidationError("Missing ELEVENLABS_API_KEY required for --live")

    files_for_apply = _parse_file_args(args.file or [], allow_exists=will_execute)
    result, outputs, receipt = _apply_operation(
        ctx=ctx,
        op=op,
        path_params=path_params,
        params=params,
        body=body,
        files=files_for_apply,
        args=args,
        plan=plan,
    )
    receipt_path = write_receipt_to_file(receipt=receipt, path=ctx.get("receipt_out"))
    ctx["audit"].write(f"{op.name}.apply", {"receipt_out": receipt_path})
    ctx["out"].emit(
        {
            "ok": True,
            "dry_run": False,
            "plan": plan,
            "receipt": receipt,
            "receipt_out": receipt_path,
            "result": result,
            "outputs": outputs,
        }
    )
    return 0


def _operation_requires_apply(op: Operation) -> bool:
    method = op.method.upper()
    safety_tags = set(op.safety)
    if "write" in safety_tags:
        return True
    if method in READ_ONLY_METHODS:
        return False
    if POST_READ_OVERRIDE in safety_tags:
        return False
    return True


def _extract_path_placeholders(path: str) -> list[str]:
    return re.findall(r"{([^}]+)}", path)


def _collect_path_params(path: str, args: argparse.Namespace) -> dict[str, str]:
    placeholders = _extract_path_placeholders(path)
    values: dict[str, str] = {}
    for key in placeholders:
        value = str(getattr(args, key, "") or "").strip()
        if not value:
            raise ValidationError(f"Missing --{key.replace('_', '-')}")
        values[key] = value
    return values


def _parse_key_value(items: list[str], flag: str) -> dict[str, str] | None:
    if not items:
        return None
    result: dict[str, str] = {}
    for item in items:
        if "=" not in item:
            raise ValidationError(f"Invalid {flag} value '{item}'; expected key=value")
        key, value = item.split("=", 1)
        result[key.strip()] = value.strip()
    return result


def _load_json_body(body: str | None, body_file: str | None, *, allow_file_read: bool) -> dict[str, Any] | None:
    if body and body_file:
        raise ValidationError("Cannot pass --body and --body-file together")
    if body_file:
        path = Path(body_file)
        if allow_file_read:
            if not path.exists():
                raise ValidationError(f"Body file not found: {body_file}")
            try:
                return json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                raise ValidationError(f"Invalid JSON in --body-file: {exc}") from exc
        return {"__body_file": body_file}
    if body:
        try:
            return json.loads(body)
        except json.JSONDecodeError as exc:
            raise ValidationError(f"Invalid JSON in --body: {exc}") from exc
    return None


def _parse_file_args(items: list[str], *, allow_exists: bool) -> dict[str, Path | str] | None:
    if not items:
        return None
    result: dict[str, Path | str] = {}
    for item in items:
        if "=" not in item:
            raise ValidationError(f"Invalid --file value '{item}'; expected key=@path")
        key, value = item.split("=", 1)
        if not value.startswith("@"):
            raise ValidationError(f"--file values must start with '@<path>'; got '{value}'")
        target = Path(value[1:])
        if allow_exists and not target.exists():
            raise ValidationError(f"File not found for --file: {target}")
        result[key.strip()] = target if allow_exists else value[1:]
    return result


def _enforce_apply_requirements(op: Operation, ctx: dict[str, Any]) -> None:
    if not ctx.get("live"):
        raise SafetyError("Refused: --apply requires --live")
    if "spend_money" in op.safety and not ctx.get("ack_spend_money"):
        raise SafetyError("Refused: spend-money operations require --ack-spend-money")
    if "irreversible" in op.safety:
        if not ctx.get("ack_irreversible"):
            raise SafetyError("Refused: irreversible operations require --ack-irreversible")
        if not ctx.get("yes"):
            raise SafetyError("Refused: irreversible operations require --yes")


def _apply_operation(
    *,
    ctx: dict[str, Any],
    op: Operation,
    path_params: dict[str, str],
    params: dict[str, str] | None,
    body: dict[str, Any] | None,
    files: dict[str, Path] | None,
    args: argparse.Namespace,
    plan: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    cfg = ctx["cfg"]
    url = _build_request_url(cfg.base_url, op.path, path_params)
    headers = {"xi-api-key": cfg.token}
    files_payload, handles = _prepare_files_payload(files)
    payload = body
    data_payload = None
    if files_payload and body is not None:
        data_payload = _multipart_form_fields(body)
        payload = None

    try:
        resp = ctx["http_client"].request(
            op.method,
            url,
            headers=headers,
            params=params,
            json=payload,
            data=data_payload,
            files=files_payload if files_payload else None,
        )
    except RuntimeError as exc:
        raise ToolError(str(exc)) from exc
    finally:
        for handle in handles:
            handle.close()

    result = {"status_code": resp.status}
    outputs: dict[str, Any] = {}
    if "binary_output" in op.safety:
        out_path = ensure_output_file(
            path=getattr(args, "out", None),
            overwrite=bool(getattr(args, "overwrite", False)),
        )
        fingerprint = write_binary_file(out_path, resp.body)
        result["file"] = fingerprint
        outputs["file"] = fingerprint
    elif "sensitive_output" in op.safety:
        out_path = ensure_json_output_file(
            path=getattr(args, "out", None),
            overwrite=bool(getattr(args, "overwrite", False)),
        )
        try:
            decoded = resp.json()
        except json.JSONDecodeError as exc:
            raise ToolError(f"Invalid JSON response for {op.cli_command}: {exc}") from exc
        fingerprint = write_json_file(out_path, decoded)
        result["file"] = fingerprint
        outputs["file"] = fingerprint
    else:
        try:
            decoded = resp.json()
        except json.JSONDecodeError:
            decoded = resp.text()
        outputs["response"] = decoded
        result["response"] = decoded

    verification = default_verification(op=op)
    receipt = build_receipt(
        ctx=ctx,
        op=op,
        plan=plan,
        result=result,
        verification=verification,
        outputs=outputs,
        changed="write" in op.safety,
    )
    return result, outputs, receipt


def _prepare_files_payload(files: dict[str, Path] | None) -> tuple[list[tuple[str, tuple[str, BinaryIO]]], list[BinaryIO]]:
    if not files:
        return [], []
    payload: list[tuple[str, tuple[str, BinaryIO]]] = []
    handles: list[BinaryIO] = []
    for key, path in files.items():
        handle = path.open("rb")
        handles.append(handle)
        payload.append((key, (path.name, handle)))
    return payload, handles


def _multipart_form_fields(body: dict[str, Any]) -> dict[str, str]:
    fields: dict[str, str] = {}
    for key, value in body.items():
        if value is None:
            continue
        if isinstance(value, bool):
            fields[key] = "true" if value else "false"
        elif isinstance(value, (str, int, float)):
            fields[key] = str(value)
        else:
            fields[key] = json.dumps(value, separators=(",", ":"))
    return fields


def _build_request_url(base_url: str, path: str, path_params: dict[str, str]) -> str:
    filled = path
    for key, value in path_params.items():
        filled = filled.replace(f"{{{key}}}", value)
    if filled.startswith(("http://", "https://", "ws://", "wss://")):
        return filled
    return f"{base_url}{filled}"
