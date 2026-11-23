from __future__ import annotations

import os
import shlex
from pathlib import Path


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


def _env_payload() -> list[str]:
    return [
        "NAMEBRIGHT_CLIENT_ID=",
        "NAMEBRIGHT_CLIENT_SECRET=",
        "NAMEBRIGHT_TIMEOUT_S=30",
    ]


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
            with os.fdopen(fd, "w", encoding="utf-8") as file:
                file.write("\n".join(_env_payload()) + "\n")
            env_created = True

    lines = env_path.read_text(encoding="utf-8").splitlines(keepends=True) if env_path.exists() else []

    missing: list[str] = []
    for key in ["NAMEBRIGHT_CLIENT_ID", "NAMEBRIGHT_CLIENT_SECRET"]:
        if not _has_nonempty_env_value(lines, key):
            missing.append(key)

    env_flag = f" --env-file {shlex.quote(env_file)}" if env_file != ".env" else ""
    next_command = f"namebright-safe-cli --output json{env_flag} auth check"
    steps = [
        f"Add your NameBright settings to {env_file}. Keep this file private.",
        "  - NAMEBRIGHT_CLIENT_ID=<client_id>",
        "  - NAMEBRIGHT_CLIENT_SECRET=<client_secret>",
        "  - NAMEBRIGHT_TIMEOUT_S=30 (optional; defaults to 30)",
        "In NameBright, request API access and add the IP address that will send requests.",
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
