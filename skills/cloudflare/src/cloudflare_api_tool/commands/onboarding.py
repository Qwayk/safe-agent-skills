from __future__ import annotations

import shlex
from pathlib import Path

from ..config import load_config
from .config_local import write_settings_file


def cmd_onboarding(args: object, ctx: dict) -> int:
    env_file = Path(ctx["env_file"]).expanduser()
    should_write = not bool(getattr(args, "no_write_env", False))
    created = should_write and not env_file.exists()
    if created:
        write_settings_file(env_file, env_file.parent / ".env.example")

    cfg = load_config(str(env_file), require_env_file=env_file.exists(), env_file_only=True)
    missing = [] if cfg.token else ["CLOUDFLARE_API_TOKEN"]
    command = shlex.join(["cloudflare-api-tool", "--env-file", str(env_file), "--output", "json", "auth", "check"])
    steps = [f"Put your Cloudflare API token in {env_file}.", f"Run {command}"]
    if str(getattr(args, "output", "json")) == "json":
        ctx["out"].emit({"ok": True, "onboarding": {
            "env_file": str(env_file), "env_created": created, "missing": missing,
            "next_command": command, "steps": steps,
        }})
    else:
        print("\n".join(steps))
    return 0
