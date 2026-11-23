from __future__ import annotations

import shlex
from pathlib import Path

from ..config import load_config
from .common import write_private_file


def cmd_onboarding(args: object, ctx: dict) -> int:
    env_file = Path(ctx["env_file"])
    created = not env_file.exists() and not bool(getattr(args, "no_write_env", False))
    if created:
        example = env_file.with_name(".env.example")
        template = example.read_bytes() if example.is_file() else (
            b"AWIN_API_TOKEN=\n# AWIN_FEED_API_KEY=\n# AWIN_PROOF_OF_PURCHASE_API_KEY=\n"
        )
        write_private_file(env_file, template, overwrite=False)

    config = load_config(str(env_file), file_only=True)
    missing = [] if config.token else ["AWIN_API_TOKEN"]
    command = shlex.join(["awin-publisher-safe-cli", "--env-file", str(env_file), "--output", "json", "auth", "check"])
    steps = [f"Put your Awin API token in {env_file}.", f"Run {command}"]

    if str(getattr(args, "output", "json")) == "json":
        ctx["out"].emit({"ok": True, "onboarding": {
            "env_file": str(env_file), "env_created": created, "missing": missing,
            "next_command": command, "steps": steps,
        }})
    else:
        print("\n".join(steps))
    return 0
