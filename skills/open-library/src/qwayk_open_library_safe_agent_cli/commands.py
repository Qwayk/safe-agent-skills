from __future__ import annotations

from pathlib import Path

from . import __version__
from .api_helpers import get_json
from .config import Config
from .errors import ValidationError


_TOOL = "qwayk-open-library-safe-agent-cli"


def _run_get(*, cfg: Config, ctx: dict, endpoint: str, params: dict[str, object] | None) -> int:
    client = ctx["http_client"]
    payload = get_json(client=client, base_url=cfg.base_url, endpoint=endpoint, params=params)
    out = {
        "ok": True,
        "tool": _TOOL,
        "version": __version__,
        "path": endpoint,
        "data": payload,
    }
    if params:
        out["params"] = params
    ctx["out"].emit(out)
    return 0


def cmd_onboarding(args, ctx) -> int:
    _ = args
    out = ctx["out"]
    env_file = str(ctx.get("env_file") or ".env")
    env_path = Path(env_file)
    env_created = False

    if not env_path.exists():
        # Resolve .env.example next to cwd, then package root, then src root.
        example_path = Path(".env.example")
        if not example_path.exists():
            alt_root = Path(__file__).resolve().parents[2] / ".env.example"
            if alt_root.exists():
                example_path = alt_root
            else:
                alt_root = Path(__file__).resolve().parents[1] / ".." / ".env.example"
                if alt_root.exists():
                    example_path = alt_root
        if example_path.exists():
            env_path.write_text(example_path.read_text(encoding="utf-8"), encoding="utf-8")
        else:
            env_path.write_text("", encoding="utf-8")
        env_created = True

    out.emit(
        {
            "ok": True,
            "tool": _TOOL,
            "version": __version__,
            "onboarding": {
                "env_file": env_file,
                "env_created": env_created,
                "missing": [],
                "optional": [
                    "OPEN_LIBRARY_CONTACT",
                    "OPEN_LIBRARY_USER_AGENT_APP",
                ],
                "note": (
                    "This tool is read-only and needs no auth key for Open Library public endpoints. "
                    "Set OPEN_LIBRARY_CONTACT and OPEN_LIBRARY_USER_AGENT_APP to improve identification during low-volume use."
                ),
                "next_command": f"{_TOOL} --output json search books --q <text>",
            },
        }
    )
    return 0


def cmd_search_books(args, ctx) -> int:
    params: dict[str, object] = {"q": str(args.q)}
    if args.fields is not None:
        params["fields"] = args.fields
    if args.sort is not None:
        params["sort"] = args.sort
    if args.lang is not None:
        params["lang"] = args.lang
    if args.limit is not None:
        params["limit"] = args.limit
    if args.page is not None:
        params["page"] = args.page
    if args.offset is not None:
        params["offset"] = args.offset
    return _run_get(cfg=ctx["cfg"], ctx=ctx, endpoint="search.json", params=params)


def cmd_search_authors(args, ctx) -> int:
    params: dict[str, object] = {"q": str(args.q)}
    if args.limit is not None:
        params["limit"] = args.limit
    if args.offset is not None:
        params["offset"] = args.offset
    return _run_get(cfg=ctx["cfg"], ctx=ctx, endpoint="search/authors.json", params=params)


def cmd_works_get(args, ctx) -> int:
    work_id = str(args.work_id).strip()
    if not work_id:
        raise ValidationError("work_id is required")
    return _run_get(cfg=ctx["cfg"], ctx=ctx, endpoint=f"works/{work_id}.json", params=None)


def cmd_works_editions_list(args, ctx) -> int:
    work_id = str(args.work_id).strip()
    if not work_id:
        raise ValidationError("work_id is required")
    params: dict[str, object] = {}
    if args.limit is not None:
        params["limit"] = args.limit
    if args.offset is not None:
        params["offset"] = args.offset
    return _run_get(cfg=ctx["cfg"], ctx=ctx, endpoint=f"works/{work_id}/editions.json", params=params or None)


def cmd_editions_get(args, ctx) -> int:
    edition_id = str(args.edition_id).strip()
    if not edition_id:
        raise ValidationError("edition_id is required")
    return _run_get(cfg=ctx["cfg"], ctx=ctx, endpoint=f"books/{edition_id}.json", params=None)


def cmd_isbn_lookup(args, ctx) -> int:
    isbn = str(args.isbn).strip()
    if not isbn:
        raise ValidationError("isbn is required")
    return _run_get(cfg=ctx["cfg"], ctx=ctx, endpoint=f"isbn/{isbn}.json", params=None)


def cmd_authors_get(args, ctx) -> int:
    author_id = str(args.author_id).strip()
    if not author_id:
        raise ValidationError("author_id is required")
    return _run_get(cfg=ctx["cfg"], ctx=ctx, endpoint=f"authors/{author_id}.json", params=None)


def cmd_authors_works_list(args, ctx) -> int:
    author_id = str(args.author_id).strip()
    if not author_id:
        raise ValidationError("author_id is required")
    params: dict[str, object] = {}
    if args.limit is not None:
        params["limit"] = args.limit
    if args.offset is not None:
        params["offset"] = args.offset
    return _run_get(cfg=ctx["cfg"], ctx=ctx, endpoint=f"authors/{author_id}/works.json", params=params or None)


def cmd_subjects_get(args, ctx) -> int:
    subject = str(args.subject).strip()
    if not subject:
        raise ValidationError("subject is required")
    params: dict[str, object] = {}
    if args.details:
        params["details"] = "true"
    if args.ebooks:
        params["ebooks"] = "true"
    if args.published_in is not None:
        params["published_in"] = args.published_in
    if args.limit is not None:
        params["limit"] = args.limit
    if args.offset is not None:
        params["offset"] = args.offset
    return _run_get(cfg=ctx["cfg"], ctx=ctx, endpoint=f"subjects/{subject}.json", params=params or None)
