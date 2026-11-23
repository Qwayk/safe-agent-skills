from __future__ import annotations

import argparse
import shlex
from pathlib import Path

from ..errors import ValidationError
from ..json_files import new_private_file


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

    if env_path.is_symlink() or (env_path.exists() and not env_path.is_file()):
        raise ValidationError("The settings path must be a regular file.")
    if write_env and not env_path.exists():
        with new_private_file(env_path) as stream:
            stream.write(
                "DYNADOT_API_BASE_URL=https://api.dynadot.com/api3.json\n"
                "DYNADOT_API_KEY=\n"
                "DYNADOT_TIMEOUT_S=30\n"
            )
        env_created = True

    lines = _read_text_lines(env_path)
    missing = [
        key for key in ("DYNADOT_API_BASE_URL", "DYNADOT_API_KEY")
        if not _has_nonempty_env_value(lines, key)
    ]
    next_command = shlex.join(
        ["dynadot-api-tool", "--output", "json", "--env-file", env_file, "auth", "check"]
    )
    steps = [
        f"Open {env_file} and add your Dynadot API key. Keep it out of chat and Git.",
        "Use https://api.dynadot.com/api3.json for a production key.",
        f"Run {next_command}",
        "For a move between two Dynadot accounts, use a separate settings file for each account.",
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
        print(f"Next: {next_command}")
    return 0


def register_onboarding(
    subparsers: argparse._SubParsersAction,
    *,
    parser_class: type[argparse.ArgumentParser],
) -> None:
    _ = parser_class
    onboarding = subparsers.add_parser("onboarding", help="First-time setup help (no secrets)")
    onboarding.add_argument(
        "--no-write-env",
        action="store_true",
        help="Do not write/update the env file; print instructions only",
    )
    onboarding.set_defaults(func=cmd_onboarding, write_capable=False)
