from __future__ import annotations

import os
import shlex
from pathlib import Path

from ..config import _get, _parse_env_file


def cmd_onboarding(args: object, ctx: dict) -> int:
    out = ctx["out"]
    env_path = Path(getattr(args, "env_file", ".env"))
    env_created = False
    if not getattr(args, "no_write_env", False) and not env_path.exists():
        example = env_path.parent / ".env.example"
        template = (
            example.read_text(encoding="utf-8") if example.is_file()
            else "META_ADS_ACCESS_TOKEN=\nMETA_ADS_AD_ACCOUNT_ID=\n"
        )
        try:
            fd = os.open(env_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        except FileExistsError:
            pass
        else:
            with os.fdopen(fd, "w", encoding="utf-8") as env:
                env.write(template)
            env_created = True

    token_present = bool(_get(_parse_env_file(env_path), "META_ADS_ACCESS_TOKEN"))
    missing = [] if token_present else ["META_ADS_ACCESS_TOKEN"]
    next_command = "meta-ads-api-tool --output json"
    if str(env_path) != ".env":
        next_command += " --env-file " + shlex.quote(str(env_path))
    next_command += " auth check"
    steps = [
        f"Add your Meta access token to {env_path} as META_ADS_ACCESS_TOKEN, or set it in your shell.",
        "Set META_ADS_AD_ACCOUNT_ID if you want to save a default account.",
        "Run the account check, then list the accounts you can read.",
    ]
    payload = {
        "env_file": str(env_path),
        "env_created": env_created,
        "missing": missing,
        "next_command": next_command,
        "steps": steps,
    }
    if getattr(args, "output", "json") == "json":
        out.emit({"ok": True, "onboarding": payload})
    else:
        out.emit("\n".join([*steps, next_command]))
    return 0
