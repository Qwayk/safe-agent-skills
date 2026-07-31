from __future__ import annotations

import argparse
import os
import stat
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any, cast

from . import __version__
from .audit_log import AuditLogger, CompositeAuditLogger
from .client import NameBrightClient
from .commands import auth as auth_cmd
from .commands import onboarding as onboarding_cmd
from .config import Config, load_config
from .errors import NotSupportedError, SafetyError, ToolError, ValidationError
from .operations import OPERATIONS, OperationSpec
from .output import Output
from .runs import (
    RunContext,
    append_index_row,
    build_deterministic_summary,
    find_run,
    init_run_context,
    list_runs,
    runs_index_path_for_env_file,
    write_summary_md,
)
from .workflow import apply_plan, create_plan

NAME = "namebright-safe-cli"


ACK_FLAGS: tuple[tuple[str, str], ...] = (
    ("ack_spend", "ack-spend"),
    ("ack_high_risk", "ack-high-risk"),
    ("ack_destructive", "ack-destructive"),
    ("ack_ownership", "ack-ownership"),
    ("ack_no_snapshot", "ack-no-snapshot"),
    ("ack_irreversible", "ack-irreversible"),
    ("ack_external_message", "ack-external-message"),
    ("ack_account_creation", "ack-account-creation"),
)


class _ToolArgumentParser(argparse.ArgumentParser):
    """
    Keep parser failures JSON-friendly.
    """

    def error(self, message: str) -> None:  # type: ignore[override]
        raise ValidationError(message)


def _output_mode_from_argv(argv: list[str]) -> str:
    if "--output" not in argv:
        return "json"
    idx = argv.index("--output")
    if idx + 1 >= len(argv):
        return "json"
    v = str(argv[idx + 1]).lower().strip()
    return v if v in {"json", "text"} else "json"


def _parse_bool_arg(value: str) -> bool:
    normalized = str(value).strip().lower()
    if normalized == "true":
        return True
    if normalized == "false":
        return False
    raise argparse.ArgumentTypeError("expected true or false")


def _parse_int_arg(value: str) -> int:
    if isinstance(value, bool):
        raise argparse.ArgumentTypeError("expected integer")
    try:
        return int(str(value).strip())
    except Exception:
        raise argparse.ArgumentTypeError("expected integer") from None


def _safe_leaf_name(spec: OperationSpec) -> str:
    return spec.command.partition(" ")[2]


def _safe_command_label(spec: OperationSpec) -> str:
    return f"{NAME} {spec.family} {_safe_leaf_name(spec)}"


def _add_field_arg(parser: argparse.ArgumentParser, field: Any) -> None:
    if field.source != "cli" or not field.cli_name:
        return
    dest = field.cli_name.replace("-", "_")
    arg = f"--{field.cli_name}"
    kwargs: dict[str, Any] = {"dest": dest, "help": None}
    if field.choices:
        kwargs["choices"] = list(field.choices)
    if field.kind == "int":
        kwargs["type"] = _parse_int_arg
    elif field.kind == "bool":
        kwargs["type"] = _parse_bool_arg
        if field.default is not None:
            kwargs["default"] = bool(field.default)
        if field.required:
            kwargs["required"] = True
    elif field.kind == "secret_file":
        kwargs["type"] = str
        kwargs["required"] = False
    else:
        kwargs["type"] = str

    if field.kind not in {"bool", "secret_file"}:
        if field.required and field.default is None:
            kwargs["required"] = True
        else:
            kwargs["required"] = False
            if field.default is not None:
                kwargs["default"] = field.default

    parser.add_argument(arg, **kwargs)


def _is_secret_file_read_allowed(path: Path) -> bool:
    return path.is_file() and (not path.is_symlink())


def _read_secret_file(path: Path) -> str:
    if not _is_secret_file_read_allowed(path):
        raise ValidationError("Refused: secret file must be a regular file and not a symlink")
    try:
        mode = path.stat().st_mode
    except FileNotFoundError as e:
        raise ValidationError("Refused: secret file is unavailable") from e

    if os.name == "posix" and stat.S_IMODE(mode) != 0o600:
        raise ValidationError("Refused: secret file mode must be 0600 on POSIX")
    try:
        size = path.stat().st_size
    except FileNotFoundError as e:
        raise ValidationError("Refused: secret file is unavailable") from e
    if size <= 0:
        raise ValidationError("Refused: secret file must be non-empty")
    if size > 64 * 1024:
        raise ValidationError("Refused: secret file must be <= 64KiB")

    text = path.read_text(encoding="utf-8")
    if text.strip() == "":
        raise ValidationError("Refused: secret file must be non-empty")
    return text.strip()


def _operation_values_from_args(spec: OperationSpec, args: argparse.Namespace) -> dict[str, Any]:
    values: dict[str, Any] = {}
    for field in spec.fields:
        if field.source != "cli" or not field.cli_name or field.kind == "secret_file":
            continue
        name = field.cli_name.replace("-", "_")
        value = getattr(args, name, None)
        if value is None:
            if field.required:
                raise ValidationError(f"Missing required flag: --{field.cli_name}")
            continue
        values[field.api_name] = value
    return values


def _secret_values_from_args(spec: OperationSpec, args: argparse.Namespace) -> dict[str, str]:
    values: dict[str, str] = {}
    for field in spec.fields:
        if field.source != "cli" or field.kind != "secret_file" or not field.cli_name:
            continue
        raw = str(getattr(args, field.cli_name.replace("-", "_"), "") or "").strip()
        if not raw:
            continue
        values[field.api_name] = _read_secret_file(Path(raw).expanduser())
    return values


def _required_secret_fields_missing_for_apply(spec: OperationSpec, args: argparse.Namespace) -> list[str]:
    missing: list[str] = []
    for field in spec.fields:
        if (
            field.source != "cli"
            or field.kind != "secret_file"
            or not field.cli_name
            or not field.required
        ):
            continue
        raw = str(getattr(args, field.cli_name.replace("-", "_"), "") or "").strip()
        if not raw:
            missing.append(f"--{field.cli_name}")
    return missing


def _validate_non_write_flags_for_read(spec: OperationSpec, args: argparse.Namespace) -> None:
    if spec.write_capable:
        return
    if bool(args.apply):
        raise ValidationError("--apply is only available for write-capable operations")
    if bool(getattr(args, "yes", False)):
        raise ValidationError("--yes is only available with write-capable --apply")
    if getattr(args, "plan_in", None):
        raise ValidationError("--plan-in is only available for write-capable operations")
    if getattr(args, "plan_out", None):
        raise ValidationError("--plan-out is only available for write-capable operations")
    if getattr(args, "receipt_out", None):
        raise ValidationError("--receipt-out is only available for write-capable operations")
    for ack, _ in ACK_FLAGS:
        if bool(getattr(args, ack, False)):
            raise ValidationError("ack flags are only available with write-capable operations")


def _validate_non_write_flags_for_auth(args: argparse.Namespace) -> None:
    if bool(args.apply):
        raise ValidationError("--apply is not available for auth operations")
    if bool(getattr(args, "plan_in", None)):
        raise ValidationError("--plan-in is not available for auth operations")
    if bool(getattr(args, "plan_out", None)):
        raise ValidationError("--plan-out is not available for auth operations")
    if bool(getattr(args, "receipt_out", None)):
        raise ValidationError("--receipt-out is not available for auth operations")
    if bool(args.yes):
        raise ValidationError("--yes is not available for auth operations")
    for ack, _ in ACK_FLAGS:
        if bool(getattr(args, ack, False)):
            raise ValidationError("ack flags are not available for auth operations")


def _acknowledgements_from_args(args: argparse.Namespace) -> dict[str, bool]:
    return {ack: bool(getattr(args, ack, None)) for ack, _ in ACK_FLAGS}


def _cmd_runs_list(args: argparse.Namespace, ctx: dict[str, Any]) -> int:
    runs_index = ctx.get("runs_index_path")
    if not runs_index or not runs_index.exists():
        ctx["out"].emit({"ok": True, "runs": [], "count": 0})
        return 0
    limit = int(getattr(args, "limit", 20) or 20)
    rows = list_runs(runs_index, limit=limit)
    ctx["out"].emit({"ok": True, "runs": rows, "count": len(rows)})
    return 0


def _cmd_runs_show(args: argparse.Namespace, ctx: dict[str, Any]) -> int:
    rid = str(getattr(args, "run_id", "") or "").strip()
    if not rid:
        ctx["out"].emit({"ok": False, "error": "Missing --run-id", "error_type": "ValidationError"})
        return 1
    runs_index = ctx.get("runs_index_path")
    if not runs_index or not runs_index.exists():
        ctx["out"].emit({"ok": False, "error": "No runs index found", "error_type": "NotFound"})
        return 1
    row = find_run(runs_index, run_id=rid)
    if not row:
        ctx["out"].emit({"ok": False, "error": f"Run not found: {rid}", "error_type": "NotFound"})
        return 1
    summary = None
    try:
        artifacts_dir = row.get("artifacts_dir")
        if isinstance(artifacts_dir, str) and artifacts_dir:
            summary_path = Path(artifacts_dir) / "summary.md"
            if summary_path.exists():
                summary = summary_path.read_text(encoding="utf-8")
    except Exception:
        summary = None
    ctx["out"].emit({"ok": True, "run": row, "summary_md": summary})
    return 0


def _build_registry_parser(parent: argparse._SubParsersAction) -> dict[str, argparse._SubParsersAction]:
    families: dict[str, argparse._SubParsersAction] = {}
    for spec in OPERATIONS:
        if spec.family == "auth":
            continue
        family = families.get(spec.family)
        if family is None:
            family_parser = parent.add_parser(spec.family, help=f"{spec.family} operations")
            family_parser.set_defaults(_is_local_command=False)
            families[spec.family] = family_parser.add_subparsers(
                dest="operation_leaf",
                required=True,
                parser_class=_ToolArgumentParser,
            )
            family = families[spec.family]

        leaf_parser = family.add_parser(_safe_leaf_name(spec), help=f"{spec.family} {_safe_leaf_name(spec)}")
        leaf_parser.set_defaults(
            _registry_spec=spec,
            _is_local_command=False,
            _safe_command=_safe_command_label(spec),
        )
        for field in spec.fields:
            _add_field_arg(leaf_parser, field)
    return families


def _finalize_run_artifacts(
    *,
    run_ctx: RunContext,
    output_obj: dict[str, Any] | None,
    command: str | None,
    env_fingerprint: str | None,
    version: str,
    apply: bool,
    yes: bool,
    audit_log_path: str | None,
    audit_log_global_path: str | None,
) -> None:
    if not run_ctx.enabled or not run_ctx.artifacts_dir or not run_ctx.runs_index_path or not run_ctx.run_id:
        return
    plan_file = run_ctx.artifacts_dir / "plan.json"
    receipt_file = run_ctx.artifacts_dir / "receipt.json"
    plan_path = str(plan_file) if plan_file.exists() else None
    receipt_path = str(receipt_file) if receipt_file.exists() else None
    summary_lines = build_deterministic_summary(
        tool=NAME,
        version=version,
        run_id=run_ctx.run_id,
        env_fingerprint=env_fingerprint,
        command=command,
        output_obj=output_obj,
        plan_path=plan_path,
        receipt_path=receipt_path,
        audit_log_path=audit_log_path,
        audit_log_global_path=audit_log_global_path,
        runs_index_path=str(run_ctx.runs_index_path),
    )
    write_summary_md(path=run_ctx.artifacts_dir / "summary.md", lines=summary_lines)
    append_index_row(
        run_ctx.runs_index_path,
        {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "run_id": run_ctx.run_id,
            "artifacts_dir": str(run_ctx.artifacts_dir),
            "tool": NAME,
            "version": version,
            "command": command,
            "env_fingerprint": env_fingerprint,
            "dry_run": bool(output_obj.get("dry_run")) if isinstance(output_obj, dict) else None,
            "apply": bool(apply),
            "yes": bool(yes),
            "ok": bool(output_obj.get("ok")) if isinstance(output_obj, dict) else None,
            "refused": bool(output_obj.get("refused")) if isinstance(output_obj, dict) else False,
            "plan_path": plan_path,
            "receipt_path": receipt_path,
            "audit_log": audit_log_path,
            "audit_log_global": audit_log_global_path,
        },
    )


def _run_registry_command(
    args: argparse.Namespace,
    spec: OperationSpec,
    ctx: dict[str, Any],
    client: NameBrightClient,
) -> int:
    values = _operation_values_from_args(spec, args)
    command_label = str(getattr(args, "_safe_command", _safe_command_label(spec)))
    _validate_non_write_flags_for_read(spec=spec, args=args)

    if spec.write_capable:
        if bool(args.apply):
            if getattr(args, "plan_out", None):
                raise ValidationError("--plan-out is not available with --apply")
            if not getattr(args, "plan_in", None):
                ctx["out"].emit({"ok": False, "error": "Missing --plan-in for apply", "error_type": "ValidationError"})
                return 1
            if not bool(args.yes):
                ctx["out"].emit({"ok": True, "refused": True, "reasons": ["Refused: --yes is required for apply"], "refusal_type": "SafetyError"})
                return 0
            if not getattr(args, "receipt_out", None) and not ctx["run_ctx"].enabled:
                ctx["out"].emit(
                    {"ok": False, "error": "Missing --receipt-out when artifacts are disabled", "error_type": "ValidationError"},
                )
                return 1
            missing = _required_secret_fields_missing_for_apply(spec=spec, args=args)
            if missing:
                ctx["out"].emit({"ok": False, "error": f"Missing required file flag(s): {', '.join(missing)}", "error_type": "ValidationError"})
                return 1
            secret_values = _secret_values_from_args(spec, args)
            if not args.receipt_out and ctx["run_ctx"].enabled and ctx["run_ctx"].artifacts_dir:
                args.receipt_out = str(ctx["run_ctx"].artifacts_dir / "receipt.json")
            receipt = apply_plan(
                spec,
                values,
                plan_in=str(args.plan_in),
                receipt_out=str(args.receipt_out),
                client=client,
                yes=True,
                acknowledgements=_acknowledgements_from_args(args),
                secret_values=secret_values,
                tool_version=ctx["tool_version"],
            )
            ctx["out"].emit(
                {
                    "ok": True,
                    "dry_run": False,
                    "applied": True,
                    "operation": {"family": spec.family, "command": spec.command},
                    "receipt": receipt,
                    "receipt_out": args.receipt_out,
                }
            )
            return 0

        if getattr(args, "plan_in", None):
            raise ValidationError("--plan-in is only available with --apply")
        if getattr(args, "receipt_out", None):
            raise ValidationError("--receipt-out is only available with --apply")
        if bool(getattr(args, "yes", False)):
            raise ValidationError("--yes is only available with --apply")
        for ack, _ in ACK_FLAGS:
            if bool(getattr(args, ack, False)):
                raise ValidationError("ack flags are only available with --apply")

        if not args.plan_out and ctx["run_ctx"].enabled and ctx["run_ctx"].artifacts_dir:
            args.plan_out = str(ctx["run_ctx"].artifacts_dir / "plan.json")

        if not args.plan_out and not ctx["run_ctx"].enabled:
            ctx["out"].emit(
                {"ok": False, "error": "Missing --plan-out when artifacts are disabled", "error_type": "ValidationError"},
            )
            return 1

        plan = create_plan(
            spec,
            values,
            plan_out=str(args.plan_out),
            client=client,
            tool_version=ctx["tool_version"],
        )
        ctx["out"].emit(
            {
                "ok": True,
                "dry_run": True,
                "operation": {"family": spec.family, "command": spec.command},
                "plan": plan,
                "plan_out": args.plan_out,
            }
        )
        return 0

    envelope = client.execute_operation(spec, values=values)
    payload = envelope.payload if hasattr(envelope, "payload") else None
    ctx["out"].emit(
        {
            "ok": True,
            "operation": {"family": spec.family, "command": spec.command},
            "response": payload,
            "command_label": command_label,
        }
    )
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = _ToolArgumentParser(prog=NAME)
    p.add_argument("--version", action="store_true", help="Print version and exit")
    p.add_argument("--env-file", default=".env", help="Path to .env file")
    p.add_argument("--timeout-s", type=float, default=None, help="HTTP request timeout seconds")
    p.add_argument("--verbose", action="store_true", help="Verbose provider logs")
    p.add_argument("--output", choices=("json", "text"), default="json", help="Output format")
    p.add_argument("--log-file", default=None, help="Audit log path")
    p.add_argument("--apply", action="store_true", help="Apply a saved plan")
    p.add_argument("--yes", action="store_true", help="Confirm the reviewed saved plan for apply")
    p.add_argument("--plan-out", default=None, help="Plan output file path")
    p.add_argument("--plan-in", default=None, help="Plan input file path")
    p.add_argument("--receipt-out", default=None, help="Receipt output file path")
    for _ack, flag in ACK_FLAGS:
        p.add_argument(f"--{flag}", action="store_true", default=False, help="Safety ack flag")
    p.add_argument("--run-id", default=None, help="Run ID for artifacts")
    p.add_argument("--artifacts-dir", default=None, help="Artifacts directory override")
    p.add_argument("--no-artifacts", action="store_true", help="Disable run artifacts")

    sub = p.add_subparsers(dest="command", required=False, parser_class=_ToolArgumentParser)

    onboarding = sub.add_parser("onboarding", help="Set up local env file")
    onboarding.add_argument("--no-write-env", action="store_true", help="Do not write/update .env")
    onboarding.set_defaults(_is_local_command=True, func=onboarding_cmd.cmd_onboarding, _safe_command=f"{NAME} onboarding")

    runs = sub.add_parser("runs", help="List and inspect run history")
    runs.set_defaults(_is_local_command=True)
    runs_sub = runs.add_subparsers(dest="runs_cmd", required=True, parser_class=_ToolArgumentParser)
    runs_list = runs_sub.add_parser("list", help="List recent runs")
    runs_list.add_argument("--limit", type=int, default=20, help="Max runs to return")
    runs_list.set_defaults(_is_local_command=True, func=_cmd_runs_list, _safe_command=f"{NAME} runs list")

    runs_show = runs_sub.add_parser("show", help="Show run summary")
    runs_show.add_argument("--run-id", required=True, help="Run identifier")
    runs_show.set_defaults(_is_local_command=True, func=_cmd_runs_show, _safe_command=f"{NAME} runs show")

    auth = sub.add_parser("auth", help="Authentication checks")
    auth.set_defaults(_is_local_command=True)
    auth_sub = auth.add_subparsers(dest="auth_cmd", required=True, parser_class=_ToolArgumentParser)
    auth_check = auth_sub.add_parser("check", help="Check local credential presence")
    auth_check.set_defaults(_is_local_command=True, func=auth_cmd.cmd_auth_check, _safe_command=f"{NAME} auth check")
    auth_token_spec = next(
        spec for spec in OPERATIONS if spec.family == "auth" and spec.command == "auth token"
    )
    auth_token = auth_sub.add_parser("token", help="Obtain a safe OAuth token status")
    auth_token.set_defaults(
        _registry_spec=auth_token_spec,
        _is_local_command=False,
        _safe_command=_safe_command_label(auth_token_spec),
    )

    _build_registry_parser(sub)
    return p


def main(argv: list[str], *, client_factory: Callable[..., NameBrightClient] | None = None) -> int:
    parser = build_parser()
    if client_factory is None:
        client_factory = NameBrightClient
    out = Output(mode=_output_mode_from_argv(argv))

    try:
        args = parser.parse_args(argv)
    except ValidationError as e:
        out.emit({"ok": False, "error": str(e), "error_type": "ValidationError"})
        return 1
    except SystemExit as e:
        try:
            return int(e.code or 0)
        except Exception:
            return 1

    if bool(args.version):
        out.emit({"ok": True, "tool": NAME, "version": __version__})
        return 0

    if not getattr(args, "command", None):
        out.emit({"ok": False, "error": "Missing command", "error_type": "ValidationError"})
        return 1
    if args.timeout_s is not None and float(args.timeout_s) <= 0:
        out.emit(
            {
                "ok": False,
                "error": "--timeout-s must be greater than zero",
                "error_type": "ValidationError",
            }
        )
        return 1

    command_str = str(
        getattr(args, "_safe_command", f"{NAME} {str(getattr(args, 'command', '')).strip()}"),
    ).strip()
    is_local = bool(getattr(args, "_is_local_command", False))
    if is_local and str(getattr(args, "command", "")) == "auth":
        try:
            _validate_non_write_flags_for_auth(args)
        except ValidationError as e:
            out.emit({"ok": False, "error": str(e), "error_type": "ValidationError"})
            return 1
    registry_spec = getattr(args, "_registry_spec", None)

    if not is_local and not isinstance(registry_spec, OperationSpec):
        out.emit({"ok": False, "error": "Unsupported command", "error_type": "ValidationError"})
        return 1

    cfg: Config | None = None
    if (not is_local) or str(getattr(args, "command", "")) == "auth":
        try:
            cfg = load_config(str(args.env_file))
        except Exception as e:
            out.emit({"ok": False, "error": str(e), "error_type": "ValidationError"})
            return 1
    env_fingerprint = getattr(cfg, "base_url", None) if cfg is not None else None

    if is_local and str(getattr(args, "command", "")) == "runs":
        run_ctx = init_run_context(
            env_file=str(args.env_file),
            enabled=False,
            run_id=None,
            artifacts_dir=None,
            no_artifacts=True,
        )
    elif is_local:
        run_ctx = RunContext(enabled=False, run_id=None, artifacts_dir=None, runs_index_path=None, audit_log_path=None)
    else:
        assert isinstance(registry_spec, OperationSpec)
        run_ctx = init_run_context(
            env_file=str(args.env_file),
            enabled=bool(registry_spec.write_capable),
            run_id=str(args.run_id) if args.run_id else None,
            artifacts_dir=str(args.artifacts_dir) if args.artifacts_dir else None,
            no_artifacts=bool(args.no_artifacts),
        )

    runs_index_path = runs_index_path_for_env_file(str(args.env_file))
    if is_local and str(getattr(args, "command", "")) == "runs":
        run_ctx = RunContext(
            enabled=False,
            run_id=None,
            artifacts_dir=None,
            runs_index_path=runs_index_path,
            audit_log_path=None,
        )

    run_log_path = str(run_ctx.audit_log_path) if run_ctx.audit_log_path else None
    global_log_path = str(args.log_file) if args.log_file else None
    loggers: list[AuditLogger] = []
    if run_log_path:
        loggers.append(AuditLogger(path=run_log_path, enabled=True))
    if global_log_path:
        loggers.append(AuditLogger(path=global_log_path, enabled=True))
    audit = CompositeAuditLogger(loggers) if len(loggers) > 1 else (loggers[0] if loggers else AuditLogger(path=None, enabled=False))

    out.set_provenance(
        {
            "run_id": run_ctx.run_id,
            "artifacts_dir": str(run_ctx.artifacts_dir) if run_ctx.artifacts_dir else None,
            "runs_index": str(run_ctx.runs_index_path) if run_ctx.runs_index_path else str(runs_index_path),
            "audit_log": run_log_path or global_log_path,
            "audit_log_global": global_log_path,
        }
    )

    audit.bind_context(
        {
            "tool": NAME,
            "version": __version__,
            "command": command_str,
            "apply": bool(args.apply),
            "yes": bool(args.yes),
            "env_fingerprint": env_fingerprint,
            "run_id": run_ctx.run_id,
        }
    )

    if run_ctx.enabled and run_ctx.artifacts_dir:
        if not bool(args.apply) and not args.plan_out:
            args.plan_out = str(run_ctx.artifacts_dir / "plan.json")
        if bool(args.apply) and not args.receipt_out:
            args.receipt_out = str(run_ctx.artifacts_dir / "receipt.json")

    if cfg is None and not is_local:
        out.emit({"ok": False, "error": "Missing configuration", "error_type": "ValidationError"})
        return 1

    ctx: dict[str, Any] = {
        "cfg": cfg,
        "out": out,
        "audit": audit,
        "tool": NAME,
        "client_factory": client_factory,
        "tool_version": __version__,
        "command": command_str,
        "env_file": str(args.env_file),
        "timeout_s": float(args.timeout_s) if args.timeout_s is not None and cfg is not None else None,
        "verbose": bool(args.verbose),
        "apply": bool(args.apply),
        "yes": bool(args.yes),
        "plan_out": args.plan_out,
        "plan_in": args.plan_in,
        "receipt_out": args.receipt_out,
        "run_ctx": run_ctx,
        "runs_index_path": runs_index_path,
        "ack_no_snapshot": bool(getattr(args, "ack_no_snapshot", False)),
        "ack_external_message": bool(getattr(args, "ack_external_message", False)),
    }

    try:
        if is_local:
            if getattr(args, "command", "") == "onboarding":
                rc = int(args.func(args, ctx))
            elif getattr(args, "command", "") == "runs":
                rc = int(args.func(args, ctx))
            elif getattr(args, "command", "") == "auth":
                rc = int(args.func(args, ctx))
            else:
                raise NotSupportedError(f"Unsupported local command: {args.command}")
        else:
            assert isinstance(cfg, Config)
            timeout_s = float(args.timeout_s) if args.timeout_s is not None else cfg.timeout_s
            client = client_factory(cfg=cfg, timeout_s=timeout_s, verbose=bool(args.verbose), user_agent=NAME)
            ctx["cfg"] = cfg
            rc = _run_registry_command(args, cast(OperationSpec, registry_spec), ctx, client)

        if run_ctx.enabled:
            _finalize_run_artifacts(
                run_ctx=run_ctx,
                output_obj=out.last if isinstance(out.last, dict) else None,
                command=command_str,
                env_fingerprint=env_fingerprint,
                version=__version__,
                apply=bool(args.apply),
                yes=bool(args.yes),
                audit_log_path=run_log_path or global_log_path,
                audit_log_global_path=global_log_path,
            )
        return rc
    except SafetyError as e:
        out.emit({"ok": True, "refused": True, "reasons": [str(e)], "refusal_type": "SafetyError"})
        if run_ctx.enabled:
            _finalize_run_artifacts(
                run_ctx=run_ctx,
                output_obj=out.last if isinstance(out.last, dict) else None,
                command=command_str,
                env_fingerprint=env_fingerprint,
                version=__version__,
                apply=bool(args.apply),
                yes=bool(args.yes),
                audit_log_path=run_log_path or global_log_path,
                audit_log_global_path=global_log_path,
            )
        return 0
    except ToolError as e:
        out.emit({"ok": False, "error": str(e), "error_type": type(e).__name__})
        if run_ctx.enabled:
            _finalize_run_artifacts(
                run_ctx=run_ctx,
                output_obj=out.last if isinstance(out.last, dict) else None,
                command=command_str,
                env_fingerprint=env_fingerprint,
                version=__version__,
                apply=bool(args.apply),
                yes=bool(args.yes),
                audit_log_path=run_log_path or global_log_path,
                audit_log_global_path=global_log_path,
            )
        return 1
    except Exception as e:  # noqa: BLE001
        out.emit({"ok": False, "error_type": type(e).__name__})
        if run_ctx.enabled:
            _finalize_run_artifacts(
                run_ctx=run_ctx,
                output_obj=out.last if isinstance(out.last, dict) else None,
                command=command_str,
                env_fingerprint=env_fingerprint,
                version=__version__,
                apply=bool(args.apply),
                yes=bool(args.yes),
                audit_log_path=run_log_path or global_log_path,
                audit_log_global_path=global_log_path,
            )
        return 1
    finally:
        audit.close()
