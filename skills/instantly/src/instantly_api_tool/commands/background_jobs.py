from __future__ import annotations

from typing import Any

from ..errors import ValidationError
from ..http import HttpClient
from ..instantly_client import InstantlyClient


def _client(ctx: dict) -> InstantlyClient:
    cfg = ctx["cfg"]
    http = HttpClient(timeout_s=float(ctx["timeout_s"]), verbose=bool(ctx.get("verbose")), user_agent="instantly-api-tool")
    return InstantlyClient(cfg=cfg, http=http)


def _pagination_params(args: Any) -> dict[str, Any]:
    params: dict[str, Any] = {}
    if getattr(args, "limit", None) is not None:
        params["limit"] = int(args.limit)
    if getattr(args, "starting_after", None):
        params["starting_after"] = str(args.starting_after).strip()
    return params


def cmd_background_jobs_list(args: Any, ctx: dict) -> int:
    client = _client(ctx)
    res = client.get("/background-jobs", params=_pagination_params(args))
    out = {"ok": True, "jobs": res.data, "next_starting_after": res.next_starting_after}
    ctx["audit"].write("background_jobs.list", {"ok": True})
    ctx["out"].emit(out)
    return 0


def cmd_background_jobs_get(args: Any, ctx: dict) -> int:
    job_id = str(getattr(args, "job_id", "") or "").strip()
    if not job_id:
        raise ValidationError("Missing --job-id")
    client = _client(ctx)
    res = client.get(f"/background-jobs/{job_id}")
    out = {"ok": True, "job": res.data}
    ctx["audit"].write("background_jobs.get", {"ok": True})
    ctx["out"].emit(out)
    return 0

