from __future__ import annotations

import os
import shlex
from pathlib import Path

from ..config import ENV_TEMPLATE, settings_values


def cmd_onboarding(args: object, ctx: dict) -> int:
    selected = getattr(args, "env_file", None)
    path = Path(selected or ".env")
    created = False

    if not getattr(args, "no_write_env", False) and not path.exists():
        example = path.parent / ".env.example"
        template = example.read_text(encoding="utf-8") if example.is_file() else ENV_TEMPLATE
        try:
            fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        except FileExistsError:
            pass
        else:
            with os.fdopen(fd, "w", encoding="utf-8") as file:
                file.write(template)
            created = True

    values = settings_values(selected)
    missing = [key for key in ("AWIN_API_TOKEN", "AWIN_ADVERTISER_ID") if not values.get(key)]
    flags = f" --env-file {shlex.quote(selected)}" if selected else ""
    next_command = f"awin-advertiser-safe-cli --output json{flags} auth check"
    result = {
        "env_file": str(path),
        "env_created": created,
        "missing": missing,
        "next_command": next_command,
        "steps": [
            f"Set AWIN_API_TOKEN and AWIN_ADVERTISER_ID in {path}. Keep this file private.",
            f"Run: {next_command}",
        ],
    }
    if getattr(args, "output", "json") == "json":
        ctx["out"].emit({"ok": True, "onboarding": result})
    else:
        print("\n".join(result["steps"]))
    return 0
