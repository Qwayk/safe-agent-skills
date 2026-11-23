from __future__ import annotations

import os
import shlex
from pathlib import Path

from ..config import read_settings

REQUIRED_SETTINGS = ("SKIMLINKS_CLIENT_ID", "SKIMLINKS_CLIENT_SECRET", "SKIMLINKS_PUBLISHER_ID")
OPTIONAL_SETTINGS = (
    "SKIMLINKS_PUBLISHER_DOMAIN_ID",
    "SKIMLINKS_PRODUCT_CLIENT_ID",
    "SKIMLINKS_PRODUCT_CLIENT_SECRET",
    "SKIMLINKS_LINK_WRAPPER_ID",
)


def _open_private(path: str, flags: int) -> int:
    return os.open(path, flags, 0o600)


def cmd_onboarding(args, ctx) -> int:
    env_path = Path(args.env_file or ".env")
    env_created = False
    if not args.no_write_env and not env_path.exists():
        example = env_path.with_name(".env.example")
        if example.is_file() and example != env_path:
            template = example.read_text(encoding="utf-8")
        else:
            template = "".join(f"{key}=\n" for key in (*REQUIRED_SETTINGS, *OPTIONAL_SETTINGS))
        try:
            with open(env_path, "x", encoding="utf-8", opener=_open_private) as handle:
                handle.write(template)
        except FileExistsError:
            pass
        else:
            env_created = True

    settings = read_settings(args.env_file, allow_missing=True)
    missing = [key for key in REQUIRED_SETTINGS if not settings.get(key, "").strip()]
    options = ["--env-file", args.env_file] if args.env_file is not None else []
    next_command = shlex.join(["skimlinks-safe-cli", "--output", "json", *options, "auth", "check"])
    steps = [
        "In Publisher Hub, open Toolbox, APIs, then API Authentication.",
        f"Enter the Client ID, Client Secret and Publisher ID in {env_path}. Keep credentials out of chat.",
        "For Product Key, set SKIMLINKS_PUBLISHER_DOMAIN_ID or pass --publisher-domain-id.",
        "If Skimlinks gave you separate Product Key credentials, fill in both Product Key fields.",
        "To make affiliate links, set SKIMLINKS_LINK_WRAPPER_ID to your Site ID or pass --id.",
        f"Run {next_command}",
    ]
    if args.output == "json":
        ctx["out"].emit(
            {
                "ok": True,
                "onboarding": {
                    "env_file": str(env_path),
                    "env_created": env_created,
                    "missing": missing,
                    "next_command": next_command,
                    "steps": steps,
                },
            }
        )
    else:
        for number, step in enumerate(steps, start=1):
            print(f"{number}. {step}")
        if missing:
            print(f"Missing settings for {env_path}: " + ", ".join(missing))
    return 0
