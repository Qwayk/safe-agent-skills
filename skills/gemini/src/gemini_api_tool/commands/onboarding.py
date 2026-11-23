from __future__ import annotations

import os
import shlex
import sys
from pathlib import Path

from ..config import API_KEY_PLACEHOLDER, _parse_env_file, configured_api_key

STARTER = (
    "# Keep this file private. Replace the placeholder with your Gemini API key.\n"
    f"GEMINI_API_KEY={API_KEY_PLACEHOLDER}\n"
)


def _create_settings(path: Path) -> bool:
    if path.exists():
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError:
        return False
    with os.fdopen(fd, "w", encoding="utf-8") as file:
        file.write(STARTER)
    return True


def cmd_onboarding(args: object, ctx: dict) -> int:
    env_path = Path(ctx["env_file"]).expanduser()
    env_created = not bool(getattr(args, "no_write_env", False)) and _create_settings(env_path)
    missing = [] if configured_api_key(_parse_env_file(env_path)) else ["GEMINI_API_KEY"]

    launcher = Path(sys.argv[0])
    entrypoint = shlex.quote(str(launcher.absolute())) if launcher.name == "gemini-api-tool" else "gemini-api-tool"
    command = f"{entrypoint} --output json --env-file {shlex.quote(str(env_path))}"
    auth_command = f"{command} auth check"
    models_command = f"{command} models list"
    steps = []
    if missing:
        steps.append(f"Set GEMINI_API_KEY in {env_path} or in your shell. Keep the key out of chat and Git.")
    steps.extend([f"Check your local settings with {auth_command}", f"List models with {models_command}"])

    if getattr(args, "output", "json") == "json":
        ctx["out"].emit({
            "ok": True,
            "onboarding": {
                "env_file": str(env_path),
                "env_created": env_created,
                "missing": missing,
                "next_command": auth_command,
                "steps": steps,
            },
        })
    else:
        print("\n".join(steps))
    return 0
