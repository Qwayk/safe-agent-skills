from __future__ import annotations

from typing import Any

from ..errors import SafetyError, ValidationError
from ..http import GraphQLClient
from ..schema_registry import OperationField
from ..json_files import read_json_file, write_json_file
from .common import (
    args_hash,
    build_graphql_selection,
    build_operation_document,
    filter_allowed_args,
    parse_payload_argument,
    parse_selection,
    mutation_requires_ack_irreversible,
    mutation_requires_no_snapshot,
    mutation_snapshot_plan_fields,
    text_hash,
)


def _risk_for_mutation(name: str) -> str:
    return "high" if mutation_requires_no_snapshot(name) else "medium"


def _build_plan(*, mutation: str, args_in: dict[str, Any], selection: str | None, ctx: dict[str, Any]) -> dict[str, Any]:
    document = build_operation_document(operation=mutation, args=args_in, selection=selection, operation_type="mutation")
    return {
        "command": f"write.{mutation}",
        "operation": mutation,
        "mutation": mutation,
        "intended_mutation": mutation,
        "arguments": args_in,
        "arguments_summary": {"count": len(args_in), "keys": sorted(args_in.keys())},
        "arguments_hash": args_hash(args_in),
        "selection": selection,
        "selection_hash": text_hash(selection),
        "graphql": {
            "document": document,
            "document_hash": text_hash(document),
        },
        "risk": _risk_for_mutation(mutation),
        **mutation_snapshot_plan_fields(),
        "verification_plan": {
            "type": "read_back",
            "steps": [
                "Run a matching read command with a limited selector",
                "Check expected fields changed",
                "Confirm response includes requested mutation result",
            ],
            "required_for_apply": True,
        },
        "env_fingerprint": ctx["cfg"].graphql_url,
    }


def _refuse_apply(*, spec: OperationField, reason: str, ctx: dict[str, Any]) -> int:
    out = {
        "ok": True,
        "dry_run": False,
        "refused": True,
        "command": f"write.{spec.name}",
        "operation": spec.name,
        "reasons": [reason],
        "refusal_type": "SafetyError",
    }
    ctx["audit"].write(f"write.{spec.name}.refused", out)
    ctx["out"].emit(out)
    return 0


def _load_apply_plan(ctx: dict[str, Any]) -> dict[str, Any]:
    plan_in = ctx.get("plan_in")
    if not plan_in:
        raise SafetyError("Refused: live write apply requires --plan-in from a reviewed plan")
    plan = read_json_file(plan_in)
    if not isinstance(plan, dict):
        raise ValidationError("Plan file must be a JSON object")
    return plan


def _expect_plan_value(plan: dict[str, Any], key: str, expected: Any, reason: str) -> None:
    if plan.get(key) != expected:
        raise SafetyError(reason)


def _validate_apply_plan(*, plan: dict[str, Any], current_plan: dict[str, Any], spec: OperationField, ctx: dict[str, Any]) -> None:
    graph = plan.get("graphql")
    current_graph = current_plan.get("graphql")
    if not isinstance(graph, dict) or not isinstance(current_graph, dict):
        raise SafetyError("Refused: plan is missing GraphQL document metadata")

    _expect_plan_value(
        plan,
        "env_fingerprint",
        ctx["cfg"].graphql_url,
        "Refused: plan env_fingerprint does not match current Jobber endpoint",
    )
    _expect_plan_value(plan, "operation", spec.name, "Refused: plan operation does not match command")
    _expect_plan_value(plan, "mutation", spec.name, "Refused: plan mutation does not match command")
    _expect_plan_value(plan, "intended_mutation", spec.name, "Refused: plan intended_mutation does not match command")
    _expect_plan_value(plan, "arguments_hash", current_plan["arguments_hash"], "Refused: command arguments do not match reviewed plan")
    _expect_plan_value(plan, "selection_hash", current_plan["selection_hash"], "Refused: command selection does not match reviewed plan")
    _expect_plan_value(
        plan,
        "snapshot_status",
        current_plan.get("snapshot_status", "No snapshot available"),
        "Refused: plan missing expected no-snapshot metadata",
    )

    if graph.get("document_hash") != current_graph.get("document_hash"):
        raise SafetyError("Refused: GraphQL document hash does not match reviewed plan")
    if graph.get("document") != current_graph.get("document"):
        raise SafetyError("Refused: GraphQL document does not match reviewed plan")


def cmd_write_operation(args, ctx: dict[str, Any]) -> int:
    spec: OperationField = getattr(args, "schema_operation")
    raw_args = parse_payload_argument(args_json=getattr(args, "args_json", None), args_file=getattr(args, "args_file", None))
    args_in = filter_allowed_args(spec=spec, raw_args=raw_args)

    selection = parse_selection(selection=getattr(args, "selection", None), selection_file=getattr(args, "selection_file", None))
    if spec.type.kind not in {"SCALAR", "ENUM"}:
        selection = build_graphql_selection(spec.type.kind, selection)

    plan = _build_plan(mutation=spec.name, args_in=args_in, selection=selection, ctx=ctx)
    plan_out = ctx.get("plan_out")
    if plan_out and not bool(ctx.get("apply")):
        plan_path = write_json_file(plan_out, plan)
    else:
        plan_path = None

    if not bool(ctx.get("apply")):
        out = {
            "ok": True,
            "dry_run": True,
            "plan": plan,
            "plan_out": plan_path,
            "command": f"write.{spec.name}",
            "operation": spec.name,
        }
        ctx["audit"].write(f"write.{spec.name}.plan", out)
        ctx["out"].emit(out)
        return 0

    if not ctx.get("plan_in"):
        return _refuse_apply(
            spec=spec,
            reason="Refused: live write apply requires --plan-in from a reviewed plan",
            ctx=ctx,
        )

    if not bool(ctx.get("yes")):
        return _refuse_apply(
            spec=spec,
            reason="Refused: write operations require --apply --yes",
            ctx=ctx,
        )

    if mutation_requires_no_snapshot(spec.name) and not bool(ctx.get("ack_no_snapshot")):
        return _refuse_apply(
            spec=spec,
            reason="Refused: high-risk write operations require --ack-no-snapshot before HTTP",
            ctx=ctx,
        )

    if mutation_requires_ack_irreversible(spec.name) and not bool(ctx.get("ack_irreversible")):
        return _refuse_apply(
            spec=spec,
            reason="Refused: this irreversible operation requires --ack-irreversible",
            ctx=ctx,
        )

    apply_plan = _load_apply_plan(ctx)
    _validate_apply_plan(plan=apply_plan, current_plan=plan, spec=spec, ctx=ctx)

    client = GraphQLClient(
        endpoint=ctx["cfg"].graphql_url,
        token=ctx["cfg"].token,
        graphql_version=ctx["cfg"].graphql_version,
        timeout_s=ctx["timeout_s"],
        verbose=ctx["verbose"],
    )
    if not ctx["cfg"].token:
        raise ValidationError("Missing access token for mutation execution")

    response = client.execute(plan["graphql"]["document"], variables=None)
    out = {
        "ok": True,
        "dry_run": False,
        "command": f"write.{spec.name}",
        "operation": spec.name,
        "plan": plan,
        "result": response,
        "snapshot_status": plan["snapshot_status"],
        "recovery_notes": plan["recovery_notes"],
        "recovery": plan["recovery"],
        "selection": selection,
        "arguments": args_in,
    }

    receipt_out = ctx.get("receipt_out")
    if receipt_out:
        receipt_payload = {
            "plan": plan,
            "result": response,
            "snapshot_status": plan["snapshot_status"],
            "recovery_notes": plan["recovery_notes"],
            "recovery": plan["recovery"],
        }
        out["receipt_out"] = write_json_file(receipt_out, receipt_payload)
    ctx["audit"].write(f"write.{spec.name}.apply", out)
    ctx["out"].emit(out)
    return 0
