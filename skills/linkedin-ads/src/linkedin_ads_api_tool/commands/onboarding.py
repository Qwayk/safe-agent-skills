from __future__ import annotations

from pathlib import Path

from ..config import (
    DEFAULT_BASE_URL,
    DEFAULT_LINKEDIN_VERSION,
    DEFAULT_RESTLI_PROTOCOL_VERSION,
    read_env_file,
    resolve_token,
)


_PLACEHOLDER_ENV = f"""# LinkedIn Ads settings
LINKEDIN_ADS_BASE_URL={DEFAULT_BASE_URL}
LINKEDIN_ADS_TOKEN=
LINKEDIN_ADS_LINKEDIN_VERSION={DEFAULT_LINKEDIN_VERSION}
LINKEDIN_ADS_RESTLI_PROTOCOL_VERSION={DEFAULT_RESTLI_PROTOCOL_VERSION}
LINKEDIN_ADS_TIMEOUT_S=30
"""


def cmd_onboarding(args: object, ctx: dict) -> int:
    out = ctx["out"]
    env_file = str(getattr(args, "env_file", ".env"))
    write_env = not bool(getattr(args, "no_write_env", False))

    env_path = Path(env_file)
    env_created = False

    if write_env and not env_path.exists():
        env_path.write_text(_PLACEHOLDER_ENV, encoding="utf-8")
        env_created = True

    token = resolve_token(env_file, read_env_file(env_path))

    steps = [
        "If you need to add a LinkedIn access token, save it in your local settings or use auth token set.",
        "Run linkedin-ads-api-tool --output json auth check to see which ad accounts you can access.",
        "If LinkedIn denies access, check the app's approved products, the token permissions, and your account role.",
    ]

    payload = {
        "ok": True,
        "onboarding": {
            "env_file": env_file,
            "env_created": env_created,
            "missing": [] if token else ["LINKEDIN_ADS_TOKEN"],
            "next_command": "linkedin-ads-api-tool --output json auth check",
            "steps": steps,
        },
    }

    out.emit(payload)
    return 0
