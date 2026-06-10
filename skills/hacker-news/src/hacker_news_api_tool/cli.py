from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import sys
from typing import Any, Callable, cast

from . import __version__
from .audit_log import AuditLogger
from .config import DEFAULT_HACKER_NEWS_API_ROOT, load_config, normalize_hacker_news_api_root
from .errors import ToolError, ValidationError
from .output import Output
from .hacker_news_client import HackerNewsClient


TOOL_NAME = "hacker-news-api-tool"


class _ToolArgumentParser(argparse.ArgumentParser):
    """
    Convert argparse errors to JSON-friendly exceptions.
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
    allowed = {"api_root", "base_url", "timeout_s"}
    unknown = sorted([k for k in raw.keys() if str(k) not in allowed])
    if unknown:
        raise ValidationError(f"Config file has unknown keys: {', '.join(unknown)}")

    out: dict[str, str] = {}
    if raw.get("api_root") is not None:
        out["HACKER_NEWS_API_ROOT"] = str(raw.get("api_root") or "").strip()
    elif raw.get("base_url") is not None:
        out["HACKER_NEWS_API_ROOT"] = str(raw.get("base_url") or "").strip()
    if raw.get("timeout_s") is not None:
        out["HACKER_NEWS_TIMEOUT_S"] = str(raw.get("timeout_s") or "").strip()
    return out


def _client_from_ctx(ctx: dict[str, Any]) -> HackerNewsClient:
    cfg = cast(Any, ctx["cfg"])
    return HackerNewsClient(
        api_root=cfg.api_root,
        timeout_s=float(ctx["timeout_s"]),
        verbose=bool(ctx["verbose"]),
        user_agent=f"{TOOL_NAME}/{__version__}",
    )


def _emit_ok(ctx: dict[str, Any], *, endpoint: str, data: Any) -> None:
    audit: AuditLogger | None = ctx.get("audit")
    if audit is not None:
        try:
            audit.write("command.ok", {"endpoint": endpoint})
        except Exception:
            pass
    ctx["out"].emit(
        {
            "ok": True,
            "tool": TOOL_NAME,
            "api_root": ctx["cfg"].api_root,
            "endpoint": endpoint,
            "data": data,
        }
    )


def _require_payload(kind: str, key: str | int, payload: Any) -> Any:
    if payload is None:
        raise ValidationError(f"{kind} '{key}' was not found.")
    return payload


def _cmd_onboarding(args: argparse.Namespace, ctx: dict[str, Any]) -> int:
    out: Output = ctx["out"]
    env_file = str(getattr(args, "env_file", ".env"))
    env_path = Path(env_file)
    example_path = env_path.parent / ".env.example"
    env_created = False

    if not bool(getattr(args, "no_write_env", False)) and not env_path.exists():
        if example_path.exists():
            env_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(example_path, env_path)
        else:
            env_path.parent.mkdir(parents=True, exist_ok=True)
            env_path.write_text("", encoding="utf-8")
        env_created = True

    out.emit(
        {
            "ok": True,
            "tool": TOOL_NAME,
            "env_file": env_file,
            "env_created": env_created,
            "notes": [
                "Hacker News API is public and read-only.",
                "Run `hacker-news-api-tool auth check` to verify live API access.",
                "No secrets are required.",
            ],
            "default_api_root": DEFAULT_HACKER_NEWS_API_ROOT,
            "commands": [
                "items get",
                "users get",
                "stories top",
                "stories new",
                "stories best",
                "stories ask",
                "stories show",
                "stories jobs",
                "maxitem get",
                "updates get",
            ],
        }
    )
    return 0


def _cmd_auth_check(_args: argparse.Namespace, ctx: dict[str, Any]) -> int:
    data = _client_from_ctx(ctx).get_maxitem()
    _emit_ok(
        ctx,
        endpoint="/v0/maxitem.json",
        data={
            "auth": {"required": False, "type": "none"},
            "note": "This tool uses public endpoints only. No secrets are needed.",
            "maxitem": data,
        },
    )
    return 0


def _cmd_items_get(args: argparse.Namespace, ctx: dict[str, Any]) -> int:
    data = _client_from_ctx(ctx).get_item(int(args.item_id))
    _emit_ok(ctx, endpoint=f"/v0/item/{int(args.item_id)}.json", data=_require_payload("Item", args.item_id, data))
    return 0


def _cmd_users_get(args: argparse.Namespace, ctx: dict[str, Any]) -> int:
    user_id = str(args.user_id)
    data = _client_from_ctx(ctx).get_user(user_id)
    _emit_ok(ctx, endpoint=f"/v0/user/{user_id}.json", data=_require_payload("User", user_id, data))
    return 0


def _cmd_stories_top(_args: argparse.Namespace, ctx: dict[str, Any]) -> int:
    data = _client_from_ctx(ctx).get_stories("top")
    _emit_ok(ctx, endpoint="/v0/topstories.json", data=data)
    return 0


def _cmd_stories_new(_args: argparse.Namespace, ctx: dict[str, Any]) -> int:
    data = _client_from_ctx(ctx).get_stories("new")
    _emit_ok(ctx, endpoint="/v0/newstories.json", data=data)
    return 0


def _cmd_stories_best(_args: argparse.Namespace, ctx: dict[str, Any]) -> int:
    data = _client_from_ctx(ctx).get_stories("best")
    _emit_ok(ctx, endpoint="/v0/beststories.json", data=data)
    return 0


def _cmd_stories_ask(_args: argparse.Namespace, ctx: dict[str, Any]) -> int:
    data = _client_from_ctx(ctx).get_stories("ask")
    _emit_ok(ctx, endpoint="/v0/askstories.json", data=data)
    return 0


def _cmd_stories_show(_args: argparse.Namespace, ctx: dict[str, Any]) -> int:
    data = _client_from_ctx(ctx).get_stories("show")
    _emit_ok(ctx, endpoint="/v0/showstories.json", data=data)
    return 0


def _cmd_stories_jobs(_args: argparse.Namespace, ctx: dict[str, Any]) -> int:
    data = _client_from_ctx(ctx).get_stories("job")
    _emit_ok(ctx, endpoint="/v0/jobstories.json", data=data)
    return 0


def _cmd_maxitem_get(_args: argparse.Namespace, ctx: dict[str, Any]) -> int:
    data = _client_from_ctx(ctx).get_maxitem()
    _emit_ok(ctx, endpoint="/v0/maxitem.json", data=data)
    return 0


def _cmd_updates_get(_args: argparse.Namespace, ctx: dict[str, Any]) -> int:
    data = _client_from_ctx(ctx).get_updates()
    _emit_ok(ctx, endpoint="/v0/updates.json", data=data)
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = _ToolArgumentParser(prog=TOOL_NAME)
    p.add_argument("--version", action="store_true", help="Print version and exit")
    p.add_argument("--env-file", default=".env", help="Optional .env file path (default: .env)")
    p.add_argument("--config", default=None, help="Optional JSON config file (non-secret defaults)")
    p.add_argument("--api-root", "--base-url", dest="api_root", default=None, help="Override Hacker News API root")
    p.add_argument("--timeout-s", type=float, default=None, help="Override timeout seconds")
    p.add_argument("--log-file", default=None, help="Optional JSONL audit log path (no secrets)")
    p.add_argument("--verbose", action="store_true", help="Verbose HTTP logging to stderr")
    p.add_argument("--debug", action="store_true", help="Show stack traces on errors")
    p.add_argument("--output", choices=("json", "text"), default="json", help="Output format (default: json)")

    sub = p.add_subparsers(dest="cmd", required=False, parser_class=_ToolArgumentParser)

    onboarding = sub.add_parser("onboarding", help="First-time setup help (no secrets)")
    onboarding.add_argument("--no-write-env", action="store_true", help="Do not write a local .env file")
    onboarding.set_defaults(func=_cmd_onboarding)

    auth = sub.add_parser("auth", help="Authentication checks")
    auth_sub = auth.add_subparsers(dest="auth_cmd", required=True, parser_class=_ToolArgumentParser)
    auth_check = auth_sub.add_parser("check", help="Check auth requirements with a live read")
    auth_check.set_defaults(func=_cmd_auth_check)

    items = sub.add_parser("items", help="Items")
    items_sub = items.add_subparsers(dest="items_cmd", required=True, parser_class=_ToolArgumentParser)
    items_get = items_sub.add_parser("get", help="Get one item by ID")
    items_get.add_argument("--id", dest="item_id", required=True, type=int, help="Hacker News item ID")
    items_get.set_defaults(func=_cmd_items_get)

    users = sub.add_parser("users", help="Users")
    users_sub = users.add_subparsers(dest="users_cmd", required=True, parser_class=_ToolArgumentParser)
    users_get = users_sub.add_parser("get", help="Get one user by ID")
    users_get.add_argument("--id", dest="user_id", required=True, type=str, help="Hacker News username")
    users_get.set_defaults(func=_cmd_users_get)

    stories = sub.add_parser("stories", help="Story IDs")
    stories_sub = stories.add_subparsers(dest="stories_cmd", required=True, parser_class=_ToolArgumentParser)
    stories_sub.add_parser("top", help="Top stories").set_defaults(func=_cmd_stories_top)
    stories_sub.add_parser("new", help="New stories").set_defaults(func=_cmd_stories_new)
    stories_sub.add_parser("best", help="Best stories").set_defaults(func=_cmd_stories_best)
    stories_sub.add_parser("ask", help="Ask HN stories").set_defaults(func=_cmd_stories_ask)
    stories_sub.add_parser("show", help="Show HN stories").set_defaults(func=_cmd_stories_show)
    stories_sub.add_parser("jobs", help="Job stories").set_defaults(func=_cmd_stories_jobs)

    maxitem = sub.add_parser("maxitem", help="Max item endpoint")
    maxitem_sub = maxitem.add_subparsers(dest="maxitem_cmd", required=True, parser_class=_ToolArgumentParser)
    maxitem_sub.add_parser("get", help="Get current max item ID").set_defaults(func=_cmd_maxitem_get)

    updates = sub.add_parser("updates", help="Latest changes")
    updates_sub = updates.add_subparsers(dest="updates_cmd", required=True, parser_class=_ToolArgumentParser)
    updates_sub.add_parser("get", help="Get latest item/user updates").set_defaults(func=_cmd_updates_get)

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
            payload = {"ok": True, "tool": TOOL_NAME, "version": __version__}
            if args.output == "json":
                out.emit(payload)
            else:
                print(f"{TOOL_NAME} {__version__}")
            return 0

        if not getattr(args, "cmd", None):
            parser.error("Missing command. Use --help to see available commands.")

        audit = AuditLogger(path=str(args.log_file) if args.log_file else None, enabled=bool(args.log_file))

        config_defaults = _load_project_config(str(args.config) if args.config else None)
        if args.api_root is not None and str(args.api_root).strip():
            config_defaults["HACKER_NEWS_API_ROOT"] = normalize_hacker_news_api_root(str(args.api_root))

        cfg = load_config(str(args.env_file), config_defaults=config_defaults)
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
                "tool": TOOL_NAME,
                "version": __version__,
                "command": f"{TOOL_NAME} {args.cmd}",
                "api_root": cfg.api_root,
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
        out.emit({"ok": False, "error": str(e), "error_type": "RuntimeError"})
        return 1


def main_entrypoint() -> None:
    raise SystemExit(main(sys.argv[1:]))
