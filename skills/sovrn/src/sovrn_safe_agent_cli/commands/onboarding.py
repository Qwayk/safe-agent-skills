from __future__ import annotations

import os
import shlex
from pathlib import Path

from ..config import SETUP_KEYS, settings_values


def cmd_onboarding(args: object, ctx: dict) -> int:
    selected = getattr(args, "env_file", None)
    path = Path(selected or ".env")
    created = False

    if not getattr(args, "no_write_env", False) and not path.exists():
        example = path.parent / ".env.example"
        template = example.read_text(encoding="utf-8") if example.is_file() else "".join(
            f"{key}=\n" for key in SETUP_KEYS
        )
        try:
            fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        except FileExistsError:
            pass
        else:
            with os.fdopen(fd, "w", encoding="utf-8") as file:
                file.write(template)
            created = True

    values = settings_values(selected)
    missing = [key for key in SETUP_KEYS if not values.get(key)]
    flags = f" --env-file {shlex.quote(selected)}" if selected else ""
    next_command = f"sovrn-safe-cli --output json{flags} auth check"
    steps = [
        f"Open {path} and add only the settings for the job you want to do. Keep the file private.",
        "Link checks use the Commerce site API key. Commerce reports use the Commerce secret key.",
        "Advertising reports use the Advertising key and publisher ID.",
        f"Run: {next_command}",
    ]
    result = {
        "env_file": str(path),
        "env_created": created,
        "missing": missing,
        "next_command": next_command,
        "steps": steps,
    }
    if getattr(args, "output", "json") == "json":
        ctx["out"].emit({"ok": True, "onboarding": result})
    else:
        print("\n".join(steps))
    return 0
