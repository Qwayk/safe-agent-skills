from __future__ import annotations

import re
from typing import Any

from ..paapi import PaApiError
from ._shared import (
    PAAPI_MAX_BROWSE_NODE_IDS_PER_REQUEST,
    api_errors,
    batch_values,
    browse_nodes_from_paapi_response,
    build_paapi_client,
    resolve_resources,
    simplify_browse_node,
)

_BROWSE_NODE_RE = re.compile(r"^[0-9]+$")


def cmd_browse_get(args: Any, ctx: dict[str, Any]) -> int:
    ids = [str(a).strip() for a in (args.browse_node_id or []) if str(a).strip()]
    if not ids:
        raise RuntimeError("At least one --browse-node-id is required")
    bad = [i for i in ids if not _BROWSE_NODE_RE.fullmatch(i)]
    if bad:
        raise RuntimeError(f"Invalid browse node id(s): {', '.join(bad)}")

    resources = resolve_resources(
        preset=getattr(args, "resources_preset", None),
        resources=getattr(args, "resource", None),
        default_resources=[],
    )
    batch_size = int(getattr(args, "batch_size", PAAPI_MAX_BROWSE_NODE_IDS_PER_REQUEST))
    max_requests = getattr(args, "max_requests", None)
    max_requests_i = int(max_requests) if max_requests is not None else None
    batches = batch_values(
        ids,
        batch_size=batch_size,
        api_max_per_request=PAAPI_MAX_BROWSE_NODE_IDS_PER_REQUEST,
        max_requests=max_requests_i,
        yes=bool(ctx.get("yes")),
        what="browse.get",
    )

    client = build_paapi_client(ctx)
    nodes_out: list[dict[str, Any]] = []
    request_ids: list[str | None] = []
    raw_responses: list[dict[str, Any]] = []
    errors_by_request: list[dict[str, Any]] = []

    for batch in batches:
        try:
            resp = client.get_browse_nodes(browse_node_ids=batch, resources=resources or None)
        except PaApiError as e:
            raise RuntimeError(str(e)) from None

        request_ids.append(resp.request_id)
        raw_responses.append(resp.data)
        nodes = [simplify_browse_node(n) for n in browse_nodes_from_paapi_response(resp.data)]
        nodes_out.extend(nodes)

        errs = api_errors(resp.data)
        if errs:
            errors_by_request.append({"request_id": resp.request_id, "errors": errs})

    out: dict[str, Any] = {
        "ok": True,
        "requested": ids,
        "count": len(nodes_out),
        "browse_nodes": nodes_out,
    }
    if len(batches) == 1:
        out["request_id"] = request_ids[0]
    else:
        out["requests"] = len(batches)
        out["request_ids"] = request_ids
        out["batch_size"] = batch_size
        if max_requests_i is not None:
            out["max_requests"] = max_requests_i

    if bool(ctx.get("include_raw")):
        out["raw"] = raw_responses[0] if len(batches) == 1 else raw_responses
    if errors_by_request:
        out["api_errors"] = errors_by_request[0]["errors"] if len(batches) == 1 else errors_by_request

    ctx["audit"].write("browse.get", out)
    ctx["out"].emit(out)
    return 0

