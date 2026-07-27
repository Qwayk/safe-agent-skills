from __future__ import annotations

import os
from pathlib import Path
from typing import Any

DEFAULT_ENV = """JIRA_BASE_URL=
JIRA_EMAIL=
JIRA_API_TOKEN=
JIRA_OAUTH_ACCESS_TOKEN=
JIRA_TIMEOUT_S=30
"""


def cmd_onboarding(args: Any, ctx: dict[str, Any]) -> int:
    env_path = Path(args.env_file)
    created = False
    if not args.no_write_env and not env_path.exists():
        example = env_path.parent / ".env.example"
        env_path.write_text(
            example.read_text(encoding="utf-8") if example.exists() else DEFAULT_ENV,
            encoding="utf-8",
        )
        os.chmod(env_path, 0o600)
        created = True
    if args.auth_mode == "basic":
        required = ["JIRA_BASE_URL", "JIRA_EMAIL", "JIRA_API_TOKEN"]
        method = "Atlassian account email plus API token"
    else:
        required = ["JIRA_BASE_URL", "JIRA_OAUTH_ACCESS_TOKEN"]
        method = "OAuth 2.0 bearer access token"
    payload = {
        "ok": True,
        "env_file": str(env_path),
        "env_created": created,
        "auth_mode": args.auth_mode,
        "auth_method": method,
        "required_fields": required,
        "next_command": "jira-safe --env-file .env auth check",
        "first_useful_command": "jira-safe --env-file .env platform get-all-projects",
        "secret_rule": "Keep credentials in the local .env file; never paste them into chat.",
    }
    ctx["out"].emit(payload)
    return 0
