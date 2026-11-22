from __future__ import annotations

import os
import shlex
from pathlib import Path

from ..config import _get, _parse_env_file

REQUIRED_SETTINGS = ("CONTENTSQUARE_CLIENT_ID", "CONTENTSQUARE_CLIENT_SECRET")


def _create_env_file(env_path: Path) -> bool:
    env_path.parent.mkdir(parents=True, exist_ok=True)
    example_path = env_path.parent / ".env.example"
    template = (
        example_path.read_text(encoding="utf-8")
        if example_path.is_file()
        else "".join(f"{name}=\n" for name in REQUIRED_SETTINGS)
    )
    try:
        with os.fdopen(
            os.open(env_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), "w", encoding="utf-8"
        ) as file:
            file.write(template)
    except FileExistsError:
        return False
    return True


def cmd_onboarding(args: object, ctx: dict) -> int:
    env_file = str(getattr(args, "env_file", ".env"))
    env_path = Path(env_file)
    env_created = False
    if not getattr(args, "no_write_env", False) and not env_path.exists():
        env_created = _create_env_file(env_path)

    settings = _parse_env_file(env_path)
    missing = [name for name in REQUIRED_SETTINGS if not _get(settings, name)]
    next_args = ["contentsquare-safe-cli", "--output", "json", "--env-file", env_file]
    if project_id := getattr(args, "oauth_project_id", None):
        next_args.extend(("--oauth-project-id", project_id))
    next_command = shlex.join([*next_args, "auth", "check"])
    steps = [
        "Create server-to-server OAuth credentials in Contentsquare for the API you need.",
        f"Set CONTENTSQUARE_CLIENT_ID and CONTENTSQUARE_CLIENT_SECRET in {env_file} or in your shell.",
        "For account-level credentials, also set CONTENTSQUARE_PROJECT_ID to the project you want to use.",
        "Leave CONTENTSQUARE_API_BASE_URL blank unless Contentsquare gave you a fixed API address.",
        "Run the connection check, then list export jobs in a project you recognize.",
    ]
    if str(getattr(args, "output", "json")) == "json":
        ctx["out"].emit({
            "ok": True,
            "onboarding": {
                "env_file": env_file,
                "env_created": env_created,
                "missing": missing,
                "next_command": next_command,
                "steps": steps,
            },
        })
    else:
        for step in steps:
            print(step)
        if missing:
            print("Missing settings: " + ", ".join(missing))
        print(f"Next: {next_command}")
    return 0
