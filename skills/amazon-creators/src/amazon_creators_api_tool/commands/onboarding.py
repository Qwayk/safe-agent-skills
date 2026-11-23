from __future__ import annotations

import os
import shlex
from pathlib import Path

from ..config import DEFAULT_BASE_URL, REQUIRED_SETTINGS, read_settings


def _open_private(path: str, flags: int) -> int:
    return os.open(path, flags, 0o600)


def cmd_onboarding(args, ctx) -> int:
    env_path = Path(args.env_file or ".env")
    options = ["--env-file", args.env_file] if args.env_file is not None else []
    template = f"AMAZON_CREATORS_API_BASE_URL={DEFAULT_BASE_URL}\n" + "".join(
        f"{key}={value}\n" for key, value in REQUIRED_SETTINGS.items()
    )
    created = False
    if ctx.get("apply") and not args.no_write_env:
        try:
            with open(env_path, "x", encoding="utf-8", opener=_open_private) as handle:
                handle.write(template)
        except FileExistsError:
            pass
        else:
            created = True

    settings = read_settings(args.env_file, allow_missing=True)
    missing = [key for key in REQUIRED_SETTINGS if not settings.get(key, "").strip()]
    next_command = shlex.join(["amazon-creators-api-tool", *options, "auth", "token", "fetch"])
    create_command = shlex.join(["amazon-creators-api-tool", *options, "onboarding", "--apply"])
    steps = [
        f"If the settings file is missing, create it with {create_command}",
        f"Enter the Credential ID, Credential Secret and Version from Associates Central in {env_path}.",
        "Set the marketplace locale and the tracking tag for that marketplace. Keep these settings out of chat and Git.",
        f"Preview getting a token with {next_command}",
    ]
    if args.output == "json":
        ctx["out"].emit(
            {
                "ok": True,
                "onboarding": {
                    "env_file": str(env_path),
                    "env_created": created,
                    "missing": missing,
                    "settings_template": template,
                    "next_command": next_command,
                    "steps": steps,
                },
            }
        )
    else:
        for step in steps:
            print(step)
        if missing:
            print("Missing settings: " + ", ".join(missing))
        if not env_path.exists():
            print(template, end="")
    return 0
