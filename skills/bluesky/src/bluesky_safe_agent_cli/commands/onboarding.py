from __future__ import annotations

from pathlib import Path
from shlex import quote

from ..config import load_config
from ..session_store import configured_access_session

_ENV_TEMPLATE = "# Settings for signing in to Bluesky. Keep this file private.\nBLUESKY_IDENTIFIER=\nBLUESKY_APP_PASSWORD=\n"



def cmd_onboarding(args: object, ctx: dict) -> int:
    out = ctx["out"]
    env_file = str(getattr(args, "env_file", ".env"))
    write_env = not bool(getattr(args, "no_write_env", False))

    env_path = Path(env_file)
    env_created = False

    if write_env and not env_path.exists():
        env_path.parent.mkdir(parents=True, exist_ok=True)
        example_path = env_path.parent / ".env.example"
        if example_path.exists():
            env_path.write_text(example_path.read_text(encoding="utf-8"), encoding="utf-8")
        else:
            env_path.write_text(_ENV_TEMPLATE, encoding="utf-8")
        env_created = True

    cfg = load_config(env_file)
    token, _, _ = configured_access_session(cfg.access_jwt, env_file)
    missing: list[str] = []
    if not token and not cfg.identifier:
        missing.append("BLUESKY_IDENTIFIER")
    if not token and not cfg.app_password:
        missing.append("BLUESKY_APP_PASSWORD")

    steps = [
        "You can read public feeds without signing in.",
        "To sign in, create an app password in Bluesky Settings and add it and your handle to this file.",
        "Use auth login to save a session and auth check to confirm the signed-in account.",
    ]
    env_option = f" --env-file {quote(env_file)}" if env_file != ".env" else ""
    next_action = "check" if token else "login"
    next_command = f"bluesky-safe-cli --output json{env_option} auth {next_action}"

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
        print(f"Next: {next_command}")
    return 0
