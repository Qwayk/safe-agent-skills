from __future__ import annotations

import os
import shlex
import sys
from pathlib import Path


def _create_settings(path: Path) -> bool:
    if path.exists():
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError:
        return False
    with os.fdopen(fd, "w", encoding="utf-8") as file:
        file.write("# Optional Google Cloud settings. Keep credentials in Application Default Credentials.\nGCP_QUOTA_PROJECT=\n")
    return True


def cmd_onboarding(args: object, ctx: dict) -> int:
    path = Path(ctx["env_file"]).expanduser()
    created = not bool(getattr(args, "no_write_env", False)) and _create_settings(path)
    launcher = Path(sys.argv[0])
    entrypoint = shlex.quote(str(launcher.absolute())) if launcher.name == "qwayk-gcp-safe-agent-cli" else "qwayk-gcp-safe-agent-cli"
    auth_command = f"{entrypoint} --output json --env-file {shlex.quote(str(path))} auth check"
    steps = [
        "Use Google Application Default Credentials to connect.",
        "Set a quota project or resource lists in the settings file if you need them.",
        f"Check the connection with {auth_command}",
    ]
    if getattr(args, "output", "json") == "json":
        ctx["out"].emit({
            "ok": True,
            "onboarding": {
                "env_file": str(path),
                "env_created": created,
                "missing": [],
                "next_command": auth_command,
                "steps": steps,
            },
        })
    else:
        print("\n".join(steps))
    return 0
