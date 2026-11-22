from __future__ import annotations

import os
import shlex
from pathlib import Path

from ..config import _get, _parse_env_file
from ..oauth_tokens import read_access_token_from_file, token_path_for_env_file

_DEFAULT_SETTINGS = """# Use the credentials for the Wix account or site you want to check.
WIX_API_KEY=
WIX_ACCOUNT_ID=
WIX_APP_ID=
WIX_APP_SECRET=
WIX_INSTANCE_ID=
WIX_ACCESS_TOKEN=
"""


def cmd_onboarding(args: object, ctx: dict) -> int:
    env_file = str(getattr(args, "env_file", ".env"))
    env_path = Path(env_file)
    env_created = False
    if not bool(getattr(args, "no_write_env", False)) and not env_path.exists():
        env_path.parent.mkdir(parents=True, exist_ok=True)
        example = env_path.parent / ".env.example"
        settings = example.read_text() if example.is_file() else _DEFAULT_SETTINGS
        try:
            with open(env_path, "x", opener=_open_private) as handle:
                handle.write(settings)
            env_created = True
        except FileExistsError:
            pass

    settings = _parse_env_file(env_path)
    saved_token = read_access_token_from_file(token_path_for_env_file(env_file))
    account_ready = all(_get(settings, key) for key in ("WIX_API_KEY", "WIX_ACCOUNT_ID"))
    app_ready = all(_get(settings, key) for key in ("WIX_APP_ID", "WIX_APP_SECRET", "WIX_INSTANCE_ID"))
    site_ready = bool(_get(settings, "WIX_ACCESS_TOKEN") or saved_token or app_ready)
    if site_ready or account_ready:
        missing = []
    else:
        missing = ["WIX_API_KEY and WIX_ACCOUNT_ID, or an app token or app credentials"]

    command = f"wix-safe-agent-cli --output json --env-file {shlex.quote(env_file)} auth check"
    steps = [
        f"Keep {env_file} private.",
        "To list sites in an account, set WIX_API_KEY and WIX_ACCOUNT_ID.",
        "For a site app, set WIX_ACCESS_TOKEN or WIX_APP_ID, WIX_APP_SECRET, and WIX_INSTANCE_ID.",
        f"Run {command}",
    ]
    ctx["out"].emit({
        "ok": True,
        "onboarding": {
            "env_file": env_file,
            "env_created": env_created,
            "missing": missing,
            "readiness": {"account": account_ready, "site_app": site_ready},
            "next_command": command,
            "steps": steps,
        },
    })
    return 0


def _open_private(path, flags):
    return os.open(path, flags, 0o600)
