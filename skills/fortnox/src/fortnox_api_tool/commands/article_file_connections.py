from __future__ import annotations

from typing import Any

from .wrapped_file_connections import (
    WrappedFileConnectionSpec,
    cmd_create as _cmd_create,
    cmd_get as _cmd_get,
    cmd_list as _cmd_list,
    cmd_remove as _cmd_remove,
)

SPEC = WrappedFileConnectionSpec(
    family_slug="article-file-connections",
    item_slug="article-file-connection",
    collection_key="ArticleFileConnections",
    item_key="ArticleFileConnection",
    payload_key="ArticleFileConnection",
    path="/articlefileconnections",
    list_query_params=(("article_number", "articlenumber"),),
    payload_required_keys=("ArticleNumber", "FileId"),
    singular_label="article file connection",
    plural_label="article file connections",
)


def cmd_article_file_connections_list(args: Any, ctx: dict[str, Any]) -> int:
    return _cmd_list(args, ctx, spec=SPEC)


def cmd_article_file_connections_get(args: Any, ctx: dict[str, Any]) -> int:
    return _cmd_get(args, ctx, spec=SPEC)


def cmd_article_file_connections_create(args: Any, ctx: dict[str, Any]) -> int:
    return _cmd_create(args, ctx, spec=SPEC)


def cmd_article_file_connections_remove(args: Any, ctx: dict[str, Any]) -> int:
    return _cmd_remove(args, ctx, spec=SPEC)
