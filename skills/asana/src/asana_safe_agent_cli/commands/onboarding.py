from __future__ import annotations

import os
from pathlib import Path
from typing import Any

_PLACEHOLDER = "# Keep this file private.\nASANA_ACCESS_TOKEN=\nASANA_TIMEOUT_S=30\n"


def cmd_onboarding(args: Any, ctx: dict[str, Any]) -> int:
    env_path = Path(ctx["env_file"]).expanduser()
    created = False
    if not args.no_write_env and not env_path.exists():
        env_path.parent.mkdir(parents=True, exist_ok=True)
        env_path.write_text(_PLACEHOLDER, encoding="utf-8")
        os.chmod(env_path, 0o600)
        created = True
    ctx["out"].emit(
        {
            "ok": True,
            "env_file": str(env_path),
            "created": created,
            "steps": [
                "Create an Asana personal access token or obtain an approved OAuth/service-account bearer token.",
                f"Put it in {env_path} as ASANA_ACCESS_TOKEN without sharing it in chat.",
                "Run `asana-safe auth check`.",
                "Run `asana-safe commands show get-workspaces` before the first read if you want its exact parameters.",
            ],
        }
    )
    return 0
