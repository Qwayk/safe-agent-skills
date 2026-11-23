from __future__ import annotations

import os
import shlex
from pathlib import Path


def _read_text_lines(path: Path) -> list[str]:
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8")
    if not text:
        return []
    return text.splitlines(keepends=True)


def _has_nonempty_env_value(lines: list[str], key: str) -> bool:
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        candidate = stripped
        if candidate.startswith("export "):
            candidate = candidate[len("export ") :].lstrip()
        k, v = candidate.split("=", 1)
        if k.strip() == key and v.strip().strip("'").strip('"'):
            return True
    return False


def cmd_onboarding(args: object, ctx: dict) -> int:
    out = ctx["out"]
    env_file = str(getattr(args, "env_file", ".env"))
    write_env = not bool(getattr(args, "no_write_env", False))

    env_path = Path(env_file)
    env_created = False

    if write_env:
        try:
            fd = os.open(env_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        except FileExistsError:
            pass
        else:
            with os.fdopen(fd, "w", encoding="utf-8") as settings:
                settings.write("SPACESHIP_API_KEY=\nSPACESHIP_API_SECRET=\nSPACESHIP_TIMEOUT_S=30\n")
            env_created = True

    lines = _read_text_lines(env_path)

    missing: list[str] = []
    if not _has_nonempty_env_value(lines, "SPACESHIP_API_KEY"):
        missing.append("SPACESHIP_API_KEY")
    if not _has_nonempty_env_value(lines, "SPACESHIP_API_SECRET"):
        missing.append("SPACESHIP_API_SECRET")

    env_flag = f" --env-file {shlex.quote(env_file)}" if env_file != ".env" else ""
    next_command = f"qwayk-spaceship-safe-agent-cli --output json{env_flag} auth check"
    steps = [
        f"Add your Spaceship settings to {env_file}. Keep this file private.",
        "  - SPACESHIP_API_KEY=<your key>",
        "  - SPACESHIP_API_SECRET=<your secret>",
        f"Run {next_command}",
    ]

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
        print(next_command)
    return 0
