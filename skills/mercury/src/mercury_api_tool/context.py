from __future__ import annotations

from typing import Any

from .http import HttpClient
from .mercury_client import MercuryClient


def build_mercury_client(ctx: dict[str, Any]) -> MercuryClient:
    cfg = ctx["cfg"]
    timeout_s = float(ctx["timeout_s"])
    verbose = bool(ctx.get("verbose"))
    tool = str(ctx.get("tool") or "mercury-api-tool")
    version = str(ctx.get("tool_version") or "0.0.0")
    http = HttpClient(timeout_s=timeout_s, verbose=verbose, user_agent=f"{tool}/{version}")
    return MercuryClient(cfg=cfg, http=http)
