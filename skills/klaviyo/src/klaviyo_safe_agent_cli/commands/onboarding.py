from __future__ import annotations

import os
import shlex
from pathlib import Path

from ..config import DEFAULT_BASE_URL, load_config


def cmd_onboarding(args, ctx: dict) -> int:
    env_path = Path(args.env_file)
    env_created = False
    if not args.no_write_env and not env_path.exists():
        example = env_path.parent / ".env.example"
        template = (
            example.read_text(encoding="utf-8")
            if example.is_file()
            else f"KLAVIYO_API_BASE_URL={DEFAULT_BASE_URL}\nKLAVIYO_API_KEY=\n"
        )
        try:
            with open(env_path, "x", encoding="utf-8", opener=lambda name, flags: os.open(name, flags, 0o600)) as f:
                f.write(template)
            env_created = True
        except FileExistsError:
            pass

    cfg = load_config(args.env_file)
    missing = [] if cfg.api_key else ["KLAVIYO_API_KEY"]
    next_command = shlex.join(
        ["klaviyo-safe-agent-cli", "--env-file", args.env_file, "--output", "json", "--live", "api", "get_lists"]
    )
    steps = [
        f"Save your Klaviyo private API key in {env_path} as KLAVIYO_API_KEY.",
        "Use a key with lists:read to list audiences.",
        "If you only need client commands, set KLAVIYO_COMPANY_ID and use the client command directly.",
    ]
    if args.output == "text":
        for step in steps:
            print(step)
        print(next_command)
    else:
        ctx["out"].emit({
            "ok": True,
            "onboarding": {
                "env_file": str(env_path),
                "env_created": env_created,
                "missing": missing,
                "next_command": next_command,
                "steps": steps,
            },
        })
    return 0
