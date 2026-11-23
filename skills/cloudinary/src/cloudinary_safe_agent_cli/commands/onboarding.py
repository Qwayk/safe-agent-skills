from __future__ import annotations

import os
from pathlib import Path
from shlex import quote

from ..config import load_config

_PRODUCT_FIELDS = {
    "cloud_name": "CLOUDINARY_CLOUD_NAME",
    "api_key": "CLOUDINARY_API_KEY",
    "api_secret": "CLOUDINARY_API_SECRET",
}
_ACCOUNT_FIELDS = {
    "account_id": "CLOUDINARY_ACCOUNT_ID",
    "account_api_key": "CLOUDINARY_ACCOUNT_API_KEY",
    "account_api_secret": "CLOUDINARY_ACCOUNT_API_SECRET",
}


def cmd_onboarding(args, ctx) -> int:
    env_file = ctx["env_file"]
    env_path = Path(env_file)
    env_created = False
    if not args.no_write_env and not env_path.exists():
        example = env_path.with_name(".env.example")
        initial = (
            example.read_text(encoding="utf-8")
            if example.is_file()
            else "".join(f"{key}=\n" for key in (*_PRODUCT_FIELDS.values(), *_ACCOUNT_FIELDS.values()))
        )
        env_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            fd = os.open(env_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            with os.fdopen(fd, "w", encoding="utf-8") as target:
                target.write(initial)
            env_created = True
        except FileExistsError:
            pass

    cfg = load_config(env_file)
    prefix = f"cloudinary-safe-agent-cli --env-file {quote(env_file)}"
    next_command = f"{prefix} operations admin resources-get-resources --path-param resource_type=image --query max_results=1"
    steps = [
        f"Put the cloud name, API key, and API secret for your media library in {env_file}.",
        "Account credentials are only needed for account-level commands.",
        "Keep your settings file and secrets out of Git and chat.",
        "Run the asset read below to check the Cloudinary library you chose.",
    ]
    payload = {
        "ok": True,
        "onboarding": {
            "env_file": env_file,
            "env_created": env_created,
            "missing": {
                "product": [key for attr, key in _PRODUCT_FIELDS.items() if not getattr(cfg, attr)],
                "account": [key for attr, key in _ACCOUNT_FIELDS.items() if not getattr(cfg, attr)],
            },
            "next_command": next_command,
            "steps": steps,
        },
    }
    if args.output == "json":
        ctx["out"].emit(payload)
    else:
        for step in steps:
            print(step)
        print(next_command)
    return 0
