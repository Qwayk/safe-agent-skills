from __future__ import annotations

import os
import shlex
from pathlib import Path

from .. import config as config_mod


def cmd_onboarding(args, ctx) -> int:
    out = ctx["out"]
    env_file = Path(args.env_file).absolute()
    try:
        env_file.parent.mkdir(parents=True, exist_ok=True)
        fd = os.open(env_file, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError:
        wrote = False
    except OSError:
        out.emit({"ok": False, "error": "Could not create the settings file", "error_type": "SettingsFileError"})
        return 1
    else:
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                handle.write(f"GIANTPANDA_API_TOKEN=\nGIANTPANDA_TIMEOUT_S={config_mod.DEFAULT_TIMEOUT_S}\n")
        except OSError:
            out.emit({"ok": False, "error": "Could not write the settings file", "error_type": "SettingsFileError"})
            return 1
        wrote = True

    token = config_mod.load_config(str(env_file)).token
    missing = ["GIANTPANDA_API_TOKEN"] if config_mod.is_placeholder_token(token or "") else []
    out.emit(
        {
            "ok": True,
            "onboarding": {
                "env_file": str(env_file),
                "env_created": wrote,
                "missing": missing,
                "next_command": shlex.join(
                    ["giantpanda", "--output", "json", "--env-file", str(env_file), "auth", "check"]
                ),
                "steps": ["Set GIANTPANDA_API_TOKEN in the settings file."] if missing else [],
            },
        }
    )
    return 0
