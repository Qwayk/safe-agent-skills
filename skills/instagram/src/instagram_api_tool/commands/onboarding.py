from __future__ import annotations

from pathlib import Path
from shlex import quote

from ..config import load_config
from ..oauth_tokens import read_access_token, token_path_for_env_file

_ENV_TEMPLATE = """# Keep your Instagram settings on this computer.
INSTAGRAM_ACCESS_TOKEN=
INSTAGRAM_APP_ID=
INSTAGRAM_APP_SECRET=
INSTAGRAM_REDIRECT_URI=
INSTAGRAM_IG_USER_ID=
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
    token = cfg.token or read_access_token(token_path_for_env_file(env_file))
    app_settings = {
        "INSTAGRAM_APP_ID": cfg.app_id,
        "INSTAGRAM_APP_SECRET": cfg.app_secret,
        "INSTAGRAM_REDIRECT_URI": cfg.redirect_uri,
    }
    missing = [] if token else [name for name, value in app_settings.items() if not value]
    env_option = f" --env-file {quote(env_file)}" if env_file != ".env" else ""
    next_action = "check" if token or missing else "login-url --scope instagram_business_basic"
    steps = [
        "If you have an Instagram user token, put it in INSTAGRAM_ACCESS_TOKEN and run auth check.",
        "To sign in through a Meta app, fill in the Instagram app ID, secret and redirect URL first.",
        "Keep the settings and saved token files private.",
    ]
    next_command = f"instagram-api-tool --output json{env_option} auth {next_action}"
    if getattr(args, "output", "json") == "text":
        for step in steps:
            print(step)
        if missing:
            print("Missing app settings: " + ", ".join(missing))
        print(next_command)
    else:
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
    return 0
