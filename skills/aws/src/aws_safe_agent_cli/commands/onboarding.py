from __future__ import annotations

import os
import shlex
import sys
from pathlib import Path


def _create_settings(path: Path) -> bool:
    if path.exists():
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    example = path.parent / ".env.example"
    settings = example.read_text(encoding="utf-8") if example.is_file() else (
        "# Optional AWS settings. Keep credentials in your AWS profile or sign-in.\n"
        "AWS_PROFILE=\nAWS_DEFAULT_REGION=\n"
    )
    try:
        descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError:
        return False
    with os.fdopen(descriptor, "w", encoding="utf-8") as output:
        output.write(settings)
    return True


def cmd_onboarding(args: object, ctx: dict) -> int:
    path = Path(str(getattr(args, "env_file", ".env"))).expanduser()
    created = not bool(getattr(args, "no_write_env", False)) and _create_settings(path)
    launcher = Path(sys.argv[0])
    entrypoint = (
        shlex.quote(str(launcher.absolute()))
        if launcher.name == "qwayk-aws-safe-agent-cli"
        else "qwayk-aws-safe-agent-cli"
    )
    command = f"{entrypoint} --output json --env-file {shlex.quote(str(path))} auth check"
    steps = [
        "Sign in with the AWS profile or role you want to use.",
        "Set AWS_PROFILE to choose a named profile. Set AWS_DEFAULT_REGION only to override its region.",
        f"Check the account, role and region with {command}",
    ]
    if str(getattr(args, "output", "json")) == "json":
        ctx["out"].emit({
            "ok": True,
            "onboarding": {
                "env_file": str(path),
                "env_created": created,
                "missing": [],
                "next_command": command,
                "steps": steps,
            },
        })
    else:
        print("\n".join(steps))
    return 0
