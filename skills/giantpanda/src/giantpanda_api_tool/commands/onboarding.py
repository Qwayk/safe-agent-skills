from __future__ import annotations

import os
from pathlib import Path

from .. import config as config_mod


def _read_lines(path: Path) -> list[str]:
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8")
    return text.splitlines(keepends=True)


def _has_value(lines: list[str], key: str) -> bool:
    for raw in lines:
        s = raw.strip()
        if not s or s.startswith("#") or "=" not in s:
            continue
        if s.startswith("export "):
            s = s[len("export ") :].strip()
        k, v = s.split("=", 1)
        if k.strip() == key and not config_mod.is_placeholder_token(v.strip().strip("'").strip('"')):
            return True
    return False


def cmd_onboarding(args, ctx) -> int:
    out = ctx["out"]
    env_file = Path(getattr(args, "env_file", ".env"))
    wrote = False

    if not env_file.exists():
        example = env_file.parent / ".env.example"
        if not example.exists():
            out.emit({"ok": False, "error": "Missing .env.example", "error_type": "ValidationError"})
            return 1
        env_file.write_text(example.read_text(encoding="utf-8"), encoding="utf-8")
        os.chmod(env_file, 0o600)
        wrote = True

    lines = _read_lines(env_file)
    missing: list[str] = []
    if not _has_value(lines, "GIANTPANDA_API_TOKEN"):
        missing.append("GIANTPANDA_API_TOKEN")

    payload = {
        "ok": True,
        "onboarding": {
            "env_file": str(env_file),
            "env_created": wrote,
            "missing": missing,
            "next_command": "giantpanda --output json auth check",
            "steps": [
                "Create .env from .env.example (already done if missing).",
                "Set GIANTPANDA_API_TOKEN in .env.",
            ],
        },
    }
    out.emit(payload)
    return 0
