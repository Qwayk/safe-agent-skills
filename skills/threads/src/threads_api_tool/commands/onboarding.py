from __future__ import annotations

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

    if write_env and not env_path.exists():
        example_path = env_path.parent / ".env.example"
        if example_path.exists():
            env_path.write_text(example_path.read_text(encoding="utf-8"), encoding="utf-8")
        else:
            env_path.write_text("", encoding="utf-8")
        env_created = True

    lines = _read_text_lines(env_path)

    required_keys = [
        "THREADS_API_BASE_URL",
        "THREADS_API_VERSION",
        "THREADS_REDIRECT_URI",
        "THREADS_APP_ID",
        "THREADS_APP_SECRET",
    ]

    missing: list[str] = []
    for key in required_keys:
        if not _has_nonempty_env_value(lines, key):
            missing.append(key)

    steps = [
        "Copy .env.example -> .env (local-only; do not commit it).",
        "Open .env and fill the required values:",
        "  - THREADS_API_BASE_URL=https://graph.threads.net",
        "  - THREADS_API_VERSION=v1.0",
        "  - THREADS_APP_ID, THREADS_APP_SECRET",
        "  - THREADS_REDIRECT_URI, THREADS_DEFAULT_USER_ID (optional)",
        "Run: threads-api-tool --output json auth check",
    ]

    payload = {
        "ok": True,
        "onboarding": {
            "env_file": env_file,
            "env_created": env_created,
            "missing": missing,
            "next_command": "threads-api-tool --output json auth check",
            "steps": steps,
        },
    }

    out.emit(payload)
    return 0
