from __future__ import annotations

import os
import shlex
import sys
from pathlib import Path

from ..config import _get, _parse_env_file


def _create_settings(path: Path) -> bool:
    if path.exists():
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError:
        return False
    with os.fdopen(fd, "w", encoding="utf-8") as file:
        file.write("# Keep this file private. Add your Cloud Management Key.\nQDRANT_CLOUD_API_KEY=\n")
    return True


def cmd_onboarding(args: object, ctx: dict) -> int:
    path = Path(ctx["env_file"]).expanduser()
    created = not bool(getattr(args, "no_write_env", False)) and _create_settings(path)
    missing = [] if _get(_parse_env_file(path), "QDRANT_CLOUD_API_KEY") else ["QDRANT_CLOUD_API_KEY"]
    launcher = Path(sys.argv[0])
    entrypoint = shlex.quote(str(launcher.absolute())) if launcher.name == "qdrant-cloud-api-tool" else "qdrant-cloud-api-tool"
    command = f"{entrypoint} --output json --env-file {shlex.quote(str(path))}"
    auth = f"{command} auth check"
    first_read = f"{command} --live account-v1 list-accounts"
    steps = []
    if missing:
        steps.append(f"Set QDRANT_CLOUD_API_KEY in {path} or in your shell. Keep it out of chat and Git.")
    steps.extend([f"Check the local settings with {auth}", f"List accounts when live access is approved with {first_read}"])
    if getattr(args, "output", "json") == "json":
        ctx["out"].emit({
            "ok": True,
            "onboarding": {
                "env_file": str(path),
                "env_created": created,
                "missing": missing,
                "next_command": auth,
                "steps": steps,
            },
        })
    else:
        print("\n".join(steps))
    return 0
