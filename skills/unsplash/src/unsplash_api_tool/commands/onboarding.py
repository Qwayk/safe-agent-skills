from __future__ import annotations

import os
import shlex
from pathlib import Path

from ..auth_store import auth_path_for_env_file, get_access_key_from_store
from ..config import load_config


def cmd_onboarding(args: object, ctx: dict) -> int:
    out = ctx["out"]
    env_file = str(getattr(args, "env_file", ".env"))
    env_path = Path(env_file).expanduser()
    write_env = not bool(getattr(args, "no_write_env", False))
    created = False

    if write_env and not env_path.exists():
        env_path.parent.mkdir(parents=True, exist_ok=True)
        example = env_path.parent / ".env.example"
        contents = example.read_text(encoding="utf-8") if example.exists() else "UNSPLASH_ACCESS_KEY=\n"
        fd = os.open(env_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            stream.write(contents)
        created = True

    config = load_config(str(env_path))
    access_key = config.access_key or get_access_key_from_store(auth_path_for_env_file(str(env_path)))
    missing = [] if access_key else ["UNSPLASH_ACCESS_KEY"]
    next_command = shlex.join(["unsplash-api-tool", "--output", "json", "--env-file", str(env_path), "auth", "check"])
    steps = []
    if missing:
        steps.append(f"Put your Unsplash Access Key in {env_path} as UNSPLASH_ACCESS_KEY. Keep it private.")
    steps.append(f"Check the connection with {next_command}.")

    if str(getattr(args, "output", "json")) == "json":
        out.emit({
            "ok": True,
            "onboarding": {
                "env_file": str(env_path), "env_created": created, "missing": missing,
                "next_command": next_command, "steps": steps,
            },
        })
    else:
        print("\n".join(steps))
    return 0
