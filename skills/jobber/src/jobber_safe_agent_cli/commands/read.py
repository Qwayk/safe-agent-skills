from __future__ import annotations

from typing import Any

from ..errors import ValidationError
from ..http import GraphQLClient
from ..schema_registry import OperationField
from .common import (
    args_hash,
    build_graphql_selection,
    build_operation_document,
    filter_allowed_args,
    parse_payload_argument,
    parse_selection,
)


def _build_limit_if_applicable(*, args_in: dict[str, Any], spec: OperationField, limit: int | None) -> dict[str, Any]:
    if limit is None:
        return args_in
    if "limit" in {arg.name for arg in spec.args} and "limit" not in args_in:
        args_in["limit"] = limit
    elif "first" in {arg.name for arg in spec.args} and "first" not in args_in:
        args_in["first"] = limit
    return args_in


def cmd_read_operation(args, ctx: dict[str, Any]) -> int:
    spec: OperationField = getattr(args, "schema_operation")
    if not ctx["cfg"].token:
        raise ValidationError("Missing access token for read execution")

    args_in = parse_payload_argument(args_json=getattr(args, "args_json", None), args_file=getattr(args, "args_file", None))
    args_in = filter_allowed_args(spec=spec, raw_args=args_in)

    args_in = _build_limit_if_applicable(
        args_in=args_in,
        spec=spec,
        limit=getattr(args, "limit", None),
    )

    selection = parse_selection(selection=getattr(args, "selection", None), selection_file=getattr(args, "selection_file", None))
    base_type = spec.type.kind
    if base_type not in {"SCALAR", "ENUM"}:
        selection = build_graphql_selection(base_type, selection)
    document = build_operation_document(
        operation=spec.name,
        args=args_in,
        selection=selection,
        operation_type="query",
    )

    client = GraphQLClient(
        endpoint=ctx["cfg"].graphql_url,
        token=ctx["cfg"].token,
        graphql_version=ctx["cfg"].graphql_version,
        timeout_s=ctx["timeout_s"],
        verbose=ctx["verbose"],
    )
    response = client.execute(document, variables=None)

    out = {
        "ok": True,
        "dry_run": False,
        "command": f"read.{spec.name}",
        "operation": spec.name,
        "graphql": {"document": document, "document_hash": args_hash({"selection": selection or "", "args": args_in})},
        "selection": selection,
        "arguments": args_in,
        "result": response.get("data"),
        "errors": response.get("errors"),
    }
    ctx["audit"].write(f"read.{spec.name}", out)
    ctx["out"].emit(out)
    return 0
