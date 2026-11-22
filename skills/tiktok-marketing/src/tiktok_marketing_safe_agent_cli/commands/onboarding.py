from __future__ import annotations

from pathlib import Path
from shlex import quote

from ..config import DEFAULT_BASE_URL, DEFAULT_TIMEOUT_S, load_config
from .auth import _resolve_access_token

_ENV_TEMPLATE = f"""# Keep these TikTok Marketing settings private.
TIKTOK_MARKETING_API_BASE_URL={DEFAULT_BASE_URL}
TIKTOK_MARKETING_APP_ID=
TIKTOK_MARKETING_APP_SECRET=
TIKTOK_MARKETING_ACCESS_TOKEN=
TIKTOK_MARKETING_TIMEOUT_S={DEFAULT_TIMEOUT_S}
"""


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
            env_path.write_text(_ENV_TEMPLATE, encoding="utf-8")
        env_created = True

    cfg = load_config(env_file)
    token, _ = _resolve_access_token(cfg, env_file)

    missing: list[str] = []
    if not cfg.app_id:
        missing.append("TIKTOK_MARKETING_APP_ID")
    if not cfg.app_secret:
        missing.append("TIKTOK_MARKETING_APP_SECRET")
    if not token:
        missing.append("TIKTOK_MARKETING_ACCESS_TOKEN")

    steps = [
        "Fill any missing fields in your local settings. Keep the app secret and access token private.",
        "You can also save the access token from a local JSON file with auth token set.",
        "Run auth check with the same settings file to see the ad accounts this token can access.",
    ]
    env_option = f" --env-file {quote(env_file)}" if env_file != ".env" else ""
    next_command = f"tiktok-marketing-api-tool --output json{env_option} auth check"

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
