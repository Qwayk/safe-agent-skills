from __future__ import annotations

from pathlib import Path
from shlex import quote

from ..config import load_config


def cmd_onboarding(args, ctx) -> int:
    env_file = ctx["env_file"]
    env_path = Path(env_file)
    env_created = False
    if not args.no_write_env and not env_path.exists():
        example = env_path.with_name(".env.example")
        initial = example.read_text(encoding="utf-8") if example.is_file() else "FIGMA_ACCESS_TOKEN=\n"
        env_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with env_path.open("x", encoding="utf-8") as target:
                target.write(initial)
            env_created = True
        except FileExistsError:
            pass

    cfg = load_config(env_file)
    missing = [] if cfg.token else ["FIGMA_ACCESS_TOKEN"]
    if missing and cfg.auth_mode == "oauth":
        missing = ["FIGMA_ACCESS_TOKEN or OAuth token file"]

    prefix = f"figma-safe-agent-cli --env-file {quote(env_file)}"
    next_command = f"{prefix} operations files get-file-meta --file-key YOUR_FILE_KEY"
    steps = [
        "Give your Figma token access to the file and the read permission needed for the command.",
        f"For a personal token, set FIGMA_ACCESS_TOKEN in {env_file}. Personal mode is the default.",
        "For OAuth, set FIGMA_AUTH_MODE=oauth and use auth token set or FIGMA_ACCESS_TOKEN.",
        "For a plan token, set FIGMA_AUTH_MODE=plan and FIGMA_ACCESS_TOKEN.",
        "Keep tokens and local settings files private.",
        "Try a file you can open in Figma. The file metadata command needs file_metadata:read.",
    ]
    payload = {
        "ok": True,
        "onboarding": {
            "env_file": env_file,
            "env_created": env_created,
            "auth_mode": cfg.auth_mode,
            "token_source": cfg.token_source,
            "missing": missing,
            "next_command": next_command,
            "steps": steps,
        },
    }
    if args.output == "json":
        ctx["out"].emit(payload)
    else:
        for step in steps:
            print(step)
        if missing:
            print(f"Set up your Figma token in {env_file} first.")
        print(next_command)
    return 0
