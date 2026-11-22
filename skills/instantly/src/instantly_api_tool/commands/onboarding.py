from __future__ import annotations

import os
import shlex
from pathlib import Path

from ..config import _get, _parse_env_file


def cmd_onboarding(args: object, ctx: dict) -> int:
    env_file = str(getattr(args, "env_file", ".env"))
    env_path = Path(env_file)
    write_env = not bool(getattr(args, "no_write_env", False))
    env_created = False

    if write_env and not env_path.exists():
        example_path = env_path.parent / ".env.example"
        contents = example_path.read_text(encoding="utf-8") if example_path.is_file() else "INSTANTLY_API_KEY=\n"
        try:
            fd = os.open(env_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        except FileExistsError:
            pass
        else:
            with os.fdopen(fd, "w", encoding="utf-8") as file:
                file.write(contents)
            env_created = True

    key = _get(_parse_env_file(env_path), "INSTANTLY_API_KEY")
    missing = [] if key else ["INSTANTLY_API_KEY"]
    next_command = shlex.join(["instantly-api-tool", "--output", "json", "--env-file", env_file, "auth", "check"])
    steps = [
        "In Instantly, open Settings, then API Keys. Use a key with access to the work you want to do.",
        f"Set INSTANTLY_API_KEY in {env_file}. Keep the key out of chat and Git.",
        "Run the connection check below.",
    ]

    payload = {
        "ok": True,
        "onboarding": {
            "env_file": env_file,
            "env_created": env_created,
            "missing": missing,
            "next_command": next_command,
            "steps": steps,
        },
    }
    if str(getattr(args, "output", "json")) == "json":
        ctx["out"].emit(payload)
    else:
        for i, step in enumerate(steps, start=1):
            print(f"{i}. {step}")
        if missing:
            print(f"Missing settings: {', '.join(missing)}")
        print(next_command)
    return 0
