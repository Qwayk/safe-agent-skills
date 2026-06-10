from __future__ import annotations

from typing import Any

from ..commands.common import build_optional_params, build_read_params
from ..errors import ValidationError
from ..threads_client import ThreadsAPIClient


def _client(ctx: dict[str, Any]) -> ThreadsAPIClient:
    return ThreadsAPIClient(
        cfg=ctx["cfg"],
        env_file=ctx["env_file"],
        timeout_s=ctx["timeout_s"],
        verbose=ctx["verbose"],
    )


def cmd_search_keyword(args, ctx: dict[str, Any]) -> int:
    query = str(getattr(args, "q", "") or "").strip()
    if not query:
        raise ValidationError("Missing --q")
    params = build_read_params(args=args)
    params.update(build_optional_params(args=args, include_search_mode=True, include_search_type=True, include_media_type=True))
    params["q"] = query
    result = _client(ctx).search_keyword(query=query, params=params)
    out = {"ok": True, "command": "search.keyword", "result": result}
    ctx["audit"].write("search.keyword", out)
    ctx["out"].emit(out)
    return 0


def cmd_search_topic_tag(args, ctx: dict[str, Any]) -> int:
    topic_tag = str(getattr(args, "topic_tag", "") or "").strip()
    if not topic_tag:
        raise ValidationError("Missing --topic-tag")
    params = build_read_params(args=args)
    params.update(build_optional_params(args=args, include_search_mode=True, include_search_type=True, include_media_type=True))
    params["q"] = topic_tag
    result = _client(ctx).search_topic_tag(topic_tag=topic_tag, params=params)
    out = {"ok": True, "command": "search.topic-tag", "result": result}
    ctx["audit"].write("search.topic_tag", out)
    ctx["out"].emit(out)
    return 0


def cmd_search_recent_keywords(args, ctx: dict[str, Any]) -> int:
    _ = args
    result = _client(ctx).recently_searched_keywords()
    out = {"ok": True, "command": "search.recent-keywords", "result": result}
    ctx["audit"].write("search.recent_keywords", out)
    ctx["out"].emit(out)
    return 0
