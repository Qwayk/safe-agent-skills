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
        "# Optional Azure settings. Keep your Azure CLI sign-in on this machine.\n"
        "AZURE_SUBSCRIPTION_ID=\n"
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
    executable = (
        shlex.quote(str(launcher.absolute()))
        if launcher.name == "qwayk-azure-safe-agent-cli"
        else "qwayk-azure-safe-agent-cli"
    )
    command = f"{executable} --output json --env-file {shlex.quote(str(path))} auth check"
    steps = [
        "Sign in locally with az login, or use your existing Azure token settings.",
        "Set AZURE_SUBSCRIPTION_ID if you want to select a subscription in this settings file.",
        f"Check the connection with {command}",
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
