from __future__ import annotations

from pathlib import Path


ENV_TEMPLATE = """# Safe local defaults for TheMealDB free V1 access.
THEMEALDB_BASE_URL=https://www.themealdb.com/api/json/v1
THEMEALDB_API_KEY=1
THEMEALDB_TIMEOUT_S=30
"""


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
        current_key, current_value = candidate.split("=", 1)
        if current_key.strip() == key and current_value.strip().strip("'").strip('"'):
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
            env_path.write_text(ENV_TEMPLATE, encoding="utf-8")
        env_created = True

    lines = _read_text_lines(env_path)

    missing: list[str] = []
    if not _has_nonempty_env_value(lines, "THEMEALDB_BASE_URL"):
        missing.append("THEMEALDB_BASE_URL")
    if not _has_nonempty_env_value(lines, "THEMEALDB_API_KEY"):
        missing.append("THEMEALDB_API_KEY")
    if not _has_nonempty_env_value(lines, "THEMEALDB_TIMEOUT_S"):
        missing.append("THEMEALDB_TIMEOUT_S")

    steps = [
        "Keep the default public key `1` unless you already have your own TheMealDB supporter key.",
        "If `.env` does not exist yet, let this command create it from `.env.example`.",
        "Run `qwayk-themealdb-safe-agent-cli --output json auth check` to confirm the API is reachable.",
        "Start with read-only commands like `categories`, `search`, `lookup`, and `filter`.",
    ]

    payload = {
        "ok": True,
        "onboarding": {
            "env_file": env_file,
            "env_created": env_created,
            "missing": missing,
            "next_command": "qwayk-themealdb-safe-agent-cli --output json auth check",
            "steps": steps,
        },
    }

    if str(getattr(args, "output", "json")) == "json":
        out.emit(payload)
    else:
        print("This tool is ready to use with the public TheMealDB key `1`.")
        for index, step in enumerate(steps, start=1):
            print(f"{index}. {step}")
        if missing:
            print("")
            print(f"Missing in {env_file}: " + ", ".join(missing))
        print("")
        print("Next: qwayk-themealdb-safe-agent-cli --output json auth check")
    return 0
