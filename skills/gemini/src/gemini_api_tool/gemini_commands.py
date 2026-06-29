from __future__ import annotations

import argparse
from typing import Any

from .gemini_runtime import GeminiClient, execute_operation, load_json_arg
from .operation_registry import OPERATIONS, OperationSpec


def _flag_name(name: str) -> str:
    out = []
    for ch in name:
        if ch.isupper():
            out.append("-")
            out.append(ch.lower())
        else:
            out.append(ch)
    return "".join(out).replace("_", "-").strip("-")


def _dest_name(name: str) -> str:
    return name.replace("-", "_")


def _cmd_operation(args: argparse.Namespace, ctx: dict[str, Any]) -> int:
    op: OperationSpec = args.operation_spec
    cfg = ctx["cfg"]
    body = load_json_arg(getattr(args, "request_json", None))
    query = load_json_arg(getattr(args, "query_json", None)) or {}
    path_values = {
        name: str(getattr(args, _dest_name(_flag_name(name)), "") or "")
        for name in op.path_params
    }
    client = GeminiClient(
        api_key=cfg.api_key,
        base_url=cfg.base_url,
        timeout_s=ctx["timeout_s"],
        verbose=bool(ctx.get("verbose")),
    )
    result = execute_operation(
        op,
        client=client,
        path_values=path_values,
        query_values=query,
        body=body,
        media_file=getattr(args, "media_file", None),
        apply=bool(ctx.get("apply")),
        yes=bool(ctx.get("yes")),
        ack_no_snapshot=bool(getattr(args, "ack_no_snapshot", False)),
        ack_irreversible=bool(getattr(args, "ack_irreversible", False) or ctx.get("ack_irreversible")),
        plan_in=ctx.get("plan_in"),
        receipt_out=ctx.get("receipt_out"),
        plan_out=ctx.get("plan_out"),
        api_version=getattr(args, "api_version", None),
    )
    ctx["audit"].write("gemini.operation", {"operation_id": op.operation_id, "ok": result.get("ok"), "dry_run": result.get("dry_run")})
    ctx["out"].emit(result)
    return 0 if result.get("ok") or result.get("refused") else 1


def register(subparsers: argparse._SubParsersAction) -> None:
    by_family: dict[str, list[OperationSpec]] = {}
    for op in OPERATIONS:
        by_family.setdefault(op.family, []).append(op)

    for family in sorted(by_family):
        family_parser = subparsers.add_parser(family, help=f"Gemini {family.replace('-', ' ')} commands")
        family_sub = family_parser.add_subparsers(dest=f"{family.replace('-', '_')}_cmd", required=True)
        for op in sorted(by_family[family], key=lambda item: item.method_name):
            method_parser = family_sub.add_parser(
                op.method_name,
                help=(op.description or op.operation_id)[:120],
            )
            method_parser.add_argument(
                "--api-version",
                choices=op.versions,
                default=None,
                help="Optional official API version override for this operation",
            )
            for param in op.path_params:
                method_parser.add_argument(
                    f"--{_flag_name(param)}",
                    dest=_dest_name(_flag_name(param)),
                    required=True,
                    help=f"Path value for {param}",
                )
            if op.query_params:
                method_parser.add_argument(
                    "--query-json",
                    default=None,
                    help="Optional JSON object or JSON file for documented query parameters",
                )
            if op.request_ref:
                method_parser.add_argument(
                    "--request-json",
                    default=None,
                    help=f"JSON object or file for {op.request_ref}",
                )
            if op.supports_media_upload:
                method_parser.add_argument("--media-file", default=None, help="Local media file to upload")
            if op.safety_class == "state_changing":
                method_parser.add_argument(
                    "--ack-no-snapshot",
                    action="store_true",
                    help="Acknowledge that this Gemini operation has no safe before-state snapshot",
                )
                method_parser.add_argument(
                    "--ack-irreversible",
                    action="store_true",
                    help="Acknowledge destructive or irreversible Gemini actions",
                )
            method_parser.set_defaults(func=_cmd_operation, operation_spec=op, write_capable=(op.safety_class == "state_changing"))
