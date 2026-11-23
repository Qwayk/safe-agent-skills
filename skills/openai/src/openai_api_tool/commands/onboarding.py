from __future__ import annotations

import os
import shlex
from pathlib import Path
from typing import Any

from ..config import load_config
from ..errors import ValidationError

_SETTINGS = """OPENAI_API_BASE_URL=https://api.openai.com/v1
OPENAI_API_KEY=
OPENAI_ORGANIZATION_ID=
OPENAI_PROJECT_ID=
OPENAI_TIMEOUT_S=30
"""


def cmd_onboarding(args: Any, ctx: dict[str, Any]) -> int:
    env_file = Path(args.env_file).absolute()
    created = False
    if not args.no_write_env:
        try:
            env_file.parent.mkdir(parents=True, exist_ok=True)
            fd = os.open(env_file, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                handle.write(_SETTINGS)
            created = True
        except FileExistsError:
            pass
        except OSError as exc:
            raise ValidationError("Could not create the private settings file") from exc

    missing = [] if load_config(str(env_file)).api_key else ["OPENAI_API_KEY"]
    next_command = shlex.join(
        ["openai-api-tool", "--env-file", str(env_file), "--output", "json", "auth", "check"]
    )
    steps = ["Set OPENAI_API_KEY in the selected settings file."] if missing else []
    if args.output == "json":
        ctx["out"].emit({
            "ok": True,
            "onboarding": {
                "env_file": str(env_file),
                "env_created": created,
                "missing": missing,
                "next_command": next_command,
                "steps": steps,
            },
        })
    else:
        for message in steps:
            print(message)
        print(f"Settings file {env_file}")
        print(f"Next command {next_command}")
    return 0
