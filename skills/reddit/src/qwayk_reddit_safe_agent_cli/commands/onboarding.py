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
        env_key, env_value = candidate.split("=", 1)
        if env_key.strip() == key and env_value.strip().strip("'").strip('"'):
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
    missing: list[str] = []
    for key in ("REDDIT_CLIENT_ID", "REDDIT_REDIRECT_URI", "REDDIT_CONTACT_USERNAME"):
        if not _has_nonempty_env_value(lines, key):
            missing.append(key)

    steps = [
        "Copy .env.example to .env if you do not already have one.",
        "In Reddit, create a Data API app and request access approval if you do not already have it.",
        "Fill .env with your client id, redirect URI, and contact username.",
        "Run: qwayk-reddit-safe-agent-cli auth login",
        "Open the printed URL, approve the app, then run --live auth exchange-code with the redirect URL.",
        "After that, run: qwayk-reddit-safe-agent-cli --live auth check",
    ]

    payload = {
        "ok": True,
        "onboarding": {
            "env_file": env_file,
            "env_created": env_created,
            "missing": missing,
            "next_command": "qwayk-reddit-safe-agent-cli auth login",
            "steps": steps,
        },
    }
    if str(getattr(args, "output", "json")) == "json":
        out.emit(payload)
    else:
        print("Set up the Reddit tool like this:")
        for index, step in enumerate(steps, start=1):
            print(f"{index}. {step}")
        if missing:
            print("")
            print(f"Missing in {env_file}: " + ", ".join(missing))
    return 0
