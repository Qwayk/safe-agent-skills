from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Callable

from . import __version__
from .audit_log import AuditLogger
from .config import load_config, normalize_statuspage_base_url
from .errors import ToolError, ValidationError
from .output import Output
from .statuspage_client import StatuspageClient


class _ToolArgumentParser(argparse.ArgumentParser):
    """
    Ensure user-input errors can be surfaced as JSON.

    Argparse defaults to printing usage/help to stderr and raising SystemExit, which makes it
    hard to keep the `--output json` contract (exactly one JSON object to stdout on errors).
    """

    def error(self, message: str) -> None:  # type: ignore[override]
        raise ValidationError(message)


def _output_mode_from_argv(argv: list[str]) -> str:
    try:
        idx = argv.index("--output")
    except ValueError:
        return "json"
    if idx + 1 >= len(argv):
        return "json"
    v = str(argv[idx + 1] or "").strip()
    return v if v in {"json", "text"} else "json"


def _client_from_ctx(ctx: dict[str, Any]) -> StatuspageClient:
    cfg = ctx["cfg"]
    return StatuspageClient(
        base_url=cfg.base_url,
        timeout_s=float(ctx["timeout_s"]),
        verbose=bool(ctx["verbose"]),
        user_agent=f"statuspage-api-tool/{__version__}",
    )


def _emit_ok(ctx: dict[str, Any], *, endpoint: str, data: Any) -> None:
    audit: AuditLogger | None = ctx.get("audit")
    if audit is not None:
        try:
            audit.write("command.ok", {"endpoint": endpoint})
        except Exception:
            pass
    ctx["out"].emit({"ok": True, "base_url": ctx["cfg"].base_url, "endpoint": endpoint, "data": data})


def _cmd_auth_check(_args: argparse.Namespace, ctx: dict[str, Any]) -> int:
    out: Output = ctx["out"]
    audit: AuditLogger | None = ctx.get("audit")
    if audit is not None:
        try:
            audit.write("auth.check", {"required": False, "type": "none"})
        except Exception:
            pass
    out.emit(
        {
            "ok": True,
            "tool": "statuspage-api-tool",
            "auth": {"required": False, "type": "none"},
            "note": "This tool calls Statuspage public Status API endpoints and does not use authentication.",
        }
    )
    return 0


def _cmd_status_get(_args: argparse.Namespace, ctx: dict[str, Any]) -> int:
    data = _client_from_ctx(ctx).get_status()
    _emit_ok(ctx, endpoint="/api/v2/status.json", data=data)
    return 0


def _cmd_summary_get(_args: argparse.Namespace, ctx: dict[str, Any]) -> int:
    data = _client_from_ctx(ctx).get_summary()
    _emit_ok(ctx, endpoint="/api/v2/summary.json", data=data)
    return 0


def _cmd_incidents_list(_args: argparse.Namespace, ctx: dict[str, Any]) -> int:
    data = _client_from_ctx(ctx).list_incidents()
    _emit_ok(ctx, endpoint="/api/v2/incidents.json", data=data)
    return 0


def _cmd_maintenances_list(_args: argparse.Namespace, ctx: dict[str, Any]) -> int:
    data = _client_from_ctx(ctx).list_scheduled_maintenances()
    _emit_ok(ctx, endpoint="/api/v2/scheduled-maintenances.json", data=data)
    return 0


def _load_project_config(path: str | None) -> dict[str, str]:
    if not path:
        return {}
    p = Path(path)
    if not p.exists():
        raise ValidationError(f"Config file not found: {path}")
    try:
        raw = json.loads(p.read_text(encoding="utf-8"))
    except Exception as e:
        raise ValidationError(f"Invalid JSON in config file: {path}: {e}") from None
    if not isinstance(raw, dict):
        raise ValidationError("Config file must be a JSON object")
    allowed = {"base_url", "timeout_s"}
    unknown = sorted([k for k in raw.keys() if str(k) not in allowed])
    if unknown:
        raise ValidationError(f"Config file has unknown keys: {', '.join(unknown)}")

    out: dict[str, str] = {}
    if raw.get("base_url") is not None:
        out["STATUSPAGE_BASE_URL"] = str(raw.get("base_url") or "").strip()
    if raw.get("timeout_s") is not None:
        out["STATUSPAGE_TIMEOUT_S"] = str(raw.get("timeout_s") or "").strip()
    return out


def build_parser() -> argparse.ArgumentParser:
    p = _ToolArgumentParser(prog="statuspage-api-tool")
    p.add_argument("--version", action="store_true", help="Print version and exit")
    p.add_argument("--env-file", default=".env", help="Optional .env file path (default: .env)")
    p.add_argument("--config", default=None, help="Optional JSON config file (non-secret defaults)")
    p.add_argument("--base-url", default=None, help="Override Statuspage base URL (https://status.somevendor.com)")
    p.add_argument("--timeout-s", type=float, default=None, help="Override timeout seconds")
    p.add_argument("--log-file", default=None, help="Optional JSONL audit log path (no secrets)")
    p.add_argument("--verbose", action="store_true", help="Verbose HTTP logging to stderr")
    p.add_argument("--debug", action="store_true", help="Show stack traces on errors")
    p.add_argument("--output", choices=("json", "text"), default="json", help="Output format (default: json)")

    sub = p.add_subparsers(dest="cmd", required=False, parser_class=_ToolArgumentParser)

    auth = sub.add_parser("auth", help="Authentication (informational)")
    auth_sub = auth.add_subparsers(dest="auth_cmd", required=True, parser_class=_ToolArgumentParser)
    auth_check = auth_sub.add_parser("check", help="Show auth requirements (no API call)")
    auth_check.set_defaults(func=_cmd_auth_check)

    status = sub.add_parser("status", help="Current status")
    status_sub = status.add_subparsers(dest="status_cmd", required=True, parser_class=_ToolArgumentParser)
    status_get = status_sub.add_parser("get", help="Get current status (/api/v2/status.json)")
    status_get.set_defaults(func=_cmd_status_get)

    summary = sub.add_parser("summary", help="Summary")
    summary_sub = summary.add_subparsers(dest="summary_cmd", required=True, parser_class=_ToolArgumentParser)
    summary_get = summary_sub.add_parser("get", help="Get summary (/api/v2/summary.json)")
    summary_get.set_defaults(func=_cmd_summary_get)

    incidents = sub.add_parser("incidents", help="Incidents")
    incidents_sub = incidents.add_subparsers(dest="incidents_cmd", required=True, parser_class=_ToolArgumentParser)
    incidents_list = incidents_sub.add_parser("list", help="List incidents (/api/v2/incidents.json)")
    incidents_list.set_defaults(func=_cmd_incidents_list)

    maint = sub.add_parser("maintenances", help="Scheduled maintenances")
    maint_sub = maint.add_subparsers(dest="maint_cmd", required=True, parser_class=_ToolArgumentParser)
    maint_list = maint_sub.add_parser(
        "list", help="List scheduled maintenances (/api/v2/scheduled-maintenances.json)"
    )
    maint_list.set_defaults(func=_cmd_maintenances_list)

    return p


def main(argv: list[str]) -> int:
    parser = build_parser()
    out = Output(mode=_output_mode_from_argv(argv))
    try:
        args = parser.parse_args(argv)
    except ValidationError as e:
        out.emit({"ok": False, "error": str(e), "error_type": type(e).__name__})
        return 1
    except SystemExit as e:
        try:
            return int(e.code or 0)
        except Exception:
            return 0

    try:
        if bool(args.version):
            payload = {"ok": True, "tool": "statuspage-api-tool", "version": __version__}
            if args.output == "json":
                out.emit(payload)
            else:
                print(f"statuspage-api-tool {__version__}")
            return 0

        if not getattr(args, "cmd", None):
            parser.error("Missing command. Use --help to see available commands.")

        audit = AuditLogger(path=str(args.log_file) if args.log_file else None, enabled=bool(args.log_file))

        # Auth command is informational; it must not require config or network.
        if str(args.cmd) == "auth":
            ctx: dict[str, Any] = {"out": out, "audit": audit}
            func: Callable[[argparse.Namespace, dict[str, Any]], int] = getattr(args, "func")
            rc = int(func(args, ctx))
            audit.close()
            return rc

        config_defaults = _load_project_config(str(args.config) if args.config else None)
        # `--base-url` is meant to allow running without a `.env` file.
        # Set it as a default so `load_config()` doesn't fail on missing STATUSPAGE_BASE_URL.
        if args.base_url is not None and str(args.base_url).strip():
            config_defaults["STATUSPAGE_BASE_URL"] = str(args.base_url).strip()
        cfg = load_config(str(args.env_file), config_defaults=config_defaults)
        if args.base_url is not None and str(args.base_url).strip():
            cfg = type(cfg)(
                base_url=normalize_statuspage_base_url(str(args.base_url)),
                timeout_s=cfg.timeout_s,
            )
        timeout_s = float(args.timeout_s) if args.timeout_s is not None else float(cfg.timeout_s)

        ctx: dict[str, Any] = {
            "cfg": cfg,
            "out": out,
            "timeout_s": timeout_s,
            "verbose": bool(args.verbose),
            "audit": audit,
        }
        audit.bind_context(
            {
                "tool": "statuspage-api-tool",
                "version": __version__,
                "command": f"statuspage-api-tool {args.cmd}",
                "base_url": cfg.base_url,
            }
        )

        func: Callable[[argparse.Namespace, dict[str, Any]], int] = getattr(args, "func")
        rc = int(func(args, ctx))
        audit.close()
        return rc
    except ToolError as e:
        try:
            audit = locals().get("audit")
            if isinstance(audit, AuditLogger):
                audit.write("command.error", {"error_type": type(e).__name__, "error": str(e)[:500]})
                audit.close()
        except Exception:
            pass
        out.emit({"ok": False, "error": str(e), "error_type": type(e).__name__})
        return 1
    except Exception as e:  # noqa: BLE001
        if bool(getattr(args, "debug", False)):
            raise
        try:
            audit = locals().get("audit")
            if isinstance(audit, AuditLogger):
                audit.write("command.error", {"error_type": type(e).__name__, "error": str(e)[:500]})
                audit.close()
        except Exception:
            pass
        out.emit({"ok": False, "error": str(e), "error_type": type(e).__name__})
        return 1


def main_entrypoint() -> None:
    raise SystemExit(main(sys.argv[1:]))
