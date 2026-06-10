from __future__ import annotations

from pathlib import Path
from typing import Any

from ..runtime import get_api
from ..webhooks_ledger import append_webhook_row, iter_webhook_rows, webhooks_index_path_for_env_file


def add_webhook_commands(webhook_sub) -> None:
    webhook_create = webhook_sub.add_parser(
        "create",
        help="Create a webhook (high-impact; dry-run by default; apply requires --yes --plan-in --ack-no-verify)",
    )
    webhook_create.add_argument("--event", required=True)
    webhook_create.add_argument("--target-url", required=True)
    webhook_create.add_argument("--name", default=None)
    webhook_create.add_argument("--api-version", default=None)
    webhook_create.add_argument(
        "--secret-file",
        default=None,
        help="Optional path to a local secret file (never printed or persisted; plan shows ***REDACTED***)",
    )
    webhook_create.set_defaults(func=cmd_webhook_create)

    webhook_update = webhook_sub.add_parser(
        "update",
        help="Update a webhook (high-impact; dry-run by default; apply requires --yes --plan-in --ack-no-verify)",
    )
    webhook_update.add_argument("--id", required=True)
    webhook_update.add_argument("--event", default=None)
    webhook_update.add_argument("--target-url", default=None)
    webhook_update.add_argument("--name", default=None)
    webhook_update.add_argument("--api-version", default=None)
    webhook_update.set_defaults(func=cmd_webhook_update)

    webhook_delete = webhook_sub.add_parser(
        "delete",
        help="Delete a webhook (high-impact; dry-run by default; apply requires --yes --plan-in --ack-no-verify)",
    )
    webhook_delete.add_argument("--id", required=True)
    webhook_delete.set_defaults(func=cmd_webhook_delete)


def _redact_secrets(obj: Any) -> Any:
    if isinstance(obj, dict):
        out: dict[str, Any] = {}
        for k, v in obj.items():
            lk = str(k).lower()
            if lk in {"secret"} or lk.endswith("_secret") or lk.endswith("_token") or lk.endswith("_api_key"):
                continue
            out[k] = _redact_secrets(v)
        return out
    if isinstance(obj, list):
        return [_redact_secrets(x) for x in obj]
    return obj


def _extract_webhook(obj: dict[str, Any], *, label: str) -> dict[str, Any]:
    webhooks = obj.get("webhooks") or []
    if not isinstance(webhooks, list) or not webhooks or not isinstance(webhooks[0], dict):
        raise RuntimeError(f"Unexpected response (missing webhooks list) for {label}")
    return webhooks[0]


def _ledger_path(ctx: dict[str, Any]) -> Path:
    env_file = str(ctx.get("env_file") or "").strip()
    if not env_file:
        raise RuntimeError("Internal error: env_file missing from context")
    return webhooks_index_path_for_env_file(env_file)


def _webhook_recovery(*, ledger_path: Path, run_id: str | None, include_rows: bool) -> dict[str, Any]:
    recovery: dict[str, Any] = {
        "end_state": "irreversible_and_clearly_labeled",
        "strategy": "ledger_only_proof",
        "rollback_ready": False,
        "rollback_plan": None,
        "backups": [],
        "snapshots": [],
        "ledger_path": str(ledger_path),
        "restore_note": "Ghost has no webhook get/list endpoint. This tool stores a local ledger row for proof, but it does not create a restorable snapshot or direct undo path for webhook writes.",
    }
    if include_rows:
        rows = iter_webhook_rows(ledger_path)
        if run_id:
            rows = [row for row in rows if str(row.get("run_id") or "") == str(run_id)]
        recovery["ledger_rows"] = rows[-3:]
    return recovery


def _refuse_no_verify(ctx: dict[str, Any], *, action: str, selector: dict[str, Any], planned: dict[str, Any]) -> int:
    if not bool(ctx.get("ack_no_verify")):
        ledger_path = _ledger_path(ctx)
        ctx["out"].print(
            {
                "ok": True,
                "apply": True,
                "refused": True,
                "reasons": ["Refused: webhook changes require --ack-no-verify (Ghost has no webhook get/list endpoint to verify)"],
                "action": action,
                "selector": selector,
                "planned": planned,
                "recovery": _webhook_recovery(ledger_path=ledger_path, run_id=str(ctx.get("run_id") or ""), include_rows=False),
                "backups": [],
                "rollback_plan": None,
            }
        )
        return 0
    return -1


def cmd_webhook_create(args, ctx) -> int:
    planned: dict[str, Any] = {
        "event": args.event,
        "target_url": args.target_url,
    }
    if args.name is not None:
        planned["name"] = args.name
    if args.api_version is not None:
        planned["api_version"] = args.api_version
    if args.secret_file is not None:
        planned["secret"] = "***REDACTED***"

    ledger_path = _ledger_path(ctx)

    if not ctx["apply"]:
        ctx["out"].print(
            {
                "apply": False,
                "refused": False,
                "create": planned,
                "ledger_path": str(ledger_path),
                "note": "Ghost has no webhook get/list endpoint; apply will store a local ledger entry.",
                "recovery": _webhook_recovery(ledger_path=ledger_path, run_id=str(ctx.get("run_id") or ""), include_rows=False),
            }
        )
        return 0

    refused = _refuse_no_verify(ctx, action="webhook.create", selector={}, planned=planned)
    if refused == 0:
        return 0

    secret_value = None
    if args.secret_file is not None:
        p = Path(str(args.secret_file)).expanduser()
        secret_value = p.read_text(encoding="utf-8").strip()

    webhook: dict[str, Any] = {
        "event": args.event,
        "target_url": args.target_url,
    }
    if args.name is not None:
        webhook["name"] = args.name
    if args.api_version is not None:
        webhook["api_version"] = args.api_version
    if isinstance(secret_value, str) and secret_value:
        webhook["secret"] = secret_value

    api = get_api(ctx)
    res = api.webhooks_create({"webhooks": [webhook]})
    redacted = _redact_secrets(res)
    created = _extract_webhook(redacted, label="create")
    webhook_id = created.get("id")

    append_webhook_row(
        ledger_path,
        {
            "action": "create",
            "webhook_id": webhook_id,
            "event": created.get("event"),
            "target_url": created.get("target_url"),
            "name": created.get("name"),
            "api_version": created.get("api_version"),
            "integration_id": created.get("integration_id"),
            "run_id": ctx.get("run_id"),
        },
    )

    ctx["audit"].write("webhook.create", {"apply": True, "webhook_id": webhook_id, "event": args.event})
    ctx["out"].print(
        {
            "ok": True,
            "webhook": created,
            "ledger_path": str(ledger_path),
            "recovery": _webhook_recovery(ledger_path=ledger_path, run_id=str(ctx.get("run_id") or ""), include_rows=True),
            "backups": [],
            "rollback_plan": None,
        }
    )
    return 0


def cmd_webhook_update(args, ctx) -> int:
    planned: dict[str, Any] = {}
    if args.event is not None:
        planned["event"] = args.event
    if args.target_url is not None:
        planned["target_url"] = args.target_url
    if args.name is not None:
        planned["name"] = args.name
    if args.api_version is not None:
        planned["api_version"] = args.api_version

    if not planned:
        ctx["out"].print({"apply": ctx["apply"], "refused": False, "reasons": [], "note": "No changes requested"})
        return 0

    ledger_path = _ledger_path(ctx)

    if not ctx["apply"]:
        ctx["out"].print(
            {
                "apply": False,
                "refused": False,
                "webhook_id": args.id,
                "update": planned,
                "ledger_path": str(ledger_path),
                "note": "Ghost has no webhook get/list endpoint; apply will store a local ledger entry.",
                "recovery": _webhook_recovery(ledger_path=ledger_path, run_id=str(ctx.get("run_id") or ""), include_rows=False),
            }
        )
        return 0

    refused = _refuse_no_verify(ctx, action="webhook.update", selector={"id": args.id}, planned=planned)
    if refused == 0:
        return 0

    api = get_api(ctx)
    res = api.webhooks_update(args.id, {"webhooks": [{**planned, "id": args.id}]})
    redacted = _redact_secrets(res)
    updated = _extract_webhook(redacted, label="update")

    append_webhook_row(
        ledger_path,
        {
            "action": "update",
            "webhook_id": args.id,
            "event": updated.get("event"),
            "target_url": updated.get("target_url"),
            "name": updated.get("name"),
            "api_version": updated.get("api_version"),
            "integration_id": updated.get("integration_id"),
            "run_id": ctx.get("run_id"),
        },
    )

    ctx["audit"].write("webhook.update", {"apply": True, "webhook_id": args.id, "fields": sorted(planned.keys())})
    ctx["out"].print(
        {
            "ok": True,
            "webhook": updated,
            "ledger_path": str(ledger_path),
            "recovery": _webhook_recovery(ledger_path=ledger_path, run_id=str(ctx.get("run_id") or ""), include_rows=True),
            "backups": [],
            "rollback_plan": None,
        }
    )
    return 0


def cmd_webhook_delete(args, ctx) -> int:
    ledger_path = _ledger_path(ctx)

    if not ctx["apply"]:
        ctx["out"].print(
            {
                "apply": False,
                "refused": False,
                "delete": {"id": args.id},
                "ledger_path": str(ledger_path),
                "note": "Ghost has no webhook get/list endpoint; apply will store a local ledger entry.",
                "recovery": _webhook_recovery(ledger_path=ledger_path, run_id=str(ctx.get("run_id") or ""), include_rows=False),
            }
        )
        return 0

    refused = _refuse_no_verify(ctx, action="webhook.delete", selector={"id": args.id}, planned={})
    if refused == 0:
        return 0

    api = get_api(ctx)
    resp = api.webhooks_delete(args.id)
    if resp.status not in (200, 204):
        raise RuntimeError(f"Unexpected delete response: HTTP {resp.status}")

    append_webhook_row(ledger_path, {"action": "delete", "webhook_id": args.id, "run_id": ctx.get("run_id")})
    ctx["audit"].write("webhook.delete", {"apply": True, "webhook_id": args.id})
    ctx["out"].print(
        {
            "ok": True,
            "deleted": {"id": args.id},
            "ledger_path": str(ledger_path),
            "recovery": _webhook_recovery(ledger_path=ledger_path, run_id=str(ctx.get("run_id") or ""), include_rows=True),
            "backups": [],
            "rollback_plan": None,
        }
    )
    return 0
