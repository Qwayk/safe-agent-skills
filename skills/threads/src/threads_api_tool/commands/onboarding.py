from __future__ import annotations

from pathlib import Path
from shlex import quote

from ..config import load_config

_ENV_TEMPLATE = """# Keep your Threads settings on this computer.
THREADS_API_TOKEN=
THREADS_APP_ID=
THREADS_APP_SECRET=
THREADS_REDIRECT_URI=
THREADS_DEFAULT_USER_ID=
"""


def cmd_onboarding(args: object, ctx: dict) -> int:
    env_file = ctx["env_file"]
    env_path = Path(env_file)
    env_created = False

    if not getattr(args, "no_write_env", False) and not env_path.exists():
        example = env_path.parent / ".env.example"
        contents = example.read_text(encoding="utf-8") if example.is_file() else _ENV_TEMPLATE
        env_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with env_path.open("x", encoding="utf-8") as file:
                file.write(contents)
            env_created = True
        except FileExistsError:
            pass

    cfg = load_config(env_file)
    app_settings = {
        "THREADS_APP_ID": cfg.app_id,
        "THREADS_APP_SECRET": cfg.app_secret,
        "THREADS_REDIRECT_URI": cfg.redirect_uri,
    }
    missing = [] if cfg.token else [key for key, value in app_settings.items() if not value]
    env_option = f" --env-file {quote(env_file)}" if env_file != ".env" else ""
    next_action = "check" if cfg.token or missing else "authorize-url --scope threads_basic"
    ctx["out"].emit(
        {
            "ok": True,
            "onboarding": {
                "env_file": env_file,
                "env_created": env_created,
                "missing": missing,
                "next_command": f"threads-api-tool --output json{env_option} auth {next_action}",
                "steps": [
                    "If you have a Threads user token, put it in THREADS_API_TOKEN and run auth check.",
                    "To connect through a Meta app, fill in its ID, secret and redirect URL before running auth authorize-url.",
                    "Keep the settings and saved token files private.",
                ],
            },
        }
    )
    return 0
