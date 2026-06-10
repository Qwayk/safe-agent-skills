from __future__ import annotations

import argparse
import sys

from . import __version__
from .api_helpers import normalize_isbn, normalize_ol_id, normalize_subject
from .audit_log import AuditLogger
from .commands import (
    cmd_authors_get,
    cmd_authors_works_list,
    cmd_editions_get,
    cmd_isbn_lookup,
    cmd_onboarding,
    cmd_search_authors,
    cmd_search_books,
    cmd_subjects_get,
    cmd_works_editions_list,
    cmd_works_get,
)
from .config import load_config
from .errors import ValidationError
from .http import HttpClient
from .output import Output

_TOOL = "qwayk-open-library-safe-agent-cli"


class _ToolArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:  # type: ignore[override]
        raise ValidationError(message)


def _output_mode_from_argv(argv: list[str]) -> str:
    try:
        idx = argv.index("--output")
    except ValueError:
        return "json"
    if idx + 1 >= len(argv):
        return "json"
    v = str(argv[idx + 1]).strip()
    return v if v in {"json", "text"} else "json"


def build_parser() -> argparse.ArgumentParser:
    p = _ToolArgumentParser(prog=_TOOL)
    p.add_argument("--version", action="store_true", help="Print version and exit")
    p.add_argument("--config", default=None, help="Optional JSON file for request defaults")
    p.add_argument("--env-file", default=".env", help="Optional .env file path (default: .env)")
    p.add_argument("--timeout-s", type=float, default=None, help="Override timeout seconds")
    p.add_argument("--verbose", action="store_true", help="Verbose HTTP logging to stderr")
    p.add_argument("--debug", action="store_true", help="Show stack traces on errors")
    p.add_argument("--log-file", default=None, help="Optional audit log path (JSONL)")
    p.add_argument("--output", choices=("json", "text"), default="json", help="Output format (default: json)")

    sub = p.add_subparsers(dest="cmd", required=False, parser_class=_ToolArgumentParser)

    onb = sub.add_parser("onboarding", help="Create .env from .env.example and show no-auth setup")
    onb.set_defaults(func=cmd_onboarding)

    search = sub.add_parser("search", help="Search Open Library")
    search_sub = search.add_subparsers(dest="search_cmd", required=True, parser_class=_ToolArgumentParser)
    books = search_sub.add_parser("books", help="Search books")
    books.add_argument("--q", required=True, help="Search query")
    books.add_argument("--fields", default=None, help="Fields to return")
    books.add_argument("--sort", default=None, help="Sort order")
    books.add_argument("--lang", default=None, help="Language filter")
    books.add_argument("--limit", type=int, default=None)
    books.add_argument("--page", type=int, default=None)
    books.add_argument("--offset", type=int, default=None)
    books.set_defaults(func=cmd_search_books)

    authors_search = search_sub.add_parser("authors", help="Search authors")
    authors_search.add_argument("--q", required=True, help="Search query")
    authors_search.add_argument("--limit", type=int, default=None)
    authors_search.add_argument("--offset", type=int, default=None)
    authors_search.set_defaults(func=cmd_search_authors)

    works = sub.add_parser("works", help="Work commands")
    works_sub = works.add_subparsers(dest="works_cmd", required=True, parser_class=_ToolArgumentParser)
    w_get = works_sub.add_parser("get", help="Get one work")
    w_get.add_argument("work_id")
    w_get.set_defaults(func=cmd_works_get)
    w_editions = works_sub.add_parser("editions", help="List work editions")
    w_editions_sub = w_editions.add_subparsers(dest="works_editions_cmd", required=True, parser_class=_ToolArgumentParser)
    w_editions_list = w_editions_sub.add_parser("list", help="List work editions")
    w_editions_list.add_argument("work_id")
    w_editions_list.add_argument("--limit", type=int, default=None)
    w_editions_list.add_argument("--offset", type=int, default=None)
    w_editions_list.set_defaults(func=cmd_works_editions_list)

    editions = sub.add_parser("editions", help="Edition commands")
    e_sub = editions.add_subparsers(dest="editions_cmd", required=True, parser_class=_ToolArgumentParser)
    e_get = e_sub.add_parser("get", help="Get one edition")
    e_get.add_argument("edition_id")
    e_get.set_defaults(func=cmd_editions_get)

    isbn = sub.add_parser("isbn", help="ISBN lookup")
    isbn_sub = isbn.add_subparsers(dest="isbn_cmd", required=True, parser_class=_ToolArgumentParser)
    isbn_lookup = isbn_sub.add_parser("lookup", help="Lookup by ISBN")
    isbn_lookup.add_argument("isbn")
    isbn_lookup.set_defaults(func=cmd_isbn_lookup)

    authors = sub.add_parser("authors", help="Author commands")
    authors_sub = authors.add_subparsers(dest="authors_cmd", required=True, parser_class=_ToolArgumentParser)
    a_get = authors_sub.add_parser("get", help="Get one author")
    a_get.add_argument("author_id")
    a_get.set_defaults(func=cmd_authors_get)
    a_works = authors_sub.add_parser("works", help="Works by author")
    a_works_sub = a_works.add_subparsers(dest="authors_works_cmd", required=True, parser_class=_ToolArgumentParser)
    a_works_list = a_works_sub.add_parser("list", help="List author works")
    a_works_list.add_argument("author_id")
    a_works_list.add_argument("--limit", type=int, default=None)
    a_works_list.add_argument("--offset", type=int, default=None)
    a_works_list.set_defaults(func=cmd_authors_works_list)

    subjects = sub.add_parser("subjects", help="Subject commands")
    subjects_sub = subjects.add_subparsers(dest="subjects_cmd", required=True, parser_class=_ToolArgumentParser)
    subjects_get = subjects_sub.add_parser("get", help="Get subject details")
    subjects_get.add_argument("subject")
    subjects_get.add_argument("--details", action="store_true", help="Include extra details")
    subjects_get.add_argument("--ebooks", action="store_true", help="Only include works with ebooks")
    subjects_get.add_argument("--published-in", dest="published_in", default=None, help="Filter by publish year")
    subjects_get.add_argument("--limit", type=int, default=None)
    subjects_get.add_argument("--offset", type=int, default=None)
    subjects_get.set_defaults(func=cmd_subjects_get)

    return p


def _normalize_command_args(args: argparse.Namespace) -> None:
    if args.cmd == "search":
        return

    if args.cmd == "works":
        if args.works_cmd == "get":
            args.work_id = normalize_ol_id(args.work_id, expected_prefix="works")
            return
        if args.works_cmd == "editions" and args.works_editions_cmd == "list":
            args.work_id = normalize_ol_id(args.work_id, expected_prefix="works")
            return

    if args.cmd == "editions":
        args.edition_id = normalize_ol_id(args.edition_id, expected_prefix="books")
        return

    if args.cmd == "authors":
        if args.authors_cmd == "get":
            args.author_id = normalize_ol_id(args.author_id, expected_prefix="authors")
        elif args.authors_cmd == "works":
            args.author_id = normalize_ol_id(args.author_id, expected_prefix="authors")
        return

    if args.cmd == "isbn":
        if getattr(args, "isbn_cmd", "") != "lookup":
            raise ValidationError("Expected isbn lookup command")
        args.isbn = normalize_isbn(args.isbn)
        return

    if args.cmd == "subjects":
        if getattr(args, "subjects_cmd", "") != "get":
            raise ValidationError("Expected subjects get command")
        args.subject = normalize_subject(args.subject)
        return


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

    if bool(args.version):
        out.emit({"ok": True, "tool": _TOOL, "version": __version__})
        return 0

    if not getattr(args, "cmd", None):
        out.emit({"ok": False, "error": "Missing command. Use --help.", "error_type": "ValidationError"})
        return 1

    audit = AuditLogger(path=args.log_file, enabled=bool(args.log_file))
    audit.bind_context({"tool": _TOOL, "version": __version__, "command": f"{_TOOL} {' '.join(argv)}"})
    audit.write("command_start", {"argv": argv})

    try:
        _normalize_command_args(args)
        ctx = {
            "out": out,
            "env_file": str(getattr(args, "env_file", ".env")),
            "audit": audit,
        }

        if getattr(args, "cmd", "") == "onboarding":
            rc = int(args.func(args, ctx))
            audit.write("command_ok", {"exit_code": rc, "output": out.last})
            return rc

        cfg = load_config(str(getattr(args, "env_file", ".env")), config_file=getattr(args, "config", None))
        timeout = args.timeout_s if args.timeout_s is not None else cfg.timeout_s
        if timeout <= 0:
            raise ValidationError("--timeout-s must be > 0")

        cfg = cfg.__class__(
            base_url=cfg.base_url,
            timeout_s=timeout,
            user_agent_app=cfg.user_agent_app,
            contact=cfg.contact,
        )
        user_agent = cfg.user_agent_app
        if cfg.contact:
            user_agent = f"{cfg.user_agent_app} ({cfg.contact})"

        http = HttpClient(
            timeout_s=cfg.timeout_s,
            verbose=bool(args.verbose),
            user_agent=user_agent,
        )

        ctx.update(
            {
                "cfg": cfg,
                "http_client": http,
                "debug": bool(args.debug),
            }
        )

        rc = int(args.func(args, ctx))
        audit.write("command_ok", {"exit_code": rc, "output": out.last})
        return rc
    except ValidationError as e:
        audit.write("command_error", {"exit_code": 1, "error_type": "ValidationError", "error": str(e)})
        out.emit({"ok": False, "error": str(e), "error_type": "ValidationError"})
        return 1
    except Exception as e:  # noqa: BLE001
        audit.write("command_error", {"exit_code": 1, "error_type": type(e).__name__, "error": str(e)})
        if bool(args.debug):
            raise
        out.emit({"ok": False, "error": str(e), "error_type": type(e).__name__})
        return 1
    finally:
        audit.close()


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
