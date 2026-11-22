from __future__ import annotations

from pathlib import Path
from shlex import join

from ..config import load_configured_access_token
from ..oauth_tokens import resolve_access_token


def cmd_onboarding(args: object, ctx: dict) -> int:
    out = ctx["out"]
    env_file = str(getattr(args, "env_file", ".env"))
    write_env = not bool(getattr(args, "no_write_env", False))

    env_path = Path(env_file)
    env_created = False

    if write_env and not env_path.exists():
        example_path = env_path.parent / ".env.example"
        if example_path.exists():
            env_path.write_text(example_path.read_text(encoding="utf-8"), encoding="utf-8")
        else:
            env_path.write_text("", encoding="utf-8")
        env_created = True

    token = resolve_access_token(load_configured_access_token(env_file), env_file)
    missing = [] if token else ["HUBSPOT_ACCESS_TOKEN"]
    next_command = join(
        ["qwayk-hubspot-safe-agent-cli", "--output", "json", "--env-file", env_file, "auth", "check"]
    )
    steps = []
    if not token:
        steps.append(f"Set HUBSPOT_ACCESS_TOKEN in {env_file} or in your shell. Keep the token private.")
    steps.append(f"Check the connection with {next_command}")

    payload = {
        "ok": True,
        "onboarding": {
            "env_file": env_file,
            "env_created": env_created,
            "missing": missing,
            "next_command": next_command,
            "steps": steps,
        },
    }

    if str(getattr(args, "output", "json")) == "json":
        out.emit(payload)
    else:
        print("To connect this tool to your API, do this once:")
        for i, s in enumerate(steps, start=1):
            print(f"{i}. {s}")
        if missing:
            print("")
            print(f"Missing in {env_file}: " + ", ".join(missing))
        print("")
    return 0
