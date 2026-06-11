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

    missing: list[str] = []
    if not _has_nonempty_env_value(lines, "TIKTOK_MARKETING_APP_ID"):
        missing.append("TIKTOK_MARKETING_APP_ID")
    if not _has_nonempty_env_value(lines, "TIKTOK_MARKETING_APP_SECRET"):
        missing.append("TIKTOK_MARKETING_APP_SECRET")
    if not _has_nonempty_env_value(lines, "TIKTOK_MARKETING_ACCESS_TOKEN"):
        missing.append("TIKTOK_MARKETING_ACCESS_TOKEN")

    steps = [
        "Copy .env.example → .env (local-only; do not commit it).",
        "Fill these environment values:",
        "  - TIKTOK_MARKETING_API_BASE_URL=https://business-api.tiktok.com",
        "  - TIKTOK_MARKETING_APP_ID=<your TikTok app id>",
        "  - TIKTOK_MARKETING_APP_SECRET=<your TikTok app secret>",
        "  - TIKTOK_MARKETING_ACCESS_TOKEN=<your TikTok Marketing access token>",
        "Use: tiktok-marketing-api-tool --output json auth check",
        "The auth check runs oauth2-advertiser-get using env token if set, or .state/token.json.",
    ]

    payload = {
        "ok": True,
        "onboarding": {
            "env_file": env_file,
            "env_created": env_created,
            "missing": missing,
            "next_command": "tiktok-marketing-api-tool --output json auth check",
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
        print("Next: tiktok-marketing-api-tool --output json auth check")
    return 0
