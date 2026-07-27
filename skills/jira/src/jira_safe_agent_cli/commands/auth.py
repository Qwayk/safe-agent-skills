from __future__ import annotations

from typing import Any

from .. import __version__
from ..http import HttpClient
from ..operations import redact


def cmd_auth_check(args: Any, ctx: dict[str, Any]) -> int:
    config = ctx["config_loader"](require_auth=True)
    client = HttpClient(
        config=config, verbose=bool(args.verbose), user_agent=f"jira-safe/{__version__}"
    )
    response = client.request("GET", config.base_url + "/rest/api/3/myself", retries=2)
    body = redact(response.json()) if response.body else None
    payload = {
        "ok": True,
        "base_url": config.base_url,
        "auth_mode": config.auth_mode,
        "status": response.status,
        "account": body,
    }
    ctx["audit"].write(
        "auth.check",
        {"base_url": config.base_url, "auth_mode": config.auth_mode, "status": response.status},
    )
    ctx["out"].emit(payload)
    return 0
