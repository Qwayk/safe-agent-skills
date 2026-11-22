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
        template = example.read_text(encoding="utf-8") if example.is_file() else "OPENAI_ADS_API_KEY=\n"
        try:
            fd = os.open(env_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        except FileExistsError:
            pass
        else:
            with os.fdopen(fd, "w", encoding="utf-8") as env:
                env.write(template)
            env_created = True

    key_present = bool(_get(_parse_env_file(env_path), "OPENAI_ADS_API_KEY"))
    missing = [] if key_present else ["OPENAI_ADS_API_KEY"]
    next_command = "openai-ads-safe-agent-cli --output json"
    if str(env_path) != ".env":
        next_command += " --env-file " + shlex.quote(str(env_path))
    next_command += " auth check"
    steps = [
        f"Add the Ads Manager key to {env_path} as OPENAI_ADS_API_KEY, or set it in your shell.",
        "Run the account check to see which Ads account the key can read.",
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
